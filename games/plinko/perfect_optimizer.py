"""Perfect Plinko Optimizer - Constraint-based mathematical solver for exact RTP/HR targeting."""

import numpy as np
from scipy.optimize import minimize, LinearConstraint, Bounds
from typing import List, Dict, Optional, Tuple
import json
from optimizer_config import OptimizerConfig
from weight_generator import WeightGenerator


class PlinkoOptimizer:
    """Mathematical optimizer for Plinko bucket distributions."""
    
    def __init__(self, mode: str, config: Optional[OptimizerConfig] = None,
                 custom_multipliers: Optional[List[float]] = None):
        """Initialize optimizer for a specific mode.
        
        Args:
            mode: One of 'mild', 'sinful', 'demonic'
            config: Optional custom configuration (uses default if None)
            custom_multipliers: Optional custom bucket multipliers (uses game config if None)
        """
        self.mode = mode.lower()
        self.config = config if config else OptimizerConfig()
        self.mode_config = self.config.get_config(self.mode)
        
        # Get bucket multipliers
        if custom_multipliers:
            self.multipliers = np.array(custom_multipliers)
        else:
            # Import game config to get multipliers
            from game_config import GameConfig
            game_config = GameConfig()
            self.multipliers = np.array(game_config.bucket_multipliers[self.mode])
        
        self.num_buckets = len(self.multipliers)
        self.solution = None
        self.optimization_result = None
    
    def solve(self, verbose: bool = True) -> Dict:
        """Solve for optimal bucket probabilities.
        
        Args:
            verbose: Print optimization progress
            
        Returns:
            Dictionary with solution and statistics
        """
        # Initial guess: smart distribution based on target RTP
        # Start by heavily weighting buckets close to target RTP
        target_rtp = self.mode_config["target_rtp"]
        
        # Calculate initial weights inversely proportional to distance from target
        distances = np.abs(self.multipliers - target_rtp)
        # Avoid division by zero
        weights = 1.0 / (distances + 0.1)
        # Normalize to probabilities
        x0 = weights / np.sum(weights)
        
        # Set up constraints
        constraints = self._build_constraints()
        
        # Set up bounds (all probabilities between min and 1)
        min_prob = self.mode_config.get("min_bucket_prob", 0.00001)
        bounds = Bounds(
            lb=np.full(self.num_buckets, min_prob),
            ub=np.ones(self.num_buckets)
        )
        
        # Objective function: minimize weighted distance from ideal distribution
        # This helps achieve scaling preferences
        def objective(x):
            # Primary: distance from target RTP
            rtp = np.sum(x * self.multipliers)
            target_rtp = self.mode_config["target_rtp"]
            rtp_penalty = 1e6 * (rtp - target_rtp) ** 2
            
            # Secondary: apply scaling preferences
            scaling_penalty = self._calculate_scaling_penalty(x)
            
            # Tertiary: encourage smooth distribution (avoid extreme spikes)
            smoothness_penalty = 0.01 * np.var(x)
            
            return rtp_penalty + scaling_penalty + smoothness_penalty
        
        # Run optimization
        if verbose:
            print(f"\n{'='*60}")
            print(f"Optimizing {self.mode.upper()} mode")
            print(f"{'='*60}")
            print(f"Target RTP: {self.mode_config['target_rtp']:.6f}")
            print(f"Target prob_less_bet: {self.mode_config['target_prob_less_bet']:.6f}")
            print(f"Bucket constraints: {self.mode_config.get('bucket_constraints', {})}")
            print(f"{'='*60}\n")
        
        # Try optimization with increased iterations and tolerance
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 5000, 'ftol': 1e-12, 'disp': False}
        )
        
        # If it didn't converge, try with trust-constr method
        if not result.success and verbose:
            print("  SLSQP didn't converge, trying trust-constr method...")
            result = minimize(
                objective,
                x0,
                method='trust-constr',
                bounds=bounds,
                constraints=[
                    {'type': 'eq', 'fun': c['fun']} for c in constraints
                ],
                options={'maxiter': 5000, 'verbose': 0}
            )
        
        if not result.success:
            print(f"WARNING: Optimization did not converge. Message: {result.message}")
        
        self.solution = result.x
        self.optimization_result = result
        
        # Calculate statistics
        stats = self._calculate_statistics(self.solution)
        
        if verbose:
            self._print_results(stats)
        
        return stats
    
    def _build_constraints(self) -> List:
        """Build constraint list for scipy optimizer."""
        constraints = []
        
        # Constraint 1: Probabilities must sum to 1
        constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(x) - 1.0
        })
        
        # Constraint 2: RTP must equal target
        target_rtp = self.mode_config["target_rtp"]
        constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(x * self.multipliers) - target_rtp
        })
        
        # Constraint 3: prob_less_bet must equal target
        target_plb = self.mode_config["target_prob_less_bet"]
        less_bet_mask = self.multipliers < 1.0
        constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(x[less_bet_mask]) - target_plb
        })
        
        # Constraint 4: Specific bucket hit rates
        bucket_constraints = self.mode_config.get("bucket_constraints", {})
        for bucket_idx, constraint in bucket_constraints.items():
            if "hr" in constraint:
                target_prob = 1.0 / constraint["hr"]
                constraints.append({
                    'type': 'eq',
                    'fun': lambda x, idx=bucket_idx, p=target_prob: x[idx] - p
                })
        
        return constraints
    
    def _calculate_scaling_penalty(self, probabilities: np.ndarray) -> float:
        """Calculate penalty based on scaling preferences."""
        penalty = 0.0
        scaling_prefs = self.mode_config.get("scaling_preferences", {})
        
        # Favor certain multiplier ranges
        for pref in scaling_prefs.get("favor", []):
            mult_range = pref["multiplier_range"]
            weight = pref["weight"]
            
            # Find buckets in this range
            mask = (self.multipliers >= mult_range[0]) & (self.multipliers <= mult_range[1])
            
            # Penalize if these buckets have low probability (we want to favor them)
            total_prob = np.sum(probabilities[mask])
            # Inverse penalty: lower probability = higher penalty
            penalty += (1.0 / (total_prob + 0.001)) * (1.0 / weight)
        
        # Punish certain multiplier ranges
        for pref in scaling_prefs.get("punish", []):
            mult_range = pref["multiplier_range"]
            weight = pref["weight"]
            
            # Find buckets in this range
            mask = (self.multipliers >= mult_range[0]) & (self.multipliers <= mult_range[1])
            
            # Penalize if these buckets have high probability (we want to punish them)
            total_prob = np.sum(probabilities[mask])
            # Direct penalty: higher probability = higher penalty
            penalty += total_prob * weight
        
        return penalty
    
    def _calculate_statistics(self, probabilities: np.ndarray) -> Dict:
        """Calculate comprehensive statistics from probability distribution."""
        rtp = float(np.sum(probabilities * self.multipliers))
        
        # Probability of winning less than bet
        prob_less_bet = float(np.sum(probabilities[self.multipliers < 1.0]))
        
        # Hit rates for each bucket
        hit_rates = {}
        for i, prob in enumerate(probabilities):
            hr = 1.0 / prob if prob > 0 else float('inf')
            hit_rates[int(i)] = float(hr)
        
        # Expected value and variance
        ev = rtp
        variance = float(np.sum(probabilities * (self.multipliers - ev) ** 2))
        std = float(np.sqrt(variance))
        
        # Mean to median (volatility measure)
        # For median, find cumulative probability
        cumsum = np.cumsum(probabilities)
        median_idx = np.searchsorted(cumsum, 0.5)
        median = float(self.multipliers[median_idx])
        m2m = float(ev / median if median > 0 else float('inf'))
        
        return {
            "mode": self.mode,
            "probabilities": [float(p) for p in probabilities],
            "multipliers": [float(m) for m in self.multipliers],
            "rtp": rtp,
            "target_rtp": float(self.mode_config["target_rtp"]),
            "rtp_error": float(abs(rtp - self.mode_config["target_rtp"])),
            "prob_less_bet": prob_less_bet,
            "target_prob_less_bet": float(self.mode_config["target_prob_less_bet"]),
            "plb_error": float(abs(prob_less_bet - self.mode_config["target_prob_less_bet"])),
            "hit_rates": hit_rates,
            "expected_value": ev,
            "variance": variance,
            "std": std,
            "median": median,
            "m2m": m2m,
            "optimization_success": bool(self.optimization_result.success if self.optimization_result else False),
        }
    
    def _print_results(self, stats: Dict):
        """Print optimization results in a readable format."""
        print(f"\n{'='*60}")
        print(f"OPTIMIZATION RESULTS - {self.mode.upper()} MODE")
        print(f"{'='*60}\n")
        
        print(f"RTP:")
        print(f"  Target:  {stats['target_rtp']:.6f}")
        print(f"  Actual:  {stats['rtp']:.6f}")
        print(f"  Error:   {stats['rtp_error']:.8f}")
        
        print(f"\nProb Less Bet:")
        print(f"  Target:  {stats['target_prob_less_bet']:.6f}")
        print(f"  Actual:  {stats['prob_less_bet']:.6f}")
        print(f"  Error:   {stats['plb_error']:.8f}")
        
        print(f"\nVolatility Metrics:")
        print(f"  Std Dev: {stats['std']:.4f}")
        print(f"  Variance: {stats['variance']:.4f}")
        print(f"  M2M Ratio: {stats['m2m']:.2f}")
        
        print(f"\nBucket Distribution:")
        print(f"  {'Bucket':<8} {'Mult':<10} {'Probability':<15} {'Hit Rate':<15}")
        print(f"  {'-'*50}")
        
        for i in range(len(stats['probabilities'])):
            prob = stats['probabilities'][i]
            mult = stats['multipliers'][i]
            hr = stats['hit_rates'][i]
            hr_str = f"1 in {hr:.0f}" if hr != float('inf') else "Never"
            print(f"  {i:<8} {mult:<10.2f} {prob:<15.8f} {hr_str:<15}")
        
        print(f"\n{'='*60}\n")
    
    def save_to_csv(self, output_path: str, total_weight: int = 1000000):
        """Save optimized distribution to CSV file.
        
        Args:
            output_path: Path to save CSV file
            total_weight: Total weight of distribution (default: 1,000,000 for precision)
        """
        if self.solution is None:
            raise ValueError("Must run solve() before saving to CSV")
        
        generator = WeightGenerator(total_weight=total_weight)
        
        # Convert probabilities to weights (no refinement - use optimizer result directly)
        weights = generator.probabilities_to_weights(
            self.solution,
            multipliers=self.multipliers,
            target_rtp=self.mode_config["target_rtp"]
        )
        
        generator.weights_to_csv(weights, output_path)
        
        print(f"✓ Saved optimized distribution to: {output_path}")
        
        # Verify
        verification = generator.verify_distribution(
            output_path, 
            self.solution, 
            self.multipliers.tolist()
        )
        
        print(f"  Total weight: {verification['total_weight']:,}")
        print(f"  RTP: {verification['actual_rtp']:.6f} (error: {verification['rtp_error']:.8f})")
        print(f"  Prob<Bet: {verification['actual_prob_less_bet']:.6f} (error: {verification['plb_error']:.8f})")
    
    def save_solution(self, output_path: str):
        """Save full solution to JSON file.
        
        Args:
            output_path: Path to save JSON file
        """
        if self.solution is None:
            raise ValueError("Must run solve() before saving solution")
        
        stats = self._calculate_statistics(self.solution)
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Saved solution to: {output_path}")

