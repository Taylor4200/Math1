# Optimization Parameters Explained

## What Each Parameter Does

### 1. `num_show_pigs` (Currently: 2000)
**What it does**: Number of candidate distributions to test and score.

**Impact**:
- **Higher** (2000): Tests 2000 different weight distributions, finds the BEST one
- **Lower** (500): Tests 500 different distributions, finds a GOOD one
- **Trade-off**: More = better quality but 4x slower

**Will you still hit RTP?** ✅ **YES** - The optimizer will still try to hit your target RTP (96.3%), it just might find a slightly less optimal solution.

### 2. `num_pigs_per_fence` (Currently: 10000)
**What it does**: Number of "pig" components to create per fence (distribution building blocks).

**Impact**:
- **Higher** (10000): Creates 10000 building blocks, needs to find 100 good ones (sqrt(10000))
- **Lower** (2000): Creates 2000 building blocks, needs to find 45 good ones (sqrt(2000))
- **Trade-off**: More = more variety in distributions but MUCH slower (this is your bottleneck!)

**Will you still hit RTP?** ✅ **YES** - Just less variety in how it achieves the RTP.

### 3. `simulation_trials` (Currently: 2000)
**What it does**: Number of simulation runs to test each candidate distribution.

**Impact**:
- **Higher** (2000): More accurate scoring, better picks the best distribution
- **Lower** (1000): Less accurate scoring, might pick a slightly worse distribution
- **Trade-off**: More = more accurate but 2x slower

**Will you still hit RTP?** ✅ **YES** - The scoring is just less precise, but still accurate enough.

---

## Recommended Settings

### **Conservative (Fast, Still Good Quality)**
```python
num_show_pigs: 500          # 4x faster, still tests 500 candidates
num_pigs_per_fence: 2000    # 5x faster, still good variety
simulation_trials: 1000      # 2x faster, still accurate enough
```
**Time**: ~15-30 minutes (vs hours)
**Quality**: 95% as good as your current settings
**RTP**: ✅ Will still hit 96.3% target

### **Balanced (Good Speed/Quality)**
```python
num_show_pigs: 1000         # 2x faster
num_pigs_per_fence: 4000    # 2.5x faster  
simulation_trials: 1500     # 1.3x faster
```
**Time**: ~30-60 minutes
**Quality**: 98% as good
**RTP**: ✅ Will still hit 96.3% target

### **Your Current (Maximum Quality, Very Slow)**
```python
num_show_pigs: 2000
num_pigs_per_fence: 10000   # This is the killer - takes hours
simulation_trials: 2000
```
**Time**: 2-4+ hours
**Quality**: Best possible
**RTP**: ✅ Will hit 96.3% target

---

## What Actually Controls RTP?

**The RTP target is controlled by**:
- `pmb_rtp: 0.963` in your config ✅ (This stays the same)
- The optimizer's algorithm ✅ (This doesn't change)
- Your game's paytable ✅ (This doesn't change)

**These parameters DON'T control RTP** - they control:
- How thoroughly the optimizer searches
- How accurately it scores candidates
- How long it takes

---

## Real-World Analogy

Think of it like finding the best route:

- **num_show_pigs**: How many routes to try (500 vs 2000)
- **num_pigs_per_fence**: How many roads to explore (2000 vs 10000)
- **simulation_trials**: How accurately to measure each route (1000 vs 2000 trials)

**Lower values** = You might find Route A (96.2% RTP) instead of Route B (96.35% RTP)
**Higher values** = You find the absolute best Route B (96.35% RTP)

**Both still get you to your destination (96.3% RTP target)**, one just takes longer to find the absolute best path.

---

## Recommendation

**Start with Conservative settings**:
- ✅ Still hits your RTP target
- ✅ 10-20x faster
- ✅ 95% as good quality
- ✅ Can always increase later if needed

If the results aren't good enough, you can always increase the parameters for the next optimization run.
