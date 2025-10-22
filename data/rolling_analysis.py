"""
Rolling window cointegration analysis for time-varying relationship detection.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen


def rolling_cointegration_analysis(data, window=252, step_size=21, crit_level=1):
    """
    Rolling cointegration analysis for pairs or baskets.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data (log prices)
    window : int
        Rolling window size in days (default 252 = 1 year)
    step_size : int
        Days to shift window (default 21 = ~1 month)
    crit_level : int
        Confidence level for Johansen test: 0=90%, 1=95%, 2=99%

    Returns:
    --------
    pd.DataFrame
        Rolling test results with cointegrating vectors
    """
    n_stocks = len(data.columns)
    results = []

    if n_stocks == 2:
        # PAIRS: Use Engle-Granger test
        print(f"\nRunning rolling cointegration for pair: {' vs '.join(data.columns)}")
        print(f"Window: {window} days, Step: {step_size} days")
        print(f"Total windows: {(len(data) - window) // step_size + 1}\n")

        for i in range(window, len(data) + 1, step_size):
            window_data = data.iloc[i-window:i]

            # Engle-Granger test
            score, p_value, _ = coint(window_data.iloc[:, 0], window_data.iloc[:, 1])

            # Calculate beta (hedge ratio)
            beta = np.polyfit(window_data.iloc[:, 1], window_data.iloc[:, 0], 1)[0]

            results.append({
                'date': data.index[i-1],
                'p_value': p_value,
                'beta': beta,
                'cointegrated': p_value < 0.05
            })

        # Summary statistics
        results_df = pd.DataFrame(results).set_index('date')
        pct_coint = (results_df['p_value'] < 0.05).mean() * 100

        print(f"Summary:")
        print(f"  Cointegrated {pct_coint:.1f}% of the time")
        print(f"  Beta: {results_df['beta'].mean():.3f} ± {results_df['beta'].std():.3f}")
        print(f"  Beta range: [{results_df['beta'].min():.3f}, {results_df['beta'].max():.3f}]")

    else:
        # BASKETS: Use Johansen test
        print(f"\nRunning rolling cointegration for basket: {', '.join(data.columns)}")
        print(f"Window: {window} days, Step: {step_size} days")
        print(f"Total windows: {(len(data) - window) // step_size + 1}\n")

        for i in range(window, len(data) + 1, step_size):
            window_data = data.iloc[i-window:i]

            try:
                # Johansen test
                result = coint_johansen(window_data, det_order=0, k_ar_diff=1)
                coint_rank = sum(result.lr1 > result.cvt[:, crit_level])
                max_trace = result.lr1[0] if len(result.lr1) > 0 else 0

                # Calculate approximate p-value based on trace statistic and critical values
                # Using the ratio of trace stat to critical value as a proxy
                if len(result.lr1) > 0 and len(result.cvt) > 0:
                    # If trace stat exceeds 99% critical value, p-value < 0.01
                    # If it exceeds 95% critical value, p-value < 0.05
                    # If it exceeds 90% critical value, p-value < 0.10
                    if result.lr1[0] > result.cvt[0, 2]:  # 99% critical value
                        approx_pvalue = 0.005
                    elif result.lr1[0] > result.cvt[0, 1]:  # 95% critical value
                        approx_pvalue = 0.025
                    elif result.lr1[0] > result.cvt[0, 0]:  # 90% critical value
                        approx_pvalue = 0.075
                    else:
                        approx_pvalue = 0.15
                else:
                    approx_pvalue = np.nan

                # Store cointegrating vectors if they exist
                vectors_dict = {}
                if coint_rank > 0:
                    for j in range(coint_rank):
                        for k, stock in enumerate(window_data.columns):
                            vectors_dict[f'{stock}_v{j+1}'] = result.evec[k, j]

                results.append({
                    'date': data.index[i-1],
                    'trace_stat': max_trace,
                    'coint_rank': coint_rank,
                    'p_value_approx': approx_pvalue,
                    'crit_val_90': result.cvt[0, 0] if len(result.cvt) > 0 else np.nan,
                    'crit_val_95': result.cvt[0, 1] if len(result.cvt) > 0 else np.nan,
                    'crit_val_99': result.cvt[0, 2] if len(result.cvt) > 0 else np.nan,
                    **vectors_dict
                })

            except Exception as e:
                print(f"  Error at window ending {data.index[i-1]}: {e}")

        # Summary statistics
        results_df = pd.DataFrame(results).set_index('date')
        avg_rank = results_df['coint_rank'].mean()

        print(f"Summary:")
        print(f"  Average cointegration rank: {avg_rank:.2f}")
        print(f"  Max rank observed: {results_df['coint_rank'].max()}")
        print(f"  % of windows with cointegration: {(results_df['coint_rank'] > 0).mean()*100:.1f}%")

    return results_df


def batch_rolling_analysis(data_dict, window=252, step_size=21, crit_level=1):
    """
    Run rolling cointegration analysis on multiple baskets.

    Parameters:
    -----------
    data_dict : dict
        Dictionary mapping basket names to DataFrames
    window : int
        Rolling window size
    step_size : int
        Step size
    crit_level : int
        Confidence level

    Returns:
    --------
    dict
        Dictionary mapping basket names to results DataFrames
    """
    all_results = {}

    for i, (basket_name, data) in enumerate(data_dict.items(), 1):
        print(f"\n{'='*70}")
        print(f"Basket {i}/{len(data_dict)}: {basket_name}")
        print('='*70)

        try:
            results = rolling_cointegration_analysis(data, window=window,
                                                    step_size=step_size,
                                                    crit_level=crit_level)
            if results is not None:
                all_results[basket_name] = results

        except Exception as e:
            print(f"  Error analyzing basket: {e}")

    print(f"\n\nCompleted: {len(all_results)} baskets analyzed")
    return all_results


def calculate_spread(data, hedge_ratio=None):
    """
    Calculate the spread for a pair of stocks.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with exactly 2 columns
    hedge_ratio : float, optional
        Hedge ratio (beta). If None, will be calculated.

    Returns:
    --------
    pd.Series
        The spread time series
    """
    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks")

    stock_a, stock_b = data.columns

    if hedge_ratio is None:
        hedge_ratio = np.polyfit(data[stock_b], data[stock_a], 1)[0]

    spread = data[stock_a] - hedge_ratio * data[stock_b]
    return spread


def calculate_zscore(spread, window=20):
    """
    Calculate the z-score of the spread for mean reversion trading.

    Parameters:
    -----------
    spread : pd.Series
        The spread time series
    window : int
        Rolling window for mean and std calculation

    Returns:
    --------
    pd.Series
        Z-score time series
    """
    spread_mean = spread.rolling(window=window).mean()
    spread_std = spread.rolling(window=window).std()
    zscore = (spread - spread_mean) / spread_std
    return zscore


def analyze_spread_stability(data, window=252, step_size=21):
    """
    Analyze the stability of the spread over time using rolling windows.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with exactly 2 columns
    window : int
        Rolling window size
    step_size : int
        Step size

    Returns:
    --------
    pd.DataFrame
        Statistics about spread stability over time
    """
    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks for spread analysis")

    results = []

    for i in range(window, len(data) + 1, step_size):
        window_data = data.iloc[i-window:i]

        # Calculate hedge ratio for this window
        beta = np.polyfit(window_data.iloc[:, 1], window_data.iloc[:, 0], 1)[0]

        # Calculate spread
        spread = window_data.iloc[:, 0] - beta * window_data.iloc[:, 1]

        # Calculate spread statistics
        spread_mean = spread.mean()
        spread_std = spread.std()
        spread_adf = None  # Could add ADF test here if needed

        results.append({
            'date': data.index[i-1],
            'hedge_ratio': beta,
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'spread_cv': spread_std / abs(spread_mean) if spread_mean != 0 else np.nan
        })

    results_df = pd.DataFrame(results).set_index('date')

    print(f"\nSpread Stability Analysis:")
    print(f"  Hedge ratio range: [{results_df['hedge_ratio'].min():.3f}, {results_df['hedge_ratio'].max():.3f}]")
    print(f"  Hedge ratio volatility: {results_df['hedge_ratio'].std():.3f}")
    print(f"  Average spread CV: {results_df['spread_cv'].mean():.3f}")

    return results_df
