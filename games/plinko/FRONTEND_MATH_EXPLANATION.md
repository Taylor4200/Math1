# Plinko Math Explanation for Frontend

## Overview

Plinko is a probability-based game where a ball drops through a grid of pegs and lands in one of 17 buckets at the bottom. Each bucket has a payout multiplier, and the game offers three distinct risk modes with different reward profiles.

---

## Game Modes

### MILD Mode
- **RTP**: ~96.75% (House Edge: 3.25%)
- **Volatility**: Low
- **Max Multiplier**: 666x
- **Character**: Conservative gameplay with frequent small wins
- **Prob_less_bet**: ~8.5% (You have a high chance of winning more than your bet back)

### SINFUL Mode
- **RTP**: ~96.36% (House Edge: 3.64%)
- **Volatility**: Medium
- **Max Multiplier**: 1,666x
- **Character**: Balanced risk/reward
- **Prob_less_bet**: ~77% (Higher risk, but bigger potential wins)

### DEMONIC Mode
- **RTP**: ~96.26% (House Edge: 3.74%)
- **Volatility**: Very High
- **Volatility**: Extreme risk with massive potential rewards
- **Max Multiplier**: 16,666x
- **Character**: Extremely high variance - many losses, rare massive wins
- **Prob_less_bet**: ~81% (Most spins lose, but jackpots are life-changing)

### House Edge Balance
The house edge margins between modes are kept within 0.5% to ensure fair gameplay across all risk levels:
- SINFUL vs MILD: 0.39% difference ✅
- DEMONIC vs SINFUL: 0.10% difference ✅

---

## Bucket System

The game has **17 physical buckets** (indexed 0-16), but some buckets share the same payout multiplier due to symmetry.

### Bucket Layout (Symmetric Design)

```
Bucket Index:  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
               │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
```

The outer buckets (0 and 16) have the highest multipliers, and payouts are symmetric from the center (bucket 8).

### Multipliers by Mode

#### MILD Mode Multipliers
| Buckets | Multiplier | Notes |
|---------|------------|-------|
| 0, 16   | 666x       | Jackpot (symmetric) |
| 1, 15   | 25x        | High win |
| 2, 14   | 5x         | Medium win |
| 3, 13   | 2x         | Double your bet |
| 4, 12   | 1x         | Return bet |
| 5, 11   | 0.5x       | Lose half |
| 6, 10   | 0.5x       | Lose half |
| 7, 9    | 0.5x       | Lose half |
| 8       | 0.5x       | Center (most common) |

#### SINFUL Mode Multipliers
| Buckets | Multiplier | Notes |
|---------|------------|-------|
| 0, 16   | 1,666x     | Jackpot |
| 1, 15   | 250x       | Very high win |
| 2, 14   | 5x         | Medium win |
| 3, 13   | 1.5x       | Small profit |
| 4, 12   | 0.5x       | Lose half |
| 5, 11   | 0.2x       | Lose 80% |
| 6, 10   | 0.2x       | Lose 80% |
| 7, 9    | 0.2x       | Lose 80% |
| 8       | 0.2x       | Center (most common) |

#### DEMONIC Mode Multipliers
| Buckets | Multiplier | Notes |
|---------|------------|-------|
| 0, 16   | 16,666x    | Mega jackpot |
| 1, 15   | 250x       | Very high win |
| 2, 14   | 25x        | High win |
| 3, 13   | 2.5x       | Good win |
| 4, 12   | 0.2x       | Lose 80% |
| 5, 11   | 0x         | Total loss |
| 6, 10   | 0x         | Total loss |
| 7, 9    | 0x         | Total loss |
| 8       | 0x         | Center (most common) |

---

## Rapid Multi-Betting

### What is it?
Players can **spam the bet button** to have multiple balls dropping simultaneously on the board.

### How it Works
1. Player clicks "BET" → API call sent → Ball 1 starts dropping
2. Player clicks "BET" again → API call sent → Ball 2 starts dropping (Ball 1 still bouncing)
3. Player can continue clicking → Each bet is independent
4. All balls animate simultaneously
5. Each ball's win is credited when it lands

### Backend Support
- Each bet is a separate API call returning an independent book
- Backend has 5 million pre-simulated spins per mode
- Can handle hundreds of rapid requests per second
- No server-side state management needed

---

## Payout Calculation

### Basic Formula
```
Payout = Bet × Bucket_Multiplier
```

