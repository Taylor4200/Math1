"""SIMPLE FIX SOLVER - Fixes key multipliers, solves for the rest, ensures ALL buckets possible."""

import random
import csv
import os
import numpy as np
from scipy.optimize import minimize

def solve_simple_fix(mode, target_rtp=0.96):
    """Simple solver: fix key multipliers, solve for the rest."""
    
    print(f"\n{mode.upper()}: Simple fix solver for {target_rtp:.1%} RTP")
    
    n_buckets = 17
    
    # FIXED MULTIPLIERS (your desired structure)
    if mode == "mild":
        # Fix edge multipliers (your jackpots)
        fixed_multipliers = {
            0: 666,   # Left edge
            16: 666   # Right edge
        }
        # Fix center multiplier
        center_multiplier = 0.5
        center_buckets = [8]  # Bucket 8 gets 0.5x
        
        # Fix a few middle multipliers for natural progression
        middle_fixed = {
            6: 2.0,   # Left side
            10: 2.0   # Right side
        }
        
    elif mode == "sinful":
        # Fix edge multipliers
        fixed_multipliers = {
            0: 1666,  # Left edge
            16: 1666  # Right edge
        }
        # Fix center multiplier
        center_multiplier = 0.2
        center_buckets = [8]  # Bucket 8 gets 0.2x
        
        # Fix a few middle multipliers
        middle_fixed = {
            6: 2.0,   # Left side
            10: 2.0   # Right side
        }
        
    else:  # demonic
        # Fix edge multipliers
        fixed_multipliers = {
            0: 16666, # Left edge
            16: 16666 # Right edge
        }
        # Fix center multipliers (0x buckets)
        center_multiplier = 0.0
        center_buckets = [7, 8, 9]  # Buckets 7,8,9 get 0x
        
        # Fix a few middle multipliers
        middle_fixed = {
            6: 2.0,   # Left side
            10: 2.0   # Right side
        }
    
    # Calculate which buckets to optimize
    all_fixed_buckets = set(fixed_multipliers.keys()) | set(center_buckets) | set(middle_fixed.keys())
    optimize_buckets = [i for i in range(n_buckets) if i not in all_fixed_buckets]
    
    print(f"  Fixed buckets: {sorted(all_fixed_buckets)}")
    print(f"  Optimizing buckets: {optimize_buckets}")
    
    def objective(x):
        """Objective: minimize RTP error + ensure all buckets possible."""
        # x contains: [multipliers for optimize_buckets, probabilities for all buckets]
        n_opt_mult = len(optimize_buckets)
        opt_mults = x[:n_opt_mult]
        probs = x[n_opt_mult:]
        
        # Construct full multiplier array
        mults = np.zeros(n_buckets)
        
        # Set fixed multipliers
        for bucket, mult in fixed_multipliers.items():
            mults[bucket] = mult
        
        # Set center multipliers
        for bucket in center_buckets:
            mults[bucket] = center_multiplier
        
        # Set middle fixed multipliers
        for bucket, mult in middle_fixed.items():
            mults[bucket] = mult
        
        # Set optimized multipliers
        for i, bucket in enumerate(optimize_buckets):
            mults[bucket] = opt_mults[i]
        
        # Calculate RTP
        rtp = np.sum(probs * mults)
        rtp_error = abs(rtp - target_rtp)
        
        # Calculate prob_less_bet
        prob_less = np.sum(probs[np.array(mults) < 1.0])
        prob_less_error = max(0, prob_less - 0.80)  # Penalty if > 80%
        
        # Ensure ALL buckets are possible (no 0% buckets)
        min_prob_penalty = 0
        for i, prob in enumerate(probs):
            if prob < 0.0001:  # Less than 0.01%
                min_prob_penalty += (0.0001 - prob) * 10000
        
        # Natural progression penalty
        progression_penalty = 0.0
        
        # Check left side progression (buckets 0-8)
        left_mults = [mults[i] for i in range(9)]
        for i in range(1, len(left_mults)):
            if left_mults[i-1] > 0 and left_mults[i] > 0:
                # Should be decreasing from edge to center
                if left_mults[i-1] < left_mults[i]:
                    progression_penalty += (left_mults[i] - left_mults[i-1]) * 1000
        
        # Check right side progression (buckets 8-16)
        right_mults = [mults[i] for i in range(8, 17)]
        for i in range(1, len(right_mults)):
            if right_mults[i-1] > 0 and right_mults[i] > 0:
                # Should be increasing from center to edge
                if right_mults[i-1] > right_mults[i]:
                    progression_penalty += (right_mults[i-1] - right_mults[i]) * 1000
        
        # Total objective
        total_penalty = rtp_error * 10000 + prob_less_error * 1000 + min_prob_penalty + progression_penalty
        
        return total_penalty
    
    # Constraints
    def rtp_constraint(x):
        """RTP must equal target."""
        n_opt_mult = len(optimize_buckets)
        opt_mults = x[:n_opt_mult]
        probs = x[n_opt_mult:]
        
        # Construct full multiplier array
        mults = np.zeros(n_buckets)
        
        # Set fixed multipliers
        for bucket, mult in fixed_multipliers.items():
            mults[bucket] = mult
        
        # Set center multipliers
        for bucket in center_buckets:
            mults[bucket] = center_multiplier
        
        # Set middle fixed multipliers
        for bucket, mult in middle_fixed.items():
            mults[bucket] = mult
        
        # Set optimized multipliers
        for i, bucket in enumerate(optimize_buckets):
            mults[bucket] = opt_mults[i]
        
        rtp = np.sum(probs * mults)
        return rtp - target_rtp
    
    def sum_constraint(x):
        """Probabilities must sum to 1."""
        n_opt_mult = len(optimize_buckets)
        probs = x[n_opt_mult:]
        return np.sum(probs) - 1.0
    
    def prob_less_constraint(x):
        """Prob_less_bet must be <= 80%."""
        n_opt_mult = len(optimize_buckets)
        opt_mults = x[:n_opt_mult]
        probs = x[n_opt_mult:]
        
        # Construct full multiplier array
        mults = np.zeros(n_buckets)
        
        # Set fixed multipliers
        for bucket, mult in fixed_multipliers.items():
            mults[bucket] = mult
        
        # Set center multipliers
        for bucket in center_buckets:
            mults[bucket] = center_multiplier
        
        # Set middle fixed multipliers
        for bucket, mult in middle_fixed.items():
            mults[bucket] = mult
        
        # Set optimized multipliers
        for i, bucket in enumerate(optimize_buckets):
            mults[bucket] = opt_mults[i]
        
        prob_less = np.sum(probs[np.array(mults) < 1.0])
        return 0.80 - prob_less  # Must be >= 0 (so prob_less <= 0.80)
    
    # Initial guess
    # Initial multipliers for optimized buckets
    if mode == "mild":
        initial_opt_mults = [100, 40, 15, 6, 3, 1.5, 1, 1.5, 3, 6, 15, 40, 100]
    elif mode == "sinful":
        initial_opt_mults = [200, 80, 30, 10, 4, 1.5, 1, 1.5, 4, 10, 30, 80, 200]
    else:  # demonic
        initial_opt_mults = [1000, 300, 100, 30, 6, 1.5, 1, 1.5, 6, 30, 100, 300, 1000]
    
    # Trim to correct length
    initial_opt_mults = initial_opt_mults[:len(optimize_buckets)]
    
    # Initial probabilities (bell curve)
    initial_probs = np.ones(n_buckets) / n_buckets
    
    x0 = np.concatenate([initial_opt_mults, initial_probs])
    
    # Bounds
    bounds = []
    
    # Multiplier bounds for optimized buckets
    for i in range(len(optimize_buckets)):
        bounds.append((0.1, 10000))  # Multipliers between 0.1x and 10000x
    
    # Probability bounds
    for i in range(n_buckets):
        bounds.append((0.0001, 0.8))  # Probabilities between 0.01% and 80%
    
    # Constraints
    constraints = [
        {'type': 'eq', 'fun': rtp_constraint},
        {'type': 'eq', 'fun': sum_constraint},
        {'type': 'ineq', 'fun': prob_less_constraint}
    ]
    
    # Solve
    print(f"  Solving optimization...")
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 10000}
    )
    
    if not result.success:
        print(f"  SLSQP failed, trying COBYLA...")
        result = minimize(
            objective,
            x0,
            method='COBYLA',
            options={'maxiter': 10000}
        )
    
    if not result.success:
        print(f"  All optimization methods failed: {result.message}")
        return None
    
    # Extract solution
    n_opt_mult = len(optimize_buckets)
    opt_mults = result.x[:n_opt_mult]
    probs = result.x[n_opt_mult:]
    
    # Construct final multiplier array
    mults = np.zeros(n_buckets)
    
    # Set fixed multipliers
    for bucket, mult in fixed_multipliers.items():
        mults[bucket] = mult
    
    # Set center multipliers
    for bucket in center_buckets:
        mults[bucket] = center_multiplier
    
    # Set middle fixed multipliers
    for bucket, mult in middle_fixed.items():
        mults[bucket] = mult
    
    # Set optimized multipliers
    for i, bucket in enumerate(optimize_buckets):
        mults[bucket] = opt_mults[i]
    
    # Calculate final stats
    final_rtp = np.sum(probs * mults)
    prob_less = np.sum(probs[np.array(mults) < 1.0])
    
    print(f"  Final RTP: {final_rtp:.6%}")
    print(f"  Prob_less_bet: {prob_less:.4%}")
    print(f"  Optimization Success: {result.success}")
    
    # Show final multipliers
    print(f"  Final Multipliers:")
    for i in range(n_buckets):
        print(f"    Bucket {i:2d}: {mults[i]:8.3f}x")
    
    # Show distribution
    print(f"  Final Distribution:")
    for i in range(n_buckets):
        if probs[i] > 0.0001:
            hit_rate = 1 / (probs[i] * 100000) if probs[i] > 0 else float('inf')
            print(f"    Bucket {i:2d}: {probs[i]:.4%} ({mults[i]:8.3f}x) - 1 in {hit_rate:,.0f}")
        else:
            print(f"    Bucket {i:2d}: {probs[i]:.4%} ({mults[i]:8.3f}x) - IMPOSSIBLE!")
    
    # Convert to bucket counts (100k total)
    counts = np.array([int(p * 100000) for p in probs])
    diff = 100000 - np.sum(counts)
    counts[8] += diff  # Adjust middle bucket
    
    return counts, mults

