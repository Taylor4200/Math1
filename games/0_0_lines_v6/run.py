"""Main file for generating results for sample lines-pay game."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 3
    rust_threads = 10
    batching_size = 50000  # Reduced for faster processing
    compression = True
    profiling = False

    # Reduced simulation counts for MUCH faster runs
    # Only regenerate base and bonus_booster (bonus modes already optimized)
    num_sim_args = {
        "base": int(1e5),  # Regenerate base with new multiplier frequency
        "bonus_booster": int(1e5),  # Regenerate bonus_booster with new base reels
        # "Wrath of Olympus": int(1e5),  # SKIP - already optimized
        # "Super Wrath of Olympus": int(1e5),  # SKIP - already optimized
        # "Divine Strikes": int(1e5),  # SKIP - already optimized
    }

    run_conditions = {
        "run_sims": True,        # Set to False to skip book creation (books already exist)
        "run_optimization": False,  # Only run optimization
        "run_analysis": False,     # Skip analysis for now
        "run_format_checks": True, # Skip format checks for now
    }
    target_modes = list(num_sim_args.keys())

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    optimized_modes = []  # Track which modes were optimized
    if run_conditions["run_optimization"]:
        print("\n" + "="*70)
        print("RUNNING OPTIMIZATION FOR ALL MODES")
        print("="*70)
        print(f"Target modes: {target_modes}")
        print("="*70 + "\n")
        
        try:
            OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        except Exception as e:
            print(f"\n[ERROR] Optimization failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        # Swap optimized lookup tables (use pig 1 which is typically the best)
        # Note: Rust optimizer writes directly to publish_files for pig_index=0,
        # but we swap pig 1 (index 1) which is usually the best optimized distribution
        # WARNING: After swapping, books and lookup tables won't match until books are regenerated
        print("\n" + "="*70)
        print("SWAPPING OPTIMIZED LOOKUP TABLES")
        print("="*70)
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from utils.swap_lookups import swap_tables
        
        for mode in target_modes:
            try:
                swap_tables(config.game_id, mode, 1)  # Use pig 1 (best optimized distribution)
                print(f"  [OK] Swapped optimized table for {mode}")
                optimized_modes.append(mode)  # Track successfully optimized modes
            except FileNotFoundError as e:
                print(f"  [WARN] No optimization file found for {mode}: {e}")
                print(f"         Optimizer may not have run for this mode.")
                print(f"         Check optimization output above for errors.")
            except Exception as e:
                print(f"  [ERROR] Failed to swap table for {mode}: {e}")
        
        generate_configs(gamestate)
        
        # Automatically regenerate books for optimized modes to match optimized lookup tables
        if optimized_modes:
            print(f"\n" + "="*70)
            print("REGENERATING BOOKS FOR OPTIMIZED MODES")
            print("="*70)
            print(f"Modes to regenerate: {optimized_modes}")
            print("Books will be regenerated to match optimized lookup tables.")
            print("="*70 + "\n")
            
            # Create dict with only optimized modes for regeneration
            optimized_sim_args = {mode: num_sim_args[mode] for mode in optimized_modes if mode in num_sim_args}
            
            # Regenerate books for optimized modes only
            create_books(
                gamestate,
                config,
                optimized_sim_args,
                batching_size,
                num_threads,
                compression,
                profiling,
            )
            
            # Regenerate configs after new books are created
            generate_configs(gamestate)
            
            print(f"\n  [OK] Books regenerated for optimized modes: {optimized_modes}")
            print(f"       Books and lookup tables now match - ready to publish!")

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        # Run verification for all modes (books should match after regeneration)
        print(f"\n[NOTE] Running verification/stats generation.")
        if run_conditions["run_optimization"] and optimized_modes:
            print(f"       Books were regenerated for optimized modes, verification should pass.")
        
        execute_all_tests(config)
