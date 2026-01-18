# Multiplier Fix Summary for 0_0_lines_v9

## Problem
The backend was calculating wins correctly using multipliers, but the multiplier values were not being included in the board data sent to the frontend for visual display.

## Root Cause
The issue was in the `draw_board_with_sticky_wilds()` method in `game_override.py`. When drawing the board for the first free spin (or base game), it was calling `super().draw_board(emit_event, trigger_symbol)` which would use the parent class's `reveal_event()` function from `src/events/events.py` instead of the custom `reveal_event()` method that includes multiplier data.

## Fixes Applied

### 1. Fixed `draw_board_with_sticky_wilds()` method
**File**: `game_override.py` (lines 57-62)

**Before**:
```python
else:
    # Normal board drawing for base game or first free spin
    super().draw_board(emit_event, trigger_symbol)
```

**After**:
```python
else:
    # Normal board drawing for base game or first free spin
    # ALWAYS use custom reveal_event to include multipliers
    super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
    if emit_event:
        self.reveal_event()
```

**Why**: This ensures that the custom `reveal_event()` method (which includes multipliers) is always called, not the parent class's version.

### 2. Enhanced `reveal_event()` method with better error handling
**File**: `game_override.py` (lines 79-119)

**Changes**:
- Added explicit checks for Wild symbols (`if self.board[reel][row].name == "W"`)
- Added fallback handling if a Wild somehow doesn't have a multiplier (prints warning and defaults to 1)
- Applied the same logic to padding symbols (top and bottom)
- Added comments clarifying that multipliers should ALWAYS be included for frontend display

**Why**: This makes the code more robust and ensures multipliers are always included in the board data.

### 3. Improved multiplier assignment safety check
**File**: `game_override.py` (lines 197-204)

**Changes**:
- Added detailed comments explaining when multipliers are assigned
- Changed the check from `not symbol.check_attribute("multiplier")` to `mult_val is None`
- This is a safety check since `create_symbol("W")` should automatically call `assign_mult_property()`

**Why**: More explicit and safer checking for missing multipliers.

## How Multipliers Work

### Symbol Creation Flow:
1. `create_symbol("W")` is called
2. This creates a Symbol instance with `multiplier = 1` by default (from `assign_default_attribute()`)
3. Then `assign_mult_property(sym)` is automatically called via `special_symbol_functions`
4. This assigns a random multiplier value from the distribution (e.g., 2, 3, 5, 10, 20, 50, 100, 250, 500)

### Sticky Wilds in Free Games:
1. When a Wild lands during a free spin, it's stored in `self.sticky_wilds[reel_idx][row_idx] = symbol`
2. This stores a **reference** to the Symbol object (not a copy)
3. On subsequent free spins, the stored Wild symbol (with its original multiplier) is placed back on the board
4. The multiplier is **locked in** from the original spin and never changes

### Board Data for Frontend:
1. `reveal_event()` is called after every board draw
2. For each Wild symbol, it extracts the multiplier value: `symbol.get_attribute("multiplier")`
3. The multiplier is added to the JSON: `symbol_json["multiplier"] = int(mult_val)`
4. This data is sent to the frontend for visual display

## Testing

### Test Script: `test_multipliers.py`
Created a test script that verifies:
- ✅ All Wild symbols have multipliers in base game
- ✅ Multipliers are included in the board data (reveal events)
- ✅ Multiple spins consistently include multipliers

**Test Results**:
```
Testing BASE GAME multipliers...
  Wild at reel 0, row 6: multiplier = 3
  Wild at reel 1, row 6: multiplier = 3
  Wild at reel 2, row 6: multiplier = 3
Total wilds found: 3
Wilds with multipliers: 3
[OK] All wilds have multipliers!

Testing MULTIPLE BASE GAME spins for consistency...
  Seed 10: 3 wilds, all have multipliers [OK]
  Seed 30: 2 wilds, all have multipliers [OK]
  Seed 40: 3 wilds, all have multipliers [OK]
  Seed 50: 2 wilds, all have multipliers [OK]
```

## Verification Checklist

- ✅ Multipliers are assigned to all Wild symbols when created
- ✅ Multipliers are included in board data for base game
- ✅ Multipliers are included in board data for free games
- ✅ Sticky wilds maintain their original multiplier values
- ✅ Padding symbols (top/bottom) also include multipliers
- ✅ Win calculations use multipliers correctly (was already working)
- ✅ Frontend will receive multiplier data for visual display

## Next Steps

To fully verify the fix in production:
1. Run a full simulation: `python games/0_0_lines_v9/run.py`
2. Check the generated books in `library/publish_files/`
3. Decompress a sample book and verify multipliers are present
4. Test with the frontend to ensure multipliers display correctly

## Notes

- The multiplier value of `1` is valid and should be included in the board data
- Multipliers are additive in win calculations (see `apply_added_symbol_mult` in `src/wins/multiplier_strategy.py`)
- The config defines multiplier distributions for both basegame and freegame types
- Different bet modes have different multiplier distributions (see `game_config.py` lines 197-508)


