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
        # Initialize sticky wilds tracking for free games
        self.sticky_wilds = {}  # {reel: {row: wild_symbol}}

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            "K": [self.assign_key_drop_count],
        }
    
    def assign_key_drop_count(self, symbol) -> dict:
        """Assign how many wilds this K symbol will drop (1-5)."""
        # Random number of wilds to drop: 1-5
        drop_count = random.randint(1, 5)
        symbol.assign_attribute({"wild_drops": drop_count})
    
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
        """Override draw_board to preserve sticky wilds during free games and process K symbols."""
        if self.gametype == self.config.freegame_type and self.sticky_wilds:
            # Draw new board normally
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
            
            # Apply sticky wilds to the new board
            for reel_idx, reel_wilds in self.sticky_wilds.items():
                for row_idx, wild_symbol in reel_wilds.items():
                    if reel_idx < len(self.board) and row_idx < len(self.board[reel_idx]):
                        # Place the sticky wild with its original multiplier (preserve the original symbol)
                        self.board[reel_idx][row_idx] = wild_symbol
            
            # Process any K symbols that landed (they can drop wilds on sticky wilds, doubling multipliers)
            self.process_k_symbols()
            
            if emit_event:
                from src.events.events import reveal_event
                reveal_event(self)
            
            # Emit sticky wilds update event for frontend (disabled for now)
            # self.emit_sticky_wilds_event()
        else:
            # Normal board drawing for base game or first free spin
            # This will also process K symbols via the draw_board override
            self.draw_board(emit_event, trigger_symbol)
            

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
        """Override draw_board to handle K symbol wild drops and feature modes."""
        conditions = self.get_current_distribution_conditions()
        
        # Check for forced K symbols (Feature Spin modes)
        force_k_count = conditions.get("force_k_symbols")
        if force_k_count:
            self._force_k_symbol_board(force_k_count, emit_event, trigger_symbol)
        # Check for multiplier feature mode - guarantee minimum wild count
        elif conditions.get("force_min_wilds"):
            min_forced_wilds = conditions["force_min_wilds"]
            self._force_multiplier_feature_board(min_forced_wilds)
        # Check for 1000x multiplier feature - guarantee at least one 1000x multiplier
        elif conditions.get("force_min_multiplier_value") == 1000:
            min_multipliers = conditions.get("force_min_multipliers", 1)
            self._force_1000x_multiplier_board(min_multipliers)
        else:
            # Normal board drawing
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
            # Process K symbols if any landed
            self.process_k_symbols()
            if emit_event:
                from src.events.events import reveal_event
                reveal_event(self)
    
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
        
        from src.events.events import reveal_event
        reveal_event(self)
    
    def _force_1000x_multiplier_board(self, min_multipliers: int = 1) -> None:
        """Force at least one wild with 1000x multiplier to appear on the board for 1000x multiplier feature.
        Also ensures at least min_multipliers wilds appear."""
        # Draw a board normally first
        self.create_board_reelstrips()
        
        # Count existing wilds and check for 1000x
        wild_count = 0
        has_1000x = False
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W":
                    wild_count += 1
                    # Assign multiplier to existing wild
                    self.assign_mult_property(symbol)
                    if symbol.get_attribute("multiplier") == 1000:
                        has_1000x = True
        
        # Ensure we have at least min_multipliers wilds
        while wild_count < min_multipliers:
            # Find a random position that doesn't already have a wild
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            if self.board[reel_idx][row_idx].name != "W":
                wild_symbol = self.create_symbol("W")
                # If this is the first wild and we don't have 1000x yet, force it to be 1000x
                if not has_1000x:
                    wild_symbol.assign_attribute({"multiplier": 1000})
                    has_1000x = True
                else:
                    self.assign_mult_property(wild_symbol)
                self.board[reel_idx][row_idx] = wild_symbol
                wild_count += 1
        
        # If we still don't have a 1000x multiplier, force one of the existing wilds to be 1000x
        if not has_1000x and wild_count > 0:
            # Find a random wild and change its multiplier to 1000x
            wild_positions = []
            for reel_idx, reel in enumerate(self.board):
                for row_idx, symbol in enumerate(reel):
                    if symbol.name == "W":
                        wild_positions.append((reel_idx, row_idx))
            
            if wild_positions:
                reel_idx, row_idx = random.choice(wild_positions)
                self.board[reel_idx][row_idx].assign_attribute({"multiplier": 1000})
        
        # Assign multipliers to any other wilds that don't have one yet
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "W" and symbol.get_attribute("multiplier") is None:
                    self.assign_mult_property(symbol)
        
        from src.events.events import reveal_event
        reveal_event(self)
    
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
    
    def process_k_symbols(self) -> None:
        """Process all K symbols on the board and drop wilds."""
        # Find all K symbols on the board
        k_symbols = []
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "K":
                    drop_count = symbol.get_attribute("wild_drops")
                    if drop_count:
                        k_symbols.append({"reel": reel_idx, "row": row_idx, "drops": drop_count})
        
        # Process each K symbol and drop wilds
        for k_info in k_symbols:
            self.drop_wilds_from_k(k_info["drops"])
    
    def drop_wilds_from_k(self, num_drops: int) -> None:
        """Drop wilds randomly on the board from a K symbol.
        If a wild lands on an existing wild, DOUBLE the multiplier."""
        for _ in range(num_drops):
            # Pick a random position on the board (5x5)
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            current_symbol = self.board[reel_idx][row_idx]
            
            # Check if there's already a wild at this position
            if current_symbol.name == "W":
                # DOUBLE the multiplier
                current_multiplier = current_symbol.get_attribute("multiplier")
                if current_multiplier:
                    new_multiplier = current_multiplier * 2
                    current_symbol.assign_attribute({"multiplier": new_multiplier})
            else:
                # Place a new wild with a random multiplier (up to 128x)
                new_wild = self.create_symbol("W")
                # Assign a multiplier up to 128x
                multiplier = self._get_k_wild_multiplier()
                new_wild.assign_attribute({"multiplier": multiplier})
                self.board[reel_idx][row_idx] = new_wild
    
    def _get_k_wild_multiplier(self) -> int:
        """Get a random multiplier for wilds dropped by K symbols (up to 128x)."""
        # Weighted distribution for K-dropped wild multipliers
        multiplier_weights = {
            2: 100,
            3: 80,
            5: 60,
            10: 40,
            20: 20,
            50: 10,
            100: 5,
            128: 2,
        }
        return get_random_outcome(multiplier_weights)
    
    def _force_k_symbol_board(self, min_k_count: int, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Force at least min_k_count K symbols on the board for Feature Spin modes.
        Board may have MORE than the minimum naturally, but guarantees at least the minimum."""
        # Draw a board normally first
        self.create_board_reelstrips()
        
        # Count existing K symbols
        existing_k_count = 0
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "K":
                    existing_k_count += 1
        
        # Only add more if we have fewer than the minimum
        # If we already have more than minimum naturally, keep them all
        while existing_k_count < min_k_count:
            # Find a random position that doesn't have a K or scatter
            reel_idx = random.randint(0, len(self.board) - 1)
            row_idx = random.randint(0, len(self.board[reel_idx]) - 1)
            
            if self.board[reel_idx][row_idx].name not in ["K", "S"]:
                self.board[reel_idx][row_idx] = self.create_symbol("K")
                existing_k_count += 1
        
        # Now process the K symbols to drop wilds
        self.process_k_symbols()
        
        if emit_event:
            from src.events.events import reveal_event
            reveal_event(self)
