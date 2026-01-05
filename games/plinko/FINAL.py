"""FINAL PRECISION TUNED DISTRIBUTIONS."""
import random

M={"mild":[666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],"sinful":[1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],"demonic":[16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666]}

# FINAL PRECISION TUNED:
# MILD: Need slightly more 1x to hit 97.3% from 94.1%
mild=[1,22,37,130,300,1000,2700,13000,70000,13000,2700,1000,300,130,37,22,1]

# SINFUL: 96.14% is very close to 96.8%! Add tiny bit more 2x-4x
sinful=[1,15,30,100,400,1300,5000,12000,53000,12000,5000,1300,400,100,30,15,1]

# DEMONIC: Need much more 0x weight to lower RTP from 183% to 96%!
demonic=[1,1,20,50,150,450,4000,29000,29100,29000,4000,450,150,50,20,1,1]

for mode,w in[("mild",mild),("sinful",sinful),("demonic",demonic)]:
    s=[]
    for i,wt in enumerate(w):
        s.extend([i]*int(wt/sum(w)*100000))
    while len(s)<100000:s.append(8)
    while len(s)>100000:s.pop()
    random.shuffle(s)
    wins=[M[mode][b]for b in s]
    r=sum(wins)/len(wins)
    respin={"mild":0.05,"sinful":0.08,"demonic":0.12}[mode]
    eff=r*(1+respin)
    pb=sum(1 for v in wins if v<1.0)/len(wins)
    with open(f'games/plinko/reels/{mode.upper()}.csv','w',newline='')as f:
        for b in s:f.write(f"{b}\n")
    t={"mild":0.973,"sinful":0.968,"demonic":0.963}[mode]
    e=abs(eff-t)
    print(f"{mode.upper()}: RTP {eff:.4f}(err {e:.4f}), Prob<Bet {pb:.3f} {'[OK]'if e<0.01 and pb<0.80 else''}")
print("\n[RUN] python games/plinko/run.py")



