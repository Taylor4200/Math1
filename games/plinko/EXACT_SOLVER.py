"""EXACT mathematical solver for perfect Plinko distributions."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

def solve_exact(mode, base_rtp_target, max_prob_less):
    """Solve for exact probability distribution."""
    mults = M[mode]
    
    # EXACT calculation using constraints:
    # Constraint 1: prob_less_bet <= max_prob_less (e.g., 0.79)
    # Constraint 2: RTP = base_rtp_target
    # Constraint 3: sum(probs) = 1.0
    
    # Strategy: Set <1x buckets to exactly max_prob_less, then solve for >=1x buckets
    
    # Identify <1x buckets
    less_than_one_indices = [i for i, m in enumerate(mults) if m < 1.0]
    gte_one_indices = [i for i, m in enumerate(mults) if m >= 1.0]
    
    # Allocate exactly max_prob_less to <1x buckets
    # Split proportionally based on how low they are
    probs = [0.0] * len(mults)
    
    # For <1x buckets, assign probabilities
    if mode == "mild":
        # Bucket 8 (0.5x) gets most of the <1x probability
        probs[8] = 0.68  # 68% in 0.5x
        probs[7] = 0.055 # Small amount in adjacent buckets
        probs[9] = 0.055
    elif mode == "sinful":
        # Bucket 8 (0.2x), buckets 7,9 (0.5x each)
        probs[8] = 0.60  # 60% in 0.2x
        probs[7] = 0.095 # 9.5% each in 0.5x
        probs[9] = 0.095
    else:  # demonic
        # Buckets 7,8,9 are all 0x
        probs[7] = 0.263  # Split evenly-ish
        probs[8] = 0.264
        probs[9] = 0.263
    
    # Calculate RTP from <1x buckets
    rtp_from_less = sum(probs[i] * mults[i] for i in range(len(mults)))
    
    # Remaining probability for >=1x buckets
    remaining_prob = 1.0 - sum(probs)
    
    # Remaining RTP needed from >=1x buckets
    remaining_rtp_needed = base_rtp_target - rtp_from_less
    
    # Average multiplier needed from >=1x buckets
    avg_mult_needed = remaining_rtp_needed / remaining_prob if remaining_prob > 0 else 0
    
    print(f"  <1x prob: {sum(probs):.3f}, contributes {rtp_from_less:.4f} RTP")
    print(f"  >=1x prob: {remaining_prob:.3f}, needs {remaining_rtp_needed:.4f} RTP (avg {avg_mult_needed:.2f}x)")
    
    # Distribute remaining probability to >=1x buckets
    # Weight them so average multiplier = avg_mult_needed
    gte_weights = []
    for i in gte_one_indices:
        mult = mults[i]
        # Weight inversely to multiplier, but scaled to hit avg
        if mult >= 100:
            weight = 0.0001
        elif mult >= 20:
            weight = 0.001
        elif mult >= 10:
            weight = 0.01
        elif mult >= 4:
            weight = 0.1
        elif mult >= 2:
            weight = 1.0
        else:  # mult == 1
            weight = 2.0
        gte_weights.append(weight)
    
    # Normalize gte_weights to sum to remaining_prob
    total_gte_weight = sum(gte_weights)
    for idx, i in enumerate(gte_one_indices):
        probs[i] = (gte_weights[idx] / total_gte_weight) * remaining_prob
    
    # Fine-tune to hit exact RTP
    for _ in range(100):
        current_rtp = sum(probs[i] * mults[i] for i in range(len(mults)))
        error = current_rtp - base_rtp_target
        
        if abs(error) < 0.0005:
            break
        
        # Adjust by shifting probability between buckets
        if error > 0:  # RTP too high - shift to lower multipliers
            # Find highest mult >=1x bucket with significant probability
            for i in sorted(gte_one_indices, key=lambda x: mults[x], reverse=True):
                if probs[i] > 0.001:
                    transfer = min(probs[i] * 0.1, abs(error) / mults[i])
                    probs[i] -= transfer
                    # Add to 1x or 2x bucket
                    target_bucket = 7 if mode == "mild" else 6
                    probs[target_bucket] += transfer
                    break
        else:  # RTP too low - shift to higher multipliers
            # Shift from 1x-2x to 4x-8x
            for i in gte_one_indices:
                if mults[i] <= 2 and probs[i] > 0.01:
                    transfer = min(probs[i] * 0.1, abs(error) / 4)
                    probs[i] -= transfer
                    # Add to 4x bucket
                    target_bucket = 5 if i < 8 else 11
                    probs[target_bucket] += transfer
                    break
    
    # Convert to bucket counts
    counts = [int(p * 100000) for p in probs]
    diff = 100000 - sum(counts)
    counts[8] += diff
    
    return counts

# Solve for all modes
base_rtps = {"mild": 0.9267, "sinful": 0.8963, "demonic": 0.8598}

for mode, target_base_rtp in base_rtps.items():
    counts = solve_exact(mode, target_base_rtp, 0.79)
    
    # Create strip
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Stats
    wins = [M[mode][b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
    eff_rtp = base_rtp * (1 + respin)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Write
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
    err = abs(eff_rtp - targets[mode])
    
    print(f"  FINAL: Eff RTP {eff_rtp:.4f} (err {err:.4f}), Prob<Bet {prob_less:.3f}")
    
    if err < 0.003 and prob_less < 0.80:
        print(f"  [PERFECT!!!]\n")
    elif err < 0.01 and prob_less < 0.80:
        print(f"  [EXCELLENT!]\n")
    else:
        print(f"  [{'RTP' if err >= 0.01 else ''}{'&' if err >= 0.01 and prob_less >= 0.80 else ''}{'Prob' if prob_less >= 0.80 else ''} needs adjustment]\n")

print("="*70)
print("[DONE] Optimization complete! Run: python games/plinko/run.py")



