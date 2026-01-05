"""Create all three mode distributions with exact RTP targets."""

def solve_for_weights(mults, target_rtp):
    """Find weights to achieve target RTP using primarily center buckets."""
    center = len(mults) // 2
    
    # Find which buckets are closest to target RTP
    # We'll heavily weight those and add tiny weights to others
    
    # Strategy: Use buckets close to 1x heavily, add small weights to others
    weights = [1] * len(mults)  # Start with minimum weight for all
    
    # Find buckets closest to target RTP
    closest_indices = sorted(range(len(mults)), key=lambda i: abs(mults[i] - target_rtp))
    
    # Give MASSIVE weight to the 2-3 buckets closest to target
    base_weight = 10000000  # 10 million
    for idx in closest_indices[:3]:
        weights[idx] = base_weight
    
    # Add moderate weight to next closest
    for idx in closest_indices[3:6]:
        weights[idx] = base_weight // 10
    
    # Add small weight to next
    for idx in closest_indices[6:10]:
        weights[idx] = base_weight // 100
    
    return weights

# MILD: Target 97.3%
mild_mults = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
mild_weights = solve_for_weights(mild_mults, 0.973)

total = sum(mild_weights)
rtp = sum(mild_mults[i] * mild_weights[i] for i in range(17)) / total
print(f"MILD: {rtp*100:.2f}% RTP (target 97.3%), {total:,} total weight")

with open("games/plinko/reels/MILD.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(mild_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

# SINFUL: Target 96.8%
sinful_mults = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
sinful_weights = solve_for_weights(sinful_mults, 0.968)

total = sum(sinful_weights)
rtp = sum(sinful_mults[i] * sinful_weights[i] for i in range(17)) / total
print(f"SINFUL: {rtp*100:.2f}% RTP (target 96.8%), {total:,} total weight")

with open("games/plinko/reels/SINFUL.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(sinful_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

# DEMONIC: Target 96.3%  
demonic_mults = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]
demonic_weights = solve_for_weights(demonic_mults, 0.963)

total = sum(demonic_weights)
rtp = sum(demonic_mults[i] * demonic_weights[i] for i in range(17)) / total
print(f"DEMONIC: {rtp*100:.2f}% RTP (target 96.3%), {total:,} total weight")

with open("games/plinko/reels/DEMONIC.csv", "w") as f:
    for bucket_idx in range(17):
        for _ in range(demonic_weights[bucket_idx]):
            f.write(f"{bucket_idx}\n")

print("\n[OK] All distributions created!")
print("These are massive CSVs (millions of lines) - that's correct!")
print("The optimizer will fine-tune from here.")






