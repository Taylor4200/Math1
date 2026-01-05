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
        self.game_id = "0_0_lines_v7"
        self.provider_number = 0
        self.working_name = "Gates of Olympus Style Game"
        self.wincap = 10000.0
        self.win_type = "scatter"
        self.rtp = 0.9630
        self.construct_paths()

        # Game Dimensions - Gates of Olympus style: 6 reels, 5 rows
        self.num_reels = 6
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties - Scatter pays (minimum 8 symbols)
        # Sweet Bonanza style: 3 premium candies, 4 fruit lows
        # Format: ((min_count, max_count), symbol_name): payout
        pay_group = {
            # Premium candies
            ((8, 9), "H1"): 10,
            ((10, 11), "H1"): 25,
            ((12, 30), "H1"): 50,

            ((8, 9), "H2"): 2.5,  # 2.5 * 100 = 250 cents (multiple of 10) ✓
            ((10, 11), "H2"): 10,
            ((12, 30), "H2"): 25,

            ((8, 9), "H3"): 2,
            ((10, 11), "H3"): 5,
            ((12, 30), "H3"): 15,

            # Fruits
            ((8, 9), "L1"): 0.8,  # 0.8 * 100 = 80 cents (multiple of 10) ✓
            ((10, 11), "L1"): 1.2,  # 1.2 * 100 = 120 cents (multiple of 10) ✓
            ((12, 30), "L1"): 8,

            ((8, 9), "L2"): 0.5,  # 0.5 * 100 = 50 cents (multiple of 10) ✓
            ((10, 11), "L2"): 1,
            ((12, 30), "L2"): 5,

            ((8, 9), "L3"): 0.4,  # 0.4 * 100 = 40 cents (multiple of 10) ✓
            ((10, 11), "L3"): 0.9,  # 0.9 * 100 = 90 cents (multiple of 10) ✓
            ((12, 30), "L3"): 4,

            ((8, 9), "L4"): 0.3,  # Rounded from 0.25 -> 0.3 (30 cents, multiple of 10) ✓
            ((10, 11), "L4"): 0.8,  # Rounded from 0.75 -> 0.8 (80 cents, multiple of 10) ✓
            ((12, 30), "L4"): 2,
        }
        self.paytable = self.convert_range_table(pay_group)

        # No paylines - scatter pays anywhere on screen
        self.paylines = {}

        self.include_padding = True
        # Multiplier symbols: single bomb (only in free spins)
        self.special_symbols = {
            "wild": [],  # No wilds, but needed for scatter pay function
            "scatter": ["S"],
            "multiplier": ["M"],
        }
        
        # Multiplier symbol possible values (Sweet Bonanza bomb)
        self.multiplier_symbol_values = {
            "M": [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 1000],
        }

        # Free spins structure - 3 scatters trigger bonus, 4 scatters trigger super bonus
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},  # 3 scatters = 10 free spins, 4 scatters = 10 free spins (super bonus)
            self.freegame_type: {3: 10, 4: 10},  # Retrigger: 3 scatters = 10 more free spins, 4 scatters = 10 more free spins
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
        # No padding multipliers for Sweet Bonanza
        self.padding_symbol_values = {}
        
        # Multiplier symbol distributions (single bomb, only in free spins)
        self.multiplier_symbol_distributions = {
            "M": {
                self.basegame_type: {},
                self.freegame_type: {
                    2: 8,
                    3: 8,
                    4: 8,
                    5: 8,
                    6: 8,
                    8: 8,
                    10: 8,
                    12: 6,
                    15: 6,
                    20: 6,
                    25: 6,
                    50: 4,
                    100: 3,
                    1000: 1,
                },
            }
        }

        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=0.9630,
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
                                self.basegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2, 250: 0.2},
                                self.freegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2, 250: 0.5},
                            },
                            "scatter_triggers": {3: 1},
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
                            "scatter_triggers": {3: 100, 4: 0},  # Only 3 scatters -> 10 spins (4 disabled)
                                "mult_values": {
                                self.basegame_type: {1: 20, 2: 60, 3: 80, 5: 50, 10: 30, 20: 20, 50: 10, 100: 5, 250: 0.5},
                                self.freegame_type: {2: 40, 3: 60, 5: 40, 10: 30, 20: 25, 50: 15, 100: 10, 250: 2},
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
                            "scatter_triggers": {3: 0, 4: 100},  # Only 4 scatters -> 10 spins (3 disabled, same as bought super bonus)
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {20: 25, 50: 30, 100: 25, 250: 8},
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
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.78,  # Adjusted for new bonus structure
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=0.9580,  # Adjusted to within 0.5% of base (0.9630)
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
                                self.basegame_type: {1: 1, 250: 0.1},
                                self.freegame_type: {2: 5, 3: 10, 5: 15, 10: 20, 20: 25, 50: 15, 100: 10, 250: 5},
                            },
                            "scatter_triggers": {3: 1},
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
                                self.basegame_type: {1: 1, 250: 0.1},
                                self.freegame_type: {2: 140, 3: 160, 5: 140, 10: 120, 20: 100, 50: 50, 100: 40, 250: 20},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="super_bonus",
                cost=500.0,
                rtp=0.9580,  # Adjusted to within 0.5% of base (0.9630)
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
                                self.basegame_type: {1: 1, 250: 0.1},
                                self.freegame_type: {20: 25, 50: 30, 100: 25, 250: 10},
                            },
                            "scatter_triggers": {4: 1},  # ALWAYS force 4 scatters in pre-game
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
                            "scatter_triggers": {3: 0, 4: 100},  # ALWAYS only 4 scatters = 10 spins (3 disabled)
                            "mult_values": {
                                self.basegame_type: {1: 1, 250: 0.1},
                                self.freegame_type: {20: 140, 50: 120, 100: 100, 250: 60},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_booster",
                cost=2.0,  # 2x the user's bet
                rtp=0.9630,  # Matches base RTP exactly
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
                                self.basegame_type: {1: 1, 250: 0.1},
                                self.freegame_type: {2: 5, 3: 10, 5: 15, 10: 20, 20: 25, 50: 15, 100: 10, 250: 5},
                            },
                            "scatter_triggers": {3: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame_boosted",
                        quota=0.15,  # Regular bonus (3 scatters) - same as base mode
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100, 4: 0},  # Only 3 scatters = 10 spins (4 disabled, same as base mode)
                            "mult_values": {
                                self.basegame_type: {1: 20, 2: 60, 3: 80, 5: 50, 10: 30, 20: 20, 50: 10, 100: 5, 250: 0.5},
                                self.freegame_type: {2: 40, 3: 60, 5: 40, 10: 30, 20: 25, 50: 15, 100: 10, 250: 2},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="super_freegame_boosted",
                        quota=0.04,  # Super bonus (4 scatters) - same as base mode
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 0, 4: 100},  # Only 4 scatters = 10 spins (3 disabled, same as base mode super bonus)
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {20: 25, 50: 30, 100: 25, 250: 8},
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
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame_boosted",
                        quota=0.798,  # Adjusted for new bonus structure (0.002 + 0.15 + 0.04 + 0.01 + 0.798 = 1.0)
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 10, 3: 15, 5: 30, 10: 25, 20: 15, 50: 3, 100: 1, 250: 0.1},
                                self.freegame_type: {1: 2, 2: 10, 3: 15, 5: 30, 10: 25, 20: 15, 50: 3, 100: 1, 250: 0.5},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="multiplierfeature",
                cost=20.0,
                rtp=0.9630,  # Matches base RTP exactly
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
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5},
                            },
                            "force_min_multipliers": 1,  # Guarantee at least 1 multiplier symbol appears
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
