"""ABSOLUTELY FINAL - Center-dominant distributions."""
import random

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

# Calculate exact sums
# MILD: 134,532 - 34,532 from bucket 8 = adjust to 47,468
mild = [1,20,35,120,250,850,1800,8000,82000,8000,1800,850,250,120,35,20,1]
mild_sum = sum(mild)
mild[8] = mild[8] - (mild_sum - 100000)

# SINFUL: 102,492 - 2,492 from bucket 8 = adjust to 80,508
sinful = [1,15,30,100,350,1000,3000,5000,83000,5000,3000,1000,350,100,30,15,1]
sinful_sum = sum(sinful)
sinful[8] = sinful[8] - (sinful_sum - 100000)

# DEMONIC: 100,644 - 644 from bucket 8 = adjust to 30,156
demonic = [1,1,20,50,150,500,3500,30700,30800,30700,3500,500,150,50,20,1,1]
demonic_sum = sum(demonic)
demonic[8] = demonic[8] - (demonic_sum - 100000)

print(f"MILD sum: {sum(mild)}")
print(f"SINFUL sum: {sum(sinful)}")
print(f"DEMONIC sum: {sum(demonic)}\n")

for mode, counts in [("mild", mild), ("sinful", sinful), ("demonic", demonic)]:
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
    
    status = "[PERFECT]" if err < 0.003 and prob_less < 0.80 else "[EXCELLENT]" if err < 0.01 and prob_less < 0.80 else ""
    print(f"{mode.upper()}: RTP {eff_rtp:.4f} (target {targets[mode]}, err {err:.4f}), Prob<Bet {prob_less:.3f} {status}")

print("\n[FINAL] Run: python games/plinko/run.py")



