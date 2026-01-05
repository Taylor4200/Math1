"""Simple bulletproof Plinko optimizer."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

# Targets from game_config
TARGETS = {
    "mild": {"base_rtp": 0.9267, "eff_rtp": 0.973, "respin": 0.05},
    "sinful": {"base_rtp": 0.8963, "eff_rtp": 0.968, "respin": 0.08},
    "demonic": {"base_rtp": 0.8598, "eff_rtp": 0.963, "respin": 0.12},
}

def binary_search_optimize(mode):
    """Use binary search to find perfect center/side bucket balance."""
    mults = M[mode]
    target = TARGETS[mode]
    
    print(f"\nOptimizing {mode.upper()}...")
    
    # Start with a range for center bucket percentage
    low_center = 0.50
    high_center = 0.95
    best_counts = None
    best_error = float('inf')
    
    for _ in range(50):  # 50 iterations should be enough
        mid_center = (low_center + high_center) / 2
        
        # Allocate probabilities
        p = [0.0] * 17
        
        # Center bucket gets mid_center percentage
        p[8] = mid_center
        
        # Remaining prob split between <1x neighbors and >=1x buckets
        remaining = 1.0 - mid_center
        
        # Adjacent buckets to center (also <1x for MILD/SINFUL, or 0x for DEMONIC)
        if mode in ["mild", "sinful"]:
            p[7] = p[9] = remaining * 0.12  # 12% each in adjacent
            prob_less_so_far = p[7] + p[8] + p[9]
        else:  # demonic - buckets 7,8,9 are all 0x
            p[7] = p[9] = remaining * 0.12
            prob_less_so_far = p[7] + p[8] + p[9]
        
        # Remaining for >=1x buckets
        gte_remaining = 1.0 - prob_less_so_far
        
        # Distribute to achieve target RTP
        # Buckets 5,6,10,11 (symmetric 2x and 4x)
        p[5] = p[11] = gte_remaining * 0.10  # 4x buckets
        p[6] = p[10] = gte_remaining * 0.35  # 2x buckets
        
        # Remaining for higher multipliers
        higher_remaining = gte_remaining - (p[5] + p[6] + p[10] + p[11])
        
        # Distribute remaining to buckets 0-4, 12-16
        rare_buckets = [0, 1, 2, 3, 4, 12, 13, 14, 15, 16]
        for i in rare_buckets:
            if mults[i] >= 100:
                p[i] = higher_remaining * 0.001
            elif mults[i] >= 20:
                p[i] = higher_remaining * 0.01
            elif mults[i] >= 8:
                p[i] = higher_remaining * 0.05
            else:
                p[i] = higher_remaining * 0.1
        
        # Renormalize
        p = [prob / sum(p) for prob in p]
        
        # Calculate RTP
        rtp = sum(p[i] * mults[i] for i in range(17))
        prob_less = sum(p[i] for i in range(17) if mults[i] < 1.0)
        
        # Check error
        error = abs(rtp - target["base_rtp"])
        
        if error < best_error:
            best_error = error
            best_counts = [int(prob * 100000) for prob in p]
        
        # Binary search adjustment
        if rtp > target["base_rtp"]:
            low_center = mid_center  # Need more center bucket (lower mult)
        else:
            high_center = mid_center  # Need less center bucket
    
    # Use best counts found
    counts = best_counts
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
    eff_rtp = base_rtp * (1 + target["respin"])
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Write
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    print(f"  Base RTP: {base_rtp:.4f}, Effective: {eff_rtp:.4f}")
    print(f"  Prob<Bet: {prob_less:.3f}")
    print(f"  Error: {abs(eff_rtp - target['eff_rtp']):.4f}")
    
    if abs(eff_rtp - target['eff_rtp']) < 0.005 and prob_less < 0.80:
        print(f"  [PERFECT]")
    else:
        print(f"  [Close]")
    
    return counts

# Run
print("PLINKO SIMPLE OPTIMIZER")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    optimize_mode(mode)

print("\n[DONE] Run: python games/plinko/run.py")



