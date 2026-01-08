"""Regenerate ALL books with new reels"""

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
    
    # Regenerate all modes
    num_sim_args = {
        "base": int(1e5),
        "Bonus": int(1e5),
        "Super Bonus": int(1e5),
        "Bonus Booster": int(1e5),
        "Feature Spin": int(1e5),
        "Super Feature Spin": int(1e5),
    }
    
    num_threads = 16
    batching_size = 5000
    compression = True
    profiling = False
    
    print("=" * 70)
    print("REGENERATING ALL BOOKS WITH NEW REELS")
    print("=" * 70)
    
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )
    
    print("\nRegenerating configs...")
    generate_configs(gamestate)
    
    print("\n" + "=" * 70)
    print("DONE! All books regenerated with new reels.")
    print("=" * 70)





