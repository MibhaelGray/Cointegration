# Quick Reference: Parameter Selection

## TL;DR

**Will it work with any parameters?**
- ❌ **NO** - but the system will tell you if your parameters are invalid
- ✓ **YES** - if you follow the recommended ranges

## Recommended Configurations by Data Period

### 2+ Years (500+ days) - ✓ BEST

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="2y",                    # or "5y", "10y"
    window=252,                     # 1 year
    step_size=21,                   # ~1 month
    backtest_method="walk_forward"  # Most robust
)
```

**Validation:** ✓ Passes with no warnings

---

### 1 Year (250 days) - ⚠️ OK

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="1y",
    window=126,                     # 6 months
    step_size=21,
    backtest_method="walk_forward"
)
```

**Validation:** ⚠️ May show warnings but will proceed

---

### 6 Months (126 days) - ⚠️ MARGINAL

```python
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="6mo",
    window=63,                      # 3 months
    step_size=10,
    backtest_method="train_test_split"  # Simpler method
)
```

**Validation:** ⚠️ Multiple warnings, limited reliability

---

### Less than 6 Months - ❌ NOT RECOMMENDED

```python
# This will FAIL validation:
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="3mo",
    window=252,
    backtest_method="walk_forward"
)
# Returns: None (with error message)
```

**Validation:** ❌ Returns `None` - cannot proceed

---

## Parameter Constraints

| Parameter | Minimum | Recommended | Maximum | Notes |
|-----------|---------|-------------|---------|-------|
| **period** | "2mo" (~40 days) | "2y" | "10y" | More is better |
| **window** | 30 days | 126-252 days | < data length | For rolling cointegration |
| **step_size** | 1 day | 21 days | < window | Smaller = more windows |
| **zscore_window** | 10 days | 20 days | 60 days | For backtest z-scores |

---

## What Happens with Invalid Parameters

### Automatic Validation
The system automatically validates your parameters when you call `comprehensive_cointegration_analysis()`.

**If VALID:**
```
[VALID] Configuration is valid
[OK] No issues detected - configuration looks good!

[Continues with analysis...]
```

**If INVALID:**
```
[INVALID] Configuration is INVALID - cannot proceed

ERRORS (must fix):
  1. Rolling window (252) >= data length (66)

[ERROR] Invalid parameter configuration - cannot proceed with analysis
```
**Returns:** `None`

---

## Get Suggested Parameters

```python
from parameter_validator import suggest_parameters, print_suggested_parameters
from data_loader import get_close_price_data

# Download data first
data = get_close_price_data(["AAPL", "MSFT"], period="1y")

# Get suggestions
suggestions = suggest_parameters(len(data), "walk_forward")
print_suggested_parameters(suggestions)

# Use suggestions
results = comprehensive_cointegration_analysis(
    tickers=["AAPL", "MSFT"],
    period="1y",
    window=suggestions['rolling_window'],
    step_size=suggestions['rolling_step'],
    backtest_method=suggestions['method']
)
```

---

## Common Errors and Quick Fixes

### Error: "Rolling window >= data length"

**Problem:** Asking for 252-day window with only 100 days of data

**Fix:**
```python
# Option 1: Get more data
period="2y"  # instead of "6mo"

# Option 2: Use smaller window
window=63  # instead of 252
```

---

### Error: "Cannot create any walk-forward periods"

**Problem:** Train + test windows exceed data length

**Fix:**
```python
# Option 1: Get more data
period="2y"

# Option 2: Use simpler method
backtest_method="train_test_split"
```

---

### Warning: "Only X rolling windows"

**Problem:** Not enough windows for stability analysis

**Fix:**
```python
# Option 1: More data
period="2y"

# Option 2: Smaller step size
step_size=10  # instead of 21

# Option 3: Smaller window
window=126  # instead of 252
```

---

## When in Doubt

**Use these "safe" parameters:**

```python
results = comprehensive_cointegration_analysis(
    tickers=["YOUR", "STOCKS"],
    period="2y",                    # 👈 Safe choice
    window=126,                     # 👈 6 months (safe middle ground)
    step_size=21,                   # 👈 Monthly (standard)
    backtest_method="walk_forward", # 👈 Most robust
    use_llm=True,
    save_plots=True
)
```

**This configuration:**
- ✓ Works with 2 years of data
- ✓ Gives ~20 rolling windows
- ✓ Gives ~15 walk-forward periods
- ✓ Passes validation
- ✓ Provides reliable results

---

## Check if Pair is Tradeable

After running analysis, check these key metrics:

```python
# 1. Cointegration percentage
rolling = results['rolling_analysis']
pct_coint = (rolling['p_value'] < 0.05).mean()

if pct_coint < 0.50:
    print("❌ Cointegrated < 50% of time - NOT suitable")
elif pct_coint < 0.70:
    print("⚠️ Cointegrated 50-70% of time - Risky")
else:
    print("✓ Cointegrated > 70% of time - Good")

# 2. Parameter stability
if 'parameter_stability' in results['backtest']['metrics']:
    ps = results['backtest']['metrics']['parameter_stability']
    cv = ps['hedge_ratio_cv']

    if cv > 0.30:
        print("❌ Hedge ratio CV > 30% - Unstable")
    elif cv > 0.20:
        print("⚠️ Hedge ratio CV 20-30% - Moderate")
    else:
        print("✓ Hedge ratio CV < 20% - Stable")

# 3. Backtest performance
metrics = results['backtest']['metrics']
sharpe = metrics['sharpe_ratio']

if sharpe < 0.5:
    print("❌ Sharpe < 0.5 - Poor performance")
elif sharpe < 1.0:
    print("⚠️ Sharpe 0.5-1.0 - Moderate")
else:
    print("✓ Sharpe > 1.0 - Good performance")
```

---

## Summary

✓ **Use 2+ years of data when possible**
✓ **Trust the defaults (they're optimized)**
✓ **System will validate and warn you**
✓ **Check cointegration %, CV, and Sharpe before trading**
❌ **Don't use < 6 months of data**
❌ **Don't ignore validation warnings**
