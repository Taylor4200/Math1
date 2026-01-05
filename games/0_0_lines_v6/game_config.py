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
        self.game_id = "0_0_lines_v6"
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
        # Gates of Olympus paytable - pays anywhere on screen
        # Using range-based pay groups for scatter pays
        # Format: ((min_count, max_count), symbol_name): payout
        pay_group = {
            # H1 - Red Crown/Gem
            ((8, 9), "H1"): 10.0,
            ((10, 11), "H1"): 25.0,
            ((12, 30), "H1"): 50.0,
            # H2 - Purple/Gold Ring
            ((8, 9), "H2"): 2.0,
            ((10, 11), "H2"): 5.0,
            ((12, 30), "H2"): 15.0,
            # H3 - Gold/Purple Hourglass
            ((8, 9), "H3"): 1.5,
            ((10, 11), "H3"): 2.0,
            ((12, 30), "H3"): 12.0,
            # L1 - Red Gem
            ((8, 9), "L1"): 0.5,
            ((10, 11), "L1"): 1.0,
            ((12, 30), "L1"): 8.0,
            # L2 - Purple Gem
            ((8, 9), "L2"): 0.4,
            ((10, 11), "L2"): 0.5,
            ((12, 30), "L2"): 5.0,
            # L3 - Gold Gem
            ((8, 9), "L3"): 0.30,  # 0.30 * 100 = 30 cents (multiple of 10) ✓
            ((10, 11), "L3"): 0.80,  # 0.80 * 100 = 80 cents (multiple of 10) ✓
            ((12, 30), "L3"): 4.0,
            # L4 - Green Gem
            ((8, 9), "L4"): 0.30,  # 0.30 * 100 = 30 cents (multiple of 10) ✓
            ((10, 11), "L4"): 0.30,  # 0.30 * 100 = 30 cents (multiple of 10) ✓
            ((12, 30), "L4"): 2.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        # No paylines - scatter pays anywhere on screen
        self.paylines = {}

        self.include_padding = True
        # Multiplier symbol: single M symbol (frontend handles visuals)
        self.special_symbols = {
            "wild": [],  # No wilds, but needed for scatter pay function
            "scatter": ["S"], 
            "multiplier": ["M"]  # Single multiplier symbol
        }

        # Free spins structure - 3 scatters trigger bonus
        self.freespin_triggers = {
            self.basegame_type: {3: 10},  # 3 scatters = 10 free spins
            self.freegame_type: {3: 10},  # Retrigger: 3 scatters = 10 more free spins
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
        
        # Multiplier symbol distribution - single M symbol with weighted random values
        # Used for both base game and free game, with different weights
        self.multiplier_symbol_distributions = {
            self.basegame_type: {
                2: 25, 3: 22, 4: 18, 5: 15, 6: 12, 8: 10, 10: 8, 15: 5, 20: 3, 25: 2,
                50: 1, 100: 0.5, 250: 0.2, 500: 0.1
            },
            self.freegame_type: {
                2: 20, 3: 20, 4: 18, 5: 15, 6: 12, 8: 10, 10: 8, 15: 6, 20: 4, 25: 3,
                50: 2, 100: 1.5, 250: 0.5, 500: 0.2
            },
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
                            "scatter_triggers": {3: 100},  # 3 scatters -> 10 spins
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
                            "scatter_triggers": {3: 100},  # 3 scatters -> 10 spins
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
                        quota=0.798,  # Adjusted to sum quotas to 1.0 (0.002 + 0.15 + 0.04 + 0.01 + 0.798 = 1.0)
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
                name="Wrath of Olympus",
                cost=100.0,
                rtp=0.9600,  # Adjusted to be within 0.5% of main RTP (96.3%)
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
                name="Super Wrath of Olympus",
                cost=500.0,
                rtp=0.9580,  # Adjusted to be within 0.5% of main RTP (96.3%)
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
                            "scatter_triggers": {3: 100},  # GUARANTEED 3 scatters = 10 spins
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
                rtp=0.9600,  # Higher RTP than base game
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,  # Feature spin - persists after each round
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
                        criteria="freegame_boosted",
                        quota=0.20,  # Same as base game freegame quota (but 5x scatter chance)
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100},  # 3 scatters = 10 spins
                            "mult_values": {
                                self.basegame_type: {1: 20, 2: 60, 3: 80, 5: 50, 10: 30, 20: 20, 50: 10, 100: 5, 250: 0.5},
                                self.freegame_type: {2: 40, 3: 60, 5: 40, 10: 30, 20: 25, 50: 15, 100: 10, 250: 2},
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
                        quota=0.788,  # Adjusted to sum quotas to 1.0 (0.002 + 0.20 + 0.01 + 0.788 = 1.0)
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
                name="Divine Strikes",
                cost=20.0,
                rtp=0.9600,  # Similar to bonus_booster
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,  # Feature spin - persists after each round
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
            BetMode(
                name="Divine Judgement",
                cost=1000.0,
                rtp=0.9600,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,  # Feature spin - persists after each round
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="divine_judgement",
                        quota=1.0,  # 100% - always use divine judgement mode
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05, 250: 0.01},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3, 250: 0.5},
                            },
                            "enable_max_multiplier": True,  # Enable MAX multiplier symbol
                            "max_multiplier_chance": 0.05,  # 5% chance for M symbol to be MAX in Divine Judgement
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
