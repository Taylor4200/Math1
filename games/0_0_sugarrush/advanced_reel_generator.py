"""
Advanced Reel Generation Algorithm for Sugar Rush Game
Based on @slot-engine/core GeneratedReelSet algorithm with full feature support.

Features:
- Weighted random distribution
- Symbol quotas (percentage-based)
- Symbol stacking (configurable chance, min/max stack size)
- Spacing rules (same symbol spacing, symbol pair spacing)
- Symbol restrictions (limit symbols to specific reels)
- Stacking preference (percentage chance to prefer stacking)
- Seeded RNG for reproducibility
"""

import csv
import random
from typing import Dict, List, Optional, Tuple, Union
from collections import Counter


class SeededRNG:
    """Seeded Random Number Generator for reproducibility."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(0, 2**31 - 1)
        self.rng = random.Random(self.seed)
    
    def random_float(self, low: float = 0.0, high: float = 1.0) -> float:
        """Returns float in range [low, high)."""
        return self.rng.uniform(low, high)
    
    def random_int(self, low: int, high: int) -> int:
        """Returns integer in range [low, high] (inclusive)."""
        return self.rng.randint(low, high)
    
    def shuffle(self, array: List) -> None:
        """Fisher-Yates shuffle."""
        self.rng.shuffle(array)


class AdvancedReelGenerator:
    """
    Advanced reel generator with full feature support for Sugar Rush game.
    
    Supports:
    - Weighted random distribution
    - Symbol quotas (percentage-based per reel)
    - Symbol stacking (chance, min, max stack size)
    - Spacing rules (same symbol spacing, symbol pair spacing)
    - Symbol restrictions (limit symbols to specific reels)
    - Stacking preference (percentage chance to prefer stacking)
    """
    
    def __init__(
        self,
        num_reels: int = 7,
        num_rows: int = 250,
        symbol_weights: Dict[str, float] = None,
        symbol_quotas: Optional[Dict[str, Union[float, List[float]]]] = None,
        symbol_stacks: Optional[Dict[str, Dict]] = None,
        prefer_stacked_symbols: float = 0.0,  # 0-100 percentage
        space_between_same_symbols: Optional[Union[int, Dict[str, int]]] = None,  # 1-8
        space_between_symbols: Optional[Dict[str, Dict[str, int]]] = None,
        limit_symbols_to_reels: Optional[Dict[str, List[int]]] = None,
        seed: Optional[int] = None,
    ):
        """
        Initialize advanced reel generator.
        
        Args:
            num_reels: Number of reels (columns) - Sugar Rush: 7
            num_rows: Number of positions per reel (rows) - default: 250
            symbol_weights: Map of symbol IDs to weights (e.g., {"L1": 3.5, "H1": 0.8})
            symbol_quotas: Percentage quotas per reel (e.g., {"S": [3.0, 2.5, 2.0, ...]})
            symbol_stacks: Stacking config (e.g., {"H1": {"chance": 20, "min": 2, "max": 4}})
            prefer_stacked_symbols: Percentage chance to prefer stacking (0-100)
            space_between_same_symbols: Min distance between same symbols (1-8)
            space_between_symbols: Min distance between symbol pairs
            limit_symbols_to_reels: Restrict symbols to specific reels
            seed: Random seed for reproducibility
        """
        self.num_reels = num_reels
        self.num_rows = num_rows
        self.rng = SeededRNG(seed)
        
        # Sugar Rush symbols: H1, H2, H3, L1, L2, L3, L4, S
        if symbol_weights is None:
            # Default Sugar Rush weights
            self.symbol_weights = {
                "H1": 0.05,
                "H2": 0.06,
                "H3": 0.07,
                "L1": 0.26,
                "L2": 0.20,
                "L3": 0.18,
                "L4": 0.18,
                "S": 0.03,  # Scatter
            }
        else:
            self.symbol_weights = symbol_weights.copy()
        
        self.symbol_quotas = symbol_quotas or {}
        self.symbol_stacks = symbol_stacks or {}
        self.prefer_stacked_symbols = max(0.0, min(100.0, prefer_stacked_symbols))
        self.space_between_same_symbols = space_between_same_symbols
        self.space_between_symbols = space_between_symbols or {}
        self.limit_symbols_to_reels = limit_symbols_to_reels or {}
        
        # Validate spacing values
        if isinstance(self.space_between_same_symbols, int):
            if not (1 <= self.space_between_same_symbols <= 8):
                raise ValueError("space_between_same_symbols must be between 1 and 8")
        elif isinstance(self.space_between_same_symbols, dict):
            for sym, spacing in self.space_between_same_symbols.items():
                if not (1 <= spacing <= 8):
                    raise ValueError(f"Spacing for {sym} must be between 1 and 8")
    
    def weighted_random(self, weights: Dict[str, float]) -> str:
        """Select symbol using weighted random distribution."""
        total_weight = sum(weights.values())
        if total_weight == 0:
            raise ValueError("Total weight cannot be zero")
        
        random_value = self.rng.random_float(0.0, total_weight)
        cumulative_weight = 0.0
        
        for symbol_id, weight in weights.items():
            cumulative_weight += weight
            if random_value < cumulative_weight:
                return symbol_id
        
        # Fallback to last symbol
        return list(weights.keys())[-1]
    
    def circular_distance(self, pos1: int, pos2: int, reel_length: int) -> int:
        """Calculate circular distance between two positions."""
        diff = abs(pos1 - pos2)
        return min(diff, reel_length - diff)
    
    def violates_spacing(self, reel: List[Optional[str]], symbol_id: str, target_index: int) -> bool:
        """Check if placing symbol at target_index violates spacing rules."""
        for i, existing_symbol in enumerate(reel):
            if existing_symbol is None:
                continue
            
            dist = self.circular_distance(target_index, i, len(reel))
            
            # Check same symbol spacing
            same_spacing = None
            if isinstance(self.space_between_same_symbols, int):
                same_spacing = self.space_between_same_symbols
            elif isinstance(self.space_between_same_symbols, dict):
                same_spacing = self.space_between_same_symbols.get(symbol_id)
            
            if same_spacing is not None and same_spacing >= 1:
                if existing_symbol == symbol_id and dist <= same_spacing:
                    return True
            
            # Check symbol pair spacing
            if self.space_between_symbols:
                forward = self.space_between_symbols.get(symbol_id, {}).get(existing_symbol, 0)
                if forward >= 1 and dist <= forward:
                    return True
                
                reverse = self.space_between_symbols.get(existing_symbol, {}).get(symbol_id, 0)
                if reverse >= 1 and dist <= reverse:
                    return True
        
        return False
    
    def is_symbol_allowed(self, symbol_id: str, reel_idx: int) -> bool:
        """Check if symbol is allowed on this reel."""
        if not self.limit_symbols_to_reels:
            return True
        
        allowed_reels = self.limit_symbols_to_reels.get(symbol_id)
        if allowed_reels is None or len(allowed_reels) == 0:
            return True
        
        return reel_idx in allowed_reels
    
    def resolve_stacking(self, symbol_id: str, reel_idx: int) -> Optional[Dict]:
        """Resolve stacking configuration for symbol on reel."""
        cfg = self.symbol_stacks.get(symbol_id)
        if cfg is None:
            return None
        
        chance = cfg.get("chance")
        if isinstance(chance, list):
            chance = chance[reel_idx] if reel_idx < len(chance) else chance[0] if chance else 0
        chance = chance or 0
        
        if chance <= 0:
            return None
        
        min_size = cfg.get("min", 1)
        if isinstance(min_size, list):
            min_size = min_size[reel_idx] if reel_idx < len(min_size) else min_size[0] if min_size else 1
        
        max_size = cfg.get("max", 4)
        if isinstance(max_size, list):
            max_size = max_size[reel_idx] if reel_idx < len(max_size) else max_size[0] if max_size else 4
        
        return {"chance": chance, "min": min_size, "max": max_size}
    
    def try_place_stack(
        self, 
        reel: List[Optional[str]], 
        symbol_id: str, 
        start_index: int, 
        max_stack: int,
        reel_idx: int
    ) -> int:
        """Try to place a stack of symbols starting at start_index."""
        if not self.is_symbol_allowed(symbol_id, reel_idx):
            return 0
        
        can_place = 0
        for j in range(max_stack):
            idx = (start_index + j) % len(reel)
            if reel[idx] is not None:
                break
            can_place += 1
        
        if can_place == 0:
            return 0
        
        # Place the stack
        for j in range(can_place):
            idx = (start_index + j) % len(reel)
            reel[idx] = symbol_id
        
        return can_place
    
    def generate_reel(self, reel_idx: int) -> List[str]:
        """Generate a single reel with all features."""
        reel = [None] * self.num_rows
        
        # Phase 1: Handle symbol quotas
        reel_quotas = {}
        quota_counts = {}
        total_reels_quota = 0.0
        
        for symbol, quota in self.symbol_quotas.items():
            if isinstance(quota, list):
                quota_value = quota[reel_idx] if reel_idx < len(quota) else 0.0
            else:
                quota_value = quota
            
            if quota_value > 0:
                reel_quotas[symbol] = quota_value
                total_reels_quota += quota_value
        
        # Validate total quotas
        if total_reels_quota > 100.0:
            raise ValueError(f"Total quotas exceed 100% on reel {reel_idx}: {total_reels_quota}%")
        
        # Calculate actual counts needed
        if total_reels_quota > 0:
            for symbol, quota in reel_quotas.items():
                count = int(self.num_rows * quota / 100.0)
                quota_counts[symbol] = max(1, count)  # At least 1
        
        # Place quota symbols first
        for symbol, remaining in quota_counts.items():
            attempts = 0
            max_attempts = self.num_rows * 10
            
            while remaining > 0:
                if attempts >= max_attempts:
                    raise RuntimeError(
                        f"Failed to place quota symbols for {symbol} on reel {reel_idx} "
                        f"after {max_attempts} attempts. Spacing rules may be too strict."
                    )
                
                attempts += 1
                pos = self.rng.random_int(0, self.num_rows - 1)
                stack_cfg = self.resolve_stacking(symbol, reel_idx)
                
                placed = 0
                if stack_cfg and self.rng.random_int(1, 100) <= stack_cfg["chance"]:
                    stack_size = self.rng.random_int(stack_cfg["min"], stack_cfg["max"])
                    to_place = min(stack_size, remaining)
                    placed = self.try_place_stack(reel, symbol, pos, to_place, reel_idx)
                
                if placed == 0 and reel[pos] is None:
                    if self.is_symbol_allowed(symbol, reel_idx) and not self.violates_spacing(reel, symbol, pos):
                        reel[pos] = symbol
                        placed = 1
                
                remaining -= placed
        
        # Phase 2: Fill remaining positions
        for r in range(self.num_rows):
            if reel[r] is not None:
                continue  # Skip already filled positions
            
            # Step 1: Select symbol using weighted random
            chosen_symbol_id = self.weighted_random(self.symbol_weights)
            
            # Step 2: Check for stacking preference
            if self.prefer_stacked_symbols > 0:
                prev_symbol = reel[r - 1] if r > 0 else reel[self.num_rows - 1]  # Wrap around
                if prev_symbol is not None:
                    if self.rng.random_int(1, 100) <= self.prefer_stacked_symbols:
                        if not self.violates_spacing(reel, prev_symbol, r):
                            chosen_symbol_id = prev_symbol
            
            # Step 3: Try to place stack
            stack_cfg = self.resolve_stacking(chosen_symbol_id, reel_idx)
            if stack_cfg and self.is_symbol_allowed(chosen_symbol_id, reel_idx):
                roll = self.rng.random_int(1, 100)
                if roll <= stack_cfg["chance"]:
                    desired_size = self.rng.random_int(stack_cfg["min"], stack_cfg["max"])
                    placed = self.try_place_stack(reel, chosen_symbol_id, r, desired_size, reel_idx)
                    if placed > 0:
                        r += placed - 1  # Skip placed positions
                        continue
            
            # Step 4: Validate placement and retry if needed
            tries = 0
            max_tries = 2500
            
            while not self.is_symbol_allowed(chosen_symbol_id, reel_idx) or self.violates_spacing(reel, chosen_symbol_id, r):
                if tries >= max_tries:
                    raise RuntimeError(
                        f"Failed to place symbol on reel {reel_idx} at position {r} "
                        f"after {max_tries} attempts. Spacing rules may be too strict."
                    )
                
                tries += 1
                # Retry with new random symbol
                chosen_symbol_id = self.weighted_random(self.symbol_weights)
                
                # Re-check stacking preference
                if self.prefer_stacked_symbols > 0:
                    prev_symbol = reel[r - 1] if r > 0 else reel[self.num_rows - 1]
                    if prev_symbol is not None:
                        if self.rng.random_int(1, 100) <= self.prefer_stacked_symbols:
                            if not self.violates_spacing(reel, prev_symbol, r):
                                chosen_symbol_id = prev_symbol
            
            # Step 5: Place the symbol
            reel[r] = chosen_symbol_id
        
        # Validate all positions are filled
        if None in reel:
            raise RuntimeError(f"Reel {reel_idx} has unfilled positions")
        
        return reel
    
    def generate_reel_file(self, output_path: str) -> None:
        """Generate complete reel CSV file."""
        print(f"Generating reels: {output_path}")
        print(f"  Reels: {self.num_reels}, Rows per reel: {self.num_rows}")
        print(f"  Seed: {self.rng.seed}")
        
        # Generate all reels
        reel_strips = []
        for reel_idx in range(self.num_reels):
            print(f"  Generating reel {reel_idx + 1}/{self.num_reels}...", end="\r")
            reel = self.generate_reel(reel_idx)
            reel_strips.append(reel)
        print()  # New line after progress
        
        # Write CSV file (row-wise: each row contains one position from each reel)
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            for row_idx in range(self.num_rows):
                row = [reel_strips[reel_idx][row_idx] for reel_idx in range(self.num_reels)]
                writer.writerow(row)
        
        # Print statistics
        self._print_statistics(output_path, reel_strips)
    
    def _print_statistics(self, output_path: str, reel_strips: List[List[str]]) -> None:
        """Print statistics about the generated reel file."""
        all_symbols = []
        for strip in reel_strips:
            all_symbols.extend(strip)
        
        symbol_counts = Counter(all_symbols)
        total = len(all_symbols)
        
        print(f"\nGenerated: {output_path}")
        print(f"  Total positions: {total}")
        print(f"\n  Symbol distribution:")
        for symbol in sorted(symbol_counts.keys()):
            count = symbol_counts[symbol]
            percentage = (count / total) * 100
            print(f"    {symbol:8s}: {count:4d} ({percentage:5.2f}%)")
        
        # Per-reel statistics
        print(f"\n  Per-reel distribution:")
        for reel_idx, strip in enumerate(reel_strips):
            reel_counts = Counter(strip)
            print(f"    Reel {reel_idx + 1}:")
            for symbol in sorted(reel_counts.keys()):
                count = reel_counts[symbol]
                percentage = (count / len(strip)) * 100
                print(f"      {symbol:8s}: {count:4d} ({percentage:5.2f}%)")


def generate_sugar_rush_reels(
    basegame_config: Dict = None,
    freegame_config: Dict = None,
    seed: Optional[int] = None,
):
    """
    Generate Sugar Rush reel files with customizable configurations.
    
    Args:
        basegame_config: Configuration dict for base game reels
        freegame_config: Configuration dict for free game reels
        seed: Random seed for reproducibility
    """
    # Default base game configuration
    if basegame_config is None:
        basegame_config = {
            "symbol_weights": {
                "H1": 0.05,
                "H2": 0.06,
                "H3": 0.07,
                "L1": 0.26,
                "L2": 0.20,
                "L3": 0.18,
                "L4": 0.18,
                "S": 0.03,
            },
            "symbol_quotas": {
                "S": 3.0,  # 3% scatter quota per reel
            },
            "prefer_stacked_symbols": 0.0,  # No stacking preference
            "space_between_same_symbols": None,  # No spacing rules
        }
    
    # Default free game configuration
    if freegame_config is None:
        freegame_config = {
            "symbol_weights": {
                "H1": 0.08,
                "H2": 0.09,
                "H3": 0.10,
                "L1": 0.25,
                "L2": 0.20,
                "L3": 0.15,
                "L4": 0.13,
                "S": 0.025,
            },
            "symbol_quotas": {
                "S": 2.5,  # 2.5% scatter quota per reel (for retriggers)
            },
            "prefer_stacked_symbols": 0.0,
            "space_between_same_symbols": None,
        }
    
    # Generate base game reels
    print("=" * 70)
    print("GENERATING BASE GAME REELS (BR0.csv)")
    print("=" * 70)
    base_generator = AdvancedReelGenerator(
        num_reels=7,
        num_rows=250,
        seed=seed,
        **basegame_config
    )
    base_generator.generate_reel_file("reels/BR0.csv")
    
    # Generate free game reels
    print("\n" + "=" * 70)
    print("GENERATING FREE GAME REELS (FR0.csv)")
    print("=" * 70)
    free_generator = AdvancedReelGenerator(
        num_reels=7,
        num_rows=250,
        seed=seed,
        **freegame_config
    )
    free_generator.generate_reel_file("reels/FR0.csv")
    
    print("\n" + "=" * 70)
    print("ALL REEL FILES GENERATED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    # Example: Generate with default settings
    generate_sugar_rush_reels(seed=42)
    
    # Example: Generate with custom configuration
    # custom_base = {
    #     "symbol_weights": {
    #         "H1": 0.06,
    #         "H2": 0.07,
    #         "H3": 0.08,
    #         "L1": 0.25,
    #         "L2": 0.20,
    #         "L3": 0.18,
    #         "L4": 0.16,
    #         "S": 0.03,
    #     },
    #     "symbol_quotas": {"S": 3.0},
    #     "symbol_stacks": {
    #         "H1": {"chance": 20, "min": 2, "max": 4},  # 20% chance to stack H1, 2-4 symbols
    #     },
    #     "prefer_stacked_symbols": 15.0,  # 15% chance to prefer stacking
    #     "space_between_same_symbols": 2,  # Min 2 positions between same symbols
    # }
    # generate_sugar_rush_reels(basegame_config=custom_base, seed=42)

