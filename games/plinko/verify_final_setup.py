"""Verify the final setup is correct."""
import csv
import zstandard as zstd
import json

print("="*70)
print("FINAL SETUP VERIFICATION")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    print(f"\n{mode.upper()}:")
    
    # Check lookup table
    lut_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    with open(lut_file, 'r') as f:
        lut_rows = list(csv.reader(f))
    
    weights = [int(row[1]) for row in lut_rows if len(row) == 3]
    payouts = [int(row[2]) for row in lut_rows if len(row) == 3]
    
    total_weight = sum(weights)
    # RGS divides payouts by 100 to convert cents to dollars (line 18 in distribution_functions.py)
    total_payout_dollars = sum(w * (p / 100.0) for w, p in zip(weights, payouts))
    rtp = total_payout_dollars / total_weight  # Bet cost is 1 dollar
    
    print(f"  Lookup table: {len(lut_rows)} rows")
    print(f"  Total weight: {total_weight:,}")
    print(f"  Unique weights: {len(set(weights))}")
    print(f"  Calculated RTP: {rtp:.2%}")
    
    # Check books
    book_file = f"library/publish_files/books_{mode}.jsonl.zst"
    with open(book_file, 'rb') as f:
        data = zstd.ZstdDecompressor().decompress(f.read()).decode()
        books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    
    print(f"  Books: {len(books)}")
    
    # Verify first book structure
    first_book = books[0]
    print(f"  First book payoutMultiplier: {first_book['payoutMultiplier']}")
    print(f"  First book events: {len(first_book['events'])}")

print(f"\n{'='*70}")
print("VERIFICATION COMPLETE")
print('='*70)

