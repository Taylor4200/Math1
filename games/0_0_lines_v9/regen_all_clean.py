"""Regenerate all modes cleanly with new reels"""

from gamestate import GameState
from game_config import GameConfig
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("NEW REEL STATS:")
    print("=" * 70)
    print("  BR0 (Base):   K symbols at 2.4%")
    print("  FR0 (Free):   K symbols at 3.1% (33 positions)")
    print("  FRWCAP:       K symbols at 3.1%")
    print("=" * 70 + "\n")
    
    config = GameConfig()
    gamestate = GameState(config)
    
    # Regenerate ALL modes with new reels
    num_sim_args = {
        "base": int(1e5),
        "Bonus": int(1e5),
        "Super Bonus": int(1e5),
        "Bonus Booster": int(1e5),
        "Feature Spin": int(1e5),
        "Super Feature Spin": int(1e5),
    }
    
    create_books(
        gamestate,
        config,
        num_sim_args,
        5000,  # batch size
        16,    # threads
        True,  # compression
        False, # profiling
    )
    
    print("\nGenerating configs...")
    generate_configs(gamestate)
    
    print("\n" + "=" * 70)
    print("ALL BOOKS REGENERATED WITH NEW REELS!")
    print("=" * 70)



