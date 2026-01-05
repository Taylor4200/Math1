"""Create reels based on GAMEPLAY requirements (good hit rates)."""
import random

# Bucket multipliers
M_MILD = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
M_SINFUL = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
M_DEMONIC = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

# GAMEPLAY-FIRST hit rates (total 100K entries in reel)
# Format: [bucket_0, bucket_1, ..., bucket_16]

# MILD: Target 96% RTP with good gameplay
# 666x should be 1 in 5000 → 20 hits in 100K
# 150x should be 1 in 2500 → 40 hits
# 60x should be 1 in 1250 → 80 hits
# 20x should be 1 in 500 → 200 hits
# 8x should be 1 in 100 → 1000 hits
# 4x should be 1 in 50 → 2000 hits
# 2x should be 1 in 20 → 5000 hits
# 1x should be 1 in 5 → 20000 hits
# 0.5x fills the rest

mild_hits = [
    10, 20, 40, 100, 500, 1000, 2500, 10000,  # Buckets 0-7
    60000,  # Bucket 8 (0.5x) - most common
    10000,  2500, 1000, 500, 100, 40, 20, 10  # Buckets 9-16 (symmetric)
]

# SINFUL: Target 95.5% RTP
# Similar distribution but shifted for sinful multipliers
sinful_hits = [
    5, 10, 20, 50, 200, 800, 2000, 8000,  # Buckets 0-7
    70000,  # Bucket 8 (0.2x) - most common
    8000, 2000, 800, 200, 50, 20, 10, 5  # Buckets 9-16
]

# DEMONIC: Target 95% RTP
# 16666x should be 1 in 10000 → 10 hits
# More 0x payouts to balance the extreme max wins
demonic_hits = [
    5, 8, 15, 40, 120, 400, 1500, 11000,  # Buckets 0-7
    11000,  # Bucket 8 (0x)
    11000,  # Bucket 9 (0x)
    1500, 400, 120, 40, 15, 8, 5  # Buckets 10-16
]

def create_gameplay_reel(mode, hits, mults):
    """Create reel from hit rates."""
    reel = []
    for bucket, hit_count in enumerate(hits):
        reel.extend([bucket] * hit_count)
    
    # Shuffle
    random.seed(42)
    random.shuffle(reel)
    
    # Calculate RTP
    total_payout = sum(hits[i] * mults[i] for i in range(17))
    rtp = total_payout / len(reel)
    
    # Write reel
    with open(f"reels/{mode.upper()}.csv", 'w', newline='') as f:
        for bucket in reel:
            f.write(f"{bucket}\n")
    
    print(f"{mode.upper()}:")
    print(f"  Total entries: {len(reel)}")
    print(f"  RTP: {rtp:.2%}")
    print(f"  666x hit rate: 1 in {len(reel)//hits[0] if hits[0] > 0 else 'N/A'}")
    return rtp

print("="*70)
print("CREATING GAMEPLAY-FIRST REELS")
print("="*70)
print()

mild_rtp = create_gameplay_reel("mild", mild_hits, M_MILD)
sinful_rtp = create_gameplay_reel("sinful", sinful_hits, M_SINFUL)
demonic_rtp = create_gameplay_reel("demonic", demonic_hits, M_DEMONIC)

print(f"\n{'='*70}")
print(f"RTPs: MILD={mild_rtp:.2%}, SINFUL={sinful_rtp:.2%}, DEMONIC={demonic_rtp:.2%}")
print('='*70)







