"""Solve for exact weights to achieve target RTP."""

def solve_two_bucket_rtp(mult1, mult2, target_rtp, weight1=1000000):
    """
    Solve for weight2 given:
    (mult1 * weight1 + mult2 * weight2) / (weight1 + weight2) = target_rtp
    """
    # Rearrange: mult1*w1 + mult2*w2 = target*(w1 + w2)
    # mult1*w1 + mult2*w2 = target*w1 + target*w2
    # mult2*w2 - target*w2 = target*w1 - mult1*w1
    # w2*(mult2 - target) = w1*(target - mult1)
    # w2 = w1 * (target - mult1) / (mult2 - target)
    
    weight2 = weight1 * (target_rtp - mult1) / (mult2 - target_rtp)
    return weight2

# MILD: Want 97.3% RTP
# Use bucket 8 (0.5x) and bucket 9 (1x) as primary weights
w8 = 1000000
w9 = solve_two_bucket_rtp(0.5, 1.0, 0.973, w8)

print(f"To achieve 97.3% RTP:")
print(f"  Bucket 8 (0.5x): {w8:,.0f} weight")
print(f"  Bucket 9 (1x):   {w9:,.0f} weight")

# Verify
total = w8 + w9
rtp = (0.5 * w8 + 1.0 * w9) / total
print(f"  Verification: {rtp*100:.4f}% RTP")

# Now create full distribution with these as base + tiny amounts of others
mild_mults = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
weights = [
    1,      # 0: 666x
    1,      # 1: 150x
    1,      # 2: 60x
    5,      # 3: 20x
    50,     # 4: 8x
    500,    # 5: 4x
    5000,   # 6: 2x
    10000,  # 7: 1x (but we'll adjust based on our calculation)
    int(w8),  # 8: 0.5x - MASSIVE
    int(w9),  # 9: 1x - MASSIVE
    5000,   # 10: 2x
    500,    # 11: 4x
    50,     # 12: 8x
    5,      # 13: 20x
    1,      # 14: 60x
    1,      # 15: 150x
    1,      # 16: 666x
]

# Wait, let me use bucket 7 and 9 (both 1x) to balance bucket 8 (0.5x)
# Split the calculated weight between them
w_one_x = int(w9 / 2)  # Split between buckets 7 and 9
weights[7] = w_one_x
weights[9] = w_one_x

total_weight = sum(weights)
actual_rtp = sum(mild_mults[i] * weights[i] for i in range(17)) / total_weight

print(f"\nFinal MILD Distribution:")
print(f"  Total weight: {total_weight:,}")
print(f"  Actual RTP: {actual_rtp*100:.4f}%")
print(f"  Target: 97.30%")
print(f"  Error: {abs(actual_rtp - 0.973)*100:.4f}%")

# Print key buckets
for i in [0, 7, 8, 9, 16]:
    pct = weights[i] / total_weight * 100
    print(f"  Bucket {i}: {mild_mults[i]}x × {weights[i]:,} = {pct:.4f}%")

if abs(actual_rtp - 0.973) < 0.01:  # Within 1%
    print("\n[OK] Writing MILD.csv...")
    with open("games/plinko/reels/MILD.csv", "w") as f:
        for bucket_idx in range(17):
            for _ in range(weights[bucket_idx]):
                f.write(f"{bucket_idx}\n")
    print(f"  File size: {total_weight:,} lines")
    print("  [OK] Done!")
else:
    print(f"\n[ERROR] Still {abs(actual_rtp - 0.973)*100:.2f}% off target")







