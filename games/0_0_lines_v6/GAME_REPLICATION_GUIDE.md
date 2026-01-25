# Game Replication Guide - Lines V6 (Gates of Olympus Style)

## Table of Contents
1. [Game Overview](#game-overview)
2. [Board & Symbol Setup](#board--symbol-setup)
3. [Paytable Configuration](#paytable-configuration)
4. [Multiplier System](#multiplier-system)
5. [Tumble Mechanics](#tumble-mechanics)
6. [Free Spin System](#free-spin-system)
7. [Game Flow Implementation](#game-flow-implementation)
8. [Win Calculation Logic](#win-calculation-logic)
9. [Implementation Checklist](#implementation-checklist)

---

## Game Overview

**Game Type:** Scatter Pay Slot (No Paylines)  
**Style:** Gates of Olympus (Pragmatic Play inspired)  
**RTP:** 96.30%  
**Max Win:** 10,000x bet  
**Core Mechanics:** Scatter pays, Tumbles, Multiplier symbols

### Key Features
- 6 reels × 5 rows (30 positions)
- Symbols pay anywhere when 8+ appear
- Winning symbols explode and new ones fall (tumble)
- Multiplier symbols enhance wins
- Free spins with cumulative multipliers
- No traditional paylines

---

## Board & Symbol Setup

### Board Dimensions
```
Reels: 6 columns
Rows: 5 per reel
Total positions: 30
Layout: [5, 5, 5, 5, 5, 5] (rows per reel)
```

### Symbol Types

#### Regular Symbols (8 types)

**High Symbols (3):**
- `H1` - Red Crown/Gem (Highest paying)
- `H2` - Purple/Gold Ring
- `H3` - Gold/Purple Hourglass

**Low Symbols (4):**
- `L1` - Red Gem
- `L2` - Purple Gem
- `L3` - Gold Gem
- `L4` - Green Gem (Lowest paying)

**Special Symbols (2):**
- `S` - Scatter (triggers free spins, doesn't explode)
- `M` - Multiplier (has weighted random values, doesn't explode)

### Symbol Hierarchy
```
H1 > H2 > H3 > L1 > L2 > L3 > L4
```

---

## Paytable Configuration

### Scatter Pay Rules
- **Minimum:** 8+ symbols of the same type anywhere on board
- **No pattern required:** Symbols can be in any position
- **Multiple wins:** Different symbol types can win simultaneously

### Paytable (All values in bet multipliers)

#### H1 - Red Crown/Gem
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 10.0x  |
| 10-11       | 25.0x  |
| 12-30       | 50.0x  |

#### H2 - Purple/Gold Ring
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 2.0x   |
| 10-11       | 5.0x   |
| 12-30       | 15.0x  |

#### H3 - Gold/Purple Hourglass
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 1.5x   |
| 10-11       | 2.0x   |
| 12-30       | 12.0x  |

#### L1 - Red Gem
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 0.5x   |
| 10-11       | 1.0x   |
| 12-30       | 8.0x   |

#### L2 - Purple Gem
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 0.4x   |
| 10-11       | 0.5x   |
| 12-30       | 5.0x   |

#### L3 - Gold Gem
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 0.30x  |
| 10-11       | 0.80x  |
| 12-30       | 4.0x   |

#### L4 - Green Gem
| Symbol Count | Payout |
|-------------|--------|
| 8-9         | 0.30x  |
| 10-11       | 0.30x  |
| 12-30       | 2.0x   |

### Implementation Format
```python
paytable = {
    # H1 - Red Crown/Gem
    (8, "H1"): 10.0,
    (9, "H1"): 10.0,
    (10, "H1"): 25.0,
    (11, "H1"): 25.0,
    (12, "H1"): 50.0,
    # ... (13-30 all pay 50.0)
    
    # Repeat for all symbols H2, H3, L1, L2, L3, L4
}
```

---

## Multiplier System

### Multiplier Symbol (M)

The `M` symbol is special:
- Does NOT explode during tumbles (stays on board)
- Each `M` has a weighted random multiplier value
- Values differ between base game and free game

### Base Game Multiplier Distribution

```python
base_multiplier_weights = {
    2: 25,      # 2x multiplier (weight: 25)
    3: 22,      # 3x multiplier (weight: 22)
    4: 18,      # 4x multiplier (weight: 18)
    5: 15,      # 5x multiplier (weight: 15)
    6: 12,      # 6x multiplier (weight: 12)
    8: 10,      # 8x multiplier (weight: 10)
    10: 8,      # 10x multiplier (weight: 8)
    15: 5,      # 15x multiplier (weight: 5)
    20: 3,      # 20x multiplier (weight: 3)
    25: 2,      # 25x multiplier (weight: 2)
    50: 1,      # 50x multiplier (weight: 1)
    100: 0.5,   # 100x multiplier (weight: 0.5)
    250: 0.2,   # 250x multiplier (weight: 0.2)
    500: 0.1    # 500x multiplier (weight: 0.1)
}
```

**Note:** Higher multiplier values are rarer (lower weights).

### Free Game Multiplier Distribution

```python
free_multiplier_weights = {
    2: 20,      # Slightly lower weight for small values
    3: 20,
    4: 18,
    5: 15,
    6: 12,
    8: 10,
    10: 8,
    15: 6,      # Higher weights for medium-high values
    20: 4,
    25: 3,
    50: 2,
    100: 1.5,
    250: 0.5,
    500: 0.2
}
```

**Note:** Free game has better distribution for higher multipliers.

### Multiplier Selection Logic

```python
def assign_multiplier_value(symbol, game_type):
    """Assign a random multiplier value based on weighted distribution."""
    if game_type == "base":
        weights = base_multiplier_weights
    else:  # free game
        weights = free_multiplier_weights
    
    # Weighted random selection
    multiplier_value = weighted_random_choice(weights)
    symbol.multiplier = multiplier_value
    return symbol
```

---

## Tumble Mechanics

### How Tumbles Work

1. **Initial Board:** Draw symbols from reel strips
2. **Evaluate Wins:** Count each symbol type, check paytable
3. **Mark Winners:** Symbols with 8+ count are marked to explode
4. **Explode:** Remove winning symbols (except S and M)
5. **Cascade:** Symbols above fall down to fill gaps
6. **Refill:** New symbols drop from top
7. **Repeat:** Re-evaluate wins until no more wins exist

### Tumble Rules

| Symbol Type | Explodes? | Notes |
|-------------|-----------|-------|
| H1-H3, L1-L4 | ✅ Yes | Regular symbols explode when they win |
| S (Scatter) | ❌ No | Stays on board during tumbles |
| M (Multiplier) | ❌ No | Stays on board during tumbles |

### Tumble Chain Example

```
Initial Board:
- 10 H1 symbols → Win = 25.0x
- H1 symbols explode

After Tumble 1:
- New symbols fall
- 8 L1 symbols → Win = 0.5x
- L1 symbols explode

After Tumble 2:
- New symbols fall
- No wins → Stop tumbling
- Total win from tumbles: 25.0 + 0.5 = 25.5x
```

### Implementation Pseudocode

```python
def run_tumbles():
    total_win = 0
    
    while True:
        # Evaluate scatter pays
        win = evaluate_scatter_pays()
        total_win += win
        
        if win == 0:
            break  # No more wins, stop tumbling
        
        # Mark winning symbols (except S and M)
        mark_symbols_to_explode(exclude=["S", "M"])
        
        # Remove exploding symbols
        explode_symbols()
        
        # Cascade symbols down
        cascade_symbols()
        
        # Refill from top
        refill_board()
    
    return total_win
```

---

## Free Spin System

### Trigger Conditions

**Base Game:**
- 3+ scatter symbols (S) anywhere on board
- Awards: 10 free spins

**During Free Spins (Retrigger):**
- 3+ scatter symbols (S) anywhere on board
- Awards: +5 additional free spins

### Free Spin Mechanics

#### Key Differences from Base Game

| Feature | Base Game | Free Spins |
|---------|-----------|------------|
| Multiplier Application | Sum of all M values (one-time) | Cumulative (adds up across spins) |
| Multiplier Persistence | Resets each spin | Accumulates throughout bonus |
| Retrigger | N/A | 3 scatters = +5 spins |
| Reel Strips | Base game reels | Free game reels |

#### Cumulative Multiplier System

The cumulative multiplier is the defining feature of free spins:

1. **Initialize:** `cumulative_multiplier = 0` at start of bonus
2. **Each Spin:**
   - Complete all tumbles
   - Sum multiplier values on board (if any M symbols present)
   - **Add to cumulative:** `cumulative_multiplier += board_multiplier_sum`
   - **Multiply win:** `final_win = base_win × cumulative_multiplier`
3. **Persist:** Cumulative carries to next spin
4. **End:** Cumulative resets when bonus ends

#### Cumulative Multiplier Example

```
Bonus Start: cumulative = 0

Spin 1:
- Base win from tumbles: 10x
- M symbols on board: 2x, 3x (sum = 5)
- cumulative = 0 + 5 = 5
- Final win: 10 × 5 = 50x

Spin 2:
- Base win from tumbles: 5x
- M symbols on board: 10x (sum = 10)
- cumulative = 5 + 10 = 15
- Final win: 5 × 15 = 75x

Spin 3:
- Base win from tumbles: 8x
- No M symbols on board (sum = 0)
- cumulative = 15 + 0 = 15 (stays same)
- Final win: 8 × 15 = 120x

Spin 4:
- Base win from tumbles: 0x (no wins)
- M symbols on board: 20x (sum = 20)
- cumulative = 15 + 20 = 35
- Final win: 0 × 35 = 0x (no wins to multiply)

Total Bonus Win: 50 + 75 + 120 + 0 = 245x
```

**Important:** If a spin has no wins from tumbles, multipliers still add to cumulative but don't contribute to that spin's win (0 × multiplier = 0).

### Free Spin Implementation

```python
def run_free_spins(total_spins):
    cumulative_multiplier = 0
    total_bonus_win = 0
    current_spin = 0
    
    while current_spin < total_spins:
        current_spin += 1
        
        # Draw board and run tumbles
        draw_board(use_free_game_reels=True)
        base_win = run_tumbles()
        
        # Get multiplier sum from board
        board_multiplier_sum = get_board_multipliers_sum()
        
        # Add to cumulative
        cumulative_multiplier += board_multiplier_sum
        
        # Apply cumulative to win (only if cumulative > 0)
        if cumulative_multiplier > 0:
            final_win = base_win * cumulative_multiplier
        else:
            final_win = base_win
        
        total_bonus_win += final_win
        
        # Check for retrigger
        scatter_count = count_symbols("S")
        if scatter_count >= 3:
            total_spins += 5  # Add 5 more spins
    
    return total_bonus_win
```

---

## Game Flow Implementation

### Base Game Spin Flow

```python
def run_base_game_spin():
    # 1. Draw initial board
    board = draw_board(use_base_game_reels=True)
    
    # 2. Run tumbles and accumulate wins
    tumble_win = run_tumbles()
    
    # 3. Get multiplier sum from board
    multiplier_sum = get_board_multipliers_sum()
    
    # 4. Apply multipliers to total tumble win
    if multiplier_sum > 0:
        final_win = tumble_win * multiplier_sum
    else:
        final_win = tumble_win
    
    # 5. Check for free spin trigger
    scatter_count = count_symbols("S")
    if scatter_count >= 3:
        bonus_win = run_free_spins(total_spins=10)
        final_win += bonus_win
    
    return final_win
```

### Tumble Loop

```python
def run_tumbles():
    total_win = 0
    
    while True:
        # Count each symbol type
        symbol_counts = count_all_symbols()
        
        # Evaluate wins from paytable
        spin_win = 0
        for symbol, count in symbol_counts.items():
            if count >= 8:  # Minimum for scatter pay
                payout = get_paytable_value(symbol, count)
                spin_win += payout
        
        # If no wins, stop tumbling
        if spin_win == 0:
            break
        
        # Add to total
        total_win += spin_win
        
        # Explode winning symbols (except S and M)
        explode_winning_symbols(exclude=["S", "M"])
        
        # Cascade and refill
        cascade_symbols()
        refill_board()
    
    return total_win
```

---

## Win Calculation Logic

### Step-by-Step Win Calculation

#### Base Game

```
1. Draw board from base game reels
2. Tumble Loop:
   a. Count each symbol type
   b. For each symbol with 8+ count:
      - Look up payout in paytable
      - Add to tumble_win
   c. If tumble_win > 0:
      - Explode winning symbols (not S or M)
      - Cascade and refill
      - Repeat from step 2a
   d. If tumble_win = 0:
      - Exit loop
3. Sum all multiplier (M) values on board
4. Final win = tumble_win × multiplier_sum
   (If multiplier_sum = 0, final win = tumble_win)
5. Check for free spin trigger (3+ S symbols)
```

#### Free Game

```
1. Initialize cumulative_multiplier = 0
2. For each free spin:
   a. Draw board from free game reels
   b. Tumble Loop (same as base game):
      - Accumulate tumble_win
   c. Sum all multiplier (M) values on board
   d. cumulative_multiplier += board_multiplier_sum
   e. If cumulative_multiplier > 0:
      - spin_final_win = tumble_win × cumulative_multiplier
      Else:
      - spin_final_win = tumble_win
   f. Add spin_final_win to total_bonus_win
   g. Check for retrigger (3+ S symbols = +5 spins)
3. Return total_bonus_win
```

### Multiplier Application Examples

#### Base Game Example

```
Board after tumbles:
- Tumble win: 25.5x
- M symbols: 2x, 5x, 10x
- Multiplier sum: 2 + 5 + 10 = 17x
- Final win: 25.5 × 17 = 433.5x
```

#### Free Game Example

```
Spin 1:
- Tumble win: 10x
- M symbols: 2x, 3x (sum = 5)
- Cumulative: 0 + 5 = 5
- Final: 10 × 5 = 50x

Spin 2:
- Tumble win: 5x
- M symbols: 10x (sum = 10)
- Cumulative: 5 + 10 = 15
- Final: 5 × 15 = 75x

Spin 3:
- Tumble win: 8x
- No M symbols (sum = 0)
- Cumulative: 15 + 0 = 15
- Final: 8 × 15 = 120x

Total: 50 + 75 + 120 = 245x
```

---

## Implementation Checklist

### Core Components

- [ ] **Board System**
  - [ ] 6×5 grid (30 positions)
  - [ ] Symbol creation (H1-H3, L1-L4, S, M)
  - [ ] Board drawing from reel strips
  - [ ] Separate base/free game reels

- [ ] **Paytable**
  - [ ] Range-based scatter pays (8-9, 10-11, 12-30)
  - [ ] All 8 symbol types configured
  - [ ] Count-based lookup function

- [ ] **Multiplier System**
  - [ ] Weighted random selection
  - [ ] Base game distribution (14 values)
  - [ ] Free game distribution (14 values)
  - [ ] Multiplier assignment to M symbols

- [ ] **Tumble Mechanics**
  - [ ] Win evaluation loop
  - [ ] Symbol explosion (exclude S and M)
  - [ ] Cascade logic (symbols fall down)
  - [ ] Refill from top
  - [ ] Repeat until no wins

- [ ] **Win Calculation**
  - [ ] Scatter pay evaluation
  - [ ] Multiple symbol wins simultaneously
  - [ ] Multiplier sum calculation
  - [ ] Base game: tumble_win × multiplier_sum
  - [ ] Free game: tumble_win × cumulative_multiplier

- [ ] **Free Spin System**
  - [ ] Trigger detection (3+ S symbols)
  - [ ] 10 free spins awarded
  - [ ] Cumulative multiplier tracking
  - [ ] Retrigger logic (3+ S = +5 spins)
  - [ ] Separate free game reels

- [ ] **Special Symbol Handling**
  - [ ] S (Scatter) doesn't explode
  - [ ] M (Multiplier) doesn't explode
  - [ ] M gets random value on creation

### Testing Scenarios

- [ ] **Basic Wins**
  - [ ] 8 symbols of same type pays correctly
  - [ ] 10 symbols pays higher tier
  - [ ] 12+ symbols pays highest tier
  - [ ] Multiple symbol types win together

- [ ] **Tumble Tests**
  - [ ] Winning symbols explode
  - [ ] S and M symbols stay on board
  - [ ] Symbols cascade down correctly
  - [ ] New symbols refill from top
  - [ ] Multiple tumbles chain correctly

- [ ] **Multiplier Tests**
  - [ ] M symbols get random values
  - [ ] Base game: sum applied once
  - [ ] Free game: cumulative adds up
  - [ ] No multipliers = no multiplication

- [ ] **Free Spin Tests**
  - [ ] 3 S symbols trigger 10 spins
  - [ ] Cumulative starts at 0
  - [ ] Cumulative persists across spins
  - [ ] Retrigger adds 5 spins
  - [ ] Cumulative resets after bonus ends

- [ ] **Edge Cases**
  - [ ] No wins (0x payout)
  - [ ] Wins with no multipliers
  - [ ] Multipliers with no wins
  - [ ] Max win cap (10,000x)

---

## Key Implementation Notes

### Critical Rules

1. **Scatter Pays:** Minimum 8 symbols required, no pattern needed
2. **Persistent Symbols:** S and M never explode during tumbles
3. **Multiplier Timing:** Applied AFTER all tumbles complete
4. **Cumulative Logic:** Only in free spins, adds each spin's M values
5. **Retrigger:** Only during free spins, adds +5 spins (not +10)

### Common Pitfalls

❌ **Don't:**
- Apply multipliers during tumbles (wait until all tumbles finish)
- Explode S or M symbols
- Reset cumulative multiplier between free spins
- Award 10 spins on retrigger (it's +5)
- Apply cumulative multiplier in base game

✅ **Do:**
- Count all symbols on board for scatter pays
- Keep S and M on board during tumbles
- Apply multipliers once after all tumbles
- Use cumulative multiplier in free spins
- Add M values to cumulative even if no wins

### Performance Considerations

- Tumbles can chain multiple times (5-10+ tumbles possible)
- Free spins can retrigger multiple times (20-30+ total spins)
- Cumulative multiplier can grow very large (100x+)
- Max win cap should stop game at 10,000x

---

## Summary

This game is a **scatter-pay slot** with these core mechanics:

1. **6×5 board** with 8 regular symbols + 2 special symbols
2. **Scatter pays** require 8+ symbols anywhere (no paylines)
3. **Tumble mechanics** explode winners and refill (except S and M)
4. **Multiplier symbols (M)** enhance wins with weighted random values
5. **Base game:** Multiply total tumble win by sum of M values
6. **Free spins:** Cumulative multiplier system (adds up across spins)
7. **Trigger:** 3+ S symbols = 10 free spins (retrigger = +5)

The math is balanced through:
- Symbol frequencies on reel strips
- Multiplier value weights
- Paytable ranges (8-9, 10-11, 12-30)
- RTP target: 96.30%
- Max win: 10,000x bet

---

## Additional Resources

### File Structure
```
game_config.py       - Paytable, multiplier distributions, game parameters
game_override.py     - Custom logic for multipliers and forced outcomes
gamestate.py         - Main game flow (spin, tumbles, free spins)
game_executables.py  - Win calculation, multiplier application
reels/BR0.csv        - Base game reel strips
reels/FR0.csv        - Free game reel strips
```

### Key Functions to Implement

```python
# Core functions needed
draw_board(use_free_game_reels)
run_tumbles()
evaluate_scatter_pays()
explode_symbols(exclude)
cascade_symbols()
refill_board()
get_board_multipliers_sum()
assign_multiplier_value(symbol, game_type)
run_free_spins(total_spins)
check_free_spin_trigger()
apply_cumulative_multiplier(base_win, cumulative)
```

---

**End of Replication Guide**
