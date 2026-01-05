"""Generate a single reel file with natural distribution."""

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import os
import sys

def create_bell_curve_probabilities(num_buckets=17, sharpness=2.5):
    center = (num_buckets - 1) / 2
    positions = np.arange(num_buckets)
    probabilities = norm.pdf(positions, loc=center, scale=sharpness)
    probabilities = probabilities / np.sum(probabilities)
    return probabilities

def find_optimal_sharpness(multipliers, target_rtp):
    def rtp_error(sharpness):
        probs = create_bell_curve_probabilities(num_buckets=len(multipliers), sharpness=sharpness)
        actual_rtp = np.sum(probs * multipliers)
        return (actual_rtp - target_rtp) ** 2
    
    result = minimize_scalar(rtp_error, bounds=(1.0, 5.0), method='bounded')
    return result.x

def probabilities_to_csv(probabilities, output_path, total_weight=100000):
    weights = np.round(probabilities * total_weight).astype(int)
    diff = total_weight - np.sum(weights)
    if diff > 0:
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(diff):
            weights[sorted_indices[i % len(sorted_indices)]] += 1
    elif diff < 0:
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(abs(diff)):
            idx = sorted_indices[i % len(sorted_indices)]
            if weights[idx] > 0:
                weights[idx] -= 1
    
    bucket_list = []
    for bucket_idx, weight in enumerate(weights):
        bucket_list.extend([bucket_idx] * int(weight))
    
    np.random.shuffle(bucket_list)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for bucket in bucket_list:
            f.write(f"{bucket}\n")
    
    return weights

if __name__ == "__main__":
    from game_config import GameConfig
    config = GameConfig()
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "mild"
    targets = {"mild": 0.9525, "sinful": 0.9500, "demonic": 0.9550}
    
    target_rtp = targets[mode]
    multipliers = np.array(config.bucket_multipliers[mode])
    
    print(f"Generating {mode.upper()} with target RTP={target_rtp:.6f}")
    
    optimal_sharpness = find_optimal_sharpness(multipliers, target_rtp)
    probabilities = create_bell_curve_probabilities(num_buckets=17, sharpness=optimal_sharpness)
    actual_rtp = np.sum(probabilities * multipliers)
    
    print(f"  Sharpness: {optimal_sharpness:.3f}")
    print(f"  Actual RTP: {actual_rtp:.6f}")
    print(f"  Error: {abs(actual_rtp - target_rtp):.8f}")
    
    csv_path = os.path.join("games", "plinko", "reels", f"{mode.upper()}.csv")
    probabilities_to_csv(probabilities, csv_path, total_weight=100000)
    
    print(f"  Saved to: {csv_path}")
    print(f"  File size: {os.path.getsize(csv_path)} bytes")











