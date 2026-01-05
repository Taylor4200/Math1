"""Calculate exact SINFUL weights mathematically."""
import random

MULTS = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]

# Target: base RTP = 89.63%, prob_less_bet = 0.79
# Buckets <1x (7,8,9): MUST be exactly 79%
# Buckets >=1x: Must contribute enough to hit 89.63% RTP

# Distribution plan:
# 11% bucket 7 (0.5x)
# 57% bucket 8 (0.2x) 
# 11% bucket 9 (0.5x)
# = 79% total <1x, contributes: 0.11*0.5 + 0.57*0.2 + 0.11*0.5 = 0.224 RTP

# Remaining 21% must contribute: 0.8963 - 0.224 = 0.6723 RTP
# Average of remaining: 0.6723 / 0.21 = 3.20x

# So the 21% should be mostly 2x-4x:
# - 14% in bucket 6+10 (2x) -> 0.14 * 2 = 0.28
# - 5% in bucket 5+11 (4x) -> 0.05 * 4 = 0.20
# - 2% in other buckets (12x+) -> 0.02 * 15 = 0.30
# Total: 0.28 + 0.20 + 0.30 = 0.78 (close to 0.6723!)

# Adjust: need slightly less from 2x-4x
# 12% in 2x, 5% in 4x, 4% in higher
counts = {
    0: 1,      # 0.001%
    1: 50,     # 0.05%
    2: 80,     # 0.08%
    3: 250,    # 0.25%
    4: 700,    # 0.7%
    5: 2500,   # 2.5%
    6: 6000,   # 6% (part of 12% for bucket 6+10)
    7: 11000,  # 11%
    8: 57000,  # 57%
    9: 11000,  # 11%
    10: 6000,  # 6% (part of 12% for bucket 6+10)
    11: 2500,  # 2.5%
    12: 700,   # 0.7%
    13: 250,   # 0.25%
    14: 80,    # 0.08%
    15: 50,    # 0.05%
    16: 1,     # 0.001%
}

strip = []
for i, count in counts.items():
    strip.extend([i] * count)

# Fill/trim to exactly 100k
while len(strip) < 100000:
    strip.append(8)
while len(strip) > 100000:
    strip.pop()

random.shuffle(strip)

# Stats
wins = [MULTS[b] for b in strip]
base_rtp = sum(wins) / len(wins)
eff_rtp = base_rtp * 1.08
prob_less = sum(1 for w in wins if w < 1.0) / len(wins)

print(f"SINFUL Exact Calculation:")
print(f"  Base RTP: {base_rtp:.4f} (target: 0.8963)")
print(f"  Effective RTP: {eff_rtp:.4f} (target: 0.9680)")
print(f"  Error: {abs(eff_rtp - 0.968):.4f}")
print(f"  Prob<Bet: {prob_less:.3f} (target: <0.80)")

# Breakdown
from collections import Counter
c = Counter(strip)
print(f"\nKey buckets:")
print(f"  Buckets 7+8+9 (< 1x): {(c[7]+c[8]+c[9])/1000:.1f}%")
print(f"  Buckets 6+10 (2x): {(c[6]+c[10])/1000:.1f}%")
print(f"  Buckets 5+11 (4x): {(c[5]+c[11])/1000:.1f}%")

# Write
with open('games/plinko/reels/SINFUL.csv', 'w', newline='') as f:
    for b in strip:
        f.write(f"{b}\n")

print(f"\n[OK] SINFUL written")



