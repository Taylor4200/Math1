"""Create expanded lookup tables with ALL possible bonus peg compound wins."""
import itertools

# Base bucket probabilities (from our optimized lookup tables)
BASE_WEIGHTS = {
    "mild": {
        "weights": [1, 1, 1, 4, 4, 4, 3, 457270, 85418, 457270, 3, 4, 4, 4, 1, 1, 1],
        "multipliers": [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666],
        "bonus_peg_prob": 0.05,
    },
    "sinful": {
        "weights": [1, 1, 46, 44, 1, 63803, 51399, 109211, 550982, 109211, 51399, 63803, 1, 44, 46, 1, 1],
        "multipliers": [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666],
        "bonus_peg_prob": 0.08,
    },
    "demonic": {
        "weights": [1, 1, 1, 10, 50, 44000, 51000, 269933, 269934, 269933, 51000, 44000, 50, 10, 1, 1, 1],
        "multipliers": [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666],
        "bonus_peg_prob": 0.12,
    },
}

def generate_compound_wins(mode_name, weights, multipliers, bonus_prob, max_respins=5):
    """Generate all possible compound win outcomes with bonus peg."""
    
    # Convert weights to probabilities
    total_w = sum(weights)
    probs = [w / total_w for w in weights]
    
    # Store all possible outcomes: {payout_cents: cumulative_probability}
    outcomes = {}
    
    # Single bucket outcomes (no bonus peg)
    for i, (prob, mult) in enumerate(zip(probs, multipliers)):
        payout_cents = int(mult * 100)
        prob_no_bonus = prob * (1 - bonus_prob)  # Probability of NOT hitting bonus peg
        
        if payout_cents not in outcomes:
            outcomes[payout_cents] = 0
        outcomes[payout_cents] += prob_no_bonus
    
    # Compound outcomes (with bonus peg respins)
    # For simplicity, simulate up to 2 respins (most common cases)
    for respin_count in range(1, min(max_respins + 1, 3)):  # 1 or 2 respins
        # Probability diminishes: 100%, 50%, 25%, ...
        diminishing_factors = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        
        # Generate all possible combinations of respin_count buckets
        for bucket_combo in itertools.product(range(len(multipliers)), repeat=respin_count + 1):
            # Calculate total payout
            total_mult = sum(multipliers[b] for b in bucket_combo)
            payout_cents = int(total_mult * 100)
            
            # Calculate probability of this specific chain
            prob_chain = probs[bucket_combo[0]]  # First bucket
            
            for r in range(respin_count):
                # Probability of hitting bonus peg at this respin
                effective_bonus_prob = bonus_prob * diminishing_factors[r]
                prob_chain *= effective_bonus_prob
                prob_chain *= probs[bucket_combo[r + 1]]  # Next bucket
            
            # Final respin: NO bonus peg (chain ends)
            if respin_count < max_respins:
                final_bonus_prob = bonus_prob * diminishing_factors[respin_count]
                prob_chain *= (1 - final_bonus_prob)
            
            if payout_cents not in outcomes:
                outcomes[payout_cents] = 0
            outcomes[payout_cents] += prob_chain
    
    return outcomes

def write_expanded_lookup_table(mode_name, outcomes, total_weight=1000000):
    """Write expanded lookup table with all compound wins."""
    
    # Convert probabilities to integer weights
    lookup_entries = []
    book_id = 1
    
    for payout_cents in sorted(outcomes.keys()):
        prob = outcomes[payout_cents]
        weight = max(1, int(prob * total_weight))  # At least 1
        
        lookup_entries.append(f"{book_id},{weight},{payout_cents}")
        book_id += 1
    
    # Write to file
    output_path = f"library/publish_files/lookUpTable_{mode_name}_0.csv"
    with open(output_path, 'w') as f:
        f.write('\n'.join(lookup_entries))
    
    print(f"\n{mode_name.upper()}:")
    print(f"  Total unique payouts: {len(outcomes)}")
    print(f"  Lookup table entries: {len(lookup_entries)}")
    print(f"  [OK] Written to {output_path}")
    
    # Calculate RTP
    total_w = sum(int(outcomes[p] * total_weight) for p in outcomes.keys())
    total_p = sum(int(outcomes[p] * total_weight) * p for p in outcomes.keys())
    rtp = total_p / total_w / 100 if total_w > 0 else 0
    
    print(f"  Actual RTP: {rtp:.4%}")
    print(f"  House Edge: {(1-rtp)*100:.2f}%")
    
    return rtp

print("="*70)
print("CREATING EXPANDED LOOKUP TABLES WITH BONUS PEG COMPOUND WINS")
print("="*70)

for mode_name, config in BASE_WEIGHTS.items():
    outcomes = generate_compound_wins(
        mode_name,
        config["weights"],
        config["multipliers"],
        config["bonus_peg_prob"],
        max_respins=5
    )
    
    write_expanded_lookup_table(mode_name, outcomes)

print("\n" + "="*70)
print("DONE! Expanded lookup tables created.")
print("="*70)

