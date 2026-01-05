# Hell's Plinko

A fully optimizable Plinko game with three volatility modes, bonus peg respin feature, and RGS integration support.

## Game Mechanics

Unlike traditional slot games, Plinko uses a bucket-based probability system:
- 17 buckets (indexed 0-16)
- Each bucket has a fixed multiplier based on volatility mode
- Ball drops are determined by weighted bucket distributions (stored in "reel" CSV files)
- No reels, no symbols, no paylines - just pure bucket probability
- **BONUS PEG RESPIN**: Ball can hit a bonus peg and trigger a FREE ball drop (no bet cost!)

## Bonus Peg (Respin) Feature

### How It Works
- During each ball drop, there's a chance to hit the "bonus peg" (center peg, row 8)
- If hit, triggers a **FREE ball drop** (no additional bet cost)
- Total win = original ball + free ball winnings
- Free balls can hit the bonus peg again (chain respins possible!)

### Bonus Peg Probabilities
- **MILD**: 5% chance per drop
- **SINFUL**: 8% chance per drop
- **DEMONIC**: 12% chance per drop (higher volatility = more respins)

### RGS Integration
Books with bonus peg hits contain **multiple `plinkoResult` events**:
```json
{
  "events": [
    {
      "type": "plinkoResult",
      "bucketIndex": 8,
      "multiplier": 0.5,
      "hitBonusPeg": true
    },
    {
      "type": "plinkoResult", 
      "bucketIndex": 0,
      "multiplier": 666,
      "isFreeBall": true
    }
  ]
}
```

## Volatility Modes

### MILD Mode (RTP: 97%, Max Win: 666x)
- Lower volatility, frequent small wins
- Good "feel" with lots of 1-2x wins
- Bucket multipliers (0-16): [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]

### SINFUL Mode (RTP: 96%, Max Win: 1,666x)
- Medium volatility, balanced distribution
- More edge outcomes than MILD
- Bucket multipliers (0-16): [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]

### DEMONIC Mode (RTP: 94%, Max Win: 16,666x)
- Extreme volatility, high risk/reward
- Three center buckets pay 0x (instant loss)
- Bimodal distribution favoring edges and center losses
- Bucket multipliers (0-16): [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

## File Structure

### Bucket Distributions (reels/)
- `MILD.csv` - Weighted bucket distribution for MILD mode
- `SINFUL.csv` - Weighted bucket distribution for SINFUL mode  
- `DEMONIC.csv` - Weighted bucket distribution for DEMONIC mode

Each CSV contains a single column of bucket indices (0-16). The optimizer adjusts how many times each bucket appears to achieve target RTP and volatility characteristics.

### Game Logic
- `game_config.py` - Bucket multipliers, bet modes, distributions
- `gamestate.py` - Bucket selection logic (no board, no free spins)
- `game_calculations.py` - Bucket win evaluation
- `game_override.py` - Forced bucket selection for optimization

### Optimization
- `game_optimization.py` - Optimization parameters for all 3 modes
  - Conditions: wincap, high_wins, medium_wins, low_wins, losses
  - Scaling: Favors/punishes specific win ranges for better feel
  - Parameters: Simulation trials, test spins, M2M ratios

## RGS Integration

The game emits `plinkoResult` events compatible with the frontend:

```json
{
  "type": "plinkoResult",
  "bucketIndex": 8,
  "multiplier": 0.5
}
```

See `BACKEND_INTEGRATION_REQUIREMENTS.md` for full RGS spec.

## Running Simulations & Optimization

Generate books, run optimizer, and create optimized distributions:
```bash
python games/plinko/run.py
```

This will:
1. **Generate initial books** with uniform bucket distribution
2. **Run Rust optimizer** to find optimal bucket weights for each mode
3. **Update bucket CSVs** with optimized weights
4. **Create final lookup tables** with target RTPs

Output files:
- `library/lookup_tables/lookUpTable_mild.csv`
- `library/lookup_tables/lookUpTable_sinful.csv`
- `library/lookup_tables/lookUpTable_demonic.csv`
- `library/stats_summary.json` (generate with `python generate_stats_summary.py`)
- `reels/MILD.csv` (updated with optimized weights)
- `reels/SINFUL.csv` (updated with optimized weights)
- `reels/DEMONIC.csv` (updated with optimized weights)

## Optimization

Optimize a specific mode (e.g., MILD):
```python
from optimization_program.run_script import OptimizationExecution
from games.plinko.game_config import GameConfig

config = GameConfig()
OptimizationExecution.run_opt_single_mode(config, "mild", threads=8)
```

The optimizer will:
1. Adjust bucket distribution weights
2. Target specified RTP and hit rates
3. Apply scaling to favor/punish win ranges
4. Generate optimized bucket "reels"

## Key Differences from Slot Games

| Aspect | Slot Games | Plinko |
|--------|-----------|--------|
| Outcome | Reel positions + symbols | Single bucket index (0-16) |
| Payouts | Paytable + line combos | Fixed multiplier per bucket |
| Reels | 5 reels x multiple rows | 1 "reel" of bucket indices |
| Free Spins | Yes | No |
| Scatters | Yes | No |
| Wilds | Yes | No |

## Optimization Metrics

All standard metrics are supported:
- `prob_less_bet` - Probability of winning less than bet amount
- `hr_max` - Hit rate for max win
- `m2m` - Mean-to-median ratio (volatility measure)
- `rtp` - Return to player
- `std`, `var` - Standard deviation and variance
- `skew`, `kurtosis` - Distribution shape

## Notes

- Bucket 0 = leftmost edge (max win)
- Bucket 8 = center (typically lowest multiplier)
- Bucket 16 = rightmost edge (max win)
- All modes cost 1.0 (same bet amount)
- RTPs vary to balance volatility feel
