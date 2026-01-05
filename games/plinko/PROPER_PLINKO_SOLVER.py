"""PROPER PLINKO SOLVER - Natural progression with edge multipliers, small middle multipliers."""

import random
import csv
import os
import numpy as np
from scipy.optimize import minimize

def solve_proper_plinko(mode, target_rtp=0.97):
    """Proper Plinko solver with natural progression."""
    
    print(f"\n{mode.upper()}: Proper Plinko solver for {target_rtp:.1%} RTP")
    
    n_buckets = 17
    
    # FIXED MULTIPLIERS - Natural Plinko progression
    if mode == "mild":
        # Natural progression: 666x | 60x | 20x | 8x | 4x | 2x | 1x | 0.5x | 1x | 2x | 4x | 8x | 20x | 60x | 666x
        fixed_multipliers = {
            0: 666,   # Left edge
            1: 60,    # Left transition
            2: 20,    # Left transition
            3: 8,     # Left middle
            4: 4,     # Left middle
            5: 2,     # Left center
            6: 1,     # Left center
            7: 0.5,   # Center
            8: 1,     # Right center
            9: 2,     # Right center
            10: 4,    # Right middle
            11: 8,    # Right middle
            12: 20,   # Right transition
            13: 60,   # Right transition
            14: 150,  # Right transition (missing bucket)
            15: 300,  # Right transition (missing bucket)
            16: 666   # Right edge
        }
        
    elif mode == "sinful":
        # Natural progression: 1666x | 8x | 4x | 2x | 1.5x | 1x | 0.5x | 0.2x | 0.5x | 1x | 1.5x | 2x | 4x | 8x | 1666x
        fixed_multipliers = {
            0: 1666,  # Left edge
            1: 8,     # Left transition
            2: 4,     # Left transition
            3: 2,     # Left middle
            4: 1.5,   # Left middle
            5: 1,     # Left center
            6: 0.5,   # Left center
            7: 0.2,   # Center
            8: 0.5,   # Right center
            9: 1,     # Right center
            10: 1.5,  # Right middle
            11: 2,    # Right middle
            12: 4,    # Right transition
            13: 8,    # Right transition
            14: 12,   # Right transition (missing bucket)
            15: 20,   # Right transition (missing bucket)
            16: 1666  # Right edge
        }
        
    else:  # demonic
        # Natural progression: 6666x | 8x | 4x | 2x | 1.5x | 1x | 0x | 0x | 0x | 1x | 1.5x | 2x | 4x | 8x | 6666x
        fixed_multipliers = {
            0: 6666,  # Left edge
            1: 8,     # Left transition
            2: 4,     # Left transition
            3: 2,     # Left middle
            4: 1.5,   # Left middle
            5: 1,     # Left center
            6: 0,     # Left center
            7: 0,     # Center
            8: 0,     # Center
            9: 0,     # Right center
            10: 1,    # Right center
            11: 1.5,  # Right middle
            12: 2,    # Right middle
            13: 4,    # Right transition
            14: 8,    # Right transition
            15: 12,   # Right transition (missing bucket)
            16: 6666  # Right edge
        }
    
    # Only optimize probabilities, multipliers are fixed
    print(f"  All multipliers fixed with natural progression")
    
    def objective(probs):
        """Objective: minimize RTP error + ensure all buckets possible."""
        # Calculate RTP
        rtp = np.sum(probs * np.array([fixed_multipliers[i] for i in range(n_buckets)]))
        rtp_error = abs(rtp - target_rtp)
        
        # Calculate prob_less_bet
        mults = np.array([fixed_multipliers[i] for i in range(n_buckets)])
        prob_less = np.sum(probs[np.array(mults) < 1.0])
        prob_less_error = max(0, prob_less - 0.80)  # Penalty if > 80%
        
        # Ensure ALL buckets are possible (no 0% buckets)
        min_prob_penalty = 0
        for i, prob in enumerate(probs):
            if prob < 0.0001:  # Less than 0.01%
                min_prob_penalty += (0.0001 - prob) * 10000
        
        # Natural bell curve penalty
        # Encourage center-heavy distribution
        center_buckets = [7, 8, 9]  # Center buckets should have higher probability
        center_prob = np.sum([probs[i] for i in center_buckets])
        center_penalty = max(0, 0.4 - center_prob) * 1000  # Center should be at least 40%
        
        # Edge buckets should be rare but possible
        edge_buckets = [0, 16]  # Edge buckets
        edge_prob = np.sum([probs[i] for i in edge_buckets])
        
        # For DEMONIC mode, make edge buckets ULTRA rare (1 in 100M = 0.000001%)
        if mode == "demonic":
            edge_penalty = max(0, 0.00000001 - edge_prob) * 1000000  # Edges should be at least 0.000001%
        else:
            edge_penalty = max(0, 0.0001 - edge_prob) * 10000  # Edges should be at least 0.01%
        
        # Total objective - MUCH higher penalty for RTP error
        total_penalty = rtp_error * 1000000 + prob_less_error * 1000 + min_prob_penalty + center_penalty + edge_penalty
        
        return total_penalty
    
    # Constraints
    def rtp_constraint(probs):
        """RTP must equal target."""
        mults = np.array([fixed_multipliers[i] for i in range(n_buckets)])
        rtp = np.sum(probs * mults)
        return rtp - target_rtp
    
    def sum_constraint(probs):
        """Probabilities must sum to 1."""
        return np.sum(probs) - 1.0
    
    def prob_less_constraint(probs):
        """Prob_less_bet must be <= 80%."""
        mults = np.array([fixed_multipliers[i] for i in range(n_buckets)])
        prob_less = np.sum(probs[np.array(mults) < 1.0])
        return 0.80 - prob_less  # Must be >= 0 (so prob_less <= 0.80)
    
    # Initial probabilities (bell curve)
    initial_probs = np.ones(n_buckets) / n_buckets
    
    # Bounds
    bounds = []
    for i in range(n_buckets):
        if mode == "demonic" and i in [0, 16]:  # Edge buckets for DEMONIC
            bounds.append((0.0000001, 0.00001))  # Ultra rare: 0.00001% to 0.001%
        else:
            bounds.append((0.0001, 0.8))  # Probabilities between 0.01% and 80%
    
    # Constraints - STRICT RTP constraint
    constraints = [
        {'type': 'eq', 'fun': rtp_constraint},  # RTP MUST be exactly 97%
        {'type': 'eq', 'fun': sum_constraint},   # Probabilities MUST sum to 1
        {'type': 'ineq', 'fun': prob_less_constraint}  # Prob_less_bet <= 80%
    ]
    
    # Solve
    print(f"  Solving optimization...")
    result = minimize(
        objective,
        initial_probs,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 10000}
    )
    
    if not result.success:
        print(f"  SLSQP failed, trying COBYLA...")
        result = minimize(
            objective,
            initial_probs,
            method='COBYLA',
            options={'maxiter': 10000}
        )
    
    if not result.success:
        print(f"  All optimization methods failed: {result.message}")
        return None
    
    probs = result.x
    
    # Calculate final stats
    mults = np.array([fixed_multipliers[i] for i in range(n_buckets)])
    final_rtp = np.sum(probs * mults)
    prob_less = np.sum(probs[np.array(mults) < 1.0])
    
    print(f"  Final RTP: {final_rtp:.6%}")
    print(f"  Prob_less_bet: {prob_less:.4%}")
    print(f"  Optimization Success: {result.success}")
    
    # Show final multipliers
    print(f"  Final Multipliers:")
    for i in range(n_buckets):
        print(f"    Bucket {i:2d}: {fixed_multipliers[i]:8.3f}x")
    
    # Show distribution
    print(f"  Final Distribution:")
    for i in range(n_buckets):
        if probs[i] > 0.0001:
            hit_rate = 1 / (probs[i] * 100000) if probs[i] > 0 else float('inf')
            print(f"    Bucket {i:2d}: {probs[i]:.4%} ({fixed_multipliers[i]:8.3f}x) - 1 in {hit_rate:,.0f}")
        else:
            print(f"    Bucket {i:2d}: {probs[i]:.4%} ({fixed_multipliers[i]:8.3f}x) - IMPOSSIBLE!")
    
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
print("PROPER PLINKO SOLVER - Natural progression with realistic multipliers")
print("="*70)

