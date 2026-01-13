"""Verify event ID mapping in book files."""
import json
import zstandard as zstd
from pathlib import Path

script_dir = Path(__file__).parent
publish_dir = script_dir / "library" / "publish_files"
book_file = publish_dir / "books_base.jsonl.zst"

print("Reading first 100 events from base mode to check ID mapping...\n")

with open(book_file, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(f.read())

lines = decompressed.decode('utf-8').strip().split('\n')

# Check first 10 events
print("First 10 events in book file:")
for i, line in enumerate(lines[:10]):
    if not line.strip():
        continue
    book = json.loads(line)
    event_id = book['id']
    payout = book['payoutMultiplier']
    payout_x = payout / 100.0
    print(f"  Line {i}: Book ID={event_id}, Payout={payout} cents ({payout_x:.2f}x)")

# Check specific event IDs the user mentioned
print("\n\nChecking specific event IDs user mentioned:")
target_ids = [22, 23, 45, 46, 67, 68]

for target_id in target_ids:
    found = False
    for line in lines:
        if not line.strip():
            continue
        book = json.loads(line)
        if book['id'] == target_id:
            payout = book['payoutMultiplier']
            payout_x = payout / 100.0
            print(f"  Event ID {target_id}: {payout} cents ({payout_x:.2f}x)")
            found = True
            break
    if not found:
        print(f"  Event ID {target_id}: NOT FOUND")

# Also check if IDs are 0-indexed or 1-indexed
print("\n\nChecking if there's an off-by-one issue:")
print("Looking for events with payout 20 cents (0.2x):")
count = 0
for line in lines:
    if not line.strip():
        continue
    book = json.loads(line)
    if book['payoutMultiplier'] == 20:
        print(f"  Event ID {book['id']}: 0.2x")
        count += 1
        if count >= 10:
            break








