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
        # Stores wilds using INTERNAL board indices (not including padding)
        self.sticky_wilds = {}  # {reel: {row: wild_symbol}}
        # Also track padding symbols separately
        self.sticky_top_padding = {}  # {reel: wild_symbol}
        self.sticky_bottom_padding = {}  # {reel: wild_symbol}

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
            
            # Apply sticky padding wilds
            if self.config.include_padding:
                for reel_idx, wild_symbol in self.sticky_top_padding.items():
                    if reel_idx < len(self.top_symbols):
                        self.top_symbols[reel_idx] = wild_symbol
                for reel_idx, wild_symbol in self.sticky_bottom_padding.items():
                    if reel_idx < len(self.bottom_symbols):
                        self.bottom_symbols[reel_idx] = wild_symbol
            
            if emit_event:
                self.reveal_event()
        else:
            # Normal board drawing for base game or first free spin
            # ALWAYS use custom reveal_event to include multipliers
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
            if emit_event:
                self.reveal_event()

    def update_sticky_wilds(self) -> None:
        """Update sticky wilds with any new wilds that appeared on the board."""
        if self.gametype == self.config.freegame_type:
            # Update main board sticky wilds
            for reel_idx, reel in enumerate(self.board):
                for row_idx, symbol in enumerate(reel):
                    if symbol.name == "W":
                        if reel_idx not in self.sticky_wilds:
                            self.sticky_wilds[reel_idx] = {}
                        # Store the wild symbol (with its multiplier) as sticky
                        self.sticky_wilds[reel_idx][row_idx] = symbol
            
            # Update padding sticky wilds
            if self.config.include_padding:
                for reel_idx, symbol in enumerate(self.top_symbols):
                    if symbol.name == "W":
                        self.sticky_top_padding[reel_idx] = symbol
                for reel_idx, symbol in enumerate(self.bottom_symbols):
                    if symbol.name == "W":
                        self.sticky_bottom_padding[reel_idx] = symbol

    def clear_sticky_wilds(self) -> None:
        """Clear all sticky wilds (called when free game ends)."""
        self.sticky_wilds = {}
        self.sticky_top_padding = {}
        self.sticky_bottom_padding = {}
    
    def reveal_event(self):
        """Override reveal_event to include multiplier information for wild symbols."""
        board_client = []
        special_attributes = list(self.config.special_symbols.keys())
        
        # Build board with special attributes
        for reel, _ in enumerate(self.board):
            board_client.append([])
            for row in range(len(self.board[reel])):
                symbol_json = json_ready_sym(self.board[reel][row], special_attributes)
                # Add multiplier value for wild symbols (ALWAYS include it for frontend display)
                if self.board[reel][row].name == "W":
                    mult_val = self.board[reel][row].get_attribute("multiplier")
                    if mult_val is not None:
                        symbol_json["multiplier"] = int(mult_val)
                    else:
                        # This should never happen, but log it if it does
                        print(f"WARNING: Wild symbol at reel {reel}, row {row} has no multiplier!")
                        symbol_json["multiplier"] = 1  # Fallback to 1
                board_client[reel].append(symbol_json)
        
        # Handle padding symbols
        if self.config.include_padding:
            for reel, _ in enumerate(board_client):
                top_symbol_json = json_ready_sym(self.top_symbols[reel], special_attributes)
                if self.top_symbols[reel].name == "W":
                    mult_val = self.top_symbols[reel].get_attribute("multiplier")
                    if mult_val is not None:
                        top_symbol_json["multiplier"] = int(mult_val)
                    else:
                        print(f"WARNING: Top padding wild symbol at reel {reel} has no multiplier!")
                        top_symbol_json["multiplier"] = 1
                
                bottom_symbol_json = json_ready_sym(self.bottom_symbols[reel], special_attributes)
                if self.bottom_symbols[reel].name == "W":
                    mult_val = self.bottom_symbols[reel].get_attribute("multiplier")
                    if mult_val is not None:
                        bottom_symbol_json["multiplier"] = int(mult_val)
                    else:
                        print(f"WARNING: Bottom padding wild symbol at reel {reel} has no multiplier!")
                        bottom_symbol_json["multiplier"] = 1
                
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
        self.tot_fs = self.config.freespin_triggers[self.gametype][scatter_count]
        
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
        """Force at least `min_wilds` wilds to appear on the board for multiplier feature.
        After ensuring minimum target, may add extra wilds randomly for variety."""
        # Draw a board normally first
        self.create_board_reelstrips()
        
        # Count existing wilds
        wild_count = 0
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W":
                    wild_count += 1
        
        # If we have less than the minimum, add more until we reach it
        while wild_count < min_wilds:
            # Find a random position that doesn't already have a wild
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            if self.board[reel_idx][row_idx].name != "W":
                self.board[reel_idx][row_idx] = self.create_symbol("W")
                wild_count += 1
        
        # Add variety: randomly add 0-3 extra wilds (50% chance for each extra wild)
        # This gives variety: results may exceed the minimum wild count
        total_positions = sum(len(reel) for reel in self.board)
        non_wild_positions = []
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name != "W":
                    non_wild_positions.append((reel_idx, row_idx))
        
        # Randomly add 0-3 extra wilds (each has 50% chance)
        extra_wilds = sum(1 for _ in range(3) if random.random() < 0.5)
        extra_wilds = min(extra_wilds, len(non_wild_positions))  # Don't exceed available positions
        
        if extra_wilds > 0 and len(non_wild_positions) > 0:
            positions_to_add = random.sample(non_wild_positions, extra_wilds)
            for reel_idx, row_idx in positions_to_add:
                self.board[reel_idx][row_idx] = self.create_symbol("W")
        
        # Ensure all wilds have multipliers assigned
        # Note: create_symbol("W") should automatically call assign_mult_property via special_symbol_functions
        # This is a safety check in case any wilds were created without going through that flow
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W":
                    # Double-check that multiplier was assigned (should already be done by create_symbol)
                    mult_val = symbol.get_attribute("multiplier")
                    if mult_val is None:
                        self.assign_mult_property(symbol)
        
        self.reveal_event()
    
    def _force_500x_multiplier_board(self, min_multipliers: int = 1) -> None:
        """Force at least one wild with 500x multiplier for Super Feature Spin mode.
        Other wilds get random multipliers. Also ensures at least min_multipliers wilds appear."""
        # Draw a board normally first
        self.create_board_reelstrips()
        
        # Count existing wilds and check for 500x
        wild_count = 0
        has_500x = False
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W":
                    wild_count += 1
                    # Assign random multiplier to existing wilds
                    self.assign_mult_property(symbol)
                    if symbol.get_attribute("multiplier") == 500:
                        has_500x = True
        
        # Ensure we have at least min_multipliers wilds
        while wild_count < min_multipliers:
            # Find a random position that doesn't already have a wild
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            if self.board[reel_idx][row_idx].name != "W":
                wild_symbol = self.create_symbol("W")
                # If we don't have a 500x yet, force this one to be 500x
                if not has_500x:
                    wild_symbol.assign_attribute({"multiplier": 500})
                    has_500x = True
                else:
                    # Other wilds get random multipliers
                    self.assign_mult_property(wild_symbol)
                self.board[reel_idx][row_idx] = wild_symbol
                wild_count += 1
        
        # If we still don't have a 500x multiplier, force one of the existing wilds to be 500x
        if not has_500x and wild_count > 0:
            # Find a random wild and change its multiplier to 500x
            wild_positions = []
            for reel_idx, reel in enumerate(self.board):
                for row_idx, symbol in enumerate(reel):
                    if symbol.name == "W":
                        wild_positions.append((reel_idx, row_idx))
            
            if wild_positions:
                reel_idx, row_idx = random.choice(wild_positions)
                self.board[reel_idx][row_idx].assign_attribute({"multiplier": 500})
        
        # Assign random multipliers to any other wilds that don't have one yet
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W" and symbol.get_attribute("multiplier") is None:
                    self.assign_mult_property(symbol)
        
        self.reveal_event()
    
