# Complete Math System Explanation - 0_0_lines_v6 (Gates of Olympus Style)

## Table of Contents
1. [Game Overview](#game-overview)
2. [Board Structure](#board-structure)
3. [Symbol System](#symbol-system)
4. [Win Mechanics - Scatter Pays](#win-mechanics---scatter-pays)
5. [Multiplier System](#multiplier-system)
6. [Tumble Mechanics](#tumble-mechanics)
7. [Free Spin System](#free-spin-system)
8. [Bet Modes & Costs](#bet-modes--costs)
9. [Distribution System](#distribution-system)
10. [RTP & Optimization Targets](#rtp--optimization-targets)
11. [Game Flow](#game-flow)

---

## Game Overview

**Game ID:** `0_0_lines_v6`  
**Style:** Gates of Olympus (Pragmatic Play style)  
**Base RTP:** 96.30%  
**Max Win:** 5,000x bet  
**Win Type:** Scatter Pays (no paylines)

---

## Board Structure

- **Reels:** 6 columns
- **Rows:** 5 rows per reel
- **Total Positions:** 30 (6 × 5)
- **Padding:** Enabled (hidden symbols above/below visible area)

### Reel Files
- `BR0.csv` - Base game reels
- `FR0.csv` - Free game reels  
- `FRWCAP.csv` - Free game reels for max win scenarios

---

## Symbol System

### Regular Symbols (8 types)

**High Symbols (3):**
- **H1** - Red Crown/Gem (Highest paying)
- **H2** - Purple/Gold Ring
- **H3** - Gold/Purple Hourglass

**Low Symbols (4):**
- **L1** - Red Gem
- **L2** - Purple Gem
- **L3** - Gold Gem
- **L4** - Green Gem (Lowest paying)

**Special Symbols (2):**
- **S** - Scatter (triggers free spins)
- **M** - Multiplier (single symbol with weighted random values)

### Symbol Hierarchy (Pay Order)
H1 > H2 > H3 > L1 > L2 > L3 > L4

---

## Win Mechanics - Scatter Pays

**NO PAYLINES** - Symbols pay anywhere on the board when minimum count is reached.

### Minimum Win Requirement
- **8+ symbols** of the same type must appear on the board
- Symbols can be anywhere (no specific pattern required)

### Paytable Structure

Each symbol has **3 payout tiers** based on count ranges:

#### H1 (Red Crown/Gem) - Highest Payer
- **8-9 symbols:** 10.0x bet
- **10-11 symbols:** 25.0x bet
- **12-30 symbols:** 50.0x bet

#### H2 (Purple/Gold Ring)
- **8-9 symbols:** 2.0x bet
- **10-11 symbols:** 5.0x bet
- **12-30 symbols:** 15.0x bet

#### H3 (Gold/Purple Hourglass)
- **8-9 symbols:** 1.5x bet
- **10-11 symbols:** 2.0x bet
- **12-30 symbols:** 12.0x bet

#### L1 (Red Gem)
- **8-9 symbols:** 0.5x bet
- **10-11 symbols:** 1.0x bet
- **12-30 symbols:** 8.0x bet

#### L2 (Purple Gem)
- **8-9 symbols:** 0.4x bet
- **10-11 symbols:** 0.5x bet
- **12-30 symbols:** 5.0x bet

#### L3 (Gold Gem)
- **8-9 symbols:** 0.30x bet (30 cents)
- **10-11 symbols:** 0.80x bet (80 cents)
- **12-30 symbols:** 4.0x bet

#### L4 (Green Gem) - Lowest Payer
- **8-9 symbols:** 0.30x bet (30 cents)
- **10-11 symbols:** 0.30x bet (30 cents)
- **12-30 symbols:** 2.0x bet

### Win Calculation Process

1. **Count symbols** of each type on the board
2. **Check paytable** for each symbol type with 8+ count
3. **Sum all wins** from different symbol types
4. **Apply multipliers** (see Multiplier System section)

**Example:**
- 10 H1 symbols = 25.0x bet
- 9 L1 symbols = 0.5x bet
- **Total before multiplier:** 25.5x bet

---

## Multiplier System

### Multiplier Symbol (M)

- **Single symbol type:** Only "M" exists (frontend handles visual variety)
- **Weighted random values:** Each M symbol gets a random multiplier value
- **Distribution differs** between base game and free game

### Base Game Multiplier Distribution

```python
{
    2: 25,    # 2x multiplier (weight: 25)
    3: 22,    # 3x multiplier (weight: 22)
    4: 18,    # 4x multiplier (weight: 18)
    5: 15,    # 5x multiplier (weight: 15)
    6: 12,    # 6x multiplier (weight: 12)
    8: 10,    # 8x multiplier (weight: 10)
    10: 8,    # 10x multiplier (weight: 8)
    15: 6,    # 15x multiplier (weight: 6)
    20: 4,    # 20x multiplier (weight: 4)
    25: 3,    # 25x multiplier (weight: 3)
    50: 2,    # 50x multiplier (weight: 2)
    100: 1.5, # 100x multiplier (weight: 1.5)
    250: 0.5, # 250x multiplier (weight: 0.5)
    500: 0.2  # 500x multiplier (weight: 0.2)
}
```

**Higher values are rarer** (lower weights).

### Free Game Multiplier Distribution

```python
{
    2: 20,    # Slightly lower weights for small multipliers
    3: 20,
    4: 18,
    5: 15,
    6: 12,
    8: 10,
    10: 8,
    15: 6,    # Higher weights for medium-high multipliers
    20: 4,
    25: 3,
    50: 2,
    100: 1.5,
    250: 0.5,
    500: 0.2
}
```

**Free game has better distribution** for higher multipliers.

### Multiplier Application

#### Base Game
1. After all tumbles complete
2. **Sum all multiplier values** on the board
3. **Multiply win** by the sum
4. If sum = 0 (no multipliers), win stays unchanged

**Formula:** `Final Win = Base Win × Sum of All Multiplier Values`

**Example:**
- Base win: 25.5x bet
- M symbols on board: 2x, 5x, 10x
- Sum: 2 + 5 + 10 = 17x
- **Final win:** 25.5 × 17 = **433.5x bet**

#### Free Game (Bonus)
1. **Cumulative multiplier system**
2. Start with cumulative = 0
3. After each spin's tumbles:
   - If multipliers land: **Add their values to cumulative**
   - **Multiply win by NEW cumulative total** (includes just-landed multipliers)
4. Cumulative persists across all free spins
5. If no multipliers land: win stays as is (no multiplication)

**Formula:** `Cumulative = Previous Cumulative + New Multipliers`  
**Formula:** `Spin Win = Base Win × New Cumulative`

**Example:**
- Spin 1: Win = 10x, Multipliers = 2x, 3x → Cumulative = 5, Final = 10 × 5 = 50x
- Spin 2: Win = 5x, Multipliers = 10x → Cumulative = 15, Final = 5 × 15 = 75x
- Spin 3: Win = 8x, No multipliers → Cumulative = 15, Final = 8 × 15 = 120x
- **Total bonus win:** 50 + 75 + 120 = 245x bet

---

## Tumble Mechanics

### How Tumbles Work

1. **Winning symbols explode** (removed from board)
2. **Symbols above fall down** to fill empty spaces
3. **New symbols drop** from top to fill remaining positions
4. **Re-evaluate wins** on the new board
5. **Repeat** until no more wins (or wincap triggered)

### Tumble Restrictions

- **Scatter symbols (S)** do NOT explode (stay on board)
- **Multiplier symbols (M)** do NOT explode (stay on board)
- Only **regular winning symbols** (H1-H3, L1-L4) explode

### Tumble Chain Example

**Initial Board:**
- 10 H1 symbols → Win = 25.0x bet
- H1 symbols explode

**After Tumble 1:**
- New symbols fall in
- 8 L1 symbols → Win = 0.5x bet
- L1 symbols explode

**After Tumble 2:**
- No more wins → Tumble chain ends
- **Total base win:** 25.0 + 0.5 = 25.5x bet

### Multiplier Application After Tumbles

- Multipliers are applied **ONCE** after all tumbles complete
- Not per tumble, but to the **total win from all tumbles**

---

## Free Spin System

### Trigger Conditions

- **3+ scatter symbols (S)** on base game board
- **Awards:** 10 free spins

### Free Spin Mechanics

1. **10 free spins** awarded
2. Each spin follows same tumble rules
3. **Cumulative multipliers** (see Multiplier System)
4. **Retrigger:** 3+ scatters during free spins = +5 additional spins
5. **Max win protection:** If wincap (5,000x) is reached, free spins stop immediately

### Free Spin Retrigger

- **3 scatters** during free spins
- **Adds:** +5 free spins to remaining count
- Can retrigger multiple times
- No limit on total free spins (except wincap)

---

## Bet Modes & Costs

### 1. Base Mode

**Cost:** 1.0x bet  
**RTP:** 96.30%  
**Max Win:** 5,000x bet  
**Type:** Regular spin (not a buy bonus)

**Distributions:**
- **wincap (1%):** Forces max win outcome
- **freegame (15%):** Regular bonus trigger (3 scatters)
- **super_freegame (4%):** Super bonus trigger (4 scatters) - enhanced multipliers
- **0 (1%):** Zero win spins
- **basegame (79.8%):** Regular base game spins

### 2. Wrath of Olympus (Buy Bonus)

**Cost:** 100.0x bet  
**RTP:** 96.00%  
**Max Win:** 5,000x bet  
**Type:** Buy bonus (guaranteed free spins)

**Distributions:**
- **wincap (0.2%):** Forces max win outcome
- **freegame (99.9%):** Guaranteed 3 scatters → 10 free spins (enhanced multipliers)

**Special Features:**
- **Guaranteed free spins** (99.9% quota)
- **Enhanced multiplier distribution** in free spins
- **3 scatters guaranteed** on base spin (triggers bonus)

### 3. Super Wrath of Olympus (Buy Super Bonus)

**Cost:** 500.0x bet  
**RTP:** 95.80%  
**Max Win:** 5,000x bet  
**Type:** Buy super bonus (premium multipliers)

**Distributions:**
- **wincap (0.2%):** Forces max win outcome
- **freegame (99.9%):** Guaranteed 3 scatters → 10 free spins (premium multipliers)

**Special Features:**
- **Premium multiplier distribution** (higher values more common)
- **Guaranteed free spins** with enhanced multipliers
- **3 scatters guaranteed** on base spin

### 4. Bonus Booster (Feature Spin)

**Cost:** 2.0x bet  
**RTP:** 96.00%  
**Max Win:** 5,000x bet  
**Type:** Feature spin (persists after each round)

**Distributions:**
- **wincap (1%):** Forces max win outcome
- **freegame_boosted (20%):** Increased bonus trigger rate (5x scatter chance)
- **0 (1%):** Zero win spins
- **basegame_boosted (78.8%):** Enhanced base game (better multiplier distribution)

**Special Features:**
- **5x higher scatter chance** (more frequent bonuses)
- **Enhanced multiplier distribution** in base game
- **Feature persists** after each spin (not one-time)

### 5. Divine Strikes (Multiplier Feature)

**Cost:** 20.0x bet  
**RTP:** 96.00%  
**Max Win:** 5,000x bet  
**Type:** Feature spin (guaranteed multiplier symbols)

**Distributions:**
- **multiplier_feature (100%):** Guarantees at least 1 multiplier symbol per spin

**Special Features:**
- **Guaranteed multipliers** (at least 1 M symbol per spin)
- **Enhanced win potential** with consistent multipliers
- **Feature persists** after each spin

### 6. Divine Judgement (MAX Multiplier Feature)

**Cost:** 1,000.0x bet  
**RTP:** 96.00%  
**Max Win:** 5,000x bet  
**Type:** Feature spin (chance for MAX multiplier)

**Distributions:**
- **divine_judgement (100%):** MAX multiplier enabled

**Special Features:**
- **5% chance** for M symbol to be "MAX" (instead of normal value)
- **MAX + Tumble = Max Win** (5,000x bet instantly, regardless of tumble amount)
- **Premium feature** with highest win potential
- **Feature persists** after each spin

---

## Distribution System

### Distribution Quotas

Each bet mode has multiple **distributions** (outcome types) that sum to 1.0 (100%).

**Example - Base Mode:**
- wincap: 0.01 (1%)
- freegame: 0.15 (15%)
- super_freegame: 0.04 (4%)
- 0: 0.01 (1%)
- basegame: 0.798 (79.8%)
- **Total:** 1.0 (100%)

### Distribution Conditions

Each distribution specifies:

1. **Reel Weights:**
   - Which reel file to use (BR0, FR0, WCAP)
   - Weight probabilities for each reel

2. **Multiplier Values:**
   - Distribution of multiplier values (M symbol)
   - Different for base game vs free game

3. **Scatter Triggers:**
   - Guaranteed scatter counts (e.g., {3: 100} = always 3 scatters)

4. **Force Flags:**
   - `force_wincap`: Force max win outcome
   - `force_freegame`: Force free spin trigger
   - `force_min_multipliers`: Guarantee minimum multiplier count

### Multiplier Value Distribution Example

```python
"mult_values": {
    "basegame": {
        1: 2,      # 1x multiplier (weight: 2)
        2: 65,     # 2x multiplier (weight: 65) - most common
        3: 28,     # 3x multiplier (weight: 28)
        5: 4,      # 5x multiplier (weight: 4)
        10: 1,     # 10x multiplier (weight: 1)
        # ... etc
    },
    "freegame": {
        # Different distribution for free spins
    }
}
```

---

## RTP & Optimization Targets

### Base RTP: 96.30%

RTP is achieved through:
1. **Symbol distribution** on reels
2. **Multiplier distribution** (weights)
3. **Scatter trigger frequency**
4. **Optimization program** fine-tunes weights to hit exact RTP

### Optimization Targets

The optimization program targets specific RTPs for each mode:

**Base Mode:**
- basegame RTP: 94.3%
- wincap RTP: 2.0%
- **Total:** ~96.3%

**Wrath of Olympus:**
- freegame RTP: 94.8%
- wincap RTP: 1.2%
- **Total:** 96.0%

**Super Wrath of Olympus:**
- freegame RTP: 94.6%
- wincap RTP: 1.2%
- **Total:** 95.8%

### Optimization Parameters

For each mode, optimization uses:

1. **Conditions:**
   - Target RTP for each distribution type
   - Average win targets
   - Hit rate targets

2. **Scaling:**
   - Win range preferences (favor certain win sizes)
   - Scale factors (penalty/reward weights)

3. **Parameters:**
   - `num_show`: 5,000 (candidates to evaluate)
   - `num_per_fence`: 10,000 (variety per range)
   - `sim_trials`: 5,000 (simulation accuracy)
   - `min_m2m`: 4 (variance range)
   - `max_m2m`: 8 (variance range)
   - `pmb_rtp`: Target RTP (e.g., 0.963)

---

## Game Flow

### Base Game Spin Flow

```
1. Reset seed (deterministic randomness)
2. Draw board (6×5 grid from BR0.csv reels)
3. Evaluate scatter pays (count symbols, apply paytable)
4. Emit tumble win events
5. TUMBLE LOOP:
   - If wins exist AND wincap not triggered:
     - Explode winning symbols (H1-H3, L1-L4)
     - Keep scatter (S) and multiplier (M) symbols
     - Symbols fall down
     - New symbols drop in
     - Re-evaluate scatter pays
     - Emit tumble win events
     - Repeat until no wins
6. Apply multipliers (sum M values, multiply total win)
7. Check free spin trigger (3+ scatters)
8. If triggered: Run free spins
9. Evaluate final win
10. Check repeat conditions (if needed)
11. Imprint wins to book
```

### Free Spin Flow

```
1. Reset free spin state
2. Reset cumulative multiplier = 0
3. FOR each free spin (up to tot_fs):
   a. Update free spin counter
   b. Draw board (from FR0.csv reels)
   c. Evaluate scatter pays
   d. Emit tumble win events
   e. TUMBLE LOOP (same as base game)
   f. Apply multipliers:
      - Sum multiplier values on board
      - Add to cumulative
      - Multiply win by NEW cumulative total
   g. Update win manager
   h. Check retrigger (3+ scatters = +5 spins)
   i. If wincap triggered: Exit loop immediately
4. End free spins
5. Add bonus win to total
```

### Key Differences: Base vs Free Spins

| Aspect | Base Game | Free Spins |
|--------|-----------|------------|
| Multiplier Application | Multiply by sum (one-time) | Cumulative (adds up) |
| Retrigger | N/A | 3 scatters = +5 spins |
| Reel File | BR0.csv | FR0.csv |
| Multiplier Distribution | Base game weights | Free game weights |
| Max Win Protection | Stops spin | Stops entire bonus |

---

## Summary

This is a **scatter-pay slot game** with:
- **No paylines** (symbols pay anywhere)
- **Tumble mechanics** (winning symbols explode, new symbols fall)
- **Multiplier system** (base: sum, bonus: cumulative)
- **Free spins** (3 scatters trigger, retriggers possible)
- **Multiple bet modes** (base, buy bonuses, feature spins)
- **96.30% RTP** (optimized through weight distributions)
- **5,000x max win** (wincap protection)

The math is controlled by:
1. **Reel strips** (symbol frequencies)
2. **Multiplier distributions** (weights for M symbol values)
3. **Distribution quotas** (percentages for different outcome types)
4. **Optimization program** (fine-tunes weights to hit exact RTP targets)

---

## Files Reference

### Configuration Files
- `game_config.py` - All game parameters, paytable, bet modes
- `game_optimization.py` - Optimization targets and parameters
- `game_override.py` - Custom game logic overrides

### Game Logic Files
- `gamestate.py` - Main game flow (run_spin, run_freespin)
- `game_executables.py` - Win evaluation, multiplier application
- `game_calculations.py` - Custom calculation overrides

### Reel Files
- `reels/BR0.csv` - Base game reel strips
- `reels/FR0.csv` - Free game reel strips
- `reels/FRWCAP.csv` - Free game reels for max win

### Execution
- `run.py` - Main script to run simulations, optimization, analysis




