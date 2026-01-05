# Diagnosing "No Negative Pigs" Issue

## What This Means

If the optimizer can't find **ANY** negative pigs (RTP < avg_win), it suggests:

### Possible Issues:

1. **Fence Configuration Mismatch** ⚠️
   - Your fence says: `hr=4.5, rtp=0.651` → `avg_win = 4.5 × 0.651 = 2.93x`
   - But your **actual books** might have higher average wins
   - **Result**: All generated distributions have RTP > 2.93x

2. **Books Are Too High** ⚠️
   - Your books might have too many high wins
   - The win distribution is skewed upward
   - **Result**: Can't create low-RTP distributions

3. **Pig Generation Algorithm Issue** ⚠️
   - The random pig generation might be biased
   - Not exploring the low-RTP space properly
   - **Result**: Always generates high-RTP pigs

## How to Diagnose

### Step 1: Check Actual Book RTP
```python
# Check what the actual average win is in your books
# This should match your fence configuration
```

### Step 2: Verify Fence Configuration
Your "basegame" fence:
- `hr=4.5` (hits 1 in 4.5 spins)
- `rtp=0.651` (65.1% RTP)
- `avg_win = 4.5 × 0.651 = 2.93x`

**Question**: Does your actual basegame have an average win of ~2.93x?

### Step 3: Check Win Distribution
Look at your lookup table - are there enough low wins (< 2.93x) to create negative pigs?

## Solutions

### Option 1: Fix Fence Configuration (If Wrong)
If your actual basegame has different stats:
```python
"basegame": ConstructConditions(
    hr=4.5,      # Adjust if wrong
    rtp=0.651    # Adjust if wrong
).return_dict(),
```

### Option 2: Regenerate Books (If Books Are Wrong)
If the books have too many high wins, you might need to:
- Adjust paytable
- Regenerate books
- Check game logic

### Option 3: Adjust Pig Generation (If Algorithm Issue)
Make the algorithm try harder to find negative pigs by:
- Increasing iterations
- Adjusting generation strategy
- Creating fallback pigs (but maintain variance!)

## The Real Question

**Is your fence configuration correct?**

If `hr=4.5, rtp=0.651` is correct, then the books should support finding negative pigs. If it can't find ANY, either:
1. The books are wrong (too many high wins)
2. The fence config is wrong (doesn't match reality)
3. The algorithm needs adjustment

**You're right to want PROPER math** - this needs to be fixed at the source, not worked around.
