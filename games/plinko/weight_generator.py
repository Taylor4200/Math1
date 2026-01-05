"""Convert bucket probabilities to weighted CSV distributions."""

import numpy as np
from typing import List, Dict, Optional
import os


class WeightGenerator:
    """Generates weighted bucket distributions from probability arrays."""
    
    def __init__(self, total_weight: int = 100000):
        """Initialize weight generator.
        
        Args:
            total_weight: Total number of entries in the weighted distribution (default: 100,000)
        """
        self.total_weight = total_weight
    
    def probabilities_to_weights(self, probabilities: np.ndarray, 
                                  multipliers: Optional[np.ndarray] = None,
                                  target_rtp: Optional[float] = None) -> np.ndarray:
        """Convert probability array to integer weights with RTP preservation.
        
        Args:
            probabilities: Array of probabilities (must sum to 1.0)
            multipliers: Optional array of multipliers for RTP-aware rounding
            target_rtp: Optional target RTP to preserve
            
        Returns:
            Array of integer weights (sums to self.total_weight)
        """
        # Initial weights (floor to be conservative)
        weights = np.floor(probabilities * self.total_weight).astype(int)
        
        # Ensure minimum weight of 1 for any non-zero probability
        for i in range(len(weights)):
            if probabilities[i] > 0 and weights[i] == 0:
                weights[i] = 1
        
        # Calculate remaining weight to distribute
        current_total = np.sum(weights)
        remaining = self.total_weight - current_total
        
        if remaining > 0:
            # Calculate fractional parts for each bucket
            fractional_parts = (probabilities * self.total_weight) - weights
            
            # If we have multipliers and target RTP, use RTP-aware distribution
            if multipliers is not None and target_rtp is not None:
                # Calculate current RTP from weights
                current_probs = weights / self.total_weight
                current_rtp = np.sum(current_probs * multipliers)
                rtp_error = target_rtp - current_rtp
                
                # Prioritize adding to buckets that improve RTP
                if rtp_error > 0:
                    # Need to increase RTP - favor high multiplier buckets
                    priorities = fractional_parts * multipliers
                else:
                    # Need to decrease RTP - favor low multiplier buckets  
                    priorities = fractional_parts * (1.0 / (multipliers + 0.1))
                
                # Add remaining weights to highest priority buckets
                sorted_indices = np.argsort(priorities)[::-1]
                for i in range(remaining):
                    weights[sorted_indices[i]] += 1
            else:
                # No RTP info - just use largest fractional parts
                sorted_indices = np.argsort(fractional_parts)[::-1]
                for i in range(remaining):
                    weights[sorted_indices[i]] += 1
        
        elif remaining < 0:
            # Somehow we have too many - remove from lowest priority
            for i in range(abs(remaining)):
                # Find bucket with lowest fractional part and weight > 1
                sorted_indices = np.argsort(probabilities)
                for idx in sorted_indices:
                    if weights[idx] > 1:
                        weights[idx] -= 1
                        break
        
        return weights
    
    def refine_weights_for_rtp(self, weights: np.ndarray, multipliers: np.ndarray,
                               target_rtp: float, max_iterations: int = 1000,
                               tolerance: float = 0.0001) -> np.ndarray:
        """Iteratively refine weights to achieve exact target RTP.
        
        Args:
            weights: Initial integer weights
            multipliers: Bucket multipliers
            target_rtp: Target RTP to achieve
            max_iterations: Maximum refinement iterations
            tolerance: RTP error tolerance
            
        Returns:
            Refined weights with RTP closer to target
        """
        weights = weights.copy().astype(np.int64)
        total_weight = np.sum(weights)
        
        for iteration in range(max_iterations):
            # Calculate current RTP
            probs = weights / total_weight
            current_rtp = np.sum(probs * multipliers)
            rtp_error = target_rtp - current_rtp
            
            # Check if we're within tolerance
            if abs(rtp_error) < tolerance:
                break
            
            # ONE transfer per iteration for stability
            if rtp_error > 0:
                # Need to increase RTP
                # Find bucket with highest multiplier that has significant weight
                candidates = (weights > total_weight * 0.0001) & (multipliers > current_rtp)
                if np.any(candidates):
                    best_add_idx = np.argmax(multipliers * candidates)
                else:
                    # Just add to highest multiplier
                    best_add_idx = np.argmax(multipliers)
                
                # Find bucket with lowest multiplier that has excess weight
                candidates_sub = (weights > total_weight * 0.01) & (multipliers < current_rtp)
                if np.any(candidates_sub):
                    best_sub_idx = np.argmin(multipliers + 1000 * ~candidates_sub)
                else:
                    # Take from highest weight low multiplier
                    best_sub_idx = np.argmax(weights * (multipliers < 1.0))
                
                # Transfer ONE weight
                weights[best_sub_idx] -= 1
                weights[best_add_idx] += 1
            else:
                # Need to decrease RTP
                # Find bucket with lowest multiplier
                candidates = (weights > total_weight * 0.0001) & (multipliers < current_rtp)
                if np.any(candidates):
                    best_add_idx = np.argmin(multipliers + 1000 * ~candidates)
                else:
                    best_add_idx = np.argmin(multipliers)
                
                # Find bucket with highest multiplier that has excess weight
                candidates_sub = (weights > total_weight * 0.0001) & (multipliers > current_rtp)
                if np.any(candidates_sub):
                    best_sub_idx = np.argmax(multipliers * candidates_sub)
                else:
                    # Take from any high multiplier
                    best_sub_idx = np.argmax(multipliers * (weights > 10))
                
                # Transfer ONE weight
                if weights[best_sub_idx] > 10:
                    weights[best_sub_idx] -= 1
                    weights[best_add_idx] += 1
            
            total_weight = np.sum(weights)
        
        return weights
    
    def weights_to_csv(self, weights: np.ndarray, output_path: str):
        """Convert weights to CSV file with bucket indices.
        
        Args:
            weights: Array of weights for each bucket (index = bucket number)
            output_path: Path to save CSV file
        """
        bucket_list = []
        
        for bucket_idx, weight in enumerate(weights):
            bucket_list.extend([bucket_idx] * int(weight))
        
        # Shuffle for randomness (optional, but good practice)
        np.random.shuffle(bucket_list)
        
        # Write to CSV
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            for bucket in bucket_list:
                f.write(f"{bucket}\n")
    
    def verify_distribution(self, csv_path: str, expected_probabilities: np.ndarray, 
                           multipliers: List[float]) -> Dict:
        """Verify that a CSV distribution matches expected probabilities.
        
        Args:
            csv_path: Path to CSV file
            expected_probabilities: Expected probability array
            multipliers: Bucket multipliers for RTP calculation
            
        Returns:
            Dictionary with verification statistics
        """
        # Read CSV
        with open(csv_path, 'r') as f:
            buckets = [int(line.strip()) for line in f if line.strip()]
        
        total = len(buckets)
        actual_probs = np.zeros(len(expected_probabilities))
        
        # Calculate actual probabilities
        for bucket in buckets:
            actual_probs[bucket] += 1
        actual_probs /= total
        
        # Calculate RTP
        actual_rtp = np.sum(actual_probs * np.array(multipliers))
        expected_rtp = np.sum(expected_probabilities * np.array(multipliers))
        
        # Calculate prob_less_bet (multipliers < 1.0)
        actual_plb = np.sum(actual_probs[np.array(multipliers) < 1.0])
        expected_plb = np.sum(expected_probabilities[np.array(multipliers) < 1.0])
        
        # Calculate max differences
        max_prob_diff = np.max(np.abs(actual_probs - expected_probabilities))
        
        return {
            "total_weight": total,
            "actual_rtp": actual_rtp,
            "expected_rtp": expected_rtp,
            "rtp_error": abs(actual_rtp - expected_rtp),
            "actual_prob_less_bet": actual_plb,
            "expected_prob_less_bet": expected_plb,
            "plb_error": abs(actual_plb - expected_plb),
            "max_probability_error": max_prob_diff,
            "actual_probabilities": actual_probs,
            "expected_probabilities": expected_probabilities,
        }
    
    def calculate_hit_rates(self, probabilities: np.ndarray) -> Dict[int, float]:
        """Calculate hit rates (1 in X spins) from probabilities.
        
        Args:
            probabilities: Array of bucket probabilities
            
        Returns:
            Dictionary mapping bucket index to hit rate
        """
        hit_rates = {}
        for i, prob in enumerate(probabilities):
            if prob > 0:
                hit_rates[i] = 1.0 / prob
            else:
                hit_rates[i] = float('inf')
        return hit_rates

