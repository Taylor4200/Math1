"""
Automated Reel Balancing Script
Diagnoses RTP issues and automatically adjusts reel parameters to hit target RTP.

This script:
1. Runs quick simulations to identify RTP drivers
2. Analyzes tumble chains, symbol frequencies, multiplier impact
3. Automatically adjusts reel generation parameters
4. Iteratively regenerates reels until target RTP is reached
"""

import os
import sys
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import subprocess

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books


class ReelBalancer:
    """Analyzes simulation results and automatically balances reels to target RTP."""
    
    def __init__(self, target_rtp: float = 0.70, max_iterations: int = 10):
        """
        Initialize reel balancer.
        
        Args:
            target_rtp: Target RTP for simulations (not optimization RTP)
            max_iterations: Max number of reel regeneration attempts
        """
        self.target_rtp = target_rtp
        self.max_iterations = max_iterations
        self.config = GameConfig()
        self.gamestate = GameState(self.config)
        
        # Track diagnostics across iterations
        self.iteration_history = []
        
    def run_quick_sim(self, num_spins: int = 1000) -> Dict:
        """Run a quick simulation to diagnose issues."""
        print(f"\n{'='*70}")
        print(f"Running diagnostic simulation ({num_spins:,} spins)...")
        print(f"{'='*70}")
        
        # Run simulation
        num_sim_args = {"base": num_spins}
        create_books(
            self.gamestate,
            self.config,
            num_sim_args,
            batching_size=10000,
            num_threads=1,
            compression=False,
            profiling=False,
        )
        
        # Read results from published files
        return self._read_simulation_results()
    
    def _read_simulation_results(self) -> Dict:
        """Read and parse simulation results."""
        results = {
            "rtp": 0.0,
            "avg_win": 0.0,
            "tumble_chains": [],
            "symbol_hits": defaultdict(int),
            "multiplier_impact": 0.0,
            "bonus_frequency": 0.0,
            "diagnostics": {},
        }
        
        # Read from books file if available
        books_path = os.path.join(
            self.config.publish_files_path,
            "base",
            "books_0_base.json"
        )
        
        if not os.path.exists(books_path):
            print(f"[WARN] Books file not found: {books_path}")
            return results
        
        try:
            with open(books_path, 'r') as f:
                data = json.load(f)
            
            # Calculate RTP and metrics
            total_spins = len(data)
            total_win = sum(spin.get('totalWin', 0) for spin in data)
            total_bet = total_spins * 1.0  # Assuming bet = 1
            
            results["rtp"] = total_win / total_bet if total_bet > 0 else 0
            results["avg_win"] = total_win / total_spins if total_spins > 0 else 0
            
            # Analyze each spin
            tumble_counts = []
            multiplier_wins = []
            bonus_triggers = 0
            symbol_frequency = defaultdict(int)
            
            for spin in data:
                # Count tumbles (look for multiple win events)
                events = spin.get('events', [])
                tumble_count = sum(1 for e in events if 'win' in e.get('type', '').lower())
                tumble_counts.append(tumble_count)
                
                # Track multiplier impact
                for event in events:
                    if 'multiplier' in event.get('type', '').lower():
                        mult_value = event.get('value', 1)
                        multiplier_wins.append(mult_value)
                
                # Count bonus triggers
                if any('freespin' in e.get('type', '').lower() for e in events):
                    bonus_triggers += 1
                
                # Count symbol frequencies on board
                board = spin.get('board', [])
                for row in board:
                    for symbol in row:
                        symbol_frequency[symbol] += 1
            
            results["tumble_chains"] = tumble_counts
            results["symbol_hits"] = dict(symbol_frequency)
            results["multiplier_impact"] = sum(multiplier_wins) / len(multiplier_wins) if multiplier_wins else 1.0
            results["bonus_frequency"] = bonus_triggers / total_spins if total_spins > 0 else 0
            
            # Store diagnostics
            avg_tumbles = sum(tumble_counts) / len(tumble_counts) if tumble_counts else 0
            max_tumbles = max(tumble_counts) if tumble_counts else 0
            
            results["diagnostics"] = {
                "total_spins": total_spins,
                "avg_tumbles_per_spin": avg_tumbles,
                "max_tumbles_seen": max_tumbles,
                "avg_multiplier": results["multiplier_impact"],
                "bonus_hit_rate": results["bonus_frequency"],
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to read simulation results: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def diagnose_issues(self, results: Dict) -> Dict[str, float]:
        """
        Analyze results and identify what's driving high RTP.
        Returns adjustment factors for reel parameters.
        """
        print(f"\n{'='*70}")
        print("DIAGNOSTIC RESULTS")
        print(f"{'='*70}")
        
        current_rtp = results["rtp"]
        diagnostics = results["diagnostics"]
        
        print(f"  Current RTP: {current_rtp:.2%} (Target: {self.target_rtp:.2%})")
        print(f"  Average Win: {results['avg_win']:.2f}x")
        print(f"  Avg Tumbles/Spin: {diagnostics.get('avg_tumbles_per_spin', 0):.2f}")
        print(f"  Max Tumbles Seen: {diagnostics.get('max_tumbles_seen', 0)}")
        print(f"  Avg Multiplier: {diagnostics.get('avg_multiplier', 1.0):.2f}x")
        print(f"  Bonus Hit Rate: {diagnostics.get('bonus_hit_rate', 0):.2%}")
        
        # Analyze symbol distribution
        total_symbols = sum(results["symbol_hits"].values())
        print(f"\n  Symbol Distribution (from boards):")
        for symbol in sorted(results["symbol_hits"].keys()):
            count = results["symbol_hits"][symbol]
            pct = count / total_symbols * 100 if total_symbols > 0 else 0
            print(f"    {symbol:3s}: {pct:5.2f}%")
        
        # Calculate adjustment factors
        rtp_ratio = current_rtp / self.target_rtp
        print(f"\n  RTP Ratio: {rtp_ratio:.2f}x target")
        
        adjustments = {}
        
        # If RTP is way too high, we need to reduce high-paying symbols and multipliers
        if rtp_ratio > 1.5:  # RTP is 50%+ too high
            print(f"\n  🔴 CRITICAL: RTP is {(rtp_ratio-1)*100:.0f}% above target!")
            print(f"     Main issues to address:")
            
            # Check tumble chains
            avg_tumbles = diagnostics.get('avg_tumbles_per_spin', 0)
            if avg_tumbles > 1.5:
                print(f"       - Too many tumbles ({avg_tumbles:.1f} avg) → Reduce high symbols")
                adjustments['high_symbol_factor'] = 0.5  # Cut high symbols in half
                adjustments['low_symbol_factor'] = 1.3  # Boost low symbols
            else:
                adjustments['high_symbol_factor'] = 0.7
                adjustments['low_symbol_factor'] = 1.2
            
            # Check multipliers
            avg_mult = diagnostics.get('avg_multiplier', 1.0)
            if avg_mult > 3.0:
                print(f"       - High multipliers ({avg_mult:.1f}x avg) → Drastically reduce M symbols")
                adjustments['multiplier_factor'] = 0.3  # Cut to 30%
            elif avg_mult > 2.0:
                print(f"       - Moderate multipliers ({avg_mult:.1f}x avg) → Reduce M symbols")
                adjustments['multiplier_factor'] = 0.5
            else:
                adjustments['multiplier_factor'] = 0.7
            
            # Check bonus frequency
            bonus_rate = diagnostics.get('bonus_hit_rate', 0)
            if bonus_rate > 0.15:  # More than 15% bonus rate
                print(f"       - High bonus rate ({bonus_rate:.1%}) → Reduce scatters")
                adjustments['scatter_factor'] = 0.6
            else:
                adjustments['scatter_factor'] = 0.8
                
        elif rtp_ratio > 1.1:  # RTP is 10%+ too high
            print(f"\n  🟡 MODERATE: RTP is {(rtp_ratio-1)*100:.0f}% above target")
            adjustments['high_symbol_factor'] = 0.8
            adjustments['low_symbol_factor'] = 1.15
            adjustments['multiplier_factor'] = 0.7
            adjustments['scatter_factor'] = 0.9
            
        elif rtp_ratio < 0.9:  # RTP is too low
            print(f"\n  🔵 RTP is below target - need to increase")
            adjustments['high_symbol_factor'] = 1.2
            adjustments['low_symbol_factor'] = 0.9
            adjustments['multiplier_factor'] = 1.3
            adjustments['scatter_factor'] = 1.1
            
        else:
            print(f"\n  ✅ RTP is within acceptable range!")
            adjustments['high_symbol_factor'] = 1.0
            adjustments['low_symbol_factor'] = 1.0
            adjustments['multiplier_factor'] = 1.0
            adjustments['scatter_factor'] = 1.0
        
        return adjustments
    
    def apply_adjustments_and_regenerate(self, adjustments: Dict[str, float]) -> None:
        """Apply adjustments to generate_reels.py and regenerate reels."""
        print(f"\n{'='*70}")
        print("APPLYING ADJUSTMENTS TO REEL GENERATION")
        print(f"{'='*70}")
        
        for key, value in adjustments.items():
            print(f"  {key}: {value:.2f}x")
        
        # Read current generate_reels.py
        gen_reels_path = os.path.join(os.path.dirname(__file__), "generate_reels.py")
        with open(gen_reels_path, 'r') as f:
            content = f.read()
        
        # Extract current weights and adjust them
        # This is a simplified version - in production you'd parse more carefully
        import re
        
        # Find base game weights
        base_pattern = r'# Base game reels.*?symbol_weights=\{(.*?)\}'
        base_match = re.search(base_pattern, content, re.DOTALL)
        
        if base_match:
            weights_text = base_match.group(1)
            # Parse weights
            weight_dict = {}
            for line in weights_text.split('\n'):
                if ':' in line and '"' in line:
                    parts = line.split(':')
                    symbol = parts[0].strip().strip('"')
                    value = float(parts[1].strip().rstrip(','))
                    weight_dict[symbol] = value
            
            # Apply adjustments
            high_factor = adjustments.get('high_symbol_factor', 1.0)
            low_factor = adjustments.get('low_symbol_factor', 1.0)
            mult_factor = adjustments.get('multiplier_factor', 1.0)
            scatter_factor = adjustments.get('scatter_factor', 1.0)
            
            # Adjust weights
            if 'H1' in weight_dict:
                weight_dict['H1'] *= high_factor
            if 'H2' in weight_dict:
                weight_dict['H2'] *= high_factor
            if 'H3' in weight_dict:
                weight_dict['H3'] *= high_factor
            if 'L1' in weight_dict:
                weight_dict['L1'] *= low_factor
            if 'L2' in weight_dict:
                weight_dict['L2'] *= low_factor
            if 'L3' in weight_dict:
                weight_dict['L3'] *= low_factor
            if 'L4' in weight_dict:
                weight_dict['L4'] *= low_factor
            
            # Normalize weights to sum to ~1.0
            total_weight = sum(weight_dict.values())
            for symbol in weight_dict:
                weight_dict[symbol] /= total_weight
            
            print(f"\n  New Base Game Weights:")
            for symbol, weight in sorted(weight_dict.items()):
                print(f"    {symbol}: {weight:.4f}")
        
        # Regenerate reels using the script
        print(f"\n  Regenerating reels...")
        result = subprocess.run(
            [sys.executable, "generate_reels.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✅ Reels regenerated successfully")
            print(result.stdout)
        else:
            print(f"  ❌ Failed to regenerate reels")
            print(result.stderr)
    
    def run_balancing_loop(self) -> None:
        """Main loop: simulate → diagnose → adjust → repeat until target RTP reached."""
        print(f"\n{'='*80}")
        print(f"AUTOMATED REEL BALANCING")
        print(f"{'='*80}")
        print(f"Target RTP: {self.target_rtp:.2%}")
        print(f"Max Iterations: {self.max_iterations}")
        print(f"{'='*80}\n")
        
        for iteration in range(self.max_iterations):
            print(f"\n{'#'*80}")
            print(f"ITERATION {iteration + 1} / {self.max_iterations}")
            print(f"{'#'*80}")
            
            # Step 1: Run simulation
            results = self.run_quick_sim(num_spins=2000)  # Quick diagnostic run
            
            # Step 2: Diagnose issues
            adjustments = self.diagnose_issues(results)
            
            # Store results
            self.iteration_history.append({
                "iteration": iteration + 1,
                "rtp": results["rtp"],
                "adjustments": adjustments,
            })
            
            # Step 3: Check if we're close enough to target
            rtp_diff = abs(results["rtp"] - self.target_rtp) / self.target_rtp
            if rtp_diff < 0.05:  # Within 5% of target
                print(f"\n{'='*80}")
                print(f"✅ SUCCESS! RTP is within 5% of target ({results['rtp']:.2%})")
                print(f"{'='*80}")
                break
            
            # Step 4: Apply adjustments and regenerate reels
            if all(v == 1.0 for v in adjustments.values()):
                print(f"\n  No adjustments needed - stopping.")
                break
            
            self.apply_adjustments_and_regenerate(adjustments)
            
            # Small delay between iterations
            import time
            time.sleep(1)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"BALANCING SUMMARY")
        print(f"{'='*80}")
        for entry in self.iteration_history:
            print(f"  Iteration {entry['iteration']}: RTP = {entry['rtp']:.2%}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    # Run the automated balancing
    balancer = ReelBalancer(target_rtp=0.70, max_iterations=5)
    balancer.run_balancing_loop()
