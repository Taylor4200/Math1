"""Extract verified event IDs directly from book files with accurate payouts."""
import json
import zstandard as zstd
from pathlib import Path

# Load stats to get average payouts
stats_path = Path("library/stats_summary.json")
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
    events_by_payout = {}
    all_events_list = []
    
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
        
        if payout_multiplier not in events_by_payout:
            events_by_payout[payout_multiplier] = []
        
        events_by_payout[payout_multiplier].append(event_id)
        all_events_list.append((event_id, payout_multiplier, payout_x))
    
    # Get all unique payouts and sort
    all_payouts = sorted(events_by_payout.keys())
    
    if not all_payouts:
        print(f"Warning: No events found in {book_file}")
        continue
    
    # Low payout events (minimum)
    low_payout = all_payouts[0]
    low_events = events_by_payout[low_payout][:3]
    
    # High payout events (maximum)
    high_payout = all_payouts[-1]
    high_events = events_by_payout[high_payout][:3]
    
    # Average payout events - find closest to average
    avg_target = int(round(avg_win))
    
    # Sort all events by distance from average
    events_with_distance = [(eid, p, abs(p - avg_target)) for eid, p, _ in all_events_list]
    events_with_distance_sorted = sorted(events_with_distance, key=lambda x: x[2])
    
    # For modes with very low averages, prefer non-zero events
    if avg_win < 10 and min_win == 0:
        non_zero = [e for e in events_with_distance_sorted if e[1] > 0]
        if non_zero:
            avg_events_data = non_zero[:3]
        else:
            avg_events_data = events_with_distance_sorted[:3]
    else:
        avg_events_data = events_with_distance_sorted[:3]
    
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

# Print results
print("=" * 80)
print("VERIFIED TEST EVENT IDs BY GAME MODE")
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
    
    print(f"  AVERAGE PAYOUT (target: {data['average_payout']['target_payout_x']:.2f}x):")
    for i, eid in enumerate(data['average_payout']['event_ids']):
        actual = data['average_payout']['actual_payouts_x'][i]
        actual_cents = data['average_payout']['actual_payouts'][i]
        print(f"    Event ID: {eid} (actual: {actual:.2f}x = {actual_cents} cents)")
    print()
    print("-" * 80)
    print()

# For base mode, also show some examples with the payouts the user mentioned
print("\n=== ADDITIONAL BASE MODE EXAMPLES ===")
print("Events with 0.2x (20 cents): Event IDs 23, 46, 68, 131, 142, 164, 184, 251, 334, 351")
print("Events with 0.3x (30 cents): Event IDs 1, 3, 13, 21, 36, 37, 49, 57, 60, 70")
print("Events with 2.6x (260 cents): Event IDs 262, 404, 709, 714, 991, 1140, 1525, 2311, 3385, 4079")
print()

# Save to JSON
output_file = Path("library/test_event_ids_final.json")
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_file}")








