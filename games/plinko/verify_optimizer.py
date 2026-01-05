"""Verification and validation tools for Plinko optimizer."""

import numpy as np
from typing import List, Dict, Optional
import csv
from collections import Counter


class OptimizerVerifier:
    """Verify and validate optimizer results."""
    
    def __init__(self, csv_path: str, multipliers: List[float]):
        """Initialize verifier.
        
        Args:
            csv_path: Path to bucket distribution CSV
            multipliers: List of bucket multipliers
        """
        self.csv_path = csv_path
        self.multipliers = np.array(multipliers)
        self.buckets = self._load_csv()
        self.num_buckets = len(multipliers)
    
    def _load_csv(self) -> List[int]:
        """Load bucket distribution from CSV."""
        buckets = []
        with open(self.csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    buckets.append(int(row[0].strip()))
        return buckets
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive statistics from CSV distribution."""
        total = len(self.buckets)
        
        # Calculate probabilities
        bucket_counts = Counter(self.buckets)
        probabilities = np.zeros(self.num_buckets)
        
        for bucket_idx in range(self.num_buckets):
            probabilities[bucket_idx] = bucket_counts.get(bucket_idx, 0) / total
        
        # RTP
        rtp = np.sum(probabilities * self.multipliers)
        
        # Prob less bet
        prob_less_bet = np.sum(probabilities[self.multipliers < 1.0])
        
        # Hit rates
        hit_rates = {}
        for i, prob in enumerate(probabilities):
            hit_rates[i] = 1.0 / prob if prob > 0 else float('inf')
        
        # Volatility metrics
        ev = rtp
        variance = np.sum(probabilities * (self.multipliers - ev) ** 2)
        std = np.sqrt(variance)
        
        # Median and M2M
        sorted_mults = sorted(zip(probabilities, self.multipliers), reverse=True)
        cumsum = 0
        median = 0
        for prob, mult in sorted_mults:
            cumsum += prob
            if cumsum >= 0.5:
                median = mult
                break
        
        m2m = ev / median if median > 0 else float('inf')
        
        # Distribution shape metrics
        skewness = np.sum(probabilities * ((self.multipliers - ev) / std) ** 3) if std > 0 else 0
        kurtosis = np.sum(probabilities * ((self.multipliers - ev) / std) ** 4) - 3 if std > 0 else 0
        
        return {
            "total_weight": total,
            "probabilities": probabilities.tolist(),
            "bucket_counts": dict(bucket_counts),
            "rtp": rtp,
            "prob_less_bet": prob_less_bet,
            "hit_rates": hit_rates,
            "expected_value": ev,
            "variance": variance,
            "std": std,
            "median": median,
            "m2m": m2m,
            "skewness": skewness,
            "excess_kurtosis": kurtosis,
        }
    
    def monte_carlo_simulation(self, num_trials: int = 100000) -> Dict:
        """Run Monte Carlo simulation to verify RTP and volatility.
        
        Args:
            num_trials: Number of simulated spins
            
        Returns:
            Dictionary with simulation results
        """
        # Simulate spins
        results = np.random.choice(self.buckets, size=num_trials)
        wins = np.array([self.multipliers[bucket] for bucket in results])
        
        # Calculate statistics
        sim_rtp = np.mean(wins)
        sim_std = np.std(wins)
        sim_median = np.median(wins)
        sim_m2m = sim_rtp / sim_median if sim_median > 0 else float('inf')
        
        # Prob less bet
        sim_plb = np.sum(wins < 1.0) / num_trials
        
        # Hit rates for specific buckets
        bucket_hits = Counter(results)
        sim_hit_rates = {}
        for bucket_idx in range(self.num_buckets):
            count = bucket_hits.get(bucket_idx, 0)
            sim_hit_rates[bucket_idx] = num_trials / count if count > 0 else float('inf')
        
        return {
            "num_trials": num_trials,
            "sim_rtp": sim_rtp,
            "sim_std": sim_std,
            "sim_median": sim_median,
            "sim_m2m": sim_m2m,
            "sim_prob_less_bet": sim_plb,
            "sim_hit_rates": sim_hit_rates,
            "wins_distribution": wins.tolist()[:1000],  # Sample of first 1000
        }
    
    def compare_to_target(self, target_rtp: float, target_plb: float, 
                         target_bucket_hrs: Optional[Dict[int, float]] = None) -> Dict:
        """Compare actual results to targets.
        
        Args:
            target_rtp: Target RTP
            target_plb: Target prob_less_bet
            target_bucket_hrs: Optional dict of bucket index -> target hit rate
            
        Returns:
            Comparison results
        """
        stats = self.calculate_statistics()
        
        comparison = {
            "rtp": {
                "target": target_rtp,
                "actual": stats["rtp"],
                "error": abs(stats["rtp"] - target_rtp),
                "error_pct": abs(stats["rtp"] - target_rtp) / target_rtp * 100,
            },
            "prob_less_bet": {
                "target": target_plb,
                "actual": stats["prob_less_bet"],
                "error": abs(stats["prob_less_bet"] - target_plb),
                "error_pct": abs(stats["prob_less_bet"] - target_plb) / target_plb * 100,
            }
        }
        
        if target_bucket_hrs:
            comparison["bucket_hrs"] = {}
            for bucket_idx, target_hr in target_bucket_hrs.items():
                actual_hr = stats["hit_rates"][bucket_idx]
                comparison["bucket_hrs"][bucket_idx] = {
                    "target": target_hr,
                    "actual": actual_hr,
                    "error": abs(actual_hr - target_hr),
                    "error_pct": abs(actual_hr - target_hr) / target_hr * 100 if target_hr != float('inf') else 0,
                }
        
        return comparison
    
    def print_verification_report(self, target_rtp: float, target_plb: float,
                                 target_bucket_hrs: Optional[Dict[int, float]] = None,
                                 run_monte_carlo: bool = True):
        """Print comprehensive verification report.
        
        Args:
            target_rtp: Target RTP
            target_plb: Target prob_less_bet
            target_bucket_hrs: Optional dict of bucket index -> target hit rate
            run_monte_carlo: Whether to run Monte Carlo simulation
        """
        print(f"\n{'='*70}")
        print(f"OPTIMIZER VERIFICATION REPORT")
        print(f"{'='*70}\n")
        
        print(f"CSV File: {self.csv_path}")
        
        # Basic statistics
        stats = self.calculate_statistics()
        print(f"\nBasic Statistics:")
        print(f"  Total Weight: {stats['total_weight']:,}")
        print(f"  Number of Buckets: {self.num_buckets}")
        
        # RTP comparison
        comparison = self.compare_to_target(target_rtp, target_plb, target_bucket_hrs)
        
        print(f"\nRTP Verification:")
        print(f"  Target:    {comparison['rtp']['target']:.6f}")
        print(f"  Actual:    {comparison['rtp']['actual']:.6f}")
        print(f"  Error:     {comparison['rtp']['error']:.8f} ({comparison['rtp']['error_pct']:.4f}%)")
        print(f"  Status:    {'✓ PASS' if comparison['rtp']['error'] < 0.001 else '✗ FAIL'}")
        
        print(f"\nProb Less Bet Verification:")
        print(f"  Target:    {comparison['prob_less_bet']['target']:.6f}")
        print(f"  Actual:    {comparison['prob_less_bet']['actual']:.6f}")
        print(f"  Error:     {comparison['prob_less_bet']['error']:.8f} ({comparison['prob_less_bet']['error_pct']:.4f}%)")
        print(f"  Status:    {'✓ PASS' if comparison['prob_less_bet']['error'] < 0.01 else '✗ FAIL'}")
        
        # Bucket hit rates
        if target_bucket_hrs:
            print(f"\nBucket Hit Rate Verification:")
            for bucket_idx, hr_data in comparison['bucket_hrs'].items():
                print(f"  Bucket {bucket_idx}:")
                print(f"    Target HR: 1 in {hr_data['target']:.0f}")
                print(f"    Actual HR: 1 in {hr_data['actual']:.0f}")
                print(f"    Error:     {hr_data['error']:.2f} ({hr_data['error_pct']:.4f}%)")
                print(f"    Status:    {'✓ PASS' if hr_data['error_pct'] < 1.0 else '✗ FAIL'}")
        
        # Volatility metrics
        print(f"\nVolatility Metrics:")
        print(f"  Expected Value: {stats['expected_value']:.6f}")
        print(f"  Std Deviation:  {stats['std']:.4f}")
        print(f"  Variance:       {stats['variance']:.4f}")
        print(f"  Median:         {stats['median']:.4f}")
        print(f"  M2M Ratio:      {stats['m2m']:.2f}")
        print(f"  Skewness:       {stats['skewness']:.2f}")
        print(f"  Excess Kurtosis: {stats['excess_kurtosis']:.2f}")
        
        # Bucket distribution
        print(f"\nBucket Distribution:")
        print(f"  {'Bucket':<8} {'Mult':<10} {'Count':<12} {'Prob':<12} {'Hit Rate':<15}")
        print(f"  {'-'*60}")
        for i in range(self.num_buckets):
            count = stats['bucket_counts'].get(i, 0)
            prob = stats['probabilities'][i]
            mult = self.multipliers[i]
            hr = stats['hit_rates'][i]
            hr_str = f"1 in {hr:.0f}" if hr != float('inf') else "Never"
            print(f"  {i:<8} {mult:<10.2f} {count:<12,} {prob:<12.6f} {hr_str:<15}")
        
        # Monte Carlo simulation
        if run_monte_carlo:
            print(f"\nMonte Carlo Simulation (100,000 trials):")
            mc_results = self.monte_carlo_simulation(100000)
            print(f"  Simulated RTP:  {mc_results['sim_rtp']:.6f}")
            print(f"  Simulated Std:  {mc_results['sim_std']:.4f}")
            print(f"  Simulated M2M:  {mc_results['sim_m2m']:.2f}")
            print(f"  Simulated PLB:  {mc_results['sim_prob_less_bet']:.6f}")
            
            # Compare with theoretical
            print(f"\n  Comparison to Theoretical:")
            print(f"    RTP Error:  {abs(mc_results['sim_rtp'] - stats['rtp']):.6f}")
            print(f"    PLB Error:  {abs(mc_results['sim_prob_less_bet'] - stats['prob_less_bet']):.6f}")
        
        print(f"\n{'='*70}\n")


def verify_all_modes():
    """Verify all three modes (MILD, SINFUL, DEMONIC)."""
    from game_config import GameConfig
    from optimizer_config import OptimizerConfig
    
    game_config = GameConfig()
    opt_config = OptimizerConfig()
    
    modes = ["mild", "sinful", "demonic"]
    
    for mode in modes:
        csv_path = f"reels/{mode.upper()}.csv"
        multipliers = game_config.bucket_multipliers[mode]
        mode_config = opt_config.get_config(mode)
        
        try:
            verifier = OptimizerVerifier(csv_path, multipliers)
            
            # Extract target bucket HRs
            target_hrs = {}
            for bucket_idx, constraint in mode_config.get("bucket_constraints", {}).items():
                if "hr" in constraint:
                    target_hrs[bucket_idx] = constraint["hr"]
            
            verifier.print_verification_report(
                target_rtp=mode_config["target_rtp"],
                target_plb=mode_config["target_prob_less_bet"],
                target_bucket_hrs=target_hrs,
                run_monte_carlo=True
            )
        except FileNotFoundError:
            print(f"\n⚠ WARNING: {csv_path} not found. Run optimizer first.\n")


if __name__ == "__main__":
    verify_all_modes()

