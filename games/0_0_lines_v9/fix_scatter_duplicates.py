"""Fix reel files to ensure no reel has more than 1 S symbol per reel"""

import csv
import os
import random

def fix_scatter_duplicates(input_file, output_file):
    """Ensure each reel (column) has at most 1 S symbol"""
    rows = []
    
    # Read the reel file
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                rows.append(row)
    
    num_reels = len(rows[0]) if rows else 0
    print(f"\n=== Processing {input_file} ===")
    print(f"Total rows: {len(rows)}")
    print(f"Number of reels: {num_reels}")
    
    # Count S symbols per reel
    s_positions = {reel: [] for reel in range(num_reels)}
    for row_idx, row in enumerate(rows):
        for reel_idx, symbol in enumerate(row):
            if symbol == 'S':
                s_positions[reel_idx].append(row_idx)
    
    # Report current state
    print("\nCurrent S symbol positions per reel:")
    for reel_idx in range(num_reels):
        count = len(s_positions[reel_idx])
        if count > 0:
            print(f"  Reel {reel_idx}: {count} S symbols at rows {s_positions[reel_idx]}")
    
    # Fix reels with multiple S symbols
    # Replacement symbols (weighted towards low symbols, no S)
    replacements = ['L1'] * 10 + ['L2'] * 8 + ['L3'] * 6 + ['L4'] * 6 + ['H3'] * 4 + ['H2'] * 3 + ['H1'] * 2
    
    random.seed(42)  # For reproducibility
    changes_made = 0
    
    for reel_idx in range(num_reels):
        if len(s_positions[reel_idx]) > 1:
            # Keep the first S, replace the rest
            s_rows = s_positions[reel_idx]
            rows_to_fix = s_rows[1:]  # All except the first
            
            print(f"\n  Fixing Reel {reel_idx}: Keeping S at row {s_rows[0]}, replacing {len(rows_to_fix)} duplicates")
            
            for row_idx in rows_to_fix:
                # Replace S with a random symbol
                rows[row_idx][reel_idx] = random.choice(replacements)
                changes_made += 1
                print(f"    Row {row_idx}: S -> {rows[row_idx][reel_idx]}")
    
    # Write the fixed reel
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    
    # Verify fix
    s_positions_after = {reel: [] for reel in range(num_reels)}
    for row_idx, row in enumerate(rows):
        for reel_idx, symbol in enumerate(row):
            if symbol == 'S':
                s_positions_after[reel_idx].append(row_idx)
    
    print(f"\n=== Results ===")
    print(f"Changes made: {changes_made}")
    print("\nS symbol positions per reel (after fix):")
    for reel_idx in range(num_reels):
        count = len(s_positions_after[reel_idx])
        if count > 0:
            print(f"  Reel {reel_idx}: {count} S symbol(s) at row(s) {s_positions_after[reel_idx]}")
        if count > 1:
            print(f"    WARNING: Reel {reel_idx} still has {count} S symbols!")
    
    return changes_made

if __name__ == "__main__":
    reels_dir = "reels"
    
    # Files to process (only base game reel has S symbols)
    files_to_fix = [
        ("BR0.csv", "BR0.csv"),
    ]
    
    for input_name, output_name in files_to_fix:
        input_path = os.path.join(reels_dir, input_name)
        output_path = os.path.join(reels_dir, output_name)
        
        if os.path.exists(input_path):
            # Backup original
            backup_path = os.path.join(reels_dir, f"{output_name}.backup_scatter_fix")
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy(input_path, backup_path)
                print(f"Backed up {input_name} -> {backup_path}")
            
            fix_scatter_duplicates(input_path, output_path)
        else:
            print(f"File not found: {input_path}")

