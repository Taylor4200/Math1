"""Create optimized lookup tables matching book order exactly."""
import zstandard as zstd
import json

print("="*70)
print("CREATING LOOKUP TABLES FROM BOOKS")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    print(f"\n{mode.upper()}:")
    
    # Read books
    book_file = f"library/publish_files/books_{mode}.jsonl.zst"
    with open(book_file, 'rb') as f:
        data = zstd.ZstdDecompressor().decompress(f.read()).decode()
        books = [json.loads(line) for line in data.strip().split('\n') if line.strip()]
    
    # Create lookup table matching book order
    output_file = f"library/optimization_files/{mode}_0_1.csv"
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"Name,From_Books_{mode}\n")
        f.write("Score,0.0\n")
        f.write("LockedUpRTP,\n")
        f.write("Rtp,0.96\n")  # Placeholder
        f.write("Win Ranges\n")
        f.write("Distribution\n")
        
        # Write one row per book
        for i, book in enumerate(books):
            payout_cents = book['payoutMultiplier']
            payout_dollars = payout_cents / 100.0
            f.write(f"{i+1},1,{payout_dollars}\n")
    
    print(f"  [OK] Created {output_file} with {len(books)} rows matching books")

print(f"\n{'='*70}")
print("COMPLETE - Now swap these into publish_files")
print('='*70)







