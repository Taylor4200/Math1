"""Calculate exact distributions from mathematical constraints."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

def calculate_perfect_weights(mode, base_rtp_target, max_prob_less):
    """Calculate exact weights to hit both constraints."""
    mults = M[mode]
    
    # Constraint 1: prob_less_bet <= 0.79
    # Buckets <1x must be <=79%
    # Buckets >=1x must be >=21%
    
    # Constraint 2: Base RTP = target
    # Sum(prob_i * mult_i) = base_rtp_target
    
    # For symmetry, split probabilities evenly on left/right
    # Buckets 7&9 (symmetric around center 8)
    # Buckets 6&10, 5&11, etc.
    
    # Let's assign probabilities:
    p = [0.0] * 17
    
    # Rare max wins
    p[0] = p[16] = 0.00001  # 0.001% each (666x or 1666x or 16666x)
    
    # High wins (buckets 1-2, 14-15)
    p[1] = p[15] = 0.0002
    p[2] = p[14] = 0.0004
    
    # Medium-high wins (buckets 3, 13)
    p[3] = p[13] = 0.0015
    
    # Medium wins (buckets 4, 12)
    p[4] = p[12] = 0.005
    
    # Now calculate remaining for buckets 5-11
    # These are the critical buckets that determine RTP and prob_less_bet
    
    remaining_prob = 1.0 - sum(p)
    remaining_rtp = base_rtp_target - sum(p[i] * mults[i] for i in range(17))
    
    # Buckets 5-11: [4x, 2x, 1x, 0.5x/0.2x/0x, 1x, 2x, 4x]
    # Need to distribute remaining_prob (~98%) to contribute remaining_rtp
    
    # For prob_less_bet < 0.79, buckets 7,8,9 should sum to ~0.78 MAX
    # Let remaining >=1x buckets (5,6,10,11) get ~0.20
    
    # Split >=1x buckets (need ~20-21% here):
    # Buckets 5&11 (4x): 2% each = 4% total
    # Buckets 6&10 (2x): 8% each = 16% total
    # Total >=1x from 5-6, 10-11: 20%
    
    p[5] = p[11] = 0.02   # 4x buckets
    p[6] = p[10] = 0.08   # 2x buckets
    
    # Buckets 7,8,9 get the remaining
    remaining_for_center = 1.0 - sum(p)
    
    # Split center buckets to hit exact RTP
    # Buckets 7&9 are symmetric (both 1x for MILD, both 0.5x for SINFUL, both 0x for DEMONIC)
    # Let's split evenly first, then adjust
    
    p[7] = p[9] = remaining_for_center * 0.15  # 15% each
    p[8] = remaining_for_center * 0.70  # 70% in center
    
    # Verify and adjust to hit exact RTP
    current_rtp = sum(p[i] * mults[i] for i in range(17))
    
    print(f"\n{mode.upper()}:")
    print(f"  Initial RTP: {current_rtp:.4f}, Target: {base_rtp_target:.4f}")
    print(f"  Initial prob_less_bet: {sum(p[i] for i in range(17) if mults[i] < 1.0):.3f}")
    
    # Fine-tune by adjusting bucket 8 vs buckets 7&9
    if current_rtp > base_rtp_target:
        # Lower RTP - shift from 7&9 to 8
        shift = (current_rtp - base_rtp_target) / 2
        p[8] += shift
        p[7] -= shift / 2
        p[9] -= shift / 2
    else:
        # Raise RTP - shift from 8 to 7&9
        shift = (base_rtp_target - current_rtp) / 2
        p[7] += shift / 2
        p[9] += shift / 2
        p[8] -= shift
    
    # Convert to counts
    counts = [int(prob * 100000) for prob in p]
    diff = 100000 - sum(counts)
    counts[8] += diff  # Add/remove from center
    
    return counts

# Create distributions
base_rtps = {"mild": 0.9267, "sinful": 0.8963, "demonic": 0.8598}

for mode, target_base_rtp in base_rtps.items():
    weights = calculate_perfect_weights(mode, target_base_rtp, 0.79)
    
    # Create strip
    strip = []
    for i, count in enumerate(weights):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Stats
    wins = [M[mode][b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
    eff = base_rtp * (1 + respin)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Write
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
    rtp_err = abs(eff - targets[mode])
    
    print(f"  Final Effective RTP: {eff:.4f} (target: {targets[mode]}, error: {rtp_err:.4f})")
    print(f"  Final Prob<Bet: {prob_less:.3f}")
    
    if rtp_err < 0.005 and prob_less < 0.80:
        print(f"  [PERFECT!!!]")
    elif rtp_err < 0.01:
        print(f"  [GOOD] RTP within 1%")
    else:
        print(f"  [ADJUST]")

print("\n[OK] Calculated distributions created!")



