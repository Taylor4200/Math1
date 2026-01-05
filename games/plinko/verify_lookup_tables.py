"""Verify RTP from actual lookup tables (what RGS uses)."""

import csv

def verify_lookup_table(mode):
    """Calculate RTP from lookup table."""
    lut_path = f"library/publish_files/lookUpTable_{mode}_0.csv"
    
    total_weight = 0
    weighted_wins = 0.0
    wins_less_than_bet = 0
    
    with open(lut_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3:
                try:
                    book_id = int(parts[0])
                    weight = int(parts[1])
                    win_cents = int(parts[2])
                    win_multiplier = win_cents / 100.0  # Convert cents to multiplier
                    
                    total_weight += weight
                    weighted_wins += weight * win_multiplier
                    
                    if win_multiplier < 1.0:
                        wins_less_than_bet += weight
                        
                except ValueError:
                    continue
    
    rtp = weighted_wins / total_weight if total_weight > 0 else 0
    prob_less_bet = wins_less_than_bet / total_weight if total_weight > 0 else 0
    house_edge = 1 - rtp
    
    print(f"\n{'='*70}")
    print(f"{mode.upper()} LOOKUP TABLE VERIFICATION")
    print(f"{'='*70}")
    print(f"Total weight:     {total_weight:,}")
    print(f"RTP:              {rtp:.6f} ({rtp*100:.4f}%)")
    print(f"House Edge:       {house_edge*100:.4f}%")
    print(f"Prob < Bet:       {prob_less_bet*100:.4f}%")
    print(f"{'='*70}")
    
    return rtp, house_edge

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*15 + "PLINKO LOOKUP TABLE VERIFICATION")
    print(" "*10 + "(What the RGS actually uses for gameplay)")
    print("="*70)
    
    results = {}
    for mode in ["mild", "sinful", "demonic"]:
        try:
            rtp, he = verify_lookup_table(mode)
            results[mode] = {"rtp": rtp, "house_edge": he}
        except FileNotFoundError:
            print(f"\nERROR: Lookup table for {mode} not found!")
    
    print(f"\n{'='*70}")
    print("HOUSE EDGE COMPARISON")
    print(f"{'='*70}")
    for i, mode in enumerate(["mild", "sinful", "demonic"]):
        if mode in results:
            he = results[mode]["house_edge"] * 100
            print(f"{mode.upper():8s}: {he:.4f}% house edge")
            if i > 0:
                prev_mode = ["mild", "sinful"][i-1]
                if prev_mode in results:
                    prev_he = results[prev_mode]["house_edge"] * 100
                    diff = he - prev_he
                    target_diff = 0.5
                    status = "PERFECT" if abs(diff - target_diff) < 0.1 else f"OFF BY {abs(diff - target_diff):.2f}%"
                    print(f"          +{diff:.4f}% from {prev_mode} ({status})")
    print(f"{'='*70}\n")







