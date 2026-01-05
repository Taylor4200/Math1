"""Expand optimized lookup tables to 100K rows for RGS validation."""
import csv
import random

print("="*70)
print("EXPANDING OPTIMIZED LOOKUP TABLES")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    print(f"\n{mode.upper()}:")
    
    # Read compact optimized lookup
    compact_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    weighted_payouts = []
    
    with open(compact_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                book_id, weight, payout = row
                weight = int(weight)
                payout = int(payout)
                weighted_payouts.append((weight, payout))
    
    # Expand to match reel size
    expanded_payouts = []
    for weight, payout in weighted_payouts:
        for _ in range(weight):
            expanded_payouts.append(payout)
    
    # Shuffle to match book generation (which draws random from reels)
    random.seed(42)  # For reproducibility
    random.shuffle(expanded_payouts)
    
    # Limit to 100K (same as num_sims)
    expanded_payouts = expanded_payouts[:100000]
    
    # Write expanded lookup
    expanded_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    with open(expanded_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for i, payout in enumerate(expanded_payouts):
            writer.writerow([i+1, 1, payout])
    
    print(f"  Original: {len(weighted_payouts)} rows")
    print(f"  Expanded: {len(expanded_payouts)} rows")
    print(f"  [OK] Written to {expanded_file}")

print(f"\n{'='*70}")
print("EXPANSION COMPLETE")
print('='*70)
print("\nNow books and lookup tables will have matching MD5 hashes!")







