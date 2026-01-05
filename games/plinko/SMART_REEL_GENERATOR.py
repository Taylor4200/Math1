"""Generate reels that achieve target RTP with good gameplay."""

# Target configuration
# For 96% RTP with these multipliers, calculate required hit rates

M_MILD = [666, 150, 60, 20, 8, 4, 2, 1, 0.5, 1, 2, 4, 8, 20, 60, 150, 666]
TOTAL_REEL = 100000

# Desired hit rates (symmetric buckets)
# Start with rare wins and work down
target_config = {
    "mild": {
        666: 20,      # 1 in 5000 (buckets 0, 16)
        150: 60,      # 1 in 1667
        60: 150,      # 1 in 667
        20: 300,      # 1 in 333
        8: 800,       # 1 in 125
        4: 2000,      # 1 in 50
        2: 5000,      # 1 in 20
        1: 15000,     # 1 in 6.67
        0.5: 76670,   # Rest (fills to 100K)
    }
}

# Calculate if this hits target RTP
def calc_rtp(config, mults):
    total = 0
    for mult, hits in config.items():
        total += mult * hits
    return total / TOTAL_REEL

mild_config = target_config["mild"]
mild_rtp = calc_rtp(mild_config, M_MILD)

print(f"MILD RTP with target config: {mild_rtp:.2%}")
print(f"Target: 96%")
print(f"Difference: {(mild_rtp - 0.96)*100:.2f}%")

# Adjust to hit exactly 96%
# Current: 117.86%
# Need to reduce high multipliers or increase 0.5x

# Let me try: reduce all high mults, increase 0.5x
adjusted_mild = {
    666: 5,       # 1 in 20000 (very rare)
    150: 15,      # 1 in 6667
    60: 40,       # 1 in 2500
    20: 100,      # 1 in 1000
    8: 500,       # 1 in 200
    4: 2000,      # 1 in 50
    2: 5000,      # 1 in 20
    1: 15000,     # 1 in 6.67
    0.5: 77340,   # Rest
}

print("\nAdjusted MILD:")
adj_rtp = calc_rtp(adjusted_mild, M_MILD)
print(f"  RTP: {adj_rtp:.2%}")

# Create the reel
import csv
import random

def create_reel(mode, config, mults):
    reel = []
    for i, mult in enumerate(mults):
        hits = config.get(mult, 0)
        reel.extend([i] * hits)
    
    random.seed(42)
    random.shuffle(reel)
    
    with open(f"reels/{mode.upper()}.csv", 'w', newline='') as f:
        for bucket in reel:
            f.write(f"{bucket}\n")
    
    rtp = sum(config.get(mults[i], 0) * mults[i] for i in range(len(mults))) / len(reel)
    print(f"\n{mode.upper()} reel created: {len(reel)} entries, RTP={rtp:.2%}")
    return rtp

create_reel("mild", adjusted_mild, M_MILD)

print(f"\n{'='*70}")
print("Reel created - now run: python run.py")
print('='*70)







