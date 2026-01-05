import random
from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Handles game logic for Plinko - single ball drop per spin."""

    def run_spin(self, sim):
        """Execute Plinko ball drop(s) - single or multi-ball (Hells Storm)."""
        self.reset_seed(sim)
        
        # Apply distribution conditions for this criteria
        self.apply_distribution_conditions()
        
        self.reset_book()
        
        # Check if this is a multi-ball mode (Hells Storm)
        mode_name = self.betmode
        if mode_name in self.config.multi_ball_config:
            # Hells Storm mode
            num_balls = self.config.multi_ball_config[mode_name]["num_balls"]
            base_mode = self.config.multi_ball_config[mode_name]["base_mode"]
        else:
            # Normal single-ball mode
            num_balls = 1
            base_mode = None
        
        # Drop ball(s)
        for ball_num in range(num_balls):
            # Use base_mode reel if this is a Hells Storm mode
            if base_mode:
                self.draw_bucket_from_base_mode(base_mode, force_criteria=False)
            else:
                self.draw_bucket(force_criteria=False)
            
            self.evaluate_bucket_win()
        
        # All wins are basegame wins
        self.win_manager.update_gametype_wins(self.gametype)
        
        # Emit setTotalWin before finalWin
        self.emit_set_total_win()
        
        self.evaluate_finalwin()
        self.imprint_wins()
    
    def draw_bucket_from_base_mode(self, base_mode, force_criteria=False):
        """Draw bucket using a different mode's reel (for Hells Storm modes)."""
        mode_map = {"mild": "MILD", "sinful": "SINFUL", "demonic": "DEMONIC"}
        reel_key = mode_map[base_mode]
        
        # Normal weighted random selection from base mode's reel
        bucket_strip = self.config.reels[reel_key][0]  # Column 0
        position = random.randint(0, len(bucket_strip) - 1)
        self.bucket_index = int(bucket_strip[position])
