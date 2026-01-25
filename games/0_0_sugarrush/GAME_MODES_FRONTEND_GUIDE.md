# Sugar Rush - Game Modes Guide for Frontend

## Overview
Sugar Rush offers **4 distinct game modes**, each with different costs, RTPs, and mechanics.

---

## Game Modes Summary

| Mode Name | API Name | Cost | RTP | Description |
|-----------|----------|------|-----|-------------|
| **Base Game** | `"base"` | 1x bet | **96.30%** | Regular gameplay with natural free spin triggers |
| **Bonus Buy** | `"bonus"` | 100x bet | **95.80%** | Instantly trigger free spins |
| **Super Bonus** | `"super_bonus"` | 500x bet | **95.80%** | Free spins with ALL positions starting at 2x-1024x multipliers |
| **Bonus Booster** | `"bonus_booster"` | 2x bet | **96.30%** | Enhanced base game with more frequent free spin triggers |

---

## Mode 1: Base Game (`"base"`)

### Cost & RTP
- **Cost:** 1x bet (standard bet amount)
- **RTP:** 96.30%

### Mechanics
- Standard Sugar Rush gameplay
- **Grid:** 7 reels × 7 rows (49 positions total)
- **Win Type:** Cluster pays (minimum 5 connected symbols horizontally/vertically)
- **Symbols:** H1, H2, H3 (high), L1, L2, L3, L4 (low), S (scatter)
- **No wilds, no multiplier symbols** - multipliers come from grid positions
- **Tumbles:** Winning symbols explode, remaining fall down, new symbols drop from top
- **Multiplier spots:** Grow during tumbles (2x → 4x → 8x → 16x → 32x → 64x → 128x → 256x → 512x → 1024x max)
  - First hit on a position: marks it (explosion_count = 1, no multiplier yet)
  - Second hit: creates 2x multiplier (explosion_count = 2)
  - Each subsequent hit: multiplier doubles (4x → 8x → 16x...)
  - Formula: `multiplier = 2^(explosion_count - 1)` (capped at 1024x)
- **Multipliers reset after each spin** (cleared when tumbles end)
- Free spins triggered naturally by landing 3-7 scatter symbols

### Free Spin Awards (Base Game & All Modes)
| Scatters | Free Spins Awarded |
|----------|-------------------|
| **3** | **10** |
| **4** | **12** |
| **5** | **15** |
| **6** | **20** |
| **7** | **30** |

**Retriggers:** Same scatter counts award same free spins amounts during free spins (adds to remaining spins)

---

## Mode 2: Bonus Buy (`"bonus"`)

### Cost & RTP
- **Cost:** 100x bet
- **RTP:** 95.80%

### Mechanics
- **Instantly triggers free spins** (skips base game)
- Awards 3-7 scatters initially (10-30 free spins based on scatter count)
- Free spins mechanics:
  - **Multipliers persist** across all free spins in the round
  - Multipliers continue to grow with each tumble
  - Can retrigger with 3-7 scatters during free spins (adds more spins)
  - Uses special free spin reels (different from base game reels)

### Free Spin Awards
Same as base game:
- 3 scatters = 10 free spins
- 4 scatters = 12 free spins
- 5 scatters = 15 free spins
- 6 scatters = 20 free spins
- 7 scatters = 30 free spins

---

## Mode 3: Super Bonus (`"super_bonus"`)

### Cost & RTP
- **Cost:** 500x bet
- **RTP:** 95.80%

### Mechanics
- **Premium buy bonus** with special starting condition
- Instantly triggers free spins
- **Special Feature:** ALL 49 positions start with random multipliers (2x-1024x)
  - Multipliers are placed **BEFORE** the first spin begins
  - Each position gets a random multiplier: 2x, 4x, 8x, 16x, 32x, 64x, 128x, 256x, 512x, or 1024x
  - Frontend receives `updateGrid` event with initial multipliers **BEFORE** first `reveal` event
  - Then gameplay proceeds with multipliers continuing to grow normally from their starting values
  - These starting multipliers can then double with each subsequent hit (e.g., 2x → 4x → 8x...)

