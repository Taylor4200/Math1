"""
Use the optimized lookup tables and regenerate all files to match.
This ensures RTP, prob_less_bet, and house edge margins are correct.
"""
import shutil
import os

print("="*70)
print("USING OPTIMIZED MATH")
print("="*70)

# Step 1: Copy optimized lookup tables to publish directory
print("\nStep 1: Copying optimized lookup tables to publish_files...")
for mode in ["mild", "sinful", "demonic"]:
    src = f"OPTIMIZED_lookUpTable_{mode}.csv"
    dst = f"library/publish_files/lookUpTable_{mode}_0.csv"
    
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"  [OK] Copied {mode}")
    else:
        print(f"  [ERROR] {src} not found!")

# Step 2: Regenerate reels from optimized lookup tables
print("\nStep 2: Regenerating reels from optimized lookup tables...")
import subprocess
result = subprocess.run(["python", "create_reels_from_lookup.py"], capture_output=True, text=True)
if result.returncode == 0:
    print("  [OK] Reels regenerated")
else:
    print(f"  [ERROR] {result.stderr}")

# Step 3: Regenerate books from corrected reels
print("\nStep 3: Regenerating books (this will take ~15 seconds)...")
print("  Run: python run.py")
print("\nAfter books are generated, the lookup tables in publish_files will have")
print("the OPTIMIZED weights (not weight=1), giving correct RTP calculations!")

print(f"\n{'='*70}")
print("READY TO REGENERATE BOOKS")
print('='*70)
print("\nNext: Run 'python run.py' to generate books from the optimized distribution")







