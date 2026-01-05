from game_executables import GameExecutables
from src.events.events import set_total_event


class GameCalculations(GameExecutables):
    """Plinko-specific calculations for bucket wins."""
    
    def emit_set_total_win(self):
        """Emit setTotalWin event."""
        set_total_event(self)

    def evaluate_bucket_win(self):
        """Calculate win from bucket index and volatility mode."""
        multiplier = self.get_bucket_multiplier()
        
        # For Hells Storm modes, each ball uses base bet (1.0), not total cost (66.0)
        mode_name = self.betmode
        if mode_name in self.config.multi_ball_config:
            # Each ball in Hells Storm is calculated as a $1 bet
            bet_cost = 1.0
        else:
            # Normal modes use configured cost
            bet_cost = self.get_current_betmode().get_cost()
        
        win_amount = bet_cost * multiplier
        
        self.win_manager.update_spinwin(win_amount)
        
        # Emit plinkoResult event
        self.emit_plinko_event(self.bucket_index, multiplier)

    def get_bucket_multiplier(self):
        """Get multiplier for current bucket and mode."""
        # Check if this is a Hells Storm mode
        mode_name = self.betmode
        if mode_name in self.config.multi_ball_config:
            # Use base mode multipliers (e.g., hells_storm_mild uses MILD multipliers)
            mode_key = self.config.multi_ball_config[mode_name]["base_mode"]
        else:
            # Normal mode mapping
            mode_map = {"mild": "mild", "sinful": "sinful", "demonic": "demonic"}
            mode_key = mode_map[mode_name]
        
        return self.config.bucket_multipliers[mode_key][self.bucket_index]

    def emit_plinko_event(self, bucket_index, multiplier):
        """Emit plinkoResult event for RGS integration."""
        event = {
            "index": len(self.book.events),
            "type": "plinkoResult",
            "bucketIndex": bucket_index,
            "multiplier": multiplier
        }
        
        self.book.add_event(event)
