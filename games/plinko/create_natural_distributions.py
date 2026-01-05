"""Create natural bell-curve Plinko distributions that feel like real physics."""

import numpy as np
from scipy.stats import norm
import os
from game_config import GameConfig

def create_bell_curve_probabilities(num_buckets=17, sharpness=2.5):
    """Create natural bell curve probabilities centered at middle bucket.
    
    Args:
        num_buckets: Number of buckets (17 for Plinko)
        sharpness: How sharp the bell curve is (lower = flatter, higher = sharper)
                   Realistic Plinko should be around 2.0-3.0
    
    Returns:
        Array of probabilities that sum to 1.0
    """
    center = (num_buckets - 1) / 2  # 8 for 17 buckets
    
    # Create positions (0 to 16)
    positions = np.arange(num_buckets)
    
    # Calculate bell curve (normal distribution)
    probabilities = norm.pdf(positions, loc=center, scale=sharpness)
    
    # Normalize to sum to 1.0
    probabilities = probabilities / np.sum(probabilities)
    
    return probabilities

def adjust_for_rtp(probabilities, multipliers, target_rtp, max_iterations=50000):
    """Adjust probabilities to hit target RTP while maintaining bell curve shape.
    
    Strategy: Shift probability mass between high and low multiplier buckets.
    """
    probabilities = probabilities.copy()
    
    for iteration in range(max_iterations):
        current_rtp = np.sum(probabilities * multipliers)
        error = target_rtp - current_rtp
        
        if abs(error) < 0.00001:
            break
        
        # Calculate how much we need to shift
        # If RTP too high: move probability from high-mult to low-mult buckets
        # If RTP too low: move probability from low-mult to high-mult buckets
        
        if error > 0:  # Need to increase RTP
            # Move from lowest mult bucket to highest mult bucket
            # But keep transfers small to preserve shape
            donor_idx = np.argmin(multipliers)  # Bucket with lowest multiplier
            recipient_idx = np.argmax(multipliers)  # Bucket with highest multiplier
            
            if probabilities[donor_idx] > 0.00001:
                # Transfer a tiny amount
                transfer = min(0.00001, probabilities[donor_idx] * 0.1, abs(error) / (multipliers[recipient_idx] - multipliers[donor_idx]))
                probabilities[donor_idx] -= transfer
                probabilities[recipient_idx] += transfer
        
        else:  # Need to decrease RTP (error < 0)
            # Move from highest mult bucket to lowest mult bucket
            donor_idx = np.argmax(multipliers)  # Bucket with highest multiplier
            recipient_idx = np.argmin(multipliers)  # Bucket with lowest multiplier
            
            if probabilities[donor_idx] > 0.00001:
                # Transfer a tiny amount
                transfer = min(0.00001, probabilities[donor_idx] * 0.1, abs(error) / (multipliers[donor_idx] - multipliers[recipient_idx]))
                probabilities[donor_idx] -= transfer
                probabilities[recipient_idx] += transfer
    
    return probabilities

def probabilities_to_csv(probabilities, output_path, total_weight=100000):
    """Convert probabilities to weighted CSV file."""
    # Convert to integer weights
    weights = np.round(probabilities * total_weight).astype(int)
    
    # Adjust to exactly total_weight
    diff = total_weight - np.sum(weights)
    if diff > 0:
        # Add to largest probability buckets
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(diff):
            weights[sorted_indices[i % len(sorted_indices)]] += 1
    elif diff < 0:
        # Remove from largest probability buckets
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(abs(diff)):
            idx = sorted_indices[i % len(sorted_indices)]
            if weights[idx] > 0:
                weights[idx] -= 1
    
    # Create bucket list
    bucket_list = []
    for bucket_idx, weight in enumerate(weights):
        bucket_list.extend([bucket_idx] * int(weight))
    
    # Shuffle for randomness
    np.random.shuffle(bucket_list)
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for bucket in bucket_list:
            f.write(f"{bucket}\n")
    
    return weights

