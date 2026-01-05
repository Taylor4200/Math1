"""Game-specific configuration file for Hell's Plinko"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "plinko"
        self.provider_number = 0
        self.working_name = "Hell's Plinko"
        self.wincap = 16666.0  # Max win from DEMONIC mode (bucket 0 or 16)
        self.win_type = "plinko"
        self.rtp = 0.9600  # All modes now target 96% RTP
        self.construct_paths()

        # Plinko-specific properties - Per BACKEND_INTEGRATION_REQUIREMENT2.md
        self.num_buckets = 17
        self.bucket_multipliers = {
            # MILD: Max 666x (buckets 0 and 16) - From BACKEND_INTEGRATION_REQUIREMENT2.md
            "mild": [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666],
            # SINFUL: Max 1666x (buckets 0 and 16) - From BACKEND_INTEGRATION_REQUIREMENT2.md
            "sinful": [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666],
            # DEMONIC: Max 16666x (buckets 0 and 16) - From BACKEND_INTEGRATION_REQUIREMENT2.md
            "demonic": [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]
        }
        
        # Bonus peg removed - no respin functionality
        
        # Hells Storm multi-ball configuration
        # Maps mode name to (num_balls, base_mode) for multi-ball modes
        self.multi_ball_config = {
            "hells_storm_mild": {"num_balls": 66, "base_mode": "mild"},
            "hells_storm_sinful": {"num_balls": 66, "base_mode": "sinful"},
            "hells_storm_demonic": {"num_balls": 66, "base_mode": "demonic"},
        }

        # Plinko doesn't use symbols/paytables/reels, but parent class expects them
        self.paytable = {}
        self.special_symbols = {}
        self.num_reels = 1  # Dummy value for parent class
        self.num_rows = [1]  # Dummy value for parent class

        # Read bucket "reels" (probability distributions)
        reels = {
            "MILD": "MILD.csv",
            "SINFUL": "SINFUL.csv",
            "DEMONIC": "DEMONIC.csv"
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        # Define 3 bet modes for different volatility levels
        self.bet_modes = [
            BetMode(
                name="mild",
                cost=1.0,
                rtp=0.9600,  # 4.00% house edge - ALL modes at 96% RTP
                max_win=666.0,  # Buckets 0/16 in MILD mode
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=666.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": True,
                        },
                    ),
                    Distribution(
                        criteria="high_wins",
                        quota=0.049,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="medium_wins",
                        quota=0.20,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="low_wins",
                        quota=0.741,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="losses",
                        quota=0.009,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="sinful",
                cost=1.0,
                rtp=0.9600,  # 4.00% house edge - ALL modes at 96% RTP
                max_win=1666.0,  # Buckets 0/16 in SINFUL mode
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=1666.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": True,
                        },
                    ),
                    Distribution(
                        criteria="high_wins",
                        quota=0.04,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="medium_wins",
                        quota=0.18,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="low_wins",
                        quota=0.759,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="losses",
                        quota=0.02,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="demonic",
                cost=1.0,
                rtp=0.9600,  # 4.00% house edge - ALL modes at 96% RTP
                max_win=16666.0,  # Buckets 0/16 in DEMONIC mode
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.0005,
                        win_criteria=16666.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": True,
                        },
                    ),
                    Distribution(
                        criteria="high_wins",
                        quota=0.02,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="medium_wins",
                        quota=0.10,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="low_wins",
                        quota=0.8195,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                    Distribution(
                        criteria="losses",
                        quota=0.06,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
            # HELLS STORM MODES - 66 balls per spin
            # Configuration for multi-ball modes stored in self.multi_ball_config above
            BetMode(
                name="hells_storm_mild",
                cost=66.0,  # 66× base bet
                rtp=0.9600,  # Same RTP as MILD - ALL modes at 96% RTP
                max_win=666.0 * 66,  # 66 balls × max MILD multiplier = 43,956
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="all",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MILD": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="hells_storm_sinful",
                cost=66.0,  # 66× base bet
                rtp=0.9600,  # Same RTP as SINFUL - ALL modes at 96% RTP
                max_win=1666.0 * 66,  # 66 balls × max SINFUL multiplier = 109,956
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="all",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"SINFUL": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="hells_storm_demonic",
                cost=66.0,  # 66× base bet
                rtp=0.9600,  # Same RTP as DEMONIC - ALL modes at 96% RTP
                max_win=16666.0 * 66,  # 66 balls × max DEMONIC multiplier = 1,099,956
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="all",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"DEMONIC": 1},
                            },
                            "force_wincap": False,
                        },
                    ),
                ],
            ),
        ]
