"""Check if event IDs need to be adjusted (system uses 0-indexed, books use 1-indexed)."""
import json
import zstandard as zstd
from pathlib import Path

script_dir = Path(__file__).parent
publish_dir = script_dir / "library" / "publish_files"
book_file = publish_dir / "books_base.jsonl.zst"

print("Checking event ID mapping...")
print("User reports:")
print("  System Event ID 23 -> 0.9x (but book ID 23 = 0.2x)")
print("  System Event ID 22 -> 0.3x (but book ID 22 = 9.0x)")
print("  System Event ID 46 -> 1.5x (but book ID 46 = 0.2x)")
print("  System Event ID 45 -> 0.2x (but book ID 45 = 6.0x)")
print("  System Event ID 68 -> 4x (but book ID 68 = 0.2x)")
print("  System Event ID 67 -> 0.2x (but book ID 67 = 0.6x)")
print("\nChecking if system Event ID N maps to book ID N+1:\n")

with open(book_file, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(f.read())

lines = decompressed.decode('utf-8').strip().split('\n')

# Create a mapping of book ID to payout
book_data = {}
for line in lines:
    if not line.strip():
        continue
    book = json.loads(line)
    book_data[book['id']] = book['payoutMultiplier'] / 100.0

# Check if system event ID N corresponds to book ID N+1
test_cases = [
    (23, 0.9),  # User says system ID 23 = 0.9x
    (22, 0.3),  # User says system ID 22 = 0.3x
    (46, 1.5),  # User says system ID 46 = 1.5x
    (45, 0.2),  # User says system ID 45 = 0.2x
    (68, 4.0),  # User says system ID 68 = 4.0x
    (67, 0.2),  # User says system ID 67 = 0.2x
]

print("Testing if system Event ID N = book ID N+1:")
for sys_id, expected_payout in test_cases:
    book_id = sys_id + 1
    if book_id in book_data:
        actual_payout = book_data[book_id]
        match = "MATCH" if abs(actual_payout - expected_payout) < 0.1 else "NO MATCH"
        print(f"  {match} System Event ID {sys_id} -> Book ID {book_id}: {actual_payout:.2f}x (expected: {expected_payout:.2f}x)")
    else:
        print(f"  NOT FOUND: System Event ID {sys_id} -> Book ID {book_id}")

print("\nTesting if system Event ID N = book ID N:")
for sys_id, expected_payout in test_cases:
    book_id = sys_id
    if book_id in book_data:
        actual_payout = book_data[book_id]
        match = "MATCH" if abs(actual_payout - expected_payout) < 0.1 else "NO MATCH"
        print(f"  {match} System Event ID {sys_id} -> Book ID {book_id}: {actual_payout:.2f}x (expected: {expected_payout:.2f}x)")
    else:
        print(f"  NOT FOUND: System Event ID {sys_id} -> Book ID {book_id}")

print("\nTesting if system Event ID N = book ID N-1:")
for sys_id, expected_payout in test_cases:
    book_id = sys_id - 1
    if book_id in book_data:
        actual_payout = book_data[book_id]
        match = "MATCH" if abs(actual_payout - expected_payout) < 0.1 else "NO MATCH"
        print(f"  {match} System Event ID {sys_id} -> Book ID {book_id}: {actual_payout:.2f}x (expected: {expected_payout:.2f}x)")
    else:
        print(f"  NOT FOUND: System Event ID {sys_id} -> Book ID {book_id}")

