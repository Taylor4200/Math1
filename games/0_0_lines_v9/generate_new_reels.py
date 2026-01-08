"""Generate new reels specifically designed for K symbol sticky wild mechanics"""

import csv
import random

def generate_reel(length, symbol_weights, num_reels=5):
    """
    Generate a reel with specific symbol weights.
    
    symbol_weights: dict like {'K': 2, 'H1': 15, 'L1': 100, ...}
    Returns: list of rows, each row is a list of symbols for each reel position
    """
    # Create weighted symbol pool
    symbol_pool = []
    for symbol, weight in symbol_weights.items():
        symbol_pool.extend([symbol] * weight)
    
    # Generate reel strips
    rows = []
    for _ in range(length):
        row = []
        for _ in range(num_reels):
            row.append(random.choice(symbol_pool))
        rows.append(row)
    
    return rows

def save_reel(rows, filename):
    """Save reel to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Saved {filename}: {len(rows)} rows")

if __name__ == "__main__":
    random.seed(42)  # Reproducible
    
    # BASE GAME REEL - Normal frequency
    print("\n=== Generating Base Game Reel (BR0.csv) ===")
    base_weights = {
        'K': 12,      # K symbols - moderate (drops wilds, but rare in base)
        'S': 2,       # Scatters - VERY RARE (max 4 should land)
        'H1': 35,     # High symbols
        'H2': 30,
        'H3': 30,
        'L1': 80,     # Low symbols - most common
        'L2': 70,
        'L3': 70,
        'L4': 70,
    }
    
    base_reel = generate_reel(220, base_weights)
    save_reel(base_reel, 'reels/BR0.csv')
    
    # FREE GAME REEL - Balanced K frequency (enough to be exciting but not broken)
    print("\n=== Generating Free Game Reel (FR0.csv) ===")
    free_weights = {
        'K': 15,      # K symbols - Balanced (7-8% of positions)
        'H1': 45,     # More high symbols in free games
        'H2': 40,
        'H3': 35,
        'L1': 65,     # Still lots of lows
        'L2': 55,
        'L3': 55,
        'L4': 55,
    }
    
    free_reel = generate_reel(210, free_weights)
    save_reel(free_reel, 'reels/FR0.csv')
    
    # WINCAP REEL - For forced wincap distributions
    print("\n=== Generating Wincap Reel (FRWCAP.csv) ===")
    wincap_weights = {
        'K': 12,      # Moderate K symbols for wincap
        'H1': 55,     # Weighted to highs for big wins
        'H2': 50,
        'H3': 45,
        'L1': 30,
        'L2': 25,
        'L3': 25,
        'L4': 25,
    }
    
    wincap_reel = generate_reel(210, wincap_weights)
    save_reel(wincap_reel, 'reels/FRWCAP.csv')
    
    print("\n=== Backing up old reels ===")
    import shutil
    import os
    for old_file in ['BR0.csv', 'FR0.csv', 'FRWCAP.csv']:
        old_path = f'reels/{old_file}'
        backup_path = f'reels/{old_file}.backup'
        if os.path.exists(old_path):
            shutil.copy(old_path, backup_path)
            print(f"Backed up {old_file} -> {old_file}.backup")
    
    # Count symbols
    print("\n=== Symbol Counts ===")
    for reel_name, reel_data in [('BR0', base_reel), ('FR0', free_reel), ('FRWCAP', wincap_reel)]:
        from collections import Counter
        all_symbols = [sym for row in reel_data for sym in row]
        counts = Counter(all_symbols)
        print(f"\n{reel_name}:")
        for sym in sorted(counts.keys()):
            pct = counts[sym] / len(all_symbols) * 100
            print(f"  {sym}: {counts[sym]:4d} ({pct:5.1f}%)")


