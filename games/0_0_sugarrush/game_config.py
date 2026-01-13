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
        self.game_id = "0_0_sugarrush"
        self.provider_number = 0
        self.working_name = "Sugar Rush"
        self.wincap = 25000.0  # 25,000x bet max win
        self.win_type = "cluster"  # Cluster pays (connected horizontally/vertically)
        self.rtp = 0.9630
        self.construct_paths()

        # Game Dimensions - Sugar Rush: 7x7 grid (7 reels, 7 rows)
        self.num_reels = 7
        self.num_rows = [7] * self.num_reels
        
        # Multiplier spots system: max multiplier is x1024 (2^10)
        self.maximum_board_mult = 1024
        
        # Board and Symbol Properties - Cluster pays (minimum 5 connected symbols)
        # Sugar Rush symbols: L1-L4 (low), H1-H3 (high), S (scatter) - NO M multiplier symbols!
        # Format: ((min_count, max_count), symbol_name): payout (in bet multiplier)
        pay_group = {
            # High symbols: H1, H2, H3
            ((5, 6), "H1"): 0.5,
            ((7, 8), "H1"): 1.5,
            ((9, 10), "H1"): 5.0,
            ((11, 12), "H1"): 15.0,
            ((13, 14), "H1"): 50.0,
            ((15, 49), "H1"): 300.0,  # 15+ symbols pay 300x
            
            ((5, 6), "H2"): 0.4,
            ((7, 8), "H2"): 1.2,
            ((9, 10), "H2"): 4.0,
            ((11, 12), "H2"): 12.0,
            ((13, 14), "H2"): 40.0,
            ((15, 49), "H2"): 200.0,  # 15+ symbols pay 200x
            
            ((5, 6), "H3"): 0.3,
            ((7, 8), "H3"): 1.0,
            ((9, 10), "H3"): 3.0,
            ((11, 12), "H3"): 10.0,
            ((13, 14), "H3"): 30.0,
            ((15, 49), "H3"): 120.0,  # 15+ symbols pay 120x
            
            # Low symbols: L1, L2, L3, L4
            ((5, 6), "L1"): 0.2,
            ((7, 8), "L1"): 0.6,
            ((9, 10), "L1"): 2.0,
            ((11, 12), "L1"): 6.0,
            ((13, 14), "L1"): 20.0,
            ((15, 49), "L1"): 60.0,  # 15+ symbols pay 60x
            
            ((5, 6), "L2"): 0.15,
            ((7, 8), "L2"): 0.5,
            ((9, 10), "L2"): 1.5,
            ((11, 12), "L2"): 5.0,
            ((13, 14), "L2"): 15.0,
            ((15, 49), "L2"): 50.0,  # 15+ symbols pay 50x
            
            ((5, 6), "L3"): 0.1,
            ((7, 8), "L3"): 0.4,
            ((9, 10), "L3"): 1.2,
            ((11, 12), "L3"): 4.0,
            ((13, 14), "L3"): 12.0,
            ((15, 49), "L3"): 40.0,  # 15+ symbols pay 40x
            
            ((5, 6), "L4"): 0.08,
            ((7, 8), "L4"): 0.3,
            ((9, 10), "L4"): 1.0,
            ((11, 12), "L4"): 3.5,
            ((13, 14), "L4"): 10.0,
            ((15, 49), "L4"): 30.0,  # 15+ symbols pay 30x
        }
        self.paytable = self.convert_range_table(pay_group)

        # No paylines - cluster pays (connected symbols)
        self.paylines = {}

        self.include_padding = True
        # Special symbols - only scatter (no wilds, NO multiplier symbols - multipliers are grid-based spots)
        # Symbols: L1-L4 (low), H1-H3 (high), S (scatter) - that's it!
        self.special_symbols = {
            "wild": [],  # No wilds
            "scatter": ["S"],  # Scatter triggers free spins
            "multiplier": [],  # NO multiplier symbols - multipliers come from cluster hits on grid spots
        }

        # Free spins structure - Sugar Rush: 3, 4, 5, 6, or 7 scatters trigger free spins
        # Base game: 3=10, 4=12, 5=15, 6=20, 7=30 free spins
        # Free spins: Same retrigger amounts
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 15, 6: 20, 7: 30},
            self.freegame_type: {3: 10, 4: 12, 5: 15, 6: 20, 7: 30},  # Retrigger: same amounts
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
        # No padding multipliers for Sugar Rush (grid-based multipliers from cluster hits)
        self.padding_symbol_values = {}
        
        # NO multiplier symbol distributions - multipliers come from cluster explosions on grid spots, not symbols!

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
                            "scatter_triggers": {3: 1},  # Sugar Rush: 3-7 scatters possible (for wincap)
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.006,  # ~1 in 167 spins (0.6% trigger rate) - Sugar Rush standard trigger rate
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            # Base game: Can get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
                            # Weighted distribution - more likely to get 3-4 scatters
                            "scatter_triggers": {3: 50, 4: 30, 5: 12, 6: 6, 7: 2},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="super_freegame",
                        quota=0.0005,  # ~1 in 2000 spins (0.05% trigger rate) - Very rare super bonus
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            # Base game super bonus: Can also get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
                            # Weighted distribution - slightly better odds than regular bonus
                            "scatter_triggers": {3: 40, 4: 35, 5: 15, 6: 7, 7: 3},
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
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.9815,  # Adjusted for realistic trigger rates (1 - 0.006 - 0.0005 - 0.01 - 0.002 = 0.9815)
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
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
                            "scatter_triggers": {3: 1},  # Sugar Rush: 3-7 scatters possible (for wincap)
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
                            # Regular bonus: Can get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
                            # Weighted distribution - more likely to get 3-4 scatters, less likely 7
                            "scatter_triggers": {3: 50, 4: 30, 5: 12, 6: 6, 7: 2},
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
                            "scatter_triggers": {3: 1},  # Sugar Rush: 3-7 scatters possible (for wincap)
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
                            # Super bonus: Can also get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
                            # Weighted distribution - slightly more likely to get higher counts than regular bonus
                            "scatter_triggers": {3: 30, 4: 35, 5: 20, 6: 10, 7: 5},
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
                            "scatter_triggers": {3: 1},  # Sugar Rush: 3-7 scatters possible (for wincap)
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame_boosted",
                        quota=0.02,  # ~1 in 50 spins (2% trigger rate) - Bonus booster makes free spins more common
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            # Bonus booster: Can get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
                            # Weighted distribution - same as base but triggers more often
                            "scatter_triggers": {3: 50, 4: 30, 5: 12, 6: 6, 7: 2},
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
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame_boosted",
                        quota=0.968,  # Adjusted for realistic trigger rates (1 - 0.002 - 0.02 - 0.01 = 0.968)
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
