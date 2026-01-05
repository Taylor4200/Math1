"""Solve for EXACT DEMONIC weights using direct calculation."""

# Target: 95.0% base RTP (bonus peg will add extra RTP on top)
# Total weight: 1,000,000
# Target payout: 95,000,000 cents

target_payout_cents = 95000000
total_weight = 1000000

# DEMONIC multipliers (in cents):
# [1666600, 250000, 60000, 15000, 4000, 800, 200, 0, 0, 0, 200, 800, 4000, 15000, 60000, 250000, 1666600]

# Strategy: Start with all weight on 0x, then add just enough 2x/8x to hit target

# Trial and error to find right balance
print("Searching for perfect weight distribution...")
print()

best_solution = None
best_error = float('inf')

# Try different distributions
for weight_2x in range(50000, 300000, 1000):  # Weight per 2x bucket (6, 10) - WIDER RANGE
    for weight_8x in range(10000, 100000, 500):  # Weight per 8x bucket (5, 11) - WIDER RANGE
        # Remaining weight goes to 0x buckets
        used_weight = (weight_2x * 2) + (weight_8x * 2) + 200  # +200 for rare buckets
        if used_weight > total_weight:
            continue
        
        weight_0x_total = total_weight - used_weight
        weight_0x_per = weight_0x_total // 3
        
        # Remaining goes to bucket 8 (center)
        weight_0x_center = weight_0x_total - (weight_0x_per * 2)
        
        # Calculate payout (include ALL buckets!)
        rare_payout = (1*1666600 + 1*250000 + 1*60000 + 10*15000 + 50*4000) * 2  # Both sides
        payout_2x = weight_2x * 2 * 200  # 2 buckets * 200 cents each
        payout_8x = weight_8x * 2 * 800  # 2 buckets * 800 cents each
        payout = rare_payout + payout_2x + payout_8x
        rtp = payout / total_weight / 100
        
        error = abs(rtp - 0.95)
        
        if error < best_error:
            best_error = error
            best_solution = {
                "weight_2x": weight_2x,
                "weight_8x": weight_8x,
                "weight_0x_side": weight_0x_per,
                "weight_0x_center": weight_0x_center,
                "rtp": rtp,
                "he": (1 - rtp) * 100,
                "payout": payout,
            }

if best_solution:
    print("BEST SOLUTION FOUND!")
    print(f"  2x buckets (6,10): {best_solution['weight_2x']:,} each")
    print(f"  8x buckets (5,11): {best_solution['weight_8x']:,} each")
    print(f"  0x buckets (7,9): {best_solution['weight_0x_side']:,} each")
    print(f"  0x bucket (8): {best_solution['weight_0x_center']:,}")
    print(f"  RTP: {best_solution['rtp']:.4%}")
    print(f"  House Edge: {best_solution['he']:.2f}%")
    print(f"  Error: {best_error:.6%}")
    print()
    
    # Create final weights
    final_weights = [
        1,  # 0: 16666x
        1,  # 1: 2500x
        1,  # 2: 600x
        10,  # 3: 150x
        50,  # 4: 40x
        best_solution['weight_8x'],  # 5: 8x
        best_solution['weight_2x'],  # 6: 2x
        best_solution['weight_0x_side'],  # 7: 0x
        best_solution['weight_0x_center'],  # 8: 0x
        best_solution['weight_0x_side'],  # 9: 0x
        best_solution['weight_2x'],  # 10: 2x
        best_solution['weight_8x'],  # 11: 8x
        50,  # 12: 40x
        10,  # 13: 150x
        1,  # 14: 600x
        1,  # 15: 2500x
        1,  # 16: 16666x
    ]
    
    # Verify calculation
    mults_cents = [1666600, 250000, 60000, 15000, 4000, 800, 200, 0, 0, 0, 200, 800, 4000, 15000, 60000, 250000, 1666600]
    actual_total_weight = sum(final_weights)
    actual_total_payout = sum(w * m for w, m in zip(final_weights, mults_cents))
    actual_rtp = actual_total_payout / actual_total_weight / 100
    actual_he = (1 - actual_rtp) * 100
    
    print("VERIFICATION OF ACTUAL WEIGHTS:")
    print(f"  Total weight: {actual_total_weight:,}")
    print(f"  Total payout: {actual_total_payout:,} cents")
    print(f"  Actual RTP: {actual_rtp:.4%}")
    print(f"  Actual HE: {actual_he:.2f}%")
    print()
    
    # Write to file
    lines = []
    for i, (w, m) in enumerate(zip(final_weights, mults_cents)):
        book_id = i + 1
        lines.append(f"{book_id},{w},{m}")
    
    # Write in Rust optimizer output format (17 rows with proper weights)
    output_path = "library/optimization_files/demonic_0_1.csv"
    with open(output_path, 'w') as f:
        f.write("Name,Optimized_demonic\n")
        f.write("Score,0.0\n")
        f.write("LockedUpRTP,\n")
        f.write(f"Rtp,{rtp}\n")
        f.write("Win Ranges\n")
        f.write("Distribution\n")
        for line in lines:
            parts = line.split(',')
            # Convert cents to dollars for optimizer format
            payout_dollars = int(parts[2]) / 100.0
            f.write(f"{parts[0]},{parts[1]},{payout_dollars}\n")
    
    print(f"[OK] DEMONIC lookup table written to {output_path} (17 rows, weighted)!")
else:
    print("No solution found!")

