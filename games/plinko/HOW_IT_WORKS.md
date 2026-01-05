# How Plinko Optimization Works

## The Challenge

Backend spec requires massive multipliers:
- MILD: 666x max win
- SINFUL: 1666x max win
- DEMONIC: 16666x max win

But we need realistic RTPs:
- MILD: 97.3% RTP (2.7% house edge)
- SINFUL: 96.8% RTP (3.2% house edge)
- DEMONIC: 96.3% RTP (3.7% house edge)

**How can we have 666x multipliers but 97% RTP?**

## The Solution: Weighted Bucket Distributions

### Starting Point (Uniform Distribution)

Each bucket appears once in the CSV:
```csv
0   ← 666x multiplier
1   ← 150x multiplier
...
8   ← 0.5x multiplier
...
16  ← 666x multiplier
```

**Result**: RTP = (666+150+60+...+666)/17 = ~10,720% ❌

### After Optimization

The optimizer adjusts how many times each bucket appears:
```csv
8   ← 0.5x (appears 50,000 times!)
8
8
...
7   ← 1x (appears 20,000 times)
7
7
...
0   ← 666x (appears maybe 1 time out of 100,000)
```

**Result**: Weighted RTP = (50000×0.5 + 20000×1 + ... + 1×666) / 100000 = ~97.3% ✅

## How The Optimizer Works

### Input Targets (from game_optimization.py)
```python
"wincap": {
    rtp: 0.001,   # Contribute only 0.1% to total RTP
    hr: 6000,      # Hit every 6,000 spins
    av_win: 666,   # When it hits, pays 666x
}
```

### Optimizer Logic

1. **Read all simulated outcomes** from lookup table
2. **Group by criteria** (wincap, high_wins, etc.)
3. **Calculate ideal weights** for each outcome to hit BOTH:
   - Target RTP (0.001 for wincap)
   - Target HR (1 in 6,000)
4. **Apply scaling preferences** (favor 1-2x wins, punish <1x)
5. **Write optimized CSV files** with adjusted bucket weights

### Result

The CSV file now has:
- **Bucket 8 (0.5x)**: Appears 10,000+ times (common)
- **Bucket 0 (666x)**: Appears ~17 times out of 100,000 (1 in ~6,000)

Weighted RTP ≈ 97.3% with 666x still possible!

## Example Calculation

If we have 100,000 total drops in the distribution:

| Bucket | Multiplier | Times in CSV | Probability | RTP Contribution |
|--------|------------|--------------|-------------|------------------|
| 8 | 0.5x | 50,000 | 50% | 0.25 (25%) |
| 7/9 | 1x | 30,000 | 30% | 0.30 (30%) |
| 6/10 | 2x | 15,000 | 15% | 0.30 (30%) |
| 5/11 | 4x | 3,000 | 3% | 0.12 (12%) |
| ... | ... | ... | ... | ... |
| 0/16 | 666x | 17 | 0.017% | 0.113 (0.113%) |

**Total**: ~97.3% RTP with 666x hitting ~1 in 6,000 times!

## Respin Feature

The bonus peg adds another layer:
- 5% of drops hit bonus peg → FREE ball
- Free balls use same bucket distribution
- Effective RTP = 97.3% + (5% × 97.3%) ≈ 102.2%

## Optimization Process

### Phase 1: Initial Simulation (Uniform)
```
RTP: ~10,720% (bad!)
All buckets equally likely
```

### Phase 2: Optimizer Runs
```
Rust program analyzes outcomes
Calculates optimal weights
Updates CSV files
```

### Phase 3: Re-simulation (Optimized)
```
RTP: ~97.3% (perfect!)
666x hits ~1 in 6,000 times
Most drops are 0.5x-5x
```

## Key Files

- **reels/MILD.csv**: Bucket weight distribution (optimizer updates this!)
- **lookup_tables/lookUpTable_mild.csv**: All possible outcomes with weights
- **stats_summary.json**: Final RTP, HR, variance stats
- **game_optimization.py**: Target RTPs and HRs

## Why It Works

✅ Backend multipliers unchanged (666x, 1666x, 16666x)  
✅ Frontend gets correct bucket indices  
✅ Display uses backend spec multipliers  
✅ Math model achieves realistic RTPs  
✅ Max wins still possible (just rare!)  
✅ Optimizer handles the heavy lifting  
✅ Fully certifiable (all randomness from RGS)  

The magic is in the **weighted bucket distribution** - massive wins are possible, just extremely rare!


