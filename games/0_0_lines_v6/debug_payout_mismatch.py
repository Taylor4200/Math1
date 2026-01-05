"""Debug why book payouts don't match lookup table payouts."""
import zstandard as zstd
import json
import csv
import hashlib
import pickle

mode = "base"

# Read lookup table
lut_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
lut_payouts = []
lut_ids = []
with open(lut_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 3:
            lut_ids.append(int(row[0]))
            lut_payouts.append(int(row[2]))

# Read books
book_file = f"library/publish_files/books_{mode}.jsonl.zst"
book_payouts = []
book_ids = []
with open(book_file, 'rb') as f:
    data = zstd.ZstdDecompressor().decompress(f.read()).decode()
    books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    for book in books:
        book_ids.append(book['id'])
        book_payouts.append(book['payoutMultiplier'])

print(f"Lookup table: {len(lut_payouts)} entries")
print(f"Books: {len(book_payouts)} entries")
print(f"Length match: {len(lut_payouts) == len(book_payouts)}")

if len(lut_payouts) != len(book_payouts):
    print(f"\nERROR: Different lengths!")
    print(f"  Missing in LUT: {len(book_payouts) - len(lut_payouts)}")
    print(f"  Extra in LUT: {len(lut_payouts) - len(book_payouts)}")
    exit(1)

# Check first 20 entries
print(f"\nFirst 20 entries comparison:")
print(f"{'Index':<8} {'Book ID':<10} {'LUT ID':<10} {'Book Payout':<15} {'LUT Payout':<15} {'Match':<10}")
print("-" * 80)
mismatches = []
for i in range(min(20, len(book_payouts))):
    book_id = book_ids[i] if i < len(book_ids) else "N/A"
    lut_id = lut_ids[i] if i < len(lut_ids) else "N/A"
    book_pay = book_payouts[i] if i < len(book_payouts) else "N/A"
    lut_pay = lut_payouts[i] if i < len(lut_payouts) else "N/A"
    match = "✓" if (book_pay == lut_pay and book_id == lut_id) else "✗"
    if book_pay != lut_pay or book_id != lut_id:
        mismatches.append(i)
    print(f"{i:<8} {book_id:<10} {lut_id:<10} {book_pay:<15} {lut_pay:<15} {match:<10}")

# Check if IDs match
print(f"\nID order check:")
id_mismatches = [i for i in range(min(len(book_ids), len(lut_ids))) if book_ids[i] != lut_ids[i]]
if id_mismatches:
    print(f"  Found {len(id_mismatches)} ID mismatches (first 10): {id_mismatches[:10]}")
else:
    print(f"  ✓ All IDs match in order")

# Check if payouts match
print(f"\nPayout check:")
payout_mismatches = [i for i in range(min(len(book_payouts), len(lut_payouts))) if book_payouts[i] != lut_payouts[i]]
if payout_mismatches:
    print(f"  Found {len(payout_mismatches)} payout mismatches")
    print(f"  First 10 mismatches:")
    for i in payout_mismatches[:10]:
        print(f"    Index {i}: Book={book_payouts[i]}, LUT={lut_payouts[i]}, Diff={abs(book_payouts[i] - lut_payouts[i])}")
else:
    print(f"  ✓ All payouts match")

# MD5 check
book_hash = hashlib.md5(pickle.dumps(book_payouts)).hexdigest()
lut_hash = hashlib.md5(pickle.dumps(lut_payouts)).hexdigest()
print(f"\nMD5 Hashes:")
print(f"  Books: {book_hash}")
print(f"  LUT:   {lut_hash}")
print(f"  Match: {book_hash == lut_hash}")

# Check if it's just order
if set(book_payouts) == set(lut_payouts):
    print(f"\n✓ Same payouts, but different order!")
    print(f"  This means the optimizer changed the order of books")
else:
    print(f"\n✗ Different payout values!")
    book_unique = set(book_payouts)
    lut_unique = set(lut_payouts)
    only_in_books = book_unique - lut_unique
    only_in_lut = lut_unique - book_unique
    if only_in_books:
        print(f"  Payouts only in books (first 10): {sorted(list(only_in_books))[:10]}")
    if only_in_lut:
        print(f"  Payouts only in LUT (first 10): {sorted(list(only_in_lut))[:10]}")
