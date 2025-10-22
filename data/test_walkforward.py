"""
Test script for walk-forward and train/test split backtesting.
"""

import warnings
warnings.filterwarnings('ignore')

from cointegration_analysis import comprehensive_cointegration_analysis
from backtesting import walk_forward_backtest, backtest_with_train_test_split, print_backtest_summary
from data_loader import get_close_price_data


def test_walkforward_backtest():
    """Test walk-forward backtesting methodology."""
    print("=" * 70)
    print("TESTING WALK-FORWARD BACKTESTING")
    print("=" * 70)

    # Test with a pair
    tickers = ["AAPL", "MSFT"]
    period = "1y"  # Use 1 year for faster testing

    print(f"\nDownloading data for {tickers}...")
    data = get_close_price_data(tickers, period=period)
    print(f"Downloaded {len(data)} days of data")

    # Run walk-forward backtest
    print("\n" + "=" * 70)
    print("1. WALK-FORWARD BACKTEST")
    print("=" * 70)

    wf_results = walk_forward_backtest(
        data,
        train_window=120,  # 6 months training
        test_window=40,    # 2 months testing
        step_size=20,      # Roll forward every month
        entry_zscore=2.0,
        exit_zscore=0.5,
        stop_loss_zscore=4.0,
        transaction_cost=0.001,
        initial_capital=100000,
        zscore_window=20
    )

    print_backtest_summary(wf_results)

    # Run train/test split for comparison
    print("\n" + "=" * 70)
    print("2. TRAIN/TEST SPLIT BACKTEST")
    print("=" * 70)

    tt_results = backtest_with_train_test_split(
        data,
        train_pct=0.6,
        entry_zscore=2.0,
        exit_zscore=0.5,
        stop_loss_zscore=4.0,
        transaction_cost=0.001,
        initial_capital=100000,
        zscore_window=20
    )

    print_backtest_summary(tt_results)

    # Compare results
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    wf_metrics = wf_results['metrics']
    tt_metrics = tt_results['test_results']['metrics']

    print("\nWalk-Forward vs Train/Test Split:")
    print(f"  Total Return:")
    print(f"    Walk-Forward: {wf_metrics['total_return_pct']:.2f}%")
    print(f"    Train/Test:   {tt_metrics['total_return_pct']:.2f}%")

    print(f"\n  Sharpe Ratio:")
    print(f"    Walk-Forward: {wf_metrics['sharpe_ratio']:.2f}")
    print(f"    Train/Test:   {tt_metrics['sharpe_ratio']:.2f}")

    print(f"\n  Total Trades:")
    print(f"    Walk-Forward: {wf_metrics['total_trades']}")
    print(f"    Train/Test:   {tt_metrics['total_trades']}")

    print(f"\n  Win Rate:")
    print(f"    Walk-Forward: {wf_metrics['win_rate']:.1f}%")
    print(f"    Train/Test:   {tt_metrics['win_rate']:.1f}%")

    if 'parameter_stability' in wf_metrics:
        ps = wf_metrics['parameter_stability']
        print(f"\n  Walk-Forward Parameter Stability:")
        print(f"    Hedge Ratio CV: {ps['hedge_ratio_cv']*100:.2f}%")
        print(f"    Hedge Ratio Range: [{ps['hedge_ratio_range'][0]:.4f}, {ps['hedge_ratio_range'][1]:.4f}]")

    return wf_results, tt_results


def test_comprehensive_with_walkforward():
    """Test comprehensive analysis with walk-forward backtesting."""
    print("\n\n" + "=" * 70)
    print("TESTING COMPREHENSIVE ANALYSIS WITH WALK-FORWARD")
    print("=" * 70)

    # Run comprehensive analysis with walk-forward
    results = comprehensive_cointegration_analysis(
        tickers=["AAPL", "MSFT"],
        period="1y",
        window=63,
        step_size=21,
        use_llm=False,  # Disable LLM for faster testing
        save_plots=True,
        plots_dir="plots",
        backtest_method="walk_forward"  # Use walk-forward method
    )

    print("\n" + "=" * 70)
    print("COMPREHENSIVE ANALYSIS COMPLETE")
    print("=" * 70)

    if results['backtest']:
        print("\nBacktest method used:", results.get('backtest_method', 'unknown'))
        print("Check the 'plots' directory for:")
        print("  - Price charts")
        print("  - Spread analysis")
        print("  - Rolling cointegration results")
        print("  - Backtest trades CSV")
        print("  - Walk-forward parameters CSV")

    return results


if __name__ == "__main__":
    # Test 1: Direct walk-forward and train/test split comparison
    print("\n" + "=" * 70)
    print("TEST 1: Walk-Forward vs Train/Test Split")
    print("=" * 70)
    wf_results, tt_results = test_walkforward_backtest()

    # Test 2: Comprehensive analysis with walk-forward
    print("\n\n" + "=" * 70)
    print("TEST 2: Comprehensive Analysis with Walk-Forward")
    print("=" * 70)
    comprehensive_results = test_comprehensive_with_walkforward()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\nKey Improvements Made:")
    print("  1. Fixed look-ahead bias - now uses rolling z-scores")
    print("  2. Added walk-forward backtesting - most robust method")
    print("  3. Added train/test split - simpler alternative")
    print("  4. Parameter stability tracking - monitors hedge ratio changes")
    print("  5. Integrated into comprehensive analysis workflow")
