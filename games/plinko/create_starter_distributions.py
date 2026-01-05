"""Create reasonable starting distributions closer to target RTPs."""

def create_bell_curve_distribution(multipliers, center_weight_multiplier=100):
    """Create a bell curve heavily weighted to center."""
    num_buckets = len(multipliers)
    center = num_buckets // 2
    
    weights = []
    for i in range(num_buckets):
        # Distance from center
        dist_from_center = abs(i - center)
        # Exponential decay from center
        weight = max(1, int(center_weight_multiplier / (2 ** dist_from_center)))
        weights.append(weight)
    
    return weights

# MILD multipliers
mild_mults = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]

# Create distribution heavily weighted to center
mild_weights = create_bell_curve_distribution(mild_mults, center_weight_multiplier=10000)

# Calculate expected RTP
total_weight = sum(mild_weights)
expected_rtp = sum(mild_mults[i] * mild_weights[i] for i in range(17)) / total_weight

print("MILD Mode Distribution:")
print(f"Total weight: {total_weight}")
print(f"Expected RTP: {expected_rtp:.4f} ({expected_rtp*100:.2f}%)")
print("\nWeights:")
for i in range(17):
    pct = (mild_weights[i] / total_weight) * 100
    print(f"  Bucket {i:2d}: {mild_mults[i]:6}x × {mild_weights[i]:4d} = {pct:5.2f}%")

# Write to CSV
print("\nWriting MILD.csv...")
with open("games/plinko/reels/MILD.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(mild_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

# SINFUL
sinful_mults = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
sinful_weights = create_bell_curve_distribution(sinful_mults, center_weight_multiplier=20000)
total = sum(sinful_weights)
rtp = sum(sinful_mults[i] * sinful_weights[i] for i in range(17)) / total
print(f"\nSINFUL Expected RTP: {rtp:.4f} ({rtp*100:.2f}%)")

with open("games/plinko/reels/SINFUL.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(sinful_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

# DEMONIC
demonic_mults = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]
demonic_weights = create_bell_curve_distribution(demonic_mults, center_weight_multiplier=50000)
total = sum(demonic_weights)
rtp = sum(demonic_mults[i] * demonic_weights[i] for i in range(17)) / total
print(f"DEMONIC Expected RTP: {rtp:.4f} ({rtp*100:.2f}%)")

with open("games/plinko/reels/DEMONIC.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(demonic_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

print("\n[OK] All distributions created!")

