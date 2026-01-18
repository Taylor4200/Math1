from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from game_events import update_grid_mult_event
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Sugar Rush game executables - cluster pays with multiplier spots"""

    def reset_multiplier_spots(self):
        """Initialize multiplier spots grid - tracks explosion count per position."""
        # Track explosion count per position (0 = no mark, 1 = marked, 2+ = multiplier active)
        self.explosion_count = [
            [0 for _ in range(self.config.num_rows[reel])] 
            for reel in range(self.config.num_reels)
        ]
        # Track multiplier value per position (starts at 0, becomes 2x after 2nd explosion, doubles each time)
        self.position_multipliers = [
            [0 for _ in range(self.config.num_rows[reel])] 
            for reel in range(self.config.num_reels)
        ]

    def update_multiplier_spots(self, emit_event: bool = True):
        """
        Sugar Rush multiplier spots system:
        - First hit: Marks/activates the spot (multiplier = 0x, just marked)
        - Second hit: Creates 2x multiplier
        - Each subsequent hit doubles the multiplier (2x → 4x → 8x → 16x... up to 1024x)
        - Multiple multipliers in same cluster add together
        
        Optimized: Use lookup table for powers of 2 (much faster), only emit events when needed.
        """
        if self.win_data["totalWin"] > 0:
            # Pre-computed powers of 2 lookup table
            # Index 0 = 0x (marked but not active), Index 1 = 2x, Index 2 = 4x, etc.
            # [0x, 2x, 4x, 8x, 16x, 32x, 64x, 128x, 256x, 512x, 1024x]
            MULTIPLIER_LOOKUP = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
            max_mult = self.config.maximum_board_mult
            
            for win in self.win_data["wins"]:
                for pos in win["positions"]:
                    reel_idx = pos["reel"]
                    row_idx = pos["row"]
                    
                    # Increment explosion count
                    self.explosion_count[reel_idx][row_idx] += 1
                    count = self.explosion_count[reel_idx][row_idx]
                    
                    # count = 0: not hit (0x)
                    # count = 1: first hit, marked but not active (0x)
                    # count = 2: second hit, creates 2x multiplier
                    # count = 3: third hit, 4x multiplier
                    # count = 4: fourth hit, 8x multiplier, etc.
                    if count == 0:
                        mult_value = 0
                    elif count == 1:
                        mult_value = 0  # Marked but not active yet
                    elif count - 1 < len(MULTIPLIER_LOOKUP):
                        mult_value = MULTIPLIER_LOOKUP[count - 1]  # count=2 → index 1 = 2x, count=3 → index 2 = 4x
                    else:
                        mult_value = max_mult  # Already at max
                    
                    if mult_value > max_mult:
                        mult_value = max_mult
                    
                    self.position_multipliers[reel_idx][row_idx] = mult_value
            
            # Only emit event if requested (skip during tumble chain, emit at end)
            if emit_event:
                update_grid_mult_event(self)

    def get_clusters_update_wins(self):
        """Find clusters on board and update win manager with multiplier spots applied."""
        # Optimized: Only evaluate clusters if we need to (skip if board is empty)
        clusters = Cluster.get_clusters(self.board, "wild")
        
        # Early exit if no clusters found
        if not clusters:
            self.win_data = {"totalWin": 0, "wins": []}
            self.win_manager.update_spinwin(0)
            self.win_manager.tumble_win = 0
            return
        
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.board, self.win_data = self.evaluate_clusters_with_grid(
            config=self.config,
            board=self.board,
            clusters=clusters,
            pos_mult_grid=self.position_multipliers,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
        # Note: multiplier spots persist in free spins (not reset)
