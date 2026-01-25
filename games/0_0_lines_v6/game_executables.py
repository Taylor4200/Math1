from game_calculations import GameCalculations
from src.calculations.scatter import Scatter


class GameExecutables(GameCalculations):

    def get_scatterpays_update_wins(self):
        """Evaluate scatter pays, record wins, and update win manager.
        Multiplier and scatter symbols should NOT explode - they stay on the board."""
        # Evaluate scatter pays (symbols pay anywhere, minimum 8 symbols)
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )
        
        # Remove explode attribute from multiplier and scatter symbols
        # They should stay on the board during tumbles
        multiplier_symbols = self.config.special_symbols.get("multiplier", [])
        scatter_symbols = self.config.special_symbols.get("scatter", [])
        persistent_symbols = set(multiplier_symbols + scatter_symbols)
        
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name in persistent_symbols:
                    # Remove explode attribute so these symbols don't disappear
                    if symbol.check_attribute("explode"):
                        symbol.assign_attribute({"explode": False})
        
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])
    
    def set_end_tumble_event(self):
        """After all tumbling events have finished, apply multiplier symbols (Gates of Olympus style)."""
        # Base game: multiply win by sum of multipliers on board
        board_mult_sum = self.get_board_multipliers_sum()
        
        if board_mult_sum > 0:
            # Multiply win by the sum of multiplier values
            current_win = self.win_manager.spin_win
            self.win_manager.set_spin_win(current_win * board_mult_sum)
        
        from src.events.events import set_win_event, set_total_event
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)
    
    def get_board_multipliers_sum(self):
        """Get sum of all multiplier symbol values on the board (M symbols only)."""
        total_mult = 0
        multiplier_symbols = self.config.special_symbols.get("multiplier", [])
        
        # Count all multiplier symbols (M)
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name in multiplier_symbols:
                    if symbol.check_attribute("multiplier"):
                        mult_value = symbol.get_attribute("multiplier")
                        if isinstance(mult_value, (int, float)):
                            total_mult += mult_value
        
        return total_mult  # Return sum of multiplier values (can be 0 if none present)
    
    def set_end_tumble_event_bonus(self, board_mult_sum: float, cumulative_multiplier_before: float):
        """After all tumbling events have finished in bonus.
        If multiplier symbols landed: add to cumulative and multiply win by NEW cumulative total.
        If no multiplier symbols: just pay base win (no multiplier applied)."""
        from src.events.events import set_win_event, set_total_event
        
        current_win = self.win_manager.spin_win
        
        if board_mult_sum > 0:
            # Multiplier symbols landed: add to cumulative and multiply win by NEW total
            new_cumulative = cumulative_multiplier_before + board_mult_sum
            # Multiply win by the NEW cumulative total (includes the multipliers that just landed)
            self.win_manager.set_spin_win(current_win * new_cumulative)
            if self.win_manager.spin_win > 0:
                set_win_event(self)
            set_total_event(self)
            return new_cumulative  # Return new cumulative for tracking
        else:
            # No multiplier symbols: just pay base win (no multiplier applied)
            # Win stays as is (current_win) - no multiplication
            if self.win_manager.spin_win > 0:
                set_win_event(self)
            set_total_event(self)
            return cumulative_multiplier_before  # Cumulative doesn't change
