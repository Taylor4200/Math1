# Backend Integration Requirements for Hell's Plinko

## Overview
All frontend infrastructure is now ready for RGS integration. The game is waiting for backend math to provide Plinko-specific book events.

---

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

---

## 2. Bucket Index to Multiplier Mapping

The 17 buckets (0-16) map to multipliers based on volatility mode:

### MILD Mode (Max Win: 666×)
```
Bucket:     0     1    2   3  4  5  6  7   8   9   10  11 12 13  14  15   16
Multiplier: 666×  150× 60× 20× 8× 4× 2× 1× 0.5× 1× 2× 4× 8× 20× 60× 150× 666×
```

### SINFUL Mode (Max Win: 1,666×)
```
Bucket:     0      1    2    3   4   5  6  7    8    9    10  11 12  13  14   15   16
Multiplier: 1666× 400× 120× 40× 12× 4× 2× 0.5× 0.2× 0.5× 2× 4× 12× 40× 120× 400× 1666×
```

### DEMONIC Mode (Max Win: 16,666×)
```
Bucket:     0       1      2    3    4   5  6  7  8  9  10  11 12  13   14   15     16
Multiplier: 16666× 2500× 600× 150× 40× 8× 2× 0× 0× 0× 2× 8× 40× 150× 600× 2500× 16666×
```

---

## 3. 🎯 BONUS PEG FEATURE (Critical!)

### Current Implementation
- Center peg (row 8, middle position) is a special "bonus peg"
- If ball hits it, triggers a **free ball drop**
- Currently client-side only

### ⚠️ CERTIFICATION REQUIREMENT
For the game to be certifiable, **the bonus peg mechanic must be RGS-controlled**.

### Recommended Backend Approach

When RGS determines a ball will hit the bonus peg, the book should contain **multiple `plinkoResult` events**:

```json
{
  "id": 12345,
  "payoutMultiplier": 2.5,
  "events": [
    {
      "index": 0,
      "type": "plinkoResult",
      "bucketIndex": 8,
      "multiplier": 0.5,
      "hitBonusPeg": true
    },
    {
      "index": 1,
      "type": "plinkoResult",
      "bucketIndex": 4,
      "multiplier": 8.0,
      "isFreeBall": true
    },
    {
      "index": 2,
      "type": "setTotalWin",
      "amount": 850
    },
    {
      "index": 3,
      "type": "finalWin",
      "amount": 850
    }
  ]
}
```

### New Properties for Bonus Peg

- **`hitBonusPeg`** (boolean, optional): If true, this ball triggered the bonus peg
- **`isFreeBall`** (boolean, optional): If true, this is a free ball from bonus peg (no bet deducted)

### Math Considerations

1. **Bonus Peg Hit Probability**: Backend determines if ball path hits center peg
2. **Free Ball Outcome**: Backend generates second `plinkoResult` for the free ball
3. **Total Win Calculation**: Sum of both balls' wins
4. **RTP Impact**: Free balls increase overall RTP - must be factored into optimization

### Alternative: Client-Side Only (Not Recommended)

If backend cannot support bonus peg logic, we can keep it client-side only, BUT:
- ⚠️ May fail certification
- Free ball wins would not count toward RGS total
- Would be purely cosmetic/entertainment

**RECOMMENDATION**: Implement RGS-controlled bonus peg for full certification.

---

## 4. Math File Structure (Stake Engine Standard Format)

### Answer: **1a, 2a, 3a, 4a**

1. **Single CSV file** with 17 rows (buckets 0-16) with probability weights
2. **Each volatility mode as separate bet mode**: `"mild"`, `"sinful"`, `"demonic"`
3. **Segment by win ranges**:
   - `"low_wins"` (0-5x): Buckets 8, 7/9, 6/10, 5/11
   - `"medium_wins"` (5-50x): Buckets 4/12, 3/13
   - `"high_wins"` (50-500x): Buckets 2/14, 1/15
   - `"max_wins"` (500x+): Buckets 0/16
4. **Weighted random selection** (like reel strip positions)

---

## 5. Complete Book Examples

