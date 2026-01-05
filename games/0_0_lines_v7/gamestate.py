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

            # Tumble while there are wins
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
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
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            # Evaluate scatter pays
            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()  # Transmit win information

            # Tumble while there are wins
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_scatterpays_update_wins()
                self.emit_tumble_win_events()

            # After all tumbles, apply multiplier symbols (bombs only affect this spin)
            self.set_end_tumble_event()
            
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            # Check if wincap was triggered and stop free spins immediately
            if self.wincap_triggered:
                self.fs = self.tot_fs  # Set current spins to total to exit loop
                break

        self.end_freespin()
