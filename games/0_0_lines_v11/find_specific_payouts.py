"""Find event IDs with specific payout values in base mode."""
import json
import zstandard as zstd
from pathlib import Path

publish_dir = Path("library/publish_files")
book_file = publish_dir / "books_base.jsonl.zst"

# Target payouts in cents
target_payouts = [20, 30, 260]  # 0.2x, 0.3x, 2.6x

# Decompress and read books
with open(book_file, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(f.read())

lines = decompressed.decode('utf-8').strip().split('\n')

found_events = {payout: [] for payout in target_payouts}

for line in lines:
    if not line.strip():
        continue
    book = json.loads(line)
    event_id = book['id']
    payout_multiplier = book['payoutMultiplier']  # in cents
    
    if payout_multiplier in target_payouts:
        found_events[payout_multiplier].append({
            'id': event_id,
            'payout_multiplier': payout_multiplier,
            'payout_x': payout_multiplier / 100.0
        })

print("=== EVENTS WITH SPECIFIC PAYOUTS IN BASE MODE ===\n")
for payout in target_payouts:
    events = found_events[payout]
    print(f"Payout: {payout} cents = {payout/100.0:.1f}x")
    if events:
        print(f"  Found {len(events)} events:")
        for e in events[:10]:  # Show first 10
            print(f"    Event ID: {e['id']}")
    else:
        print(f"  No events found with this payout")
    print()

# Also check the specific event IDs the user mentioned
print("\n=== CHECKING USER-REPORTED EVENT IDs ===\n")
for event_id in [250, 348, 403]:
    found = False
    for line in lines:
        if not line.strip():
            continue
        book = json.loads(line)
        if book['id'] == event_id:
            payout = book['payoutMultiplier']
            print(f"Event ID {event_id}: {payout} cents = {payout/100.0:.1f}x")
            found = True
            break
    if not found:
        print(f"Event ID {event_id}: NOT FOUND in book file")








