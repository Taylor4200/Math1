"""Run ONLY optimization - no books or lookup tables generated.
You can build books and lookup tables elsewhere after optimization completes."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution

if __name__ == "__main__":
    
    rust_threads = 10
    
    # Define which modes to optimize
    target_modes = [
        "base",
        "Wrath of Olympus",
        "Super Wrath of Olympus",
        "bonus_booster",
        "Divine Strikes",
        "Divine Judgement",
    ]
    
    print("\n" + "="*70)
    print("RUNNING OPTIMIZATION ONLY (NO BOOKS/LOOKUP TABLES)")
    print("="*70)
    print(f"Target modes: {target_modes}")
    print("="*70 + "\n")
    
    # Initialize config and optimization setup
    config = GameConfig()
    gamestate = GameState(config)
    optimization_setup_class = OptimizationSetup(config)
    
    # Run optimization for all target modes
    try:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        print("\n" + "="*70)
        print("OPTIMIZATION COMPLETE")
        print("="*70)
        print("\nOptimized lookup tables are in:")
        print(f"  {config.output_files.optimization['paths']['optimization_files']}")
        print("\nYou can now:")
        print("  1. Build books elsewhere using the optimized reels")
        print("  2. Generate lookup tables elsewhere")
        print("  3. Use swap_tables() to swap optimized tables into publish_files")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n[ERROR] Optimization failed with error: {e}")
        import traceback
        traceback.print_exc()












