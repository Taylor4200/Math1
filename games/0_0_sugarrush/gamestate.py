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
            self.update_multiplier_spots(emit_event=True)  # Update and emit immediately so next tumble uses updated multipliers

            # Tumble while there are wins
            while (self.win_data["totalWin"] > 0 and 
                   not self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_multiplier_spots(emit_event=True)  # Update and emit immediately so next tumble uses updated multipliers

            # After all tumbles, clear multiplier spots in base game
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            # If wincap reached, finish this spin but don't trigger free spins
            if self.wincap_triggered:
                # Still evaluate final win and check repeat, but skip free spin trigger
                self.evaluate_finalwin()
                self.check_repeat()
            else:
                # Normal flow - check for free spin trigger
                if self.check_fs_condition() and self.check_freespin_entry():
                    self.run_freespin_from_base()

                self.evaluate_finalwin()
                self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        
        # SUPER BONUS: Emit initial multipliers BEFORE first spin starts
        # This allows frontend to show starting animation with multipliers already on board
        if hasattr(self, 'betmode') and self.betmode == "super_bonus":
            update_grid_mult_event(self)  # Emit initial random multipliers (2x-1024x on all spots)
        
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            update_grid_mult_event(self)  # Emit grid multiplier state at start of spin
            
            # Evaluate cluster pays
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            self.update_multiplier_spots(emit_event=True)  # Update and emit immediately so next tumble uses updated multipliers
            
            # Tumble while there are wins
            # Free spins allow multipliers to create longer chains
            while (self.win_data["totalWin"] > 0 and 
                   not self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_multiplier_spots(emit_event=True)  # Update and emit immediately so next tumble uses updated multipliers
            
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            # Check if wincap was triggered and stop free spins immediately
            if self.wincap_triggered:
                self.fs = self.tot_fs  # Set current spins to total to exit loop
                break

        self.end_freespin()
