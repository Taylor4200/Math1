from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        # Initialize sticky wilds tracking for free games
        self.sticky_wilds = {}  # {reel: {row: wild_symbol}}

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            "X2": [self.process_x2_modifier],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in both basegame and freegame."""
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def process_x2_modifier(self, symbol) -> dict:
        """Process X2 modifier - doubles ALL existing sticky wild multipliers on the board at this moment."""
        # Only process X2 during free games when sticky wilds are active
        if self.gametype == self.config.freegame_type and self.sticky_wilds:
            # Double multipliers of sticky wilds that are currently on the board
            # This does NOT affect new wilds that appear in future spins
            self.double_existing_sticky_wild_multipliers()
        
        # X2 symbol itself has no attributes
        return {}

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

    def double_existing_sticky_wild_multipliers(self) -> None:
        """Double the multiplier value of all sticky wilds currently on the board."""
        for reel_idx, reel_wilds in self.sticky_wilds.items():
            for row_idx, wild_symbol in reel_wilds.items():
                # Get current multiplier using the Symbol's get_attribute method
                current_mult = wild_symbol.get_attribute('multiplier')
                
                if current_mult and current_mult > 0:
                    new_mult = current_mult * 2
                    
                    # Update multiplier using Symbol's assign_attribute method
                    wild_symbol.assign_attribute({'multiplier': new_mult})
                    
                    # Also update the symbol on the board
                    if reel_idx < len(self.board) and row_idx < len(self.board[reel_idx]):
                        self.board[reel_idx][row_idx].assign_attribute({'multiplier': new_mult})

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Override to handle hidden bonus with 5 scatters."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Check for hidden bonus (5 scatters = 12 spins)
        if scatter_count >= 5:
            self.tot_fs = 12
            # Hidden bonus no longer has special activation
        else:
            # Use normal freespin triggers
            self.tot_fs = self.config.freespin_triggers[self.gametype][scatter_count]
        
        # Emit event
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        
        from src.events.events import fs_trigger_event
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

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
