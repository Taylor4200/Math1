# GUI Tool Architecture: Building Inside SDK

## ✅ **Recommendation: Build Inside SDK**

### Why Build Inside SDK?

1. **Direct Access**: Use all existing code without duplication
2. **Enhance SDK**: Make SDK functions more reusable as you build GUI
3. **Single Codebase**: Easier maintenance, versioning, and deployment
4. **Natural Integration**: GUI is essentially a wrapper for SDK functionality
5. **Better Organization**: Can structure it cleanly without cluttering core SDK

---

## Proposed Directory Structure

```
math-sdk/
├── src/                    # Core SDK (unchanged)
├── games/                  # Game implementations (unchanged)
├── utils/                  # Utilities (unchanged)
├── optimization_program/   # Rust optimizer (unchanged)
├── tools/                  # 🆕 NEW: GUI and development tools
│   ├── gui/                # GUI application
│   │   ├── app.py          # Main Streamlit/FastAPI app
│   │   ├── pages/          # Multi-page GUI
│   │   │   ├── lookup_explorer.py
│   │   │   ├── rtp_optimizer.py
│   │   │   ├── compliance_checker.py
│   │   │   ├── game_server.py
│   │   │   └── analytics.py
│   │   ├── components/     # Reusable UI components
│   │   │   ├── rtp_calculator.py
│   │   │   ├── distribution_chart.py
│   │   │   └── weight_adjuster.py
│   │   └── api/            # API endpoints (if FastAPI)
│   │       ├── lookup_api.py
│   │       ├── rtp_api.py
│   │       └── optimization_api.py
│   ├── server/             # Local game server
│   │   ├── local_server.py # Flask/FastAPI server for math files
│   │   └── static/         # Served files
│   └── requirements.txt    # GUI-specific dependencies
├── tests/                  # Tests (unchanged)
└── docs/                   # Documentation (unchanged)
```

---

## Benefits of This Structure

### 1. **Clean Separation**
- GUI code in `tools/gui/` - doesn't clutter core SDK
- Core SDK remains focused and clean
- Easy to find GUI-related code

### 2. **Easy Integration**
```python
# GUI can directly import SDK
from src.state.run_sims import create_books
from utils.rgs_verification import execute_all_tests
from utils.analysis.distribution_functions import calculate_rtp
```

### 3. **Optional Installation**
```python
# tools/requirements.txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
# ... GUI-specific deps only
```

Users can:
- Use SDK without GUI: `pip install -r requirements.txt` (core only)
- Use SDK with GUI: `pip install -r tools/requirements.txt` (includes GUI)

### 4. **Enhance SDK While Building**
As you build GUI, you'll naturally improve SDK:

```python
# Before: utils/analysis/distribution_functions.py
def calculate_rtp(dist: dict, bet_cost: float) -> float:
    # Basic calculation
    ...

# After: Enhanced for GUI
def calculate_rtp(
    dist: dict, 
    bet_cost: float,
    return_breakdown: bool = False  # 🆕 GUI enhancement
) -> float | dict:
    # Calculate RTP
    rtp = ...
    
    if return_breakdown:
        # Return detailed breakdown for GUI
        return {
            'rtp': rtp,
            'by_range': breakdown_by_range,
            'contributions': contributions
        }
    return rtp
```

---

## Entry Points

### Option 1: Streamlit (Quick Start)
```bash
# Run GUI
streamlit run tools/gui/app.py

# Or add to Makefile
make gui
```

### Option 2: FastAPI + React (Production)
```bash
# Start backend
python tools/gui/api/main.py

# Start frontend (separate)
cd tools/gui/frontend && npm start
```

### Option 3: CLI Wrapper
```bash
# SDK command-line tool
python -m tools.cli --gui
python -m tools.cli --server
python -m tools.cli --check-compliance
```

---

## SDK Enhancements While Building GUI

### 1. **Make Functions More Reusable**
```python
# Current: utils/rgs_verification.py
def execute_all_tests(config):
    # Runs all tests, prints to console
    ...

# Enhanced: Add return values for GUI
def execute_all_tests(config, return_results: bool = False):
    results = {}
    # ... run tests
    if return_results:
        return results  # GUI can display
    else:
        print_results(results)  # CLI behavior
```

### 2. **Add Real-Time Calculation**
```python
# New: utils/rtp/real_time_calculator.py
class RealTimeRTPCalculator:
    """Fast RTP calculation for GUI weight adjustments"""
    
    def calculate_from_weights(self, weights: dict, payouts: dict) -> float:
        # Optimized for real-time updates
        ...
    
    def calculate_breakdown(self, weights: dict, payouts: dict) -> dict:
        # Return detailed breakdown
        ...
```

### 3. **Add Progress Callbacks**
```python
# Enhanced: optimization_program/run_script.py
def run_optimization(
    config, 
    mode, 
    threads,
    progress_callback=None  # 🆕 GUI can hook in
):
    if progress_callback:
        progress_callback(0, "Starting...")
    # ... optimization
    if progress_callback:
        progress_callback(50, "Halfway...")
    # ...
```

---

## Development Workflow

### Phase 1: Setup Structure
1. Create `tools/` directory
2. Set up basic GUI framework (Streamlit)
3. Create first page (Lookup Table Explorer)

### Phase 2: Build Core Features
1. RTP Calculator (reuse `calculate_rtp`)
2. Compliance Checker (reuse `rgs_verification`)
3. Distribution Visualizer (new, but uses existing data)

### Phase 3: Enhance SDK
1. Add return values to existing functions
2. Add progress callbacks to long operations
3. Create reusable calculation modules

### Phase 4: Advanced Features
1. Interactive optimization (enhance Rust integration)
2. Local game server
3. Crowd simulation

---

## Example: Enhanced SDK Function

```python
# utils/rtp/calculator.py (NEW - created for GUI)
"""Enhanced RTP calculation with breakdown support"""

from utils.analysis.distribution_functions import calculate_rtp

def calculate_rtp_with_breakdown(
    lookup_table_path: str,
    bet_cost: float = 1.0,
    win_ranges: list = None
) -> dict:
    """
    Calculate RTP with detailed breakdown for GUI visualization.
    
    Returns:
        {
            'rtp': 0.963,
            'total_weight': 100000,
            'by_range': {
                '0.0-0.5x': {'rtp_contribution': 0.452, 'count': 45231},
                '0.5-1.0x': {'rtp_contribution': 0.251, 'count': 25123},
                ...
            },
            'top_contributors': [...]
        }
    """
    # Load lookup table
    dist = make_win_distribution(lookup_table_path)
    
    # Calculate base RTP
    rtp = calculate_rtp(dist, bet_cost)
    
    # Calculate breakdown
    breakdown = _calculate_breakdown(dist, win_ranges)
    
    return {
        'rtp': rtp,
        'total_weight': sum(dist.values()),
        'by_range': breakdown,
        'top_contributors': _get_top_contributors(dist)
    }
```

This function:
- ✅ Reuses existing `calculate_rtp`
- ✅ Adds GUI-specific features
- ✅ Can be used by both CLI and GUI
- ✅ Makes SDK more powerful

---

## Conclusion

**Build inside SDK** because:
1. ✅ Natural integration
2. ✅ Enhances SDK as you build
3. ✅ Single codebase
4. ✅ Easy to maintain
5. ✅ Users get both CLI and GUI

**Structure**: `tools/gui/` keeps it organized and optional.

**Result**: Stronger SDK + Powerful GUI = Best of both worlds!
