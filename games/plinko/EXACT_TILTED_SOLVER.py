import os
import csv
import math
import random
from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import root

# Fixed multipliers per mode (symmetric L->R). Adjust only if absolutely required.
MULTS = {
    "mild": np.array([666, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 666], dtype=float),
    "sinful": np.array([1666, 8, 4, 2, 1.5, 1, 0.5, 0.2, 0.5, 1, 1.5, 2, 4, 8, 1666], dtype=float),
    # Demonic with 0x center buckets (three 0x in the middle on a 17-bucket board => map to 15 by dropping pure zero slots into the center weight)
    # We'll approximate a 15-position model by aggregating center zeros into the central bucket's weight control using the penalty parameter.
    # To remain consistent with the existing 17 buckets in game_config, we will map final 15-bucket probs back to 17 buckets with 0x in 3 center slots.
}

# For integration with a 17-bucket board, define indices mapping
# We will operate on 17-bucket vectors directly to avoid remapping issues
MULTS_17 = {
    "mild": np.array([666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666], dtype=float),
    "sinful": np.array([1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666], dtype=float),
    "demonic": np.array([6666, 8, 4, 2, 1.5, 1, 0, 0, 0, 1, 1.5, 2, 4, 8, 12, 300, 6666], dtype=float),
}

TARGET_RTP = 0.97
MAX_PROB_LESS = {
    "mild": 0.80,
    "sinful": 0.80,
    "demonic": 0.80,
}
TOTAL_ROWS = 5_000_000
EPS = 1e-9


def gaussian_weights(n: int, center: float, sigma: float) -> NDArray[np.float64]:
    x = np.arange(n)
    w = np.exp(-0.5 * ((x - center) / max(sigma, 1e-6)) ** 2)
    return w