### Example 1: Simple Win (No Bonus Peg)
```json
{
  "id": 1,
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

### Example 2: Bonus Peg Hit + Free Ball Win
```json
{
  "id": 2,
  "payoutMultiplier": 668.5,
  "events": [
    {
      "index": 0,
      "type": "plinkoResult",
      "bucketIndex": 8,
      "multiplier": 0.5,
      "hitBonusPeg": true
    },
    {
      "index": 1,
      "type": "plinkoResult",
      "bucketIndex": 0,
      "multiplier": 666.0,
      "isFreeBall": true
    },
    {
      "index": 2,
      "type": "setTotalWin",
      "amount": 66650
    },
    {
      "index": 3,
      "type": "finalWin",
      "amount": 66650
    }
  ]
}
```

### Example 3: Max Win Edge Bucket
```json
{
  "id": 3,
  "payoutMultiplier": 666,
  "events": [
    {
      "index": 0,
      "type": "plinkoResult",
      "bucketIndex": 16,
      "multiplier": 666.0
    },
    {
      "index": 1,
      "type": "setTotalWin",
      "amount": 66600
    },
    {
      "index": 2,
      "type": "finalWin",
      "amount": 66600
    }
  ]
}
```

---

## 6. Volatility Modes

The backend should respect the `mode` parameter in bet requests:
- `"mild"` - Medium volatility (Max: 666×)
- `"sinful"` - High volatility (Max: 1,666×)
- `"demonic"` - Ultra volatility (Max: 16,666×)

Future bonus modes:
- `"bonus"` - Infernal Bounce (bouncier physics)
- `"super_bonus"` - Demon's Favor (guaranteed bonus peg hit?)

---

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
9. ✅ Bonus peg visual implementation (ready for RGS control)

### ⚠️ Bonus Peg Frontend Status

- ✅ Visual bonus peg renders and pulses
- ✅ Ball collision detection with bonus peg
- ✅ Client-side free ball drop
- ⚠️ **Needs RGS integration** for certification

---

## Testing Strategy

### For Backend Team

1. **Create test books** for each bucket (0-16) across all volatility modes
2. **Test bonus peg scenarios**:
   - Ball hits bonus peg → generates free ball
   - Free ball lands in various buckets
   - Total win = original ball + free ball
3. **Test edge cases**:
   - Bucket 0 (left edge, max win)
   - Bucket 8 (center, low multiplier)
   - Bucket 16 (right edge, max win)
   - Multiple bonus peg hits in succession
4. **Verify calculations**:
   - `setTotalWin.amount` = bet amount × (ball1 multiplier + ball2 multiplier if bonus)
   - All amounts use RGS API_MULTIPLIER correctly

### For Frontend Team

1. Use **Force Result API** to test specific book IDs
2. Verify ball lands in correct bucket 100% of time
3. Test bonus peg books with multiple `plinkoResult` events
4. Check console for physics errors (⚠️ warnings)
5. Verify win amounts match RGS exactly

---

## Console Logs to Monitor

### Normal Spin:
```
📊 RGS Plinko Result: { bucketIndex: 8, multiplier: 0.5 }
🎲 RGS commanded ball drop to bucket: 8
🎯 Ball 0 landed in slot 8 with multiplier 0.5x
✅ Plinko ball animation complete
```

### Bonus Peg Hit:
```
📊 RGS Plinko Result: { bucketIndex: 8, multiplier: 0.5, hitBonusPeg: true }
🎲 RGS commanded ball drop to bucket: 8
🎯 Ball 0 landed in slot 8 with multiplier 0.5x
✅ Plinko ball animation complete
📊 RGS Plinko Result: { bucketIndex: 0, multiplier: 666, isFreeBall: true }
🎲 RGS commanded ball drop to bucket: 0
🎯 Ball 1 landed in slot 0 with multiplier 666x
✅ Plinko ball animation complete
```

**Error case (should NOT happen):**
```
⚠️ PHYSICS ERROR: Ball landed in wrong bucket! { expected: 8, actual: 7, difference: 1 }
```

---

## Critical Notes

- **Physics is cosmetic only** - Ball always lands where RGS says
- **Win comes from RGS** - Frontend doesn't calculate, just displays
- **Certifiable** - All randomness from backend certified math
- **Bucket index is 0-based** - Remember: 0-16, not 1-17
- **Bonus peg MUST be RGS-controlled** for certification
- **Free balls count toward total win** - included in `setTotalWin` amount

---

## Questions for Backend Team

1. Can the math model support **bonus peg probability** per ball drop?
2. Should free balls have **different bucket distributions** than paid balls?
3. Should bonus peg be **always active** or configurable per volatility mode?
4. Should **"Demon's Favor"** bonus mode guarantee bonus peg hits?

---

**Status**: ✅ Frontend Ready - Awaiting Backend Math Implementation (including bonus peg logic)

