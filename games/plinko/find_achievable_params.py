"""Find achievable RTP and prob_less_bet for each mode given the bucket multipliers."""

import numpy as np
from scipy.optimize import minimize
from game_config import GameConfig

def find_achievable_rtp_for_plb(mode, target_plb):
    """Find the achievable RTP for a given prob_less_bet target."""
    game_config = GameConfig()
    multipliers = np.array(game_config.bucket_multipliers[mode])
    num_buckets = len(multipliers)
    
    # Find max RTP with given prob_less_bet constraint
    def objective(x):
        return -np.sum(x * multipliers)  # Negative because we maximize
    
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},  # Sum to 1
        {'type': 'eq', 'fun': lambda x: np.sum(x[multipliers < 1.0]) - target_plb},  # prob_less_bet
    ]
    
    bounds = [(0.00001, 1.0) for _ in range(num_buckets)]
    x0 = np.ones(num_buckets) / num_buckets
    
    result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if result.success:
        max_rtp = -result.fun
        min_rtp = np.min(multipliers[multipliers >= 0])  # Minimum possible
        return max_rtp, min_rtp
    else:
        return None, None

def find_achievable_plb_for_rtp(mode, target_rtp):
    """Find the achievable prob_less_bet for a given RTP target."""
    game_config = GameConfig()
    multipliers = np.array(game_config.bucket_multipliers[mode])
    num_buckets = len(multipliers)
    
    # Find the prob_less_bet when achieving target RTP
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},  # Sum to 1
        {'type': 'eq', 'fun': lambda x: np.sum(x * multipliers) - target_rtp},  # RTP
    ]
    
    bounds = [(0.00001, 1.0) for _ in range(num_buckets)]
    x0 = np.ones(num_buckets) / num_buckets
    
    # Try to find a solution
    def objective(x):
        return np.sum(x ** 2)  # Minimize variance (find smoothest distribution)
    
    result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if result.success:
        plb = np.sum(result.x[multipliers < 1.0])
        return plb, result.x
    else:
        return None, None

if __name__ == "__main__":
    modes = ["mild", "sinful", "demonic"]
    game_config = GameConfig()
    
    for mode in modes:
        print(f"\n{'='*60}")
        print(f"{mode.upper()} MODE ANALYSIS")
        print(f"{'='*60}")
        
        mults = np.array(game_config.bucket_multipliers[mode])
        print(f"Multipliers: {mults}")
        print(f"Average: {mults.mean():.4f}")
        print(f"Min: {mults.min():.4f}, Max: {mults.max():.4f}")
        
        # Count sub-1x buckets
        sub_1x = mults < 1.0
        print(f"Sub-1x buckets: {np.sum(sub_1x)} buckets: {mults[sub_1x]}")
        
        # Find achievable RTP for different prob_less_bet values
        print(f"\nAchievable RTP for different prob_less_bet targets:")
        for plb in [0.1, 0.2, 0.3, 0.5, 0.75]:
            max_rtp, min_rtp = find_achievable_rtp_for_plb(mode, plb)
            if max_rtp:
                print(f"  prob_less_bet={plb:.2f}: RTP range [{min_rtp:.4f}, {max_rtp:.4f}]")
            else:
                print(f"  prob_less_bet={plb:.2f}: NOT ACHIEVABLE")
        
        # Find achievable prob_less_bet for target RTP
        target_rtps = {"mild": 0.9267, "sinful": 0.8963, "demonic": 0.8598}
        target_rtp = target_rtps[mode]
        print(f"\nFor target RTP={target_rtp}:")
        plb, solution = find_achievable_plb_for_rtp(mode, target_rtp)
        if plb is not None:
            print(f"  Achievable prob_less_bet: {plb:.4f}")
            print(f"  Distribution (top 5 buckets):")
            top_indices = np.argsort(solution)[::-1][:5]
            for idx in top_indices:
                print(f"    Bucket {idx} (mult={mults[idx]:.2f}): prob={solution[idx]:.6f}")
        else:
            print(f"  Target RTP={target_rtp} NOT ACHIEVABLE")


