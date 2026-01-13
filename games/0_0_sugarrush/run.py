"""Main file for generating results for Sugar Rush game with multipliers that drop on the board."""

import os

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    # Optimized settings like 0_0_cluster for better performance
    num_threads = 2  # Increased from 8 to 10 (like cluster game)
    rust_threads = 20  # Increased from 8 to 20 for optimization (like cluster game)
    batching_size = 10000  # Much larger batching (like cluster game) - reduces I/O overhead significantly
    compression = True
    profiling = False

    # Keep 100k simulations as required
    num_sim_args = {
        "base": int(1e5),
        "bonus": int(1e5),
        "super_bonus": int(1e5),
        "bonus_booster": int(1e5),
        "multiplierfeature": 0,  # Skip multiplier feature - we don't have M symbols
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base", "bonus", "super_bonus", "bonus_booster"]

    config = GameConfig()
    gamestate = GameState(config)

    # Filter out bet modes we are not running (e.g., multiplierfeature)
    allowed_modes = set(target_modes)
    config.bet_modes = [bm for bm in config.bet_modes if bm.get_name() in allowed_modes]
    gamestate.config.bet_modes = config.bet_modes

    # Ensure temp directory exists for multi-threaded output
    temp_mt_dir = os.path.join(config.library_path, "temp_multi_threaded_files")
    os.makedirs(temp_mt_dir, exist_ok=True)

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

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
