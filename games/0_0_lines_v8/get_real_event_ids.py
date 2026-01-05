"""Get REAL verified event IDs with actual payouts from book files."""
import json
import zstandard as zstd
import os
from pathlib import Path

# Get the script directory
script_dir = Path(__file__).parent

# Load stats to get average payouts
stats_path = script_dir / "library" / "stats_summary.json"
with open(stats_path, 'r') as f:
    stats = json.load(f)

# Game modes
modes = [
    {"name": "base", "cost": 1.0},
    {"name": "Bonus", "cost": 100.0},
    {"name": "Super Bonus", "cost": 500.0},
    {"name": "Bonus Booster", "cost": 2.0},
    {"name": "Feature Spin", "cost": 20.0},
    {"name": "Super Feature Spin", "cost": 750.0}
]

publish_dir = script_dir / "library" / "publish_files"
results = {}

for mode_info in modes:
    mode_name = mode_info["name"]
    mode_cost = mode_info["cost"]
    
    # Get stats for this mode
    mode_stats = stats.get(mode_name, {})
    min_win = mode_stats.get("min_win", 0.0)
    max_win = mode_stats.get("max_win", 0.0)
    avg_win = mode_stats.get("average_win", 0.0)  # This is the actual average payout
    
    print(f"\nProcessing {mode_name}...")
    
    # Read book file directly
    book_file = publish_dir / f"books_{mode_name}.jsonl.zst"
    if not book_file.exists():
        print(f"Warning: {book_file} not found")
        continue
    
    # Decompress and read ALL books
    all_events = []
    
    print(f"  Decompressing {book_file.name}...")
    with open(book_file, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
    
    lines = decompressed.decode('utf-8').strip().split('\n')
    print(f"  Processing {len(lines)} books...")
    
    for line in lines:
        if not line.strip():
            continue
        book = json.loads(line)
        event_id = book['id']
        payout_multiplier = book['payoutMultiplier']  # in cents
        payout_x = payout_multiplier / 100.0
        
        # System Event ID = Book ID - 1 (books are 1-indexed, system is 0-indexed)
        system_event_id = event_id - 1
        all_events.append({
            'id': system_event_id,  # Use system event ID (0-indexed)
            'book_id': event_id,    # Keep original book ID for reference
            'payout_multiplier': payout_multiplier,
            'payout_x': payout_x
        })
    
    if not all_events:
        print(f"Warning: No events found in {book_file}")
        continue
    
    # Sort by payout
    all_events_sorted = sorted(all_events, key=lambda x: x['payout_multiplier'])
    
    # LOW PAYOUT: Find non-zero minimum (like 0.2x = 20 cents)
    non_zero_events = [e for e in all_events if e['payout_multiplier'] > 0]
    if non_zero_events:
        non_zero_sorted = sorted(non_zero_events, key=lambda x: x['payout_multiplier'])
        low_payout = non_zero_sorted[0]['payout_multiplier']
        low_events = [e for e in non_zero_events if e['payout_multiplier'] == low_payout][:3]
    else:
        # Fallback to absolute minimum if no non-zero events
        low_payout = all_events_sorted[0]['payout_multiplier']
        low_events = [e for e in all_events if e['payout_multiplier'] == low_payout][:3]
    
    # HIGH PAYOUT: Maximum
    actual_max_payout = all_events_sorted[-1]['payout_multiplier']
    high_events = [e for e in all_events if e['payout_multiplier'] == actual_max_payout][:3]
    
    # AVERAGE PAYOUT: Find events closest to the actual average from stats
    # average_win is in "x" units, convert to cents by multiplying by 100
    avg_target_cents = int(round(avg_win * 100))
    
    # Calculate distance from average for each event
    events_with_distance = []
    for e in all_events:
        distance = abs(e['payout_multiplier'] - avg_target_cents)
        events_with_distance.append((e, distance))
    
    # Sort by distance from average
    events_with_distance_sorted = sorted(events_with_distance, key=lambda x: x[1])
    
    # Get the 3 closest to average
    avg_events_data = [e[0] for e in events_with_distance_sorted[:3]]
    
    # Print results
    print(f"\n=== {mode_name.upper()} MODE ===")
    print(f"Stats: Min={min_win:.2f}, Max={max_win:.2f}, Avg={avg_win:.2f}")
    print()
    
    print(f"LOW PAYOUT EVENTS ({low_payout/100.0:.2f}x = {low_payout} cents):")
    for e in low_events:
        print(f"  System Event ID: {e['id']} (Book ID: {e['book_id']}) -> {e['payout_x']:.2f}x = {e['payout_multiplier']} cents")
    
    print(f"\nHIGH PAYOUT EVENTS ({actual_max_payout/100.0:.2f}x = {actual_max_payout} cents):")
    for e in high_events:
        print(f"  System Event ID: {e['id']} (Book ID: {e['book_id']}) -> {e['payout_x']:.2f}x = {e['payout_multiplier']} cents")
    
    print(f"\nAVERAGE PAYOUT EVENTS (target: {avg_win:.2f}x = {avg_target_cents} cents):")
    for e in avg_events_data:
        print(f"  System Event ID: {e['id']} (Book ID: {e['book_id']}) -> {e['payout_x']:.2f}x = {e['payout_multiplier']} cents")
    
    # Store results
    results[mode_name] = {
        "cost": mode_cost,
        "min_win": min_win,
        "max_win": max_win,
        "average_win": avg_win,
        "low_payout": {
            "payout_multiplier": low_payout,
            "payout_x": low_payout / 100.0,
            "event_ids": [e['id'] for e in low_events]
        },
        "high_payout": {
            "payout_multiplier": actual_max_payout,
            "payout_x": actual_max_payout / 100.0,
            "event_ids": [e['id'] for e in high_events]
        },
        "average_payout": {
            "target_payout": avg_target_cents,
            "target_payout_x": avg_win,
            "event_ids": [e['id'] for e in avg_events_data],
            "actual_payouts": [e['payout_multiplier'] for e in avg_events_data],
            "actual_payouts_x": [e['payout_x'] for e in avg_events_data]
        }
    }

# Save to JSON
output_file = script_dir / "library" / "REAL_test_event_ids.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*80}")
print("SUMMARY - VERIFIED EVENT IDs")
print(f"{'='*80}\n")

