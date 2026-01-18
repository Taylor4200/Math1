"""Game-specific configuration file, inherits from src/config/config.py"""

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
        self.game_id = "0_0_lines_v9"
        self.provider_number = 0
        self.working_name = "Sample Lines Game"
        self.wincap = 10000.0
        self.win_type = "lines"
        self.rtp = 0.9580
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties
        self.paytable = {
            (5, "W"): 50,
            (5, "H1"): 15,    # was 50
            (4, "H1"): 6,     # was 20
            (3, "H1"): 3,     # was 10
            (5, "H2"): 8,     # was 15
            (4, "H2"): 3,     # was 5
            (3, "H2"): 1.5,   # was 2.2
            (5, "H3"): 5,     # was 10
            (4, "H3"): 2,     # was 3
            (3, "H3"): 1,     # was 1.3
            (5, "L1"): 2,     # was 4
            (4, "L1"): 1.0,   # was 2.0
            (3, "L1"): 0.3,   # was 0.5
            (5, "L2"): 1.8,   # was 3.5
            (4, "L2"): 0.9,   # was 1.8
            (3, "L2"): 0.3,   # was 0.4
            (5, "L3"): 1.8,   # was 3.5
            (4, "L3"): 0.9,   # was 1.8
            (3, "L3"): 0.3,   # was 0.4
            (5, "L4"): 1.5,   # was 3
            (4, "L4"): 0.9,   # was 1.8
            (3, "L4"): 0.2,   # was 0.3
        }

        self.paylines = {
            1: [
                0,
                0,
                0,
                0,
                0,
            ],
            2: [
                1,
                1,
                1,
                1,
                1,
            ],
            3: [
                2,
                2,
                2,
                2,
                2,
            ],
            4: [
                3,
                3,
                3,
                3,
                3,
            ],
            5: [
                1,
                2,
                1,
                2,
                1,
            ],
            6: [
                2,
                1,
                2,
                1,
                2,
            ],
            7: [
                0,
                1,
                0,
                1,
                0,
            ],
            8: [
                1,
                0,
                1,
                0,
                1,
            ],
            9: [
                2,
                3,
                2,
                3,
                2,
            ],
            10: [
                3,
                2,
                3,
                2,
                3,
            ],
            11: [
                4,
                4,
                4,
                4,
                4,
            ],
            12: [
                3,
                4,
                3,
                4,
                3,
            ],
            13: [
                4,
                3,
                4,
                3,
                4,
            ],
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["W"],
                                "scatter": ["S"], 
                                "multiplier": ["W"]}

        # Fixed free spins structure
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12},  # Regular: 10, Super: 12
            self.freegame_type: {3: 10, 4: 12},  # Keep same triggers but scatters removed from reels
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(
                os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        self.padding_symbol_values = {"W": {"multiplier": {
            2: 100, 3: 80, 5: 60, 10: 40, 20: 20, 50: 10, 100: 5, 250: 1, 500: 0.5}}}

        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=0.9580,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.002,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2, 250: 0.2, 500: 0.05},
                                self.freegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2, 250: 0.5, 500: 0.1},
                            },
                            "scatter_triggers": {4: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.15,  # Regular bonus (3 scatters)
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100, 4: 0},  # ONLY 3 scatters -> 10 spins (regular bonus)
                                "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {2: 140, 3: 160, 5: 140, 10: 120, 20: 100, 50: 50, 100: 40, 250: 20, 500: 5},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="super_freegame",
                        quota=0.04,  # Super bonus (4 scatters)
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 0, 4: 100},  # ONLY 4 scatters -> 12 spins (super bonus)
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {20: 140, 50: 120, 100: 100, 250: 60, 500: 15},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.01,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01, 500: 0.002},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5, 500: 0.1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.798,  # Adjusted to sum quotas to 1.0 (0.002 + 0.15 + 0.04 + 0.01 + 0.798 = 1.0)
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01, 500: 0.002},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5, 500: 0.1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="Bonus",
                cost=100.0,
                rtp=0.9550,  # Adjusted to be within 0.5% of main RTP (95.8%)
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.002,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {2: 5, 3: 10, 5: 15, 10: 20, 20: 25, 50: 15, 100: 10, 250: 5, 500: 1},
                            },
                            "scatter_triggers": {4: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.999,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100, 4: 0},  # GUARANTEED 3 scatters = 10 spins
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {2: 140, 3: 160, 5: 140, 10: 120, 20: 100, 50: 50, 100: 40, 250: 20, 500: 5},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="Super Bonus",
                cost=500.0,
                rtp=0.9530,  # Adjusted to be within 0.5% of main RTP (95.8%)
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.002,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {20: 25, 50: 30, 100: 25, 250: 10, 500: 2},
                            },
                            "scatter_triggers": {4: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.999,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 0, 4: 100},  # GUARANTEED 4 scatters = 12 spins
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {20: 140, 50: 120, 100: 100, 250: 60, 500: 15},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="Bonus Booster",
                cost=2.0,  # 2x the user's bet
                rtp=0.9550,  # Higher RTP than base game
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,  # Changed to match working modes
                is_buybonus=True,  # Changed to match working modes
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.002,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {2: 5, 3: 10, 5: 15, 10: 20, 20: 25, 50: 15, 100: 10, 250: 5, 500: 1},
                            },
                            "scatter_triggers": {4: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame_boosted",
                        quota=0.20,  # Regular bonus (3 scatters) - boosted scatter chance
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100, 4: 0},  # ONLY 3 scatters -> 10 spins (regular bonus)
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {2: 140, 3: 160, 5: 140, 10: 120, 20: 100, 50: 50, 100: 40, 250: 20, 500: 5},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="super_freegame_boosted",
                        quota=0.04,  # Super bonus (4 scatters) - boosted scatter chance
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 0, 4: 100},  # ONLY 4 scatters -> 12 spins (super bonus)
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1, 500: 0.05},
                                self.freegame_type: {20: 140, 50: 120, 100: 100, 250: 60, 500: 15},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.01,  # Minimal nil wins
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01, 500: 0.002},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5, 500: 0.1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame_boosted",
                        quota=0.768,  # Adjusted to sum quotas to 1.0 (0.002 + 0.20 + 0.04 + 0.01 + 0.768 = 1.0)
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 10, 3: 15, 5: 30, 10: 25, 20: 15, 50: 3, 100: 1, 250: 0.1, 500: 0.02},
                                self.freegame_type: {1: 2, 2: 10, 3: 15, 5: 30, 10: 25, 20: 15, 50: 3, 100: 1, 250: 0.5, 500: 0.1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="Feature Spin",
                cost=20.0,
                rtp=0.955,  # 95.50% - matches Bonus Booster and Bonus
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="multiplier_feature",
                        quota=1.0,  # 100% - always trigger multiplier feature
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01, 500: 0.002},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5, 500: 0.1},
                            },
                            "force_min_wilds": 3,  # Guarantee at least 3 wilds appear
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="Super Feature Spin",
                cost=750.0,  # 750x the base bet
                rtp=0.955,  # 95.50% - matches Bonus Booster and Bonus
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="500x_multiplier_feature",
                        quota=1.0,  # 100% - always trigger 500x multiplier feature
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01, 500: 0.002},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5, 500: 0.1},
                            },
                            "force_min_multipliers": 1,  # Guarantee at least 1 multiplier symbol appears
                            "force_min_multiplier_value": 500,  # Guarantee at least 1 multiplier is 500x
                            "force_wincap": False,
                            "force_freegame": False,  # No free games in this mode
                            # No scatter_triggers - prevents bonus triggering
                        },
                    ),
                ],
            ),
        ]
