"""
Cointegration testing functions using Johansen and Engle-Granger tests.
"""

import pandas as pd
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen


def test_basket_cointegration(data_dict, k_ar_diff=5, crit_level=1):
    """
    Test Johansen cointegration for all baskets.

    Parameters:
    -----------
    data_dict : dict
        Dictionary mapping basket names to DataFrames
    k_ar_diff : int
        Lag order (default 5)
    crit_level : int
        Confidence level: 0=90%, 1=95%, 2=99%

    Returns:
    --------
    pd.DataFrame
        Summary of cointegration test results
    """
    results = []

    for name, df in data_dict.items():
        try:
            result = coint_johansen(df, det_order=0, k_ar_diff=k_ar_diff)
            n_coint = sum(result.lr1 > result.cvt[:, crit_level])

            results.append({
                'Basket': name,
                'N_Stocks': len(df.columns),
                'Coint_Rank': n_coint,
                'Max_Trace': result.lr1[0] if len(result.lr1) > 0 else 0
            })

            print(f"{name:40} | Rank: {n_coint}")

        except Exception as e:
            print(f"{name:40} | Error: {e}")

    return pd.DataFrame(results)


def analyze_basket(data, k_ar_diff=5, crit_level=1):
    """
    Perform Johansen cointegration analysis on a single basket.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data for the basket
    k_ar_diff : int
        Lag order
    crit_level : int
        0=90%, 1=95%, 2=99%

    Returns:
    --------
    tuple
        (result, cointegrating_vectors_df, n_coint)
    """
    # Run Johansen test
    result = coint_johansen(data, det_order=0, k_ar_diff=k_ar_diff)
    n_coint = sum(result.lr1 > result.cvt[:, crit_level])

    # Print results
    print(f"\nBasket: {', '.join(data.columns)}")
    print(f"Cointegration rank: {n_coint}")
    print(f"Trace statistics: {result.lr1}")
    print(f"Critical values (95%): {result.cvt[:, 1]}")

    # Extract cointegrating vectors
    vectors_df = None
    if n_coint > 0:
        vectors_df = pd.DataFrame(
            result.evec[:, :n_coint],
            index=data.columns,
            columns=[f"Vector_{i+1}" for i in range(n_coint)]
        )
        print("\nCointegrating vectors:")
        print(vectors_df.to_string())

    return result, vectors_df, n_coint


def test_pair_cointegration(data):
    """
    Test cointegration for a pair of stocks using Engle-Granger test.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with exactly 2 columns

    Returns:
    --------
    tuple
        (score, p_value, critical_values)
    """
    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks for pair testing")

    stock_a, stock_b = data.columns
    score, p_value, crit_values = coint(data[stock_a], data[stock_b])

    print(f"\nPair: {stock_a} vs {stock_b}")
    print(f"Cointegration test score: {score:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Cointegrated: {'Yes' if p_value < 0.05 else 'No'}")

    return score, p_value, crit_values


def get_hedge_ratio(data):
    """
    Calculate the hedge ratio (beta) for a pair of stocks.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with exactly 2 columns

    Returns:
    --------
    tuple
        (beta, alpha) from linear regression
    """
    import numpy as np

    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks")

    stock_a, stock_b = data.columns
    # Regression: stock_a = beta * stock_b + alpha
    beta, alpha = np.polyfit(data[stock_b], data[stock_a], 1)

    print(f"\nHedge ratio (beta): {beta:.4f}")
    print(f"Intercept (alpha): {alpha:.4f}")
    print(f"Position: Long 1 share of {stock_a}, Short {beta:.4f} shares of {stock_b}")

    return beta, alpha


