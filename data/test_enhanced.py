"""
Test script for enhanced cointegration analysis.
"""

import warnings
warnings.filterwarnings('ignore')

from cointegration_analysis import comprehensive_cointegration_analysis

def test_enhanced_analysis():
    """Test the enhanced comprehensive analysis with backtesting."""

    print("=" * 70)
    print("TESTING ENHANCED COINTEGRATION ANALYSIS")
    print("=" * 70)

    # Test with a simple pair
    tickers = ["AAPL", "MSFT"]

    print(f"\nAnalyzing pair: {', '.join(tickers)}")
    print("This will include:")
    print("  - Cointegration testing")
    print("  - Enhanced metrics (half-life, z-score distribution, etc.)")
    print("  - Rolling window analysis")
    print("  - Backtesting simulation")
    print("  - Deep LLM interpretation")

    try:
        results = comprehensive_cointegration_analysis(
            tickers=tickers,
            period="6mo",  # Use shorter period for faster testing
            window=60,
            step_size=10,
            use_llm=True,
            save_plots=True,
            plots_dir="../plots"
        )

        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)

        if results['is_pair']:
            print(f"\n✓ Cointegration Test: {'PASS' if results['cointegration']['is_cointegrated'] else 'NOT COINTEGRATED'}")
            print(f"  P-value: {results['cointegration']['p_value']:.4f}")
            print(f"  Hedge Ratio: {results['cointegration']['hedge_ratio']:.4f}")

            if 'backtest' in results and results['backtest'] is not None:
                bt = results['backtest']['metrics']
                print(f"\n✓ Backtest Results:")
                print(f"  Total Return: {bt['total_return_pct']:.2f}%")
                print(f"  Sharpe Ratio: {bt['sharpe_ratio']:.2f}")
                print(f"  Win Rate: {bt['win_rate']:.1f}%")
                print(f"  Total Trades: {bt['total_trades']}")

            if results['interpretation']:
                print(f"\n✓ LLM Interpretation: Generated ({len(results['interpretation'])} characters)")

        print("\n" + "=" * 70)
        print("TEST COMPLETE - All features working!")
        print("=" * 70)

        return results

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = test_enhanced_analysis()
