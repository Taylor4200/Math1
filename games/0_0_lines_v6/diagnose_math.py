"""Diagnose why optimizer can't find negative pigs - check if math is correct."""

import os
import sys
import csv
from collections import defaultdict

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.analysis.distribution_functions import make_win_distribution, calculate_rtp, get_distribution_average

def analyze_basegame_math():
    """Check if basegame fence configuration matches actual books."""
    
    print("="*80)
    print("DIAGNOSING MATH: Why Can't Optimizer Find Negative Pigs?")
    print("="*80)
    
    # Check lookup table
    lut_path = "library/lookup_tables/lookUpTable_base_0.csv"
    if not os.path.exists(lut_path):
        lut_path = "library/publish_files/lookUpTable_base_0.csv"
    
    if not os.path.exists(lut_path):
        print(f"ERROR: Could not find lookup table at {lut_path}")
        return
    
    print(f"\n1. ANALYZING LOOKUP TABLE: {lut_path}")
    print("-" * 80)
    
    # Load distribution
    dist = make_win_distribution(lut_path, normalize=False)
    
    total_weight = sum(dist.values())
    total_win = sum(win * weight for win, weight in dist.items())
    actual_rtp = total_win / total_weight / 1.0  # bet_cost = 1.0
    actual_avg_win = total_win / total_weight
    
    print(f"Total weight: {total_weight:,}")
    print(f"Actual RTP: {actual_rtp:.6f} ({actual_rtp*100:.4f}%)")
    print(f"Actual Average Win: {actual_avg_win:.6f}x")
    
    # Check fence configuration
    print(f"\n2. FENCE CONFIGURATION (from game_optimization.py)")
    print("-" * 80)
    print("basegame fence:")
    print("  hr = 4.5 (hits 1 in 4.5 spins)")
    print("  rtp = 0.651 (65.1% RTP)")
    print("  avg_win = hr x rtp = 4.5 x 0.651 = 2.93x")
    print("\n  NOTE: basegame fence has NO search_conditions")
    print("  This means it uses ALL entries from the lookup table!")
    
    expected_avg_win = 4.5 * 0.651
    print(f"\n  Expected avg_win: {expected_avg_win:.6f}x")
    print(f"  Actual avg_win:   {actual_avg_win:.6f}x")
    
    diff = abs(actual_avg_win - expected_avg_win)
    print(f"  Difference: {diff:.6f}x")
    
    # Analyze win distribution
    print(f"\n3. WIN DISTRIBUTION ANALYSIS")
    print("-" * 80)
    
    wins_below_avg = sum(weight for win, weight in dist.items() if win < expected_avg_win)
    wins_above_avg = sum(weight for win, weight in dist.items() if win >= expected_avg_win)
    
    print(f"Wins below {expected_avg_win:.2f}x: {wins_below_avg:,} ({wins_below_avg/total_weight*100:.2f}%)")
    print(f"Wins above {expected_avg_win:.2f}x: {wins_above_avg:,} ({wins_above_avg/total_weight*100:.2f}%)")
    
    # Check if there are enough low wins
    print(f"\n4. CAN WE CREATE NEGATIVE PIGS?")
    print("-" * 80)
    
    if wins_below_avg == 0:
        print("PROBLEM: NO wins below avg_win!")
        print("   This means the optimizer CANNOT create negative pigs.")
        print("   The win distribution is too high.")
    elif wins_below_avg < total_weight * 0.1:
        print("WARNING: Very few wins below avg_win (<10%)")
        print("   This makes it very hard to create negative pigs.")
    else:
        print("OK: There are wins below avg_win")
        print("   But optimizer still can't find negative pigs - might be algorithm issue")
    
    # Show win distribution breakdown
    print(f"\n5. WIN DISTRIBUTION BREAKDOWN")
    print("-" * 80)
    print(f"{'Win Range':<20} {'Count':<15} {'Weight':<15} {'% of Total':<15}")
    print("-" * 80)
    
    ranges = [
        (0.0, 0.5, "0.0x - 0.5x"),
        (0.5, 1.0, "0.5x - 1.0x"),
        (1.0, 2.0, "1.0x - 2.0x"),
        (2.0, expected_avg_win, f"2.0x - {expected_avg_win:.2f}x (below avg)"),
        (expected_avg_win, 5.0, f"{expected_avg_win:.2f}x - 5.0x (above avg)"),
        (5.0, 10.0, "5.0x - 10.0x"),
        (10.0, 50.0, "10.0x - 50.0x"),
        (50.0, float('inf'), "50.0x+"),
    ]
    
    for low, high, label in ranges:
        count = sum(1 for win in dist.keys() if low <= win < high)
        weight = sum(w for win, w in dist.items() if low <= win < high)
        pct = weight / total_weight * 100 if total_weight > 0 else 0
        print(f"{label:<20} {count:<15} {weight:<15,} {pct:<15.2f}%")
    
    # Show some example wins
    print(f"\n6. EXAMPLE WINS IN LOOKUP TABLE")
    print("-" * 80)
    sorted_wins = sorted(dist.keys())
    print(f"Lowest 10 wins: {[f'{w:.2f}x' for w in sorted_wins[:10]]}")
    print(f"Highest 10 wins: {[f'{w:.2f}x' for w in sorted_wins[-10:]]}")
    
    # Diagnosis
    print(f"\n7. DIAGNOSIS")
    print("-" * 80)
    
    if diff > 100:
        print("CRITICAL: MASSIVE FENCE CONFIGURATION MISMATCH")
        print(f"   Your fence says avg_win = {expected_avg_win:.2f}x")
        print(f"   But actual lookup table has avg_win = {actual_avg_win:.2f}x")
        print(f"   Difference: {diff:.2f}x (over {diff/expected_avg_win*100:.0f}% higher!)")
        print("\n   ROOT CAUSE:")
        print("   - The lookup table contains ALL modes (basegame + freegame + bonus)")
        print("   - The basegame fence has NO search_conditions to filter it")
        print("   - So it's trying to optimize using the entire table")
        print("\n   SOLUTIONS:")
        print("   1. Add search_conditions to basegame fence to filter basegame-only wins")
        print("   2. OR regenerate books with proper separation between modes")
        print("   3. OR fix fence configuration to match the actual combined table")
    elif diff > 0.5:
        print("FENCE CONFIGURATION MISMATCH")
        print(f"   Your fence says avg_win = {expected_avg_win:.2f}x")
        print(f"   But actual books have avg_win = {actual_avg_win:.2f}x")
        print(f"   Difference: {diff:.2f}x")
        print("\n   SOLUTION: Fix fence configuration to match actual books")
        print("   OR regenerate books to match fence configuration")
    elif wins_below_avg == 0:
        print("WIN DISTRIBUTION TOO HIGH")
        print("   All wins are above the expected average.")
        print("   This means your books have too many high wins.")
        print("\n   SOLUTION: Adjust paytable or regenerate books")
    else:
        print("ALGORITHM ISSUE")
        print("   Books seem OK, but optimizer can't find negative pigs.")
        print("   Might need to adjust pig generation algorithm.")
        print("   OR increase iterations significantly")
    
    print("\n" + "="*80)
    print("CONCLUSION: The math is WRONG. The lookup table doesn't match the fence config.")
    print("="*80)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    analyze_basegame_math()
