"""Regenerate books for specific modes to match current game config"""

from gamestate import GameState
from game_config import GameConfig
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)
    
    # Regenerate books for the problematic modes
    num_sim_args = {
        "Super Bonus": int(1e5),
        "Bonus Booster": int(1e5),
    }
    
    num_threads = 16
    batching_size = 5000
    compression = True
    profiling = False
    
    print(f"Regenerating books for: {list(num_sim_args.keys())}")
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )
    
    print("Regenerating configs...")
    generate_configs(gamestate)
    
    print("Done! Books should now match current game config.")





