"""Quick test to check RTPs after reel regeneration"""

from game_config import GameConfig
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.rgs_verification import execute_all_tests
import json

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTING RTPs WITH NEW REELS")
    print("=" * 70)
    
    config = GameConfig()
    
    # First copy any new LUTs
    import shutil
    for mode in ['base', 'Bonus', 'Super Bonus', 'Bonus Booster', 'Feature Spin', 'Super Feature Spin']:
        lut_src = f"library/lookup_tables/lookUpTable_{mode}.csv"
        lut_dst = f"library/publish_files/lookUpTable_{mode}_0.csv"
        if os.path.exists(lut_src):
            shutil.copy(lut_src, lut_dst)
            print(f"Copied LUT for {mode}")
    
    print("\nRunning verification...")
    execute_all_tests(config)
    
    # Read and display RTPs
    with open('library/stats_summary.json', 'r') as f:
        data = json.load(f)
    
    print("\n" + "=" * 70)
    print("FINAL RTPs:")
    print("=" * 70)
    
    modes = ['base', 'Bonus', 'Super Bonus', 'Bonus Booster', 'Feature Spin', 'Super Feature Spin']
    for mode in modes:
        rtp = data[mode]['rtp'] * 100
        avg_win = data[mode]['average_win']
        status = "✓" if 95 <= rtp <= 97 else "✗"
        print(f"{status} {mode:20s}: {rtp:7.2f}%  (avg win: {avg_win:8.2f})")
    
    print("=" * 70)





