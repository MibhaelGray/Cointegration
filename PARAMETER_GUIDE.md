# Parameter Selection Guide for Backtesting

## Quick Answer

**No, the rolling backtests will NOT work with arbitrary parameters.** There are important constraints based on data availability and statistical requirements.

## Constraints Summary

### Minimum Data Requirements

| Backtest Method | Minimum Data | Recommended Data | Notes |
|----------------|--------------|------------------|-------|
| Walk-Forward | 150 days | 500+ days (2 years) | Needs train + test windows × multiple periods |
| Train/Test Split | 60 days | 250+ days (1 year) | Needs enough for 60/40 split |
| Simple | 40 days | 250+ days (1 year) | Needs 5-10× z-score window |

### Parameter Relationships

```
Data Length
    ├── Must be > Rolling Window (for cointegration analysis)
    ├── Must be > Train Window + Test Window (for walk-forward)
    └── Must be > Z-score Window × 5 (minimum for simple backtest)

Walk-Forward:
    Train Window + Test Window <= Data Length
    Train Window should be 2-4× Test Window
    Step Size typically < Train Window (for overlapping windows)

Rolling Analysis:
    Window Size: 30-252 days (60+ recommended)
    Step Size: Usually 5-21 days
    Number of Windows = (Data Length - Window) / Step Size
    Need 5+ windows for reliable stability analysis
```

## Detailed Constraints

### 1. Z-score Window (default: 20 days)

**Purpose:** Calculate rolling mean/std for spread normalization

**Constraints:**
- Minimum: 10 days
- Maximum: 60 days (becomes too slow to react)
- Recommended: 20 days
- Must be < Data Length

**Impact of changing:**
- Smaller (10-15): More reactive, more false signals
- Larger (30-60): More stable, slower to detect opportunities

### 2. Rolling Cointegration Window

**Purpose:** Test if cointegration relationship is stable over time

**Constraints:**
- Minimum: 30 days (statistical requirement)
- Recommended: 60-252 days
- Must be < Data Length
- For pairs: 60+ days recommended
- For baskets: 180+ days recommended

**Impact of changing:**
- Too small (<30): Unreliable cointegration tests
- Too large (>252): Misses regime changes
- Must have at least 5 windows for stability analysis

### 3. Walk-Forward Parameters

#### Train Window

**Constraints:**
- Minimum: max(60, zscore_window × 3)
- Recommended: 180-252 days
- Must be 2-4× test window
- Must be < Data Length - Test Window

**Impact:**
- Too small: Parameter estimates unreliable
- Too large: Less adaptable to regime changes

#### Test Window

**Constraints:**
- Minimum: max(20, zscore_window)
- Recommended: 40-63 days
- Must be < Data Length - Train Window

**Impact:**
- Too small: Not enough trades to evaluate
- Too large: Fewer walk-forward periods

#### Step Size

**Constraints:**
- Minimum: 1 day
- Recommended: 10-21 days (2-4 weeks)
- Typically < Train Window

**Impact:**
- Smaller: More periods, more overlap, slower to run
- Larger: Fewer periods, less overlap, less robust

## Recommended Configurations

### Scenario 1: Short-Term (6 months = ~126 days)

```python
# NOT RECOMMENDED for walk-forward, but possible:
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="6mo",
    window=30,              # Small rolling window
    step_size=10,           # Small step
    backtest_method="train_test_split"  # Use simpler method
)
```

**Expected Issues:**
- Only 3-4 rolling windows
- Limited backtest periods
- Less reliable parameter estimates

**Validation will show warnings but may proceed**

### Scenario 2: Medium-Term (1 year = ~252 days)

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="1y",
    window=63,              # 3 months rolling
    step_size=21,           # Monthly steps
    backtest_method="walk_forward"
)

# This will use:
# - train_window: 84 (252 // 3 = ~84)
# - test_window: 25 (252 // 10 = ~25)
# - Approximately 5-6 walk-forward periods
```

**Expected:**
- Adequate for initial analysis
- Moderate number of rolling windows (9)
- Some walk-forward periods (5-6)

**Validation will show warnings but proceed**

### Scenario 3: Long-Term (2+ years = 500+ days) ✓ RECOMMENDED

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="2y",
    window=252,             # 1 year rolling window
    step_size=21,           # Monthly steps
    backtest_method="walk_forward"
)

# This will use:
# - train_window: 252 (1 year)
# - test_window: 50 (63 capped to ~50)
# - Approximately 10+ walk-forward periods
```

**Expected:**
- Robust statistical tests
- Many rolling windows (12+)
- Many walk-forward periods (10+)
- High confidence results

**Validation will pass with no warnings**

### Scenario 4: Very Long-Term (5+ years)

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="5y",
    window=252,             # Standard 1 year
    step_size=21,           # Standard monthly
    backtest_method="walk_forward"
)

