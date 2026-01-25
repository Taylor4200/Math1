# Frontend Hook Implementation Guide - Gates of Olympus Style Game

## Overview

This game uses **scatter pays** with **tumble mechanics** and **multiplier symbols**. The frontend must call the `onHandleGameFlow` hook to process game events and calculate wins during simulation.

## Hook Structure

### Hook Registration

```typescript
// Register the hook when initializing the game engine
const hooks = {
  onHandleGameFlow: handleGameFlowHook,
  // ... other hooks
};

// Initialize game with hooks
gameEngine.init(config, hooks);
```

### Hook Implementation

```typescript
function handleGameFlowHook(ctx: GameContext, events: GameEvent[]): void {
  // Process each event in sequence
  for (const event of events) {
    switch (event.type) {
      case 'reveal':
        handleRevealEvent(ctx, event);
        break;
      case 'tumbleWin':
        handleTumbleWinEvent(ctx, event);
        break;
      case 'setWin':
        handleSetWinEvent(ctx, event);
        break;
      case 'setTotalWin':
        handleSetTotalWinEvent(ctx, event);
        break;
      case 'fsTrigger':
        handleFreeSpinTrigger(ctx, event);
        break;
      case 'updateFreespin':
        handleUpdateFreespin(ctx, event);
        break;
      // ... other event types
    }
  }
}
```

## Critical: Scatter Pay Evaluation

### When to Call the Hook

The hook **MUST** be called after each `reveal` event to evaluate scatter pays:

```typescript
function handleRevealEvent(ctx: GameContext, event: RevealEvent): void {
  // 1. Update board state from event
  updateBoardFromReveal(ctx, event);
  
  // 2. CRITICAL: Evaluate scatter pays immediately after reveal
  const wins = evaluateScatterPays(ctx);
  
  // 3. Process wins
  if (wins.totalWin > 0) {
    // Mark winning symbols for explosion
    markWinningSymbols(ctx, wins);
    
    // Record tumble win (before multipliers)
    ctx.wallet.tumbleWin = wins.totalWin;
    
    // Emit tumble win event
    emitTumbleWinEvent(ctx, wins);
  }
  
  // 4. Check for tumbles
  if (wins.totalWin > 0) {
    // Trigger tumble animation
    triggerTumble(ctx);
  } else {
    // No wins - apply multipliers and finish spin
    applyMultipliers(ctx);
  }
}
```

## Scatter Pay Evaluation Function

```typescript
function evaluateScatterPays(ctx: GameContext): ScatterWinData {
  const board = ctx.board;
  const config = ctx.config;
  const paytable = config.paytable;
  
  // Count symbols on board
  const symbolCounts: Map<string, number> = new Map();
  const symbolPositions: Map<string, Position[]> = new Map();
  
  // Iterate through all board positions
  for (let reel = 0; reel < board.length; reel++) {
    for (let row = 0; row < board[reel].length; row++) {
      const symbol = board[reel][row];
      const symbolName = symbol.name;
      
      // Skip multiplier symbols (M) - they don't count for scatter pays
      if (symbolName === 'M') continue;
      
      // Count symbol
      const count = symbolCounts.get(symbolName) || 0;
      symbolCounts.set(symbolName, count + 1);
      
      // Track positions
      if (!symbolPositions.has(symbolName)) {
        symbolPositions.set(symbolName, []);
      }
      symbolPositions.get(symbolName)!.push({ reel, row });
    }
  }
  
  // Evaluate wins
  const wins: ScatterWin[] = [];
  let totalWin = 0;
  
  for (const [symbolName, count] of symbolCounts.entries()) {
    // Check paytable for this symbol count
    // Paytable format: { (count, symbol): payout }
    const paytableKey = `${count},${symbolName}`;
    
    // Handle range-based paytable (8-9, 10-11, 12-30)
    let payout = 0;
    if (count >= 8 && count <= 9) {
      payout = paytable[`8-9,${symbolName}`] || paytable[`(8,9),${symbolName}`];
    } else if (count >= 10 && count <= 11) {
      payout = paytable[`10-11,${symbolName}`] || paytable[`(10,11),${symbolName}`];
    } else if (count >= 12) {
      payout = paytable[`12-30,${symbolName}`] || paytable[`(12,30),${symbolName}`];
    }
    
    if (payout > 0) {
      // Calculate symbol multiplier (sum of M symbols on winning positions)
      let symbolMultiplier = 1;
      const positions = symbolPositions.get(symbolName)!;
      
      for (const pos of positions) {
        const symbol = board[pos.reel][pos.row];
        if (symbol.name === 'M' && symbol.multiplier) {
          symbolMultiplier += symbol.multiplier;
        }
      }
      
      const winAmount = payout * symbolMultiplier;
      totalWin += winAmount;
      
      wins.push({
        symbol: symbolName,
        count: count,
        payout: payout,
        multiplier: symbolMultiplier,
        win: winAmount,
        positions: positions,
      });
    }
  }
  
  return {
    wins: wins,
    totalWin: totalWin,
  };
}
```

## Event Flow During Simulation

