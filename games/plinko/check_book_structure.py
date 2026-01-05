import zstd
import json

# Check normal mode
with open('library/publish_files/books_mild.jsonl.zst', 'rb') as f:
    data = zstd.ZstdDecompressor().decompress(f.read()).decode('utf-8')
    lines = data.strip().split('\n')
    book = json.loads(lines[0])
    print("=== NORMAL MODE (MILD) ===")
    print(f"Book ID: {book['id']}")
    print(f"Payout Multiplier: {book['payoutMultiplier']}")
    print(f"Number of events: {len(book['events'])}")
    print("Events:")
    for e in book['events']:
        print(f"  {e}")
    print()

# Check Hells Storm mode
with open('library/publish_files/books_hells_storm_mild.jsonl.zst', 'rb') as f:
    data = zstd.ZstdDecompressor().decompress(f.read()).decode('utf-8')
    lines = data.strip().split('\n')
    book = json.loads(lines[0])
    print("=== HELLS STORM MODE (MILD) ===")
    print(f"Book ID: {book['id']}")
    print(f"Payout Multiplier: {book['payoutMultiplier']}")
    print(f"Number of events: {len(book['events'])}")
    print("First 5 events:")
    for i, e in enumerate(book['events'][:5]):
        print(f"  {i}: {e}")
    print(f"...")
    print(f"Last event:")
    print(f"  {book['events'][-1]}")






