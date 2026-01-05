"""Override methods for forcing specific Plinko outcomes during optimization."""

import random
from game_calculations import GameCalculations


class GameStateOverride(GameCalculations):
    """Handles forced bucket selection for optimization."""

    def create_symbol_map(self):
        """Plinko has no symbols - stub implementation."""
        # Create empty symbol storage since Plinko doesn't use symbols
        from src.calculations.symbol import SymbolStorage
        self.symbol_storage = SymbolStorage(self.config, [])

    def assign_special_sym_function(self):
        """Plinko has no special symbols - stub implementation."""
        pass

    def run_freespin(self):
        """Plinko has no free spins - stub implementation."""
        pass

    def apply_distribution_conditions(self):
        """Apply distribution-specific conditions for bucket selection."""
        # Note: self.criteria is already set by run_sims before run_spin is called
        # We just need to apply the conditions for this criteria
        
        # Get the distribution for current criteria
        bet_mode_obj = self.get_current_betmode()
        distributions = bet_mode_obj.get_distributions()
        
        for dist in distributions:
            if dist._criteria == self.criteria:
                self.distribution = dist
                break
        
        conditions = self.distribution._conditions

        # Set reel weights (bucket distribution to use)
        if "reel_weights" in conditions:
            self.reel_weights = conditions["reel_weights"]
        
        # Handle force_wincap condition
        if conditions.get("force_wincap", False):
            self.force_wincap = True
        else:
            self.force_wincap = False

    def draw_bucket(self, force_criteria=True):
        """Select bucket index - either forced by criteria or random weighted.
        
        Args:
            force_criteria: If True, apply criteria-based forcing. If False, use random selection.
        """
        mode_map = {"mild": "MILD", "sinful": "SINFUL", "demonic": "DEMONIC"}
        reel_key = mode_map[self.betmode]
        
        # Check if we need to force a specific bucket based on criteria
        if force_criteria:
            forced_bucket = self.select_bucket_for_criteria()
            
            if forced_bucket is not None:
                self.bucket_index = forced_bucket
                # Record this forced outcome for optimization
                self.record({"bucket": self.bucket_index, "criteria": self.criteria})
                return
        
        # Normal weighted random selection
        bucket_strip = self.config.reels[reel_key][0]  # Column 0
        position = random.randint(0, len(bucket_strip) - 1)
        self.bucket_index = int(bucket_strip[position])

    def select_bucket_for_criteria(self):
        """Force specific bucket based on optimization criteria."""
        mode_key_map = {"mild": "mild", "sinful": "sinful", "demonic": "demonic"}
        mode_key = mode_key_map[self.betmode]
        mode_multipliers = self.config.bucket_multipliers[mode_key]
        
        # Force wincap (max win)
        if self.criteria == "wincap" or getattr(self, 'force_wincap', False):
            # Force bucket 0 or 16 (max wins) - choose randomly
            return 0 if random.random() < 0.5 else 16
        
        # Force losses (0x or near-0x wins) - NOTE: These are MULTIPLIERS not win amounts
        if self.criteria == "losses":
            # Find buckets with lowest multipliers
            if mode_key == "mild":
                return 8  # 0.5x center bucket
            elif mode_key == "sinful":
                return 8  # 0.2x center bucket
            elif mode_key == "demonic":
                # Demonic has three 0x buckets (7, 8, 9)
                return random.choice([7, 8, 9])
        
        # For other criteria, find buckets within the MULTIPLIER range (not win amount range!)
        if self.criteria in ["high_wins", "medium_wins", "low_wins"]:
            target_buckets = []
            
            # Get MULTIPLIER range from criteria (not win amount!)
            mult_range = self.get_multiplier_range_for_criteria(self.criteria)
            
            if mult_range is not None:
                for bucket_idx, mult in enumerate(mode_multipliers):
                    if mult_range[0] <= mult <= mult_range[1]:
                        target_buckets.append(bucket_idx)
                
                if target_buckets:
                    return random.choice(target_buckets)
        
        # No forcing needed
        return None

    def get_multiplier_range_for_criteria(self, criteria):
        """Get MULTIPLIER range (not win amount) for a given criteria."""
        # These ranges MUST match game_optimization.py search_conditions EXACTLY!
        # Using EXCLUSIVE ranges to prevent bucket overlap
        if self.betmode == "mild":
            ranges = {
                "high_wins": (60.1, 150),     # EXCLUSIVE: >60, <=150
                "medium_wins": (8.1, 60),     # EXCLUSIVE: >8, <=60
                "low_wins": (0.51, 8),        # EXCLUSIVE: >0.5, <=8
            }
        elif self.betmode == "sinful":
            ranges = {
                "high_wins": (120.1, 400),    # EXCLUSIVE: >120, <=400
                "medium_wins": (12.1, 120),   # EXCLUSIVE: >12, <=120
                "low_wins": (0.21, 12),       # EXCLUSIVE: >0.2, <=12
            }
        elif self.betmode == "demonic":
            ranges = {
                "high_wins": (600.1, 2500),   # EXCLUSIVE: >600, <=2500
                "medium_wins": (40.1, 600),   # EXCLUSIVE: >40, <=600
                "low_wins": (0, 40),          # INCLUSIVE: >=0, <=40 (includes 0x losses!)
            }
        else:
            return None
        
        return ranges.get(criteria, None)
