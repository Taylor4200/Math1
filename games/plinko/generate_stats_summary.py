"""Generate stats_summary.json from lookup tables."""

import csv
import json
import math

def calculate_stats_from_lookup(mode_name):
    """Calculate statistics from a lookup table CSV."""
    # Try optimized table first, fall back to base table
    optimized_filepath = f"games/plinko/library/publish_files/lookUpTable_{mode_name}_0.csv"
    base_filepath = f"games/plinko/library/lookup_tables/lookUpTable_{mode_name}.csv"
    
    import os
    if os.path.exists(optimized_filepath):
        filepath = optimized_filepath
    else:
        filepath = base_filepath
    
    wins = []
    weights = []
    
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            book_id, weight, win = row
            wins.append(float(win) / 100.0)  # Convert from cents to dollars
            weights.append(float(weight))
    
    total_weight = sum(weights)
    
    # Calculate RTP
    rtp = sum(w * win for w, win in zip(weights, wins)) / total_weight
    
    # Calculate other stats
    non_zero_wins = [(w, win) for w, win in zip(weights, wins) if win > 0]
    non_zero_weight = sum(w for w, win in non_zero_wins)
    prob_nil = 1.0 - (non_zero_weight / total_weight)
    
    # Hit rate for non-zero
    non_zero_hr = total_weight / non_zero_weight if non_zero_weight > 0 else 0
    
    # Prob less than bet (assuming bet = 1.0)
    less_than_bet_weight = sum(w for w, win in zip(weights, wins) if win < 1.0)
    prob_less_bet = less_than_bet_weight / total_weight
    
    # Max win hit rate
    max_win = max(wins)
    max_win_weight = sum(w for w, win in zip(weights, wins) if win == max_win)
    hr_max = total_weight / max_win_weight if max_win_weight > 0 else 0
    
    # Calculate variance and std
    mean = rtp
    variance = sum(w * ((win - mean) ** 2) for w, win in zip(weights, wins)) / total_weight
    std = math.sqrt(variance)
    
    # Mean to median
    cumulative = 0
    median_win = 0
    for w, win in sorted(zip(weights, wins), key=lambda x: x[1]):
        cumulative += w
        if cumulative >= total_weight / 2:
            median_win = win
            break
    m2m = mean / median_win if median_win > 0 else 0
    
    # Calculate skewness
    skew = sum(w * ((win - mean) ** 3) for w, win in zip(weights, wins)) / (total_weight * (std ** 3)) if std > 0 else 0
    
    # Calculate excess kurtosis (kurtosis - 3)
    kurtosis = sum(w * ((win - mean) ** 4) for w, win in zip(weights, wins)) / (total_weight * (std ** 4)) if std > 0 else 0
    excess_kurtosis = kurtosis - 3
    
    # Min diff (minimum difference between wins - useful for optimization)
    sorted_unique_wins = sorted(set(wins))
    if len(sorted_unique_wins) > 1:
        min_diff = min(b - a for a, b in zip(sorted_unique_wins, sorted_unique_wins[1:]) if b != a)
    else:
        min_diff = 0
    
    return {
        "num_events": len(wins),
        "weight_range": total_weight,
        "min_win": min(wins),
        "max_win": max_win,
        "min_diff": min_diff,
        "average_win": rtp,
        "rtp": rtp,
        "std": std,
        "var": variance,
        "m2m": m2m,
        "hr_max": hr_max,
        "non_zero_hr": non_zero_hr,
        "prob_nil": prob_nil,
        "num_non_zero_payouts": len(non_zero_wins),
        "prob_less_bet": prob_less_bet,
        "skew": skew,
        "excess_kurtosis": excess_kurtosis,
        "name": mode_name
    }

# Generate stats for all 3 modes
stats_summary = {}

for mode in ["mild", "sinful", "demonic"]:
    try:
        print(f"Calculating stats for {mode}...")
        stats_summary[mode] = calculate_stats_from_lookup(mode)
        print(f"  RTP: {stats_summary[mode]['rtp']:.4f} ({stats_summary[mode]['rtp']*100:.2f}%)")
        print(f"  HR Max: 1 in {int(stats_summary[mode]['hr_max']):,}")
        print(f"  Prob < Bet: {stats_summary[mode]['prob_less_bet']*100:.1f}%")
    except FileNotFoundError:
        print(f"  Skipping {mode} - lookup table not found")

# Write to file
with open("games/plinko/library/stats_summary.json", 'w') as f:
    json.dump(stats_summary, f, indent=4)

print("\n[OK] stats_summary.json generated!")


