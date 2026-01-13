from game_calculations import GameCalculations
from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""
        # Use "global" multiplier method - global multiplier applies to ALL wins
        # In free games: global multiplier accumulates from sticky wild multipliers
        # In base game: global multiplier is sum of all wild multipliers on the board
        global_mult = getattr(self, 'global_multiplier', 1)
        
        if self.gametype == self.config.basegame_type:
            # Base game: calculate global multiplier from all wilds on the board
            global_mult = 1  # Start at 1
            for reel in self.board:
                for symbol in reel:
                    if symbol.name == "W" and symbol.check_attribute("multiplier"):
                        multiplier_value = symbol.get_attribute("multiplier")
                        if multiplier_value > 1:
                            global_mult += multiplier_value
        
        self.win_data = Lines.get_lines(
            self.board, 
            self.config, 
            multiplier_method="global",
            global_multiplier=global_mult
        )
        
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)
