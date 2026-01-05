"""Analyze actual RTPs in the reel CSV files."""

import numpy as np
from game_config import GameConfig

def analyze_reel_rtp(reel_file, mode_name):
    """Calculate RTP from a reel CSV file."""
    config = GameConfig()
    multipliers = config.bucket_multipliers[mode_name]
    
    # Read reel file
    reel_strip = config.reels[reel_file.upper()][0]
    
    # Count bucket occurrences
    bucket_counts = np.zeros(len(multipliers))
    for bucket in reel_strip:
        bucket_counts[int(bucket)] += 1
    
    # Calculate probabilities
    total = len(reel_strip)
    probabilities = bucket_counts / total
    
    # Calculate RTP
    rtp = np.sum(probabilities * np.array(multipliers))
    
    # Calculate prob_less_bet
    prob_less_bet = np.sum(probabilities[np.array(multipliers) < 1.0])
    
    print(f"\n{'='*70}")
    print(f"REEL ANALYSIS: {reel_file}.csv ({mode_name} mode)")
    print(f"{'='*70}")
    print(f"Total entries: {total:,}")
    print(f"Actual RTP: {rtp:.6f} ({(1-rtp)*100:.2f}% house edge)")
    print(f"Prob < Bet: {prob_less_bet:.6f} ({prob_less_bet*100:.2f}%)")
    print()
    print(f"{'Bucket':<8} {'Mult':<10} {'Count':<12} {'Probability':<15} {'Hit Rate':<15}")
    print("-" * 70)
    
    for i in range(len(multipliers)):
        count = int(bucket_counts[i])
        prob = probabilities[i]
        mult = multipliers[i]
        hr = 1.0 / prob if prob > 0 else float('inf')
        hr_str = f"1 in {hr:.0f}" if hr != float('inf') else "Never"
        print(f"{i:<8} {mult:<10.2f} {count:<12,} {prob:<15.8f} {hr_str:<15}")
    
    return rtp, prob_less_bet

if __name__ == "__main__":
    print("\n" + "="*70)
    print("REEL FILE RTP ANALYSIS")
    print("="*70)
    
    modes = [
        ("mild", "mild"),
        ("sinful", "sinful"),
        ("demonic", "demonic"),
    ]
    
    rtps = {}
    for reel_name, mode_name in modes:
        rtp, plb = analyze_reel_rtp(reel_name, mode_name)
        rtps[mode_name] = rtp
    
    print("\n" + "="*70)
    print("RTP SUMMARY")
    print("="*70)
    print(f"{'Mode':<12} {'RTP':<12} {'House Edge':<15}")
    print("-" * 70)
    for mode, rtp in rtps.items():
        print(f"{mode.upper():<12} {rtp:.6f}   {(1-rtp)*100:.2f}%")
    
    print()
    rtp_range = max(rtps.values()) - min(rtps.values())
    print(f"RTP Range: {rtp_range:.6f} ({rtp_range*100:.2f}%)")
    
    if rtp_range <= 0.005:
        print("✅ Within 0.5% margin!")
    else:
        print(f"❌ Exceeds 0.5% margin by {(rtp_range-0.005)*100:.2f}%")
    
    print("\n" + "="*70)
    print("These RTPs are what Hell's Storm modes will get (pure random sampling)")
    print("="*70 + "\n")