### Event Sequence
```
1. fsTrigger event (free spins starting)
2. updateGrid event (initial multipliers on ALL 49 positions)
3. reveal event (first board with symbols)
4. Gameplay continues
```

### Visual Sequence
1. Board clears (empty grid)
2. Multipliers pop onto all positions (animation showing 2x-1024x values)
3. First board reveals with multipliers already active underneath
4. Gameplay continues (multipliers grow from their starting values)

### Free Spin Awards
Same as other modes:
- 3 scatters = 10 free spins
- 4 scatters = 12 free spins
- 5 scatters = 15 free spins
- 6 scatters = 20 free spins
- 7 scatters = 30 free spins

---

## Mode 4: Bonus Booster (`"bonus_booster"`)

### Cost & RTP
- **Cost:** 2x bet
- **RTP:** 96.30% (same as base)

### Mechanics
- Enhanced base game with **increased free spin trigger rate**
- All base game rules apply:
  - 7×7 grid, cluster pays, tumbles
  - Multipliers reset after each spin
  - Same paytable and symbols
- **Key difference:** Free spins trigger more frequently than base mode (boosted scatter appearance)
- When free spins trigger, they play the same as naturally triggered free spins:
  - Multipliers persist across all free spins
  - Can retrigger with 3-7 scatters

### Free Spin Awards
Same as base game:
- 3 scatters = 10 free spins
- 4 scatters = 12 free spins
- 5 scatters = 15 free spins
- 6 scatters = 20 free spins
- 7 scatters = 30 free spins

---

## Multiplier Behavior by Mode

### Base Game & Bonus Booster
- **Multipliers reset** at the start of each spin
- Multipliers only persist during a single spin's tumble sequence
- After tumbles end, all multipliers clear

### Bonus Buy & Super Bonus (During Free Spins)
- **Multipliers persist** across all free spins in the round
- Multipliers continue to grow throughout the entire session
- Only reset when the free spins round ends

### Super Bonus Special Case
- **ALL 49 positions** start with random multipliers (2x-1024x)
- Starting multipliers set **BEFORE** first board reveal
- Frontend receives `updateGrid` event first, then `reveal` event
- Multipliers then grow normally from their starting values

---

## Win Cap (All Modes)

- **Maximum win:** 25,000x bet
- Applies to all game modes
- When reached during free spins:
  - All remaining free spins are cancelled
  - Win is awarded immediately
  - Round ends

---

## Technical Details

### Cluster Win Calculation
1. Find all connected groups of 5+ identical symbols (horizontal/vertical only)
2. Look up base payout from paytable based on cluster size and symbol
3. Sum all multipliers from positions in the cluster (multipliers ADD together)
4. Calculate final win: `win = base_payout × sum_of_position_multipliers × global_multiplier`
   - If no multipliers in cluster, use 1x (not 0x)
   - Global multiplier is currently always 1x

**Example:**
- Cluster of 8 H1 symbols (base payout = 1.5x)
- Positions have multipliers: [2x, 4x, 8x, 0x, 0x, 0x, 0x, 0x]
- Sum of multipliers = 2 + 4 + 8 = 14
- Final win = 1.5 × 14 = 21.0x bet

### Multiplier Growth Formula
```
explosion_count = number of times a cluster has formed on this position
multiplier = 2^(explosion_count - 1)  (if explosion_count > 1)
multiplier = 0  (if explosion_count = 0 or 1)

Examples:
- explosion_count = 0 → multiplier = 0 (no hit yet)
- explosion_count = 1 → multiplier = 0 (marked but not active)
- explosion_count = 2 → multiplier = 2x (first active multiplier)
- explosion_count = 3 → multiplier = 4x
- explosion_count = 4 → multiplier = 8x
- explosion_count = 11 → multiplier = 1024x (max)
- explosion_count = 12+ → multiplier = 1024x (capped)
```

### Paytable (Cluster Size → Payout Multiplier)