def find_cointegrated_pairs(basket, data_dict, p_threshold=0.05):
    """
    Find all cointegrated pairs within a basket.

    Parameters:
    -----------
    basket : list
        List of stock tickers
    data_dict : dict
        Dictionary with basket data
    p_threshold : float
        P-value threshold for cointegration

    Returns:
    --------
    pd.DataFrame
        All cointegrated pairs with their statistics
    """
    from itertools import combinations
    import numpy as np

    results = []

    # Find the basket data
    basket_name = "_".join(basket)
    if basket_name not in data_dict:
        print(f"Basket {basket_name} not found in data")
        return None

    data = data_dict[basket_name]

    # Test all pairs
    for stock_a, stock_b in combinations(data.columns, 2):
        try:
            score, p_value, _ = coint(data[stock_a], data[stock_b])
            beta = np.polyfit(data[stock_b], data[stock_a], 1)[0]

            if p_value < p_threshold:
                results.append({
                    'Stock_A': stock_a,
                    'Stock_B': stock_b,
                    'P_Value': p_value,
                    'Test_Score': score,
                    'Hedge_Ratio': beta
                })
        except Exception as e:
            print(f"Error testing {stock_a} vs {stock_b}: {e}")

    if results:
        results_df = pd.DataFrame(results).sort_values('P_Value')
        print(f"\nFound {len(results_df)} cointegrated pairs in basket")
        return results_df
    else:
        print("\nNo cointegrated pairs found")
        return pd.DataFrame()


