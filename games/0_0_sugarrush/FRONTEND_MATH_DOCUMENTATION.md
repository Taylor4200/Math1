# Sugar Rush - Frontend Math Documentation

## Overview
Sugar Rush is a **cluster pays** slot game with **multiplier spots** that grow on the grid. There are no paylines - wins are formed by connecting 5+ identical symbols horizontally or vertically.

---

## Game Grid

### Dimensions
- **7 reels × 7 rows** (49 total positions)
- Grid positions are referenced as: `{reel: 0-6, row: 0-6}`

---

## Symbols

### Regular Symbols
- **High Symbols**: H1, H2, H3 (higher value)
- **Low Symbols**: L1, L2, L3, L4 (lower value)
- **Scatter**: S (triggers free spins only, does NOT pay directly)

### Important Notes
- **NO Wild symbols**
- **NO Multiplier symbols** (multipliers come from grid spots, not symbols!)

---

## Cluster Payouts

### Minimum Cluster Size
- **5 symbols** minimum to form a winning cluster
- Clusters must be connected **horizontally and/or vertically** (not diagonally)

### Paytable (bet multipliers)

#### High Symbols
| Symbol | 5-6 symbols | 7-8 symbols | 9-10 symbols | 11-12 symbols | 13-14 symbols | 15+ symbols |
|--------|-------------|-------------|--------------|---------------|---------------|-------------|
| **H1** | 0.5x        | 1.5x        | 5.0x         | 15.0x         | 50.0x         | 300.0x      |
| **H2** | 0.4x        | 1.2x        | 4.0x         | 12.0x         | 40.0x         | 200.0x      |
| **H3** | 0.3x        | 1.0x        | 3.0x         | 10.0x         | 30.0x         | 120.0x      |

#### Low Symbols
| Symbol | 5-6 symbols | 7-8 symbols | 9-10 symbols | 11-12 symbols | 13-14 symbols | 15+ symbols |
|--------|-------------|-------------|--------------|---------------|---------------|-------------|
| **L1** | 0.2x        | 0.6x        | 2.0x         | 6.0x          | 20.0x         | 60.0x       |
| **L2** | 0.2x        | 0.5x        | 1.5x         | 5.0x          | 15.0x         | 50.0x       |
| **L3** | 0.1x        | 0.4x        | 1.2x         | 4.0x          | 12.0x         | 40.0x       |
| **L4** | 0.1x        | 0.3x        | 1.0x         | 3.5x          | 10.0x         | 30.0x       |

---

## Multiplier Spots System

### Overview
Multiplier spots are **grid positions** that grow in value when clusters form on them. This is the core mechanic of Sugar Rush.

### How Multipliers Work

#### Base Game
- Multipliers are **reset to 0** at the start of each spin
- During a spin, when clusters form:
  1. **First hit** on a position: Marks the spot (explosion_count = 1, multiplier = 0)
  2. **Second hit** on the same position: Creates **2x multiplier** (explosion_count = 2, multiplier = 2)
  3. **Each subsequent hit**: Multiplier **doubles** (4x → 8x → 16x → ...)
  4. **Maximum multiplier**: **1024x** (2^10)

#### Free Spins
- Multipliers **persist** across all free spins (NOT reset between spins)
- At start of free spins round: All multipliers reset to 0
- During free spins: Multipliers continue to grow and persist

#### Super Bonus Special Case
- At the start of Super Bonus free spins, **ALL positions** start with **4x multiplier** immediately
- Then they continue to grow normally from there

### Multiplier Calculation Formula
```
explosion_count = number of times a cluster has formed on this position
multiplier = 2^(explosion_count - 1)  (if explosion_count > 1)
multiplier = 0  (if explosion_count = 0 or 1)

Examples:
- explosion_count = 0 → multiplier = 0
- explosion_count = 1 → multiplier = 0 (marked but not active)
- explosion_count = 2 → multiplier = 2x
- explosion_count = 3 → multiplier = 4x
- explosion_count = 4 → multiplier = 8x
- explosion_count = 5 → multiplier = 16x
- explosion_count = 11 → multiplier = 1024x (max)
- explosion_count = 12+ → multiplier = 1024x (capped)
```