**High Symbols:**
| Symbol | 5-6 | 7-8 | 9-10 | 11-12 | 13-14 | 15+ |
|--------|-----|-----|------|-------|-------|-----|
| H1 | 0.5x | 1.5x | 5.0x | 15.0x | 50.0x | 300.0x |
| H2 | 0.4x | 1.2x | 4.0x | 12.0x | 40.0x | 200.0x |
| H3 | 0.3x | 1.0x | 3.0x | 10.0x | 30.0x | 120.0x |

**Low Symbols:**
| Symbol | 5-6 | 7-8 | 9-10 | 11-12 | 13-14 | 15+ |
|--------|-----|-----|------|-------|-------|-----|
| L1 | 0.2x | 0.6x | 2.0x | 6.0x | 20.0x | 60.0x |
| L2 | 0.2x | 0.5x | 1.5x | 5.0x | 15.0x | 50.0x |
| L3 | 0.1x | 0.4x | 1.2x | 4.0x | 12.0x | 40.0x |
| L4 | 0.1x | 0.3x | 1.0x | 3.5x | 10.0x | 30.0x |

**Scatter (S):** Does not pay directly, only triggers free spins

### Tumble Limits
- **Base game:** Maximum 30 tumbles per spin
- **Free spins:** Maximum 20 tumbles per spin
- **Win threshold:** Base game stops if win < 0.1x bet, Free spins stops if win < 0.5x bet

### Reel Configuration
- **Base game reels:** BR0.csv
- **Free spin reels:** FR0.csv
- **Win cap reels:** FRWCAP.csv (used during wincap distribution)
- **Max 1 scatter per reel** (scatters cannot stack on same reel)

### Grid Multipliers Format (in events)
```javascript
gridMultipliers: [
  [0, mult, mult, mult, mult, mult, mult, mult, 0],  // Reel 0: [padding, rows 1-7, padding]
  [0, mult, mult, mult, mult, mult, mult, mult, 0],  // Reel 1
  // ... 7 reels total
]
```
- **9 rows per reel:** 1 top padding + 7 main rows + 1 bottom padding
- **Padding rows (0 and 8):** Always 0
- **Main rows (1-7):** Can have multipliers (0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
- **Value meanings:**
  - `0` = No multiplier
  - `2, 4, 8, 16, 32, 64, 128, 256, 512, 1024` = Active multipliers

---

## API Usage

### Making a Bet Request

```json
{
  "betMode": "base",  // or "bonus", "super_bonus", "bonus_booster"
  "betAmount": 1.00
}
```

### Mode Names (Case-Sensitive)
- `"base"` - Base game
- `"bonus"` - Bonus buy
- `"super_bonus"` - Super bonus
- `"bonus_booster"` - Bonus booster

### Cost Multipliers (Applied Automatically)

| Mode | `betMode` Value | Cost |
|------|----------------|------|
| Base | `"base"` | 1x bet |
| Bonus Booster | `"bonus_booster"` | 2x bet |
| Bonus Buy | `"bonus"` | 100x bet |
| Super Bonus | `"super_bonus"` | 500x bet |

**Example:**
- $1 bet in base mode → costs $1.00
- $1 bet in bonus_booster mode → costs $2.00
- $1 bet in bonus mode → costs $100.00
- $1 bet in super_bonus mode → costs $500.00

---

## Quick Reference

| Mode | Cost | RTP | Multiplier Reset | Special Feature |
|------|------|-----|------------------|-----------------|
| **Base** | 1x | 96.30% | After each spin | Natural triggers |
| **Bonus Booster** | 2x | 96.30% | After each spin | More frequent triggers |
| **Bonus Buy** | 100x | 95.80% | After free spins round | Instant free spins |
| **Super Bonus** | 500x | 95.80% | After free spins round | Start with 2x-1024x on ALL positions |

---

## Additional Documentation

For more details, see:
- **Game mechanics**: `FRONTEND_MATH_DOCUMENTATION.md`
- **Super Bonus implementation**: `SUPER_BONUS_FRONTEND_GUIDE.md`
- **Mode names**: `FRONTEND_BET_MODE_NAMES.md`
- **Game overview**: `readme.txt`

