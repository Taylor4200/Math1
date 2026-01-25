# Integration Guide: Go Simulations

This guide explains how to integrate Go simulations into your existing Python workflow.

## Quick Start

### 1. Build Go Binary

```bash
cd simulation_go
go build -o cmd/simulator/sim_engine.exe ./cmd/simulator
```

### 2. Update Python run.py

Add this to your `games/0_0_lines_v6/run.py`:

```python
from simulation_go.pkg.python.wrapper import GoSimulationExecution

# In your run.py, replace create_books with:
if run_conditions["run_sims"]:
    # Option 1: Use Go (faster)
    execution = GoSimulationExecution()
    execution.run_sims_all_modes(
        game_config=config,
        modes_to_run=target_modes,
        num_sims=num_sim_args,
        threads=num_threads,
        batch_size=batching_size,
        compress=compression,
    )
    
    # Option 2: Keep Python (fallback)
    # create_books(gamestate, config, num_sim_args, batching_size, num_threads, compression, profiling)
    
    generate_configs(gamestate)
```

### 3. Test Integration

```bash
# Test with one mode first
cd games/0_0_lines_v6
python -c "
from game_config import GameConfig
from simulation_go.pkg.python.wrapper import GoSimulationExecution

config = GameConfig()
execution = GoSimulationExecution()
execution.run_sims_single_mode(config, 'base', 1000, 1, 1000, False)
"
```

## Architecture Comparison

### Current (Python)
```
run.py → create_books() → gamestate.run_sims() → multiprocessing → Python loops
```

### New (Go)
```
run.py → GoSimulationExecution → Go binary → goroutines → Go loops
```

## Key Differences

| Aspect | Python | Go |
|--------|--------|-----|
| **Speed** | Slower (GIL, interpreted) | 10-100x faster |
| **Concurrency** | Multiprocessing (process overhead) | Goroutines (lightweight) |
| **Memory** | Higher overhead | Lower overhead |
| **Startup** | Slower (imports) | Faster (compiled binary) |
| **Development** | Easier (existing code) | New codebase needed |

## Implementation Checklist

### Phase 1: Basic Setup
- [x] Create Go module structure
- [x] Create Python wrapper
- [ ] Implement configuration loading
- [ ] Implement basic simulation loop
- [ ] Test binary execution

### Phase 2: Game Logic
- [ ] Port GameState to Go
- [ ] Port board drawing logic
- [ ] Port win evaluation
- [ ] Port tumble mechanics
- [ ] Port free spin logic

### Phase 3: Output
- [ ] Implement book generation (JSONL format)
- [ ] Implement zstandard compression
- [ ] Match Python output format exactly
- [ ] Verify output compatibility

### Phase 4: Integration
- [ ] Replace create_books() calls
- [ ] Test with one game
- [ ] Verify results match Python
- [ ] Update Makefile

### Phase 5: Migration
- [ ] Migrate other games
- [ ] Performance benchmarks
- [ ] Documentation
- [ ] Remove Python fallback

## Porting Game Logic

### Example: Python → Go

**Python (gamestate.py):**
```python
def run_spin(self, sim):
    self.reset_seed(sim)
    self.repeat = True
    while self.repeat:
        self.reset_book()
        self.draw_board()
        self.get_scatterpays_update_wins()
        # ... rest of logic
```

**Go (gamestate.go):**
```go
func (gs *GameState) RunSpin(sim int) error {
    gs.ResetSeed(sim)
    gs.Repeat = true
    
    for gs.Repeat {
        gs.ResetBook()
        gs.DrawBoard()
        gs.GetScatterPaysUpdateWins()
        // ... rest of logic
    }
    return nil
}
```

## Output Format Compatibility

Go must produce **identical** book files to Python:

1. **JSONL Format:** One JSON object per line
2. **Compression:** Zstandard (.jsonl.zst)
3. **Structure:** Same event format, payoutMultiplier, etc.
4. **File Location:** Same directory structure

## Testing

### Verify Output Match

```python
# Compare Go vs Python output
import json
import zstandard as zstd

# Read Python book
with open("python_book.jsonl.zst", "rb") as f:
    py_books = zstd.decompress(f.read()).decode().splitlines()
    py_data = [json.loads(line) for line in py_books]

# Read Go book
with open("go_book.jsonl.zst", "rb") as f:
    go_books = zstd.decompress(f.read()).decode().splitlines()
    go_data = [json.loads(line) for line in go_books]

# Compare
assert len(py_data) == len(go_data)
for i, (py_book, go_book) in enumerate(zip(py_data, go_data)):
    assert py_book["payoutMultiplier"] == go_book["payoutMultiplier"], f"Mismatch at book {i}"
```

## Performance Targets

**Goal:** 10-100x speedup for simulations

- **Python baseline:** ~100k sims in 60 seconds
- **Go target:** ~100k sims in 1-6 seconds

## Troubleshooting

### Binary Not Found
```bash
# Build binary first
cd simulation_go
go build -o cmd/simulator/sim_engine.exe ./cmd/simulator
```

### Output Mismatch
- Check random seed implementation
- Verify game logic matches exactly
- Compare intermediate states

### Performance Issues
- Use `go build -ldflags="-s -w"` for release builds
- Profile with `go tool pprof`
- Check goroutine usage

## Next Steps

1. Start with a simple game (e.g., basic scatter pays)
2. Port one game fully before migrating others
3. Keep Python as fallback during development
4. Gradually migrate once Go version is proven


