### Multiplier Lookup Table
```javascript
// Powers of 2 lookup for performance
const POWER_OF_2 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024];
const multiplier = POWER_OF_2[explosion_count - 1] || 1024;
// Clamp to max 1024x
```

---

## Win Calculation

### Step-by-Step Process

1. **Find Clusters**: Identify all connected groups of 5+ identical symbols
2. **Calculate Base Win**: Look up payout from paytable based on cluster size and symbol
3. **Sum Cluster Multipliers**: **Add together** all multipliers from positions in the cluster
   - **Important**: Multipliers in the same cluster **ADD** together, they do NOT multiply
4. **Apply Global Multiplier**: Multiply by global multiplier (currently always 1x)
5. **Calculate Final Win**: `win = base_payout × (sum_of_position_multipliers) × global_multiplier`

### Example Win Calculation

**Scenario:**
- Cluster of 8 H1 symbols
- Positions in cluster have multipliers: [2x, 4x, 8x, 0x, 0x, 0x, 0x, 0x]
- Base payout for 8 H1 symbols = 1.5x

**Calculation:**
```
sum_of_multipliers = 2 + 4 + 8 + 0 + 0 + 0 + 0 + 0 = 14
base_win = 1.5x
final_win = 1.5 × 14 = 21.0x bet
```

### Critical Rules

1. **Multiple multipliers in same cluster ADD together** (not multiply)
2. **Minimum multiplier = 1x** (if no multipliers, use 1x, not 0x)
3. **Each win updates multiplier spots** before calculating the next tumble
4. **Multipliers persist across tumbles** within the same spin

---

## Tumbling System

### Process
1. **Form clusters** and calculate wins
2. **Mark winning symbols** for removal
3. **Symbols fall down** (tumble)
4. **New symbols** fall from top
5. **Update multiplier spots** after wins (increments explosion_count)
6. **Repeat** if new clusters form

### Tumbling Stops When:
- No more clusters form
- Win cap (25,000x bet) is reached
- Maximum tumble count reached (base: 30, free spins: 20)
- Win falls below threshold (base: 0.1x bet, free spins: 0.5x bet)

### Base Game vs Free Spins
- **Base game**: Multipliers reset after tumbling ends
- **Free spins**: Multipliers persist across tumbles and across spins

---

## Free Spins

### Trigger Conditions
- **3+ scatters** on the grid trigger free spins
- Scatters only count, they don't pay directly

### Free Spins Awarded
| Scatters | Free Spins |
|----------|------------|
| 3        | 10         |
| 4        | 12         |
| 5        | 15         |
| 6        | 20         |
| 7        | 30         |

### Retriggers
- Same scatter counts award same free spins amounts
- Free spins **add** to remaining spins (not replace)

### Special Behavior in Free Spins
- **Multipliers persist** across all free spins
- Multipliers **continue to grow** during free spins
- More tumble potential (but capped at 20 tumbles per spin)

---

## Event Structure

### Win Event
```json
{
  "type": "win",
  "symbol": "H1",
  "clusterSize": 8,
  "win": 21.0,
  "positions": [
    {"reel": 0, "row": 0},
    {"reel": 0, "row": 1},
    ...
  ],
  "meta": {
    "globalMult": 1,
    "clusterMult": 14,      // Sum of all position multipliers in cluster
    "winWithoutMult": 1.5,  // Base paytable value
    "overlay": {"reel": 0, "row": 3}  // Central position for overlay
  }
}
```

### Grid Multiplier Update Event
```json
{
  "type": "updateGrid",
  "index": 5,
  "gridMultipliers": [
    [0, 0, 2, 4, 0, 0, 0],  // Reel 0: multipliers per row
    [0, 0, 0, 8, 0, 0, 0],  // Reel 1
    ...
  ]
}
```
- Emitted at start of each free spin
- Emitted after all tumbles complete
- **Not emitted** during tumble chain (only at end)

