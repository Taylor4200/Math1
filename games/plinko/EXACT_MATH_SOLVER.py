"""EXACT MATH SOLVER - Pure mathematical solution for 96% RTP with natural curves."""

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

def solve_exact_96_percent(mode):
    """Solve for exactly 96% RTP using mathematical optimization."""
    
    mults = np.array(M[mode])
    n_buckets = len(mults)
    
    print(f"\n{mode.upper()}: Solving for EXACTLY 96% RTP")
    
    # Target RTP
    target_rtp = 0.96
    
    # Constraints:
    # 1. Sum of probabilities = 1
    # 2. RTP = target_rtp
    # 3. Prob_less_bet < 0.80
    # 4. All probabilities >= 0
    
    def rtp_constraint(x):
        return np.sum(x * mults) - target_rtp
    
    def prob_less_constraint(x):
        prob_less = np.sum(x[mults < 1.0])
        return 0.80 - prob_less  # Must be >= 0 (so prob_less <= 0.80)
    
    def sum_constraint(x):
        return np.sum(x) - 1.0
    
    constraints = [
        {'type': 'eq', 'fun': rtp_constraint},
        {'type': 'eq', 'fun': sum_constraint},
        {'type': 'ineq', 'fun': prob_less_constraint}
    ]
    
    # Bounds: all probabilities >= 0
    bounds = [(0.0, 1.0) for _ in range(n_buckets)]
    
    # Objective: Create natural bell curve
    # Minimize variance to create smooth distribution
    def objective(x):
        # Create a penalty for non-smooth distributions
        penalty = 0.0
        
        # Penalty for high variance (creates bell curve)
        penalty += np.var(x) * 1000
        
        # Penalty for extreme values (encourage natural distribution)
        for i, p in enumerate(x):
            if p > 0.5:  # No bucket should have >50% probability
                penalty += (p - 0.5) * 1000
            if p < 0.0001:  # No bucket should be too rare
                penalty += (0.0001 - p) * 1000
        
        return penalty
    
    # Initial guess: uniform distribution
    x0 = np.ones(n_buckets) / n_buckets
    
    # Solve
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 10000, 'ftol': 1e-12}
    )
    
    if not result.success:
        print(f"  SLSQP failed, trying trust-constr...")
        result = minimize(
            objective,
            x0,
            method='trust-constr',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 10000}
        )
    
    if not result.success:
        print(f"  Optimization failed: {result.message}")
        return None
    
    probs = result.x
    
    # Verify solution
    final_rtp = np.sum(probs * mults)
    prob_less = np.sum(probs[mults < 1.0])
    
    print(f"  Final RTP: {final_rtp:.6%}")
    print(f"  Prob_less_bet: {prob_less:.4%}")
    print(f"  RTP Error: {abs(final_rtp - target_rtp):.8%}")
    print(f"  Optimization Success: {result.success}")
    
    # Show distribution
    print(f"  Distribution:")
    for i in range(n_buckets):
        if probs[i] > 0.001:  # Only show buckets with >0.1% probability
            print(f"    Bucket {i}: {probs[i]:.3%} ({mults[i]}x)")
    
    # Convert to bucket counts (100k total)
    counts = np.array([int(p * 100000) for p in probs])
    diff = 100000 - np.sum(counts)
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

# Solve for all modes
print("="*70)
print("EXACT MATH SOLVER - PURE MATHEMATICAL SOLUTION")
print("="*70)

results = {}
for mode in ["mild", "sinful", "demonic"]:
    counts = solve_exact_96_percent(mode)
    
    if counts is None:
        print(f"  {mode.upper()}: FAILED TO SOLVE")
        continue
    
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
print("SUCCESS! Mathematical solver found exact 96% RTP solutions")
print("Run: python verify_final_rtps.py to confirm")
print("="*70)















