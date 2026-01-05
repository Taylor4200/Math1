"""
Generate balanced reel CSV files for any number of rows and reels.
Automatically balances symbols across reels for proper game distribution.
"""

import csv
import random
from collections import Counter
from typing import Dict, List, Tuple


class ReelGenerator:
    """Generate balanced reel CSV files with configurable parameters."""
    
    def __init__(
        self,
        num_reels: int = 7,
        num_rows: int = 250,
        symbols: List[str] = None,
        symbol_weights: Dict[str, float] = None,
        scatter_weight: float = 0.02,
        multiplier_weight: float = 0.03,
    ):
        """
        Initialize reel generator.
        
        Args:
            num_reels: Number of reels (columns)
            num_rows: Number of positions per reel (rows)
            symbols: List of base symbols (H1-H4, L1-L5). If None, uses default Gates of Olympus symbols
            symbol_weights: Relative weights for each symbol. If None, auto-balances
            scatter_weight: Probability of scatter (S) per position
            multiplier_weight: Total probability of multiplier symbol (M) per position
        """
        self.num_reels = num_reels
        self.num_rows = num_rows
        self.total_positions = num_reels * num_rows
        
        # Default symbols if not provided
        if symbols is None:
            self.symbols = ["H1", "H2", "H3", "L1", "L2", "L3", "L4"]
        else:
            self.symbols = symbols
        
        # Multiplier symbol (single M symbol)
        self.multiplier_symbol = "M"
        self.scatter_symbol = "S"
        
        # Calculate symbol weights if not provided
        if symbol_weights is None:
            # Auto-balance: More low symbols than high symbols
            # High symbols get lower weights (rarer), low symbols get higher weights (common)
            self.symbol_weights = {
                "H1": 0.05,  # Rarest high
                "H2": 0.06,
                "H3": 0.07,
                "L1": 0.28,  # Most common low
                "L2": 0.24,
                "L3": 0.18,
                "L4": 0.12,
            }
        else:
            self.symbol_weights = symbol_weights
        
        # Normalize weights to account for scatter and multipliers
        base_weight_sum = sum(self.symbol_weights.values())
        self.scatter_weight = scatter_weight
        self.multiplier_weight = multiplier_weight
        
        # Adjust base symbol weights to leave room for special symbols
        available_weight = 1.0 - scatter_weight - multiplier_weight
        for symbol in self.symbol_weights:
            self.symbol_weights[symbol] = (self.symbol_weights[symbol] / base_weight_sum) * available_weight
    
    def generate_reel_strip(self, reel_index: int = 0) -> List[str]:
        """
        Generate a single reel strip.
        
        Args:
            reel_index: Index of the reel (0-based) - can be used for reel-specific weighting
            
        Returns:
            List of symbols for this reel strip
        """
        reel = []
        
        # Calculate target counts for each symbol type
        symbol_counts = {}
        for symbol in self.symbols:
            count = int(self.symbol_weights[symbol] * self.num_rows)
            symbol_counts[symbol] = count
            reel.extend([symbol] * count)
        
        # Add scatter symbols
        scatter_count = int(self.scatter_weight * self.num_rows)
        reel.extend([self.scatter_symbol] * scatter_count)
        
        # Add multiplier symbols (single M symbol)
        multiplier_count = int(self.multiplier_weight * self.num_rows)
        reel.extend([self.multiplier_symbol] * multiplier_count)
        
        # Adjust for rounding errors - fill with most common low symbol
        while len(reel) < self.num_rows:
            reel.append("L1")
        
        # Trim if slightly over
        while len(reel) > self.num_rows:
            # Remove from most common symbol type
            if reel.count("L1") > 0:
                reel.remove("L1")
            elif reel.count("L2") > 0:
                reel.remove("L2")
            else:
                reel.pop()
        
        # Shuffle for randomness while maintaining distribution
        random.shuffle(reel)
        
        return reel
    
    def generate_reel_file(
        self,
        output_path: str,
        reel_type: str = "basegame",
        balance_across_reels: bool = True,
    ) -> None:
        """
        Generate a complete reel CSV file.
        
        Args:
            output_path: Path to output CSV file
            reel_type: Type of reel (basegame, freegame, etc.) - can affect distribution
            balance_across_reels: If True, ensures symbols are balanced across all reels
        """
        # Generate strips for each reel
        reel_strips = []
        for i in range(self.num_reels):
            strip = self.generate_reel_strip(i)
            reel_strips.append(strip)
        
        # Balance across reels if requested
        if balance_across_reels:
            self._balance_across_reels(reel_strips)
        
        # Write CSV file (row-wise: each row contains one position from each reel)
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            for row_idx in range(self.num_rows):
                row = [reel_strips[reel_idx][row_idx] for reel_idx in range(self.num_reels)]
                writer.writerow(row)
        
        # Print statistics
        self._print_statistics(output_path, reel_strips)
    
    def _balance_across_reels(self, reel_strips: List[List[str]]) -> None:
        """
        Balance symbol distribution across all reels to ensure fairness.
        
        Args:
            reel_strips: List of reel strips to balance
        """
        # Count symbols across all reels
        all_symbols = []
        for strip in reel_strips:
            all_symbols.extend(strip)
        
        symbol_counts = Counter(all_symbols)
        total_symbols = len(all_symbols)
        
        # Calculate target distribution
        target_counts = {}
        for symbol in self.symbols:
            target_counts[symbol] = int(self.symbol_weights[symbol] * total_symbols)
        target_counts[self.scatter_symbol] = int(self.scatter_weight * total_symbols)
        target_counts[self.multiplier_symbol] = int(self.multiplier_weight * total_symbols)
        
        # Create balanced symbol pool
        balanced_pool = []
        for symbol, count in target_counts.items():
            balanced_pool.extend([symbol] * count)
        
        # Fill any remaining slots with most common low symbols
        while len(balanced_pool) < total_symbols:
            balanced_pool.append("L1")
        
        # Trim if over
        while len(balanced_pool) > total_symbols:
            balanced_pool.pop()
        
        # Shuffle
        random.shuffle(balanced_pool)
        
        # Distribute across reels
        for reel_idx in range(self.num_reels):
            start_idx = reel_idx * self.num_rows
            end_idx = start_idx + self.num_rows
            reel_strips[reel_idx] = balanced_pool[start_idx:end_idx]
    
    def _print_statistics(self, output_path: str, reel_strips: List[List[str]]) -> None:
        """Print statistics about the generated reel file."""
        all_symbols = []
        for strip in reel_strips:
            all_symbols.extend(strip)
        
        symbol_counts = Counter(all_symbols)
        total = len(all_symbols)
        
        print(f"\nGenerated: {output_path}")
        print(f"  Reels: {self.num_reels}, Rows per reel: {self.num_rows}")
        print(f"  Total positions: {total}")
        print("\n  Symbol distribution:")
        for symbol in sorted(symbol_counts.keys()):
            count = symbol_counts[symbol]
            percentage = (count / total) * 100
            print(f"    {symbol:8s}: {count:4d} ({percentage:5.2f}%)")


