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
