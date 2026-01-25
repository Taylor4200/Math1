from copy import deepcopy

APPLY_TUMBLE_MULTIPLIER = "applyMultiplierToTumble"
UPDATE_GRID = "updateGrid"


def update_grid_mult_event(gamestate):
    """
    Pass updated position multipliers after a win.
    Frontend expects:
    - 0 = no multiplier
    - 1 = marked spot (shows "0x")
    - 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 = active multipliers
    
    IMPORTANT: If padding is enabled, the frontend board has extra rows:
    - Row 0: Top padding (no multipliers)
    - Rows 1-7: Main board (with multipliers)
    - Row 8: Bottom padding (no multipliers)
    """
    # Convert position_multipliers for frontend: marked spots (mult=0 but count=1) should send 1
    grid_for_frontend = []
    for reel_idx in range(len(gamestate.position_multipliers)):
        reel_row = []
        
        # If padding is enabled, add top padding row (always 0)
        if gamestate.config.include_padding:
            reel_row.append(0)
        
        # Add main board multipliers
        for row_idx in range(len(gamestate.position_multipliers[reel_idx])):
            mult_value = gamestate.position_multipliers[reel_idx][row_idx]
            explosion_count = gamestate.explosion_count[reel_idx][row_idx]
            
            # If multiplier is 0 but explosion_count is 1, it's a marked spot (send 1)
            if mult_value == 0 and explosion_count == 1:
                reel_row.append(1)
            else:
                # Otherwise send the actual multiplier value (0 for no hit, 2+ for active)
                reel_row.append(mult_value)
        
        # If padding is enabled, add bottom padding row (always 0)
        if gamestate.config.include_padding:
            reel_row.append(0)
        
        grid_for_frontend.append(reel_row)
    
    event = {
        "index": len(gamestate.book.events),
        "type": UPDATE_GRID,
        "gridMultipliers": grid_for_frontend,
    }
    gamestate.book.add_event(event)















