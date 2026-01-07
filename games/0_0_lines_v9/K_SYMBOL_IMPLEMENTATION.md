# K Symbol Implementation - lines_v9

## Overview
This game implements a unique K symbol mechanic where K symbols drop wilds with multipliers randomly on the board. Wilds can stack and double their multipliers when landing on existing wilds.

## Key Features

### 1. Board Configuration
- **Size:** 5x5 grid (changed from 5x4)
- **Paylines:** 15 paylines (expanded for 5x5 board)
- **Game ID:** `0_0_lines_v9`

### 2. K Symbol Mechanic

#### How K Symbols Work
1. **K symbols land on reels** during normal gameplay
2. Each K has an attribute `wild_drops` (value: 1-5) determining how many wilds it drops
3. When processed, K drops wilds to **random positions** on the 5x5 board
4. **W symbols DO NOT appear organically** - they're only created by K symbols

#### Wild Dropping Logic
```python
def drop_wilds_from_k(num_drops):
    for each drop:
        - Pick random position (reel, row)
        - If position has existing wild:
            DOUBLE the multiplier (64x -> 128x -> 256x -> 512x...)
        - If position is empty:
            Create new wild with multiplier (2x-128x)
```

#### Multiplier System
- **Initial wild multipliers:** 2x, 3x, 5x, 10x, 20x, 50x, 100x, 128x
- **Doubling mechanism:** When wild lands on wild, multiplier * 2
- **No theoretical maximum** - can stack indefinitely (128x -> 256x -> 512x -> 1024x...)
- **Weighted distribution** favors lower multipliers, with 128x being rare

### 3. Feature Spin Modes

#### Feature Spin (Cost: 20x)
- **Guarantees 2 K symbols** on the board
- Each K drops 1-5 wilds
- **Total wild potential:** 2-10 wilds
- Configuration: `"force_k_symbols": 2`

#### Super Feature Spin (Cost: 750x)
- **Guarantees 5 K symbols** on the board
- Each K drops 1-5 wilds
- **Total wild potential:** 5-25 wilds
- **High stacking potential** - many opportunities for multiplier doubling
- Configuration: `"force_k_symbols": 5`

### 4. Integration with Sticky Wilds

#### Free Game Behavior
1. K symbols can land during free spins
2. Wilds dropped by K become sticky (remain for all spins)
3. **Critical:** K symbols can drop wilds **on existing sticky wilds**, doubling their multipliers
4. Creates exponential growth potential:
   - Spin 1: K drops 128x wild at position (2,2)
   - Spin 3: Another K drops wild at same position (2,2) -> now 256x
   - Spin 5: Another K drops wild at (2,2) -> now 512x
   - This sticky wild with high multiplier stays for ALL remaining spins

### 5. Technical Implementation

#### Files Modified
1. **game_config.py**
   - Changed `num_rows` from `[4]*5` to `[5]*5`
   - Added K to `special_symbols`: `"key": ["K"]`
   - Updated paylines for 5x5 board (15 paylines)
   - Modified Feature/Super Feature distributions with `force_k_symbols`

2. **game_override.py**
   - Added `assign_key_drop_count()` - assigns 1-5 wild drops to K
   - Added `process_k_symbols()` - finds all K symbols and processes them
   - Added `drop_wilds_from_k()` - core logic for dropping wilds
   - Added `_get_k_wild_multiplier()` - weighted multiplier selection
   - Added `_force_k_symbol_board()` - forces K symbols for feature modes
   - Updated `draw_board()` - processes K symbols after board draw
   - Updated `draw_board_with_sticky_wilds()` - processes K in free games

3. **readme.txt**
   - Complete rewrite documenting K symbol mechanic
   - Explained doubling behavior
   - Documented feature spin modes

#### Symbol Attribute Structure
```python
# K Symbol
K_symbol = {
    "name": "K",
    "wild_drops": 3  # Will drop 3 wilds
}

# Wild Symbol (dropped by K)
W_symbol = {
    "name": "W",
    "multiplier": 64  # Can be 2, 3, 5, 10, 20, 50, 100, 128
}
```

