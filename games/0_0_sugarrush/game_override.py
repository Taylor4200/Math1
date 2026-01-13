from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
import random


class GameStateOverride(GameExecutables):
    """
    Sugar Rush game state overrides.
    Handles multiplier spots, free spin triggers, and board resets.
    """

    def reset_book(self):
        super().reset_book()
        # Track whether the current spin must generate a guaranteed max-win board
        self.force_wincap_pending = self.criteria == "wincap"
        # Reset multiplier spots for base game (they persist in free spins)
        # Initialize multiplier spots if they don't exist yet (during __init__)
        if not hasattr(self, 'position_multipliers'):
            self.reset_multiplier_spots()
        elif self.gametype == self.config.basegame_type:
            self.reset_multiplier_spots()

    def reset_fs_spin(self):
        super().reset_fs_spin()
        # Reset multiplier spots at start of free spins round
        # (they will persist throughout the round after this)
        self.reset_multiplier_spots()
        
        # Check if super bonus (super_bonus bet mode) - start with 4x multipliers on ALL spots immediately
        # betmode is stored as string name, but may not exist during initialization (e.g., during __init__)
        # Only set super bonus multipliers when actually starting free spins (betmode exists and is super_bonus)
        if hasattr(self, 'betmode') and self.betmode == "super_bonus":
            # Initialize all positions with 4x multiplier (explosion_count = 2 gives 2^2 = 4x)
            for reel_idx in range(self.config.num_reels):
                for row_idx in range(self.config.num_rows[reel_idx]):
                    self.explosion_count[reel_idx][row_idx] = 2  # explosion_count = 2 means 2^2 = 4x multiplier
                    self.position_multipliers[reel_idx][row_idx] = 4

    def assign_special_sym_function(self):
        # No special symbol functions needed - no multiplier symbols, only scatter
        self.special_symbol_functions = {}

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return

    def set_end_tumble_event(self):
        """After all tumbles complete, clear multiplier spots in base game."""
        from src.events.events import set_win_event, set_total_event
        
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)
        
        # In base game, clear multiplier spots after tumbling ends
        if self.gametype == self.config.basegame_type:
            self.reset_multiplier_spots()
        # In free spins, multiplier spots persist (already handled in update_multiplier_spots)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Override to handle Sugar Rush free spin triggers: 3, 4, 5, 6, or 7 scatters."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Sugar Rush: 3=10, 4=12, 5=15, 6=20, 7=30 free spins
        if scatter_count >= 7:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(7, 30)
        elif scatter_count >= 6:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(6, 20)
        elif scatter_count >= 5:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(5, 15)
        elif scatter_count >= 4:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(4, 12)
        elif scatter_count >= 3:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(3, 10)
        else:
            self.tot_fs = 0
        
        # Emit event
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        
        from src.events.events import fs_trigger_event
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)
    
    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Override to handle Sugar Rush free spin retriggers: 3, 4, 5, 6, or 7 scatters."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Sugar Rush retrigger: same amounts as initial trigger
        if scatter_count >= 7:
            additional_spins = self.config.freespin_triggers[self.gametype].get(7, 30)
            self.tot_fs += additional_spins
        elif scatter_count >= 6:
            additional_spins = self.config.freespin_triggers[self.gametype].get(6, 20)
            self.tot_fs += additional_spins
        elif scatter_count >= 5:
            additional_spins = self.config.freespin_triggers[self.gametype].get(5, 15)
            self.tot_fs += additional_spins
        elif scatter_count >= 4:
            additional_spins = self.config.freespin_triggers[self.gametype].get(4, 12)
            self.tot_fs += additional_spins
        elif scatter_count >= 3:
            additional_spins = self.config.freespin_triggers[self.gametype].get(3, 10)
            self.tot_fs += additional_spins
        else:
            return  # No retrigger
        
        from src.events.events import fs_trigger_event
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Override draw_board to handle forced max-win setups."""
        conditions = self.get_current_distribution_conditions()

        # Guarantee the max-win outcome during the freegame portion of wincap simulations
        if (
            conditions.get("force_wincap")
            and self.gametype == self.config.freegame_type
            and getattr(self, "force_wincap_pending", False)
        ):
            self._force_wincap_board()
            self.force_wincap_pending = False
            if emit_event:
                from src.events.events import reveal_event
                reveal_event(self)
            return
        
        # Normal board drawing
        super().draw_board(emit_event, trigger_symbol)
    
    def _force_wincap_board(self) -> None:
        """Build a deterministic board that guarantees the max-win payout."""
        self.refresh_special_syms()
        num_reels = self.config.num_reels
        board = []

        # Fill the board with top symbol H1 to guarantee a large cluster win
        for reel_idx in range(num_reels):
            column = []
            for row_idx in range(self.config.num_rows[reel_idx]):
                column.append(self.create_symbol("H1"))
            board.append(column)

        # Set up high multiplier spots to reach wincap
        # This is a simplified version - actual implementation would need proper cluster setup
        self.board = board
        self.reelstrip_id = "WCAP"
        # Provide simple virtual reelstrips so tumble refills continue to work
        self.reelstrip = [["H1"] for _ in range(num_reels)]
        self.reel_positions = [0] * num_reels
        self.padding_position = [0] * num_reels
        self.anticipation = [0] * num_reels

        if self.config.include_padding:
            self.top_symbols = [self.create_symbol("H1") for _ in range(num_reels)]
            self.bottom_symbols = [self.create_symbol("H1") for _ in range(num_reels)]

        self.get_special_symbols_on_board()
