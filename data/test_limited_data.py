"""
Test backtesting with limited data scenarios.

This demonstrates what parameters work for stocks with short trading histories.
"""

import warnings
warnings.filterwarnings('ignore')

from cointegration_analysis import comprehensive_cointegration_analysis
from parameter_validator import (
    validate_backtest_parameters,
    print_validation_results,
    suggest_parameters,
    print_suggested_parameters
)
from data_loader import get_close_price_data


def test_6_months_data():
    """Test with ~6 months of data (IPO'd 6 months ago)."""
    print("=" * 70)
    print("SCENARIO 1: STOCKS WITH ~6 MONTHS TRADING HISTORY")
    print("=" * 70)

    # Simulate getting 6 months of data
    tickers = ["AAPL", "MSFT"]
    data = get_close_price_data(tickers, period="6mo")

    print(f"\nData available: {len(data)} days")

    # Get suggestions for this amount of data
    suggestions = suggest_parameters(len(data), "walk_forward")
    print_suggested_parameters(suggestions)

    # Try the suggested parameters
    print("\n" + "=" * 70)
    print("RUNNING ANALYSIS WITH SUGGESTED PARAMETERS")
    print("=" * 70)

    results = comprehensive_cointegration_analysis(
        tickers=tickers,
        period="6mo",
        window=suggestions['rolling_window'],
        step_size=suggestions['rolling_step'],
        backtest_method=suggestions['method'],
        use_llm=False,
        save_plots=False
    )

    if results is not None:
        print("\n✓ Analysis completed successfully!")
        print(f"  Backtest method used: {results.get('backtest_method', 'N/A')}")

        if results['backtest']:
            metrics = results['backtest']['metrics'] if 'metrics' in results['backtest'] \
                     else results['backtest']['test_results']['metrics']
            print(f"  Total return: {metrics['total_return_pct']:.2f}%")
            print(f"  Sharpe ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Total trades: {metrics['total_trades']}")
    else:
        print("\n✗ Analysis failed - parameters invalid")

    return results


def test_1_year_data():
    """Test with ~1 year of data."""
    print("\n\n" + "=" * 70)
    print("SCENARIO 2: STOCKS WITH ~1 YEAR TRADING HISTORY")
    print("=" * 70)

    tickers = ["AAPL", "MSFT"]
    data = get_close_price_data(tickers, period="1y")

    print(f"\nData available: {len(data)} days")

    # Get suggestions
    suggestions = suggest_parameters(len(data), "walk_forward")
    print_suggested_parameters(suggestions)

    # Run analysis
    print("\n" + "=" * 70)
    print("RUNNING ANALYSIS WITH SUGGESTED PARAMETERS")
    print("=" * 70)

    results = comprehensive_cointegration_analysis(
        tickers=tickers,
        period="1y",
        window=suggestions['rolling_window'],
        step_size=suggestions['rolling_step'],
        backtest_method=suggestions['method'],
        use_llm=False,
        save_plots=False
    )

    if results is not None:
        print("\n✓ Analysis completed successfully!")
        print(f"  Backtest method used: {results.get('backtest_method', 'N/A')}")

        if results['backtest']:
            metrics = results['backtest']['metrics'] if 'metrics' in results['backtest'] \
                     else results['backtest']['test_results']['metrics']
            print(f"  Total return: {metrics['total_return_pct']:.2f}%")
            print(f"  Sharpe ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Total trades: {metrics['total_trades']}")
    else:
        print("\n✗ Analysis failed - parameters invalid")

    return results


