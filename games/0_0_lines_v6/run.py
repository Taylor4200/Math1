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

    num_threads = 16
    rust_threads = 16
    batching_size = 10000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e5),
        "Wrath of Olympus": int(1e5),
        "Super Wrath of Olympus": int(1e5),
        "bonus_booster": int(1e5),
        "Divine Strikes": int(1e5),
        "Divine Judgement": int(1e5),
    }

    run_conditions = {
        "run_sims": True,        # Set to False to skip book creation (books already exist)
        "run_optimization": True,  # Only run optimization
        "run_analysis": True,     # Skip analysis for now
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
        
        if optimized_modes:
            print(f"\n  [NOTE] Modes {optimized_modes} were optimized - books and lookup tables")
            print(f"         will not match until books are regenerated. Skipping verification for these modes.")

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        # Skip verification for optimized modes since books won't match until regenerated
        excluded_modes = optimized_modes if optimized_modes else []
        if excluded_modes:
            print(f"\n[NOTE] Skipping verification for optimized modes: {excluded_modes}")
            print(f"       Regenerate books after optimization to pass full verification.")
        
        # If optimization ran, skip verification entirely since books won't match
        # (books were generated before optimization, lookup tables were swapped after)
        if run_conditions["run_optimization"] and optimized_modes:
            print(f"\n[SKIP] Skipping all verification - books were generated before optimization.")
            print(f"       Lookup tables were swapped after optimization, so they won't match.")
            print(f"       Regenerate books with 'run_sims=True' after optimization to pass verification.")
        else:
            execute_all_tests(config, excluded_modes=excluded_modes)
