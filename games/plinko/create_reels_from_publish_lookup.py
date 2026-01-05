"""Create reels from the publish_files lookup tables."""
import csv

# Bucket multipliers (for reverse mapping)
BUCKET_MULTS = {
    "mild": [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666],
    "sinful": [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666],
    "demonic": [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666],
}

# Payout to bucket mapping
PAYOUT_TO_BUCKET = {}
for mode, mults in BUCKET_MULTS.items():
    PAYOUT_TO_BUCKET[mode] = {}
    for bucket, mult in enumerate(mults):
        payout_cents = int(mult * 100)
        if payout_cents not in PAYOUT_TO_BUCKET[mode]:
            PAYOUT_TO_BUCKET[mode][payout_cents] = []
        PAYOUT_TO_BUCKET[mode][payout_cents].append(bucket)

for mode in ["mild", "sinful", "demonic"]:
    # Read lookup table
    lookup_file = f"library/publish_files/lookUpTable_{mode}_0.csv"
    reel_buckets = []
    
    with open(lookup_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                _, _, payout = row
                payout_cents = int(payout)
                
                # Get bucket index for this payout
                possible_buckets = PAYOUT_TO_BUCKET[mode].get(payout_cents, [])
                if possible_buckets:
                    # Use first bucket for consistency
                    bucket = possible_buckets[0]
                    reel_buckets.append(bucket)
    
    # Write reel
    reel_file = f"reels/{mode.upper()}.csv"
    with open(reel_file, 'w', newline='') as f:
        for bucket in reel_buckets:
            f.write(f"{bucket}\n")
    
    print(f"{mode.upper()}: Created reel with {len(reel_buckets)} entries")

print("\n[OK] Reels created from lookup tables!")
print("Now run: python run.py")







