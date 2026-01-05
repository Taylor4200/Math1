"""Create balanced, fun Plinko reels with proper distribution."""
import random
import csv

# Bucket multipliers for each mode
MILD_MULTS = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
SINFUL_MULTS = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
DEMONIC_MULTS = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

def create_balanced_mild_reel():
    """Create MILD reel with fun, balanced distribution."""
    reel = []
    
    # Target: ~96% RTP with engaging gameplay
    # Weights: higher multipliers = rarer, but not impossibly rare
    
    weights = {
        0: 1,        # 666x - Jackpot
        1: 10,       # 150x - High win
        2: 100,      # 60x - Big win
        3: 500,      # 20x - Good win
        4: 2000,     # 8x - Nice win
        5: 8000,     # 4x - Decent win
        6: 19000,    # 2x - Double up
        7: 82000,    # 1x - Break even
        8: 355000,   # 0.5x - Small loss (most common)
        9: 82000,    # 1x - Break even
        10: 19000,   # 2x - Double up
        11: 8000,    # 4x - Decent win
        12: 2000,    # 8x - Nice win
        13: 500,     # 20x - Good win
        14: 100,     # 60x - Big win
        15: 10,      # 150x - High win
        16: 1,       # 666x - Jackpot
    }
    
    # Build reel
    for bucket, weight in weights.items():
        reel.extend([bucket] * weight)
    
    # Shuffle for randomness
    random.shuffle(reel)
    
    # Calculate actual RTP
    total = len(reel)
    rtp = sum(MILD_MULTS[bucket] for bucket in reel) / total
    
    print(f"MILD Reel Created:")
    print(f"  Total entries: {total:,}")
    print(f"  Calculated RTP: {rtp:.4f} ({rtp*100:.2f}%)")
    
    # Show distribution
    from collections import Counter
    counts = Counter(reel)
    print(f"\n  Distribution:")
    for bucket in sorted(counts.keys()):
        mult = MILD_MULTS[bucket]
        count = counts[bucket]
        pct = count / total * 100
        print(f"    Bucket {bucket:2d} ({mult:6.1f}x): {count:7,} ({pct:5.2f}%)")
    
    return reel, rtp

def create_balanced_sinful_reel():
    """Create SINFUL reel - higher variance, still balanced."""
    reel = []
    
    weights = {
        0: 1,        # 1666x - Mega jackpot
        1: 5,        # 400x - Huge win
        2: 50,       # 120x - Big win
        3: 540,      # 40x - Good win
        4: 3700,     # 12x - Nice win
        5: 17500,    # 4x - Decent win
        6: 45000,    # 2x - Double up
        7: 157000,   # 0.5x - Small loss
        8: 268000,   # 0.2x - Loss (most common)
        9: 157000,   # 0.5x - Small loss
        10: 45000,   # 2x - Double up
        11: 17500,   # 4x - Decent win
        12: 3700,    # 12x - Nice win
        13: 540,     # 40x - Good win
        14: 50,      # 120x - Big win
        15: 5,       # 400x - Huge win
        16: 1,       # 1666x - Mega jackpot
    }
    
    for bucket, weight in weights.items():
        reel.extend([bucket] * weight)
    
    random.shuffle(reel)
    
    total = len(reel)
    rtp = sum(SINFUL_MULTS[bucket] for bucket in reel) / total
    
    print(f"\nSINFUL Reel Created:")
    print(f"  Total entries: {total:,}")
    print(f"  Calculated RTP: {rtp:.4f} ({rtp*100:.2f}%)")
    
    from collections import Counter
    counts = Counter(reel)
    print(f"\n  Distribution:")
    for bucket in sorted(counts.keys()):
        mult = SINFUL_MULTS[bucket]
        count = counts[bucket]
        pct = count / total * 100
        print(f"    Bucket {bucket:2d} ({mult:6.1f}x): {count:7,} ({pct:5.2f}%)")
    
    return reel, rtp

def create_balanced_demonic_reel():
    """Create DEMONIC reel - extreme variance, massive jackpots."""
    reel = []
    
    weights = {
        0: 1,        # 16666x - MEGA JACKPOT
        1: 3,        # 2500x - Insane win
        2: 32,       # 600x - Huge win
        3: 250,      # 150x - Big win
        4: 2150,     # 40x - Good win
        5: 16800,    # 8x - Nice win
        6: 60000,    # 2x - Double up
        7: 228000,   # 0x - Loss
        8: 274000,   # 0x - Loss (most common)
        9: 228000,   # 0x - Loss
        10: 60000,   # 2x - Double up
        11: 16800,   # 8x - Nice win
        12: 2150,    # 40x - Good win
        13: 250,     # 150x - Big win
        14: 32,      # 600x - Huge win
        15: 3,       # 2500x - Insane win
        16: 1,       # 16666x - MEGA JACKPOT
    }
    
    for bucket, weight in weights.items():
        reel.extend([bucket] * weight)
    
    random.shuffle(reel)
    
    total = len(reel)
    rtp = sum(DEMONIC_MULTS[bucket] for bucket in reel) / total
    
    print(f"\nDEMONIC Reel Created:")
    print(f"  Total entries: {total:,}")
    print(f"  Calculated RTP: {rtp:.4f} ({rtp*100:.2f}%)")
    
    from collections import Counter
    counts = Counter(reel)
    print(f"\n  Distribution:")
    for bucket in sorted(counts.keys()):
        mult = DEMONIC_MULTS[bucket]
        count = counts[bucket]
        pct = count / total * 100
        print(f"    Bucket {bucket:2d} ({mult:6.1f}x): {count:7,} ({pct:5.2f}%)")
    
    return reel, rtp

def save_reel(reel, filename):
    """Save reel to CSV."""
    with open(f'reels/{filename}', 'w', newline='') as f:
        writer = csv.writer(f)
        for bucket in reel:
            writer.writerow([bucket])
    print(f"\n✅ Saved to reels/{filename}")

if __name__ == "__main__":
    print("="*70)
    print("CREATING BALANCED PLINKO REELS")
    print("="*70)
    
    mild_reel, mild_rtp = create_balanced_mild_reel()
    save_reel(mild_reel, 'MILD.csv')
    
    sinful_reel, sinful_rtp = create_balanced_sinful_reel()
    save_reel(sinful_reel, 'SINFUL.csv')
    
    demonic_reel, demonic_rtp = create_balanced_demonic_reel()
    save_reel(demonic_reel, 'DEMONIC.csv')
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"MILD RTP:    {mild_rtp*100:.2f}% (Target: 96.00%)")
    print(f"SINFUL RTP:  {sinful_rtp*100:.2f}% (Target: 95.50%)")
    print(f"DEMONIC RTP: {demonic_rtp*100:.2f}% (Target: 95.00%)")
    print("\nAll reels saved! Run 'make run GAME=plinko' to regenerate books.")

