# Sticky Wild Multiplier Fix - CRITICAL BUG RESOLVED

## The Problem

**User Report**: "At the end of the game, when sticky wilds like 'clear' and the board settles at the VERY end sometimes I notice multipliers will CHANGE value when the bonus like 'ends'. They should ALWAYS be the same from start>end even after the sticky wilds or whatever are done."

## Root Cause

The sticky wild system was **NOT preserving padding symbols** (top and bottom rows). Here's what was happening:

### Board Structure
- **Internal board** (`self.board`): 5 rows (indices 0-4)
- **Padding symbols**: `self.top_symbols` and `self.bottom_symbols` (1 symbol each per reel)
- **Frontend board**: 7 rows total (padding + main board)
  - Row 0: Top padding
  - Rows 1-5: Main board
  - Row 6: Bottom padding

### The Bug
1. **Free Spin 1**: Wild lands in top padding (row 0) with multiplier 2
2. **Free Spin 2**: New board is drawn, padding symbols are regenerated
3. **Top padding wild gets a NEW multiplier** (e.g., 20 instead of 2)
4. **Result**: Multiplier changed! ❌

The sticky wild system was only tracking `self.board` (main board), NOT the padding symbols!

## The Fix

Added separate tracking for padding sticky wilds:

### 1. Added Padding Sticky Wild Storage

```python
def reset_book(self):
    super().reset_book()
    self.sticky_wilds = {}  # Main board sticky wilds
    self.sticky_top_padding = {}  # {reel: wild_symbol}
    self.sticky_bottom_padding = {}  # {reel: wild_symbol}
```

### 2. Updated `draw_board_with_sticky_wilds()` to Restore Padding

```python
# Apply sticky padding wilds
if self.config.include_padding:
    for reel_idx, wild_symbol in self.sticky_top_padding.items():
        if reel_idx < len(self.top_symbols):
            self.top_symbols[reel_idx] = wild_symbol
    for reel_idx, wild_symbol in self.sticky_bottom_padding.items():
        if reel_idx < len(self.bottom_symbols):
            self.bottom_symbols[reel_idx] = wild_symbol
```

### 3. Updated `update_sticky_wilds()` to Track Padding

```python
# Update padding sticky wilds
if self.config.include_padding:
    for reel_idx, symbol in enumerate(self.top_symbols):
        if symbol.name == "W":
            self.sticky_top_padding[reel_idx] = symbol
    for reel_idx, symbol in enumerate(self.bottom_symbols):
        if symbol.name == "W":
            self.sticky_bottom_padding[reel_idx] = symbol
```

### 4. Updated `clear_sticky_wilds()` to Clear Padding

```python
def clear_sticky_wilds(self) -> None:
    self.sticky_wilds = {}
    self.sticky_top_padding = {}
    self.sticky_bottom_padding = {}
```

## Test Results

### Before Fix:
```
[ERROR] Wild at position (4, 0) changed multiplier!
  free_spin_3: 2
  free_spin_5: 10  ❌ CHANGED!
```

### After Fix:
```
[OK] Wild at position (4, 0) stayed consistent:
  free_spin_3: 2
  free_spin_4: 2
  free_spin_5: 2  ✅ LOCKED IN!
  free_spin_6: 2
  free_spin_7: 2
  free_spin_8: 2
  free_spin_9: 2
  free_spin_10: 2

[SUCCESS] All multipliers remained consistent!
```

## Impact

✅ **Main board wilds**: Multipliers locked in (was already working)  
✅ **Top padding wilds**: Multipliers now locked in (FIXED)  
✅ **Bottom padding wilds**: Multipliers now locked in (FIXED)  
✅ **All positions**: Multipliers stay consistent from first appearance until bonus ends  

## Files Modified

- `games/0_0_lines_v9/game_override.py`
  - `reset_book()` - Added padding sticky wild storage
  - `draw_board_with_sticky_wilds()` - Restore padding sticky wilds
  - `update_sticky_wilds()` - Track padding sticky wilds
  - `clear_sticky_wilds()` - Clear padding sticky wilds

## Verification

Run the following to verify:
```bash
python games/0_0_lines_v9/run.py
```

All multipliers will now be **IRON LOCKED** from the moment they appear until the bonus completely ends!


