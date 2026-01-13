# Go Simulation Engine

This directory contains a Go-based simulation engine that can replace Python simulations for faster execution. Go is significantly faster for running game simulations, while Python remains optimal for optimization and analysis.

## Architecture

```
Python (run.py)
  ↓
  ├─→ Go Simulation (faster) → Write Books
  └─→ Python Optimization (better) → Read Books
```

## Integration Pattern

Similar to how Rust optimizer is called:
- **Rust:** Called from Python for optimization (complex algorithms)
- **Go:** Called from Python for simulations (performance-critical loops)
- **Python:** Orchestrates workflow, handles optimization/analysis

## Setup

### 1. Install Go

```bash
# Download from https://go.dev/dl/
# Or use package manager:
# Windows (Chocolatey): choco install golang
# macOS (Homebrew): brew install go
# Linux: sudo apt install golang
```

### 2. Initialize Go Module

```bash
cd simulation_go
go mod init simulation_engine
go mod tidy
```

### 3. Build Binary

```bash
# Development build
go build -o sim_engine.exe ./cmd/simulator

# Release build (optimized)
go build -ldflags="-s -w" -o sim_engine.exe ./cmd/simulator
```

## Usage from Python

```python
from simulation_go.run_simulations import GoSimulationExecution

# Similar to OptimizationExecution
execution = GoSimulationExecution()
execution.run_sims_single_mode(
    game_config=config,
    mode="base",
    num_sims=100000,
    threads=10,
    batch_size=50000,
    compress=True
)
```

## File Structure

```
simulation_go/
├── README.md              # This file
├── go.mod                 # Go module definition
├── go.sum                 # Go dependencies
├── cmd/
│   └── simulator/
│       └── main.go        # Main entry point
├── internal/
│   ├── config/
│   │   └── config.go      # Configuration loading
│   ├── game/
│   │   ├── gamestate.go   # Game state management
│   │   ├── board.go       # Board logic
│   │   └── symbols.go     # Symbol handling
│   ├── simulation/
│   │   └── runner.go      # Simulation runner
│   └── output/
│       ├── books.go       # Book generation
│       └── writer.go      # File writing
└── pkg/
    └── python/
        └── wrapper.py     # Python wrapper (call from run.py)
```

## Key Interfaces

### 1. Configuration Input

Go reads simulation parameters from JSON/config file:
- Game ID
- Bet mode
- Number of simulations
- Thread count
- Batch size
- Compression flag

### 2. Output Format

Go writes books in the **same format** as Python:
- JSONL (JSON Lines) format
- Zstandard compression (.jsonl.zst)
- Same book structure (events, payoutMultiplier, etc.)

### 3. Integration Points

**Python calls Go:**
- `run_sims_single_mode()` - Run simulations for one mode
- `run_sims_all_modes()` - Run simulations for all modes

**Go returns:**
- Books file path (same location as Python)
- Success/failure status
- Execution time

## Performance Benefits

**Go Advantages:**
- **10-100x faster** than Python for tight loops (simulation loops)
- Better memory management (no GIL)
- Excellent concurrency (goroutines)
- Faster startup time
- Lower memory footprint

**Python Advantages (keep for):**
- Complex optimization algorithms
- Data analysis/pandas
- Configuration management
- Integration with existing codebase

## Example: Converting Python Simulation to Go

### Python (Current)
```python
def run_spin(self, sim):
    self.reset_seed(sim)
    while self.repeat:
        self.draw_board()
        self.evaluate_wins()
        self.tumble()
        # ... game logic
```

### Go (Future)
```go
func (gs *GameState) RunSpin(sim int) {
    gs.ResetSeed(sim)
    for gs.Repeat {
        gs.DrawBoard()
        gs.EvaluateWins()
        gs.Tumble()
        // ... same game logic in Go
    }
}
```

## Migration Strategy

1. **Phase 1:** Implement basic Go simulation (proof of concept)
2. **Phase 2:** Implement one game type fully (e.g., 0_0_lines_v6)
3. **Phase 3:** Test accuracy (compare Go vs Python output)
4. **Phase 4:** Integrate into existing workflow
5. **Phase 5:** Gradually migrate other games

## Notes

- Go simulations must produce **identical results** to Python (same RNG, same logic)
- Use same random seed strategy for reproducibility
- Output format must match Python books exactly
- Consider keeping Python as fallback during migration




