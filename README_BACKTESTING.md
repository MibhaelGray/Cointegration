# Pairs Trading Backtesting System

## Quick Start

### For Stocks with 2+ Years of History (Recommended)

```python
from cointegration_analysis import comprehensive_cointegration_analysis

results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="2y",                    # 2 years of data
    window=252,                     # 1 year rolling window
    step_size=21,                   # Monthly steps
    backtest_method="walk_forward"  # Most robust
)
```

### For Stocks with 6 Months - 1 Year History

```python
from parameter_validator import suggest_parameters
from data_loader import get_close_price_data
from cointegration_analysis import comprehensive_cointegration_analysis

# Get data and suggestions
data = get_close_price_data(["NEW_STOCK", "STOCK_B"], period="1y")
suggestions = suggest_parameters(len(data), "walk_forward")

# Run analysis with adapted parameters
results = comprehensive_cointegration_analysis(
    tickers=["NEW_STOCK", "STOCK_B"],
    period="1y",
    window=suggestions['rolling_window'],      # Adapts to data
    step_size=suggestions['rolling_step'],     # Adapts to data
    backtest_method=suggestions['method']      # Picks appropriate method
)
```

---

## System Features

### ✓ Fixed Critical Issues
1. **Eliminated look-ahead bias** - Now uses rolling z-scores
2. **Parameter validation** - Prevents invalid configurations
3. **Automatic adaptation** - Windows scale to data length

### ✓ Three Backtesting Methods
1. **Walk-Forward** - Gold standard (needs 1y+ data)
2. **Train/Test Split** - Simpler (works with 6mo+ data)
3. **Simple** - Basic (for comparison only)

### ✓ Comprehensive Analysis
- Cointegration testing (Engle-Granger for pairs, Johansen for baskets)
- Rolling stability analysis
- Spread analysis
- Parameter stability tracking
- Performance metrics

---

## Will It Work with My Data?

### Quick Reference Table

| Data Length | Period | Works? | Method | Notes |
|-------------|--------|--------|--------|-------|
| < 60 days | 1-2mo | ❌ | - | Too little data |
| 60-126 days | 3-6mo | ⚠️ | train_test_split | Limited reliability |
| 127-250 days | 6mo-1y | ✓ | train_test_split or walk_forward | Good |
| 251-500 days | 1-2y | ✓ | walk_forward | Very good |
| 500+ days | 2y+ | ✓ | walk_forward | Excellent |

### The System Will Tell You

```python
results = comprehensive_cointegration_analysis(...)

# If parameters are invalid:
# Output: [INVALID] Configuration is INVALID
# Returns: None

# If parameters work but are suboptimal:
# Output: [VALID] with WARNINGS
# Returns: Results (with caution)

# If parameters are good:
# Output: [VALID] No issues detected
# Returns: Results (high confidence)
```

---

## Parameter Constraints

### What Must Be True

```
✓ Rolling window < Data length
✓ Z-score window < Data length
✓ Train window + Test window < Data length (walk-forward)
✓ At least 5 rolling windows for stability analysis
✓ At least 30 days for cointegration tests
```

### What's Recommended

```
✓ Rolling window: 60-252 days
✓ Z-score window: 20 days
✓ Train window: 2-4× test window
✓ 10+ walk-forward periods
✓ 2+ years of data
```

---

## Example Workflows

### Workflow 1: Established Stocks (Standard)

```python
# Step 1: Run comprehensive analysis
results = comprehensive_cointegration_analysis(
    tickers=["AAPL", "MSFT"],
    period="2y",
    window=252,
    step_size=21,
    backtest_method="walk_forward"
)

# Step 2: Check if tradeable
rolling = results['rolling_analysis']
pct_coint = (rolling['p_value'] < 0.05).mean()

metrics = results['backtest']['metrics']
ps = metrics['parameter_stability']

print(f"Cointegrated: {pct_coint*100:.1f}% of time")
print(f"Hedge ratio CV: {ps['hedge_ratio_cv']*100:.1f}%")
print(f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}")

# Decision criteria
if pct_coint > 0.70 and ps['hedge_ratio_cv'] < 0.20 and metrics['sharpe_ratio'] > 1.0:
    print("✓ Good candidate for trading")
else:
    print("❌ Not suitable for trading")
```

### Workflow 2: New Stocks (Adapted)

```python
from parameter_validator import suggest_parameters
from data_loader import get_close_price_data

# Step 1: Download available data
data = get_close_price_data(["NEW_IPO", "ESTABLISHED"], period="6mo")
print(f"Available: {len(data)} days")

# Step 2: Get suggestions
suggestions = suggest_parameters(len(data))

# Step 3: Run analysis
results = comprehensive_cointegration_analysis(
    tickers=["NEW_IPO", "ESTABLISHED"],
    period="6mo",
    window=suggestions['rolling_window'],
    step_size=suggestions['rolling_step'],
    backtest_method=suggestions['method']
)

# Step 4: Be more conservative
if results:
    metrics = results['backtest']['test_results']['metrics']

    # Higher bar for limited data
    if metrics['sharpe_ratio'] > 1.5:
        print("✓ Strong signal - consider paper trading")
    else:
        print("⚠️ Wait for more data")
```