# This will use:
# - train_window: 252
# - test_window: 63
# - Approximately 50+ walk-forward periods
```

**Expected:**
- Very robust
- Captures multiple market regimes
- May include relationships that broke down (check rolling analysis!)

## What Happens with Invalid Parameters

The system has **built-in safeguards** but they have limits:

### Current Safeguards (cointegration_analysis.py:519-520)

```python
train_window=min(252, len(data) // 3),  # Adapts to data size
test_window=min(63, len(data) // 10),   # Adapts to data size
```

### What Gets Validated

1. **Data length vs. windows** - Will ERROR if windows > data
2. **Number of periods** - Will WARN if < 5 periods
3. **Parameter ratios** - Will WARN if train/test ratio is off
4. **Statistical requirements** - Will WARN if windows too small

### Example: Too Little Data

```python
# This will FAIL validation:
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="1mo",          # Only ~21 days
    window=252,            # Want 252-day window
    backtest_method="walk_forward"
)
```

**Output:**
```
[INVALID] Configuration is INVALID - cannot proceed

ERRORS (must fix):
  1. Rolling window (252) >= data length (21)
  2. Train window (252) + test window (63) = 315 exceeds data length (21)
  3. Cannot create any walk-forward periods.

[ERROR] Invalid parameter configuration - cannot proceed with analysis
```

**Function returns `None`** - analysis stops.

## How to Use the Validator

### Option 1: Let it run automatically

```python
# Validator runs automatically in comprehensive_cointegration_analysis
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="1y",
    window=252,
    step_size=21,
    backtest_method="walk_forward"
)

# If invalid, function returns None
if results is None:
    print("Configuration was invalid!")
```

### Option 2: Validate manually before running

```python
from parameter_validator import (
    validate_backtest_parameters,
    print_validation_results,
    suggest_parameters,
    print_suggested_parameters
)
from data_loader import get_close_price_data

# Download data first
data = get_close_price_data(["AAPL", "MSFT"], period="6mo")

# Validate your parameters
validation = validate_backtest_parameters(
    period="6mo",
    data_length=len(data),
    window=252,
    step_size=21,
    backtest_method="walk_forward"
)

print_validation_results(validation)

if not validation['valid']:
    # Get suggestions
    suggestions = suggest_parameters(len(data), "walk_forward")
    print_suggested_parameters(suggestions)
```

### Option 3: Get suggestions for your data

```python
from parameter_validator import suggest_parameters, print_suggested_parameters
from data_loader import get_close_price_data

# Download data
data = get_close_price_data(["AAPL", "MSFT"], period="1y")

# Get optimal parameters for this data
suggestions = suggest_parameters(len(data), "walk_forward")
print_suggested_parameters(suggestions)

# Use suggested parameters
results = comprehensive_cointegration_analysis(
    tickers=["AAPL", "MSFT"],
    period="1y",
    window=suggestions['rolling_window'],
    step_size=suggestions['rolling_step'],
    backtest_method=suggestions['method']
)
```

## Common Issues and Solutions

### Issue 1: "Only X rolling windows"

**Problem:** Not enough windows for reliable stability analysis

**Solutions:**
1. Increase data period (`period="2y"` instead of `"6mo"`)
2. Decrease rolling window (`window=126` instead of `252`)
3. Decrease step size (`step_size=10` instead of `21`)

### Issue 2: "Cannot create any walk-forward periods"

**Problem:** Train + test windows exceed data length

**Solutions:**
1. Increase data period
2. Use train/test split instead: `backtest_method="train_test_split"`
3. Let adaptive windows work (they're in the code already)

### Issue 3: "Train window should be 2-4x test window"

**Problem:** Unbalanced train/test ratio

**Solutions:**
1. Usually a warning, not critical
2. Adjust test_window explicitly if needed
3. Trust the defaults (they follow this rule)

### Issue 4: "Hedge ratio CV > 20%"

**Problem:** Relationship is unstable over time

**Solutions:**
1. This is a DATA problem, not a parameter problem
2. The pair may not be suitable for trading
3. Try longer rolling windows to smooth out noise
4. Consider finding a different pair

## Decision Tree

```
How much data do you have?
│
├─ < 100 days
│   └─> Use train_test_split, small windows (30-60)
│       Expect warnings, limited reliability
│
├─ 100-200 days (6mo-1yr)
│   └─> Can use walk_forward with adaptive windows
│       Use window=63-126, step_size=10-21
│       Moderate reliability
│
├─ 200-500 days (1-2yr)
│   └─> Walk_forward works well
│       Use window=126-252, step_size=21
│       Good reliability
│
└─ 500+ days (2yr+)
    └─> Walk_forward optimal
        Use window=252, step_size=21
        High reliability
```

## Summary

**Will it work with any parameters?**
- ❌ No - there are mathematical and statistical constraints
- ✓ Yes - the code has adaptive safeguards
- ⚠️ Validation will warn/error if parameters are problematic

**Best practice:**
1. Use `period="2y"` or longer when possible
2. Trust the default adaptive windows
3. Pay attention to validation warnings
4. Use `suggest_parameters()` if unsure
5. More data = more reliable results

**The validator will:**
- ✓ Prevent catastrophic failures (errors)
- ⚠️ Warn about suboptimal configurations
- 💡 Suggest better parameters
- 🚫 Stop execution if invalid
