"""Optimize all Plinko modes to be within 0.5% RTP margin."""

import numpy as np
from perfect_optimizer import PlinkoOptimizer
from optimizer_config import OptimizerConfig
import os

def main():
    """Optimize all three modes with tight 0.5% RTP margin."""
    
    print("="*70)
    print("PLINKO OPTIMIZER - 0.5% RTP MARGIN TARGET")
    print("="*70)
    print()
    
    # Target RTPs for 0.5% margin
    # We'll center around 95.25% with 0.25% steps for tight control
    target_rtps = {
        "mild": 0.9525,      # 95.25% (center)
        "sinful": 0.9500,    # 95.00% (0.25% lower)
        "demonic": 0.9550,   # 95.50% (0.25% higher)
    }
    
    # Create optimizer config
    config = OptimizerConfig()
    
    # Update all targets
    print("Setting target RTPs for 0.5% margin:")
    for mode, rtp in target_rtps.items():
        config.update_target_rtp(mode, rtp)
        print(f"  {mode.upper():<10} Target RTP: {rtp:.4f} ({(1-rtp)*100:.2f}% house edge)")
    
    print()
    print("="*70)
    print()
    
    # Optimize each mode
    results = {}
    
    for mode in ["mild", "sinful", "demonic"]:
        print(f"\n{'='*70}")
        print(f"OPTIMIZING {mode.upper()} MODE")
        print(f"{'='*70}\n")
        
        # Create optimizer
        optimizer = PlinkoOptimizer(mode, config=config)
        
        # Solve
        stats = optimizer.solve(verbose=True)
        results[mode] = stats
        
        # Save to CSV
        csv_path = os.path.join("reels", f"{mode.upper()}.csv")
        optimizer.save_to_csv(csv_path, total_weight=100000)
        
        # Save JSON
        json_path = os.path.join("library", "distributions", f"{mode}_optimized.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        optimizer.save_solution(json_path)
        
        print()
    
    # Print summary
    print("\n" + "="*70)
    print("OPTIMIZATION SUMMARY - RTP MARGIN ANALYSIS")
    print("="*70 + "\n")
    
    print(f"{'Mode':<12} {'Target RTP':<15} {'Actual RTP':<15} {'Error':<12} {'House Edge':<15}")
    print("-" * 70)
    
    for mode in ["mild", "sinful", "demonic"]:
        stats = results[mode]
        target = stats['target_rtp']
        actual = stats['rtp']
        error = stats['rtp_error']
        house_edge = (1 - actual) * 100
        
        print(f"{mode.upper():<12} {target:.6f}      {actual:.6f}      {error:.8f}   {house_edge:.4f}%")
    
    # Calculate RTP range
    rtps = [results[mode]['rtp'] for mode in ["mild", "sinful", "demonic"]]
    rtp_range = max(rtps) - min(rtps)
    
    print()
    print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.4f}%)")
    
    if rtp_range <= 0.005:
        print("✅ SUCCESS! All modes within 0.5% margin!")
    elif rtp_range <= 0.0075:
        print("⚠️  CLOSE! Modes within 0.75% margin (might be acceptable)")
    else:
        print("❌ FAILED: Modes exceed 0.5% margin")
    
    print()
    print("="*70)
    print("FILES GENERATED:")
    print("="*70)
    for mode in ["mild", "sinful", "demonic"]:
        print(f"  ✓ reels/{mode.upper()}.csv")
        print(f"  ✓ library/distributions/{mode}_optimized.json")
    
    print()
    print("="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Run simulations with: python games/plinko/run.py")
    print("2. Check simulation results match target RTPs")
    print("3. Verify Hell's Storm modes inherit base mode RTPs")
    print()

if __name__ == "__main__":
    main()











