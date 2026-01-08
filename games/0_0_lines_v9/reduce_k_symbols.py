"""Reduce K symbols in free game reel to fix RTP issues"""

import csv
import os

def reduce_k_symbols_in_reel(input_file, output_file, keep_ratio=0.3):
    """
    Reduce K symbols in a reel file by replacing some with other symbols.
    keep_ratio: What fraction of K symbols to keep (0.3 = keep 30%, remove 70%)
    """
    rows = []
    k_rows = []
    
    # Read the reel
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if row:  # Skip empty rows
                rows.append(row)
                # Check if any symbol in this row is 'K'
                if any(sym == 'K' for sym in row):
                    k_rows.append(i)
    
    print(f"Total rows: {len(rows)}")
    print(f"Rows with K symbols: {len(k_rows)}")
    
    # Decide which K symbols to remove
    import random
    random.seed(42)  # For reproducibility
    k_rows_to_modify = random.sample(k_rows, int(len(k_rows) * (1 - keep_ratio)))
    
    # Replacement symbols (weighted towards low symbols)
    replacements = ['L1'] * 10 + ['L2'] * 8 + ['L3'] * 6 + ['L4'] * 6 + ['H3'] * 4 + ['H2'] * 3 + ['H1'] * 2
    
    # Modify the selected rows
    for row_idx in k_rows_to_modify:
        row = rows[row_idx]
        for col_idx in range(len(row)):
            if row[col_idx] == 'K':
                row[col_idx] = random.choice(replacements)
    
    # Write the modified reel
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    
    # Count remaining K symbols
    remaining_k = sum(1 for row in rows if any(sym == 'K' for sym in row))
    print(f"Remaining rows with K symbols: {remaining_k}")
    print(f"Reduction: {len(k_rows)} -> {remaining_k} ({remaining_k/len(k_rows)*100:.1f}% kept)")

if __name__ == "__main__":
    reels_dir = "reels"
    
    # Reduce K symbols in FR0 (free game) - keep only 10% (very aggressive)
    print("\n=== Reducing K symbols in FR0 (Free Game) ===")
    reduce_k_symbols_in_reel(
        os.path.join(reels_dir, "FR0.csv"),
        os.path.join(reels_dir, "FR0_reduced.csv"),
        keep_ratio=0.10  # Keep only 10% of K symbols (very aggressive)
    )
    
    # Keep base game at 70%
    print("\n=== Reducing K symbols in BR0 (Base Game) ===")
    reduce_k_symbols_in_reel(
        os.path.join(reels_dir, "BR0.csv"),
        os.path.join(reels_dir, "BR0_reduced.csv"),
        keep_ratio=0.70  # Keep 70% of K symbols
    )
    
    print("\n=== Backup original reels ===")
    import shutil
    shutil.copy(os.path.join(reels_dir, "BR0.csv"), os.path.join(reels_dir, "BR0_original.csv"))
    shutil.copy(os.path.join(reels_dir, "FR0.csv"), os.path.join(reels_dir, "FR0_original.csv"))
    
    print("\n=== Replace with reduced reels ===")
    shutil.copy(os.path.join(reels_dir, "BR0_reduced.csv"), os.path.join(reels_dir, "BR0.csv"))
    shutil.copy(os.path.join(reels_dir, "FR0_reduced.csv"), os.path.join(reels_dir, "FR0.csv"))
    
    print("\nDone! Original reels backed up as BR0_original.csv and FR0_original.csv")

