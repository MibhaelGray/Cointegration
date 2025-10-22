# Cointegration Analysis Project

A comprehensive Python toolkit for analyzing cointegration relationships in stock baskets using Johansen and Engle-Granger tests.

## Project Structure

```
.
├── config.py                    # Stock basket definitions
├── data_loader.py              # Data download and loading utilities
├── cointegration_analysis.py   # Cointegration testing functions
├── rolling_analysis.py         # Rolling window analysis
├── visualization.py            # Plotting and visualization
├── main.py                     # Example usage and main script
└── README.md                   # This file
```

## Modules

### 1. `config.py`
Defines 15 stock baskets organized by sector:
- Cloud Infrastructure
- Cloud Security
- Enterprise SaaS
- Ad Tech
- Semiconductors
- And more...

### 2. `data_loader.py`
Functions for downloading and loading stock price data:
- `get_close_price_data()` - Download data from Yahoo Finance
- `download_all_baskets()` - Batch download multiple baskets
- `load_all_csv()` - Load saved CSV files
- `load_basket_csv()` - Load specific basket

### 3. `cointegration_analysis.py`
Cointegration testing utilities:
- `test_basket_cointegration()` - Test multiple baskets (Johansen)
- `analyze_basket()` - Detailed analysis of one basket
- `test_pair_cointegration()` - Test pairs (Engle-Granger)
- `get_hedge_ratio()` - Calculate beta for pairs
- `find_cointegrated_pairs()` - Find all pairs in a basket

### 4. `rolling_analysis.py`
Time-varying cointegration analysis:
- `rolling_cointegration_analysis()` - Rolling window tests
- `batch_rolling_analysis()` - Analyze multiple baskets
- `calculate_spread()` - Calculate price spread
- `calculate_zscore()` - Z-score for mean reversion
- `analyze_spread_stability()` - Spread stability metrics

### 5. `visualization.py`
Plotting functions:
- `plot_price_series()` - Plot stock prices
- `plot_rolling_results()` - Plot rolling analysis
- `plot_spread()` - Plot price spread
- `plot_zscore()` - Plot z-score with thresholds
- `plot_spread_analysis()` - Comprehensive pair analysis
- `plot_cointegration_heatmap()` - Heatmap of results

### 6. `main.py`
Example scripts demonstrating all functionality:
- Download data
- Test cointegration
- Analyze pairs and baskets
- Rolling analysis
- Visualization

## Quick Start

### 1. Download Data
```python
from config import ALL_BASKETS
from data_loader import download_all_baskets

# Download all baskets (1 year of data)
all_data = download_all_baskets(ALL_BASKETS, period="1y")
```

### 2. Test Cointegration
```python
from data_loader import load_all_csv
from cointegration_analysis import test_basket_cointegration

# Load saved data
all_data = load_all_csv()

# Test all baskets
summary = test_basket_cointegration(all_data, k_ar_diff=5, crit_level=1)
print(summary)
```

### 3. Analyze a Pair
```python
from data_loader import get_close_price_data
from cointegration_analysis import test_pair_cointegration, get_hedge_ratio
from visualization import plot_spread_analysis

# Download pair data
data = get_close_price_data(["NET", "SNOW"], period="1y")

# Test cointegration
score, p_value, _ = test_pair_cointegration(data)

# Get hedge ratio
beta, alpha = get_hedge_ratio(data)

# Visualize
plot_spread_analysis(data, hedge_ratio=beta)
```

### 4. Rolling Analysis
```python
from data_loader import get_close_price_data
from rolling_analysis import rolling_cointegration_analysis
from visualization import plot_rolling_results

# Download data
data = get_close_price_data(["NET", "SNOW"], period="2y")

# Run rolling analysis
results = rolling_cointegration_analysis(data, window=180, step_size=21)

# Plot results
plot_rolling_results(results, ["NET", "SNOW"], window=180, step_size=21)
```

## Installation

### Required packages:
```bash
pip install yfinance pandas numpy matplotlib statsmodels
```

## Usage Examples

### Example 1: Find Cointegrated Pairs in a Basket
```python
from config import basket_1
from data_loader import load_all_csv
from cointegration_analysis import find_cointegrated_pairs

all_data = load_all_csv()
pairs = find_cointegrated_pairs(basket_1, all_data, p_threshold=0.05)
print(pairs)
```

### Example 2: Batch Rolling Analysis
```python
from data_loader import load_all_csv
from rolling_analysis import batch_rolling_analysis

all_data = load_all_csv()
results = batch_rolling_analysis(all_data, window=252, step_size=21)
```

### Example 3: Spread Trading Setup
```python
from data_loader import get_close_price_data
from rolling_analysis import calculate_spread, calculate_zscore
from visualization import plot_zscore

# Get data
data = get_close_price_data(["NET", "SNOW"], period="1y")

# Calculate spread and z-score
spread = calculate_spread(data, hedge_ratio=None)  # Auto-calculate beta
zscore = calculate_zscore(spread, window=20)

# Plot with trading thresholds
plot_zscore(zscore, title="NET vs SNOW - Trading Signal")
```

## Key Features

1. **Flexible Data Loading**: Download from Yahoo Finance or load saved CSVs
2. **Multiple Test Methods**: Johansen (baskets) and Engle-Granger (pairs)
3. **Rolling Analysis**: Time-varying cointegration detection
4. **Spread Trading**: Calculate spreads, hedge ratios, and z-scores
5. **Comprehensive Visualization**: Multiple plot types for analysis
6. **Batch Processing**: Analyze multiple baskets efficiently
7. **Clean Code**: Modular design with clear separation of concerns

## Parameters Guide

### Cointegration Tests
- `k_ar_diff`: Lag order (default 5) - higher for longer-term relationships
- `crit_level`: 0=90%, 1=95%, 2=99% confidence

### Rolling Analysis
- `window`: Window size in days (252 = 1 year, 126 = 6 months)
- `step_size`: Days between windows (21 = ~1 month, 1 = daily)

### Data Download
- `period`: "1y", "2y", "6mo", etc.
- `max_missing`: Maximum missing values allowed per stock
- `log_prices`: Use log prices (recommended for cointegration)

## Running the Main Script

```bash
python main.py
```

Edit `main.py` to uncomment the examples you want to run.

## Notes

- All prices are log-transformed by default (required for cointegration)
- CSV files are automatically saved with ticker names
- Delisted stocks are automatically filtered out
- Warnings are suppressed for cleaner output

## License

This project is for educational and research purposes.