def calculate_enhanced_metrics(results):
    """
    Calculate enhanced metrics for deeper LLM interpretation.

    Parameters:
    -----------
    results : dict
        Results dictionary from comprehensive analysis

    Returns:
    --------
    dict
        Enhanced metrics including half-life, z-score distribution, etc.
    """
    import numpy as np
    from statsmodels.tsa.stattools import adfuller

    enhanced = {}

    if results['is_pair']:
        data = results['data']
        coint = results['cointegration']
        rolling = results['rolling_analysis']

        # Calculate spread
        spread = data.iloc[:, 0] - coint['hedge_ratio'] * data.iloc[:, 1]

        # 1. Half-life of mean reversion (critical for trading frequency)
        # Using lag-1 autoregression: spread(t) = a + b*spread(t-1) + error
        spread_lag = spread.shift(1).dropna()
        spread_curr = spread[1:]

        try:
            beta = np.polyfit(spread_lag, spread_curr, 1)[0]
            if 0 < abs(beta) < 1:
                halflife = -np.log(2) / np.log(abs(beta))
            else:
                halflife = np.inf
        except:
            halflife = np.inf

        enhanced['halflife_days'] = halflife if not np.isinf(halflife) else 999

        # 2. Spread statistics
        enhanced['spread_mean'] = spread.mean()
        enhanced['spread_std'] = spread.std()
        enhanced['spread_min'] = spread.min()
        enhanced['spread_max'] = spread.max()
        enhanced['spread_current'] = spread.iloc[-1]

        # Current z-score
        zscore_current = (spread.iloc[-1] - spread.mean()) / spread.std()
        enhanced['spread_zscore_current'] = zscore_current

        # 3. Z-score distribution (for entry/exit thresholds)
        zscore = (spread - spread.mean()) / spread.std()
        enhanced['zscore_quartiles'] = {
            'q25': zscore.quantile(0.25),
            'q50': zscore.quantile(0.50),
            'q75': zscore.quantile(0.75)
        }
        enhanced['zscore_extremes'] = {
            'pct_above_2': (zscore > 2).mean() * 100,
            'pct_below_neg2': (zscore < -2).mean() * 100,
            'max_zscore': zscore.max(),
            'min_zscore': zscore.min()
        }

        # 4. Trading signal analysis
        entry_signals = (zscore.abs() > 2).sum()
        enhanced['historical_entry_opportunities'] = int(entry_signals)
        enhanced['avg_days_between_entries'] = len(zscore) / entry_signals if entry_signals > 0 else 999

        # 5. Recent trend analysis (last 60 days vs historical)
        recent_window = min(60, len(rolling) // 3)
        if len(rolling) > recent_window:
            recent_pvalues = rolling['p_value'].tail(recent_window)
            older_pvalues = rolling['p_value'].head(len(rolling) - recent_window)

            enhanced['recent_trend'] = {
                'recent_avg_pvalue': recent_pvalues.mean(),
                'historical_avg_pvalue': older_pvalues.mean(),
                'relationship_strengthening': recent_pvalues.mean() < older_pvalues.mean()
            }
        else:
            enhanced['recent_trend'] = {
                'recent_avg_pvalue': rolling['p_value'].mean(),
                'historical_avg_pvalue': rolling['p_value'].mean(),
                'relationship_strengthening': False
            }

        # 6. Cointegration stability score (0-100)
        pct_coint = (rolling['p_value'] < 0.05).mean() * 100
        beta_cv = (rolling['beta'].std() / abs(rolling['beta'].mean())) * 100 if rolling['beta'].mean() != 0 else 100

        stability_score = (
            pct_coint * 0.5 +  # 50% weight on % cointegrated
            max(0, 100 - beta_cv) * 0.3 +  # 30% weight on beta stability
            max(0, 100 - rolling['p_value'].std() * 1000) * 0.2  # 20% weight on p-value consistency
        )
        enhanced['stability_score'] = min(100, max(0, stability_score))

        # 7. Simple Sharpe ratio estimate
        # Based on z-score mean reversion
        returns_estimate = []
        for i in range(1, len(zscore)):
            if abs(zscore.iloc[i-1]) > 2 and abs(zscore.iloc[i]) < abs(zscore.iloc[i-1]):
                # Mean reversion occurred
                returns_estimate.append(abs(zscore.iloc[i-1]) - abs(zscore.iloc[i]))

        if returns_estimate and len(returns_estimate) > 5:
            mean_ret = np.mean(returns_estimate)
            std_ret = np.std(returns_estimate)
            enhanced['estimated_sharpe'] = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0
        else:
            enhanced['estimated_sharpe'] = None

        # 8. Beta drift metrics
        enhanced['beta_drift'] = {
            'recent_beta_change': rolling['beta'].diff().tail(5).abs().mean(),
            'max_beta_change': rolling['beta'].diff().abs().max(),
            'beta_cv': beta_cv
        }

    else:
        # For baskets, add basket-specific metrics
        enhanced['is_basket'] = True
        # Add more basket metrics as needed

    return enhanced


def comprehensive_cointegration_analysis(
    tickers,
    period="2y",
    window=252,
    step_size=21,
    use_llm=True,
    save_plots=True,
    plots_dir="plots"
):
    """
    Comprehensive cointegration analysis for pairs or baskets.

    This function performs a complete analysis including:
    - Basic cointegration tests (Engle-Granger for pairs, Johansen for baskets)
    - Rolling window analysis to assess stability over time
    - Spread stability analysis (for pairs)
    - Pairwise cointegration within baskets
    - Visualization of all results
    - LLM-powered interpretation with trading strategy suggestions

    Parameters:
    -----------
    tickers : list
        List of stock ticker symbols
    period : str
        Time period for data download (e.g., "1y", "2y", "5y")
    window : int
        Rolling window size in trading days (default 252 = 1 year)
    step_size : int
        Step size for rolling windows in days (default 21 = ~1 month)
    use_llm : bool
        Whether to generate LLM interpretation
    save_plots : bool
        Whether to save plots to disk
    plots_dir : str
        Directory to save plots

    Returns:
    --------
    dict
        Comprehensive results dictionary containing all analysis outputs
    """
    import os
    from data_loader import get_close_price_data
    from rolling_analysis import (
        rolling_cointegration_analysis,
        analyze_spread_stability
    )
    from visualization import (
        plot_price_series,
        plot_rolling_results,
        plot_spread_analysis
    )

    print("=" * 70)
    print(f"COMPREHENSIVE COINTEGRATION ANALYSIS: {', '.join(tickers)}")
    print("=" * 70)

    # Create plots directory
    if save_plots and not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # Download data
    total_steps = 6 if len(tickers) == 2 else 5
    print(f"\n[1/{total_steps}] Downloading {period} of price data...")
    data = get_close_price_data(tickers, period=period)
    print(f"  Downloaded {len(data)} days of data")

    # Initialize results dictionary
    results = {
        'tickers': tickers,
        'is_pair': len(tickers) == 2,
        'data': data,
        'period': period,
        'window': window,
        'step_size': step_size
    }

    # Determine if pair or basket
    is_pair = len(tickers) == 2

    if is_pair:
        # PAIR ANALYSIS
        print(f"\n[2/{total_steps}] Running pair cointegration test (Engle-Granger)...")
        score, p_value, crit_values = test_pair_cointegration(data)
        beta, alpha = get_hedge_ratio(data)

        results['cointegration'] = {
            'score': score,
            'p_value': p_value,
            'critical_values': crit_values,
            'hedge_ratio': beta,
            'alpha': alpha,
            'is_cointegrated': p_value < 0.05
        }

        # Plot price series
        if save_plots:
            price_plot_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_prices.png")
            plot_price_series(data, title=f"{' vs '.join(tickers)} - Log Prices",
                            save_path=price_plot_path)

        # Spread analysis
        print(f"\n[3/{total_steps}] Analyzing spread stability...")
        stability = analyze_spread_stability(data, window=window, step_size=step_size)
        results['spread_stability'] = stability

        if save_plots:
            spread_plot_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_spread_analysis.png")
            plot_spread_analysis(data, hedge_ratio=beta, zscore_window=20,
                               save_path=spread_plot_path)

        # Rolling analysis
        print(f"\n[4/{total_steps}] Running rolling cointegration analysis...")
        rolling_results = rolling_cointegration_analysis(data, window=window, step_size=step_size)
        results['rolling_analysis'] = rolling_results

        if save_plots:
            rolling_plot_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_rolling_analysis.png")
            plot_rolling_results(rolling_results, tickers, window=window, step_size=step_size,
                               save_path=rolling_plot_path)

        results['pairs_within'] = None

    else:
        # BASKET ANALYSIS
        print(f"\n[2/{total_steps}] Running basket cointegration test (Johansen)...")
        johansen_result, vectors_df, n_coint = analyze_basket(data, k_ar_diff=5, crit_level=1)

        results['cointegration'] = {
            'rank': n_coint,
            'trace_stats': johansen_result.lr1,
            'critical_values': johansen_result.cvt,
            'cointegrating_vectors': vectors_df,
            'is_cointegrated': n_coint > 0
        }

        # Plot price series
        if save_plots:
            price_plot_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_prices.png")
            plot_price_series(data, title=f"Basket: {', '.join(tickers)} - Log Prices",
                            save_path=price_plot_path)

        # Find cointegrated pairs within basket
        print(f"\n[3/{total_steps}] Finding cointegrated pairs within basket...")
        data_dict = {"_".join(tickers): data}
        pairs = find_cointegrated_pairs(tickers, data_dict, p_threshold=0.05)
        results['pairs_within'] = pairs

        # Rolling analysis
        print(f"\n[4/{total_steps}] Running rolling cointegration analysis...")
        rolling_results = rolling_cointegration_analysis(data, window=window, step_size=step_size)
        results['rolling_analysis'] = rolling_results

        if save_plots:
            rolling_plot_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_rolling_analysis.png")
            plot_rolling_results(rolling_results, tickers, window=window, step_size=step_size,
                               save_path=rolling_plot_path)

        results['spread_stability'] = None

    # Backtesting (for pairs only)
    if is_pair:
        print(f"\n[5/6] Running backtest strategy simulation...")
        try:
            from backtesting import backtest_pairs_strategy, print_backtest_summary

            # Run backtest with default parameters
            backtest_result = backtest_pairs_strategy(
                data,
                hedge_ratio=beta,
                entry_zscore=2.0,
                exit_zscore=0.5,
                stop_loss_zscore=4.0,
                transaction_cost=0.001,
                initial_capital=100000
            )

            results['backtest'] = backtest_result

            # Print summary
            print_backtest_summary(backtest_result)

            # Optionally save trades to CSV
            if save_plots:
                trades_path = os.path.join(plots_dir, f"{'_'.join(tickers)}_backtest_trades.csv")
                backtest_result['trades'].to_csv(trades_path, index=False)
                print(f"\n  Saved backtest trades to {trades_path}")

        except Exception as e:
            print(f"  ⚠ Could not run backtest: {e}")
            results['backtest'] = None
    else:
        results['backtest'] = None

    # LLM Interpretation
    print(f"\n[6/6] Generating comprehensive interpretation...")
    if use_llm:
        try:
            from llm_interpreter import interpret_comprehensive_analysis
            interpretation = interpret_comprehensive_analysis(results)
            results['interpretation'] = interpretation

            print("\n" + "=" * 70)
            print("AI INTERPRETATION & TRADING STRATEGY:")
            print("=" * 70)
            print(interpretation)
        except Exception as e:
            print(f"  ⚠ Could not generate LLM interpretation: {e}")
            results['interpretation'] = None
    else:
        results['interpretation'] = None

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)

    return results