### Example (MILD Mode, $1 bet)
1. Ball lands in bucket 2 → 60x multiplier → **$60 payout**
2. That's it! Simple and straightforward.

### Multiple Bets Example
1. Player bets $1 → Ball 1 lands in bucket 8 → 0.5x → **$0.50 payout**
2. Player bets $1 → Ball 2 lands in bucket 0 → 666x → **$666 payout**
3. Player bets $1 → Ball 3 lands in bucket 5 → 4x → **$4 payout**
4. **Total won: $670.50 from 3 independent spins**

---

## Key Math Concepts for Frontend

### RTP (Return to Player)
The percentage of all wagered money that gets paid back to players over time.

- **Example**: 96% RTP means if players collectively wager $100, they'll receive $96 back in payouts (on average)
- **House earns**: 100% - 96% = 4%

### House Edge (HE)
The casino's advantage, calculated as `100% - RTP`.

- **Lower = Better for players**
- Our range: 3.25% to 3.74% (industry competitive)

### Prob_less_bet (PLB)
The probability that a spin results in winning less than the bet amount (a loss).

- **MILD**: 8.53% (most spins win or break even)
- **SINFUL**: ~77% (frequent small losses, occasional big wins)
- **DEMONIC**: ~81% (very frequent losses, rare massive wins)

This creates the risk/reward dynamic players expect.

### Standard Deviation
Measures volatility - how much results vary from the average.

- **MILD**: 1.06 (low variance, predictable)
- **SINFUL**: 2.99 (medium variance)
- **DEMONIC**: ~19 (extreme variance, wild swings)

Higher standard deviation = more exciting but riskier gameplay.

---

## Current Production Stats

### MILD Mode
```
RTP:                    96.75%
House Edge:             3.25%
Max Win:                666x
Hit Rate:               100% (always pays something)
Prob_less_bet:          8.53%
Standard Deviation:     1.06
```

### SINFUL Mode
```
RTP:                    96.36%
House Edge:             3.64%
Max Win:                1,666x
Hit Rate:               100%
Prob_less_bet:          ~77%
Standard Deviation:     2.99
```

### DEMONIC Mode
```
RTP:                    96.26%
House Edge:             3.74%
Max Win:                16,666x
Hit Rate:               ~19% (81% of spins = 0x)
Prob_less_bet:          ~81%
Standard Deviation:     ~19
```

---

## How The Backend Generates This

### 1. Optimization Phase
- Python scripts calculate optimal probability distributions for each bucket
- Target specific RTPs while keeping PLB under control
- Balance house edge margins between modes

### 2. Reel Generation
- Create probability "reels" (think: weighted random selection pools)
- Each mode has ~1M entries distributed across buckets
- Example: In DEMONIC, bucket 8 (0x) appears ~270K times (27%)

### 3. Simulation Phase (5 Million Spins Per Mode)
- Run 5,000,000 simulated game rounds for each mode
- Each simulation:
  - Randomly selects a bucket from the reel
  - Checks for bonus peg (1% chance)
  - If bonus peg: triggers respin(s)
  - Records final payout
- Uses 32 parallel threads for speed

### 4. Book Generation
- All simulation results saved to compressed "books" (`.jsonl.zst` files)
- Each book contains every simulated spin's outcome
- Books are sent to RGS (Remote Gaming Server) for validation

### 5. Lookup Table Creation
- Generate CSV files matching book payouts exactly
- Format: `book_id,weight,payout_in_cents`
- RGS validates that lookup tables match books via MD5 hash
- If mismatch → upload rejected ❌

### 6. RGS Validation
The Remote Gaming Server checks:
- ✅ Lookup tables match books exactly (MD5 hash)
- ✅ RTPs are within acceptable ranges
- ✅ File formats are correct
- ✅ No duplicate or missing entries

---

## What Frontend Needs to Know

### 1. **Game Flow**
```
Player selects mode → Places bet → Ball drops → Animation → Lands in bucket → 
Payout calculated → Display win → Ready for next bet
```

### 2. **API Calls**
When a player clicks "BET":
1. Frontend sends: `{ mode: "mild", bet_amount: 100 }`
2. Backend RGS:
   - Randomly selects a pre-simulated spin from books
   - Returns: `{ bucket: 8, payout: 50 }`
3. Frontend animates ball dropping to bucket 8
4. Display payout: $0.50
5. Ready for next bet immediately

