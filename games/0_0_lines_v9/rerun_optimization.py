"""Rerun optimization for specific modes to fix lookup table mismatch"""

from game_config import GameConfig
from gamestate import GameState
from game_optimization import OptimizationSetup
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from optimization_program.run_script import OptimizationExecution
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)
    optimization_setup_class = OptimizationSetup(config)
    
    # Rerun optimization for the problematic modes
    target_modes = ['Super Bonus', 'Bonus Booster']
    
    print(f"Rerunning optimization for: {target_modes}")
    OptimizationExecution().run_all_modes(config, target_modes, 16)
    
    print("Regenerating configs...")
    generate_configs(gamestate)
    
    print("Done! Lookup tables should now match books.")

