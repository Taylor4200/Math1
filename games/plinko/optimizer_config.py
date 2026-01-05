"""Configuration for Perfect Plinko Optimizer - Hybrid approach for best results."""

class OptimizerConfig:
    """Configuration class for Plinko optimization targets."""
    
    def __init__(self):
        """Initialize optimization targets with hybrid approach - minimal constraints + strong scaling."""
        
        self.configs = {
            "mild": {
                "target_rtp": 0.9525,  # 4.75% house edge (center of range)
                "target_prob_less_bet": 0.374,  # Only bucket 8 is 0.5x
                "bucket_constraints": {
                    # Only constrain max wins - let rest be natural
                    0: {"hr": 50000},    # 666x - ULTRA RARE
                    16: {"hr": 50000},   # 666x - ULTRA RARE
                },
                "min_bucket_prob": 0.0001,  # All buckets must appear
                "scaling_preferences": {
                    "favor": [
                        # STRONG scaling to create natural gradients
                        {"multiplier_range": (0.5, 1.0), "weight": 40.0},    # Heavily favor sub-1x
                        {"multiplier_range": (1.0, 2.0), "weight": 80.0},    # VERY heavily favor 1-2x
                        {"multiplier_range": (2.0, 4.0), "weight": 40.0},    # Heavily favor 2-4x
                        {"multiplier_range": (4.0, 8.0), "weight": 20.0},    # Favor 4-8x
                        {"multiplier_range": (8.0, 20.0), "weight": 10.0},   # Moderate favor 8-20x
                        {"multiplier_range": (20.0, 60.0), "weight": 3.0},   # Light favor 20-60x
                    ],
                    "punish": [
                        {"multiplier_range": (60.0, 10000.0), "weight": 50.0},  # Punish ultra-high
                    ]
                }
            },
            
            "sinful": {
                "target_rtp": 0.9500,  # 5.00% house edge (0.25% from MILD)
                "target_prob_less_bet": 0.723,  # Buckets 7, 8, 9 are sub-1x
                "bucket_constraints": {
                    # Only constrain max wins
                    0: {"hr": 100000},   # 1666x - INSANELY RARE
                    16: {"hr": 100000},  # 1666x - INSANELY RARE
                },
                "min_bucket_prob": 0.0001,
                "scaling_preferences": {
                    "favor": [
                        # Create proper gradients
                        {"multiplier_range": (0.2, 0.5), "weight": 70.0},    # Heavily favor 0.2-0.5x
                        {"multiplier_range": (0.5, 2.0), "weight": 50.0},    # Favor near-1x
                        {"multiplier_range": (2.0, 4.0), "weight": 80.0},    # VERY heavily favor 2-4x
                        {"multiplier_range": (4.0, 12.0), "weight": 40.0},   # Heavily favor 4-12x
                        {"multiplier_range": (12.0, 40.0), "weight": 20.0},  # Favor 12-40x
                        {"multiplier_range": (40.0, 120.0), "weight": 5.0},  # Light favor 40-120x
                    ],
                    "punish": [
                        {"multiplier_range": (120.0, 10000.0), "weight": 100.0},  # Heavily punish ultra-high
                    ]
                }
            },
            
            "demonic": {
                "target_rtp": 0.9550,  # 4.50% house edge (0.25% from MILD, 0.50% from SINFUL)
                "target_prob_less_bet": 0.724,  # Buckets 7, 8, 9 are 0x
                "bucket_constraints": {
                    # Only constrain max wins
                    0: {"hr": 500000},   # 16666x - INSANELY RARE
                    16: {"hr": 500000},  # 16666x - INSANELY RARE
                },
                "min_bucket_prob": 0.0001,
                "scaling_preferences": {
                    "favor": [
                        # Bimodal - zeros + good wins
                        {"multiplier_range": (0, 0), "weight": 100.0},       # Heavily favor zeros
                        {"multiplier_range": (2.0, 8.0), "weight": 120.0},   # VERY heavily favor 2-8x
                        {"multiplier_range": (8.0, 40.0), "weight": 60.0},   # Heavily favor 8-40x
                        {"multiplier_range": (40.0, 150.0), "weight": 20.0}, # Favor 40-150x
                        {"multiplier_range": (150.0, 600.0), "weight": 5.0}, # Light favor 150-600x
                    ],
                    "punish": [
                        {"multiplier_range": (600.0, 20000.0), "weight": 150.0},  # VERY heavily punish ultra-high
                    ]
                }
            }
        }
    
    def get_config(self, mode: str):
        """Get configuration for a specific mode.
        
        Args:
            mode: One of 'mild', 'sinful', 'demonic'
            
        Returns:
            Configuration dictionary for the mode
        """
        if mode not in self.configs:
            raise ValueError(f"Unknown mode: {mode}. Must be one of: mild, sinful, demonic")
        return self.configs[mode]
    
    def get_all_modes(self):
        """Get list of all available modes."""
        return list(self.configs.keys())
    
    def update_target_rtp(self, mode: str, rtp: float):
        """Update target RTP for a mode."""
        if mode in self.configs:
            self.configs[mode]["target_rtp"] = rtp
    
    def update_prob_less_bet(self, mode: str, prob: float):
        """Update target prob_less_bet for a mode."""
        if mode in self.configs:
            self.configs[mode]["target_prob_less_bet"] = prob
    
    def update_bucket_hr(self, mode: str, bucket_idx: int, hr: float):
        """Update hit rate for a specific bucket."""
        if mode in self.configs:
            if "bucket_constraints" not in self.configs[mode]:
                self.configs[mode]["bucket_constraints"] = {}
            self.configs[mode]["bucket_constraints"][bucket_idx] = {"hr": hr}
    
    def remove_bucket_constraint(self, mode: str, bucket_idx: int):
        """Remove hit rate constraint for a specific bucket."""
        if mode in self.configs:
            if bucket_idx in self.configs[mode].get("bucket_constraints", {}):
                del self.configs[mode]["bucket_constraints"][bucket_idx]
