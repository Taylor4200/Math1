"""Verify final RTPs from the lookup tables."""
import csv
import os

def calculate_rtp_from_lookup_table(lookup_path):
    """Calculate RTP from a lookup table CSV file."""
    total_weight = 0
    total_payout = 0
    
    with open(lookup_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            book_id, weight, payout_cents = row
            weight = int(weight)
            payout_cents = int(payout_cents)
            
            total_weight += weight
            total_payout += weight * payout_cents
    
    # payout_cents is in cents (100 = 1x bet)
    rtp = (total_payout / total_weight / 100) if total_weight > 0 else 0
    return rtp, total_weight, total_payout

# Get the directory of this script
script_dir = os.path.dirname(__file__)

modes = ["mild", "sinful", "demonic"]
target_rtps = {
    "mild": 0.9600,    # 4.00% house edge
    "sinful": 0.9550,  # 4.50% house edge
    "demonic": 0.9500, # 5.00% house edge
}

print("\n" + "="*70)
print("FINAL RTP VERIFICATION (WITH BONUS PEG)")
print("="*70)

for mode in modes:
    lookup_path = os.path.join(script_dir, "library", "publish_files", f"lookUpTable_{mode}_0.csv")
    
    if not os.path.exists(lookup_path):
        print(f"\n{mode.upper()}: [ERROR] Lookup table not found!")
        continue
    
    rtp, total_weight, total_payout = calculate_rtp_from_lookup_table(lookup_path)
    target = target_rtps[mode]
    error = abs(rtp - target)
    house_edge = (1 - rtp) * 100
    
    print(f"\n{mode.upper()}:")
    print(f"  Target RTP:      {target:.4%}")
    print(f"  Actual RTP:      {rtp:.4%}")
    print(f"  Error:           {error:.6%}")
    print(f"  House Edge:      {house_edge:.2f}%")
    print(f"  Total Weight:    {total_weight:,}")
    print(f"  Total Payout:    {total_payout:,} cents")
    
    if error < 0.0001:  # Within 0.01%
        print(f"  Status:          [PERFECT]")
    elif error < 0.01:  # Within 1%
        print(f"  Status:          [OK]")
    else:
        print(f"  Status:          [NEEDS ADJUSTMENT]")

print("\n" + "="*70)
print("House Edge Differences:")
print("="*70)

rtps = {}
for mode in modes:
    lookup_path = os.path.join(script_dir, "library", "publish_files", f"lookUpTable_{mode}_0.csv")
    if os.path.exists(lookup_path):
        rtp, _, _ = calculate_rtp_from_lookup_table(lookup_path)
        rtps[mode] = rtp

if len(rtps) == 3:
    mild_he = (1 - rtps["mild"]) * 100
    sinful_he = (1 - rtps["sinful"]) * 100
    demonic_he = (1 - rtps["demonic"]) * 100
    
    print(f"MILD House Edge:    {mild_he:.2f}%")
    print(f"SINFUL House Edge:  {sinful_he:.2f}%")
    print(f"DEMONIC House Edge: {demonic_he:.2f}%")
    print()
    print(f"SINFUL - MILD:      {sinful_he - mild_he:.2f}% (target: +0.50%)")
    print(f"DEMONIC - SINFUL:   {demonic_he - sinful_he:.2f}% (target: +0.50%)")
    print(f"DEMONIC - MILD:     {demonic_he - mild_he:.2f}% (target: +1.00%)")
    
    # Check if within 0.5% margins
    sinful_diff = abs((sinful_he - mild_he) - 0.50)
    demonic_diff = abs((demonic_he - sinful_he) - 0.50)
    
    if sinful_diff < 0.1 and demonic_diff < 0.1:
        print("\n[OK] House edge margins are within spec (<0.5% margin)")
    else:
        print("\n[WARNING] House edge margins may need adjustment")

print("="*70 + "\n")







