"""Regenerate books while preserving optimized lookup tables"""

from gamestate import GameState
from game_config import GameConfig
import sys
import os
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)
    
    num_sim_args = {
        "base": int(1e5),
        "Bonus": int(1e5),
        "Super Bonus": int(1e5),
        "Bonus Booster": int(1e5),
        "Feature Spin": int(1e5),
        "Super Feature Spin": int(1e5),
    }
    
    print("\n" + "=" * 70)
    print("STEP 1: Backup optimized lookup tables")
    print("=" * 70)
    
    # Backup existing optimized lookup tables from optimization_files
    backup_dir = "library/optimized_luts_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    for mode in num_sim_args.keys():
        # Check optimization_files for the best optimized table
        opt_dir = "library/optimization_files"
        best_file = None
        best_num = 0
        
        # Find the highest numbered optimized file (e.g., base_0_10.csv is better than base_0_1.csv)
        for i in range(1, 11):
            test_file = os.path.join(opt_dir, f"{mode}_0_{i}.csv")
            if os.path.exists(test_file):
                best_file = test_file
                best_num = i
        
        if best_file:
            backup_file = os.path.join(backup_dir, f"lookUpTable_{mode}_0.csv")
            shutil.copy(best_file, backup_file)
            print(f"  Backed up {mode}_0_{best_num}.csv -> backup")
        else:
            print(f"  WARNING: No optimized table found for {mode}")
    
    print("\n" + "=" * 70)
    print("STEP 2: Generate books with new reels")
    print("=" * 70)
    
    create_books(
        gamestate,
        config,
        num_sim_args,
        50000, # very large batch size (2 batches total)
        2,     # Only 2 threads - maximum stability
        True,  # compression
        False, # profiling
    )
    
    generate_configs(gamestate)
    
    print("\n" + "=" * 70)
    print("STEP 3: Restore optimized lookup tables")
    print("=" * 70)
    
    # Restore the optimized lookup tables (create_books overwrites them)
    for mode in num_sim_args.keys():
        backup_file = os.path.join(backup_dir, f"lookUpTable_{mode}_0.csv")
        publish_file = os.path.join("library/publish_files", f"lookUpTable_{mode}_0.csv")
        
        if os.path.exists(backup_file):
            shutil.copy(backup_file, publish_file)
            print(f"  Restored optimized LUT for {mode}")
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print("Books regenerated with new reels")
    print("Optimized lookup tables preserved")
    print("=" * 70)

