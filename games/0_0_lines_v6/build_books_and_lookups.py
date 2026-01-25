"""Build books and lookup tables separately (after optimization has been run).
This script assumes optimization has already completed and optimized lookup tables exist.
"""

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from utils.swap_lookups import swap_tables

if __name__ == "__main__":
    
    num_threads = 3
    batching_size = 50000
    compression = True
    profiling = False
    
    # Define simulation counts for each mode
    num_sim_args = {
        "base": int(1e5),
        "Wrath of Olympus": int(1e5),
        "Super Wrath of Olympus": int(1e5),
        "bonus_booster": int(1e5),
        "Divine Strikes": int(1e5),
    }
    
    target_modes = list(num_sim_args.keys())
    
    print("\n" + "="*70)
    print("BUILDING BOOKS AND LOOKUP TABLES")
    print("="*70)
    print(f"Target modes: {target_modes}")
    print("="*70 + "\n")
    
    # Initialize config
    config = GameConfig()
    gamestate = GameState(config)
    
    # Option 1: Use optimized lookup tables (if optimization was run)
    use_optimized = input("Use optimized lookup tables? (y/n, default=y): ").strip().lower()
    if use_optimized != 'n':
        print("\nSwapping optimized lookup tables into place...")
        for mode in target_modes:
            try:
                swap_tables(config.game_id, mode, 1)  # Use pig 1 (best optimized distribution)
                print(f"  [OK] Swapped optimized table for {mode}")
            except FileNotFoundError as e:
                print(f"  [WARN] No optimization file found for {mode}: {e}")
                print(f"         Will use default reels instead.")
            except Exception as e:
                print(f"  [ERROR] Failed to swap table for {mode}: {e}")
        
        # Generate configs after swapping
        generate_configs(gamestate)
    
    # Generate books from current reels
    print("\n" + "="*70)
    print("GENERATING BOOKS")
    print("="*70)
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )
    
    # Generate lookup tables and configs
    print("\n" + "="*70)
    print("GENERATING LOOKUP TABLES AND CONFIGS")
    print("="*70)
    generate_configs(gamestate)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    print("\nBooks and lookup tables are ready in:")
    print(f"  Books: {config.output_files.books['paths']['books']}")
    print(f"  Lookup Tables: {config.output_files.lookup['paths']['lookup_tables']}")
    print("="*70 + "\n")

















