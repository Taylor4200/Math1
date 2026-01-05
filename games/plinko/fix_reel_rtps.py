"""Generate reel CSV files with exact RTPs within 0.5% margin."""

import numpy as np
from perfect_optimizer import PlinkoOptimizer
from optimizer_config import OptimizerConfig
import os

def main():
    """Generate reel files with RTPs within 0.5% margin."""
    
    print("="*70)
    print("FIXING PLINKO REEL FILES FOR 0.5% RTP MARGIN")
    print("="*70)
    print()
    
    # Target RTPs for 0.5% total range
    # Using 95.00%-95.50% range (0.50% span)
    target_rtps = {
        "mild": 0.9525,      # 95.25% (middle)
        "sinful": 0.9500,    # 95.00% (low end)
        "demonic": 0.9550,   # 95.50% (high end)
    }
    
    # Create optimizer config
    config = OptimizerConfig()
    
    # Update all targets
    print("Target RTPs for 0.5% margin:")
    print("-" * 70)
    for mode, rtp in target_rtps.items():
        config.update_target_rtp(mode, rtp)
        print(f"  {mode.upper():<10} {rtp:.4f} ({(1-rtp)*100:.2f}% house edge)")
    
    print()
    print("="*70)
    print()
    
    # Optimize each mode with higher weight for more precision
    results = {}
    total_weight = 100000  # 100K entries for good precision
    
    for mode in ["mild", "sinful", "demonic"]:
        print(f"\n{'='*70}")
        print(f"GENERATING {mode.upper()} REEL")
        print(f"{'='*70}\n")
        
        # Create optimizer
        optimizer = PlinkoOptimizer(mode, config=config)
        
        # Solve
        stats = optimizer.solve(verbose=True)
        results[mode] = stats
        
        # Save to CSV in reels/ folder
        csv_path = os.path.join("reels", f"{mode.upper()}.csv")
        optimizer.save_to_csv(csv_path, total_weight=total_weight)
        
        # Also save solution JSON
        json_path = os.path.join("library", "distributions", f"{mode}_optimized.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        optimizer.save_solution(json_path)
        
        print()
    
    # Verify the generated reels
    print("\n" + "="*70)
    print("VERIFYING GENERATED REELS")
    print("="*70 + "\n")
    
    from game_config import GameConfig
    game_config = GameConfig()
    
    verified_rtps = {}
    for mode in ["mild", "sinful", "demonic"]:
        reel_key = mode.upper()
        reel_strip = game_config.reels[reel_key][0]
        multipliers = np.array(game_config.bucket_multipliers[mode])
        
        # Calculate RTP from reel
        bucket_counts = np.zeros(len(multipliers))
        for bucket in reel_strip:
            bucket_counts[int(bucket)] += 1
        
        probabilities = bucket_counts / len(reel_strip)
        actual_rtp = np.sum(probabilities * multipliers)
        verified_rtps[mode] = actual_rtp
        
        target_rtp = target_rtps[mode]
        error = abs(actual_rtp - target_rtp)
        
        print(f"{mode.upper():<10} Target: {target_rtp:.6f}  Actual: {actual_rtp:.6f}  Error: {error:.8f}")
    
    # Calculate range
    print()
    print("="*70)
    rtp_values = list(verified_rtps.values())
    rtp_range = max(rtp_values) - min(rtp_values)
    
    print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.4f}%)")
    print()
    
    if rtp_range <= 0.005:
        print("[OK] All reels within 0.5% margin!")
        print()
        print("Next steps:")
        print("1. Regenerate books with: python games/plinko/run.py")
        print("2. Hell's Storm modes will automatically inherit these RTPs")
    elif rtp_range <= 0.0075:
        print("[WARNING] Reels within 0.75% margin (close but not perfect)")
    else:
        print("[ERROR] Reels exceed 0.5% margin")
        print(f"        Over by: {(rtp_range-0.005)*100:.2f}%")
    
    print()
    print("="*70)
    print("FILES GENERATED:")
    print("="*70)
    for mode in ["mild", "sinful", "demonic"]:
        print(f"  [OK] reels/{mode.upper()}.csv ({total_weight:,} entries)")
    print()

if __name__ == "__main__":
    main()











