https://github.com/StakeEngine/math-sdk"""Set conditions/parameters for optimization program program"""

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
                    "wincap": ConstructConditions(rtp=0.02, av_win=10000, search_conditions=10000).return_dict(),
                    "basegame": ConstructConditions(rtp=0.943, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "basegame",
                        "scale_factor": 0.001,  # EXTREME penalty for 0-0.5x wins
                        "win_range": (0.0, 0.5),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 0.01,  # SEVERE penalty for 0.5-1x wins
                        "win_range": (0.5, 1.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 50.0,  # MASSIVE favor for 1-2x (bet back)
                        "win_range": (1.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 30.0,  # Big favor for 2-5x
                        "win_range": (2.0, 5.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 10.0,  # Favor for 5-20x
                        "win_range": (5.0, 20.0),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.963,
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "Wrath of Olympus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=10000, search_conditions=10000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.948, hr="x").return_dict(),  # Adjusted to achieve 96.0% total RTP
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
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.96,  # Updated to match target RTP of 96.0%
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                ).return_dict(),
            },
            "Super Wrath of Olympus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=10000, search_conditions=10000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.946, hr="x").return_dict(),  # Adjusted to achieve 95.8% total RTP
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
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.958,  # Updated to match target RTP of 95.8%
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus_booster": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.02, av_win=10000, search_conditions=10000).return_dict(),
                    "basegame_boosted": ConstructConditions(rtp=0.94, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 0.001,  # EXTREME penalty for 0-1x wins
                        "win_range": (0.0, 1.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 0.01,  # SEVERE penalty for 1-2x wins (still below bet)
                        "win_range": (1.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 50.0,  # MASSIVE favor for 2-4x (bet back)
                        "win_range": (2.0, 4.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 30.0,  # Big favor for 4-10x
                        "win_range": (4.0, 10.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame_boosted",
                        "scale_factor": 10.0,  # Favor for 10-40x
                        "win_range": (10.0, 40.0),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.96,
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "Divine Strikes": {
                "conditions": {
                    "multiplier_feature": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.96,
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "Divine Judgement": {
                "conditions": {
                    "divine_judgement": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": ConstructScaling([]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,       # Maximum candidates for best variance (like 0_0_cluster)
                    num_per_fence=10000,  # Maximum variety for maximum variance (like 0_0_cluster)
                    min_m2m=4,           # Tighter range for consistent variance (like 0_0_cluster)
                    max_m2m=8,            # Tighter range ensures better distribution spread
                    pmb_rtp=0.96,
                    sim_trials=5000,     # Maximum accuracy for tightest optimization (like 0_0_cluster)
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
        }