def test_manual_adjustment():
    """Test manually adjusting parameters for limited data."""
    print("\n\n" + "=" * 70)
    print("SCENARIO 3: MANUAL PARAMETER ADJUSTMENT (6 MONTHS)")
    print("=" * 70)

    tickers = ["AAPL", "MSFT"]
    data = get_close_price_data(tickers, period="6mo")

    print(f"\nData available: {len(data)} days")
    print("\nTrying different parameter combinations:")

    # Test configuration 1: Small windows, train/test split
    print("\n--- Configuration 1: Small windows + train/test split ---")
    validation1 = validate_backtest_parameters(
        period="6mo",
        data_length=len(data),
        window=30,               # Small rolling window
        step_size=10,            # Small step
        backtest_method="train_test_split",
        zscore_window=20
    )
    print_validation_results(validation1)

    if validation1['valid']:
        print("\n✓ This configuration WORKS for 6 months of data!")

    # Test configuration 2: Medium windows, train/test split
    print("\n--- Configuration 2: Medium windows + train/test split ---")
    validation2 = validate_backtest_parameters(
        period="6mo",
        data_length=len(data),
        window=63,               # 3 month rolling window
        step_size=10,
        backtest_method="train_test_split",
        zscore_window=20
    )
    print_validation_results(validation2)

    if validation2['valid']:
        print("\n✓ This configuration WORKS for 6 months of data!")

    # Test configuration 3: Try walk-forward with adjusted windows
    print("\n--- Configuration 3: Walk-forward with adaptive windows ---")

    # The system uses adaptive windows: min(252, len(data)//3)
    train_window = min(252, len(data) // 3)
    test_window = min(63, len(data) // 10)

    print(f"Adaptive train window: {train_window}")
    print(f"Adaptive test window: {test_window}")

    validation3 = validate_backtest_parameters(
        period="6mo",
        data_length=len(data),
        window=63,
        step_size=10,
        backtest_method="walk_forward",
        train_window=train_window,
        test_window=test_window,
        zscore_window=20
    )
    print_validation_results(validation3)

    if validation3['valid']:
        print("\n✓ Walk-forward CAN work with 6 months if windows are adapted!")


def show_parameter_ranges():
    """Show what parameter ranges work for different data amounts."""
    print("\n\n" + "=" * 70)
    print("WORKING PARAMETER RANGES BY DATA LENGTH")
    print("=" * 70)

    scenarios = [
        ("2 months (~40 days)", 40),
        ("3 months (~63 days)", 63),
        ("6 months (~126 days)", 126),
        ("1 year (~252 days)", 252),
        ("2 years (~504 days)", 504),
    ]

    for scenario_name, days in scenarios:
        print(f"\n{scenario_name}:")
        print("-" * 70)

        suggestions = suggest_parameters(days, "walk_forward")

        print(f"  Method: {suggestions['method']}")
        print(f"  Rolling window: {suggestions['rolling_window']} days")
        print(f"  Step size: {suggestions['rolling_step']} days")

        if suggestions['method'] == 'walk_forward':
            print(f"  Train window: {suggestions['train_window']} days")
            print(f"  Test window: {suggestions['test_window']} days")

            # Calculate expected periods
            num_periods = (days - suggestions['train_window']) // suggestions['step_size']
            print(f"  Expected walk-forward periods: {num_periods}")
        else:
            print(f"  Train/test split: {int(suggestions['train_pct']*100)}% / {int((1-suggestions['train_pct'])*100)}%")

        print(f"  Note: {suggestions['note']}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTING BACKTESTING WITH LIMITED TRADING HISTORY")
    print("=" * 70)
    print("\nThis demonstrates what parameters work when stocks")
    print("have only been trading for 6 months to 1 year.")

    # Show what parameters work for different data lengths
    show_parameter_ranges()

    # Test actual scenarios
    results_6mo = test_6_months_data()
    results_1yr = test_1_year_data()

    # Show manual parameter adjustment
    test_manual_adjustment()

    print("\n\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
1. ✓ You CAN backtest stocks with only 6 months of data
   - Use smaller windows (30-63 days)
   - Use smaller step size (5-10 days)
   - Use train/test split (simpler than walk-forward)

2. ✓ You CAN backtest stocks with 1 year of data
   - Use medium windows (63-126 days)
   - Can use walk-forward with adaptive windows
   - More reliable than 6 months

3. ⚠️ Trade-offs with limited data:
   - Fewer rolling windows → less reliability
   - Smaller windows → noisier cointegration tests
   - Fewer backtest periods → less robust validation
   - Results should be taken with more caution

4. ✓ The system ADAPTS automatically:
   - Uses min(252, len(data)//3) for train window
   - Uses min(63, len(data)//10) for test window
   - Suggests appropriate method for data length

5. 💡 Best approach for new stocks:
   - Use suggested parameters from suggest_parameters()
   - Expect warnings (that's normal)
   - Supplement with out-of-sample live testing
   - Be more conservative with position sizing
""")
