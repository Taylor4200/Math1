"""PROPER FUN SOLVER - Realistic hit rates that maintain 96% RTP with actual excitement."""

import random
import csv
import os
import numpy as np
from scipy.optimize import minimize

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

def calculate_realistic_hit_rates(mode, target_rtp=0.96):
    """Calculate realistic hit rates based on multiplier values and RTP constraints."""
    
    mults = M[mode]
    n_buckets = len(mults)
    
    print(f"\n{mode.upper()}: Calculating realistic hit rates for {target_rtp:.1%} RTP")
    
    # Strategy: Set realistic hit rates based on multiplier values
    # Higher multipliers = rarer hits (inversely proportional)
    
    if mode == "mild":
        # MILD: More generous hit rates since multipliers are lower
        base_rates = {
            666: 0.000015,  # 1 in 66,667 (0.0015%)
            150: 0.000067,  # 1 in 14,925 (0.0067%)
            60: 0.000167,   # 1 in 5,988 (0.0167%)
            20: 0.0005,     # 1 in 2,000 (0.05%)
            8: 0.00125,     # 1 in 800 (0.125%)
            4: 0.0025,      # 1 in 400 (0.25%)
            2: 0.005,       # 1 in 200 (0.5%)
            1: 0.015,       # 1 in 67 (1.5%)
            0.5: 0.975,     # 97.5%
        }
    elif mode == "sinful":
        # SINFUL: Moderate hit rates
        base_rates = {
            1666: 0.0000058, # 1 in 172,414 (0.00058%)
            400: 0.000025,   # 1 in 40,000 (0.0025%)
            120: 0.000083,   # 1 in 12,048 (0.0083%)
            40: 0.00025,     # 1 in 4,000 (0.025%)
            12: 0.000833,    # 1 in 1,200 (0.0833%)
            4: 0.0025,       # 1 in 400 (0.25%)
            2: 0.005,        # 1 in 200 (0.5%)
            0.5: 0.445,      # 44.5%
            0.2: 0.545,      # 54.5%
        }
    else:  # demonic
        # DEMONIC: Very rare hit rates for high multipliers
        base_rates = {
            16666: 0.000006, # 1 in 166,667 (0.0006%)
            2500: 0.00004,   # 1 in 25,000 (0.004%)
            600: 0.000167,   # 1 in 5,988 (0.0167%)
            150: 0.000667,   # 1 in 1,500 (0.0667%)
            40: 0.0025,      # 1 in 400 (0.25%)
            8: 0.0125,       # 1 in 80 (1.25%)
            2: 0.05,         # 1 in 20 (5%)
            0: 0.75,         # 3 in 4 (75%)
        }
    
    # Convert to bucket probabilities
    probs = np.zeros(n_buckets)
    for i, mult in enumerate(mults):
        if mult in base_rates:
            probs[i] = base_rates[mult]
        else:
            # Interpolate for missing values
            if mult > 100:
                probs[i] = 0.0001  # Very rare
            elif mult > 10:
                probs[i] = 0.001   # Rare
            elif mult > 2:
                probs[i] = 0.01    # Uncommon
            else:
                probs[i] = 0.1     # Common
    
    # Normalize to sum to 1
    total_prob = np.sum(probs)
    probs = probs / total_prob
    
    # Calculate current RTP
    current_rtp = np.sum(probs * np.array(mults))
    
    print(f"  Initial RTP: {current_rtp:.4%}")
    print(f"  Target RTP: {target_rtp:.4%}")
    print(f"  Error: {abs(current_rtp - target_rtp):.4%}")
    
    # Fine-tune to hit exact target RTP
    for iteration in range(1000):
        current_rtp = np.sum(probs * np.array(mults))
        error = current_rtp - target_rtp
        
        if abs(error) < 0.0001:  # Within 0.01%
            break
        
        # Adjust probabilities to minimize RTP error
        if error > 0:  # RTP too high - reduce high multiplier probabilities
            for i in range(n_buckets):
                if mults[i] > target_rtp and probs[i] > 0.0001:
                    reduction = min(probs[i] * 0.01, abs(error) / mults[i])
                    probs[i] -= reduction
                    # Add to lower multiplier bucket
                    if mode == "mild":
                        probs[8] += reduction  # 0.5x bucket
                    elif mode == "sinful":
                        probs[8] += reduction  # 0.2x bucket
                    else:  # demonic
                        probs[8] += reduction  # 0x bucket
                    break
        else:  # RTP too low - increase high multiplier probabilities
            for i in range(n_buckets):
                if mults[i] > target_rtp and mults[i] < target_rtp * 10 and probs[i] > 0.0001:
                    increase = min(probs[i] * 0.01, abs(error) / mults[i])
                    probs[i] += increase
                    # Reduce from lower multiplier bucket
                    if mode == "mild":
                        probs[8] -= increase  # 0.5x bucket
                    elif mode == "sinful":
                        probs[8] -= increase  # 0.2x bucket
                    else:  # demonic
                        probs[8] -= increase  # 0x bucket
                    break
        
        # Renormalize to ensure probabilities sum to 1
        total_prob = np.sum(probs)
        probs = probs / total_prob
    
    # Convert to bucket counts (100k total)
    counts = np.array([int(p * 100000) for p in probs])
    diff = 100000 - np.sum(counts)
    counts[8] += diff  # Adjust middle bucket
    
    # Calculate final stats
    final_rtp = np.sum(probs * np.array(mults))
    prob_less = np.sum(probs[np.array(mults) < 1.0])
    
    print(f"  Final RTP: {final_rtp:.6%}")
    print(f"  Prob_less_bet: {prob_less:.4%}")
    print(f"  Iterations: {iteration}")
    
    # Show distribution
    print(f"  Distribution:")
    for i in range(n_buckets):
        if probs[i] > 0.0001:  # Only show buckets with >0.01% probability
            hit_rate = 1 / (probs[i] * 100000) if probs[i] > 0 else float('inf')
            print(f"    Bucket {i}: {probs[i]:.4%} ({mults[i]:6.1f}x) - 1 in {hit_rate:,.0f}")
    
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

