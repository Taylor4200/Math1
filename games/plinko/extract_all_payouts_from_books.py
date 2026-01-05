"""Extract all unique payouts from compressed books to see what lookup table needs."""
import zstandard as zstd
import json

for mode in ["mild", "sinful", "demonic"]:
    compressed_path = f"library/publish_files/books_{mode}.jsonl.zst"
    
    # Decompress and read
    with open(compressed_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
    
    # Parse JSONL (one JSON object per line)
    lines = decompressed.decode('utf-8').strip().split('\n')
    
    # Collect unique payouts
    payouts = set()
    for line in lines:
        if line.strip():
            book = json.loads(line)
            payouts.add(book['payoutMultiplier'])
    
    # Sort and display
    payouts_sorted = sorted(payouts)
    
    print(f"\n{mode.upper()}: {len(payouts_sorted)} unique payouts")
    print(f"  Min: {min(payouts_sorted)/100}x ({min(payouts_sorted)} cents)")
    print(f"  Max: {max(payouts_sorted)/100}x ({max(payouts_sorted)} cents)")
    
    # Show first 20 and last 20
    print(f"  First 20: {[p/100 for p in payouts_sorted[:20]]}")
    print(f"  Last 20: {[p/100 for p in payouts_sorted[-20:]]}")







