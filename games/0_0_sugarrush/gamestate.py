from game_override import GameStateOverride
from game_events import update_grid_mult_event


class GameState(GameStateOverride):
    """Gamestate for Sugar Rush - cluster pays with multiplier spots that grow on the grid"""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate cluster pays
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

            # Tumble while there are wins - optimized with safety cap and minimum threshold
            tumble_count = 0
            max_tumbles = 100  # Safety cap to prevent infinite loops
            min_win_threshold = 0.01  # Stop tumbling if win is below threshold (0.01x bet)
            bet_amount = self.get_current_betmode().get_cost()
            
            while (self.win_data["totalWin"] > 0 and 
                   not self.wincap_triggered and 
                   tumble_count < max_tumbles and
                   self.win_data["totalWin"] >= min_win_threshold * bet_amount):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                tumble_count += 1

            # After all tumbles, clear multiplier spots in base game
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            update_grid_mult_event(self)  # Emit grid multiplier state at start of spin
            
            # Evaluate cluster pays
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            self.update_multiplier_spots(emit_event=False)  # Update spots but don't emit event yet
            
            # Tumble while there are wins - optimized with safety cap and minimum threshold
            # Free spins allow more tumbles since multipliers can create longer chains
            tumble_count = 0
            max_tumbles = 75  # Higher cap for free spins (multiplier spots create longer chains)
            min_win_threshold = 0.01  # Stop tumbling if win is below threshold (0.01x bet)
            bet_amount = self.get_current_betmode().get_cost()
            
            while (self.win_data["totalWin"] > 0 and 
                   not self.wincap_triggered and 
                   tumble_count < max_tumbles and
                   self.win_data["totalWin"] >= min_win_threshold * bet_amount):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_multiplier_spots(emit_event=False)  # Update but skip event emission during tumble chain
                tumble_count += 1
            
            # Emit multiplier event once after all tumbles complete
            update_grid_mult_event(self)
            
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            # Check if wincap was triggered and stop free spins immediately
            if self.wincap_triggered:
                self.fs = self.tot_fs  # Set current spins to total to exit loop
                break

        self.end_freespin()
