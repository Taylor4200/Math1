"""
Quick Reel Balancer - Directly fixes extreme RTP issues
No iteration nonsense - just diagnose and fix in one shot
"""

import os
import sys
import json
import random
import zstandard as zstd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from generate_reels import ReelGenerator


def analyze_current_rtp():
    """Quick analysis of current RTP."""
    books_path = os.path.join(
        os.path.dirname(__file__), "library", "publish_files", "books_base.jsonl.zst"
    )
    
    if not os.path.exists(books_path):
        print("[ERROR] No books file found. Run a simulation first.")
        return None
    
    print("Analyzing current RTP...")
    data = []
    with open(books_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            text_stream = reader.read().decode('utf-8')
            for line in text_stream.strip().split('\n'):
                if line:
                    data.append(json.loads(line))
    
    total_spins = len(data)
    total_win = sum(spin.get('payoutMultiplier', 0) / 100.0 for spin in data)
    rtp = total_win / total_spins if total_spins > 0 else 0
    
    # Count multipliers
    mult_hits = 0
    for spin in data[:100]:  # Sample first 100
        events = spin.get('events', [])
        if events:
            board = events[0].get('board', [])
            symbols = [cell.get('name', '') for row in board for cell in row]
            if 'M' in symbols:
                mult_hits += 1
    
    print(f"  Current RTP: {rtp:.2f}x ({rtp*100:.0f}%)")
    print(f"  Multiplier hit rate: {mult_hits}%")
    
    return rtp


def fix_reels_for_low_rtp():
    """Generate reels with VERY low RTP for easier optimization."""
    print("\n" + "="*70)
    print("GENERATING LOW-RTP REELS")
    print("="*70)
    
    random.seed(42)
    
    # Base game - PROPER GAME DESIGN: 35% high symbols, 65% low symbols
    # Higher paying symbols = rarer (inverse relationship)
    print("\nBase Game Reels:")
    base_gen = ReelGenerator(
        num_reels=6, num_rows=250,
        symbol_weights={
            "H1": 0.09,  # Highest pay = rarest (~2.7 per board)
            "H2": 0.12,  # Medium-high pay = medium rare (~3.6 per board)
            "H3": 0.14,  # Lowest high pay = most common high (~4.2 per board)
            # Total high: 35% (~10.5 per board)
            "L1": 0.13,  # Highest low pay = rarest low (~3.9 per board)
            "L2": 0.15,  # Medium-low pay (~4.5 per board)
            "L3": 0.17,  # Medium pay (~5.1 per board)
            "L4": 0.18,  # Lowest pay = most common low (~5.4 per board)
            # Total low: 63% (~18.9 per board)
        },
        scatter_weight=0.008,  # Reduced scatters - fewer bonus triggers
        multiplier_weight=0.001,  # Almost no multipliers
    )
    base_gen.generate_reel_file("reels/BR0.csv", reel_type="basegame")
    
    # Free game - MORE multipliers and slightly more tumbles for bought bonuses
    # Higher paying symbols = rarer (inverse relationship)
    # More high symbols (40%) to reduce tumble frequency
    # MORE multipliers for bought bonuses to work properly
    print("\nFree Game Reels:")
    free_gen = ReelGenerator(
        num_reels=6, num_rows=250,
        symbol_weights={
            "H1": 0.11,  # Highest pay = rarest (~3.3 per board)
            "H2": 0.13,  # Medium-high pay = medium rare (~3.9 per board)
            "H3": 0.16,  # Lowest high pay = most common high (~4.8 per board)
            # Total high: 40% (~12 per board) - MORE high symbols to reduce tumbles
            "L1": 0.12,  # Highest low pay = rarest low (~3.6 per board)
            "L2": 0.14,  # Medium-low pay (~4.2 per board)
            "L3": 0.15,  # Medium pay (~4.5 per board)
            "L4": 0.16,  # Lowest pay = most common low (~4.8 per board)
            # Total low: 57% (~17.1 per board) - REDUCED to prevent cascades
        },
        scatter_weight=0.008,  # Reduced scatters - fewer bonus triggers
        multiplier_weight=0.005,  # Increased multipliers (0.5% = ~7-8 per reel strip)
    )
    free_gen.generate_reel_file("reels/FR0.csv", reel_type="freegame")
    
    print("\n" + "="*70)
    print("REELS REGENERATED")
    print("="*70)
    print("\nFree Game stats:")
    print("  - High symbols: 40% total (~12 per board)")
    print("    H1 (highest pay): 11% = rarest (~3.3 per board)")
    print("    H2 (medium pay): 13% = medium rare (~3.9 per board)")
    print("    H3 (lowest high): 16% = most common high (~4.8 per board)")
    print("  - Low symbols: 57% total (~17 per board)")
    print("    L1 (highest low): 12% = rarest low (~3.6 per board)")
    print("    L2: 14% (~4.2 per board)")
    print("    L3: 15% (~4.5 per board)")
    print("    L4 (lowest pay): 16% = most common (~4.8 per board)")
    print("  - Key: More high symbols (40%) reduces tumble frequency")
    print("  - Key: Lower low symbol density (~3-5 each) prevents cascades")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("QUICK REEL BALANCER")
    print("="*70)
    
    # Check current RTP
    current_rtp = analyze_current_rtp()
    
    if current_rtp and current_rtp > 10:
        print(f"\n[PROBLEM] RTP is {current_rtp:.0f}x - WAY too high!")
        print("This will make optimization impossible.")
        print("\nFixing now...")
    elif current_rtp:
        print(f"\n[INFO] Current RTP: {current_rtp:.2f}x")
        if current_rtp > 2.0:
            print("Still too high - fixing...")
        else:
            print("RTP looks reasonable. Regenerating anyway for consistency.")
    
    # Fix the reels
    fix_reels_for_low_rtp()
    
    print("\n[SUCCESS] Reels have been regenerated with low RTP weights.")
    print("Run your simulations now - they should be much faster and easier to optimize!")
