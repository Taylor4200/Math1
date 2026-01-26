from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Gamestate for a single spin - Gates of Olympus style with tumble mechanics"""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate scatter pays
            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()  # Transmit win information

            # Tumble while there are wins (but only if should_tumble allows it)
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                if not self.should_tumble():
                    break  # Stop tumbling even if there's a win
                self.tumble_game_board()
                self.get_scatterpays_update_wins()
                self.emit_tumble_win_events()

            # After all tumbles, apply multiplier symbols
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        # Reset cumulative multiplier at start of bonus
        self.cumulative_multiplier_sum = 0.0
        
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            # Evaluate scatter pays
            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()  # Transmit win information

            # Tumble while there are wins (but only if should_tumble allows it)
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                if not self.should_tumble():
                    break  # Stop tumbling even if there's a win
                self.tumble_game_board()
                self.get_scatterpays_update_wins()
                self.emit_tumble_win_events()

            # After all tumbles, apply multiplier symbols
            # Base game: multiply win by sum of multipliers on board
             # Bonus: if multipliers land, add to cumulative and multiply win by NEW cumulative total
            if self.gametype == self.config.freegame_type:
                # In bonus: check if multiplier symbols landed on this spin
                spin_mult_sum = self.get_board_multipliers_sum()
                # Store cumulative before this spin
                cumulative_before = self.cumulative_multiplier_sum
                # Apply multipliers (adds to cumulative if they landed, multiplies win by NEW total)
                new_cumulative = self.set_end_tumble_event_bonus(spin_mult_sum, cumulative_before)
                # Update cumulative for next spin
                self.cumulative_multiplier_sum = new_cumulative
            else:
                # Base game: multiply win by sum of multipliers on board
                self.set_end_tumble_event()
            
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            # Check if wincap was triggered and stop free spins immediately
            if self.wincap_triggered:
                self.fs = self.tot_fs  # Set current spins to total to exit loop
                break

        # Multipliers are already applied to each spin's win in bonus
        # No need to add anything at the end - cumulative multiplier was used to multiply each win
        self.end_freespin()