### Workflow 3: Parameter Validation Only

```python
from parameter_validator import (
    validate_backtest_parameters,
    print_validation_results,
    suggest_parameters,
    print_suggested_parameters
)

# Validate before running
validation = validate_backtest_parameters(
    period="6mo",
    data_length=126,
    window=252,
    step_size=21,
    backtest_method="walk_forward"
)

print_validation_results(validation)

if not validation['valid']:
    # Get suggestions
    suggestions = suggest_parameters(126, "walk_forward")
    print_suggested_parameters(suggestions)
```

---

## Files and Documentation

### Core Files
- **backtesting.py** - Main backtesting functions
- **cointegration_analysis.py** - Comprehensive analysis wrapper
- **parameter_validator.py** - Parameter validation and suggestions
- **rolling_analysis.py** - Rolling cointegration analysis

### Test Files
- **test_walkforward.py** - Test walk-forward vs train/test split
- **test_limited_data.py** - Test with limited trading history
- **test_enhanced.py** - Full feature test

### Documentation
- **BACKTEST_IMPROVEMENTS.md** - Complete list of fixes and features
- **PARAMETER_GUIDE.md** - Detailed constraints and validation
- **LIMITED_DATA_GUIDE.md** - Guide for stocks with short history
- **QUICK_REFERENCE.md** - Quick lookup reference
- **README_BACKTESTING.md** - This file

---

## Common Questions

### Q: Can I use any parameters I want?

**A:** No - there are mathematical constraints. But the system validates automatically and tells you what's wrong.

### Q: What if my stock only has 6 months of history?

**A:** That works! Use `suggest_parameters()` to get appropriate settings. Use train/test split method and smaller windows.

### Q: Why does my 2-year backtest show different results than before?

**A:** The old code had look-ahead bias. New results are more realistic (and likely less optimistic).

### Q: How do I know if my parameters are good?

**A:** Run the analysis - validation happens automatically. Green = good, warnings = suboptimal but OK, errors = won't work.

### Q: What's the minimum data I need?

**A:** Absolute minimum is ~60 days for train/test split. Recommended is 250+ days (1 year) for walk-forward.

---

## Decision Tree

```
Do you have 2+ years of data?
│
├─ YES → Use period="2y", window=252, step_size=21, backtest_method="walk_forward"
│         Result: Excellent reliability ✓
│
└─ NO → How much data do you have?
    │
    ├─ 1 year → Use period="1y", window=63, step_size=10, backtest_method="walk_forward"
    │           Result: Good reliability ✓
    │
    ├─ 6 months → Use period="6mo", window=30, step_size=6, backtest_method="train_test_split"
    │             Result: Adequate, interpret conservatively ⚠️
    │
    └─ < 6 months → Use suggest_parameters() or wait for more data
                    Result: Limited reliability ⚠️
```

---

## Performance Expectations

### With 2+ Years of Data (Walk-Forward)
- ✓ 10-50 walk-forward periods
- ✓ 10-50 rolling windows
- ✓ High confidence parameter stability metrics
- ✓ Captures multiple market regimes
- ✓ Results you can trust

### With 1 Year of Data (Walk-Forward)
- ✓ 5-15 walk-forward periods
- ✓ 9-20 rolling windows
- ⚠️ Moderate confidence
- ⚠️ Single market regime
- ⚠️ Use conservative position sizing

### With 6 Months of Data (Train/Test Split)
- ⚠️ Single train/test split
- ⚠️ 10-20 rolling windows
- ⚠️ Lower confidence
- ⚠️ Very limited regime coverage
- ⚠️ Paper trade first, small positions

---

## Final Recommendations

### For Best Results
1. **Use 2+ years of data when possible**
2. **Trust the automatic validation**
3. **Use `suggest_parameters()` for new stocks**
4. **Check cointegration %, hedge ratio CV, and Sharpe**
5. **Be more conservative with limited data**

### Red Flags
- ❌ Cointegrated < 50% of time
- ❌ Hedge ratio CV > 30%
- ❌ Sharpe ratio < 0.5
- ❌ Very few trades (< 5)
- ❌ Large drawdowns (> 20%)

### Green Flags
- ✓ Cointegrated > 70% of time
- ✓ Hedge ratio CV < 20%
- ✓ Sharpe ratio > 1.0
- ✓ Win rate > 55%
- ✓ Consistent performance across periods

---

## Getting Help

### Run Validation Test
```bash
cd data
python parameter_validator.py
```

### Test with Limited Data
```bash
cd data
python test_limited_data.py
```

### Test Walk-Forward
```bash
cd data
python test_walkforward.py
```

---

## Summary

**The system is flexible and adapts to your data:**
- ✓ Works with 6 months to 10+ years of data
- ✓ Automatically validates parameters
- ✓ Suggests optimal configurations
- ✓ Prevents invalid setups
- ✓ Provides clear warnings and errors
- ✓ Adapts windows to data length

**You just need to:**
1. Choose an appropriate time period for your stocks
2. Use `suggest_parameters()` if unsure
3. Run the analysis
4. Trust the validation system
5. Interpret results appropriately for data length
