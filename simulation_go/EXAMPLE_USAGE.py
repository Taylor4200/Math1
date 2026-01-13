"""
Example: How to use Go simulations in your run.py

This shows how to integrate Go simulations into your existing Python workflow.
Replace the create_books() call with GoSimulationExecution.
"""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.write_data.write_configs import generate_configs

# Import Go simulation wrapper (if available)
try:
    from simulation_go.pkg.python.wrapper import GoSimulationExecution
    GO_AVAILABLE = True
except ImportError:
    GO_AVAILABLE = False
    # Fallback to Python
    from src.state.run_sims import create_books

if __name__ == "__main__":
    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e5),
        "Wrath of Olympus": int(1e5),
        # ... other modes
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = list(num_sim_args.keys())

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        if GO_AVAILABLE:
            # Use Go for faster simulations
            print("\n[INFO] Using Go simulation engine (faster)")
            execution = GoSimulationExecution()
            execution.run_sims_all_modes(
                game_config=config,
                modes_to_run=target_modes,
                num_sims=num_sim_args,
                threads=num_threads,
                batch_size=batching_size,
                compress=compression,
            )
        else:
            # Fallback to Python
            print("\n[INFO] Using Python simulation engine (fallback)")
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
        # Python optimization (keep as-is)
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        # Python analysis (keep as-is)
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        # Python verification (keep as-is)
        execute_all_tests(config)




