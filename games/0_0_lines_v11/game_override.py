from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import json_ready_sym, EventConstants
import random


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
        }
    
    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in both basegame and freegame."""
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})
    
    
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
            
            if emit_event:
                self.reveal_event()
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
                        # Store the wild symbol (with its multiplier) as sticky
                        self.sticky_wilds[reel_idx][row_idx] = symbol

    def clear_sticky_wilds(self) -> None:
        """Clear all sticky wilds (called when free game ends)."""
        self.sticky_wilds = {}
    
    def reveal_event(self):
        """Override reveal_event to include multiplier information for wild symbols."""
        board_client = []
        special_attributes = list(self.config.special_symbols.keys())
        
        # Build board with special attributes
        for reel, _ in enumerate(self.board):
            board_client.append([])
            for row in range(len(self.board[reel])):
                symbol_json = json_ready_sym(self.board[reel][row], special_attributes)
                # Add multiplier if the symbol has one
                if self.board[reel][row].name == "W" and self.board[reel][row].get_attribute("multiplier") is not None:
                    symbol_json["multiplier"] = int(self.board[reel][row].get_attribute("multiplier"))
                board_client[reel].append(symbol_json)
        
        # Handle padding symbols
        if self.config.include_padding:
            for reel, _ in enumerate(board_client):
                top_symbol_json = json_ready_sym(self.top_symbols[reel], special_attributes)
                if self.top_symbols[reel].name == "W" and self.top_symbols[reel].get_attribute("multiplier") is not None:
                    top_symbol_json["multiplier"] = int(self.top_symbols[reel].get_attribute("multiplier"))
                
                bottom_symbol_json = json_ready_sym(self.bottom_symbols[reel], special_attributes)
                if self.bottom_symbols[reel].name == "W" and self.bottom_symbols[reel].get_attribute("multiplier") is not None:
                    bottom_symbol_json["multiplier"] = int(self.bottom_symbols[reel].get_attribute("multiplier"))
                
                board_client[reel] = [top_symbol_json] + board_client[reel]
                board_client[reel].append(bottom_symbol_json)
        
        event = {
            "index": len(self.book.events),
            "type": EventConstants.REVEAL.value,
            "board": board_client,
            "paddingPositions": self.reel_positions,
            "gameType": self.gametype,
            "anticipation": self.anticipation,
        }
        self.book.add_event(event)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Override to handle freespin triggers."""
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Use normal freespin triggers
        # If scatter_count is not in the triggers dict, use the highest available trigger
        freespin_triggers = self.config.freespin_triggers[self.gametype]
        if scatter_count in freespin_triggers:
            self.tot_fs = freespin_triggers[scatter_count]
        else:
            # Use the highest scatter count trigger (e.g., 5+ scatters = 4 scatter bonus)
            max_scatter_count = max(freespin_triggers.keys())
            self.tot_fs = freespin_triggers[max_scatter_count]
        
        # Emit event
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        
        from src.events.events import fs_trigger_event
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    
    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Override draw_board to handle multiplier feature and max win feature."""
        conditions = self.get_current_distribution_conditions()
        
        # Check for multiplier feature mode - guarantee minimum wild count
        min_forced_wilds = conditions.get("force_min_wilds")
        if min_forced_wilds:
            self._force_multiplier_feature_board(min_forced_wilds)
        # Check for 500x multiplier feature - guarantee at least one 500x multiplier
        elif conditions.get("force_min_multiplier_value") == 500:
            min_multipliers = conditions.get("force_min_multipliers", 1)
            self._force_500x_multiplier_board(min_multipliers)
        else:
            # Normal board drawing - call super but use our custom reveal_event
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
            if emit_event:
                self.reveal_event()
    
    def _force_multiplier_feature_board(self, min_wilds: int) -> None:
        """Force a board with at least min_wilds wild symbols for multiplier feature."""
        max_attempts = 100
        attempt = 0
        
        while attempt < max_attempts:
            # Draw a normal board
            super().draw_board(emit_event=False, trigger_symbol="scatter")
            
            # Count wilds on the board
            wild_count = sum(1 for reel in self.board for symbol in reel if symbol.name == "W")
            
            # If we have enough wilds, we're done
            if wild_count >= min_wilds:
                self.reveal_event()
                return
            
            attempt += 1
        
        # If we couldn't get enough wilds naturally, force them
        self._force_wilds_on_board(min_wilds)
        self.reveal_event()
    
    def _force_500x_multiplier_board(self, min_multipliers: int) -> None:
        """Force a board with at least min_multipliers 500x+ multiplier symbols."""
        max_attempts = 100
        attempt = 0
        
        while attempt < max_attempts:
            # Draw a normal board
            super().draw_board(emit_event=False, trigger_symbol="scatter")
            
            # Count 500x+ multipliers on the board
            high_mult_count = sum(
                1 for reel in self.board 
                for symbol in reel 
                if symbol.name == "W" and symbol.get_attribute("multiplier") is not None 
                and symbol.get_attribute("multiplier") >= 500
            )
            
            # If we have enough high multipliers, we're done
            if high_mult_count >= min_multipliers:
                self.reveal_event()
                return
            
            attempt += 1
        
        # If we couldn't get enough high multipliers naturally, force them
        self._force_high_multipliers_on_board(min_multipliers, 500)
        self.reveal_event()
    
    def _force_wilds_on_board(self, min_wilds: int) -> None:
        """Force at least min_wilds wild symbols onto the board."""
        from src.config.symbols import Symbol
        
        # Count current wilds
        current_wilds = sum(1 for reel in self.board for symbol in reel if symbol.name == "W")
        wilds_needed = min_wilds - current_wilds
        
        if wilds_needed <= 0:
            return
        
        # Get list of non-wild positions
        non_wild_positions = [
            (r, s) for r, reel in enumerate(self.board) 
            for s, symbol in enumerate(reel) 
            if symbol.name != "W"
        ]
        
        # Randomly select positions to replace with wilds
        random.shuffle(non_wild_positions)
        for i in range(min(wilds_needed, len(non_wild_positions))):
            reel_idx, symbol_idx = non_wild_positions[i]
            wild_symbol = Symbol("W")
            self.assign_mult_property(wild_symbol)
            self.board[reel_idx][symbol_idx] = wild_symbol
    
    def _force_high_multipliers_on_board(self, min_multipliers: int, min_value: int) -> None:
        """Force at least min_multipliers symbols with multiplier >= min_value onto the board."""
        from src.config.symbols import Symbol
        
        # Count current high multipliers
        current_high_mults = sum(
            1 for reel in self.board 
            for symbol in reel 
            if symbol.name == "W" and symbol.get_attribute("multiplier") is not None 
            and symbol.get_attribute("multiplier") >= min_value
        )
        
        mults_needed = min_multipliers - current_high_mults
        
        if mults_needed <= 0:
            return
        
        # Get list of non-wild positions
        non_wild_positions = [
            (r, s) for r, reel in enumerate(self.board) 
            for s, symbol in enumerate(reel) 
            if symbol.name != "W"
        ]
        
        # Randomly select positions to replace with high multiplier wilds
        random.shuffle(non_wild_positions)
        for i in range(min(mults_needed, len(non_wild_positions))):
            reel_idx, symbol_idx = non_wild_positions[i]
            wild_symbol = Symbol("W")
            # Assign a high multiplier value (500x or 1000x)
            multiplier_value = random.choice([500, 1000])
            wild_symbol.assign_attribute({"multiplier": multiplier_value})
            self.board[reel_idx][symbol_idx] = wild_symbol
