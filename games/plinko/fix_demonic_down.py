"""Lower demonic RTP to hit ~94.80% simulation RTP."""

import numpy as np
import collections
from game_config import GameConfig

# Current simulation: 99.22%
# Target simulation: ~94.80%
# Decrease needed: 4.42%
# Current reel: 96.67%
# New target reel: 92.25%

TARGET_REEL_RTP = 0.9225

config = GameConfig()
multipliers = np.array(config.bucket_multipliers["demonic"])

# Read current demonic reel
with open('games/plinko/reels/DEMONIC.csv') as f:
    buckets = [int(line.strip()) for line in f]

counts = collections.Counter(buckets)
weights = np.array([counts[i] for i in range(17)])
total_weight = np.sum(weights)

current_rtp = np.sum(weights * multipliers) / total_weight
print(f"Current DEMONIC reel RTP: {current_rtp:.6f}")
print(f"Target DEMONIC reel RTP:  {TARGET_REEL_RTP:.6f}")
print(f"Lowering...")

# Decrease RTP by moving weight from 2x buckets to 0x buckets
max_iterations = 50000
for iteration in range(max_iterations):
    current_rtp = np.sum(weights * multipliers) / total_weight
    error = TARGET_REEL_RTP - current_rtp
    
    if abs(error) < 0.000001:
        break
    
    if error < 0:  # Need to decrease RTP
        # Take from 2x buckets (6 or 10)
        donor_idx = 6 if weights[6] > weights[10] else 10
        # Give to 0x buckets (7, 8, or 9)
        recipient_idx = 8 if weights[8] < weights[7] and weights[8] < weights[9] else (7 if weights[7] < weights[9] else 9)
        
        weights[donor_idx] -= 1
        weights[recipient_idx] += 1

final_rtp = np.sum(weights * multipliers) / total_weight
print(f"Final DEMONIC reel RTP:   {final_rtp:.6f}")
print(f"Error: {abs(final_rtp - TARGET_REEL_RTP):.8f}")
print(f"Iterations: {iteration + 1}")

# Write updated reel
bucket_list = []
for bucket_idx, weight in enumerate(weights):
    bucket_list.extend([bucket_idx] * int(weight))

np.random.shuffle(bucket_list)

with open('games/plinko/reels/DEMONIC.csv', 'w') as f:
    for bucket in bucket_list:
        f.write(f"{bucket}\n")

print(f"\n[OK] DEMONIC reel updated to {final_rtp:.6f} RTP")
print(f"     This should result in simulation RTP of ~94.80%")











