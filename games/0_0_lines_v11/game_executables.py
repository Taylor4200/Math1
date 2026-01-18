from game_calculations import GameCalculations
from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""
        # Use "symbol" multiplier method - multipliers only apply to wins that include wilds
        self.win_data = Lines.get_lines(
            self.board, 
            self.config, 
            multiplier_method="symbol",
            global_multiplier=1
        )
        
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)
