# Sugar Rush Game

Authentic Sugar Rush slot game implementation with cluster pays and multiplier spots.

**Game Features:**
- 7x7 grid (7 reels, 7 rows)
- Cluster pays: minimum 5 connected symbols (horizontally or vertically)
- Tumble mechanics: winning symbols explode, remaining fall down, new symbols drop
- Multiplier spots: spots on grid that grow with each explosion
- Free spins triggered by scatter symbols (3-7 scatters)

**Basegame:**
- Cluster pays: All symbols pay in blocks of minimum 5 symbols connected horizontally or vertically
- Scatter symbols appear on all reels
- Can trigger free spins with 3, 4, 5, 6, or 7 scatters:
  - 3 scatters = 10 free spins
  - 4 scatters = 12 free spins
  - 5 scatters = 15 free spins
  - 6 scatters = 20 free spins
  - 7 scatters = 30 free spins
- Multiplier spots: When clusters form, first hit creates 2x on that square. Each subsequent hit doubles it (2x → 4x → 8x → 16x... up to 1024x). Multiple multipliers in same cluster add together. In base game, multiplier spots are cleared when tumbling ends.

**Free Spins:**
- Triggered by 3, 4, 5, 6, or 7 scatters (10, 12, 15, 20, or 30 free spins respectively)
- Multiplier spots persist throughout the entire free spins round
- Multiplier spots can continue to grow with each tumble
- Retrigger: 3, 4, 5, 6, or 7 scatters award additional free spins (same amounts)
- Special reels are in play during the feature

**Buy Free Spins:**
- **Regular Free Spins (100x bet)**: Buy to trigger free spins feature - can get 3-7 scatters (10, 12, 15, 20, or 30 free spins)
- **Super Free Spins (500x bet)**: Buy to trigger free spins with 4x starting multipliers on ALL spots immediately - can get 3-7 scatters (10, 12, 15, 20, or 30 free spins). Can only be bought, not spun into.

**Multiplier Spots System:**
- When clusters form, first hit creates a 2x multiplier on that square in the grid
- Each subsequent hit doubles the multiplier (2x → 4x → 8x → 16x → 32x → 64x → 128x → 256x → 512x → 1024x max)
- Multipliers apply to all winning combinations that hit on top of them
- If multiple multipliers are involved in the same winning combination, they add together
- In base game: Marked spots with multipliers last until the end of the tumbling sequence and are cleared when no more tumbles occur
- In free spins: Marked spots and their multipliers remain in place until the end of the round

**Symbols (8 symbols total - NO multiplier symbols!):**
- **H1, H2, H3**: High symbols (3 types)
- **L1, L2, L3, L4**: Low symbols (4 types)  
- **S (Scatter)**: Triggers free spins (3-7 scatters)
- **NO M symbols** - multipliers come from cluster hits on grid spots!

**Max Win:**
- Maximum win is limited to 25,000x bet in both base game and free spins
- If the total win of a FREE SPINS ROUND reaches 25,000x bet, the round immediately ends, win is awarded and all remaining free spins are forfeited
