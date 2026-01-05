"""Test that reels are loaded correctly."""
from game_config import GameConfig
from collections import Counter

config = GameConfig()

for mode_key in ["MILD", "SINFUL", "DEMONIC"]:
    reel = config.reels[mode_key][0]  # Column 0
    counts = Counter(reel)
    total = len(reel)
    
    print(f"\n{mode_key}:")
    print(f"  Total entries: {total}")
    print(f"  Unique buckets: {len(counts)}")
    print(f"  Distribution:")
    for bucket in sorted(counts.keys())[:10]:
        print(f"    Bucket {bucket}: {counts[bucket]} ({counts[bucket]/total*100:.2f}%)")







