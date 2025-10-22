# Guide: Backtesting Stocks with Limited Trading History

## The Real Answer

**"2y with default parameters" is OPTIMAL, not REQUIRED.**

You **CAN** backtest stocks that have only been trading for 6 months to 1 year - you just need to adjust your parameters and understand the trade-offs.

---

## What Works with Limited Data

### 6 Months of Data (~126 days)

**✓ THIS WORKS:**

```python
results = comprehensive_cointegration_analysis(
    tickers=["NEW_IPO", "ESTABLISHED_STOCK"],
    period="6mo",
    window=30,                      # Small window (1 month)
    step_size=6,                    # ~1 week steps
    backtest_method="train_test_split"  # Simpler method
)
```

**What you get:**
- ✓ ~17 rolling cointegration windows
- ✓ 76 days training, 51 days testing
- ✓ Valid backtest results
- ⚠️ Less reliable than longer periods
- ⚠️ Warnings about small windows (normal)

**Validation output:**
```
[VALID] Configuration is valid

WARNINGS (review recommended):
  1. Rolling window (30) is below recommended 60+ days. Results may be noisy.

RECOMMENDATIONS:
  1. Data is adequate but consider 1y+ for walk-forward testing.
```

---

### 1 Year of Data (~252 days)

**✓ THIS WORKS (Walk-Forward Possible):**

```python
results = comprehensive_cointegration_analysis(
    tickers=["YEAR_OLD_STOCK", "ANOTHER_STOCK"],
    period="1y",
    window=63,                      # Medium window (3 months)
    step_size=10,                   # ~2 week steps
    backtest_method="walk_forward"  # Full methodology
)
```

**What you get:**
- ✓ Adaptive train window: ~84 days
- ✓ Adaptive test window: ~25 days
- ✓ ~16 walk-forward periods
- ✓ More robust than 6 months
- ⚠️ Still not as reliable as 2 years

---

## Complete Parameter Recommendations by Data Length

| Data Available | Period | Window | Step | Method | Train | Test | Reliability |
|----------------|--------|--------|------|--------|-------|------|-------------|
| ~40 days | 2mo | 30 | 5 | train_test_split | - | - | ⚠️ Minimal |
| ~63 days | 3mo | 30 | 5 | train_test_split | - | - | ⚠️ Limited |
| ~126 days | **6mo** | **30** | **6** | **train_test_split** | - | - | ⚠️ **Adequate** |
| ~252 days | **1y** | **63** | **10** | **walk_forward** | **90** | **30** | ✓ **Good** |
| ~504 days | **2y** | **252** | **21** | **walk_forward** | **252** | **63** | ✓ **Excellent** |
| 1000+ days | 5y+ | 252 | 21 | walk_forward | 252 | 63 | ✓ **Excellent** |

---

## Automatic Adaptation

The system **already adapts** for you! Look at the code in `cointegration_analysis.py:519-520`:

```python
train_window=min(252, len(data) // 3),  # Adapts to data size!
test_window=min(63, len(data) // 10),   # Adapts to data size!
```

**What this means:**
- If you have 126 days: train_window = 42 days (126/3)
- If you have 252 days: train_window = 84 days (252/3)
- If you have 504 days: train_window = 168 days (504/3)
- If you have 1000 days: train_window = 252 days (caps at 252)

**You don't need to calculate this manually!**

---

## Real-World Example: 6 Months

Let's say you want to test a stock that IPO'd 6 months ago:

### Step 1: Get suggested parameters

```python
from parameter_validator import suggest_parameters, print_suggested_parameters
from data_loader import get_close_price_data

# Download data
data = get_close_price_data(["NEW_IPO", "ESTABLISHED"], period="6mo")
print(f"Data available: {len(data)} days")

# Get suggestions
suggestions = suggest_parameters(len(data))
print_suggested_parameters(suggestions)
```

**Output:**
```
Data available: 127 days

Recommended configuration:
  method: train_test_split
  rolling_window: 30
  rolling_step: 6
  train_pct: 0.6
```

### Step 2: Run analysis with suggestions

```python
results = comprehensive_cointegration_analysis(
    tickers=["NEW_IPO", "ESTABLISHED"],
    period="6mo",
    window=30,
    step_size=6,
    backtest_method="train_test_split"
)
```

### Step 3: Interpret with caution

```python
if results is not None:
    # Check cointegration stability
    rolling = results['rolling_analysis']
    pct_coint = (rolling['p_value'] < 0.05).mean()

    # Check backtest
    metrics = results['backtest']['test_results']['metrics']

    print(f"Cointegrated {pct_coint*100:.1f}% of time")
    print(f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Total trades: {metrics['total_trades']}")

    # Be more conservative with limited data
    if pct_coint < 0.70:
        print("⚠️ Limited data + low cointegration % = HIGH RISK")
    if metrics['total_trades'] < 5:
        print("⚠️ Very few trades - results may not be representative")
```

---

## Trade-offs with Limited Data

### What You Lose

