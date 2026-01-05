"""Verify all three reel files have natural distributions."""

import collections
import numpy as np
from game_config import GameConfig

config = GameConfig()

print("="*70)
print("VERIFYING NATURAL BELL CURVE DISTRIBUTIONS")
print("="*70)

rtps = {}

for mode in ["mild", "sinful", "demonic"]:
    reel_key = mode.upper()
    multipliers = config.bucket_multipliers[mode]
    
    # Read buckets
    with open(f'games/plinko/reels/{reel_key}.csv') as f:
        buckets = [int(line.strip()) for line in f]
    
    counts = collections.Counter(buckets)
    total = len(buckets)
    
    # Calculate RTP
    rtp = sum(counts[i] * multipliers[i] for i in range(17)) / total
    rtps[mode] = rtp
    
    # Calculate center bucket percentage
    center_pct = (counts[7] + counts[8] + counts[9]) / total * 100
    
    print(f"\n{mode.upper()} Distribution:")
    print(f"  Total entries: {total:,}")
    print(f"  Actual RTP: {rtp:.6f} ({(1-rtp)*100:.2f}% house edge)")
    print(f"  Center buckets (7,8,9): {center_pct:.2f}%")
    
    if center_pct > 60:
        print(f"  [OK] Natural bell curve!")
    else:
        print(f"  [WARNING] Not a natural distribution")
    
    # Show top buckets
    print(f"\n  Top 5 buckets:")
    for bucket, count in counts.most_common(5):
        pct = count / total * 100
        mult = multipliers[bucket]
        print(f"    Bucket {bucket} ({mult}x): {count:6,} ({pct:5.2f}%)")

print("\n" + "="*70)
print("RTP SUMMARY")
print("="*70)
print(f"{'Mode':<12} {'RTP':<12} {'House Edge':<15}")
print("-" * 70)

for mode in ["mild", "sinful", "demonic"]:
    rtp = rtps[mode]
    house_edge = (1 - rtp) * 100
    print(f"{mode.upper():<12} {rtp:.6f}   {house_edge:.2f}%")

# Calculate range
rtp_values = list(rtps.values())
rtp_range = max(rtp_values) - min(rtp_values)

print()
print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.4f}%)")

if rtp_range <= 0.005:
    print("\n[OK] All modes within 0.5% margin!")
    print("\nNext step: Run simulations with: python games/plinko/run.py")
elif rtp_range <= 0.0075:
    print("\n[WARNING] Modes within 0.75% margin (close)")
else:
    print(f"\n[ERROR] Exceeds 0.5% margin by {(rtp_range-0.005)*100:.2f}%")

print()