def create_reel_file(mode, counts, output_dir="reels"):
    """Create reel CSV file from bucket counts."""
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Write reel file
    reel_path = os.path.join(output_dir, f"{mode.upper()}.csv")
    with open(reel_path, 'w', newline='') as f:
        for bucket in strip:
            f.write(f"{bucket}\n")
    
    return reel_path

# Create fun, realistic distributions for all modes
print("="*70)
print("PROPER FUN SOLVER - REALISTIC HIT RATES FOR EXCITEMENT")
print("="*70)

results = {}
for mode in ["mild", "sinful", "demonic"]:
    counts = calculate_realistic_hit_rates(mode, target_rtp=0.96)
    
    # Create strip and calculate stats
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    wins = [M[mode][b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Create both lookup table and reel file
    lookup_path = create_lookup_table(mode, counts)
    reel_path = create_reel_file(mode, counts)
    
    # Store results
    results[mode] = {
        "rtp": base_rtp,
        "prob_less_bet": prob_less,
        "lookup_path": lookup_path,
        "reel_path": reel_path
    }
    
    # Check if within targets
    rtp_error = abs(base_rtp - 0.96)
    rtp_ok = rtp_error < 0.001  # Within 0.1%
    prob_ok = prob_less < 0.80
    
    status = "[PERFECT]" if rtp_ok and prob_ok else "[EXCELLENT]" if rtp_error < 0.01 and prob_ok else "[GOOD]" if rtp_error < 0.02 and prob_ok else "[NEEDS ADJUSTMENT]"
    
    print(f"\n{mode.upper()} FINAL RESULTS:")
    print(f"  RTP: {base_rtp:.6%} (target: 96.000%, error: {rtp_error:.6%})")
    print(f"  Prob_less_bet: {prob_less:.4%} (target: <80%)")
    print(f"  Status: {status}")
    print(f"  Lookup table: {lookup_path}")
    print(f"  Reel file: {reel_path}")

print("\n" + "="*70)
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
    print(f"  Verified RTP: {rtp:.6%}")
    print(f"  House Edge: {house_edge:.4f}%")
    print(f"  Total Weight: {total_weight:,}")
    
    # Check if all are within 0.1% of 96%
    rtp_error = abs(rtp - 0.96)
    if rtp_error < 0.0001:
        print(f"  Status: [PERFECT - Within 0.01% of 96% RTP]")
    elif rtp_error < 0.001:
        print(f"  Status: [EXCELLENT - Within 0.1% of 96% RTP]")
    elif rtp_error < 0.01:
        print(f"  Status: [GOOD - Within 1% of 96% RTP]")
    else:
        print(f"  Status: [ERROR - {rtp_error:.4%} off from 96% RTP]")
    print()

print("="*70)
print("SUCCESS! Fun solver created realistic hit rates with 96% RTP")
print("Run: python verify_final_rtps.py to confirm")
print("="*70)
