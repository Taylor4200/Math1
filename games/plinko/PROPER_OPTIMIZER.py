"""PROPER Plinko optimizer using iterative convergence to hit EXACT targets."""
import random
import math

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

TARGETS = {
    "mild": {"eff_rtp": 0.973, "respin": 0.05, "max_prob_less": 0.79},
    "sinful": {"eff_rtp": 0.968, "respin": 0.08, "max_prob_less": 0.79},
    "demonic": {"eff_rtp": 0.963, "respin": 0.12, "max_prob_less": 0.79},
}

def optimize_distribution(mode, max_iter=2000):
    """Iteratively optimize to hit EXACT targets."""
    mults = M[mode]
    target = TARGETS[mode]
    base_rtp_target = target["eff_rtp"] / (1 + target["respin"])
    
    print(f"\n{'='*70}")
    print(f"Optimizing {mode.upper()}")
    print(f"Base RTP target: {base_rtp_target:.4f}, Max prob_less_bet: {target['max_prob_less']:.2f}")
    
    # Initialize probabilities with smart defaults
    probs = []
    for mult in mults:
        if mult == 0:
            p = 0.25  # DEMONIC 0x buckets
        elif mult < 0.5:
            p = 0.30  # 0.2x for SINFUL
        elif mult < 1:
            p = 0.20  # 0.5x buckets
        elif mult == 1:
            p = 0.05  # 1x buckets
        elif mult <= 4:
            p = 0.02
        elif mult <= 20:
            p = 0.005
        else:
            p = 0.0001
        probs.append(p)
    
    # Normalize
    total_prob = sum(probs)
    probs = [p / total_prob for p in probs]
    
    best_probs = probs.copy()
    best_error = float('inf')
    
    for iteration in range(max_iter):
        # Calculate current metrics
        rtp = sum(probs[i] * mults[i] for i in range(len(mults)))
        prob_less = sum(probs[i] for i in range(len(mults)) if mults[i] < 1.0)
        
        # Calculate errors
        rtp_error = rtp - base_rtp_target
        prob_error = max(0, prob_less - target["max_prob_less"])
        
        # Combined error (weighted)
        total_error = abs(rtp_error) * 10 + prob_error * 5
        
        if total_error < best_error:
            best_error = total_error
            best_probs = probs.copy()
        
        # Check convergence
        if abs(rtp_error) < 0.0001 and prob_less < target["max_prob_less"]:
            print(f"Converged in {iteration + 1} iterations!")
            break
        
        # Gradient descent adjustments
        lr = 0.005 if iteration < 500 else 0.001  # Learning rate
        
        for i in range(len(probs)):
            mult = mults[i]
            
            # RTP gradient
            if rtp_error > 0:  # RTP too high
                if mult < base_rtp_target:
                    probs[i] *= (1 + lr)
                else:
                    probs[i] *= (1 - lr)
            else:  # RTP too low
                if mult > base_rtp_target:
                    probs[i] *= (1 + lr)
                else:
                    probs[i] *= (1 - lr)
            
            # prob_less_bet gradient
            if prob_error > 0:  # Too many <1x
                if mult < 1.0:
                    probs[i] *= (1 - lr * 3)  # Stronger adjustment
                else:
                    probs[i] *= (1 + lr * 3)
        
        # Renormalize
        total_prob = sum(probs)
        probs = [p / total_prob for p in probs]
        
        # Clamp minimum probabilities
        probs = [max(p, 0.000001) for p in probs]
        probs = [p / sum(probs) for p in probs]
    
    # Use best found
    probs = best_probs
    
    # Convert to counts (100k strip)
    counts = [int(p * 100000) for p in probs]
    diff = 100000 - sum(counts)
    
    # Add/remove from appropriate bucket to maintain balance
    if diff > 0:
        counts[8] += diff
    elif diff < 0:
        # Remove from highest count bucket
        max_idx = counts.index(max(counts))
        counts[max_idx] += diff
    
    # Create strip
    strip = []
    for bucket_idx, count in enumerate(counts):
        strip.extend([bucket_idx] * count)
    random.shuffle(strip)
    
    # Final stats
    wins = [mults[b] for b in strip]
    final_base_rtp = sum(wins) / len(wins)
    final_eff_rtp = final_base_rtp * (1 + target["respin"])
    final_prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    print(f"Final: Base RTP {final_base_rtp:.4f}, Eff {final_eff_rtp:.4f}, Prob<Bet {final_prob_less:.3f}")
    
    # Check targets
    rtp_ok = abs(final_eff_rtp - target["eff_rtp"]) < 0.002
    prob_ok = final_prob_less < 0.80
    
    if rtp_ok and prob_ok:
        print(f"[PERFECT!!!] All targets met!")
    else:
        print(f"[Status] RTP {'OK' if rtp_ok else 'OFF'}, Prob {'OK' if prob_ok else 'HIGH'}")
    
    return strip, counts

# Run optimizer for all modes
print("PROPER PLINKO OPTIMIZATION")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    strip, counts = optimize_distribution(mode)
    
    # Write to CSV
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for bucket in strip:
            f.write(f"{bucket}\n")
    
    print(f"Wrote to games/plinko/reels/{mode.upper()}.csv")
    print(f"Bucket counts: {counts}")

print("\n" + "="*70)
print("[COMPLETE] Run: python games/plinko/run.py")