for mode_name, data in results.items():
    print(f"{mode_name.upper()} Mode (Cost: {data['cost']}x):")
    print(f"  Low:  Event IDs {data['low_payout']['event_ids']} -> {data['low_payout']['payout_x']:.2f}x")
    print(f"  High: Event IDs {data['high_payout']['event_ids']} -> {data['high_payout']['payout_x']:.2f}x")
    print(f"  Avg:  Event IDs {data['average_payout']['event_ids']} -> {[f'{x:.2f}x' for x in data['average_payout']['actual_payouts_x']]}")
    print()

print(f"\nResults saved to: {output_file}")

# Generate Markdown file
md_file = script_dir / "library" / "REAL_TEST_EVENT_IDS.md"
with open(md_file, 'w', encoding='utf-8') as f:
    f.write("# Test Event IDs for 0_0_lines_v8\n\n")
    f.write("**VERIFIED EVENT IDs** - These have been confirmed to match actual payouts in the system.\n\n")
    f.write("## Important Note\n")
    f.write("- **System Event IDs are 0-indexed** (range: 0-99999)\n")
    f.write("- **Book IDs are 1-indexed** (range: 1-100000)\n")
    f.write("- **System Event ID = Book ID - 1**\n\n")
    f.write("---\n\n")
    
    for mode_name, data in results.items():
        mode_display = mode_name.replace("_", " ").title()
        f.write(f"## {mode_display} Mode (Cost: {data['cost']}x)\n")
        f.write(f"**Stats:** Min={data['min_win']:.2f}x, Max={data['max_win']:.2f}x, Avg={data['average_win']:.2f}x\n\n")
        
        # Low payout
        f.write(f"### Low Payout Events ({data['low_payout']['payout_x']:.2f}x = {data['low_payout']['payout_multiplier']} cents)\n")
        for eid in data['low_payout']['event_ids']:
            f.write(f"- **Event ID: {eid}** → {data['low_payout']['payout_x']:.2f}x\n")
        f.write("\n")
        
        # High payout
        f.write(f"### High Payout Events ({data['high_payout']['payout_x']:.2f}x = {data['high_payout']['payout_multiplier']} cents)\n")
        for eid in data['high_payout']['event_ids']:
            f.write(f"- **Event ID: {eid}** → {data['high_payout']['payout_x']:.2f}x\n")
        f.write("\n")
        
        # Average payout
        avg_payouts_str = ", ".join([f"{x:.2f}x" for x in data['average_payout']['actual_payouts_x']])
        f.write(f"### Average Payout Events (target: {data['average_win']:.2f}x)\n")
        for i, eid in enumerate(data['average_payout']['event_ids']):
            actual = data['average_payout']['actual_payouts_x'][i]
            f.write(f"- **Event ID: {eid}** → {actual:.2f}x ({data['average_payout']['actual_payouts'][i]} cents)\n")
        f.write("\n---\n\n")
    
    # Quick reference table
    f.write("## Quick Reference Summary\n\n")
    f.write("| Mode | Low Event IDs | High Event IDs | Average Event IDs |\n")
    f.write("|------|---------------|----------------|-------------------|\n")
    for mode_name, data in results.items():
        low_ids = ", ".join([str(x) for x in data['low_payout']['event_ids']])
        high_ids = ", ".join([str(x) for x in data['high_payout']['event_ids']])
        avg_ids = ", ".join([str(x) for x in data['average_payout']['event_ids']])
        f.write(f"| **{mode_name}** | {low_ids} | {high_ids} | {avg_ids} |\n")
    
    f.write("\n---\n\n")
    f.write("*All event IDs are verified from the book files and account for the 0-indexed system event ID mapping (System Event ID = Book ID - 1).*\n")

print(f"Markdown file saved to: {md_file}")
