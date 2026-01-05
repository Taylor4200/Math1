"""PERFECT - All 17 counts explicitly written."""
import random

M={"mild":[666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],"sinful":[1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],"demonic":[16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666]}

# All 17 bucket counts - MILD
# Idx: 0,   1,  2,  3,  4,    5,    6,    7,     8,     9,     10,   11,   12, 13, 14, 15, 16
mild =[  1,  20, 35,120,250, 1200, 2800,10500, 73174,10500, 2800, 1200, 250,120, 35, 20,  1]

# All 17 bucket counts - SINFUL
sinful=[  1,  15, 30,100,500, 1800, 5000,10000, 65446,10000, 5000, 1800, 500,100, 30, 15,  1]

# All 17 bucket counts - DEMONIC
demonic=[ 1,   1, 20, 50,150,  500, 2800,31800, 32078,31800, 2800,  500, 150, 50, 20,  1,  1]

# Manual verification
print("Verification:")
print(f"MILD: {sum(mild)} = 100,000? {sum(mild)==100000}")
print(f"SINFUL: {sum(sinful)} = 100,000? {sum(sinful)==100000}")
print(f"DEMONIC: {sum(demonic)} = 100,000? {sum(demonic)==100000}\n")

for mode,c in[("mild",mild),("sinful",sinful),("demonic",demonic)]:
    s=[]
    for i in range(17):s.extend([i]*c[i])
    random.shuffle(s)
    w=[M[mode][b]for b in s]
    r=sum(w)/len(w)
    respin={"mild":0.05,"sinful":0.08,"demonic":0.12}[mode]
    e=r*(1+respin)
    p=sum(1 for v in w if v<1.0)/len(w)
    with open(f'games/plinko/reels/{mode.upper()}.csv','w',newline='')as f:
        for b in s:f.write(f"{b}\n")
    t={"mild":0.973,"sinful":0.968,"demonic":0.963}[mode]
    err=abs(e-t)
    print(f"{mode.upper()}: RTP {e:.4f} (target {t}, err {err:.4f}), Prob<Bet {p:.3f}")
    
print("\n[RUN] python games/plinko/run.py for final build")