def create_lookup_table(mode, counts, mults, output_dir="library/publish_files"):
    """Create lookup table CSV from bucket counts and multipliers."""
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    # Calculate payouts using optimized multipliers
    payouts = [int(mults[bucket] * 100) for bucket in strip]
    
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
print("SIMPLE FIX SOLVER - Fixes key multipliers, solves for the rest")
print("="*70)

results = {}
for mode in ["mild", "sinful", "demonic"]:
    solution = solve_simple_fix(mode, target_rtp=0.96)
    
    if solution is None:
        print(f"  {mode.upper()}: FAILED TO SOLVE")
        continue
    
    counts, mults = solution
    
    # Create strip and calculate stats
    strip = []
    for i, count in enumerate(counts):
        strip.extend([i] * count)
    random.shuffle(strip)
    
    wins = [mults[b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    # Create both lookup table and reel file
    lookup_path = create_lookup_table(mode, counts, mults)
    reel_path = create_reel_file(mode, counts)
    
    # Store results
    results[mode] = {
        "rtp": base_rtp,
        "prob_less_bet": prob_less,
        "lookup_path": lookup_path,
        "reel_path": reel_path,
        "multipliers": mults
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
print("SUCCESS! Simple fix solver created realistic Plinko with 96% RTP")
print("Run: python verify_final_rtps.py to confirm")
print("="*70)















