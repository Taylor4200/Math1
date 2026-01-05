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
        # Track whether the current spin must generate a guaranteed max-win board
        self.force_wincap_pending = self.criteria == "wincap"

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "M": [self.assign_multiplier_symbol_property],
        }
    
    def assign_multiplier_symbol_property(self, symbol) -> dict:
        """Assign multiplier value to multiplier symbols (Sweet Bonanza bomb)."""
        symbol_name = symbol.name
        if symbol_name in self.config.multiplier_symbol_distributions:
            mult_dist = self.config.multiplier_symbol_distributions[symbol_name][self.gametype]
            if mult_dist:
                multiplier_value = get_random_outcome(mult_dist)
                symbol.assign_attribute({"multiplier": multiplier_value})
                return
        # Fallback (base game shouldn't spawn multipliers, assign neutral)
        symbol.assign_attribute({"multiplier": 0})
    
    
    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
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
        """Override to handle freespin triggers - 3 scatters trigger bonus, 4 scatters trigger super bonus."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # 4 scatters trigger super bonus (10 free spins)
        if scatter_count >= 4:
            self.tot_fs = self.config.freespin_triggers[self.gametype].get(4, 10)
        # 3 scatters trigger regular bonus (10 free spins)
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
        """Override to handle freespin retriggers - 3 or 4 scatters retrigger bonus."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # 4 scatters retrigger super bonus (10 additional free spins)
        if scatter_count >= 4:
            additional_spins = self.config.freespin_triggers[self.gametype].get(4, 10)
            self.tot_fs += additional_spins
        # 3 scatters retrigger regular bonus (10 additional free spins)
        elif scatter_count >= 3:
            additional_spins = self.config.freespin_triggers[self.gametype].get(3, 10)
            self.tot_fs += additional_spins
        else:
            return  # No retrigger
        
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
        """Force at least `min_multipliers` multiplier symbols (Green, Blue, Purple, Red) to appear on the board.
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
                # Randomly choose a multiplier symbol color
                mult_symbol_name = random.choice(multiplier_symbols)
                self.board[reel_idx][row_idx] = self.create_symbol(mult_symbol_name)
                mult_count += 1
        
        # No extra multiplier symbols - just guarantee the minimum (1)
        
        from src.events.events import reveal_event
        reveal_event(self)

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
            (0, 0, "M", 50),
            (1, 2, "M", 25),
            (3, 1, "M", 15),
            (4, 3, "M", 10),
        ]

        for reel_idx, row_idx, symbol_name, value in multiplier_layout:
            sym = self.create_symbol(symbol_name)
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
