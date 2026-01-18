from game_override import GameStateOverride
from src.calculations.lines import Lines


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            # Super Feature Spin mode cannot trigger bonuses
            if self.betmode != "Super Feature Spin" and self.check_fs_condition():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            # Draw board with sticky wilds preserved
            self.draw_board_with_sticky_wilds()
            
            # Update sticky wilds with any new wilds that appeared on the board
            self.update_sticky_wilds()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

            if self.wincap_triggered:
                # Stop remaining spins once max win has been reached
                self.fs = self.tot_fs
                break

        # Clear sticky wilds when free game ends
        self.clear_sticky_wilds()
        self.end_freespin()