def build_base_weights(mode: str, mults: NDArray[np.float64]) -> NDArray[np.float64]:
    n = len(mults)
    center = (n - 1) / 2.0
    # Mode-specific sigma
    if mode == "mild":
        sigma = 3.2
    elif mode == "sinful":
        sigma = 3.8
    else:
        sigma = 4.2
    w = gaussian_weights(n, center, sigma)
    # Lightly penalize edges to avoid too-high E when edges are huge
    edge_penalty = np.linspace(1.0, 0.6, n // 2 + 1)
    shaped = w.copy()
    for i in range(n // 2 + 1):
        shaped[i] *= edge_penalty[(n // 2) - i]
        shaped[n - 1 - i] *= edge_penalty[(n // 2) - i]
    shaped = shaped + EPS
    shaped = shaped / shaped.sum()
    return shaped


def prob_less_than_bet(p: NDArray[np.float64], m: NDArray[np.float64]) -> float:
    return float(p[m < 1.0].sum())


def normalize(p: NDArray[np.float64]) -> NDArray[np.float64]:
    s = p.sum()
    if s <= 0:
        return np.ones_like(p) / len(p)
    return p / s


def tilted_distribution(base: NDArray[np.float64], mults: NDArray[np.float64], k: float, l: float) -> NDArray[np.float64]:
    # Exponential tilting by multiplier and penalty on <1x outcomes
    penalty = (mults < 1.0).astype(float)
    logits = np.log(base + EPS) + k * mults + l * penalty
    # Stabilize
    logits = logits - logits.max()
    p = np.exp(logits)
    return normalize(p)


def solve_k_l_for_targets(mode: str, mults: NDArray[np.float64], base: NDArray[np.float64], target_rtp: float, max_prob_less: float) -> Tuple[float, float, NDArray[np.float64]]:
    # Solve for k, l to satisfy RTP and cap prob_less_bet <= max_prob_less.
    # We set prob_less_bet to be exactly min(max_prob_less - 0.01, 0.78) when feasible to give margin.
    target_prob_less = min(max_prob_less - 0.01, 0.78)

    def equations(vars_: NDArray[np.float64]) -> NDArray[np.float64]:
        k, l = vars_[0], vars_[1]
        p = tilted_distribution(base, mults, k, l)
        rtp = float((p * mults).sum())
        pl = prob_less_than_bet(p, mults)
        return np.array([rtp - target_rtp, pl - target_prob_less], dtype=float)

    # Initial guess heuristics
    k0 = 0.0
    l0 = math.log((1 - target_prob_less + 1e-6) / (target_prob_less + 1e-6)) * 0.01
    sol = root(equations, np.array([k0, l0], dtype=float), method="hybr")

    if not sol.success:
        # Fallback: try multiple seeds
        seeds = [(-0.1, -0.1), (0.1, -0.1), (0.2, -0.2), (-0.2, 0.2), (0.5, -0.5), (-0.5, 0.5)]
        for k0, l0 in seeds:
            sol = root(equations, np.array([k0, l0], dtype=float), method="hybr")
            if sol.success:
                break

    if not sol.success:
        # Last resort: fix l via bisection on prob_less, then solve k for RTP via 1D root
        def find_l_for_prob(target_pl: float) -> float:
            lo, hi = -10.0, 10.0
            for _ in range(60):
                mid = (lo + hi) / 2
                p_mid = tilted_distribution(base, mults, 0.0, mid)
                pl_mid = prob_less_than_bet(p_mid, mults)
                if pl_mid > target_pl:
                    # need to penalize <1 more => increase l
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2

        l = find_l_for_prob(target_prob_less)
        def rtp_equation(k: float) -> float:
            p = tilted_distribution(base, mults, k, l)
            return float((p * mults).sum()) - target_rtp
        # 1D bisection on k
        lo, hi = -10.0, 10.0
        f_lo, f_hi = rtp_equation(lo), rtp_equation(hi)
        for _ in range(80):
            mid = (lo + hi) / 2
            f_mid = rtp_equation(mid)
            if f_mid == 0 or (hi - lo) < 1e-8:
                k = mid
                break
            if (f_lo > 0 and f_mid > 0) or (f_lo < 0 and f_mid < 0):
                lo, f_lo = mid, f_mid
            else:
                hi, f_hi = mid, f_mid
        else:
            k = (lo + hi) / 2
        p = tilted_distribution(base, mults, k, l)
        return k, l, p

    k, l = float(sol.x[0]), float(sol.x[1])
    p = tilted_distribution(base, mults, k, l)
    return k, l, p


def write_lookup_and_reel(mode: str, probs: NDArray[np.float64], mults: NDArray[np.float64]) -> Tuple[str, str]:
    # Ensure min epsilon per bucket
    p = probs.copy()
    p[p < 1e-7] = 1e-7
    p = normalize(p)

    counts = np.floor(p * TOTAL_ROWS).astype(int)
    # Fix rounding to exact TOTAL_ROWS
    diff = TOTAL_ROWS - counts.sum()
    # Distribute diff starting from center outwards
    idx_order = list(range(len(p)))
    idx_order.sort(key=lambda i: abs(i - (len(p) - 1) / 2.0))
    for i in idx_order:
        if diff == 0:
            break
        counts[i] += 1 if diff > 0 else -1
        diff += -1 if diff > 0 else 1

    # Build strip of bucket indices
    strip: List[int] = []
    for i, c in enumerate(counts):
        if c > 0:
            strip.extend([i] * c)
    random.shuffle(strip)

    out_dir_lut = os.path.join("games", "plinko", "library", "publish_files")
    out_dir_reels = os.path.join("games", "plinko", "reels")
    os.makedirs(out_dir_lut, exist_ok=True)
    os.makedirs(out_dir_reels, exist_ok=True)

    # Write reel
    reel_path = os.path.join(out_dir_reels, f"{mode.upper()}.csv")
    with open(reel_path, "w", newline="") as f:
        for idx in strip:
            f.write(f"{idx}\n")

    # Write LUT (payout cents)
    payouts = [int(round(mults[idx] * 100)) for idx in strip]
    lut_path = os.path.join(out_dir_lut, f"lookUpTable_{mode}_0.csv")
    with open(lut_path, "w", newline="") as f:
        w = csv.writer(f)
        for i, payout in enumerate(payouts):
            w.writerow([i + 1, 1, payout])

    return lut_path, reel_path


def main() -> None:
    results = {}
    for mode in ["mild", "sinful", "demonic"]:
        mults = MULTS_17[mode]
        base = build_base_weights(mode, mults)
        k, l, p = solve_k_l_for_targets(mode, mults, base, TARGET_RTP, MAX_PROB_LESS[mode])
        rtp = float((p * mults).sum())
        pl = prob_less_than_bet(p, mults)
        lut_path, reel_path = write_lookup_and_reel(mode, p, mults)
        results[mode] = {
            "rtp": rtp,
            "prob_less": pl,
            "lut": lut_path,
            "reel": reel_path,
            "k": k,
            "l": l,
        }
        print(f"{mode.upper()}: RTP={rtp:.6%} Prob<bet={pl:.4%} -> {os.path.basename(lut_path)}")

    print("\nVerification (quick):")
    for mode in ["mild", "sinful", "demonic"]:
        info = results[mode]
        print(f"- {mode}: RTP={info['rtp']:.6%}, Prob<bet={info['prob_less']:.4%}, LUT={os.path.basename(info['lut'])}")


if __name__ == "__main__":
    main()















