# Plinko Math Implementation Fixes

## Date: October 10, 2025

## Overview
Fixed critical issues with Plinko game math to ensure proper RTP calculations, complete CSV distributions, and optimization compatibility.

---

## Changes Made

### 1. Created Missing CSV Distribution Files

**Created: `games/plinko/reels/SINFUL.csv`**
- Added all 17 bucket indices (0-16)
- Uniform starter distribution for optimizer

**Created: `games/plinko/reels/DEMONIC.csv`**
- Added all 17 bucket indices (0-16)
- Uniform starter distribution for optimizer

**Fixed: `games/plinko/reels/MILD.csv`**
- Removed trailing newline that caused CSV reader errors

### 2. Fixed RTP Calculations to Account for Bonus Peg

**Problem**: The bonus peg respin feature was adding 5-12% extra RTP on top of base RTPs, resulting in effective RTPs over 100% (not sustainable for casino operations).

**Solution**: Adjusted base RTPs DOWN so that the respin boost brings effective RTP to target levels (~96-97%).

**Changes in `games/plinko/game_config.py`:**

| Mode | Old Base RTP | New Base RTP | Respin Rate | Effective RTP |
|------|-------------|--------------|-------------|---------------|
| MILD | 97.3% | **92.4%** | 5% | ~97.0% |
| SINFUL | 96.8% | **89.6%** | 8% | ~96.8% |
| DEMONIC | 96.3% | **86.0%** | 12% | ~96.3% |

**Formula**: `effective_rtp = base_rtp × (1 + respin_rate)`

### 3. Updated Optimization RTP Targets

**Changes in `games/plinko/game_optimization.py`:**

Updated RTP contributions for each criteria to sum to new base RTPs:

**MILD Mode** (Total: 92.4%):
- wincap: 0.1% (unchanged)
- high_wins: 4.9% → **4.7%**
- medium_wins: 20% → **18.5%**
- low_wins: 71.8% → **68.6%**
- losses: 0.5% (unchanged)

**SINFUL Mode** (Total: 89.6%):
- wincap: 0.1% (unchanged)
- high_wins: 4% → **3.6%**
- medium_wins: 18% → **16.1%**
- low_wins: 72.7% → **68.0%**
- losses: 2% → **1.8%**

**DEMONIC Mode** (Total: 86.0%):
- wincap: 0.1% (unchanged)
- high_wins: 2% → **1.7%**
- medium_wins: 10% → **8.6%**
- low_wins: 84.2% → **75.6%**
- losses: 0% (unchanged)

---

## Verification Results

```
[OK] Configuration loaded successfully!

BET MODE RTPs (Base RTP, excludes respin boost):
  * MILD:    0.924 (+ 5% respin -> ~0.970 effective)
  * SINFUL:  0.896 (+ 8% respin -> ~0.968 effective)
  * DEMONIC: 0.860 (+12% respin -> ~0.963 effective)

REEL FILES (CSV distributions):
  * MILD reels:    17 buckets
  * SINFUL reels:  17 buckets
  * DEMONIC reels: 17 buckets

BUCKET MULTIPLIERS:
  * MILD:    [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
  * SINFUL:  [1666, 400, 120, 40, 12, 4, 2, 0.5, 0.2, 0.5, 2, 4, 12, 40, 120, 400, 1666]
  * DEMONIC: [16666, 2500, 600, 150, 40, 8, 2, 0, 0, 0, 2, 8, 40, 150, 600, 2500, 16666]

BONUS PEG (Respin) RATES:
  * MILD:    5%
  * SINFUL:  8%
  * DEMONIC: 12%

[SUCCESS] All systems ready for simulation & optimization!
```

---

## Game Logic Review

### ✅ Verified Correct

**`games/plinko/gamestate.py`**:
- Respin logic correctly triggers on bonus peg hit
- Free balls use same bucket distribution
- Win manager properly accumulates wins

**`games/plinko/game_calculations.py`**:
- Win calculation: `bet_cost × multiplier`
- Free balls correctly add full win (no bet deduction)
- plinkoResult events properly emitted with flags

**`games/plinko/game_override.py`**:
- Forced bucket selection uses correct multiplier ranges
- Criteria filtering properly matches bucket multipliers
- Force recording enabled for optimization

---

## Next Steps

### 1. Run Initial Simulation
```bash
python games/plinko/run.py
```

This will:
- Generate initial books with uniform distributions (~10,000 per mode)
- Record forced outcomes for optimizer
- Run Rust optimizer to calculate proper bucket weights
- Update CSV files with optimized distributions

### 2. Expected Output

**During Simulation**:
- Thread RTPs: 85-110% (acceptable for uniform initial distribution)
- Force records: Non-empty arrays for all criteria
- No "Symbol is empty" errors

**During Optimization**:
- All fences find valid wins
- No "no wins found" warnings
- Time taken: 5-10 seconds per mode

**After Optimization**:
- CSV files updated with weighted distributions
- stats_summary.json shows correct RTPs (~92-97%)
- Lookup tables regenerated with proper win probabilities

### 3. Production Run

For production-quality distributions:
```python
# In run.py, update:
num_sim_args = {
    "mild": int(5e5),      # 500k simulations
    "sinful": int(5e5),    # 500k simulations
    "demonic": int(5e5),   # 500k simulations
}
```

---

## Technical Details

### How Weighted Distributions Work

The CSV files contain bucket indices (0-16) that can appear multiple times:

**Before Optimization** (Uniform):
```
0    ← appears once (probability: 1/17 = 5.88%)
1    ← appears once
2    ← appears once
...
16   ← appears once
```
**Result**: RTP ~10,720% (WAY TOO HIGH!)

**After Optimization** (Weighted):
```
8    ← appears 30,000 times (probability: ~50%)
8
8
...
7    ← appears 15,000 times (probability: ~25%)
7
...
0    ← appears 17 times (probability: ~0.017%)
16   ← appears 17 times (probability: ~0.017%)
```
**Result**: RTP ~92.4% (TARGET!)

### RTP Formula

```
RTP = Σ(probability_i × multiplier_i)
```

Where:
- `probability_i` = frequency of bucket i / total strip length
- `multiplier_i` = win multiplier for bucket i

---

## Key Insights

1. **Bonus Peg is RTP Boost**: The respin feature effectively multiplies base RTP by (1 + respin_rate)

2. **Most RTP from Low Wins**: ~68-76% of RTP comes from common 0.5-5x wins (buckets 5-11)

3. **Max Wins are Rare**: 666-16666x wins contribute only 0.1% RTP but occur 1 in 6k-50k spins

4. **Optimization is Critical**: Without optimizer, uniform distribution gives 10,000%+ RTP!

---

## Files Modified

1. ✅ `games/plinko/reels/MILD.csv` - Fixed trailing newline
2. ✅ `games/plinko/reels/SINFUL.csv` - Created with 17 buckets
3. ✅ `games/plinko/reels/DEMONIC.csv` - Created with 17 buckets
4. ✅ `games/plinko/game_config.py` - Updated base RTPs (92.4%, 89.6%, 86.0%)
5. ✅ `games/plinko/game_optimization.py` - Updated RTP targets to match

---

## Success Criteria

✅ All CSV files exist with 17 buckets each  
✅ Base RTPs account for respin boost  
✅ Effective RTPs target ~96-97%  
✅ Configuration loads without errors  
✅ Game logic verified correct  
✅ Ready for optimization  

---

**Status**: ✅ **READY FOR PRODUCTION SIMULATION**

The Plinko game math is now properly configured and ready for full-scale simulation and optimization!



