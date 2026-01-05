import numpy as np
from scipy.optimize import minimize

mults = np.array([16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666])
target_rtp = 0.953

def obj(x):
    return np.sum(x**2)

cons = [
    {'type':'eq','fun':lambda x:np.sum(x)-1.0}, 
    {'type':'eq','fun':lambda x:np.sum(x*mults)-target_rtp}
]

res = minimize(obj, np.ones(17)/17, method='SLSQP', bounds=[(0.00001,1) for _ in range(17)], constraints=cons)
plb = np.sum(res.x[mults<1.0])
print(f'For RTP={target_rtp}, achievable prob_less_bet={plb:.4f}')
print(f'Distribution:')
for i, (m, p) in enumerate(zip(mults, res.x)):
    if p > 0.001:
        print(f'  Bucket {i} ({m}x): {p:.4f} ({1/p:.0f} HR)')