### Base Game Spin Flow

```
1. reveal event → Call handleRevealEvent()
   ↓
2. evaluateScatterPays() → Calculate wins
   ↓
3. If wins > 0:
   - Mark winning symbols for explosion (except S and M)
   - Emit tumbleWin event
   - Trigger tumble animation
   ↓
4. tumbleWin event → Call handleTumbleWinEvent()
   ↓
5. After tumble completes:
   - New symbols fall into place
   - Repeat from step 1 (re-evaluate scatter pays)
   ↓
6. When no more wins:
   - Apply multipliers (sum all M symbols on board)
   - setWin event → Multiply tumble_win × multiplier_sum
   - setTotalWin event → Final win amount
```

### Free Spin Flow

```
1. fsTrigger event → Start free spins
   ↓
2. updateFreespin event → Increment spin counter
   ↓
3. reveal event → Call handleRevealEvent()
   ↓
4. evaluateScatterPays() → Calculate wins
   ↓
5. Tumble loop (same as base game)
   ↓
6. After tumbles complete:
   - Calculate multiplier sum from M symbols
   - Add to cumulative multiplier
   - setWin event → Multiply tumble_win × NEW cumulative
   ↓
7. Repeat for remaining free spins
```

## Important Rules

### 1. Persistent Symbols
- **S (Scatter)** and **M (Multiplier)** symbols **NEVER explode** during tumbles
- They stay on the board and can be part of multiple wins

### 2. Multiplier Application Timing
- **Base Game**: Multipliers applied **AFTER all tumbles complete**
- **Free Spins**: Multipliers added to cumulative **AFTER each spin's tumbles**

### 3. Symbol Counting
- Count **all symbols** on the board (anywhere, no pattern needed)
- **Minimum 8 symbols** required for scatter pay
- **M symbols don't count** toward scatter pay requirements

### 4. Multiplier Calculation
- **Base Game**: Sum all M symbol values on board, multiply tumble_win × sum
- **Free Spins**: Add M values to cumulative, multiply tumble_win × NEW cumulative

## Example Hook Call Sequence

```typescript
// Simulation starts
const book = await fetchBook(simulationId);

// Process events in order
for (const event of book.events) {
  // Call hook for each event
  onHandleGameFlow(ctx, [event]);
  
  // Hook internally calls:
  // - evaluateScatterPays() after reveal events
  // - Processes tumble wins
  // - Applies multipliers
  // - Updates wallet
}
```

## Configuration Access

```typescript
// Access symbols from config
const symbols = ctx.config.symbols; // Array of symbol objects
// OR convert Map to object if needed:
const symbolsObj = Object.fromEntries(ctx.config.symbols);

// Access paytable
const paytable = ctx.config.paytable; // Format: { "(count,symbol)": payout }

// Access special symbols
const scatterSymbols = ctx.config.special_symbols.scatter; // ["S"]
const multiplierSymbols = ctx.config.special_symbols.multiplier; // ["M"]
```

## Debugging Tips

1. **Hook Not Called**: Ensure hook is registered before simulation starts
2. **Zero Wins**: Verify `evaluateScatterPays()` is called after each `reveal` event
3. **Symbol Access**: Check if `ctx.config.symbols` is a Map and convert if needed
4. **Paytable Format**: Verify paytable keys match your evaluation logic (range-based vs exact count)

## Complete Hook Example

```typescript
function onHandleGameFlow(ctx: GameContext, events: GameEvent[]): void {
  for (const event of events) {
    switch (event.type) {
      case 'reveal':
        // Update board
        updateBoard(ctx, event.board);
        
        // CRITICAL: Evaluate scatter pays
        const scatterWins = evaluateScatterPays(ctx);
        
        if (scatterWins.totalWin > 0) {
          // Mark winning symbols (except S and M)
          markWinningSymbols(ctx, scatterWins);
          
          // Record tumble win
          ctx.wallet.tumbleWin = scatterWins.totalWin;
          
          // Emit tumble win event
          emitEvent(ctx, {
            type: 'tumbleWin',
            wins: scatterWins.wins,
            totalWin: scatterWins.totalWin,
          });
        } else {
          // No wins - apply multipliers
          applyMultipliers(ctx);
        }
        break;
        
      case 'setWin':
        // Apply multiplier to tumble win
        const multiplierSum = getMultiplierSum(ctx);
        const finalWin = ctx.wallet.tumbleWin * multiplierSum;
        ctx.wallet.spinWin = finalWin;
        break;
        
      case 'setTotalWin':
        ctx.wallet.totalWin = event.amount;
        break;
        
      // ... handle other events
    }
  }
}
```

## Key Points

✅ **DO:**
- Call `evaluateScatterPays()` after every `reveal` event
- Keep S and M symbols on board during tumbles
- Apply multipliers AFTER all tumbles complete
- Use cumulative multiplier in free spins

❌ **DON'T:**
- Explode S or M symbols during tumbles
- Apply multipliers during tumble loop
- Reset cumulative multiplier between free spins
- Skip scatter pay evaluation after reveals
