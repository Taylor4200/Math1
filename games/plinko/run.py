"""Main file for generating results for Hell's Plinko game."""

import os
import subprocess
from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 32
    rust_threads = 32
    batching_size = 250000  # 5M / 4 threads = 1.25M per thread
    compression = True   # ENABLED for production (creates .jsonl.zst files)
    profiling = False

    num_sim_args = {
        "mild": int(5e6),    # 5M simulations (1 event each = 5M events)
        "sinful": int(5e6),  # 5M simulations (1 event each = 5M events)
        "demonic": int(5e6), # 5M simulations (1 event each = 5M events)
        "hells_storm_mild": int(5e5),    # ~75,758 simulations (66 events each ≈ 5M events)
        "hells_storm_sinful": int(5e5),  # ~75,758 simulations (66 events each ≈ 5M events)
        "hells_storm_demonic": int(5e5), # ~75,758 simulations (66 events each ≈ 5M events)
    }

    run_conditions = {
        "run_sims": True,            # Generate books with bonus peg ENABLED
        "run_optimization": False,   # DISABLED - Rust optimizer broken for Plinko
        "run_analysis": False,       # Disabled - analysis not compatible with Plinko
        "run_format_checks": False,
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
        # Generate configs (creates lookup tables with weight=1 matching book order)
        generate_configs(gamestate)
        
        print("\n" + "="*70)
        print("BOOKS AND LOOKUP TABLES GENERATED")
        print("="*70)
        print("  Lookup tables match books exactly (100K rows, weight=1)")
        print("  RGS will calculate RTP by aggregating book payouts")

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)
        
        # Update weighted reel CSVs from optimization results
        import subprocess
        result = subprocess.run(
            ["python", "update_reels_from_optimization.py"], 
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        
        # Swap best distributions to lookup tables
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        python_exe = os.path.join(root_dir, "env", "Scripts", "python.exe")
        
        print("\n" + "="*70)
        print("SWAPPING OPTIMIZED LOOKUP TABLES")
        print("="*70)
        
        for mode in target_modes:
            print(f"Swapping {mode.upper()} lookup table...")
            result = subprocess.run(
                [python_exe, "utils/swap_lookups.py", "-g", "plinko", "-m", mode, "-n", "1"],
                cwd=root_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  [OK] {mode.upper()} lookup table updated successfully!")
            else:
                print(f"  [ERROR] {mode.upper()}: {result.stderr}")
        
        print("="*70)
        print("DONE! All lookup tables updated.")
        print("="*70 + "\n")

    if run_conditions["run_analysis"]:
        # Plinko doesn't use symbols, so no custom_keys needed
        create_stat_sheet(gamestate)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