### 6. Game Flow

#### Base Game
```
1. Draw reels -> Board may have K symbols
2. Process K symbols -> Drop wilds randomly
3. Evaluate line wins with wild multipliers
4. Check for scatter triggers (free spins)
```

#### Free Game
```
1. Draw reels (preserve sticky wilds)
2. Process K symbols -> Drop wilds (can land on sticky wilds, doubling them)
3. Update sticky wilds (add any new wilds)
4. Evaluate line wins
5. Repeat for all free spins
6. Clear sticky wilds
```

#### Feature Spin (20x cost)
```
1. Force 2 K symbols on board
2. Each K drops 1-5 wilds
3. Process immediately
4. Evaluate wins
```

#### Super Feature Spin (750x cost)
```
1. Force 5 K symbols on board
2. Each K drops 1-5 wilds (potential 5-25 wilds)
3. Multiple wilds likely to land on same positions
4. Multipliers stack through doubling
5. High win potential
```

### 7. Variance Analysis

#### High Variance Sources
1. **Random drop positions** - Can concentrate on paylines or spread out
2. **Overlap probability** - 5 K symbols dropping on 25 positions = high overlap chance
3. **Multiplier doubling** - Exponential growth (2x -> 4x -> 8x -> 16x...)
4. **Sticky wild accumulation** - Free games build up wilds over 10-12 spins
5. **Cascade potential** - Super Feature Spin can create mega multipliers

#### Win Cap Considerations
- Game has 10,000x wincap
- Super Feature Spin (5 K symbols) can realistically approach wincap
- Multiplier doubling creates potential for extreme wins
- Recommend monitoring distribution quota for wincap (currently 0.002 = 0.2%)

### 8. Important Notes

#### W Symbol Placement
- **DO NOT add W to reel strips** - they should only be created by K symbols
- W in paytable is fine (5W = 50x payout)
- W multiplier property still used for line win multiplication

#### K Symbol in Paytable
- K should **NOT** be in paytable (it's a trigger symbol, not a paying symbol)
- K doesn't contribute to line wins
- K is removed/ignored during line evaluation

#### Reels Configuration
- Make sure K symbol frequency is balanced across reels
- Consider removing or minimizing W from reel strips (if present)
- Scatters still work normally for free spin triggers

### 9. Testing Checklist

- [ ] Verify K symbols drop correct number of wilds (1-5)
- [ ] Confirm wilds landing on wilds double multipliers
- [ ] Test Feature Spin forces exactly 2 K symbols
- [ ] Test Super Feature Spin forces exactly 5 K symbols
- [ ] Verify sticky wilds work with K drops in free games
- [ ] Check multiplier doubling works with sticky wilds
- [ ] Confirm W symbols don't appear organically on reels
- [ ] Test extreme cases (all K drops on same position)
- [ ] Verify wincap triggers correctly
- [ ] Check that K symbols don't contribute to line wins

### 10. Configuration Summary

```python
# Board
num_reels = 5
num_rows = [5, 5, 5, 5, 5]

# Special Symbols
special_symbols = {
    "wild": ["W"],
    "scatter": ["S"],
    "multiplier": ["W"],
    "key": ["K"]
}

# Feature Modes
Feature Spin: force_k_symbols = 2
Super Feature Spin: force_k_symbols = 5

# K Wild Multipliers (weights)
{2: 100, 3: 80, 5: 60, 10: 40, 20: 20, 50: 10, 100: 5, 128: 2}
```

## Future Enhancements

1. **K Symbol Variants**
   - Golden K: Drops only high multiplier wilds (50x-128x)
   - Multi K: Always drops exactly 5 wilds
   
2. **Visual Effects**
   - Animate K symbol dropping wilds
   - Show multiplier doubling with special effect
   - Highlight sticky wilds in free games

3. **Additional Modes**
   - "K Frenzy": Increased K symbol frequency
   - "Multiplier Mania": Guaranteed multiplier doubling

4. **Analytics**
   - Track average wilds dropped per K
   - Monitor multiplier stacking frequency
   - Analyze overlap probability in practice

