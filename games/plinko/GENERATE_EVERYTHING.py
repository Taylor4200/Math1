"""Master script to generate ALL Plinko files in the correct order."""
import os
import subprocess
import shutil

print("="*70)
print("PLINKO COMPLETE REGENERATION")
print("="*70)

# Step 1: Clean publish_files
print("\nStep 1: Cleaning publish_files...")
publish_dir = "library/publish_files"
for file in os.listdir(publish_dir):
    if file.endswith('.csv') or file.endswith('.zst'):
        os.remove(os.path.join(publish_dir, file))
        print(f"  Deleted {file}")

# Step 2: Run optimizers
print("\nStep 2: Running Python optimizers...")
subprocess.run(["python", "OPTIMIZE_WITH_BOTH_CONSTRAINTS.py"], check=True)
subprocess.run(["python", "SOLVE_DEMONIC_FINAL.py"], check=True)

# Step 3: Generate reels from optimizers
print("\nStep 3: Generating reels from optimizers...")
subprocess.run(["python", "create_reels_from_lookup.py"], check=True)

# Step 4: Generate books from reels
print("\nStep 4: Generating books (this takes ~15 seconds)...")
subprocess.run(["python", "run.py"], check=True)

# Step 5: Verify
print("\nStep 5: Verifying...")
subprocess.run(["python", "check_md5_match.py"], check=True)
subprocess.run(["python", "verify_final_setup.py"], check=True)

print(f"\n{'='*70}")
print("COMPLETE!")
print('='*70)