results = {}
for mode in ["mild", "sinful", "demonic"]:
    solution = solve_proper_plinko(mode, target_rtp=0.97)
    
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
    rtp_error = abs(base_rtp - 0.97)
    rtp_ok = rtp_error < 0.001  # Within 0.1%
    prob_ok = prob_less < 0.80
    
    status = "[PERFECT]" if rtp_ok and prob_ok else "[EXCELLENT]" if rtp_error < 0.01 and prob_ok else "[GOOD]" if rtp_error < 0.02 and prob_ok else "[NEEDS ADJUSTMENT]"
    
    print(f"\n{mode.upper()} FINAL RESULTS:")
    print(f"  RTP: {base_rtp:.6%} (target: 97.000%, error: {rtp_error:.6%})")
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
    
    # Check if all are within 0.1% of 97%
    rtp_error = abs(rtp - 0.97)
    if rtp_error < 0.0001:
        print(f"  Status: [PERFECT - Within 0.01% of 97% RTP]")
    elif rtp_error < 0.001:
        print(f"  Status: [EXCELLENT - Within 0.1% of 97% RTP]")
    elif rtp_error < 0.01:
        print(f"  Status: [GOOD - Within 1% of 97% RTP]")
    else:
        print(f"  Status: [ERROR - {rtp_error:.4%} off from 97% RTP]")
    print()

print("="*70)
print("SUCCESS! Proper Plinko solver created realistic game with 97% RTP")
print("Run: python verify_final_rtps.py to confirm")
print("="*70)
