# Plinko Optimizer - Current Status & Solution

## 🎯 Problem Identified

You're absolutely right - having 666x and 8x with the same 1 in 100,000 hit rate is terrible gameplay!

## ⚠ The Core Issue

When you have THREE hard constraints:
1. **Exact RTP** (e.g., 96.00%)
2. **Exact prob_less_bet** (e.g., 0.374)
3. **Multiple bucket hit rates** (e.g., 8x at 1 in 50, 666x at 1 in 50,000)

The system becomes **over-constrained** and can't find a solution, OR it zeros out most buckets to meet the constraints.

## ✅ Solution: Choose Your Priority

### Option A: Perfect House Edge Margins (What You Asked For)
**Keep RTP and prob_less_bet perfect, sacrifice bucket HRs**

```python
# optimizer_config.py
"mild": {
    "target_rtp": 0.9600,  # 4.00% house edge
    "target_prob_less_bet": 0.374,
    "bucket_constraints": {},  # NO bucket constraints
    "scaling_preferences": {  # Use STRONG scaling instead
        "favor": [
            {"multiplier_range": (1.0, 2.0), "weight": 100.0},
            {"multiplier_range": (2.0, 4.0), "weight": 50.0},
            {"multiplier_range": (4.0, 8.0), "weight": 25.0},
            {"multiplier_range": (8.0, 20.0), "weight": 10.0},
        ],
        "punish": [
            {"multiplier_range": (100.0, 10000.0), "weight": 100.0},
        ]
    }
}
```

**Result**: Perfect 0.5% house edge margins, natural hit rate gradients

### Option B: Good Gameplay First (Recommended)
**Set reasonable bucket HRs, accept approximate RTP**

```python
"mild": {
    "target_rtp": 0.9600,  # Target (will be close)
    "target_prob_less_bet": 0.374,  # Target (will be close)
    "bucket_constraints": {
        0: {"hr": 50000},    # 666x - Ultra rare
        4: {"hr": 50},       # 8x - Fairly common
        3: {"hr": 200},      # 20x - Uncommon
        2: {"hr": 2000},     # 60x - Rare
        1: {"hr": 10000},    # 150x - Very rare
    },
    "scaling_preferences": {}  # Let constraints do the work
}
```

**Result**: Good gameplay, RTP within ~1% of target

### Option C: Hybrid (Best of Both)
**One or two bucket constraints for anchoring, strong scaling for rest**

```python
"mild": {
    "target_rtp": 0.9600,
    "target_prob_less_bet": 0.374,
    "bucket_constraints": {
        0: {"hr": 50000},    # Only constrain max win
        16: {"hr": 50000},
    },
    "scaling_preferences": {
        "favor": [
            {"multiplier_range": (1.0, 2.0), "weight": 100.0},  # VERY strong
            {"multiplier_range": (4.0, 8.0), "weight": 50.0},
            {"multiplier_range": (8.0, 20.0), "weight": 25.0},
        ],
        "punish": [
            {"multiplier_range": (150.0, 1000.0), "weight": 50.0},
        ]
    }
}
```

**Result**: Good balance - decent RTP precision AND natural gradients

## 🚀 My Recommendation

Use **Option C (Hybrid)** with these settings for ALL THREE MODES:

- Only constrain max win buckets (0, 16) to be ultra-rare
- Use STRONG scaling preferences to create natural gradients
- Accept RTP within 0.5-1% of target (still excellent)
- This gives you:
  - ✅ 0.5% house edge margins (achievable)
  - ✅ Good hit rate gradients (8x common, 666x rare)
  - ✅ All buckets present
  - ✅ Playable and fun

Would you like me to implement Option C?


