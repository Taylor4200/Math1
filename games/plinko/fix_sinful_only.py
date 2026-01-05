"""Fine-tune SINFUL only to hit RTP target while keeping prob_less_bet < 0.80."""

import random
import math

TARGET_RTP = 0.968
RESPIN_RATE = 0.08
BASE_RTP_NEEDED = TARGET_RTP / (1 + RESPIN_RATE)  # 0.8963

MULTIPLIERS = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]

print(f"SINFUL Target: {TARGET_RTP:.4f} -> Base RTP needed: {BASE_RTP_NEEDED:.4f}\n")

# Balanced approach: Target 89.63% base RTP with prob_less_bet < 0.80
# Need significant 1x-4x buckets to keep prob_less_bet down
# But also need 0.2x/0.5x to prevent RTP from being too high
weights = [
    1,      # Bucket 0 (1666x) - ultra rare
    15,     # Bucket 1 (400x)
    28,     # Bucket 2 (120x)
    87,     # Bucket 3 (40x)
    300,    # Bucket 4 (12x)
    1200,   # Bucket 5 (4x)
    3500,   # Bucket 6 (2x)
    10500,  # Bucket 7 (0.5x) - balance
    45000,  # Bucket 8 (0.2x) - reduced from 52000
    10500,  # Bucket 9 (0.5x) - balance
    3500,   # Bucket 10 (2x)
    1200,   # Bucket 11 (4x)
    300,    # Bucket 12 (12x)
    87,     # Bucket 13 (40x)
    28,     # Bucket 14 (120x)
    15,     # Bucket 15 (400x)
    1,      # Bucket 16 (1666x) - ultra rare
]

strip_length = 100000

# Create distribution
total = sum(weights)
bucket_strip = []
for bucket_idx, weight in enumerate(weights):
    count = int((weight / total) * strip_length)
    bucket_strip.extend([bucket_idx] * count)

# Fill to exact length
while len(bucket_strip) < strip_length:
    bucket_strip.append(8)

random.shuffle(bucket_strip)

# Calculate stats
wins = [MULTIPLIERS[b] for b in bucket_strip]
base_rtp = sum(wins) / len(wins)
effective_rtp = base_rtp * (1 + RESPIN_RATE)
prob_less_bet = sum(1 for w in wins if w < 1.0) / len(wins)

print(f"Base RTP: {base_rtp:.4f}")
print(f"Effective RTP: {effective_rtp:.4f} (target: {TARGET_RTP:.4f})")
print(f"Error: {abs(effective_rtp - TARGET_RTP):.4f}")
print(f"Prob<Bet: {prob_less_bet:.3f}")

# Write to CSV
with open('games/plinko/reels/SINFUL.csv', 'w', newline='') as f:
    for bucket in bucket_strip:
        f.write(f"{bucket}\n")

print(f"\nWrote {len(bucket_strip)} entries to SINFUL.csv")

# Show bucket frequencies
from collections import Counter
counts = Counter(bucket_strip)
print("Key buckets:")
for i in [0, 7, 8, 9, 16]:
    if i in counts:
        print(f"  Bucket {i:2d} ({MULTIPLIERS[i]:6.1f}x): {counts[i]:5d} ({counts[i]/1000:.1f}%)")

if effective_rtp <= TARGET_RTP + 0.002 and effective_rtp >= TARGET_RTP - 0.002 and prob_less_bet < 0.80:
    print("\n[OK] SINFUL optimized successfully!")
else:
    print(f"\n[WARN] Need adjustment - RTP off by {abs(effective_rtp - TARGET_RTP):.4f} or prob_less_bet={prob_less_bet:.3f}")

