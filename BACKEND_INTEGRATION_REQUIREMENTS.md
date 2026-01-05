# Backend Integration Requirements for Hell's Plinko

## Overview
All frontend infrastructure is now ready for RGS integration. The game is waiting for backend math to provide Plinko-specific book events.

## Required Backend Changes

### 1. Create Plinko Book Event Type

The backend needs to generate books with a new `plinkoResult` event type:

```json
{
  "index": 0,
  "type": "plinkoResult",
  "bucketIndex": 8,
  "multiplier": 0.5
}
```

### Event Properties

- **`index`** (number, required): Event sequence number
- **`type`** (string, required): Must be `"plinkoResult"`
- **`bucketIndex`** (number, required): Which bucket won (0-16)
  - 0 = leftmost bucket
  - 8 = center bucket
  - 16 = rightmost bucket
- **`multiplier`** (number, optional): The multiplier value
  - If not provided, frontend will derive it from bucketIndex + volatility mode

### 2. Bucket Index to Multiplier Mapping

The 17 buckets (0-16) map to multipliers based on volatility mode:

#### MILD Mode (Max Win: 666×)
```
Bucket:     0     1    2   3  4  5  6  7   8   9   10  11 12 13  14  15   16
Multiplier: 666×  150× 60× 20× 8× 4× 2× 1× 0.5× 1× 2× 4× 8× 20× 60× 150× 666×
```

#### SINFUL Mode (Max Win: 1,666×)
```
Bucket:     0      1    2    3   4   5  6  7    8    9    10  11 12  13  14   15   16
Multiplier: 1666× 400× 120× 40× 12× 4× 2× 0.5× 0.2× 0.5× 2× 4× 12× 40× 120× 400× 1666×
```

#### DEMONIC Mode (Max Win: 16,666×)
```
Bucket:     0       1      2    3    4   5  6  7  8  9  10  11 12  13   14   15     16
Multiplier: 16666× 2500× 600× 150× 40× 8× 2× 0× 0× 0× 2× 8× 40× 150× 600× 2500× 16666×
```

### 3. Complete Book Example

A complete Plinko book should look like:

```json
{
  "id": 12345,
  "payoutMultiplier": 0.5,
  "events": [
    {
      "index": 0,
      "type": "plinkoResult",
      "bucketIndex": 8,
      "multiplier": 0.5
    },
    {
      "index": 1,
      "type": "setTotalWin",
      "amount": 50
    },
    {
      "index": 2,
      "type": "finalWin",
      "amount": 50
    }
  ]
}
```

### 4. Volatility Modes

The backend should respect the `mode` parameter in bet requests:
- `"BASE"` - Uses current volatility (mild/sinful/demonic from frontend state)
- Future: May include bonus modes like `"bonus"` (Infernal Bounce) or `"super_bonus"` (Demon's Favor)

## Frontend Implementation Status

✅ **COMPLETE** - All frontend infrastructure is ready:

1. ✅ Type definitions for `BookEventPlinkoResult`
2. ✅ Type definitions for emitter events (`plinkoBallDrop`, `plinkoBallComplete`)
3. ✅ Book event handler for `plinkoResult`
4. ✅ Game state to store pending RGS results
5. ✅ PlinkoBoard listens for RGS events (not bet events)
6. ✅ Deterministic ball physics guides to RGS-determined bucket
7. ✅ Win calculation uses RGS multiplier
8. ✅ Error logging if physics misses target bucket

## Testing Strategy

### For Backend Team

1. **Create test books** for each bucket (0-16) across all volatility modes
2. **Test edge cases**:
   - Bucket 0 (left edge, max win)
   - Bucket 8 (center, low multiplier)
   - Bucket 16 (right edge, max win)
3. **Verify calculations**:
   - `setTotalWin.amount` = bet amount × multiplier
   - All amounts use RGS API_MULTIPLIER correctly

### For Frontend Team

1. Use **Force Result API** to test specific book IDs
2. Verify ball lands in correct bucket 100% of time
3. Check console for physics errors (⚠️ warnings)
4. Verify win amounts match RGS exactly

## Console Logs to Monitor

When testing, watch for these logs:

```
📊 RGS Plinko Result: { bucketIndex: 8, multiplier: 0.5 }
🎲 RGS commanded ball drop to bucket: 8
🎯 Ball 0 landed in slot 8 with multiplier 0.5x
✅ Plinko ball animation complete
```

**Error case (should NOT happen):**
```
⚠️ PHYSICS ERROR: Ball landed in wrong bucket! { expected: 8, actual: 7, difference: 1 }
```

## Critical Notes

- **Physics is cosmetic only** - Ball always lands where RGS says
- **Win comes from RGS** - Frontend doesn't calculate, just displays
- **Certifiable** - All randomness from backend certified math
- **Bucket index is 0-based** - Remember: 0-16, not 1-17

## Contact

If backend team has questions about:
- Event structure
- Multiplier tables
- Testing approach

Please reach out to frontend team for clarification.

---

**Status**: ✅ Frontend Ready - Awaiting Backend Math Implementation

