"""FINAL ANSWER - Drastically increased center buckets."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

# DRASTICALLY increase center buckets
mild_counts = [1,20,35,120,250,800,1800,8000,82000,8000,1800,800,250,120,35,20,1]  # 82% in center!
sinful_counts = [1,15,30,100,350,1000,3000,5000,83000,5000,3000,1000,350,100,30,15,1]  # 83% in center!
demonic_counts = [1,1,20,50,150,500,3500,30700,30800,30700,3500,500,150,50,20,1,1]  # 92% in 0x!

assert sum(mild_counts) == 100000
assert sum(sinful_counts) == 100000
assert sum(demonic_counts) == 100000

for mode, counts in [("mild", mild_counts), ("sinful", sinful_counts), ("demonic", demonic_counts)]:
    strip = []
    for i, c in enumerate(counts):
        strip.extend([i] * c)
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
    
    print(f"{mode.upper()}: RTP {eff_rtp:.4f} (err {err:.4f}), Prob<Bet {prob_less:.3f}")

print("\n[RUN] python games/plinko/run.py")



