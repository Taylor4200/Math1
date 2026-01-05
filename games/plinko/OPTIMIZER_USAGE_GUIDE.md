# Perfect Plinko Optimizer - Usage Guide

## ✅ Implementation Complete

The Perfect Plinko Optimizer is fully implemented and tested. It provides mathematical constraint-based optimization with adjustable RTP, prob_less_bet, and bucket hit rates.

## Quick Start

### 1. Optimize All Modes (Recommended)

```bash
cd games/plinko
python run_optimizer.py
```

This will optimize MILD, SINFUL, and DEMONIC modes with current targets.

### 2. Optimize Single Mode

```bash
python run_optimizer.py --mode mild
```

### 3. Custom Optimization

```bash
python run_optimizer.py --custom
# Or via CLI:
python run_optimizer.py --mode mild --target-rtp 0.95 --target-plb 0.40 --max-win-hr 5000
```

## Understanding the Optimizer

### What It Does

- Solves for exact bucket probabilities using scipy SLSQP optimization
- Converts probabilities to weighted CSV distributions (1M entries by default)
- Refines weights iteratively to achieve perfect RTP targets
- Verifies results with Monte Carlo simulation

### Key Constraints

1. **Sum to 1**: All probabilities must sum to 100%
2. **Exact RTP**: Weighted average of multipliers = target RTP
3. **Exact prob_less_bet**: Probability of buckets with mult<1x = target
4. **Bucket HRs**: Specific buckets can have target hit rates (e.g., 1 in 6000)
5. **Min Probability**: All buckets have minimum probability (default: 0.00001)

## Achievable Targets

Based on bucket multipliers analysis:

| Mode | Mult Range | Target RTP | Achievable prob_less_bet | Status |
|------|------------|------------|-------------------------|---------|
| MILD | 0.5 - 666x | 0.9267 | 0.374 (1 sub-1x bucket) | ✅ Working |
| SINFUL | 0.2 - 1666x | 0.8963 | 0.723 (3 sub-1x buckets) | ⚠ Needs tuning |
| DEMONIC | 0 - 16666x | 0.8598 | 0.770 (3 zero buckets) | ⚠ Needs tuning |

### Why These Targets?

The achievable `prob_less_bet` is determined by:
- Number of buckets with multipliers < 1.0
- Target RTP (higher RTP = lower prob_less_bet)
- Bucket HR constraints (rare buckets affect distribution)

Use `python find_achievable_params.py` to discover achievable ranges for your multipliers.

## Configuration

Edit `optimizer_config.py` to adjust targets:

```python
"mild": {
    "target_rtp": 0.9267,              # Exact RTP target
    "target_prob_less_bet": 0.374,      # Probability of sub-1x outcomes
    "bucket_constraints": {
        0: {"hr": 6000},               # Bucket 0: 1 in 6000 spins
        16: {"hr": 6000},              # Bucket 16: 1 in 6000 spins
    },
    "min_bucket_prob": 0.00001,        # Min prob for any bucket
    "scaling_preferences": {           # Soft constraints for feel
        "favor": [
            {"multiplier_range": (1.0, 2.0), "weight": 3.5},
        ],
        "punish": [
            {"multiplier_range": (0.5, 1.0), "weight": 0.4},
        ]
    }
}
```

## Troubleshooting

### Optimization Doesn't Converge

**Symptoms**: "Positive directional derivative" warning, uniform distribution result

**Solutions**:
1. Remove bucket HR constraints temporarily
2. Relax `prob_less_bet` target (use `find_achievable_params.py`)
3. Increase `min_bucket_prob`
4. Simplify scaling preferences

**Example**:
```python
# Temporarily remove bucket constraints
config.configs['sinful']['bucket_constraints'] = {}
```

### RTP Error Too High

**Symptoms**: RTP error > 0.01 (1%)

**Solutions**:
1. Increase total_weight (e.g., 5M or 10M instead of 1M)
2. Run more refinement iterations
3. Check if constraints are mathematically possible

**Example**:
```bash
python run_optimizer.py --mode mild --weight 5000000
```

### Bucket Never Appears

**Symptoms**: Hit rate = infinity for some bucket

**Solutions**:
1. Increase `min_bucket_prob` for that bucket
2. Remove conflicting bucket constraints
3. Verify multiplier isn't creating impossible math

## Advanced Usage

### Find Achievable Parameters

```bash
python find_achievable_params.py
```

This analyzes each mode and shows:
- Achievable RTP ranges for different `prob_less_bet` values
- Achievable `prob_less_bet` for target RTP
- Recommended bucket distribution

### Programmatic Usage

```python
from perfect_optimizer import PlinkoOptimizer
from optimizer_config import OptimizerConfig

# Standard optimization
optimizer = PlinkoOptimizer(mode="mild")
stats = optimizer.solve()
optimizer.save_to_csv("reels/MILD.csv")

# Custom constraints
config = OptimizerConfig()
config.update_target_rtp("mild", 0.95)
config.update_prob_less_bet("mild", 0.40)
config.update_bucket_hr("mild", 0, 5000)

optimizer = PlinkoOptimizer(mode="mild", config=config)
stats = optimizer.solve()
```

### Verify Results

```bash
python verify_optimizer.py
```

Or for a specific mode:

```python
from verify_optimizer import OptimizerVerifier

verifier = OptimizerVerifier("reels/MILD.csv", multipliers)
verifier.print_verification_report(
    target_rtp=0.9267,
    target_plb=0.374,
    target_bucket_hrs={0: 6000, 16: 6000}
)
```

## Files Created

- `optimizer_config.py` - Configuration and targets
- `perfect_optimizer.py` - Core solver
- `weight_generator.py` - Probability → CSV converter
- `run_optimizer.py` - User interface
- `verify_optimizer.py` - Validation tools
- `find_achievable_params.py` - Parameter discovery tool

## Expected Results

### MILD Mode (Well-Tuned)
```
RTP: 0.926700 (exactly)
prob_less_bet: 0.374 (exactly)
Bucket 0 HR: 1 in 6000
Bucket 16 HR: 1 in 6000
Status: ✓ PASS
```

### When Fully Tuned

All modes should achieve:
- RTP error < 0.001 (0.1%)
- prob_less_bet error < 0.01 (1%)
- Bucket HR error < 5%
- Monte Carlo validation passes

## Integration with Game

The optimizer generates `reels/MILD.csv`, `reels/SINFUL.csv`, `reels/DEMONIC.csv` that are directly used by `GameConfig`. No changes to game logic required.

## Tips for Best Results

1. **Start Simple**: Remove bucket constraints first, get RTP/prob_less_bet working
2. **Add Constraints Gradually**: Add bucket HRs one at a time
3. **Use find_achievable_params.py**: Know what's mathematically possible
4. **Increase Weight for Precision**: Use 5M-10M weight for critical applications
5. **Verify Always**: Run verification after optimization

## Support

- Check `PERFECT_OPTIMIZER_README.md` for detailed documentation
- Run `find_achievable_params.py` to understand constraints
- Examine `library/optimization_results_*.json` for detailed statistics
- Review verification reports for specific errors

The optimizer is production-ready for MILD mode and can be tuned for SINFUL/DEMONIC by adjusting constraints in `optimizer_config.py`.