def main():
    print("="*70)
    print("NATURAL PLINKO DISTRIBUTION GENERATOR")
    print("Bell curve physics - realistic and fun!")
    print("="*70)
    print()
    
    config = GameConfig()
    
    # Target RTPs within 0.5% margin
    targets = {
        "mild": {"rtp": 0.9525, "sharpness": 2.8},     # Tight bell curve
        "sinful": {"rtp": 0.9500, "sharpness": 2.5},   # Medium spread
        "demonic": {"rtp": 0.9550, "sharpness": 2.2},  # Wider spread (more variance)
    }
    
    results = {}
    
    for mode_name in ["mild", "sinful", "demonic"]:
        print(f"\n{'='*70}")
        print(f"GENERATING {mode_name.upper()} - Natural Bell Curve Distribution")
        print(f"{'='*70}\n")
        
        target_rtp = targets[mode_name]["rtp"]
        sharpness = targets[mode_name]["sharpness"]
        multipliers = np.array(config.bucket_multipliers[mode_name])
        
        # Create initial bell curve
        probabilities = create_bell_curve_probabilities(num_buckets=17, sharpness=sharpness)
        
        print(f"Initial bell curve (sharpness={sharpness}):")
        initial_rtp = np.sum(probabilities * multipliers)
        print(f"  RTP before adjustment: {initial_rtp:.6f}")
        
        # Adjust to target RTP while preserving shape
        probabilities = adjust_for_rtp(probabilities, multipliers, target_rtp)
        
        actual_rtp = np.sum(probabilities * multipliers)
        print(f"  Target RTP: {target_rtp:.6f}")
        print(f"  Actual RTP: {actual_rtp:.6f}")
        print(f"  Error: {abs(actual_rtp - target_rtp):.8f}")
        
        # Calculate statistics
        prob_less_bet = np.sum(probabilities[multipliers < 1.0])
        variance = np.sum(probabilities * (multipliers - actual_rtp) ** 2)
        std = np.sqrt(variance)
        
        print(f"\n  Statistics:")
        print(f"    Prob < Bet: {prob_less_bet:.4f} ({prob_less_bet*100:.2f}%)")
        print(f"    Std Dev: {std:.2f}")
        print(f"    Variance: {variance:.2f}")
        
        # Show distribution
        print(f"\n  Bucket Distribution (Bell Curve):")
        print(f"  {'Bucket':<8} {'Mult':<10} {'Probability':<15} {'Hit Rate':<20} {'Visual'}")
        print(f"  {'-'*75}")
        
        for i in range(17):
            prob = probabilities[i]
            mult = multipliers[i]
            hr = 1.0 / prob if prob > 0 else float('inf')
            hr_str = f"1 in {hr:.0f}" if hr != float('inf') else "Never"
            
            # Visual bar (using ASCII)
            bar_length = int(prob * 200)  # Scale for visibility
            bar = '#' * bar_length
            
            print(f"  {i:<8} {mult:<10.2f} {prob:<15.6f} {hr_str:<20} {bar}")
        
        # Save to CSV
        csv_path = os.path.join("reels", f"{mode_name.upper()}.csv")
        weights = probabilities_to_csv(probabilities, csv_path, total_weight=100000)
        
        print(f"\n  [OK] Saved to: {csv_path}")
        
        results[mode_name] = {
            "rtp": actual_rtp,
            "target": target_rtp,
            "error": abs(actual_rtp - target_rtp),
            "probabilities": probabilities,
        }
    
    # Summary
    print("\n" + "="*70)
    print("RTP SUMMARY - All Modes")
    print("="*70)
    print(f"{'Mode':<12} {'Target RTP':<15} {'Actual RTP':<15} {'Error':<12} {'House Edge'}")
    print("-" * 70)
    
    for mode in ["mild", "sinful", "demonic"]:
        r = results[mode]
        house_edge = (1 - r["rtp"]) * 100
        print(f"{mode.upper():<12} {r['target']:.6f}      {r['rtp']:.6f}      {r['error']:.8f}   {house_edge:.2f}%")
    
    # Calculate range
    rtps = [results[m]["rtp"] for m in ["mild", "sinful", "demonic"]]
    rtp_range = max(rtps) - min(rtps)
    
    print()
    print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.4f}%)")
    
    if rtp_range <= 0.005:
        print("\n[OK] SUCCESS! All modes within 0.5% margin!")
    elif rtp_range <= 0.0075:
        print("\n[WARNING] CLOSE! Within 0.75% margin")
    else:
        print(f"\n[ERROR] FAILED: Exceeds 0.5% margin by {(rtp_range-0.005)*100:.2f}%")
    
    print()
    print("="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Run simulations: python games/plinko/run.py")
    print("2. Hell's Storm modes will inherit these natural distributions")
    print("3. Gameplay will feel fair and exciting with proper variance!")
    print()

if __name__ == "__main__":
    main()

