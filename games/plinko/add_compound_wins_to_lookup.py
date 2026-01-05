"""Add compound win entries to existing lookup tables for RGS validation."""
import zstandard as zstd
import json
import csv

def get_all_payouts_from_books(mode):
    """Extract all unique payouts from compressed books."""
    compressed_path = f"library/publish_files/books_{mode}.jsonl.zst"
    
    with open(compressed_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
    
    lines = decompressed.decode('utf-8').strip().split('\n')
    payouts = set()
    
    for line in lines:
        if line.strip():
            book = json.loads(line)
            payouts.add(book['payoutMultiplier'])
    
    return sorted(payouts)

def read_existing_lookup(mode):
    """Read existing lookup table."""
    lookup_path = f"library/publish_files/lookUpTable_{mode}_0.csv"
    
    existing = {}
    with open(lookup_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                book_id, weight, payout_cents = row
                existing[int(payout_cents)] = int(weight)
    
    return existing

def create_expanded_lookup(mode):
    """Create expanded lookup table with base entries + compound wins."""
    
    # Get all payouts from books
    book_payouts = get_all_payouts_from_books(mode)
    
    # Get existing lookup entries
    existing_lookup = read_existing_lookup(mode)
    
    # Create expanded lookup
    expanded = {}
    
    # Keep all existing entries with their weights
    for payout_cents, weight in existing_lookup.items():
        expanded[payout_cents] = weight
    
    # Add missing compound win entries with weight = 1
    for payout_cents in book_payouts:
        if payout_cents not in expanded:
            expanded[payout_cents] = 1  # Minimal weight for validation
    
    # Write expanded lookup
    output_path = f"library/publish_files/lookUpTable_{mode}_0.csv"
    book_id = 1
    
    lines = []
    for payout_cents in sorted(expanded.keys()):
        weight = expanded[payout_cents]
        lines.append(f"{book_id},{weight},{payout_cents}")
        book_id += 1
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    # Calculate RTP
    total_w = sum(expanded.values())
    total_p = sum(w * p for p, w in expanded.items())
    rtp = total_p / total_w / 100
    he = (1 - rtp) * 100
    
    print(f"\n{mode.upper()}:")
    print(f"  Original entries: {len(existing_lookup)}")
    print(f"  Compound win entries added: {len(expanded) - len(existing_lookup)}")
    print(f"  Total entries: {len(expanded)}")
    print(f"  RTP: {rtp:.4%}")
    print(f"  House Edge: {he:.2f}%")
    print(f"  [OK] Written!")

print("="*70)
print("ADDING COMPOUND WIN ENTRIES TO LOOKUP TABLES")
print("="*70)

for mode in ["mild", "sinful", "demonic"]:
    create_expanded_lookup(mode)

print("\n" + "="*70)
print("DONE! All lookup tables now include compound win payouts.")
print("="*70)







