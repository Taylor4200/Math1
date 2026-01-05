"""Diagnose the exact mismatch between lookup and books."""
import csv
import zstandard as zstd
import json

for mode in ["mild"]:
    print(f"\n{mode.upper()}:")
    print("="*70)
    
    # Read lookup table payouts
    lut_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    lut_payouts = set()
    with open(lut_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                lut_payouts.add(int(row[2]))
    
    print(f"Lookup table payouts: {sorted(lut_payouts)}")
    
    # Read book payouts
    book_file = f"library/publish_files/books_{mode}.jsonl.zst"
    with open(book_file, 'rb') as f:
        data = zstd.ZstdDecompressor().decompress(f.read()).decode()
        books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    
    book_payouts = set(b['payoutMultiplier'] for b in books)
    print(f"Book payouts: {sorted(book_payouts)}")
    
    # Find mismatches
    missing_in_lut = book_payouts - lut_payouts
    missing_in_books = lut_payouts - book_payouts
    
    if missing_in_lut:
        print(f"\n[ERROR] Payouts in BOOKS but NOT in LOOKUP:")
        print(f"  {sorted(missing_in_lut)}")
    
    if missing_in_books:
        print(f"\n[ERROR] Payouts in LOOKUP but NOT in BOOKS:")
        print(f"  {sorted(missing_in_books)}")







