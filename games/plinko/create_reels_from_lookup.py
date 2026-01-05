"""Create reel CSVs from aggregated lookup tables."""
import csv
import random

# Bucket multipliers from game_config.py (multiplied by 100 to get cents)
BUCKET_MULTIPLIERS = {
    "mild": {
        66600: [0, 16],      # 666x
        15000: [1, 15],      # 150x
        6000: [2, 14],       # 60x
        2000: [3, 13],       # 20x
        800: [4, 12],        # 8x
        400: [5, 11],        # 4x
        200: [6, 10],        # 2x
        100: [7, 9],         # 1x
        50: [8],             # 0.5x
    },
    "sinful": {
        166600: [0, 16],     # 1666x
        40000: [1, 15],      # 400x
        12000: [2, 14],      # 120x
        4000: [3, 13],       # 40x
        1200: [4, 12],       # 12x
        400: [5, 11],        # 4x
        200: [6, 10],        # 2x
        50: [7, 9],          # 0.5x
        20: [8],             # 0.2x
    },
    "demonic": {
        1666600: [0, 16],    # 16666x
        250000: [1, 15],     # 2500x
        60000: [2, 14],      # 600x
        15000: [3, 13],      # 150x
        4000: [4, 12],       # 40x
        800: [5, 11],        # 8x
        200: [6, 10],        # 2x
        0: [7, 8, 9],        # 0x
    },
}

def create_reel_from_lookup(mode):
    """Create reel CSV from optimized lookup table."""
    # Read from optimization_files (Rust optimizer output format)
    opt_file = f"library/optimization_files/{mode}_0_1.csv"
    
    # Parse optimizer output file
    weights_and_payouts = []
    in_distribution = False
    with open(opt_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == "Distribution":
                in_distribution = True
                continue
            if in_distribution:
                parts = line.split(',')
                if len(parts) == 3:
                    book_id, weight, payout_dollars = parts
                    weight = int(weight)
                    payout_cents = int(float(payout_dollars) * 100)
                    weights_and_payouts.append((weight, payout_cents))
    
    reel_path = f"reels/{mode.upper()}.csv"
    
    print(f"\n{mode.upper()}:")
    
    # Create reel entries from optimizer weights
    reel_entries = []
    for weight, payout_cents in weights_and_payouts:
        # Get possible bucket indices for this payout
        possible_buckets = BUCKET_MULTIPLIERS[mode].get(payout_cents, [])
        if not possible_buckets:
            print(f"  [WARNING] No bucket found for payout {payout_cents}")
            continue
        
        # Add entries to reel (distribute evenly among possible buckets)
        for _ in range(weight):
            bucket = random.choice(possible_buckets)
            reel_entries.append(bucket)
        
        print(f"  Payout {payout_cents}: {weight} entries -> buckets {possible_buckets}")
    
    # Shuffle to randomize order
    random.shuffle(reel_entries)
    
    # Write reel CSV
    with open(reel_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for bucket in reel_entries:
            writer.writerow([bucket])
    
    print(f"  [OK] Created {reel_path} with {len(reel_entries)} entries")
    
    # Verify distribution
    from collections import Counter
    counts = Counter(reel_entries)
    print(f"  Bucket distribution:")
    for bucket in sorted(counts.keys()):
        print(f"    Bucket {bucket}: {counts[bucket]} times ({counts[bucket]/len(reel_entries)*100:.2f}%)")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    
    print("="*70)
    print("CREATING REELS FROM LOOKUP TABLES")
    print("="*70)
    
    for mode in ["mild", "sinful", "demonic"]:
        create_reel_from_lookup(mode)
    
    print(f"\n{'='*70}")
    print("REELS CREATED SUCCESSFULLY")
    print('='*70)

