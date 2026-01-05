"""Verify prob_less_bet is under 0.8 for all modes."""
import csv

modes = ["mild", "sinful", "demonic"]

print("="*70)
print("PROB_LESS_BET VERIFICATION")
print("="*70)

for mode in modes:
    lookup_path = f"library/publish_files/lookUpTable_{mode}_0.csv"
    
    total_weight = 0
    plb_weight = 0
    
    with open(lookup_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            book_id, weight, payout_cents = row
            weight = int(weight)
            payout_cents = int(payout_cents)
            multiplier = payout_cents / 100  # Convert cents to multiplier
            
            total_weight += weight
            if multiplier < 1.0:
                plb_weight += weight
    
    plb = plb_weight / total_weight if total_weight > 0 else 0
    
    print(f"\n{mode.upper()}:")
    print(f"  Prob_less_bet: {plb:.4%}")
    print(f"  Status: {'[OK]' if plb < 0.8 else '[OVER LIMIT]'}")

print("\n" + "="*70)
print("Done!")
print("="*70)







