"""Diagnostic script to find payout mismatches between books and lookup tables."""

import json
import zstandard as zst
from io import TextIOWrapper
from collections import Counter

# Get the first bet mode for testing
bet_mode = "base"  # Change this to test other modes

book_file = f"library/publish_files/books_{bet_mode}.jsonl.zst"
lut_file = f"library/publish_files/lookUpTable_{bet_mode}_0.csv"

print("="*70)
print(f"DIAGNOSING PAYOUT MISMATCH FOR MODE: {bet_mode}")
print("="*70)

# Read books
book_payouts = []
book_ids = []
print(f"\nReading books from: {book_file}")
with open(book_file, "rb") as f:
    decompressor = zst.ZstdDecompressor()
    with decompressor.stream_reader(f) as reader:
        txt_stream = TextIOWrapper(reader, encoding="UTF-8")
        for line in txt_stream:
            line = line.strip()
            if not line:
                continue
            blob = json.loads(line)
            book_payouts.append(blob["payoutMultiplier"])
            book_ids.append(blob["id"])

print(f"  Found {len(book_payouts)} books")
print(f"  Book IDs range: {min(book_ids)} to {max(book_ids)}")

# Read lookup table
lut_payouts = []
lut_ids = []
print(f"\nReading lookup table from: {lut_file}")
with open(lut_file, "r", encoding="UTF-8") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) >= 3:
            lut_ids.append(int(parts[0]))
            lut_payouts.append(int(float(parts[2])))

print(f"  Found {len(lut_payouts)} entries")
print(f"  LUT IDs range: {min(lut_ids)} to {max(lut_ids)}")

# Compare lengths
print(f"\n{'='*70}")
print("LENGTH COMPARISON")
print(f"{'='*70}")
print(f"Books: {len(book_payouts)}")
print(f"LUT:   {len(lut_payouts)}")
if len(book_payouts) != len(lut_payouts):
    print(f"  [ERROR] LENGTH MISMATCH!")
    print(f"  Difference: {len(lut_payouts) - len(book_payouts)} entries")
else:
    print(f"  [OK] Lengths match")

# Compare IDs
print(f"\n{'='*70}")
print("ID COMPARISON")
print(f"{'='*70}")
if book_ids != lut_ids:
    print(f"  [ERROR] ID ORDER MISMATCH!")
    mismatches = [(i, b, l) for i, (b, l) in enumerate(zip(book_ids[:20], lut_ids[:20])) if b != l]
    if mismatches:
        print(f"  First 20 ID mismatches:")
        for idx, bid, lid in mismatches[:10]:
            print(f"    Index {idx}: Book ID={bid}, LUT ID={lid}")
else:
    print(f"  [OK] IDs match in order")

# Compare payouts
print(f"\n{'='*70}")
print("PAYOUT COMPARISON")
print(f"{'='*70}")
mismatches = []
for i, (bp, lp) in enumerate(zip(book_payouts, lut_payouts)):
    if bp != lp:
        mismatches.append((i, book_ids[i], bp, lp))

if mismatches:
    print(f"  [ERROR] Found {len(mismatches)} payout mismatches!")
    print(f"\n  First 20 mismatches:")
    for idx, bid, bp, lp in mismatches[:20]:
        print(f"    Index {idx}, Book ID {bid}: Book={bp}, LUT={lp}, Diff={bp-lp}")
    
    # Show statistics
    book_counter = Counter(book_payouts)
    lut_counter = Counter(lut_payouts)
    
    print(f"\n  Payout value distribution:")
    print(f"    Unique book payouts: {len(book_counter)}")
    print(f"    Unique LUT payouts:  {len(lut_counter)}")
    
    # Find payouts that exist in one but not the other
    book_only = set(book_counter.keys()) - set(lut_counter.keys())
    lut_only = set(lut_counter.keys()) - set(book_counter.keys())
    
    if book_only:
        print(f"\n    Payouts only in books: {sorted(list(book_only))[:20]}")
    if lut_only:
        print(f"\n    Payouts only in LUT: {sorted(list(lut_only))[:20]}")
else:
    print(f"  [OK] All payouts match!")

# Check rounding
print(f"\n{'='*70}")
print("ROUNDING CHECK")
print(f"{'='*70}")
non_rounded_book = [p for p in book_payouts if p > 0 and p % 10 != 0]
non_rounded_lut = [p for p in lut_payouts if p > 0 and p % 10 != 0]

if non_rounded_book:
    print(f"  [ERROR] Found {len(non_rounded_book)} non-rounded book payouts (not multiples of 10):")
    print(f"    Examples: {non_rounded_book[:10]}")
else:
    print(f"  [OK] All book payouts are rounded to increments of 10")

if non_rounded_lut:
    print(f"  [ERROR] Found {len(non_rounded_lut)} non-rounded LUT payouts (not multiples of 10):")
    print(f"    Examples: {non_rounded_lut[:10]}")
else:
    print(f"  [OK] All LUT payouts are rounded to increments of 10")

print(f"\n{'='*70}")
print("DIAGNOSIS COMPLETE")
print(f"{'='*70}")
