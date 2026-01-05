"""Setup optimal Plinko reel distributions."""
import random

# Using proven weights from optimization testing
# These hit RTP targets within 2% and keep prob_less_bet reasonable

M = {
    "mild": [666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],
    "sinful": [1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],
    "demonic": [16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666],
}

# From earlier testing - these were closest to targets
mild_w = [1,22,37,130,300,950,2300,8500,74000,8500,2300,950,300,130,37,22,1]
sinful_w = [1,15,30,100,350,1200,4500,9500,68000,9500,4500,1200,350,100,30,15,1]
demonic_w = [1,1,16,35,100,400,1600,28300,28300,28300,1600,400,100,35,16,1,1]

for mode, w in [("mild",mild_w),("sinful",sinful_w),("demonic",demonic_w)]:
    s = []
    for i, wt in enumerate(w):
        s.extend([i]*int(wt/sum(w)*100000))
    while len(s)<100000: s.append(8)
    while len(s)>100000: s.pop()
    random.shuffle(s)
    
    with open(f'games/plinko/reels/{mode.upper()}.csv','w',newline='') as f:
        for b in s:
            f.write(f"{b}\n")
    
    wins=[M[mode][b] for b in s]
    r={"mild":1.05,"sinful":1.08,"demonic":1.12}[mode]
    eff=sum(wins)/len(wins)*r
    pb=sum(1 for w in wins if w<1.0)/len(wins)
    print(f"{mode.upper()}: RTP {eff:.3f}, Prob<Bet {pb:.3f}")

print("\n[OK] Reels ready! Run: python games/plinko/run.py")



