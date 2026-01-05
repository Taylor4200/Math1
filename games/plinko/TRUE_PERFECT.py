"""TRUE PERFECT - Counts sum to EXACTLY 100k from start."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

# MILD: Counts summing to EXACTLY 100,000
mild_counts = [1,20,35,120,300,2500,7000,11000,58048,11000,7000,2500,300,120,35,20,1]

# SINFUL: Counts summing to EXACTLY 100,000  
sinful_counts = [1,15,30,100,800,1500,3500,10000,68108,10000,3500,1500,800,100,30,15,1]

# DEMONIC: Counts summing to EXACTLY 100,000
demonic_counts = [1,1,20,50,200,1500,8500,26300,26856,26300,8500,1500,200,50,20,1,1]

# Verify sums
assert sum(mild_counts) == 100000, f"MILD sum = {sum(mild_counts)}"
assert sum(sinful_counts) == 100000, f"SINFUL sum = {sum(sinful_counts)}"
assert sum(demonic_counts) == 100000, f"DEMONIC sum = {sum(demonic_counts)}"
print(f"All sums verified = 100,000\n")

for mode, counts in [("mild", mild_counts), ("sinful", sinful_counts), ("demonic", demonic_counts)]:
    strip = []
    for i, c in enumerate(counts):
        strip.extend([i] * c)
    
    if len(strip) != 100000:
        print(f"ERROR: {mode} strip length = {len(strip)}")
        continue
    
    random.shuffle(strip)
    
    wins = [M[mode][b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
    eff_rtp = base_rtp * (1 + respin)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
    err = abs(eff_rtp - targets[mode])
    
    status = "[PERFECT]" if err < 0.003 and prob_less < 0.80 else "[GOOD]" if err < 0.01 and prob_less < 0.80 else ""
    print(f"{mode.upper()}: RTP {eff_rtp:.4f} (err {err:.4f}), Prob<Bet {prob_less:.3f} {status}")

print("\n[RUN] python games/plinko/run.py")

