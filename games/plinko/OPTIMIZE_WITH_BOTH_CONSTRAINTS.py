"""Optimize weights with BOTH RTP and PLB constraints using scipy."""
from scipy.optimize import minimize
import numpy as np

def optimize_mode(mode_name, target_rtp, multipliers, max_plb=0.79):
    """Optimize weights to hit target RTP and PLB < max_plb."""
    num_buckets = len(multipliers)
    
    # Objective: minimize deviation from target RTP
    def objective(weights):
        total_w = weights.sum()
        if total_w == 0:
            return 1e10
        
        probs = weights / total_w
        rtp = sum(p * m for p, m in zip(probs, multipliers))
        
        # Penalty for being far from target RTP
        rtp_error = (rtp - target_rtp) ** 2
        
        # Penalty for PLB being too high
        plb = sum(p for p, m in zip(probs, multipliers) if m < 1.0)
        plb_penalty = max(0, plb - max_plb) ** 2 * 1000  # Heavy penalty if PLB > max
        
        return rtp_error + plb_penalty
    
    # Constraints
    def constraint_sum_to_one(weights):
        return weights.sum() - 1.0
    
    # Bounds: each weight between 0.0001% and 90%
    bounds = [(0.000001, 0.9) for _ in range(num_buckets)]
    
    # Initial guess: uniform
    x0 = np.ones(num_buckets) / num_buckets
    
    # Optimize
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints={'type': 'eq', 'fun': constraint_sum_to_one},
        options={'maxiter': 50000, 'ftol': 1e-9}
    )
    
    if not result.success:
        print(f"  WARNING: {result.message}")
    
    # Convert to integer weights
    probs = result.x / result.x.sum()
    weights = (probs * 1000000).astype(int)
    
    # Calculate metrics
    total_w = weights.sum()
    total_p = sum(w * m * 100 for w, m in zip(weights, multipliers))
    rtp = total_p / total_w / 100
    he = (1 - rtp) * 100
    
    plb_w = sum(w for w, m in zip(weights, multipliers) if m < 1.0)
    plb = plb_w / total_w
    
    return weights, rtp, plb, he

# Configurations
mild_mults = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
sinful_mults = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
demonic_mults = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

print("="*70)
print("OPTIMIZING WITH RTP + PLB CONSTRAINTS")
print("="*70)

# Optimize each mode with adjusted targets for perfect 0.50% margins
# NOTE: With 5% bonus peg, total RTP will be higher than these base targets
# Target base RTPs: MILD 96%, SINFUL 95.5%, DEMONIC 95%
mild_weights, mild_rtp, mild_plb, mild_he = optimize_mode("mild", 0.96, mild_mults, max_plb=0.79)
sinful_weights, sinful_rtp, sinful_plb, sinful_he = optimize_mode("sinful", 0.955, sinful_mults, max_plb=0.79)
demonic_weights, demonic_rtp, demonic_plb, demonic_he = optimize_mode("demonic", 0.95, demonic_mults, max_plb=0.79)

# Display results
for mode_name, weights, mults, rtp, plb, he in [
    ("mild", mild_weights, mild_mults, mild_rtp, mild_plb, mild_he),
    ("sinful", sinful_weights, sinful_mults, sinful_rtp, sinful_plb, sinful_he),
    ("demonic", demonic_weights, demonic_mults, demonic_rtp, demonic_plb, demonic_he),
]:
    print(f"\n{mode_name.upper()}:")
    print(f"  RTP: {rtp:.4%}")
    print(f"  House Edge: {he:.2f}%")
    print(f"  Prob_less_bet: {plb:.4%} {'[OK]' if plb < 0.8 else '[OVER]'}")
    
    # Write file
    lines = []
    for i, (w, m) in enumerate(zip(weights, mults)):
        book_id = i + 1
        payout_cents = int(m * 100)
        lines.append(f"{book_id},{w},{payout_cents}")
    
    # Write in Rust optimizer output format (17 rows with proper weights)
    output_path = f"library/optimization_files/{mode_name}_0_1.csv"
    with open(output_path, 'w') as f:
        f.write(f"Name,Optimized_{mode_name}\n")
        f.write(f"Score,0.0\n")
        f.write(f"LockedUpRTP,\n")
        f.write(f"Rtp,{rtp}\n")
        f.write("Win Ranges\n")
        f.write("Distribution\n")
        for line in lines:
            parts = line.split(',')
            # Convert cents to dollars for optimizer format
            payout_dollars = int(parts[2]) / 100.0
            f.write(f"{parts[0]},{parts[1]},{payout_dollars}\n")
    
    print(f"  [OK] Written to {output_path} (17 rows, weighted)")

# Check margins
print("\n" + "="*70)
print("HOUSE EDGE MARGINS")
print("="*70)
print(f"SINFUL - MILD:    {sinful_he - mild_he:+.2f}% (target: +0.50%)")
print(f"DEMONIC - SINFUL: {demonic_he - sinful_he:+.2f}% (target: +0.50%)")

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)

