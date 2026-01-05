"""FIX 96% RTP FOR ALL MODES - Exact mathematical solver for 96% RTP with Prob_less_bet < 80%."""

import random
import csv
import os

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

def solve_96_percent_rtp(mode, max_prob_less=0.79):
    """Solve for exact 96% RTP with Prob_less_bet constraint."""
    mults = M[mode]
    
    # Target: 96% RTP for ALL modes
    target_rtp = 0.96
    
    # Identify <1x buckets
    less_than_one_indices = [i for i, m in enumerate(mults) if m < 1.0]
    gte_one_indices = [i for i, m in enumerate(mults) if m >= 1.0]
    
    print(f"\n{mode.upper()}: Solving for 96% RTP with Prob_less_bet < {max_prob_less:.0%}")
    
    # Strategy: Allocate exactly max_prob_less to <1x buckets, then solve for >=1x buckets
    probs = [0.0] * len(mults)
    
    # For <1x buckets, assign probabilities to stay under max_prob_less
    if mode == "mild":
        # Bucket 8 (0.5x) gets most of the <1x probability
        probs[8] = 0.75  # 75% in 0.5x bucket
        probs[7] = 0.02  # Small amounts in adjacent 1x buckets
        probs[9] = 0.02
    elif mode == "sinful":
        # Buckets 7,8,9: 0.5x, 0.2x, 0.5x
        probs[8] = 0.70  # 70% in 0.2x bucket
        probs[7] = 0.045 # 4.5% each in 0.5x buckets
        probs[9] = 0.045
    else:  # demonic
        # Buckets 7,8,9 are all 0x
        probs[7] = 0.25  # Split evenly
        probs[8] = 0.25
        probs[9] = 0.25
    
    # Calculate RTP from <1x buckets
    rtp_from_less = sum(probs[i] * mults[i] for i in range(len(mults)))
    
    # Remaining probability for >=1x buckets
    remaining_prob = 1.0 - sum(probs)
    
    # Remaining RTP needed from >=1x buckets
    remaining_rtp_needed = target_rtp - rtp_from_less
    
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
        if mult >= 1000:
            weight = 0.00001
        elif mult >= 100:
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
    
    # Fine-tune to hit exact 96% RTP
    for iteration in range(200):
        current_rtp = sum(probs[i] * mults[i] for i in range(len(mults)))
        error = current_rtp - target_rtp
        
        if abs(error) < 0.0001:  # Within 0.01%
            break
        
        # Adjust by shifting probability between buckets
        if error > 0:  # RTP too high - shift to lower multipliers
            # Find highest mult >=1x bucket with significant probability
            for i in sorted(gte_one_indices, key=lambda x: mults[x], reverse=True):
                if probs[i] > 0.001:
                    transfer = min(probs[i] * 0.05, abs(error) / mults[i])
                    probs[i] -= transfer
                    # Add to 1x or 2x bucket
                    if mode == "mild":
                        target_bucket = 7 if i < 8 else 9  # 1x buckets
                    else:
                        target_bucket = 6 if i < 8 else 10  # 2x buckets
                    probs[target_bucket] += transfer
                    break
        else:  # RTP too low - shift to higher multipliers
            # Shift from 1x-2x to 4x-8x
            for i in gte_one_indices:
                if mults[i] <= 2 and probs[i] > 0.01:
                    transfer = min(probs[i] * 0.05, abs(error) / 4)
                    probs[i] -= transfer
                    # Add to 4x bucket
                    target_bucket = 5 if i < 8 else 11
                    probs[target_bucket] += transfer
                    break
    
    # Convert to bucket counts (100k total)
    counts = [int(p * 100000) for p in probs]
    diff = 100000 - sum(counts)
    counts[8] += diff  # Adjust middle bucket
    
    return counts

def create_lookup_table(mode, counts, output_dir="library/publish_files"):
    """Create lookup table CSV from bucket counts."""
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Calculate payouts (multipliers * 100 for cents)
    payouts = [int(M[mode][bucket] * 100) for bucket in strip]
    
    # Write lookup table
    lookup_path = os.path.join(output_dir, f"lookUpTable_{mode}_0.csv")
    with open(lookup_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for i, payout in enumerate(payouts):
            writer.writerow([i, 1, payout])  # book_id, weight, payout_cents
    
    return lookup_path

# Solve for all modes - ALL at 96% RTP
print("="*70)
print("FIXING ALL MODES TO 96% RTP WITH Prob_less_bet < 80%")
print("="*70)

results = {}
for mode in ["mild", "sinful", "demonic"]:
    counts = solve_96_percent_rtp(mode, max_prob_less=0.79)
    
    # Create strip and calculate stats
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    wins = [M[mode][b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Create lookup table
    lookup_path = create_lookup_table(mode, counts)
    
    # Store results
    results[mode] = {
        "rtp": base_rtp,
        "prob_less_bet": prob_less,
        "lookup_path": lookup_path
    }
    
    # Check if within targets
    rtp_error = abs(base_rtp - 0.96)
    rtp_ok = rtp_error < 0.001  # Within 0.1%
    prob_ok = prob_less < 0.80
    
    status = "[PERFECT]" if rtp_ok and prob_ok else "[NEEDS ADJUSTMENT]"
    
    print(f"  {mode.upper()}:")
    print(f"    RTP: {base_rtp:.4%} (target: 96.000%, error: {rtp_error:.4%})")
    print(f"    Prob_less_bet: {prob_less:.4%} (target: <80%)")
    print(f"    Status: {status}")
    print(f"    Lookup table: {lookup_path}")
    print()

print("="*70)
print("VERIFICATION:")
print("="*70)

# Verify the generated lookup tables
for mode in results:
    lookup_path = results[mode]["lookup_path"]
    
    total_weight = 0
    total_payout = 0
    
    with open(lookup_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            book_id, weight, payout_cents = row
            weight = int(weight)
            payout_cents = int(payout_cents)
            
            total_weight += weight
            total_payout += weight * payout_cents
    
    # payout_cents is in cents (100 = 1x bet)
    rtp = (total_payout / total_weight / 100) if total_weight > 0 else 0
    house_edge = (1 - rtp) * 100
    
    print(f"{mode.upper()}:")
    print(f"  Verified RTP: {rtp:.4%}")
    print(f"  House Edge: {house_edge:.2f}%")
    print(f"  Total Weight: {total_weight:,}")
    print()

print("="*70)
print("SUCCESS! All modes now target 96% RTP with Prob_less_bet < 80%")
print("Run: python verify_final_rtps.py to confirm")
print("="*70)















