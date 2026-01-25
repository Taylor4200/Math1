# Super Bonus - Frontend Implementation Guide

## Overview

**Super Bonus** is a buy bonus mode (500x bet) that starts free spins with **random multipliers (2x-1024x) already placed on ALL positions** before the first spin begins.

## How It Works

### Backend Behavior

1. **When Super Bonus starts** (`betmode == "super_bonus"`):
   - `reset_fs_spin()` is called
   - **ALL 49 positions** (7x7 grid) are initialized with **random multipliers**
   - Multiplier distribution (linear, decreasing):
     - **50%** = `2x` (most common)
     - **~10.9%** = `4x`
     - **~9.5%** = `8x`
     - **~8.2%** = `16x`
     - **~6.8%** = `32x`
     - **~5.4%** = `64x`
     - **~4.1%** = `128x`
     - **~2.7%** = `256x`
     - **~1.4%** = `512x`
     - **1%** = `1024x` (rarest)
   - These multipliers are set **BEFORE** the first board is drawn

2. **Event Sequence**:
   ```
   reset_fs_spin() → Sets multipliers (2x-1024x on all spots)
   ↓
   update_grid_mult_event() → Emits "updateGrid" event with initial multipliers
   ↓
   draw_board() → First board reveal
   ↓
   Gameplay begins
   ```

### Frontend Requirements

#### ✅ **CRITICAL: Wait for Initial Multipliers**

**The frontend MUST:**
1. **Wait** for the `updateGrid` event that comes **BEFORE** the first `reveal` event
2. **Show a CLEARED/EMPTY board** (no symbols visible)
3. **Play an animation** that "pops" multipliers onto the board positions
4. **THEN** proceed with the first board reveal

#### ❌ **Current Bug**

The frontend is currently waiting until the **NEXT spin** to pull multiplier values. This is wrong because:
- The multipliers are set at the START of super bonus
- They should be visible BEFORE the first spin
- The `updateGrid` event is emitted immediately after `reset_fs_spin()`

## Event Flow for Super Bonus

### Correct Sequence:

```javascript
// 1. User buys super_bonus (500x bet)
POST /spin { betMode: "super_bonus" }

// 2. Backend responds with events:
[
  {
    type: "fsTrigger",
    freegameTrigger: true,
    // ... free spin count info
  },
  {
    type: "updateGrid",  // ← THIS COMES FIRST!
    gridMultipliers: [
      [0, 16, 4, 128, 2, 64, 8, 32, 0],  // Reel 0: padding + 7 rows + padding
      [0, 256, 512, 4, 8, 16, 2, 1024, 0],  // Reel 1
      // ... all 7 reels with random multipliers (2-1024) on all positions
    ]
  },
  {
    type: "reveal",  // ← Board reveal comes AFTER multipliers
    board: [...],
    // ... first board
  },
  // ... rest of first spin
]
```

## Frontend Implementation Steps

### Step 1: Detect Super Bonus Start

```javascript
if (betMode === "super_bonus" && event.type === "fsTrigger") {
  // Super bonus is starting
  // Clear the board completely
  clearBoard();
  // Wait for updateGrid event
}
```

### Step 2: Receive Initial Multipliers

```javascript
if (betMode === "super_bonus" && event.type === "updateGrid") {
  // This is the INITIAL multiplier setup
  // gridMultipliers has random values (2-1024) on ALL positions
  
  // Show starting animation
  showMultiplierPopAnimation(event.gridMultipliers);
  
  // Animation should:
  // - Pop multipliers onto positions one by one (or in waves)
  // - Show the multiplier values (2x, 4x, 8x, etc.)
  // - Complete BEFORE the first reveal event
}
```

### Step 3: Show First Board

```javascript
if (event.type === "reveal") {
  // Now show the first board
  // Multipliers are already visible from Step 2
  revealBoard(event.board);
}
```

## Grid Multipliers Format

The `gridMultipliers` array structure:

```javascript
gridMultipliers: [
  [0, 16, 4, 128, 2, 64, 8, 32, 0],  // Reel 0: [padding, row1-7, padding]
  [0, 256, 512, 4, 8, 16, 2, 1024, 0],  // Reel 1
  // ... 7 reels total
]
```

**Structure:**
- **9 rows per reel** (1 top padding + 7 main rows + 1 bottom padding)
- **Row 0**: Top padding (always `0`)
- **Rows 1-7**: Main board (can have multipliers: `2, 4, 8, 16, 32, 64, 128, 256, 512, 1024`)
- **Row 8**: Bottom padding (always `0`)

**Multiplier Values:**
- `0` = No multiplier
- `1` = Marked spot (shows "0x" - not active yet)
- `2, 4, 8, 16, 32, 64, 128, 256, 512, 1024` = Active multipliers

## Animation Example

```javascript
function showMultiplierPopAnimation(gridMultipliers) {
  // Clear board first
  clearAllMultipliers();
  
  // For each position (excluding padding rows 0 and 8)
  for (let reel = 0; reel < 7; reel++) {
    for (let row = 1; row <= 7; row++) {  // Skip padding rows
      const multiplier = gridMultipliers[reel][row];
      
      if (multiplier > 0) {
        // Animate multiplier appearing at this position
        animateMultiplierPop(reel, row - 1, multiplier);  // row-1 because frontend uses 0-6
        // Delay between pops for visual effect
        await delay(50);  // Adjust timing as needed
      }
    }
  }
  
  // Wait for animation to complete
  await waitForAnimationComplete();
  
  // Now ready for first board reveal
}
```

## Key Points

1. ✅ **Multipliers are set BEFORE first spin** - they're not from a previous spin
2. ✅ **updateGrid event comes FIRST** - before reveal event
3. ✅ **Show cleared board** - then animate multipliers popping on
4. ✅ **Animation completes** - before showing first board
5. ❌ **Don't wait for next spin** - multipliers are already there at start

## Testing

To verify correct behavior:
1. Buy super bonus (500x bet)
2. Check event sequence: `fsTrigger` → `updateGrid` → `reveal`
3. Verify `updateGrid` has multipliers (2-1024) on all positions
4. Verify frontend shows animation BEFORE first board reveal
5. Verify multipliers persist and grow during gameplay

