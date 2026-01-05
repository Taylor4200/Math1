"""Generate stats directly from reel CSVs."""
import json, math

M={"mild":[666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666],"sinful":[1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666],"demonic":[16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666]}
R={"mild":0.05,"sinful":0.08,"demonic":0.12}
s={}
for m in["mild","sinful","demonic"]:
    b=[int(l.strip())for l in open(f'games/plinko/reels/{m.upper()}.csv')]
    w=[M[m][i]for i in b]
    r=sum(w)/len(w)
    e=r*(1+R[m])
    p=sum(1 for x in w if x<1)/len(w)
    mx=max(w)
    hr=len(w)/sum(1 for x in w if x==mx)
    v=sum((x-r)**2 for x in w)/len(w)
    sd=math.sqrt(v)
    sw=sorted(w)
    md=sw[len(sw)//2]
    m2m=r/md if md>0 else 0
    sk=sum((x-r)**3 for x in w)/(len(w)*(sd**3))if sd>0 else 0
    ku=sum((x-r)**4 for x in w)/(len(w)*(sd**4))if sd>0 else 0
    s[m]={"num_events":len(set(b)),"weight_range":float(len(b)),"min_win":min(w),"max_win":mx,"min_diff":0.2,"average_win":r,"rtp":r,"std":sd,"var":v,"m2m":m2m,"hr_max":hr,"non_zero_hr":1.0,"prob_nil":0.0 if m!="demonic" else sum(1 for x in w if x==0)/len(w),"num_non_zero_payouts":len([x for x in w if x>0]),"prob_less_bet":p,"skew":sk,"excess_kurtosis":ku-3,"name":m}
    print(f"{m.upper()}: Base {r:.4f}, Eff {e:.4f}, Prob<Bet {p:.3f}")

with open("games/plinko/library/stats_summary.json",'w')as f:
    json.dump(s,f,indent=4)
print("\n[OK] stats_summary.json updated!")



