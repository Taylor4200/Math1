"""Convert optimized probabilities to weighted reel CSV files for Plinko."""

import json
import os
import random

REEL_LENGTH = 100000  # Total number of bucket indices in the reel

def create_weighted_reel_from_probabilities(probabilities, output_path):
    """
    Create a weighted reel CSV from probability array.
    
    Args:
        probabilities: List of 17 probabilities (one per bucket)
        output_path: Path to output CSV file
    """
    # Convert probabilities to bucket counts
    bucket_counts = []
    for prob in probabilities:
        # Handle negative probabilities (shouldn't happen but optimizer sometimes outputs them)
        prob = max(0, prob)
        count = round(prob * REEL_LENGTH)
        bucket_counts.append(count)
    
    # Ensure we have exactly REEL_LENGTH total (adjust for rounding errors)
    total_count = sum(bucket_counts)
    if total_count != REEL_LENGTH:
        # Add/subtract from most frequent bucket
        diff = REEL_LENGTH - total_count
        max_idx = bucket_counts.index(max(bucket_counts))
        bucket_counts[max_idx] += diff
    
    # Create reel strip by repeating each bucket index
    reel_strip = []
    for bucket_idx, count in enumerate(bucket_counts):
        reel_strip.extend([bucket_idx] * count)
    
    # Shuffle for randomness
    random.shuffle(reel_strip)
    
    # Write to CSV
    with open(output_path, 'w') as f:
        for bucket_idx in reel_strip:
            f.write(f"{bucket_idx}\n")
    
    print(f"[OK] Created weighted reel: {output_path} ({len(reel_strip):,} positions)")


def update_all_reels():
    """Update all reel CSV files from optimization results."""
    library_path = "library"
    reels_path = "reels"
    
    modes = ["mild", "sinful", "demonic"]
    
    for mode in modes:
        # Read optimization results
        opt_results_path = os.path.join(library_path, f"optimization_results_{mode}.json")
        
        try:
            with open(opt_results_path, 'r') as f:
                opt_data = json.load(f)
            
            probabilities = opt_data["probabilities"]
            
            # Create weighted reel CSV
            reel_csv_path = os.path.join(reels_path, f"{mode.upper()}.csv")
            create_weighted_reel_from_probabilities(probabilities, reel_csv_path)
            
        except FileNotFoundError:
            print(f"[WARN] {opt_results_path} not found for {mode}.")
        except KeyError as e:
            print(f"[ERROR] Missing key in {mode} optimization results: {e}")


if __name__ == "__main__":
    update_all_reels()