| Issue | With 6 Months | With 2 Years |
|-------|---------------|--------------|
| Rolling windows | ~17 windows | ~50 windows |
| Walk-forward periods | N/A (use train/test) | ~15 periods |
| Cointegration reliability | Lower | Higher |
| Parameter stability tracking | Limited | Comprehensive |
| Market regime coverage | Single regime | Multiple regimes |
| Statistical confidence | Moderate | High |

### What You Gain

- ✓ Can still analyze the pair
- ✓ Get preliminary results
- ✓ Identify obvious non-cointegrated pairs
- ✓ Start building trading intuition
- ✓ Better than no analysis at all

---

## Recommended Workflow for New Stocks

### Phase 1: Limited Data Analysis (6 months - 1 year)

```python
# Use suggested parameters
results = comprehensive_cointegration_analysis(
    tickers=["NEW_STOCK", "PARTNER"],
    period="6mo",  # or "1y" if available
    window=30,     # Small window
    step_size=6,
    backtest_method="train_test_split"
)

# Analyze conservatively
if results:
    rolling = results['rolling_analysis']
    metrics = results['backtest']['test_results']['metrics']

    # Higher bar for limited data
    if (rolling['p_value'] < 0.05).mean() > 0.80 and \
       metrics['sharpe_ratio'] > 1.5:
        print("✓ Strong signal despite limited data")
        print("→ Worth paper trading or small position")
    else:
        print("⚠️ Insufficient evidence with limited data")
        print("→ Wait for more history")
```

### Phase 2: Accumulate More Data

```python
# After 1-2 years of trading
results = comprehensive_cointegration_analysis(
    tickers=["NEW_STOCK", "PARTNER"],
    period="2y",
    window=126,    # Larger window
    step_size=21,
    backtest_method="walk_forward"  # Now viable
)

# Re-evaluate with more data
# Higher confidence in results
```

### Phase 3: Continuous Monitoring

```python
# Quarterly re-evaluation
# Check if relationship remains stable
# Adjust strategy as needed
```

---

## Example Configurations That Work

### Configuration 1: Conservative (6 months)

```python
results = comprehensive_cointegration_analysis(
    tickers=["A", "B"],
    period="6mo",
    window=30,
    step_size=10,
    backtest_method="train_test_split"
)
```

**Passes validation:** ✓
**Warnings:** Small window, limited data
**Use case:** Initial screening of new stocks

---

### Configuration 2: Moderate (1 year)

```python
results = comprehensive_cointegration_analysis(
    tickers=["A", "B"],
    period="1y",
    window=63,
    step_size=10,
    backtest_method="walk_forward"
)
```

**Passes validation:** ✓
**Warnings:** Below optimal, but workable
**Use case:** Preliminary strategy development

---

### Configuration 3: Aggressive (1 year, larger windows)

```python
results = comprehensive_cointegration_analysis(
    tickers=["A", "B"],
    period="1y",
    window=126,
    step_size=21,
    backtest_method="train_test_split"  # Can't do walk-forward
)
```

**Passes validation:** ✓
**Warnings:** Train/test split needed (walk-forward won't work)
**Use case:** Want larger rolling windows for stability

---

## When You CANNOT Backtest

The system will **reject** configurations that are mathematically impossible:

```python
# This FAILS - window > data
results = comprehensive_cointegration_analysis(
    tickers=["A", "B"],
    period="3mo",   # ~63 days
    window=252,     # > 63 days
    backtest_method="walk_forward"
)
```

**Output:**
```
[INVALID] Configuration is INVALID - cannot proceed

ERRORS (must fix):
  1. Rolling window (252) >= data length (63)

Returns: None
```

---

## Summary Table: What Works

| Your Situation | What to Do | Expected Results |
|----------------|------------|------------------|
| Stock IPO'd 2 months ago | ❌ Wait for more data | Too little for reliable analysis |
| Stock IPO'd 3-6 months ago | ⚠️ Use train_test_split with small windows | Preliminary analysis, low confidence |
| Stock IPO'd 1 year ago | ✓ Use walk_forward with medium windows | Good analysis, moderate confidence |
| Stock IPO'd 2+ years ago | ✓ Use walk_forward with standard windows | Excellent analysis, high confidence |

---

## Key Takeaways

1. **"2y is optimal" ≠ "2y is required"**
   - You CAN use 6 months to 1 year of data
   - Just use appropriate parameters

2. **The system adapts automatically**
   - Train/test windows scale with data length
   - Validation tells you what's wrong
   - Suggestions give you working configurations

3. **Understand the trade-offs**
   - Less data = less reliable
   - More data = higher confidence
   - Accept lower confidence with new stocks

4. **Use suggest_parameters()**
   - Automatically calculates optimal parameters
   - Adapts to your available data
   - Provides working configurations

5. **Be more conservative with limited data**
   - Require higher Sharpe ratios (1.5+ vs 1.0+)
   - Require higher cointegration % (80%+ vs 70%+)
   - Use smaller position sizes
   - Paper trade first

---

## Bottom Line

**You CAN backtest stocks with 6 months to 1 year of trading history.**

Just:
- Use `suggest_parameters()` to get appropriate settings
- Use smaller windows (30-63 days vs 252 days)
- Use train/test split for very limited data
- Accept more warnings (they're normal)
- Interpret results more conservatively
- Supplement with paper trading