def generate_gates_of_olympus_reels(include_wincap: bool = False):
    """
    Generate reel files specifically for Gates of Olympus style game.
    
    Game dimensions: 6 reels × 5 rows visible
    Symbols: H1, H2, H3, L1, L2, L3, L4
    Multiplier: Single M symbol

    Args:
        include_wincap: If True, also regenerate FRWCAP.csv. Leave False to keep the
            hand-crafted wincap reel (recommended so forced max-win criteria still pass).
    """
    
    # Base game reels (BR0.csv) - low symbols dominate, scatters slightly more common than multipliers
    print("Generating base game reels (BR0.csv)...")
    base_generator = ReelGenerator(
        num_reels=6,  # 6 reels
        num_rows=250,  # 250 positions per reel
        symbol_weights={
            "H1": 0.05,
            "H2": 0.06,
            "H3": 0.07,
            "L1": 0.28,
            "L2": 0.24,
            "L3": 0.18,
            "L4": 0.12,
        },
        scatter_weight=0.03,   # Slightly more scatters than multipliers in base game
        multiplier_weight=0.015,
    )
    base_generator.generate_reel_file("reels/BR0.csv", reel_type="basegame")
    
    # Free game reels (FR0.csv) - still low-heavy but with richer scatter/multiplier mix
    print("\nGenerating free game reels (FR0.csv)...")
    free_generator = ReelGenerator(
        num_reels=6,  # 6 reels
        num_rows=250,  # 250 positions per reel
        symbol_weights={
            "H1": 0.07,
            "H2": 0.08,
            "H3": 0.09,
            "L1": 0.28,
            "L2": 0.22,
            "L3": 0.16,
            "L4": 0.10,
        },
        scatter_weight=0.025,  # Higher scatter for retriggers
        multiplier_weight=0.05,  # More multipliers in free games
    )
    free_generator.generate_reel_file("reels/FR0.csv", reel_type="freegame")
    
    if include_wincap:
        print("\nGenerating win cap reels (FRWCAP.csv)...")  # Keeps lows plentiful while weighting wins upward
        wincap_generator = ReelGenerator(
            num_reels=6,  # 6 reels
            num_rows=250,  # 250 positions per reel
            symbol_weights={
                "H1": 0.08,
                "H2": 0.09,
                "H3": 0.10,
                "L1": 0.30,
                "L2": 0.22,
                "L3": 0.15,
                "L4": 0.06,
            },
            scatter_weight=0.01,
            multiplier_weight=0.08,  # High-value mode still keeps multipliers rarer than low symbols
        )
        wincap_generator.generate_reel_file("reels/FRWCAP.csv", reel_type="wincap")
    else:
        print("\nSkipping FRWCAP.csv (using curated max-win reel).")
    
    print("\nAll reel files generated successfully!")
    print("\nNote: These are balanced starter reels. Run optimization to fine-tune for target RTP.")


if __name__ == "__main__":
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    # Generate Gates of Olympus style reels
    generate_gates_of_olympus_reels()
    
    # Example: Generate custom reels with different parameters
    # generator = ReelGenerator(num_reels=5, num_rows=200)
    # generator.generate_reel_file("reels/CUSTOM.csv")

