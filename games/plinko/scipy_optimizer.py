"""Use scipy to solve constrained optimization problem."""
try:
    from scipy.optimize import minimize
    import numpy as np
    import random
    
    M = {
        "mild": np.array([666,150,60,20,8,4,2,1,0.5,1,2,4,8,20,60,150,666]),
        "sinful": np.array([1666,400,120,40,12,4,2,0.5,0.2,0.5,2,4,12,40,120,400,1666]),
        "demonic": np.array([16666,2500,600,150,40,8,2,0,0,0,2,8,40,150,600,2500,16666]),
    }
    
    def optimize_scipy(mode, base_rtp_target, max_prob_less):
        """Use scipy to find optimal probabilities."""
        mults = M[mode]
        
        def objective(probs):
            """Minimize error from target RTP."""
            rtp = np.dot(probs, mults)
            prob_less = np.sum(probs[mults < 1.0])
            
            rtp_error = (rtp - base_rtp_target) ** 2
            prob_error = max(0, prob_less - max_prob_less) ** 2 * 10
            
            return rtp_error + prob_error
        
        def constraint_sum(probs):
            """Probabilities must sum to 1."""
            return np.sum(probs) - 1.0
        
        # Initial guess - uniform
        x0 = np.ones(17) / 17
        
        # Bounds - all probs between 0.00001 and 1
        bounds = [(0.00001, 1.0) for _ in range(17)]
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': constraint_sum}]
        
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        return result.x
    
    print("SCIPY OPTIMIZER")
    print("="*70)
    
    base_rtps = {"mild": 0.9267, "sinful": 0.8963, "demonic": 0.8598}
    
    for mode, base_rtp in base_rtps.items():
        probs = optimize_scipy(mode, base_rtp, 0.79)
        
        # Convert to counts
        counts = (probs * 100000).astype(int)
        diff = 100000 - counts.sum()
        counts[8] += diff
        
        # Create strip
        strip = []
        for i, count in enumerate(counts):
            strip.extend([i] * count)
        random.shuffle(strip)
        
        # Stats
        wins = [M[mode][i] for i in strip]
        base_rtp = sum(wins) / len(wins)
        respin = {"mild": 0.05, "sinful": 0.08, "demonic": 0.12}[mode]
        eff_rtp = base_rtp * (1 + respin)
        prob_less = sum(1 for w in wins if w < 1.0) / len(wins)
        
        # Write
        with open(f'games/plinko/reels/{mode.upper()}.csv', 'w', newline='') as f:
            for b in strip:
                f.write(f"{b}\n")
        
        targets = {"mild": 0.973, "sinful": 0.968, "demonic": 0.963}
        err = abs(eff_rtp - targets[mode])
        
        print(f"{mode.upper()}: RTP {eff_rtp:.4f} (err {err:.4f}), Prob<Bet {prob_less:.3f}")
        print(f"  Counts: {counts}")
    
    print("\n[OK] Scipy optimization complete!")
    print("Run: python games/plinko/run.py")

except ImportError:
    print("scipy not installed. Install with: pip install scipy")



