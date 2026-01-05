"""Create final correct lookup tables with optimized distribution."""
import random
import csv

# Optimized weights from OPTIMIZE_WITH_BOTH_CONSTRAINTS.py
MILD_WEIGHTS = [1, 1, 1, 4, 4, 4, 3, 457270, 85418, 457270, 3, 4, 4, 4, 1, 1, 1]
MILD_MULTS = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]

SINFUL_WEIGHTS = [1, 1, 46, 44, 1, 63803, 51399, 109211, 550982, 109211, 51399, 63803, 1, 44, 46, 1, 1]
SINFUL_MULTS = [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]

DEMONIC_WEIGHTS = [1, 1, 1, 10, 50, 44000, 51000, 269933, 269934, 269933, 51000, 44000, 50, 10, 1, 1, 1]
DEMONIC_MULTS = [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

def create_lookup(mode, weights, mults):
    """Create 100K-row lookup with correct optimized distribution."""
    # Expand based on weights
    payouts_cents = []
    for weight, mult in zip(weights, mults):
        payout_cents = int(mult * 100)
        for _ in range(weight):
            payouts_cents.append(payout_cents)
    
    # Shuffle
    random.seed(42)
    random.shuffle(payouts_cents)
    
    # Limit to 100K
    payouts_cents = payouts_cents[:100000]
    
    # Write
    output = f"library/publish_files/lookUpTable_{mode}_0.csv"
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        for i, payout in enumerate(payouts_cents):
            writer.writerow([i+1, 1, payout])
    
    # Calculate RTP
    avg_payout = sum(payouts_cents) / len(payouts_cents)
    rtp = avg_payout / 100  # Bet cost is 100 cents
    
    print(f"{mode.upper()}:")
    print(f"  Created {len(payouts_cents)} rows")
    print(f"  RTP: {rtp:.2%}")
    return payouts_cents

print("="*70)
print("CREATING FINAL CORRECT LOOKUP TABLES")
print("="*70)
print()

mild_payouts = create_lookup("mild", MILD_WEIGHTS, MILD_MULTS)
sinful_payouts = create_lookup("sinful", SINFUL_WEIGHTS, SINFUL_MULTS)
demonic_payouts = create_lookup("demonic", DEMONIC_WEIGHTS, DEMONIC_MULTS)

print(f"\n{'='*70}")
print("LOOKUPS CREATED - Now create books matching this distribution!")
print('='*70)







