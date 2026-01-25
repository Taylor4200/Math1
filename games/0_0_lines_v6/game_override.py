from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
import random


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        # Initialize cumulative multiplier tracking for bonus (free games)
        self.cumulative_multiplier_sum = 0.0  # Sum of all multiplier values across bonus spins
        # Track whether the current spin must generate a guaranteed max-win board
        self.force_wincap_pending = self.criteria == "wincap"

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "M": [self.assign_multiplier_symbol_property],
        }
    
    def assign_multiplier_symbol_property(self, symbol) -> dict:
        """Assign multiplier value to multiplier symbol M.
        Uses weighted distribution based on game type (basegame or freegame)."""
        # Normal multiplier assignment
        if hasattr(self.config, 'multiplier_symbol_distributions'):
            mult_dist = self.config.multiplier_symbol_distributions[self.gametype]
            multiplier_value = get_random_outcome(mult_dist)
            symbol.assign_attribute({"multiplier": multiplier_value})
        else:
            # Fallback (shouldn't happen)
            symbol.assign_attribute({"multiplier": 2})
    
    
    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

    def draw_board_with_sticky_wilds(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Override draw_board to preserve sticky wilds during free games."""
        if self.gametype == self.config.freegame_type and self.sticky_wilds:
            # Draw new board normally
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
            
            # Apply sticky wilds to the new board
            for reel_idx, reel_wilds in self.sticky_wilds.items():
                for row_idx, wild_symbol in reel_wilds.items():
                    if reel_idx < len(self.board) and row_idx < len(self.board[reel_idx]):
                        # Place the sticky wild with its original multiplier (preserve the original symbol)
                        self.board[reel_idx][row_idx] = wild_symbol
            
            # Hidden bonus no longer has instant wilds
            
            if emit_event:
                from src.events.events import reveal_event
                reveal_event(self)
            
            # Emit sticky wilds update event for frontend (disabled for now)
            # self.emit_sticky_wilds_event()
        else:
            # Normal board drawing for base game or first free spin
            super().draw_board(emit_event, trigger_symbol)
            

    def update_sticky_wilds(self) -> None:
        """Update sticky wilds with any new wilds that appeared on the board."""
        if self.gametype == self.config.freegame_type:
            for reel_idx, reel in enumerate(self.board):
                for row_idx, symbol in enumerate(reel):
                    if symbol.name == "W":
                        if reel_idx not in self.sticky_wilds:
                            self.sticky_wilds[reel_idx] = {}
                        self.sticky_wilds[reel_idx][row_idx] = symbol

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Override to handle freespin triggers - only 3 scatters trigger bonus."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Only 3 scatters trigger bonus (10 free spins)
        if scatter_count >= 3:
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
        """Override to handle freespin retriggers - only 3 scatters retrigger bonus."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Only 3 scatters retrigger bonus (5 additional free spins)
        if scatter_count >= 3:
            additional_spins = 5  # Retrigger gives 5 extra spins
            self.tot_fs += additional_spins
            from src.events.events import fs_trigger_event
            fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def clear_sticky_wilds(self) -> None:
        """Clear all sticky wilds (called when free game ends)."""
        # Emit final sticky wilds event with cleared positions (disabled for now)
        # self.emit_sticky_wilds_event(clear_all=True)
        self.sticky_wilds = {}
    
    
    def emit_sticky_wilds_event(self, clear_all: bool = False) -> None:
        """Emit event to frontend about current sticky wild positions."""
        sticky_positions = []
        cleared_positions = []
        
        if clear_all:
            # When clearing all, send all current positions as cleared
            for reel_idx, reel_wilds in self.sticky_wilds.items():
                for row_idx in reel_wilds.keys():
                    cleared_positions.append({"reel": reel_idx, "row": row_idx})
        else:
            # Track current sticky wild positions
            current_spin_wilds = self.find_new_wilds_on_board()
            
            for reel_idx, reel_wilds in self.sticky_wilds.items():
                for row_idx, wild_symbol in reel_wilds.items():
                    is_new = any(w["reel"] == reel_idx and w["row"] == row_idx for w in current_spin_wilds)
                    
                    sticky_positions.append({
                        "reel": reel_idx,
                        "row": row_idx,
                        "symbol": {"name": wild_symbol.name, "multiplier": wild_symbol.get_attribute("multiplier")},
                        "multiplier": wild_symbol.get_attribute("multiplier"),
                        "isNew": is_new
                    })
        
        event = {
            "index": len(self.book.events),
            "type": "stickyWildsUpdate",
            "gameType": self.gametype,
            "stickyPositions": sticky_positions,
            "clearedPositions": cleared_positions,
            "totalStickyWilds": len(sticky_positions)
        }
        self.book.add_event(event)
    
    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Override draw_board to handle multiplier feature and forced max-win setups."""
        conditions = self.get_current_distribution_conditions()

        # Force zero-win board for "0" criteria to avoid infinite repeats
        if self.criteria == "0" and self.gametype == self.config.basegame_type:
            self._force_zero_win_board()
            if emit_event:
                from src.events.events import reveal_event
                reveal_event(self)
            return

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
        
        # Check for multiplier feature mode - guarantee minimum multiplier symbol count
        min_forced_multipliers = conditions.get("force_min_multipliers")
        if min_forced_multipliers:
            self._force_multiplier_feature_board(min_forced_multipliers)
        else:
            # Normal board drawing
            super().draw_board(emit_event, trigger_symbol)
    
    def _force_multiplier_feature_board(self, min_multipliers: int) -> None:
        """Force at least `min_multipliers` multiplier symbols (M) to appear on the board.
        After ensuring minimum target, may add extra multiplier symbols randomly for variety."""
        # Draw a board normally first
        self.create_board_reelstrips()
        
        # Count existing multiplier symbols
        multiplier_symbols = self.config.special_symbols.get("multiplier", [])
        mult_count = 0
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name in multiplier_symbols:
                    mult_count += 1
        
        # If we have less than the minimum, add more until we reach it
        while mult_count < min_multipliers:
            # Find a random position that doesn't already have a multiplier symbol
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            if self.board[reel_idx][row_idx].name not in multiplier_symbols:
                # Use single M symbol
                self.board[reel_idx][row_idx] = self.create_symbol("M")
                mult_count += 1
        
        # No extra multiplier symbols - just guarantee the minimum (1)
        
        from src.events.events import reveal_event
        reveal_event(self)

    def _force_zero_win_board(self) -> None:
        """Build a board that guarantees zero wins (no scatter pays, no multipliers, no tumbles)."""
        # Use normal board creation to get proper reelstrips setup
        super().draw_board(emit_event=False)
        
        # Use ALL symbols but distribute so no symbol appears 8+ times (prevents scatter pays)
        # This ensures variety to prevent tumbles while guaranteeing no wins
        all_symbols = ["H1", "H2", "H3", "L1", "L2", "L3", "L4", "S", "M"]
        num_positions = sum(len(reel) for reel in self.board)  # Total positions on board
        
        # Distribute symbols ensuring max 7 of each (prevents 8+ scatter pays)
        max_per_symbol = 7
        symbol_counts = {sym: 0 for sym in all_symbols}
        symbol_assignments = []
        
        # Fill with all symbols randomly but respect max count
        while len(symbol_assignments) < num_positions:
            available_symbols = [sym for sym in all_symbols if symbol_counts[sym] < max_per_symbol]
            if not available_symbols:
                # If all symbols hit max, reset counts and continue (shouldn't happen but safety)
                symbol_counts = {sym: 0 for sym in all_symbols}
                available_symbols = all_symbols
            
            chosen = random.choice(available_symbols)
            symbol_assignments.append(chosen)
            symbol_counts[chosen] += 1
        
        # Shuffle to randomize positions
        random.shuffle(symbol_assignments)
        
        # Replace all symbols on board
        pos = 0
        for reel_idx, reel in enumerate(self.board):
            for row_idx in range(len(reel)):
                new_symbol_name = symbol_assignments[pos]
                new_symbol = self.create_symbol(new_symbol_name)
                self.board[reel_idx][row_idx] = new_symbol
                
                # If it's an M symbol, assign it a random multiplier (won't matter since no tumble)
                if new_symbol_name == "M":
                    conditions = self.get_current_distribution_conditions()
                    if hasattr(self.config, 'multiplier_symbol_distributions'):
                        mult_dist = self.config.multiplier_symbol_distributions[self.gametype]
                        multiplier_value = get_random_outcome(mult_dist)
                        new_symbol.assign_attribute({"multiplier": multiplier_value})
                pos += 1
        
        # Refresh special symbols on board after modifications
        self.get_special_symbols_on_board()

    def _force_wincap_board(self) -> None:
        """Build a deterministic board that guarantees the max-win payout."""
        self.refresh_special_syms()
        num_reels = self.config.num_reels
        board = []

        # Fill the board with top symbol H1 to guarantee a large scatter win
        for reel_idx in range(num_reels):
            column = []
            for row_idx in range(self.config.num_rows[reel_idx]):
                column.append(self.create_symbol("H1"))
            board.append(column)

        # Inject multipliers whose sum equals 100x so the total win reaches the wincap (100 * 100)
        multiplier_layout = [
            (0, 0, 50),
            (1, 2, 25),
            (3, 1, 10),
            (4, 3, 15),
        ]

        for reel_idx, row_idx, value in multiplier_layout:
            sym = self.create_symbol("M")
            sym.assign_attribute({"multiplier": value})
            board[reel_idx][row_idx] = sym

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
    
    def find_new_wilds_on_board(self) -> list:
        """Find wilds that appeared on the board this spin (excluding existing sticky ones)."""
        new_wilds = []
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W":
                    # Check if this position wasn't already sticky
                    if not (reel_idx in self.sticky_wilds and row_idx in self.sticky_wilds[reel_idx]):
                        new_wilds.append({"reel": reel_idx, "row": row_idx})
        return new_wilds
