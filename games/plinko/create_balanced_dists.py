"""Create balanced, achievable distributions for Plinko."""
import random

M = {
    "mild": [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666],
    "sinful": [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666],
    "demonic": [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666],
}

print("Creating balanced Plinko distributions...\n")

# MILD - Can hit both targets easily
mild = [1,22,37,130,300,950,2300,8500,74000,8500,2300,950,300,130,37,22,1]

# SINFUL - Can hit both targets
sinful = [1,15,30,100,350,1100,4200,9500,68000,9500,4200,1100,350,100,30,15,1]

# DEMONIC - CANNOT hit both targets simultaneously!
# With 3x 0x buckets, to get 96.3% RTP requires ~86% in 0x = 86% prob_less_bet
# Best compromise: Accept prob_less_bet ~85%
demonic = [1,1,16,35,100,400,1600,28300,28300,28300,1600,400,100,35,16,1,1]

for mode, weights in [("mild", mild), ("sinful", sinful), ("demonic", demonic)]:
    mults = M[mode]
    total = sum(weights)
    strip = []
    for i, w in enumerate(weights):
        count = int((w / total) * 100000)
        strip.extend([i] * count)
    while len(strip) < 100000:
        strip.append(8)
    while len(strip) > 100000:
        strip.pop()
    random.shuffle(strip)
    
    wins = [mults[b] for b in strip]
    base_rtp = sum(wins) / len(wins)
    respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
    eff = base_rtp * (1 + respin)
    prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
    
    with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
        for b in strip:
            f.write(f"{b}\n")
    
    targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
    print(f"{mode.upper()}: Eff RTP {eff:.4f} (target {targets[mode]}), Prob<Bet {prob_less:.3f}")

print("\n[NOTE] DEMONIC has 3x 0x buckets - cannot achieve prob_less_bet < 0.80 at 96.3% RTP")
print("[INFO] To fix: Either accept higher prob_less_bet OR change DEMONIC bucket multipliers")
print("\n[OK] Balanced distributions created!")



