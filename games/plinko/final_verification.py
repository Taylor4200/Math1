"""Final verification that books and lookup tables match perfectly."""
import csv
import zstandard as zstd
import json
import pickle
import hashlib

print("="*70)
print("FINAL VERIFICATION: BOOKS vs LOOKUP TABLES")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    print(f"\n{mode.upper()}:")
    
    # Read lookup table
    lut_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    lut_payouts = []
    with open(lut_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                lut_payouts.append(int(row[2]))
    
    # Read books
    book_file = f"library/publish_files/books_{mode}.jsonl.zst"
    book_payouts = []
    with open(book_file, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        data = dctx.decompress(f.read()).decode()
        lines = data.strip().split('\n')
        for line in lines:
            if line.strip():
                book = json.loads(line)
                book_payouts.append(book['payoutMultiplier'])
    
    # Compare
    print(f"  Lookup table: {len(lut_payouts)} rows")
    print(f"  Books: {len(book_payouts)} entries")
    print(f"  Lengths match: {len(lut_payouts) == len(book_payouts)}")
    
    # MD5 hash comparison (RGS validation)
    book_hash = hashlib.md5(pickle.dumps(book_payouts)).hexdigest()
    lut_hash = hashlib.md5(pickle.dumps(lut_payouts)).hexdigest()
    
    print(f"  Book MD5: {book_hash}")
    print(f"  LUT MD5:  {lut_hash}")
    print(f"  Hashes match: {book_hash == lut_hash}")
    
    if book_hash == lut_hash:
        print(f"  [OK] PERFECT MATCH - RGS validation will pass!")
    else:
        print(f"  [ERROR] MISMATCH - RGS validation will fail!")

print(f"\n{'='*70}")
print("VERIFICATION COMPLETE")
print('='*70)
