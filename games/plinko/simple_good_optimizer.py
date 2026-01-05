"""Simple Plinko Optimizer - Focuses on GOOD gameplay with natural hit rate gradients."""

import numpy as np
from scipy.optimize import minimize
from typing import List, Dict
from weight_generator import WeightGenerator
import json


class SimpleGoodOptimizer:
    """Simple optimizer that creates GOOD, playable distributions."""
    
    def __init__(self, mode: str):
        """Initialize optimizer.
        
        Args:
            mode: One of 'mild', 'sinful', 'demonic'
        """
        self.mode = mode.lower()
        
        # Import game config for multipliers
        from game_config import GameConfig
        game_config = GameConfig()
        self.multipliers = np.array(game_config.bucket_multipliers[self.mode])
        self.num_buckets = len(self.multipliers)
        
        # Set targets based on mode
        if self.mode == "mild":
            self.target_rtp = 0.9600  # 4.00% house edge
            self.max_win_hr = 50000   # 666x: 1 in 50k
        elif self.mode == "sinful":
            self.target_rtp = 0.9565  # 4.35% house edge
            self.max_win_hr = 100000  # 1666x: 1 in 100k
        elif self.mode == "demonic":
            self.target_rtp = 0.9515  # 4.85% house edge
            self.max_win_hr = 500000  # 16666x: 1 in 500k
        
        self.solution = None
    
    def solve(self, verbose: bool = True) -> Dict:
        """Solve for good distribution.
        
        Strategy:
        - Only constrain: RTP and max win HR
        - Let prob_less_bet be natural result
        - Use penalty function to create gradients (higher mult = lower probability)
        """
        # Initial guess - exponential decay from center
        x0 = np.ones(self.num_buckets) / self.num_buckets
        
        # Simple constraints: RTP + sum to 1 + max win HRs
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'eq', 'fun': lambda x: np.sum(x * self.multipliers) - self.target_rtp},
            {'type': 'eq', 'fun': lambda x: x[0] - (1.0 / self.max_win_hr)},  # Bucket 0 HR
            {'type': 'eq', 'fun': lambda x: x[16] - (1.0 / self.max_win_hr)},  # Bucket 16 HR
        ]
        
        bounds = [(0.0001, 1.0) for _ in range(self.num_buckets)]
        
        # Objective: Create natural gradient (penalize high multipliers having high probability)
        def objective(x):
            penalty = 0.0
            
            # Penalize high multipliers having high probability (creates gradient)
            for i, mult in enumerate(self.multipliers):
                if mult > 10:  # For multipliers > 10x
                    # Higher multiplier = should have lower probability
                    penalty += x[i] * mult * 0.01
                elif mult >= 2:  # For 2-10x
                    # Should be common but not too common
                    penalty += x[i] * mult * 0.001
            
            # Encourage smooth distribution (avoid spikes)
            penalty += 0.001 * np.var(x)
            
            return penalty
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Optimizing {self.mode.upper()} mode (Simple Good Optimizer)")
            print(f"{'='*60}")
            print(f"Target RTP: {self.target_rtp:.4f}")
            print(f"Max win HR: 1 in {self.max_win_hr:,}")
            print(f"{'='*60}\n")
        
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 5000, 'ftol': 1e-12}
        )
        
        if not result.success:
            if verbose:
                print(f"  SLSQP didn't converge, trying trust-constr...")
            result = minimize(
                objective,
                x0,
                method='trust-constr',
                bounds=bounds,
                constraints=[{'type': 'eq', 'fun': c['fun']} for c in constraints],
                options={'maxiter': 5000}
            )
        
        self.solution = result.x
        
        # Calculate stats
        stats = self._calculate_stats()
        
        if verbose:
            self._print_results(stats)
        
        return stats
    
    def _calculate_stats(self) -> Dict:
        """Calculate statistics."""
        rtp = float(np.sum(self.solution * self.multipliers))
        prob_less_bet = float(np.sum(self.solution[self.multipliers < 1.0]))
        
        hit_rates = {}
        for i, prob in enumerate(self.solution):
            hit_rates[int(i)] = float(1.0 / prob if prob > 0 else float('inf'))
        
        return {
            "mode": self.mode,
            "rtp": rtp,
            "target_rtp": self.target_rtp,
            "prob_less_bet": prob_less_bet,
            "hit_rates": hit_rates,
            "probabilities": [float(p) for p in self.solution],
            "multipliers": [float(m) for m in self.multipliers],
        }
    
    def _print_results(self, stats: Dict):
        """Print results."""
        print(f"\n{'='*60}")
        print(f"RESULTS - {self.mode.upper()} MODE")
        print(f"{'='*60}\n")
        print(f"RTP: {stats['rtp']:.4f} (target: {stats['target_rtp']:.4f})")
        print(f"prob_less_bet: {stats['prob_less_bet']:.4f}")
        print(f"House Edge: {(1-stats['rtp'])*100:.2f}%")
        
        print(f"\n{'Bucket':<8} {'Mult':<10} {'Probability':<15} {'Hit Rate':<20}")
        print("-" * 55)
        for i in range(self.num_buckets):
            mult = self.multipliers[i]
            prob = self.solution[i]
            hr = stats['hit_rates'][i]
            hr_str = f"1 in {hr:.0f}" if hr != float('inf') else "Never"
            print(f"{i:<8} {mult:<10.2f} {prob:<15.6f} {hr_str:<20}")
        
        print(f"\n{'='*60}\n")
    
    def save_to_csv(self, output_path: str, total_weight: int = 1000000):
        """Save to CSV."""
        if self.solution is None:
            raise ValueError("Must run solve() first")
        
        generator = WeightGenerator(total_weight=total_weight)
        weights = generator.probabilities_to_weights(
            self.solution,
            multipliers=self.multipliers,
            target_rtp=self.target_rtp
        )
        generator.weights_to_csv(weights, output_path)
        
        print(f"✓ Saved to: {output_path}")
        
        # Verify
        verification = generator.verify_distribution(output_path, self.solution, self.multipliers.tolist())
        print(f"  RTP: {verification['actual_rtp']:.6f} (error: {verification['rtp_error']:.6f})")
        print(f"  prob_less_bet: {verification['actual_prob_less_bet']:.6f}")
    
    def save_solution(self, output_path: str):
        """Save solution to JSON."""
        if self.solution is None:
            raise ValueError("Must run solve() first")
        
        stats = self._calculate_stats()
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Saved solution to: {output_path}")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "mild"
    
    opt = SimpleGoodOptimizer(mode)
    stats = opt.solve()
    opt.save_to_csv(f"reels/{mode.upper()}.csv")
    opt.save_solution(f"library/simple_results_{mode}.json")


