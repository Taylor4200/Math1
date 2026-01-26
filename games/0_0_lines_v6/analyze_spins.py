"""Analyze actual spins to find what's causing extreme RTP"""

import os
import json
import zstandard as zstd
from collections import Counter

books_path = os.path.join(
    os.path.dirname(__file__), "library", "publish_files", "books_base.jsonl.zst"
)

if not os.path.exists(books_path):
    print("No books file found!")
    exit(1)

print("Loading spins...")
data = []
with open(books_path, 'rb') as f:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(f) as reader:
        text_stream = reader.read().decode('utf-8')
        for line in text_stream.strip().split('\n'):
            if line:
                data.append(json.loads(line))

print(f"Loaded {len(data)} spins\n")

# Analyze top 20 biggest wins
wins = [(i, s.get('payoutMultiplier', 0) / 100.0) for i, s in enumerate(data)]
wins.sort(key=lambda x: x[1], reverse=True)

print("="*80)
print("TOP 20 BIGGEST WINS")
print("="*80)
for idx, (spin_idx, win) in enumerate(wins[:20]):
    spin = data[spin_idx]
    events = spin.get('events', [])
    
    # Find multipliers
    multipliers = []
    tumble_count = 0
    for event in events:
        if event.get('type') == 'reveal':
            tumble_count += 1
        if 'multiplier' in str(event).lower():
            mult_val = event.get('multiplier', event.get('value', 1))
            multipliers.append(mult_val)
    
    # Get board symbols
    board_symbols = []
    if events:
        first_board = events[0].get('board', [])
        for row in first_board:
            for cell in row:
                if isinstance(cell, dict):
                    board_symbols.append(cell.get('name', ''))
    
    mult_count = board_symbols.count('M')
    scatter_count = board_symbols.count('S')
    
    print(f"\n#{idx+1} Spin {spin_idx+1}: {win:.0f}x win")
    print(f"  Tumbles: {tumble_count}")
    print(f"  Multipliers on board: {mult_count}")
    print(f"  Scatters: {scatter_count}")
    print(f"  Multiplier values: {multipliers}")
    print(f"  Board symbols: {Counter(board_symbols)}")
    
    # Show first few events
    print(f"  First 3 events:")
    for i, e in enumerate(events[:3]):
        print(f"    {i+1}. {e.get('type', 'unknown')} - {str(e)[:100]}")

print("\n" + "="*80)
print("STATISTICS")
print("="*80)

total_win = sum(s.get('payoutMultiplier', 0) / 100.0 for s in data)
avg_win = total_win / len(data)
rtp = avg_win

print(f"Total spins: {len(data)}")
print(f"Total win: {total_win:.0f}x")
print(f"Average win: {avg_win:.2f}x")
print(f"RTP: {rtp:.2f}x ({rtp*100:.0f}%)")

# Count multiplier hits
mult_hits = 0
total_mults = 0
for spin in data:
    events = spin.get('events', [])
    if events:
        board = events[0].get('board', [])
        symbols = [cell.get('name', '') for row in board for cell in row]
        mults = symbols.count('M')
        if mults > 0:
            mult_hits += 1
            total_mults += mults

print(f"\nMultiplier analysis:")
print(f"  Spins with multipliers: {mult_hits} ({mult_hits/len(data)*100:.1f}%)")
print(f"  Total multiplier symbols: {total_mults}")
print(f"  Avg multipliers per spin: {total_mults/len(data):.2f}")

# Tumble analysis
tumble_counts = []
for spin in data:
    events = spin.get('events', [])
    tumbles = len([e for e in events if e.get('type') == 'reveal']) - 1
    tumble_counts.append(max(0, tumbles))

print(f"\nTumble analysis:")
print(f"  Avg tumbles per spin: {sum(tumble_counts)/len(tumble_counts):.2f}")
print(f"  Max tumbles: {max(tumble_counts)}")
print(f"  Spins with tumbles: {sum(1 for t in tumble_counts if t > 0)} ({sum(1 for t in tumble_counts if t > 0)/len(tumble_counts)*100:.1f}%)")

# Check for free game issues
freegame_wins = []
for spin in data:
    events = spin.get('events', [])
    has_freespin = any('free' in str(e).lower() for e in events)
    if has_freespin:
        win = spin.get('payoutMultiplier', 0) / 100.0
        freegame_wins.append(win)

if freegame_wins:
    print(f"\nFree game analysis:")
    print(f"  Spins with free games: {len(freegame_wins)}")
    print(f"  Avg free game win: {sum(freegame_wins)/len(freegame_wins):.0f}x")
    print(f"  Max free game win: {max(freegame_wins):.0f}x")
