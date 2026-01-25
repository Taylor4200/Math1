"""
Generate balanced reel CSV files for 0_0_lines_v9 (6 reels, 6 rows).
Automatically balances symbols across reels for proper game distribution.
"""

import csv
import random
from collections import Counter
from typing import Dict, List


class ReelGenerator:
    """Generate balanced reel CSV files with configurable parameters."""
    
    def __init__(
        self,
        num_reels: int = 6,
        num_rows: int = 220,
        symbols: List[str] = None,
        symbol_weights: Dict[str, float] = None,
        scatter_weight: float = 0.02,
        wild_weight: float = 0.03,
    ):
        """
        Initialize reel generator.
        
        Args:
            num_reels: Number of reels (columns)
            num_rows: Number of positions per reel (rows)
            symbols: List of base symbols
            symbol_weights: Relative weights for each symbol. If None, auto-balances
            scatter_weight: Probability of scatter (S) per position
            wild_weight: Probability of wild (W) per position
        """
        self.num_reels = num_reels
        self.num_rows = num_rows
        self.total_positions = num_reels * num_rows
        
        # Default symbols if not provided
        if symbols is None:
            self.symbols = ["H1", "H2", "H3", "L1", "L2", "L3", "L4"]
        else:
            self.symbols = symbols
        
        # Wild and scatter symbols
        self.wild_symbol = "W"
        self.scatter_symbol = "S"
        
        # Calculate symbol weights if not provided
        if symbol_weights is None:
            # Auto-balance: More low symbols than high symbols
            self.symbol_weights = {
                "H1": 0.05,
                "H2": 0.06,
                "H3": 0.07,
                "L1": 0.26,
                "L2": 0.20,
                "L3": 0.18,
                "L4": 0.18,
            }
        else:
            self.symbol_weights = symbol_weights
        
        # Normalize weights to account for scatter and wilds
        base_weight_sum = sum(self.symbol_weights.values())
        self.scatter_weight = scatter_weight
        self.wild_weight = wild_weight
        
        # Adjust base symbol weights to leave room for special symbols
        available_weight = 1.0 - scatter_weight - wild_weight
        for symbol in self.symbol_weights:
            self.symbol_weights[symbol] = (self.symbol_weights[symbol] / base_weight_sum) * available_weight
    
    def generate_reel_strip(self, reel_index: int = 0) -> List[str]:
        """
        Generate a single reel strip.
        
        Args:
            reel_index: Index of the reel (0-based)
            
        Returns:
            List of symbols for this reel strip
        """
        reel = []
        
        # Calculate target counts for each symbol type
        for symbol in self.symbols:
            count = int(self.symbol_weights[symbol] * self.num_rows)
            reel.extend([symbol] * count)
        
        # Add scatter symbols
        scatter_count = int(self.scatter_weight * self.num_rows)
        reel.extend([self.scatter_symbol] * scatter_count)
        
        # Add wild symbols
        wild_count = int(self.wild_weight * self.num_rows)
        reel.extend([self.wild_symbol] * wild_count)
        
        # Adjust for rounding errors - fill with most common low symbol
        while len(reel) < self.num_rows:
            reel.append("L1")
        
        # Trim if slightly over
        while len(reel) > self.num_rows:
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
            reel_type: Type of reel (basegame, freegame, etc.)
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
        """Balance symbol distribution across all reels to ensure fairness."""
        # Count symbols across all reels
        all_symbols = []
        for strip in reel_strips:
            all_symbols.extend(strip)
        
        total_symbols = len(all_symbols)
        
        # Calculate target distribution
        target_counts = {}
        for symbol in self.symbols:
            target_counts[symbol] = int(self.symbol_weights[symbol] * total_symbols)
        target_counts[self.scatter_symbol] = int(self.scatter_weight * total_symbols)
        target_counts[self.wild_symbol] = int(self.wild_weight * total_symbols)
        
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


def generate_lines_v9_reels(include_wincap: bool = True):
    """
    Generate reel files specifically for 0_0_lines_v9 (6x6 board with sticky wilds).
    
    Args:
        include_wincap: If True, also regenerate FRWCAP.csv
    """
    
    # Base game reels (BR0.csv)
    print("Generating base game reels (BR0.csv)...")
    base_generator = ReelGenerator(
        num_reels=6,
        num_rows=220,
        scatter_weight=0.018,  # Scatters for bonus trigger
        wild_weight=0.025,     # Wilds with multipliers
    )
    base_generator.generate_reel_file("reels/BR0.csv", reel_type="basegame")
    
    # Free game reels (FR0.csv) - no scatters, more wilds
    print("\nGenerating free game reels (FR0.csv)...")
    free_generator = ReelGenerator(
        num_reels=6,
        num_rows=220,
        symbol_weights={
            "H1": 0.08,
            "H2": 0.09,
            "H3": 0.10,
            "L1": 0.25,
            "L2": 0.20,
            "L3": 0.15,
            "L4": 0.13,
        },
        scatter_weight=0.0,    # No scatters in free games
        wild_weight=0.045,     # More wilds in free games (they stick!)
    )
    free_generator.generate_reel_file("reels/FR0.csv", reel_type="freegame")
    
    if include_wincap:
        print("\nGenerating win cap reels (FRWCAP.csv)...")
        wincap_generator = ReelGenerator(
            num_reels=6,
            num_rows=100,  # Shorter for wincap scenarios
            symbol_weights={
                "H1": 0.12,
                "H2": 0.13,
                "H3": 0.14,
                "L1": 0.22,
                "L2": 0.16,
                "L3": 0.13,
                "L4": 0.10,
            },
            scatter_weight=0.0,
            wild_weight=0.15,  # Many wilds for high multiplier scenarios
        )
        wincap_generator.generate_reel_file("reels/FRWCAP.csv", reel_type="wincap")
    
    print("\nAll reel files generated successfully!")
    print("\nNote: These are balanced starter reels. Run optimization to fine-tune for target RTP.")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate 0_0_lines_v9 reels (6x6 board)
    generate_lines_v9_reels()



