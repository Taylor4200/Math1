import numpy as np
from scipy.optimize import minimize

mults = np.array([16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666])

# We need DEMONIC to have 4.85% house edge (0.35% from SINFUL's 4.50%)
# So target RTP = 100% - 4.85% = 95.15%
target_rtp = 0.9515

def obj(x):
    return np.sum(x**2)

cons = [
    {'type':'eq','fun':lambda x:np.sum(x)-1.0}, 
    {'type':'eq','fun':lambda x:np.sum(x*mults)-target_rtp}
]

res = minimize(obj, np.ones(17)/17, method='SLSQP', bounds=[(0.00001,1) for _ in range(17)], constraints=cons, options={'maxiter': 5000})

if res.success:
    plb = np.sum(res.x[mults<1.0])
    print(f'For RTP={target_rtp} (house edge=4.85%), achievable prob_less_bet={plb:.4f}')
    print(f'\nOptimal distribution:')
    for i, (m, p) in enumerate(zip(mults, res.x)):
        if p > 0.01:
            print(f'  Bucket {i} ({m}x): {p:.4f} (HR: 1 in {1/p:.0f})')
else:
    print(f'Optimization failed: {res.message}')


