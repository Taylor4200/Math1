"""Create proper distributions targeting 97% RTP."""

mild_mults = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]

# For 97.3% RTP, need to weight buckets near 1x heavily
# Bucket 7: 1x, Bucket 9: 1x are perfect for ~100% RTP
# Mix with some 0.5x and 2x to fine-tune

weights = [
    1,       # 0: 666x - ultra rare
    1,       # 1: 150x - ultra rare
    5,       # 2: 60x - very rare
    50,      # 3: 20x - rare
    500,     # 4: 8x - uncommon
    2000,    # 5: 4x - common
    5000,    # 6: 2x - very common
    20000,   # 7: 1x - MOST common (close to target RTP!)
    15000,   # 8: 0.5x - very common (pulls RTP down)
    20000,   # 9: 1x - MOST common
    5000,    # 10: 2x - very common
    2000,    # 11: 4x - common
    500,     # 12: 8x - uncommon
    50,      # 13: 20x - rare
    5,       # 14: 60x - very rare
    1,       # 15: 150x - ultra rare
    1,       # 16: 666x - ultra rare
]

total = sum(weights)
rtp = sum(mild_mults[i] * weights[i] for i in range(17)) / total

print(f"MILD Distribution:")
print(f"  Total weight: {total:,}")
print(f"  Expected RTP: {rtp*100:.2f}%")
print(f"  Target RTP: 97.3%")
print(f"  Difference: {abs(rtp - 0.973)*100:.2f}%")

if abs(rtp - 0.973) < 0.05:
    print("  [OK] Within 5% of target!")
    
    # Write CSV
    with open("games/plinko/reels/MILD.csv", "w") as f:
        for bucket_idx in range(17):
            for _ in range(weights[bucket_idx]):
                f.write(f"{bucket_idx}\n")
    print("  [OK] MILD.csv written")
    
    # SINFUL - adjust for 96.8%
    sinful_mults = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
    # Similar strategy but weight 0.5x buckets more (buckets 7/9)
    sinful_weights = [
        1, 1, 5, 50, 500, 2000, 5000,
        18000,  # 7: 0.5x
        20000,  # 8: 0.2x (center)
        18000,  # 9: 0.5x  
        5000, 2000, 500, 50, 5, 1, 1
    ]
    s_total = sum(sinful_weights)
    s_rtp = sum(sinful_mults[i] * sinful_weights[i] for i in range(17)) / s_total
    print(f"\nSINFUL: {s_rtp*100:.2f}% RTP")
    
    with open("games/plinko/reels/SINFUL.csv", "w") as f:
        for bucket_idx in range(17):
            for _ in range(sinful_weights[bucket_idx]):
                f.write(f"{bucket_idx}\n")
    print("  [OK] SINFUL.csv written")
    
    # DEMONIC - center buckets are 0x! Perfect for low RTP
    demonic_mults = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]
    # Weight 0x buckets heavily, add some 2x/4x/8x for RTP
    demonic_weights = [
        1, 1, 5, 50, 500, 2000, 5000,
        30000,  # 7: 0x
        40000,  # 8: 0x (center, most common)
        30000,  # 9: 0x
        5000, 2000, 500, 50, 5, 1, 1
    ]
    d_total = sum(demonic_weights)
    d_rtp = sum(demonic_mults[i] * demonic_weights[i] for i in range(17)) / d_total
    print(f"\nDEMONIC: {d_rtp*100:.2f}% RTP")
    
    with open("games/plinko/reels/DEMONIC.csv", "w") as f:
        for bucket_idx in range(17):
            for _ in range(demonic_weights[bucket_idx]):
                f.write(f"{bucket_idx}\n")
    print("  [OK] DEMONIC.csv written")
    
    print("\n[OK] All distributions created!")
else:
    print(f"  [ERROR] Still {abs(rtp - 0.973)*100:.2f}% off target")
    print("  Need to adjust weights further")







