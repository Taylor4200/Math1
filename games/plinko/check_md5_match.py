"""Check if MD5 hashes match (RGS validation)."""
import csv
import zstandard as zstd
import json
import pickle
import hashlib

for mode in ["mild", "sinful", "demonic"]:
    print(f"\n{mode.upper()}:")
    
    # Read lookup payouts (ALL payouts from all rows)
    lut_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    lut_payouts = []
    with open(lut_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                lut_payouts.append(int(row[2]))
    
    # Read book payouts
    book_file = f"library/publish_files/books_{mode}.jsonl.zst"
    with open(book_file, 'rb') as f:
        data = zstd.ZstdDecompressor().decompress(f.read()).decode()
        books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    
    book_payouts = [b['payoutMultiplier'] for b in books]
    
    # Compare
    print(f"  Lookup: {len(lut_payouts)} payouts")
    print(f"  Books: {len(book_payouts)} payouts")
    print(f"  Lengths match: {len(lut_payouts) == len(book_payouts)}")
    
    # MD5 check
    lut_hash = hashlib.md5(pickle.dumps(lut_payouts)).hexdigest()
    book_hash = hashlib.md5(pickle.dumps(book_payouts)).hexdigest()
    
    print(f"  LUT MD5: {lut_hash}")
    print(f"  Book MD5: {book_hash}")
    print(f"  Match: {lut_hash == book_hash}")