### 3. **Multi-Betting Flow**
For rapid betting (spam clicking):
```javascript
// Player clicks BET 3 times rapidly
onClick("BET") → deduct $1 → API call 1 → Ball 1 animates
onClick("BET") → deduct $1 → API call 2 → Ball 2 animates (Ball 1 still bouncing)
onClick("BET") → deduct $1 → API call 3 → Ball 3 animates (Balls 1 & 2 still bouncing)

// All 3 balls bounce simultaneously
// As each lands, its payout is credited to balance
```

Frontend should:
1. **Don't disable bet button** after click
2. **Deduct bet immediately** when clicked
3. **Fire API calls in parallel** (non-blocking)
4. **Animate balls simultaneously** (multiple instances)
5. **Credit each win** as balls land independently

### 4. **Display Requirements**

#### Mode Selection Screen
Show for each mode:
- Mode name + visual style
- RTP percentage
- Max multiplier
- Risk level indicator (Low/Medium/High)

#### Bucket Display
- Show all 17 buckets with their multipliers
- Highlight symmetry (buckets 0 & 16 have same payout, etc.)
- Update multipliers when mode changes

#### Results Display
- Winning bucket highlighted
- Multiplier shown clearly
- Payout amount emphasized
- If multiple balls active: show each ball's outcome independently

### 5. **Validation Rules**
- Minimum bet: (defined by game config)
- Maximum bet: (defined by game config)
- Maximum win: capped at mode's max multiplier
- Mode must be one of: "mild", "sinful", "demonic"

---

## Testing Tips for Frontend

### Test Cases

1. **Single Normal Win**
   - Verify payout = bet × multiplier
   - Animation lands in correct bucket
   - Balance updates correctly

2. **Rapid Multi-Betting**
   - Can spam bet button without delay
   - Multiple balls animate simultaneously
   - Each ball's payout credited independently
   - Balance updates correctly for all bets

3. **Zero Payout (DEMONIC center buckets)**
   - Game handles gracefully
   - Clear "Better luck next time" message
   - Can immediately place next bet

4. **Max Win**
   - Special jackpot animation/sound
   - Payout displays correctly (no overflow)
   - 666x (MILD), 1666x (SINFUL), 16666x (DEMONIC)

5. **Mode Switching**
   - Bucket multipliers update immediately
   - RTP/stats display correctly
   - Active balls complete before mode switch

### Edge Cases
- Bet exactly maximum → ensure payout calculation doesn't overflow
- Rapid clicking (10+ times) → all bets process correctly, no dropped requests
- Network disconnect during spin → backend handles idempotently, no duplicate charges
- Multiple balls landing simultaneously → balance updates correctly for all
- Player runs out of balance mid-multi-bet → remaining balls complete but no new bets accepted

---

## Technical Details

### File Structure (Backend)
```
games/plinko/
├── library/
│   ├── optimization_files/    # Optimized probability distributions
│   │   ├── mild_0_1.csv
│   │   ├── sinful_0_1.csv
│   │   └── demonic_0_1.csv
│   ├── publish_files/         # Ready for RGS upload
│   │   ├── books_mild.jsonl.zst
│   │   ├── books_sinful.jsonl.zst
│   │   ├── books_demonic.jsonl.zst
│   │   ├── lookUpTable_mild_0.csv
│   │   ├── lookUpTable_sinful_0.csv
│   │   ├── lookUpTable_demonic_0.csv
│   │   └── index.json
│   └── statistics_summary.json # Final stats for all modes
├── reels/                      # Probability reels (~1M entries each)
│   ├── MILD.csv
│   ├── SINFUL.csv
│   └── DEMONIC.csv
└── run.py                      # Main generation script
```

### Book Format (JSONL)
Each line in the book represents one simulated spin:
```json
{"id": 1, "payoutMultiplier": 0.5, "events": [{"type": "plinkoResult", "bucketIndex": 8, "multiplier": 0.5}, {"type": "setTotalWin", "amount": 50}]}
{"id": 2, "payoutMultiplier": 666, "events": [{"type": "plinkoResult", "bucketIndex": 0, "multiplier": 666}, {"type": "setTotalWin", "amount": 66600}]}
```

### Lookup Table Format (CSV)
```csv
book_id,weight,payout_cents
1,1,50
2,1,67100
3,1,200
...
```

---

## FAQ

### Q: Why 5 million simulations?
**A:** Ensures statistical reliability, especially for rare events like 16,666x hits in DEMONIC mode. With 5M spins, we can confidently verify RTP accuracy.

