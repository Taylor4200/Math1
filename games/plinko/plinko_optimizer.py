"""Dedicated Plinko optimizer - calculates perfect bucket weights from optimization config."""

import json
import random

MULTIPLIERS = {
    "mild": [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666],
    "sinful": [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666],
    "demonic": [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666],
}

def optimize_mode(mode):
    """Optimize bucket weights using RTP targets and scaling."""
    from game_config import GameConfig
    from game_optimization import OptimizationSetup
    
    config = GameConfig()
    opt_setup = OptimizationSetup(config)
    
    # Get optimization parameters
    opt_params = config.opt_params[mode]
    conditions = opt_params["conditions"]
    scaling = opt_params["scaling"]
    base_rtp_target = [m._rtp for m in config.bet_modes if m._name == mode][0]
    
    mults = MULTIPLIERS[mode]
    
    print(f"\n{'='*70}")
    print(f"Optimizing {mode.upper()}")
    print(f"Target Base RTP: {base_rtp_target:.4f}, prob_less_bet < 0.80")
    
    # Initialize bucket probabilities based on RTP contributions
    bucket_probs = [0.0] * 17
    
    # For each criteria, assign initial probabilities
    for criteria_name, criteria_config in conditions.items():
        rtp_contrib = criteria_config.get("rtp", 0)
        search_cond = criteria_config.get("search_conditions")
        
        # Find matching buckets
        matching = []
        if isinstance(search_cond, tuple):
            for i, m in enumerate(mults):
                if search_cond[0] <= m <= search_cond[1]:
                    matching.append(i)
        elif isinstance(search_cond, (int, float)):
            for i, m in enumerate(mults):
                if m == search_cond:
                    matching.append(i)
        
        if matching:
            # Distribute RTP contribution inverse to multiplier values
            inv_mults = [1.0 / (mults[i] + 0.01) for i in matching]
            total_inv = sum(inv_mults)
            
            for idx, bucket_idx in enumerate(matching):
                weight = inv_mults[idx] / total_inv
                prob_needed = (rtp_contrib * weight) / mults[bucket_idx]
                bucket_probs[bucket_idx] += prob_needed
    
    # Normalize
    total_prob = sum(bucket_probs)
    bucket_probs = [p / total_prob for p in bucket_probs]
    
    # Apply scaling
    for rule in scaling:
        win_range = rule.get("win_range", (0, 999999))
        scale_factor = rule.get("scale_factor", 1.0)
        
        for i in range(17):
            if win_range[0] <= mults[i] <= win_range[1]:
                bucket_probs[i] *= scale_factor
    
    # Renormalize
    bucket_probs = [p / sum(bucket_probs) for p in bucket_probs]
    
    # Iteratively adjust for exact targets
    for iteration in range(1000):
        rtp = sum(bucket_probs[i] * mults[i] for i in range(17))
        prob_less = sum(bucket_probs[i] for i in range(17) if mults[i] < 1.0)
        
        rtp_error = rtp - base_rtp_target
        prob_error = max(0, prob_less - 0.79)
        
        if abs(rtp_error) < 0.0005 and prob_less <= 0.79:
            print(f"Converged in {iteration + 1} iterations")
            break
        
        lr = 0.005 if iteration < 500 else 0.001
        
        for i in range(17):
            if rtp_error > 0:
                if mults[i] < base_rtp_target:
                    bucket_probs[i] *= (1 + lr)
                else:
                    bucket_probs[i] *= (1 - lr)
            else:
                if mults[i] > base_rtp_target:
                    bucket_probs[i] *= (1 + lr)
                else:
                    bucket_probs[i] *= (1 - lr)
            
            if prob_error > 0:
                if mults[i] < 1.0:
                    bucket_probs[i] *= (1 - lr * 3)
                else:
                    bucket_probs[i] *= (1 + lr * 3)
        
        bucket_probs = [max(p, 0.000001) for p in bucket_probs]
        bucket_probs = [p / sum(bucket_probs) for p in bucket_probs]
    
    # Convert to counts
    counts = [int(p * 100000) for p in bucket_probs]
    diff = 100000 - sum(counts)
    counts[8] += diff
    
    # Create strip
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Final stats
    wins = [mults[b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
    eff_rtp = base_rtp * (1 + respin)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Write CSV
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    print(f"Results: Eff RTP {eff_rtp:.4f}, Prob<Bet {prob_less:.3f}")
    print(f"Counts: {counts}")
    
    targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
    rtp_ok = abs(eff_rtp - targets[mode]) < 0.003
    prob_ok = prob_less < 0.80
    
    if rtp_ok and prob_ok:
        print(f"[PERFECT!!!]")
    elif abs(eff_rtp - targets[mode]) < 0.01 and prob_ok:
        print(f"[EXCELLENT - within 1%]")
    else:
        print(f"[Needs adjustment]")

# Run optimizer for all modes
if __name__ == "__main__":
    print("PLINKO OPTIMIZER")
    print("="*70)
    
    for mode in ["mild", "sinful", "demonic"]:
        optimize_mode(mode)
    
    print("\n" + "="*70)
    print("[COMPLETE] Optimization done!")
    print("Run: python games/plinko/run.py to generate 100k books")
