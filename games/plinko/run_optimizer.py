"""User-friendly interface for running the Perfect Plinko Optimizer."""

import argparse
import os
from perfect_optimizer import PlinkoOptimizer
from optimizer_config import OptimizerConfig
from verify_optimizer import OptimizerVerifier


def optimize_mode(mode: str, verify: bool = True, total_weight: int = 1000000):
    """Optimize a single mode.
    
    Args:
        mode: One of 'mild', 'sinful', 'demonic'
        verify: Whether to verify results after optimization
        total_weight: Total weight for CSV distribution
    """
    print(f"\n{'#'*70}")
    print(f"# PERFECT PLINKO OPTIMIZER - {mode.upper()} MODE")
    print(f"{'#'*70}\n")
    
    # Initialize optimizer
    optimizer = PlinkoOptimizer(mode=mode)
    
    # Solve
    stats = optimizer.solve(verbose=True)
    
    # Save to CSV
    csv_path = f"reels/{mode.upper()}.csv"
    optimizer.save_to_csv(csv_path, total_weight=total_weight)
    
    # Save solution JSON
    json_path = f"library/optimization_results_{mode}.json"
    optimizer.save_solution(json_path)
    
    # Verify if requested
    if verify:
        print(f"\n{'='*70}")
        print(f"VERIFICATION")
        print(f"{'='*70}")
        
        config = OptimizerConfig()
        mode_config = config.get_config(mode)
        
        # Get bucket multipliers
        from game_config import GameConfig
        game_config = GameConfig()
        multipliers = game_config.bucket_multipliers[mode]
        
        # Extract target bucket HRs
        target_hrs = {}
        for bucket_idx, constraint in mode_config.get("bucket_constraints", {}).items():
            if "hr" in constraint:
                target_hrs[bucket_idx] = constraint["hr"]
        
        verifier = OptimizerVerifier(csv_path, multipliers)
        verifier.print_verification_report(
            target_rtp=mode_config["target_rtp"],
            target_plb=mode_config["target_prob_less_bet"],
            target_bucket_hrs=target_hrs,
            run_monte_carlo=True
        )


def optimize_all_modes(verify: bool = True, total_weight: int = 1000000):
    """Optimize all three modes."""
    modes = ["mild", "sinful", "demonic"]
    
    for mode in modes:
        optimize_mode(mode, verify=verify, total_weight=total_weight)
        print("\n")


def custom_optimize(mode: str, target_rtp: float, target_plb: float, 
                   max_win_hr: float = None, total_weight: int = 1000000):
    """Run optimizer with custom parameters.
    
    Args:
        mode: One of 'mild', 'sinful', 'demonic'
        target_rtp: Target RTP
        target_plb: Target prob_less_bet
        max_win_hr: Optional hit rate for max win buckets (0 and 16)
        total_weight: Total weight for CSV distribution
    """
    print(f"\n{'#'*70}")
    print(f"# CUSTOM OPTIMIZATION - {mode.upper()} MODE")
    print(f"{'#'*70}\n")
    
    # Create custom config
    config = OptimizerConfig()
    config.update_target_rtp(mode, target_rtp)
    config.update_prob_less_bet(mode, target_plb)
    
    if max_win_hr:
        config.update_bucket_hr(mode, 0, max_win_hr)
        config.update_bucket_hr(mode, 16, max_win_hr)
    
    # Initialize optimizer with custom config
    optimizer = PlinkoOptimizer(mode=mode, config=config)
    
    # Solve
    stats = optimizer.solve(verbose=True)
    
    # Save to CSV
    csv_path = f"reels/{mode.upper()}_custom.csv"
    optimizer.save_to_csv(csv_path, total_weight=total_weight)
    
    # Save solution JSON
    json_path = f"library/optimization_results_{mode}_custom.json"
    optimizer.save_solution(json_path)
    
    print(f"\n✓ Custom optimization complete!")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")


def interactive_mode():
    """Interactive mode for custom optimization."""
    print(f"\n{'#'*70}")
    print(f"# PERFECT PLINKO OPTIMIZER - INTERACTIVE MODE")
    print(f"{'#'*70}\n")
    
    # Get mode
    mode = input("Select mode (mild/sinful/demonic): ").strip().lower()
    if mode not in ["mild", "sinful", "demonic"]:
        print(f"Invalid mode: {mode}")
        return
    
    # Get RTP target
    target_rtp = float(input("Target RTP (e.g., 0.9267): ").strip())
    
    # Get prob_less_bet target
    target_plb = float(input("Target prob_less_bet (e.g., 0.75): ").strip())
    
    # Get max win HR (optional)
    max_win_hr_input = input("Max win hit rate (optional, e.g., 6000): ").strip()
    max_win_hr = float(max_win_hr_input) if max_win_hr_input else None
    
    # Total weight
    weight_input = input("Total weight (default 1000000): ").strip()
    total_weight = int(weight_input) if weight_input else 1000000
    
    # Run custom optimization
    custom_optimize(mode, target_rtp, target_plb, max_win_hr, total_weight)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Perfect Plinko Optimizer - Constraint-based mathematical solver"
    )
    
    parser.add_argument(
        "--mode",
        choices=["mild", "sinful", "demonic", "all"],
        default="all",
        help="Which mode to optimize (default: all)"
    )
    
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip verification after optimization"
    )
    
    parser.add_argument(
        "--weight",
        type=int,
        default=1000000,
        help="Total weight for CSV distribution (default: 1000000 for precision)"
    )
    
    parser.add_argument(
        "--custom",
        action="store_true",
        help="Run in custom/interactive mode"
    )
    
    parser.add_argument(
        "--target-rtp",
        type=float,
        help="Custom target RTP (requires --mode)"
    )
    
    parser.add_argument(
        "--target-plb",
        type=float,
        help="Custom target prob_less_bet (requires --mode)"
    )
    
    parser.add_argument(
        "--max-win-hr",
        type=float,
        help="Custom max win hit rate (requires --mode)"
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.custom and not (args.target_rtp or args.target_plb):
        interactive_mode()
        return
    
    # Custom optimization with CLI args
    if args.target_rtp or args.target_plb:
        if args.mode == "all":
            print("Error: Custom optimization requires a specific --mode")
            return
        
        target_rtp = args.target_rtp if args.target_rtp else 0.96
        target_plb = args.target_plb if args.target_plb else 0.75
        
        custom_optimize(
            args.mode, 
            target_rtp, 
            target_plb, 
            args.max_win_hr,
            args.weight
        )
        return
    
    # Standard optimization
    verify = not args.no_verify
    
    if args.mode == "all":
        optimize_all_modes(verify=verify, total_weight=args.weight)
    else:
        optimize_mode(args.mode, verify=verify, total_weight=args.weight)


if __name__ == "__main__":
    # Check if running from correct directory
    if not os.path.exists("game_config.py"):
        print("Error: Must run from games/plinko/ directory")
        print("Usage: cd games/plinko && python run_optimizer.py")
    else:
        main()

