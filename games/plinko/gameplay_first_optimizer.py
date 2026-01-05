"""Gameplay-First Optimizer - Set GOOD hit rates, then find achievable house edges."""

import numpy as np
from typing import Dict
from weight_generator import WeightGenerator
import json


class GameplayFirstOptimizer:
    """Optimizer that prioritizes GOOD gameplay over exact house edge targets."""
    
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
        
        # Set GOOD hit rates for each mode
        self.hit_rates = self._get_good_hit_rates()
        self.solution = None
    
    def _get_good_hit_rates(self) -> Dict[int, float]:
        """Define GOOD, playable hit rates for each bucket."""
        
        if self.mode == "mild":
            # MILD: Bucket multipliers [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
            # For 96% RTP, we need center buckets VERY common, high multipliers VERY rare
            return {
                0: 5000,      # 666x - Rare but achievable!
                1: 3000,      # 150x - Rare
                2: 1500,      # 60x - Uncommon
                3: 500,       # 20x - Uncommon
                4: 100,       # 8x - Fairly common
                5: 30,        # 4x - Common
                6: 10,        # 2x - Very common
                7: 3.5,       # 1x - Extremely common
                8: 2.7,       # 0.5x - Most common
                9: 3.5,       # 1x - Extremely common
                10: 10,       # 2x - Very common
                11: 30,       # 4x - Common
                12: 100,      # 8x - Fairly common
                13: 500,      # 20x - Uncommon
                14: 1500,     # 60x - Uncommon
                15: 3000,     # 150x - Rare
                16: 5000,     # 666x - Rare but achievable!
            }
        
        elif self.mode == "sinful":
            # SINFUL: [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
            # Need center (0.2x) very common to keep RTP around 96%
            return {
                0: 10000,     # 1666x - Very rare
                1: 6000,      # 400x - Rare
                2: 3000,      # 120x - Uncommon
                3: 1000,      # 40x - Uncommon
                4: 300,       # 12x - Fairly common
                5: 80,        # 4x - Common
                6: 20,        # 2x - Very common
                7: 6,         # 0.5x - Extremely common
                8: 1.4,       # 0.2x - Most common (volatile!)
                9: 6,         # 0.5x - Extremely common
                10: 20,       # 2x - Very common
                11: 80,       # 4x - Common
                12: 300,      # 12x - Fairly common
                13: 1000,     # 40x - Uncommon
                14: 3000,     # 120x - Uncommon
                15: 6000,     # 400x - Rare
                16: 10000,    # 1666x - Very rare
            }
        
        elif self.mode == "demonic":
            # DEMONIC: [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]
            # 0x buckets need to dominate to keep RTP around 96%
            return {
                0: 50000,     # 16666x - Ultra rare
                1: 25000,     # 2500x - Very rare
                2: 15000,     # 600x - Rare
                3: 6000,      # 150x - Uncommon
                4: 1500,      # 40x - Fairly common
                5: 300,       # 8x - Fairly common
                6: 40,        # 2x - Common
                7: 3.5,       # 0x - Extremely common (volatile!)
                8: 3.5,       # 0x - Extremely common
                9: 3.5,       # 0x - Extremely common
                10: 40,       # 2x - Common
                11: 300,      # 8x - Fairly common
                12: 1500,     # 40x - Fairly common
                13: 6000,     # 150x - Uncommon
                14: 15000,    # 600x - Rare
                15: 25000,    # 2500x - Very rare
                16: 50000,    # 16666x - Ultra rare
            }
    
    def solve(self, verbose: bool = True) -> Dict:
        """Calculate distribution from hit rates."""
        # Convert hit rates to probabilities
        probabilities = np.zeros(self.num_buckets)
        for bucket_idx, hr in self.hit_rates.items():
            probabilities[bucket_idx] = 1.0 / hr
        
        # Normalize to sum to 1.0
        probabilities = probabilities / np.sum(probabilities)
        
        self.solution = probabilities
        
        # Calculate actual RTP
        actual_rtp = np.sum(probabilities * self.multipliers)
        house_edge = (1 - actual_rtp) * 100
        prob_less_bet = np.sum(probabilities[self.multipliers < 1.0])
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"GAMEPLAY-FIRST OPTIMIZER - {self.mode.upper()} MODE")
            print(f"{'='*60}\n")
            print(f"Actual RTP: {actual_rtp:.4f}")
            print(f"House Edge: {house_edge:.2f}%")
            print(f"prob_less_bet: {prob_less_bet:.4f}")
            
            print(f"\n{'Bucket':<8} {'Mult':<10} {'Hit Rate':<15} {'Probability':<15}")
            print("-" * 50)
            for i in range(self.num_buckets):
                mult = self.multipliers[i]
                hr = self.hit_rates[i]
                prob = probabilities[i]
                print(f"{i:<8} {mult:<10.1f} 1 in {hr:<11.0f} {prob:<15.6f}")
            
            print(f"\n{'='*60}\n")
        
        return {
            "mode": self.mode,
            "rtp": float(actual_rtp),
            "house_edge": float(house_edge),
            "prob_less_bet": float(prob_less_bet),
            "probabilities": [float(p) for p in probabilities],
            "multipliers": [float(m) for m in self.multipliers],
            "hit_rates": {int(k): float(v) for k, v in self.hit_rates.items()},
        }
    
    def save_to_csv(self, output_path: str, total_weight: int = 1000000):
        """Save to CSV."""
        if self.solution is None:
            raise ValueError("Must run solve() first")
        
        generator = WeightGenerator(total_weight=total_weight)
        weights = generator.probabilities_to_weights(self.solution)
        generator.weights_to_csv(weights, output_path)
        
        print(f"✓ Saved to: {output_path}")
        
        # Verify
        verification = generator.verify_distribution(output_path, self.solution, self.multipliers.tolist())
        print(f"  Verified RTP: {verification['actual_rtp']:.6f}")
        print(f"  Verified prob_less_bet: {verification['actual_prob_less_bet']:.6f}")
    
    def save_solution(self, output_path: str):
        """Save solution to JSON."""
        if self.solution is None:
            raise ValueError("Must run solve() first")
        
        stats = {
            "mode": self.mode,
            "rtp": float(np.sum(self.solution * self.multipliers)),
            "house_edge": float((1 - np.sum(self.solution * self.multipliers)) * 100),
            "prob_less_bet": float(np.sum(self.solution[self.multipliers < 1.0])),
            "probabilities": [float(p) for p in self.solution],
            "multipliers": [float(m) for m in self.multipliers],
            "hit_rates": {int(k): float(v) for k, v in self.hit_rates.items()},
        }
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Saved solution to: {output_path}")


