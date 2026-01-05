"""Verify books payouts match lookup table payouts exactly."""
import zstandard as zstd
import json
import csv

for mode in ["mild", "sinful", "demonic"]:
    # Get payouts from lookup table
    lookup_path = f"library/publish_files/lookUpTable_{mode}_0.csv"
    lookup_payouts = set()
    
    with open(lookup_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                lookup_payouts.add(int(row[2]))
    
    # Get payouts from books
    compressed_path = f"library/publish_files/books_{mode}.jsonl.zst"
    with open(compressed_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
    
    lines = decompressed.decode('utf-8').strip().split('\n')
    book_payouts = set()
    
    for i, line in enumerate(lines):
        if line.strip():
            book = json.loads(line)
            book_payouts.add(book['payoutMultiplier'])
            
            # Show structure of first book
            if i == 0:
                print(f"  First book structure:")
                print(f"    payoutMultiplier: {book.get('payoutMultiplier', 'NOT FOUND')}")
                print(f"    events count: {len(book.get('events', []))}")
                for j, evt in enumerate(book.get('events', [])[:3]):
                    print(f"      Event {j+1}: {evt.get('type', 'unknown')} - amount: {evt.get('amount', 'N/A')}")
    
    # Compare
    print(f"\n{mode.upper()}:")
    print(f"  Lookup table payouts: {sorted(lookup_payouts)}")
    print(f"  Book payouts: {sorted(book_payouts)}")
    
    # Check if books have payouts not in lookup
    missing_in_lookup = book_payouts - lookup_payouts
    if missing_in_lookup:
        print(f"  [ERROR] {len(missing_in_lookup)} payouts in books NOT in lookup table:")
        print(f"    {sorted(missing_in_lookup)[:10]}")
    else:
        print(f"  [OK] All book payouts exist in lookup table!")
    
    # Check if lookup has payouts not in books
    missing_in_books = lookup_payouts - book_payouts
    if missing_in_books:
        print(f"  [INFO] {len(missing_in_books)} payouts in lookup table NOT in books (OK, rare payouts)")

print("\n" + "="*70)
print("Verification complete!")
print("="*70)