### Tumble Win Events
- Emitted for each tumble iteration
- Contains all wins from that tumble

---

## Win Cap

### Maximum Win
- **25,000x bet** (wincap = 25000.0)
- When reached, all remaining free spins are cancelled
- Spin completes immediately after win cap is reached

---

## Bet Modes

| Mode | Cost | RTP | Description |
|------|------|-----|-------------|
| **base** | 1x bet | 96.30% | Standard base game |
| **bonus** | 100x bet | 95.80% | Buy bonus feature |
| **super_bonus** | 500x bet | 95.80% | Buy super bonus (starts with 4x on all positions) |
| **bonus_booster** | 2x bet | 96.30% | Increased scatter chance (2% vs 0.6%) |

---

## Key Implementation Notes for Frontend

### 1. Multiplier Grid State
- Track `explosion_count[reel][row]` for each position
- Track `position_multipliers[reel][row]` for display
- Update after each win event

### 2. Cluster Detection
- Use flood-fill algorithm to find connected symbols
- Check horizontal and vertical only (no diagonals)
- Minimum cluster size: 5 symbols

### 3. Win Calculation
- Look up base payout from paytable
- Sum multipliers from all positions in cluster
- Apply: `win = base × sum(multipliers) × global_mult`

### 4. Multiplier Updates
- After each cluster win, increment explosion_count for each position in cluster
- Calculate new multiplier: `2^(explosion_count - 1)` (capped at 1024x)
- Update position_multipliers array

### 5. Base Game vs Free Spins
- **Base game**: Reset multipliers at start of each spin
- **Free spins**: Reset multipliers at start of free spins round, then persist
- **Super bonus**: Initialize all positions to 4x at start

### 6. Visual Feedback
- Show multiplier values on grid positions (0x = no display, 2x+ = show value)
- Highlight winning clusters
- Show overlay on central position of each cluster
- Update multiplier display after each tumble

---

## Edge Cases

1. **Empty multiplier sum**: If all positions have 0x multiplier, use 1x (not 0x)
2. **Max multiplier**: Capped at 1024x, even if explosion_count > 11
3. **Super bonus initialization**: All positions start at explosion_count = 2 (4x multiplier)
4. **Base game reset**: Multipliers reset after tumbling completes (not during)

---

## Performance Optimizations

1. **Power of 2 lookup table**: Use array lookup instead of calculating 2^n
2. **Early exit**: Skip cluster evaluation if board is empty
3. **Event batching**: Only emit grid multiplier events at key moments, not every tumble
4. **Threshold checks**: Stop tumbling if win is too small

---

## Testing Scenarios

### Test Case 1: First Cluster Hit
- Cluster forms on positions with no multipliers
- Expected: Multipliers become 0x (marked), win uses 1x multiplier

### Test Case 2: Second Hit on Same Position
- Cluster forms on previously marked position
- Expected: Multiplier becomes 2x, win includes 2x multiplier

### Test Case 3: Multiple Multipliers in Cluster
- Cluster spans positions with [2x, 4x, 8x]
- Expected: Sum = 14x, applied to base win

### Test Case 4: Free Spins Persistence
- Form cluster in free spin 1
- Form cluster in same position in free spin 2
- Expected: Multiplier grows from 2x to 4x

### Test Case 5: Super Bonus
- Start super bonus free spins
- Expected: All positions show 4x multiplier immediately

---

## Summary

**Core Mechanics:**
1. Cluster pays (5+ connected symbols)
2. Multiplier spots grow on grid positions (2x → 4x → 8x... up to 1024x)
3. Multipliers in same cluster **ADD** together
4. Tumbling creates cascading wins
5. Free spins allow multipliers to persist and grow

**Key Formula:**
```
final_win = paytable_payout × sum(position_multipliers_in_cluster) × global_multiplier
multiplier = 2^(explosion_count - 1)  (capped at 1024x)
```





