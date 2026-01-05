"""Nuclear option: Clear ALL caches and regenerate everything fresh."""
import os
import shutil
import subprocess
import time

print("="*70)
print("NUCLEAR REGENERATION - CLEARING ALL CACHES")
print("="*70)

# Delete ALL generated files
print("\n[1/7] Deleting all publish files...")
pub_dir = "library/publish_files"
for f in os.listdir(pub_dir):
    if f != "index.json":
        os.remove(os.path.join(pub_dir, f))
        print(f"  Deleted {f}")

print("\n[2/7] Deleting temp files...")
temp_dirs = ["library/lookup_tables", "library/books", "library/__pycache__", "__pycache__"]
for td in temp_dirs:
    if os.path.exists(td):
        for f in os.listdir(td):
            fp = os.path.join(td, f)
            if os.path.isfile(fp):
                try:
                    os.remove(fp)
                    print(f"  Deleted {fp}")
                except:
                    pass

print("\n[3/7] Running Python optimizers...")
subprocess.run(["python", "OPTIMIZE_WITH_BOTH_CONSTRAINTS.py"], check=True)
subprocess.run(["python", "SOLVE_DEMONIC_FINAL.py"], check=True)

print("\n[4/7] Creating reels from optimizers...")
subprocess.run(["python", "create_reels_from_lookup.py"], check=True)

print("\n[5/7] Waiting 2 seconds for file system...")
time.sleep(2)

print("\n[6/7] Generating books (fresh simulation)...")
# Directly call the game without imports to avoid caching
subprocess.run(["python", "run.py"], check=True)

print("\n[7/7] Final verification...")
subprocess.run(["python", "verify_final_setup.py"], check=True)
subprocess.run(["python", "check_md5_match.py"], check=True)

print(f"\n{'='*70}")
print("NUCLEAR REGENERATION COMPLETE")
print('='*70)







