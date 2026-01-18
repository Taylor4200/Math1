"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """"""

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=25000, search_conditions=25000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.45, hr=167, search_conditions={"symbol": "scatter"}  # ~45% RTP from freegame (reduced from 0.50)
                        # Freegame triggers ~1 in 167 spins (quota 0.006), so needs high RTP per trigger
                        # Adjusted hr from 145 to 167 to match new quota (1/0.006 ≈ 167)
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.0, rtp=0.45).return_dict(),  # ~45% RTP from basegame (reduced from 0.50, hr increased from 3.5 to 4.0)
                        # Less frequent wins (hr=4.0 vs 3.5) with lower RTP per win (0.45 vs 0.50) = reduced basegame contribution
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "basegame",
                        "scale_factor": 3.5,        # favor 1-2x wins (reduced from 4.8)
                        "win_range": (1.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame", 
                        "scale_factor": 1.5,        # moderate favor 2-3x wins (reduced from 2.0)
                        "win_range": (2.0, 3.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 0.5,       # punish sub-1x junk (increased from 0.45 to allow more nil wins)
                        "win_range": (0.0, 1.0),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=20,
                    pmb_rtp=0.963,
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=25000, search_conditions=25000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.946, hr="x").return_dict(),  # Adjusted to 0.958 total (within 0.5% of base 0.963)
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 4.5,
                            "win_range": (100, 300),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 3.5,
                            "win_range": (300, 600),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.4,
                            "win_range": (30, 100),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.8,
                            "win_range": (600, 1000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                ).return_dict(),
            },
            "super_bonus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=25000, search_conditions=25000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.946, hr="x").return_dict(),  # Adjusted to 0.958 total (within 0.5% of base 0.963)
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 3.0,
                            "win_range": (5, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (20, 50),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 2.0,
                            "win_range": (50, 100),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.0,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.5,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus_booster": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=25000, search_conditions=25000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame_boosted": ConstructConditions(
                        rtp=0.45, hr=50, search_conditions={"symbol": "scatter"}  # ~45% RTP from freegames (2% trigger rate = 1 in 50 spins)
                        # Bonus booster: Higher trigger rate (2% vs 0.6%) means more frequent free spins
                    ).return_dict(),
                    "basegame_boosted": ConstructConditions(hr=3.5, rtp=0.51).return_dict(),  # ~51% RTP from basegame (targeting better balance)
                        # Adjusted for better basegame contribution (40-50% of total)
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 0.1,        # HEAVILY punish wins below 2.0 (below bet amount)
                        "win_range": (0.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted", 
                        "scale_factor": 8.0,        # HEAVILY favor wins above 2.0 (above bet amount)
                        "win_range": (2.0, 10.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 4.0,       # favor larger wins
                        "win_range": (10.0, 100.0),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=20,
                    pmb_rtp=1.0,  # Allow higher RTP ceiling for buybonus
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "multiplierfeature": {
                "conditions": {
                    "multiplier_feature": ConstructConditions(rtp=0.963, hr="x").return_dict(),  # Matches base RTP exactly
                },
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=20,
                    pmb_rtp=0.96,
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
        }
