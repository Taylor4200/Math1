"""Extract event IDs for testing: low, high, and average payout events for each game mode."""
import csv
import json
import zstandard as zstd
from pathlib import Path

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
    
    # Read lookup table
    lookup_file = publish_dir / f"lookUpTable_{mode_name}_0.csv"
    if not lookup_file.exists():
        print(f"Warning: {lookup_file} not found")
        continue
    
    events = []
    with open(lookup_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                event_id = int(row[0])
                payout = int(row[2])  # payout multiplier in cents
                events.append((event_id, payout))
    
    if not events:
        print(f"Warning: No events found in {lookup_file}")
        continue
    
    # Find low, high, and average payout events
    events_sorted = sorted(events, key=lambda x: x[1])
    
    # Low payout events (minimum or near-minimum)
    low_payout = events_sorted[0][1]
    low_events = [eid for eid, p in events if p == low_payout][:3]  # Get up to 3 examples
    
    # High payout events (maximum or near-maximum)
    high_payout = events_sorted[-1][1]
    high_events = [eid for eid, p in events if p == high_payout][:3]  # Get up to 3 examples
    
    # Average payout events (closest to average, preferring non-zero)
    avg_target = int(round(avg_win))
    
    # For modes with very low averages, try to find non-zero events close to average
    if avg_win < 10 and min_win == 0:
        # Filter to non-zero events and find closest to average
        non_zero_events = [(eid, p) for eid, p in events if p > 0]
        if non_zero_events:
            avg_candidates = sorted(non_zero_events, key=lambda x: abs(x[1] - avg_target))
            avg_events = [eid for eid, p in avg_candidates[:3]]
            avg_actual = [p for eid, p in avg_candidates[:3]]
        else:
            # Fallback to all events
            avg_candidates = sorted(events, key=lambda x: abs(x[1] - avg_target))
            avg_events = [eid for eid, p in avg_candidates[:3]]
            avg_actual = [p for eid, p in avg_candidates[:3]]
    else:
        # For modes with higher averages, find closest to average
        avg_candidates = sorted(events, key=lambda x: abs(x[1] - avg_target))
        avg_events = [eid for eid, p in avg_candidates[:3]]
        avg_actual = [p for eid, p in avg_candidates[:3]]
    
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
            "actual_payouts": avg_actual
        }
    }

# Print results in a readable format
print("=" * 80)
print("TEST EVENT IDs BY GAME MODE")
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
        actual = data['average_payout']['actual_payouts'][i]
        print(f"    Event ID: {eid} (actual: {actual/100.0:.2f}x = {actual} cents)")
    print()
    print("-" * 80)
    print()

# Also save to JSON file
output_file = Path("library/test_event_ids.json")
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults also saved to: {output_file}")

