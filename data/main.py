"""
Main script for running cointegration analysis on stock baskets.

This script demonstrates how to use the cointegration analysis modules.
"""

import warnings
import os
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

from config import ALL_BASKETS, basket_1, basket_2, basket_3
from data_loader import get_close_price_data, download_all_baskets, load_all_csv
from llm_interpreter import (
    interpret_rolling_analysis,
    interpret_basket_cointegration,
    interpret_spread_stability,
    interpret_pairs,
    interpret_pair_cointegration
)

# Create plots directory if it doesn't exist
PLOTS_DIR = "plots"
if not os.path.exists(PLOTS_DIR):
    os.makedirs(PLOTS_DIR)
from cointegration_analysis import (
    test_basket_cointegration,
    analyze_basket,
    test_pair_cointegration,
    get_hedge_ratio,
    find_cointegrated_pairs
)
from rolling_analysis import (
    rolling_cointegration_analysis,
    batch_rolling_analysis,
    calculate_spread,
    calculate_zscore,
    analyze_spread_stability
)
from visualization import (
    plot_price_series,
    plot_rolling_results,
    plot_spread,
    plot_zscore,
    plot_spread_analysis,
    plot_cointegration_heatmap
)


def example_1_download_data():
    """Example 1: Download data for all baskets."""
    print("=" * 70)
    print("EXAMPLE 1: Download Data for All Baskets")
    print("=" * 70)

    # Download all baskets
    all_data = download_all_baskets(ALL_BASKETS, period="1y", max_missing=25)

    return all_data


def example_2_test_cointegration(use_llm=True):
    """Example 2: Test cointegration for all baskets."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Test Cointegration for All Baskets")
    print("=" * 70)

    # Load all CSV data
    all_data = load_all_csv()

    # Test cointegration
    summary = test_basket_cointegration(all_data, k_ar_diff=5, crit_level=1)

    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(summary.to_string(index=False))

    # Show baskets with cointegration
    cointegrated = summary[summary['Coint_Rank'] > 0]
    print(f"\n{len(cointegrated)} baskets show cointegration:")
    print(cointegrated[['Basket', 'Coint_Rank']].to_string(index=False))

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_basket_cointegration(summary)
        print(interpretation)

    return summary


def example_3_analyze_pair(use_llm=True):
    """Example 3: Detailed analysis of a specific pair."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Analyze Specific Pair (NET vs SNOW)")
    print("=" * 70)

    # Download data for the pair
    tickers = ["NET", "SNOW"]
    data = get_close_price_data(tickers, period="1y")

    # Test cointegration
    score, p_value, _ = test_pair_cointegration(data)

    # Get hedge ratio
    beta, alpha = get_hedge_ratio(data)

    print(f"\nTest Results:")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Test Statistic: {score:.3f}")
    print(f"  Hedge Ratio: {beta:.3f}")

    # Plot prices
    plot_price_series(data, title="NET vs SNOW - Log Prices",
                     save_path=os.path.join(PLOTS_DIR, "net_snow_prices.png"))

    # Analyze spread
    plot_spread_analysis(data, hedge_ratio=beta, zscore_window=20,
                        save_path=os.path.join(PLOTS_DIR, "net_snow_spread_analysis.png"))

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_pair_cointegration(
            tickers[0], tickers[1], score, p_value, beta
        )
        print(interpretation)

    return data, beta


def example_4_rolling_analysis_pair(use_llm=True):
    """Example 4: Rolling cointegration analysis for a pair."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Rolling Analysis for Pair (NET vs SNOW)")
    print("=" * 70)

    # Download data
    tickers = ["NET", "SNOW"]
    data = get_close_price_data(tickers, period="2y")

    # Run rolling analysis
    results = rolling_cointegration_analysis(data, window=180, step_size=21)

    # Plot results
    plot_rolling_results(results, tickers, window=180, step_size=21,
                        save_path=os.path.join(PLOTS_DIR, "net_snow_rolling_analysis.png"))

    print(f"\nRolling Analysis Summary:")
    print(f"  Average cointegration rank: {results['coint_rank'].mean():.2f}")
    print(f"  % of time cointegrated: {(results['coint_rank'] > 0).mean() * 100:.1f}%")

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_rolling_analysis(results, tickers)
        print(interpretation)

    return results


def example_5_rolling_analysis_basket(use_llm=True):
    """Example 5: Rolling cointegration analysis for a basket."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Rolling Analysis for Basket")
    print("=" * 70)

    # Download data for basket
    data = get_close_price_data(basket_1, period="2y")

    # Run rolling analysis
    results = rolling_cointegration_analysis(data, window=252, step_size=21)

    # Plot results
    plot_rolling_results(results, data.columns.tolist(), window=252, step_size=21,
                        save_path=os.path.join(PLOTS_DIR, "basket1_rolling_analysis.png"))

    print(f"\nRolling Analysis Summary:")
    print(f"  Average cointegration rank: {results['coint_rank'].mean():.2f}")
    print(f"  % of time cointegrated: {(results['coint_rank'] > 0).mean() * 100:.1f}%")

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_rolling_analysis(results, data.columns.tolist())
        print(interpretation)

    return results


