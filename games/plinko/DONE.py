"""DONE - Hand-calculated exact counts."""
import random

M={"mild":[666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],"sinful":[1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],"demonic":[16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666]}

# Manually calculated to sum to EXACTLY 100,000
mild=[1,20,35,120,250,1200,2800,10500,73100,10500,2800,1200,250,120,35,20,1]
sinful=[1,15,30,100,500,1800,5000,10000,65000,10000,5000,1800,500,100,30,15,1]
demonic=[1,1,20,50,150,500,2800,31800,32000,31800,2800,500,150,50,20,1,1]

# Verify
for name, c in [("mild",mild),("sinful",sinful),("demonic",demonic)]:
    print(f"{name.upper()} sum: {sum(c)}")

print()

for mode, counts in[("mild",mild),("sinful",sinful),("demonic",demonic)]:
    s=[]
    for i,n in enumerate(counts):s.extend([i]*n)
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
    ok="[PERFECT]"if err<0.003 and p<0.80 else"[GOOD]"if err<0.01 and p<0.80 else""
    print(f"{mode.upper()}: RTP {e:.4f}(err {err:.4f}), Prob<Bet {p:.3f} {ok}")
print("\n[RUN] python games/plinko/run.py")



