"""
Automated Reel Balancing Script
Intelligently adjusts reel weights to reach target RTP during simulations.

This script:
1. Runs quick test simulations
2. Analyzes what's driving high RTP (tumbles, symbols, multipliers)
3. Calculates optimal weight adjustments
4. Regenerates reels automatically
5. Repeats until target is reached
"""

import os
import sys
import json
import random
import zstandard as zstd
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from generate_reels import ReelGenerator


class AutoBalancer:
    """Automatically balance reels to target RTP through iterative simulation and adjustment."""
    
    def __init__(self, target_rtp: float = 0.75, tolerance: float = 0.05, max_iterations: int = 6):
        """
        Args:
            target_rtp: Target RTP for simulation (NOT optimization target)
            tolerance: Acceptable deviation from target (e.g., 0.05 = ±5%)
            max_iterations: Max balancing iterations
        """
        self.target_rtp = target_rtp
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        
        self.config = GameConfig()
        self.gamestate = GameState(self.config)
        
        # Current reel weights (will be adjusted)
        self.base_weights = {
            "H1": 0.02, "H2": 0.03, "H3": 0.04,
            "L1": 0.15, "L2": 0.20, "L3": 0.30, "L4": 0.26,
        }
        self.base_scatter = 0.02
        self.base_multiplier = 0.008
        
        self.free_weights = {
            "H1": 0.04, "H2": 0.05, "H3": 0.06,
            "L1": 0.18, "L2": 0.22, "L3": 0.28, "L4": 0.17,
        }
        self.free_scatter = 0.015
        self.free_multiplier = 0.015
        
        self.history = []
    
    def run_diagnostic_sim(self, num_spins: int = 2000) -> Dict:
        """Run quick simulation and extract detailed diagnostics."""
        print(f"\n{'-'*70}")
        print(f"Running {num_spins:,} spin diagnostic...")
        print(f"{'-'*70}")
        
        try:
            num_sim_args = {"base": num_spins}
            create_books(
                self.gamestate,
                self.config,
                num_sim_args,
                batch_size=10000,
                threads=1,
                compress=True,  # Enable compression - we can read zst files
                profiling=False,
            )
            
            return self._analyze_results()
        except Exception as e:
            print(f"[ERROR] Exception during simulation/analysis: {e}")
            import traceback
            traceback.print_exc()
            return {"rtp": 999.0}
    
    def _analyze_results(self) -> Dict:
        """Deep analysis of simulation results."""
        # Books are compressed as .jsonl.zst in publish_files
        books_path = os.path.join(
            os.path.dirname(__file__), "library", "publish_files", "books_base.jsonl.zst"
        )
        
        print(f"[DEBUG] Looking for books at: {books_path}")
        print(f"[DEBUG] File exists: {os.path.exists(books_path)}")
        
        if not os.path.exists(books_path):
            print(f"[ERROR] Books file not found at: {books_path}")
            return {"rtp": 999.0}  # Error indicator
        
        # Decompress and read JSONL format
        data = []
        try:
            with open(books_path, 'rb') as f:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(f) as reader:
                    text_stream = reader.read().decode('utf-8')
                    # JSONL format: one JSON object per line
                    for line in text_stream.strip().split('\n'):
                        if line:
                            data.append(json.loads(line))
            print(f"[DEBUG] Successfully loaded {len(data)} spins")
        except Exception as e:
            print(f"[ERROR] Failed to decompress/parse books: {e}")
            import traceback
            traceback.print_exc()
            return {"rtp": 999.0}
        
        # Parse the actual books structure
        total_spins = len(data)
        total_win = 0.0
        total_bet = total_spins * 1.0
        
        print(f"[DEBUG] Processing {total_spins} spins...")
        
        # Deep metrics
        tumble_counts = []
        high_symbol_wins = 0
        low_symbol_wins = 0
        multiplier_hits = 0
        bonus_triggers = 0
        max_win_seen = 0.0
        
        for spin in data:
            # payoutMultiplier is in cents, divide by 100 to get multiplier
            win = spin.get('payoutMultiplier', 0) / 100.0
            total_win += win
            max_win_seen = max(max_win_seen, win)
            
            # Count events (tumbles are each reveal after the first)
            events = spin.get('events', [])
            tumble_count = len([e for e in events if e.get('type') == 'reveal']) - 1  # -1 for initial reveal
            tumble_counts.append(max(0, tumble_count))
            
            # Analyze board symbols from first reveal event
            if events:
                first_board = events[0].get('board', [])
                board_symbols = []
                for row in first_board:
                    for cell in row:
                        if isinstance(cell, dict):
                            board_symbols.append(cell.get('name', ''))
                
                high_count = sum(1 for s in board_symbols if s in ['H1', 'H2', 'H3'])
                low_count = sum(1 for s in board_symbols if s in ['L1', 'L2'])
                
                if win > 0:
                    if high_count >= 8:
                        high_symbol_wins += 1
                    if low_count >= 8:
                        low_symbol_wins += 1
                    
                    if 'M' in board_symbols:
                        multiplier_hits += 1
            
            # Check bonus triggers (freespin event type)
            if any(e.get('type', '').lower() == 'freespin' for e in events):
                bonus_triggers += 1
        
        rtp = total_win / total_bet if total_bet > 0 else 0
        avg_tumbles = sum(tumble_counts) / len(tumble_counts) if tumble_counts else 0
        max_tumbles = max(tumble_counts) if tumble_counts else 0
        
        print(f"[DEBUG] Analysis complete - RTP: {rtp:.2f}, Total Win: {total_win:.2f}, Max Win: {max_win_seen:.2f}")
        
        diagnostics = {
            "rtp": rtp,
            "avg_win": total_win / total_spins if total_spins > 0 else 0,
            "max_win": max_win_seen,
            "avg_tumbles": avg_tumbles,
            "max_tumbles": max_tumbles,
            "high_symbol_win_rate": high_symbol_wins / total_spins if total_spins > 0 else 0,
            "low_symbol_win_rate": low_symbol_wins / total_spins if total_spins > 0 else 0,
            "multiplier_hit_rate": multiplier_hits / total_spins if total_spins > 0 else 0,
            "bonus_trigger_rate": bonus_triggers / total_spins if total_spins > 0 else 0,
            "total_spins": total_spins,
        }
        
        return diagnostics
    
    def diagnose_and_adjust(self, diagnostics: Dict) -> Dict[str, float]:
        """
        Intelligently analyze diagnostics and calculate adjustment factors.
        Returns factors to multiply current weights by.
        """
        print(f"\n{'='*70}")
        print(f"DIAGNOSTICS")
        print(f"{'='*70}")
        
        rtp = diagnostics["rtp"]
        target = self.target_rtp
        
        print(f"  RTP:           {rtp:.4f} (Target: {target:.4f})")
        print(f"  Deviation:     {(rtp/target - 1)*100:+.1f}%")
        print(f"  Avg Win:       {diagnostics['avg_win']:.2f}x")
        print(f"  Max Win:       {diagnostics['max_win']:.2f}x")
        print(f"  Avg Tumbles:   {diagnostics['avg_tumbles']:.2f}")
        print(f"  Max Tumbles:   {diagnostics['max_tumbles']}")
        print(f"  High Sym Wins: {diagnostics['high_symbol_win_rate']:.1%}")
        print(f"  Low Sym Wins:  {diagnostics['low_symbol_win_rate']:.1%}")
        print(f"  Mult Hits:     {diagnostics['multiplier_hit_rate']:.1%}")
        print(f"  Bonus Rate:    {diagnostics['bonus_trigger_rate']:.1%}")
        
        # Calculate adjustment strategy
        rtp_ratio = rtp / target
        
        print(f"\n{'-'*70}")
        print(f"ADJUSTMENT STRATEGY")
        print(f"{'-'*70}")
        
        adjustments = {
            "H1": 1.0, "H2": 1.0, "H3": 1.0,
            "L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0,
            "scatter": 1.0, "multiplier": 1.0,
        }
        
        if abs(rtp_ratio - 1.0) < self.tolerance:
            print(f"  [OK] RTP is within tolerance - no adjustments needed!")
            return adjustments
        
        if rtp_ratio > 1.0:  # RTP too high
            overshoot = rtp_ratio - 1.0
            print(f"  [HIGH] RTP is {overshoot*100:.1f}% too HIGH")
            
            # Main drivers of high RTP
            if diagnostics['avg_tumbles'] > 2.0:
                print(f"     Issue: Excessive tumbles ({diagnostics['avg_tumbles']:.1f} avg)")
                print(f"     Action: Drastically reduce high symbols")
                # Aggressive reduction
                adjustments["H1"] = 0.4
                adjustments["H2"] = 0.5
                adjustments["H3"] = 0.6
                adjustments["L1"] = 0.9
                adjustments["L2"] = 0.95
                adjustments["L3"] = 1.2
                adjustments["L4"] = 1.3
            elif diagnostics['avg_tumbles'] > 1.3:
                print(f"     Issue: Many tumbles ({diagnostics['avg_tumbles']:.1f} avg)")
                print(f"     Action: Reduce high symbols moderately")
                adjustments["H1"] = 0.6
                adjustments["H2"] = 0.7
                adjustments["H3"] = 0.8
                adjustments["L3"] = 1.15
                adjustments["L4"] = 1.15
            else:
                print(f"     Issue: High wins without excessive tumbles")
                print(f"     Action: Moderate reduction across board")
                adjustments["H1"] = 0.75
                adjustments["H2"] = 0.8
                adjustments["H3"] = 0.85
                adjustments["L3"] = 1.1
                adjustments["L4"] = 1.1
            
            # Multiplier check
            if diagnostics['multiplier_hit_rate'] > 0.05:
                print(f"     Issue: Too many multipliers ({diagnostics['multiplier_hit_rate']:.1%})")
                print(f"     Action: Cut multipliers by 50%")
                adjustments["multiplier"] = 0.5
            elif diagnostics['multiplier_hit_rate'] > 0.03:
                adjustments["multiplier"] = 0.7
            
            # Bonus check
            if diagnostics['bonus_trigger_rate'] > 0.12:
                print(f"     Issue: Frequent bonuses ({diagnostics['bonus_trigger_rate']:.1%})")
                print(f"     Action: Reduce scatters")
                adjustments["scatter"] = 0.7
        
        else:  # RTP too low
            undershoot = 1.0 - rtp_ratio
            print(f"  [LOW] RTP is {undershoot*100:.1f}% too LOW")
            print(f"     Action: Increase high symbols and multipliers")
            
            adjustments["H1"] = 1.2
            adjustments["H2"] = 1.15
            adjustments["H3"] = 1.1
            adjustments["L3"] = 0.9
            adjustments["L4"] = 0.9
            adjustments["multiplier"] = 1.3
            adjustments["scatter"] = 1.1
        
        return adjustments
    
    def apply_adjustments_and_regenerate(self, adjustments: Dict[str, float]):
        """Apply adjustments to weights and regenerate reels."""
        print(f"\n{'-'*70}")
        print(f"APPLYING ADJUSTMENTS")
        print(f"{'-'*70}")
        
        # Adjust base game weights
        for symbol in self.base_weights:
            old_val = self.base_weights[symbol]
            self.base_weights[symbol] *= adjustments.get(symbol, 1.0)
            new_val = self.base_weights[symbol]
            print(f"  {symbol}: {old_val:.4f} -> {new_val:.4f} ({adjustments.get(symbol, 1.0):.2f}x)")
        
        # Adjust free game weights
        for symbol in self.free_weights:
            self.free_weights[symbol] *= adjustments.get(symbol, 1.0)
        
        # Adjust special symbols
        old_scatter = self.base_scatter
        old_mult = self.base_multiplier
        self.base_scatter *= adjustments.get("scatter", 1.0)
        self.base_multiplier *= adjustments.get("multiplier", 1.0)
        self.free_scatter *= adjustments.get("scatter", 1.0)
        self.free_multiplier *= adjustments.get("multiplier", 1.0)
        
        print(f"  Scatter: {old_scatter:.4f} -> {self.base_scatter:.4f}")
        print(f"  Multiplier: {old_mult:.4f} -> {self.base_multiplier:.4f}")
        
        # Normalize weights
        self._normalize_weights()
        
        # Regenerate reels
        print(f"\n  Regenerating reels...")
        self._regenerate_reels()
    
    def _normalize_weights(self):
        """Ensure weights sum to proper values."""
        base_sum = sum(self.base_weights.values())
        for symbol in self.base_weights:
            self.base_weights[symbol] /= base_sum
        
        free_sum = sum(self.free_weights.values())
        for symbol in self.free_weights:
            self.free_weights[symbol] /= free_sum
    
    def _regenerate_reels(self):
        """Generate new reel files with current weights."""
        random.seed(random.randint(0, 999999))  # Different seed each time
        
        # Base game
        base_gen = ReelGenerator(
            num_reels=6, num_rows=250,
            symbol_weights=self.base_weights.copy(),
            scatter_weight=self.base_scatter,
            multiplier_weight=self.base_multiplier,
        )
        base_gen.generate_reel_file("reels/BR0.csv", reel_type="basegame")
        
        # Free game
        free_gen = ReelGenerator(
            num_reels=6, num_rows=250,
            symbol_weights=self.free_weights.copy(),
            scatter_weight=self.free_scatter,
            multiplier_weight=self.free_multiplier,
        )
        free_gen.generate_reel_file("reels/FR0.csv", reel_type="freegame")
        
        print(f"  [OK] Reels regenerated")
    
    def run(self):
        """Main balancing loop."""
        print(f"\n{'='*70}")
        print(f"AUTOMATED REEL BALANCER")
        print(f"{'='*70}")
        print(f"  Target RTP: {self.target_rtp:.2%}")
        print(f"  Tolerance: +/-{self.tolerance*100:.0f}%")
        print(f"  Max Iterations: {self.max_iterations}")
        print(f"{'='*70}")
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'#'*70}")
            print(f"#  ITERATION {iteration} / {self.max_iterations}")
            print(f"{'#'*70}")
            
            # Run simulation and analyze
            diagnostics = self.run_diagnostic_sim(num_spins=2000)
            
            # Check for actual error (not just high RTP)
            if diagnostics.get("rtp", 0) == 999.0:  # Explicit error indicator
                print(f"[ERROR] Simulation failed - aborting")
                break
            
            # Store history
            self.history.append({
                "iteration": iteration,
                "rtp": diagnostics["rtp"],
                "diagnostics": diagnostics,
            })
            
            # Check if we're done
            rtp_ratio = diagnostics["rtp"] / self.target_rtp
            if abs(rtp_ratio - 1.0) < self.tolerance:
                print(f"\n{'='*70}")
                print(f"SUCCESS! Target RTP reached in {iteration} iterations")
                print(f"   Final RTP: {diagnostics['rtp']:.4f}")
                print(f"   Target: {self.target_rtp:.4f}")
                print(f"   Deviation: {(rtp_ratio - 1)*100:+.1f}%")
                print(f"{'='*70}")
                break
            
            # Calculate and apply adjustments
            adjustments = self.diagnose_and_adjust(diagnostics)
            
            if all(abs(v - 1.0) < 0.01 for v in adjustments.values()):
                print(f"\n  No significant adjustments - stopping")
                break
            
            self.apply_adjustments_and_regenerate(adjustments)
            
            # Reload config and gamestate to pick up new reels
            print(f"  [INFO] Reloading game configuration...")
            self.config = GameConfig()
            self.gamestate = GameState(self.config)
        
        # Summary
        self._print_summary()
    
    def _print_summary(self):
        """Print final summary of balancing process."""
        print(f"\n{'='*70}")
        print(f"BALANCING SUMMARY")
        print(f"{'='*70}")
        
        for entry in self.history:
            rtp = entry["rtp"]
            dev = (rtp / self.target_rtp - 1) * 100
            icon = "[OK]" if abs(dev) < self.tolerance * 100 else "[->]"
            print(f"  {icon} Iteration {entry['iteration']}: RTP = {rtp:.4f} ({dev:+.1f}%)")
        
        if self.history:
            final_rtp = self.history[-1]["rtp"]
            print(f"\n  Final RTP: {final_rtp:.4f}")
            print(f"  Target RTP: {self.target_rtp:.4f}")
            print(f"  Difference: {(final_rtp - self.target_rtp):.4f}")
        
        print(f"{'='*70}\n")


if __name__ == "__main__":
    # Run automatic balancing
    balancer = AutoBalancer(
        target_rtp=0.75,      # Target 75% RTP for simulations (optimization will bring it to 96%)
        tolerance=0.05,       # ±5% acceptable
        max_iterations=6,     # Max 6 attempts
    )
    balancer.run()
