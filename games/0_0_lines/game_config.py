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
        self.game_id = "0_0_lines"  # "0_0_lines"
        self.provider_number = 0
        self.working_name = "Sample Lines Game"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9500
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels
        # Board and Symbol Properties
        self.paytable = {
            (5, "W"): 50,
            (4, "W"): 20,
            (3, "W"): 10,
            (5, "H1"): 50,
            (4, "H1"): 20,
            (3, "H1"): 10,
            (5, "H2"): 15,
            (4, "H2"): 5,
            (3, "H2"): 2.2,
            (5, "H3"): 10,
            (4, "H3"): 3,
            (3, "H3"): 1.3,
            (5, "H4"): 10,
            (4, "H4"): 3,
            (3, "H4"): 1.8,
            (5, "L1"): 4,
            (4, "L1"): 2.0,
            (3, "L1"): 0.5,
            (5, "L2"): 3.5,
            (4, "L2"): 1.8,
            (3, "L2"): 0.4,
            (5, "L3"): 3.5,
            (4, "L3"): 1.8,
            (3, "L3"): 0.4,
            (5, "L4"): 3,
            (4, "L4"): 1.8,
            (3, "L4"): 0.3,
            (5, "L5"): 3,
            (4, "L5"): 1.8,
            (3, "L5"): 0.3,
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
                0,
                1,
                2,
                3,
                2,
            ],
            6: [
                3,
                2,
                1,
                0,
                1,
            ],
            7: [
                0,
                0,
                1,
                2,
                3,
            ],
            8: [
                3,
                3,
                2,
                1,
                0,
            ],
            9: [
                1,
                0,
                1,
                2,
                1,
            ],
            10: [
                1,
                2,
                1,
                0,
                1,
            ],
            11: [
                0,
                1,
                1,
                1,
                2,
            ],
            12: [
                2,
                1,
                1,
                1,
                0,
            ],
            13: [
                0,
                1,
                0,
                1,
                2,
            ],
            14: [
                2,
                1,
                2,
                1,
                0,
            ],
            15: [
                1,
                1,
                0,
                1,
                1,
            ],
            16: [
                1,
                1,
                2,
                1,
                1,
            ],
            17: [
                0,
                2,
                1,
                0,
                2,
            ],
            18: [
                2,
                0,
                1,
                2,
                0,
            ],
            19: [
                0,
                0,
                2,
                0,
                0,
            ],
            20: [
                2,
                2,
                0,
                2,
                2,
            ],
            21: [
                1,
                0,
                0,
                0,
                1,
            ],
            22: [
                1,
                3,
                3,
                3,
                1,
            ],
            23: [
                0,
                1,
                2,
                3,
                0,
            ],
            24: [
                3,
                2,
                1,
                0,
                3,
            ],
            25: [
                0,
                2,
                1,
                3,
                2,
            ],
            26: [
                3,
                1,
                2,
                0,
                1,
            ],
            27: [
                1,
                0,
                2,
                3,
                1,
            ],
            28: [
                1,
                3,
                2,
                0,
                1,
            ],
            29: [
                0,
                3,
                1,
                2,
                0,
            ],
            30: [
                3,
                0,
                2,
                1,
                3,
            ],
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["W"],
                                "scatter": ["S"], "multiplier": ["W"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {2: 3, 3: 5, 4: 8, 5: 12},
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
            2: 100, 3: 80, 5: 60, 10: 40, 20: 20, 50: 10, 100: 5}}}

        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=0.9400,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2},
                                self.freegame_type: {2: 10, 3: 20, 5: 15, 10: 10, 20: 5, 50: 3, 100: 2},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.20,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 50, 4: 20, 5: 5},
                            "mult_values": {
                                self.basegame_type: {1: 20, 2: 60, 3: 80, 5: 50, 10: 30, 20: 20, 50: 10, 100: 5},
                                self.freegame_type: {1: 20, 2: 60, 3: 80, 5: 50, 10: 30, 20: 20, 50: 10, 100: 5},
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
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.77,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 2, 2: 65, 3: 28, 5: 4, 10: 1, 20: 0.8, 50: 0.15, 100: 0.05},
                                self.freegame_type: {1: 12, 2: 58, 3: 25, 5: 22, 10: 15, 20: 10, 50: 4, 100: 3},
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
                rtp=0.9450,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 5, 3: 10, 5: 15, 10: 20, 20: 25, 50: 15, 100: 10},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
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
                            "scatter_triggers": {3: 20, 4: 10, 5: 2},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 140, 3: 160, 5: 140, 10: 120, 20: 100, 50: 50, 100: 40},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="super_bonus",
                cost=200.0,
                rtp=0.9430,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {5: 20, 10: 30, 20: 25, 50: 15, 100: 10},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
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
                            "scatter_triggers": {3: 20, 4: 10, 5: 2},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {5: 140, 10: 120, 20: 100, 50: 60, 100: 40},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
