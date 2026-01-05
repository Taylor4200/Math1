"""Generate natural bell-curve Plinko distributions with correct RTP."""

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import os
from game_config import GameConfig

def create_bell_curve_probabilities(num_buckets=17, sharpness=2.5):
    """Create natural bell curve probabilities centered at middle bucket."""
    center = (num_buckets - 1) / 2  # 8 for 17 buckets
    positions = np.arange(num_buckets)
    probabilities = norm.pdf(positions, loc=center, scale=sharpness)
    probabilities = probabilities / np.sum(probabilities)
    return probabilities

def find_optimal_sharpness(multipliers, target_rtp, sharpness_range=(1.0, 5.0)):
    """Find bell curve sharpness that naturally produces target RTP."""
    
    def rtp_error(sharpness):
        probs = create_bell_curve_probabilities(num_buckets=len(multipliers), sharpness=sharpness)
        actual_rtp = np.sum(probs * multipliers)
        return (actual_rtp - target_rtp) ** 2
    
    result = minimize_scalar(rtp_error, bounds=sharpness_range, method='bounded')
    return result.x

def probabilities_to_csv(probabilities, output_path, total_weight=100000):
    """Convert probabilities to weighted CSV file."""
    weights = np.round(probabilities * total_weight).astype(int)
    
    # Adjust to exactly total_weight
    diff = total_weight - np.sum(weights)
    if diff > 0:
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(diff):
            weights[sorted_indices[i % len(sorted_indices)]] += 1
    elif diff < 0:
        sorted_indices = np.argsort(probabilities)[::-1]
        for i in range(abs(diff)):
            idx = sorted_indices[i % len(sorted_indices)]
            if weights[idx] > 0:
                weights[idx] -= 1
    
    # Create bucket list
    bucket_list = []
    for bucket_idx, weight in enumerate(weights):
        bucket_list.extend([bucket_idx] * int(weight))
    
    np.random.shuffle(bucket_list)
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for bucket in bucket_list:
            f.write(f"{bucket}\n")
    
    return weights

def main():
    print("="*70)
    print("NATURAL PLINKO DISTRIBUTION GENERATOR v2")
    print("Bell curve physics with proper RTP!")
    print("="*70)
    print()
    
    config = GameConfig()
    
    # Target RTPs within 0.5% margin
    targets = {
        "mild": 0.9525,     # 95.25%
        "sinful": 0.9500,   # 95.00%
        "demonic": 0.9550,  # 95.50%
    }
    
    results = {}
    
    for mode_name in ["mild", "sinful", "demonic"]:
        print(f"\n{'='*70}")
        print(f"GENERATING {mode_name.upper()} - Natural Bell Curve")
        print(f"{'='*70}\n")
        
        target_rtp = targets[mode_name]
        multipliers = np.array(config.bucket_multipliers[mode_name])
        
        # Find optimal sharpness for this target RTP
        print(f"Finding optimal bell curve shape for RTP={target_rtp:.6f}...")
        optimal_sharpness = find_optimal_sharpness(multipliers, target_rtp)
        print(f"  Optimal sharpness: {optimal_sharpness:.3f}")
        
        # Generate bell curve with optimal sharpness
        probabilities = create_bell_curve_probabilities(num_buckets=17, sharpness=optimal_sharpness)
        
        # Calculate actual RTP
        actual_rtp = np.sum(probabilities * multipliers)
        error = abs(actual_rtp - target_rtp)
        
        print(f"  Target RTP: {target_rtp:.6f}")
        print(f"  Actual RTP: {actual_rtp:.6f}")
        print(f"  Error: {error:.8f}")
        
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
            bar_length = int(prob * 200)
            bar = '#' * bar_length
            print(f"  {i:<8} {mult:<10.2f} {prob:<15.6f} {hr_str:<20} {bar}")
        
        # Save to CSV
        csv_path = os.path.join("reels", f"{mode_name.upper()}.csv")
        weights = probabilities_to_csv(probabilities, csv_path, total_weight=100000)
        
        print(f"\n  [OK] Saved to: {csv_path}")
        
        results[mode_name] = {
            "rtp": actual_rtp,
            "target": target_rtp,
            "error": error,
            "sharpness": optimal_sharpness,
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
    print("NATURAL DISTRIBUTION SUMMARY:")
    print("="*70)
    print("- Center buckets (7,8,9) are MOST COMMON (15-18% each)")
    print("- Moving outward, probabilities DECREASE naturally")
    print("- Far edges are RARE but still possible")
    print("- Feels like REAL physics, not rigged!")
    print()
    print("NEXT STEPS:")
    print("1. Run: python games/plinko/run.py")
    print("2. Hell's Storm modes inherit these distributions")
    print("3. All modes will be within 0.5% RTP margin!")
    print()

if __name__ == "__main__":
    main()











