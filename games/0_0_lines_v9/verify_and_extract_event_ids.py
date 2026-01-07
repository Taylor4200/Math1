"""Extract event IDs directly from book files to ensure accuracy."""
import json
import zstandard as zstd
from pathlib import Path
from collections import defaultdict

# Load stats to get average payouts
stats_path = Path("library/stats_summary.json")
with open(stats_path, 'r') as f:
    stats = json.load(f)

# Game modes from index.json
modes = [
    {"name": "base", "cost": 1.0},
    {"name": "Bonus", "cost": 100.0},
    {"name": "Super Bonus", "cost": 500.0},
    {"name": "Bonus Booster", "cost": 2.0},
    {"name": "Feature Spin", "cost": 20.0},
    {"name": "Super Feature Spin", "cost": 750.0}
]

publish_dir = Path("library/publish_files")
results = {}

for mode_info in modes:
    mode_name = mode_info["name"]
    mode_cost = mode_info["cost"]
    
    # Get stats for this mode
    mode_stats = stats.get(mode_name, {})
    min_win = mode_stats.get("min_win", 0.0)
    max_win = mode_stats.get("max_win", 0.0)
    avg_win = mode_stats.get("average_win", 0.0)
    
    # Read book file directly
    book_file = publish_dir / f"books_{mode_name}.jsonl.zst"
    if not book_file.exists():
        print(f"Warning: {book_file} not found")
        continue
    
    # Decompress and read books
    events_by_payout = defaultdict(list)
    with open(book_file, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(f.read())
    
    lines = decompressed.decode('utf-8').strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
        book = json.loads(line)
        event_id = book['id']
        payout_multiplier = book['payoutMultiplier']  # in cents
        payout_x = payout_multiplier / 100.0
        
        events_by_payout[payout_multiplier].append({
            'id': event_id,
            'payout_multiplier': payout_multiplier,
            'payout_x': payout_x
        })
    
    # Get all unique payouts and sort
    all_payouts = sorted(events_by_payout.keys())
    
    if not all_payouts:
        print(f"Warning: No events found in {book_file}")
        continue
    
    # Low payout events
    low_payout = all_payouts[0]
    low_events_data = events_by_payout[low_payout][:3]
    low_events = [e['id'] for e in low_events_data]
    
    # High payout events
    high_payout = all_payouts[-1]
    high_events_data = events_by_payout[high_payout][:3]
    high_events = [e['id'] for e in high_events_data]
    
    # Average payout events (closest to average)
    avg_target = int(round(avg_win))
    
    # Find events closest to average
    all_events = []
    for payout, event_list in events_by_payout.items():
        for event in event_list:
            all_events.append((event['id'], payout, abs(payout - avg_target)))
    
    # Sort by distance from average
    all_events_sorted = sorted(all_events, key=lambda x: x[2])
    
    # For modes with very low averages, prefer non-zero events
    if avg_win < 10 and min_win == 0:
        non_zero_events = [e for e in all_events_sorted if e[1] > 0]
        if non_zero_events:
            avg_events_data = non_zero_events[:3]
        else:
            avg_events_data = all_events_sorted[:3]
    else:
        avg_events_data = all_events_sorted[:3]
    
    avg_events = [e[0] for e in avg_events_data]
    avg_actual_payouts = [e[1] for e in avg_events_data]
    
    results[mode_name] = {
        "cost": mode_cost,
        "min_win": min_win,
        "max_win": max_win,
        "average_win": avg_win,
        "low_payout": {
            "payout_multiplier": low_payout,
            "payout_x": low_payout / 100.0,
            "event_ids": low_events
        },
        "high_payout": {
            "payout_multiplier": high_payout,
            "payout_x": high_payout / 100.0,
            "event_ids": high_events
        },
        "average_payout": {
            "target_payout": avg_target,
            "target_payout_x": avg_target / 100.0,
            "event_ids": avg_events,
            "actual_payouts": avg_actual_payouts,
            "actual_payouts_x": [p / 100.0 for p in avg_actual_payouts]
        }
    }
    
    # Verify the user's reported events for base mode
    if mode_name == "base":
        print(f"\n=== VERIFYING BASE MODE EVENTS ===")
        for event_id in [250, 348, 403]:
            # Find this event in the books
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
                print(f"Event ID {event_id}: NOT FOUND")

# Print results
print("\n" + "=" * 80)
print("TEST EVENT IDs BY GAME MODE (FROM BOOK FILES)")
print("=" * 80)
print()

for mode_name, data in results.items():
    print(f"Mode: {mode_name} (Cost: {data['cost']}x)")
    print(f"  Stats: Min={data['min_win']:.2f}, Max={data['max_win']:.2f}, Avg={data['average_win']:.2f}")
    print()
    
    print(f"  LOW PAYOUT ({data['low_payout']['payout_x']:.2f}x = {data['low_payout']['payout_multiplier']} cents):")
    for eid in data['low_payout']['event_ids']:
        print(f"    Event ID: {eid}")
    print()
    
    print(f"  HIGH PAYOUT ({data['high_payout']['payout_x']:.2f}x = {data['high_payout']['payout_multiplier']} cents):")
    for eid in data['high_payout']['event_ids']:
        print(f"    Event ID: {eid}")
    print()
    
    print(f"  AVERAGE PAYOUT (target: {data['average_payout']['target_payout_x']:.2f}x = {data['average_payout']['target_payout']} cents):")
    for i, eid in enumerate(data['average_payout']['event_ids']):
        actual = data['average_payout']['actual_payouts_x'][i]
        actual_cents = data['average_payout']['actual_payouts'][i]
        print(f"    Event ID: {eid} (actual: {actual:.2f}x = {actual_cents} cents)")
    print()
    print("-" * 80)
    print()

# Save to JSON
output_file = Path("library/test_event_ids_verified.json")
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_file}")








