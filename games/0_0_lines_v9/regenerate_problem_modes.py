"""Regenerate just Super Bonus and Bonus Booster with new reels"""

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
    
    num_sim_args = {
        "Super Bonus": int(1e5),
        "Bonus Booster": int(1e5),
    }
    
    print("\n" + "=" * 70)
    print("REGENERATING Super Bonus & Bonus Booster WITH NEW REELS")
    print("=" * 70)
    print("New reels have:")
    print("  - BR0: K symbols at 3.4% (moderate)")
    print("  - FR0: K symbols at 0.4% (VERY RARE - only 4 positions!)")
    print("=" * 70 + "\n")
    
    create_books(
        gamestate,
        config,
        num_sim_args,
        5000,
        16,
        True,
        False,
    )
    
    print("\nRegenerating configs...")
    generate_configs(gamestate)
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)