def optimize_all_modes():
    """Optimize all three modes and show house edge margins."""
    modes = ["mild", "sinful", "demonic"]
    results = {}
    
    for mode in modes:
        print(f"\n{'#'*70}")
        print(f"# {mode.upper()} MODE")
        print(f"{'#'*70}")
        
        opt = GameplayFirstOptimizer(mode)
        stats = opt.solve(verbose=True)
        opt.save_to_csv(f"reels/{mode.upper()}.csv")
        opt.save_solution(f"library/gameplay_results_{mode}.json")
        
        results[mode] = stats
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"FINAL HOUSE EDGE SUMMARY")
    print(f"{'='*70}\n")
    
    for mode in modes:
        he = results[mode]['house_edge']
        rtp = results[mode]['rtp']
        print(f"{mode.upper():8} - House Edge: {he:.2f}%, RTP: {rtp:.4f}")
    
    print(f"\nHOUSE EDGE MARGINS:")
    mild_he = results['mild']['house_edge']
    sinful_he = results['sinful']['house_edge']
    demonic_he = results['demonic']['house_edge']
    
    print(f"  MILD -> SINFUL:   {sinful_he - mild_he:.2f}%")
    print(f"  SINFUL -> DEMONIC: {demonic_he - sinful_he:.2f}%")
    
    if abs(sinful_he - mild_he) <= 0.5 and abs(demonic_he - sinful_he) <= 0.5:
        print(f"\n✅ ALL MARGINS WITHIN 0.5% REQUIREMENT!")
    else:
        print(f"\n⚠ Margins need adjustment. Modify hit rates in GameplayFirstOptimizer._get_good_hit_rates()")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        optimize_all_modes()
    elif len(sys.argv) > 1:
        mode = sys.argv[1]
        opt = GameplayFirstOptimizer(mode)
        stats = opt.solve()
        opt.save_to_csv(f"reels/{mode.upper()}.csv")
        opt.save_solution(f"library/gameplay_results_{mode}.json")
    else:
        optimize_all_modes()