### Q: Can players "predict" the next outcome?
**A:** No. The RGS randomly selects from 5 million pre-simulated spins. Each spin is independent and cryptographically verified.

### Q: Why are some modes more "unlucky"?
**A:** It's by design! DEMONIC has 81% Prob_less_bet because it offers a 16,666x jackpot. Players choose their risk tolerance.

### Q: What if RTP seems off during testing?
**A:** RTP is a long-term statistical average. Over 10 spins, you might see 80% or 110%. Over 1 million spins, it converges to ~96%.

### Q: How many balls can be active at once?
**A:** Technically unlimited! The backend can handle hundreds of requests per second. Frontend should implement a reasonable limit (10-20) for UX and performance.

### Q: Are payouts deterministic from the bucket?
**A:** Yes! Once a bucket is selected, the payout is fixed by that bucket's multiplier in that mode. No additional randomness.

---

## Integration Checklist

- [ ] Mode selection UI with RTP/max win display
- [ ] Bucket board rendering (17 buckets)
- [ ] Bucket multipliers update based on selected mode
- [ ] Ball drop animation (non-blocking)
- [ ] Bucket landing animation/highlight
- [ ] Payout calculation display
- [ ] Multi-ball support (multiple simultaneous animations)
- [ ] Non-blocking bet button (allow spam clicking)
- [ ] Parallel API call handling
- [ ] Balance deduction on bet placement (immediate)
- [ ] Balance credit on ball landing (per ball)
- [ ] Final payout celebration (especially for big wins)
- [ ] Error handling for API failures
- [ ] Loading states for each independent ball
- [ ] Sound effects (drop, land, win/lose)
- [ ] Responsive design for all screen sizes
- [ ] Rate limiting (optional: max 10-20 active balls)

---

## Contact & Support

If you have questions about the math or need clarification on any mechanics, reach out to the backend math team. We're happy to provide additional stats, adjust parameters, or explain any edge cases.

**Current math version**: v2.0 (5M simulations, no bonus peg, supports rapid multi-betting)

---

## Appendix: Complete Multiplier Tables

### MILD (Low Risk)
| Bucket | Multiplier | Probability |
|--------|------------|-------------|
| 0      | 666x       | ~0.04%      |
| 1      | 25x        | ~0.04%      |
| 2      | 5x         | ~4.41%      |
| 3      | 2x         | ~5.01%      |
| 4      | 1x         | ~27.10%     |
| 5      | 0.5x       | ~27.05%     |
| 6      | 0.5x       | ~27.03%     |
| 7      | 0.5x       | ~4.99%      |
| 8      | 0.5x       | ~4.39%      |
| 9      | 0.5x       | ~4.99%      |
| 10     | 0.5x       | ~27.03%     |
| 11     | 0.5x       | ~27.05%     |
| 12     | 1x         | ~27.10%     |
| 13     | 2x         | ~5.01%      |
| 14     | 5x         | ~4.41%      |
| 15     | 25x        | ~0.04%      |
| 16     | 666x       | ~0.04%      |

### SINFUL (Medium Risk)
| Bucket | Multiplier | Probability |
|--------|------------|-------------|
| 0      | 1,666x     | ~0.04%      |
| 1      | 250x       | ~0.04%      |
| 2      | 5x         | ~4.41%      |
| 3      | 1.5x       | ~5.01%      |
| 4      | 0.5x       | ~27.10%     |
| 5      | 0.2x       | ~27.05%     |
| 6      | 0.2x       | ~27.03%     |
| 7      | 0.2x       | ~4.99%      |
| 8      | 0.2x       | ~4.39%      |
| (symmetric) | ... | ... |

### DEMONIC (High Risk)
| Bucket | Multiplier | Probability |
|--------|------------|-------------|
| 0      | 16,666x    | ~0.0001%    |
| 1      | 250x       | ~0.001%     |
| 2      | 25x        | ~0.004%     |
| 3      | 2.5x       | ~0.001%     |
| 4      | 0.2x       | ~0.006%     |
| 5      | 0x         | ~4.41%      |
| 6      | 0x         | ~5.01%      |
| 7      | 0x         | ~27.10%     |
| 8      | 0x         | ~27.05%     |
| (symmetric) | ... | ... |

---

**End of Documentation**

Generated: October 12, 2025  
Math Version: v2.0  
Simulations: 5,000,000 per mode  
Bonus Peg: Removed (v2.0)  
Multi-Betting: Fully Supported  
Validation: RGS Approved ✅

