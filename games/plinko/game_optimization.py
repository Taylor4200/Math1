"""Set conditions/parameters for optimization program - GOOD gameplay-focused settings."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """Optimization configuration for Hell's Plinko - 3 volatility modes."""

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "mild": {
                "conditions": {
                    # Allocate 96% RTP across categories with GOOD hit rates
                    "wincap": ConstructConditions(
                        rtp=0.1332,  # 13.32% RTP from 666x (1 in 2,500 total - COMMON for MILD!)
                        hr=5000,  # 1 in 5,000 per bucket = 1 in 2,500 total
                        av_win=666,
                        search_conditions=666
                    ).return_dict(),
                    "high_wins": ConstructConditions(
                        rtp=0.05,  # 5% RTP from big wins (reduced to balance wincap)
                        hr=1200,  # hr = 60 / 0.05 = 1200
                        av_win=60,
                        search_conditions=(60.1, 150)  # Exclusive: >60, <=150
                    ).return_dict(),
                    "medium_wins": ConstructConditions(
                        rtp=0.15,  # 15% RTP from medium wins (reduced)
                        hr=133,  # hr = 20 / 0.15 = 133
                        av_win=20,
                        search_conditions=(8.1, 60)  # Exclusive: >8, <=60
                    ).return_dict(),
                    "low_wins": ConstructConditions(
                        rtp=0.5968,  # 59.68% RTP from low wins (to hit EXACT 96% total)
                        hr=3.35,  # hr = 2 / 0.5968 = 3.35
                        av_win=2,
                        search_conditions=(0.51, 8)  # Exclusive: >0.5, <=8
                    ).return_dict(),
                    "losses": ConstructConditions(
                        rtp=0.03,  # 3% RTP from sub-0.5x
                        hr=8.33,  # hr = 0.25 / 0.03 = 8.33
                        av_win=0.25,
                        search_conditions=(0, 0.5)  # Exclusive: >=0, <=0.5
                    ).return_dict(),
                    # Total: 13.32 + 5 + 15 + 59.68 + 3 = 96.0% RTP (4.0% house edge)
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "low_wins",
                        "scale_factor": 5.0,  # Heavily favor 1-2x wins
                        "win_range": (1.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "low_wins",
                        "scale_factor": 3.0,  # Favor 2-4x wins
                        "win_range": (2.0, 4.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "medium_wins",
                        "scale_factor": 3.0,  # Favor 8-20x wins
                        "win_range": (8, 20),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "medium_wins",
                        "scale_factor": 2.0,  # Favor 20-60x wins
                        "win_range": (20, 60),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=15,
                    pmb_rtp=0.75,  # Target: <75% prob_less_bet (well under 0.8)
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "sinful": {
                "conditions": {
                    # Allocate 95.5% RTP across categories (4.5% house edge - EXACTLY 0.5% from MILD)
                    "wincap": ConstructConditions(
                        rtp=0.03332,  # 3.332% RTP from 1666x (1 in 25k total - RARER than MILD!)
                        hr=50000,  # 1 in 50,000 per bucket = 1 in 25,000 total
                        av_win=1666,
                        search_conditions=1666
                    ).return_dict(),
                    "high_wins": ConstructConditions(
                        rtp=0.05,  # 5% RTP from big wins
                        hr=2400,  # hr = 120 / 0.05 = 2400
                        av_win=120,
                        search_conditions=(120.1, 400)  # Exclusive: >120, <=400
                    ).return_dict(),
                    "medium_wins": ConstructConditions(
                        rtp=0.15,  # 15% RTP from medium wins
                        hr=267,  # hr = 40 / 0.15 = 267
                        av_win=40,
                        search_conditions=(12.1, 120)  # Exclusive: >12, <=120
                    ).return_dict(),
                    "low_wins": ConstructConditions(
                        rtp=0.69168,  # 69.168% RTP from low wins (to hit EXACT 95.5% total)
                        hr=2.9,  # hr = 2 / 0.69168 = 2.9
                        av_win=2,
                        search_conditions=(0.21, 12)  # Exclusive: >0.2, <=12
                    ).return_dict(),
                    "losses": ConstructConditions(
                        rtp=0.03,  # 3% RTP from sub-0.2x
                        hr=3.33,  # hr = 0.1 / 0.03 = 3.33
                        av_win=0.1,
                        search_conditions=(0, 0.2)  # Exclusive: >=0, <=0.2
                    ).return_dict(),
                    # Total: 3.332 + 5 + 15 + 69.168 + 3 = 95.5% RTP (4.5% house edge)
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "low_wins",
                        "scale_factor": 4.0,  # Favor 2-4x wins
                        "win_range": (2.0, 4.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "low_wins",
                        "scale_factor": 2.5,  # Favor 4-12x wins
                        "win_range": (4.0, 12.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "medium_wins",
                        "scale_factor": 3.0,  # Favor 12-40x wins
                        "win_range": (12, 40),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "high_wins",
                        "scale_factor": 2.0,  # Favor 120-400x wins
                        "win_range": (120, 400),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=20,
                    pmb_rtp=0.78,  # Target: <78% prob_less_bet (under 0.8)
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "demonic": {
                "conditions": {
                    # Allocate 95.0% RTP across categories (5.0% house edge - EXACTLY 0.5% from SINFUL)
                    "wincap": ConstructConditions(
                        rtp=0.033332,  # 3.33% RTP from 16666x (EXACT: 16666/500000)
                        hr=500000,  # EXACTLY 1 in 500,000 per bucket → 1 in 250k total!
                        av_win=16666,
                        search_conditions=16666
                    ).return_dict(),
                    "high_wins": ConstructConditions(
                        rtp=0.02,  # 2% RTP from big wins (600x-2500x EXCLUSIVE)
                        hr=30000,  # hr = 600 / 0.02 = 30,000
                        av_win=600,
                        search_conditions=(600.1, 2500)  # Exclusive: >600, <=2500
                    ).return_dict(),
                    "medium_wins": ConstructConditions(
                        rtp=0.12,  # 12% RTP from medium wins (40x-600x EXCLUSIVE)
                        hr=1250,  # hr = 150 / 0.12 = 1250
                        av_win=150,
                        search_conditions=(40.1, 600)  # Exclusive: >40, <=600
                    ).return_dict(),
                    "low_wins": ConstructConditions(
                        rtp=0.776668,  # 77.6668% RTP from low wins (includes 0x-40x)
                        hr=10.3,  # hr = 8 / 0.776668 = 10.3
                        av_win=8,
                        search_conditions=(0, 40)  # Exclusive: >=0, <=40 (includes 0x losses!)
                    ).return_dict(),
                    # Note: 0x buckets (7,8,9) are in low_wins
                    # Total: 3.3332 + 2 + 12 + 77.6668 = 95.0% RTP (5.0% house edge)
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "low_wins",
                        "scale_factor": 6.0,  # HEAVILY favor 2-8x wins
                        "win_range": (2.0, 8.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "low_wins",
                        "scale_factor": 3.0,  # Favor 8-40x wins
                        "win_range": (8.0, 40.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "medium_wins",
                        "scale_factor": 3.0,  # Favor 40-150x wins
                        "win_range": (40, 150),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "high_wins",
                        "scale_factor": 1.5,  # Moderate favor extreme wins
                        "win_range": (600, 2500),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2500,
                    num_per_fence=12000,
                    min_m2m=1,
                    max_m2m=30,
                    pmb_rtp=0.78,  # Target: <78% prob_less_bet (under 0.8)
                    sim_trials=2500,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
