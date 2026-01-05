"""Test script to run optimization for bonus mode only."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    rust_threads = 16
    
    config = GameConfig()
    gamestate = GameState(config)
    optimization_setup_class = OptimizationSetup(config)
    
    # Generate configs first (needed for optimization)
    generate_configs(gamestate)
    
    # Run optimization for bonus only
    print("Running optimization for bonus mode only...")
    OptimizationExecution().run_opt_single_mode(config, "bonus", rust_threads)
    
    # Regenerate configs after optimization
    generate_configs(gamestate)
    print("Bonus optimization complete!")

