"""Fine-tune reel CSVs to hit exact target RTPs while preserving bell curve shape."""

import numpy as np
import collections
from game_config import GameConfig

def fine_tune_reel(mode, target_rtp, max_iterations=10000):
    """Adjust reel weights to hit exact target RTP."""
    config = GameConfig()
    multipliers = np.array(config.bucket_multipliers[mode])
    
    # Read current reel
    reel_path = f'games/plinko/reels/{mode.upper()}.csv'
    with open(reel_path) as f:
        buckets = [int(line.strip()) for line in f]
    
    # Count current distribution
    counts = collections.Counter(buckets)
    weights = np.array([counts[i] for i in range(17)])
    total_weight = np.sum(weights)
    
    print(f"\n{mode.upper()}:")
    print(f"  Initial RTP: {np.sum(weights * multipliers) / total_weight:.6f}")
    print(f"  Target RTP:  {target_rtp:.6f}")
    
    # Iteratively adjust weights
    for iteration in range(max_iterations):
        current_probs = weights / total_weight
        current_rtp = np.sum(current_probs * multipliers)
        error = target_rtp - current_rtp
        
        if abs(error) < 0.000001:
            break
        
        # Transfer ONE weight to improve RTP
        if error > 0:  # Need to increase RTP
            # Move from lowest mult (with enough weight) to highest mult
            donor_candidates = [(i, weights[i]) for i in range(17) if weights[i] > total_weight * 0.001]
            donor_idx = min(donor_candidates, key=lambda x: multipliers[x[0]])[0]
            
            recipient_candidates = [(i, multipliers[i]) for i in range(17)]
            recipient_idx = max(recipient_candidates, key=lambda x: x[1])[0]
            
            weights[donor_idx] -= 1
            weights[recipient_idx] += 1
        else:  # Need to decrease RTP
            # Move from highest mult (with enough weight) to lowest mult
            donor_candidates = [(i, weights[i]) for i in range(17) if weights[i] > total_weight * 0.001]
            donor_idx = max(donor_candidates, key=lambda x: multipliers[x[0]])[0]
            
            recipient_candidates = [(i, multipliers[i]) for i in range(17)]
            recipient_idx = min(recipient_candidates, key=lambda x: x[1])[0]
            
            weights[donor_idx] -= 1
            weights[recipient_idx] += 1
    
    # Verify final RTP
    final_probs = weights / total_weight
    final_rtp = np.sum(final_probs * multipliers)
    
    print(f"  Final RTP:   {final_rtp:.6f}")
    print(f"  Error:       {abs(final_rtp - target_rtp):.8f}")
    print(f"  Iterations:  {iteration + 1}")
    
    # Write updated reel
    bucket_list = []
    for bucket_idx, weight in enumerate(weights):
        bucket_list.extend([bucket_idx] * int(weight))
    
    np.random.shuffle(bucket_list)
    
    with open(reel_path, 'w') as f:
        for bucket in bucket_list:
            f.write(f"{bucket}\n")
    
    print(f"  [OK] Saved updated reel")
    
    return final_rtp

if __name__ == "__main__":
    print("="*70)
    print("FINE-TUNING REEL RTPs FOR 0.5% MARGIN")
    print("="*70)
    
    # Use tighter targets centered around 95.25%
    targets = {
        "mild": 0.9525,      # 95.25% (center)
        "sinful": 0.9500,    # 95.00% (0.25% lower)
        "demonic": 0.9550,   # 95.50% (0.25% higher)
    }
    
    rtps = {}
    for mode in ["mild", "sinful", "demonic"]:
        rtps[mode] = fine_tune_reel(mode, targets[mode])
    
    print("\n" + "="*70)
    print("FINAL RTP SUMMARY")
    print("="*70)
    print(f"{'Mode':<12} {'Target':<12} {'Actual':<12} {'Error':<12} {'House Edge'}")
    print("-" * 70)
    
    for mode in ["mild", "sinful", "demonic"]:
        target = targets[mode]
        actual = rtps[mode]
        error = abs(actual - target)
        house_edge = (1 - actual) * 100
        print(f"{mode.upper():<12} {target:.6f}   {actual:.6f}   {error:.8f}   {house_edge:.2f}%")
    
    # Calculate range
    rtp_values = list(rtps.values())
    rtp_range = max(rtp_values) - min(rtp_values)
    
    print()
    print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.4f}%)")
    
    if rtp_range <= 0.005:
        print("\n[OK] SUCCESS! All modes within 0.5% margin!")
        print("\nReady to run simulations: python games/plinko/run.py")
    elif rtp_range <= 0.0075:
        print("\n[WARNING] Within 0.75% margin (close)")
    else:
        print(f"\n[ERROR] Exceeds 0.5% margin by {(rtp_range-0.005)*100:.2f}%")
    
    print()