def example_6_batch_rolling_analysis():
    """Example 6: Batch rolling analysis for multiple baskets."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Batch Rolling Analysis")
    print("=" * 70)

    # Load all CSV data
    all_data = load_all_csv()

    # Run batch analysis (limit to first 3 for demonstration)
    limited_data = {k: all_data[k] for k in list(all_data.keys())[:3]}
    results = batch_rolling_analysis(limited_data, window=252, step_size=21)

    return results


def example_7_find_pairs_in_basket(use_llm=True):
    """Example 7: Find all cointegrated pairs within a basket."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Find Cointegrated Pairs in Basket")
    print("=" * 70)

    # Load all data
    all_data = load_all_csv()

    # Find pairs in basket_1
    pairs = find_cointegrated_pairs(basket_1, all_data, p_threshold=0.05)

    if len(pairs) > 0:
        print("\nCointegrated Pairs:")
        print(pairs.to_string(index=False))

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_pairs(pairs, basket_name="Basket 1")
        print(interpretation)

    return pairs


def example_8_spread_stability(use_llm=True):
    """Example 8: Analyze spread stability for a pair."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Spread Stability Analysis")
    print("=" * 70)

    # Download data
    tickers = ["NET", "SNOW"]
    data = get_close_price_data(tickers, period="2y")

    # Analyze spread stability
    stability = analyze_spread_stability(data, window=180, step_size=21)

    # Plot hedge ratio over time
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 5))
    plt.plot(stability.index, stability['hedge_ratio'], linewidth=2, color='purple')
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Hedge Ratio', fontsize=11)
    plt.title('Hedge Ratio Stability Over Time', fontsize=13, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    save_path = os.path.join(PLOTS_DIR, "hedge_ratio_stability.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"  Saved plot to {save_path}")
    plt.close()

    print(f"\nHedge Ratio Statistics:")
    print(f"  Average: {stability['hedge_ratio'].mean():.3f}")
    print(f"  Std Dev: {stability['hedge_ratio'].std():.3f}")
    print(f"  Range: {stability['hedge_ratio'].min():.3f} to {stability['hedge_ratio'].max():.3f}")

    # LLM Interpretation
    if use_llm:
        print("\n" + "=" * 70)
        print("AI INTERPRETATION:")
        print("=" * 70)
        interpretation = interpret_spread_stability(stability, tickers)
        print(interpretation)

    return stability


def main():
    """
    Main function to run all examples.

    Comment out examples you don't want to run.
    """
    print("\n" + "=" * 70)
    print("COINTEGRATION ANALYSIS - MAIN SCRIPT")
    print("=" * 70)

    # Uncomment the examples you want to run:

    # Example 1: Download all basket data
    # all_data = example_1_download_data()

    # Example 2: Test cointegration for all baskets
    # summary = example_2_test_cointegration()

    # Example 3: Analyze a specific pair
    # data, beta = example_3_analyze_pair()

    # Example 4: Rolling analysis for a pair
    # results_pair = example_4_rolling_analysis_pair()

    # Example 5: Rolling analysis for a basket
    # results_basket = example_5_rolling_analysis_basket()

    # Example 6: Batch rolling analysis
    # batch_results = example_6_batch_rolling_analysis()

    # Example 7: Find pairs in a basket
    # pairs = example_7_find_pairs_in_basket()

    # Example 8: Spread stability analysis
    # stability = example_8_spread_stability()

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Import the comprehensive analysis function
    from cointegration_analysis import comprehensive_cointegration_analysis

    # Example 1: Analyze a pair of stocks
    pair_results = comprehensive_cointegration_analysis(
        tickers=["SNDK", "MU"],
        period="6mo",
        window=63,  
        step_size=21,  # ~1 month
        use_llm=True
    )

    # Example 2: Analyze a basket of stocks
    # basket_results = comprehensive_cointegration_analysis(
    #     tickers=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"],
    #     period="2y",
    #     window=252,  # 252 trading days = ~1 year
    #     step_size=21,
    #     use_llm=True
    # )
    