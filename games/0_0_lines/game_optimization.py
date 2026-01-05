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
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.34, hr=120, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.5, rtp=0.59).return_dict(),
                },
                "scaling": ConstructScaling([
                    {
                        "criteria": "basegame",
                        "scale_factor": 4.8,        # heavily favor 1-2x wins
                        "win_range": (1.0, 2.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame", 
                        "scale_factor": 2.0,        # moderate favor 2-3x wins
                        "win_range": (2.0, 3.0),
                        "probability": 1.0,
                    },
                    {
                        "criteria": "basegame",
                        "scale_factor": 0.45,       # heavily punish sub-1x junk
                        "win_range": (0.0, 1.0),
                        "probability": 1.0,
                    },
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=2000,
                    num_per_fence=10000,
                    min_m2m=1,
                    max_m2m=20,
                    pmb_rtp=0.85,
                    sim_trials=2000,
                    test_spins=[100, 200, 500],
                    test_weights=[0.2, 0.3, 0.5],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.935, hr="x").return_dict(),
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
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.933, hr="x").return_dict(),
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
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
