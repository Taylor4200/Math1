"""Check if lookup table and books have matching payouts."""
import zstandard as zstd
import json
import csv

# Read lookup table
lut_file = "library/publish_files/lookUpTable_base_0.csv"
lut_payouts = []
with open(lut_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 3:
            lut_payouts.append(int(row[2]))

# Read books
book_file = "library/publish_files/books_base.jsonl.zst"
book_payouts = []
with open(book_file, 'rb') as f:
    data = zstd.ZstdDecompressor().decompress(f.read()).decode()
    books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    book_payouts = [b['payoutMultiplier'] for b in books]

print(f"Lookup table: {len(lut_payouts)} entries")
print(f"Books: {len(book_payouts)} entries")
print(f"\nFirst 10 lookup payouts: {lut_payouts[:10]}")
print(f"First 10 book payouts: {book_payouts[:10]}")

# Check if they match
if len(lut_payouts) != len(book_payouts):
    print(f"\nERROR: Length mismatch! LUT={len(lut_payouts)}, Books={len(book_payouts)}")
else:
    mismatches = []
    for i, (lut, book) in enumerate(zip(lut_payouts, book_payouts)):
        if lut != book:
            mismatches.append((i, lut, book))
            if len(mismatches) <= 10:
                print(f"Mismatch at index {i}: LUT={lut}, Book={book}")
    
    if mismatches:
        print(f"\nERROR: {len(mismatches)} mismatches found!")
    else:
        print("\nOK: All payouts match!")
