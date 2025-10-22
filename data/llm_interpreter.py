"""
LLM Interpreter Module for Cointegration Analysis Results

This module provides functions to interpret technical cointegration analysis results
using GPT-4o-mini, translating statistical outputs into plain English explanations
suitable for non-technical users.
"""

import os
from openai import OpenAI
import pandas as pd
from typing import List, Dict, Any


def _get_openai_client():
    """Initialize and return OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    return OpenAI(api_key=api_key)


def _call_gpt4o_mini(prompt: str, max_tokens: int = 500) -> str:
    """
    Call GPT-4o-mini API with the given prompt.

    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens in the response

    Returns:
        The model's response as a string
    """
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst explaining technical cointegration analysis results to non-technical investors. Use clear, simple language and focus on practical implications."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


def interpret_rolling_analysis(results_df: pd.DataFrame, tickers: List[str]) -> str:
    """
    Interpret rolling cointegration analysis results.

    Args:
        results_df: DataFrame with rolling analysis results (from rolling_cointegration_analysis)
        tickers: List of ticker symbols analyzed

    Returns:
        Plain English interpretation of the results
    """
    # Check if this is a pair (has p_value) or basket (has coint_rank)
    is_pair = 'p_value' in results_df.columns

    if is_pair:
        # For pairs: use p_value based metrics
        pct_cointegrated = (results_df['p_value'] < 0.05).mean() * 100
        avg_pvalue = results_df['p_value'].mean()
        avg_beta = results_df['beta'].mean()
        beta_std = results_df['beta'].std()

        prompt = f"""
Explain these rolling cointegration analysis results for stocks {', '.join(tickers)} to a non-technical investor:

Key Statistics:
- Stocks were cointegrated {pct_cointegrated:.1f}% of the time periods analyzed
- Average p-value: {avg_pvalue:.3f}
- Average hedge ratio: {avg_beta:.3f} ± {beta_std:.3f}
- Total number of stocks: {len(tickers)}

Please explain:
1. What this means for the relationship between these stocks
2. Whether this indicates a stable or unstable relationship
3. Implications for portfolio diversification and risk
4. Whether these stocks tend to move together or independently

Keep it under 200 words and avoid jargon.
"""
    else:
        # For baskets: use coint_rank based metrics
        avg_rank = results_df['coint_rank'].mean()
        pct_cointegrated = (results_df['coint_rank'] > 0).mean() * 100
        max_rank = results_df['coint_rank'].max()

        # Extract p-value and critical value information if available
        avg_pvalue = results_df['p_value_approx'].mean() if 'p_value_approx' in results_df.columns else None
        avg_trace = results_df['trace_stat'].mean()
        avg_crit_95 = results_df['crit_val_95'].mean() if 'crit_val_95' in results_df.columns else None

        # Extract cointegrating vectors info
        vector_cols = [col for col in results_df.columns if '_v1' in col]
        has_vectors = len(vector_cols) > 0

        # Build hedge ratio info string
        hedge_info = ""
        if has_vectors:
            # Get average weights from first cointegrating vector when it exists
            coint_windows = results_df[results_df['coint_rank'] > 0]
            if len(coint_windows) > 0:
                avg_weights = {}
                for col in vector_cols:
                    stock = col.replace('_v1', '')
                    avg_weights[stock] = coint_windows[col].mean()

                hedge_info = "\n\nCointegrating Vector (average hedge ratios when cointegrated):\n"
                for stock, weight in avg_weights.items():
                    hedge_info += f"- {stock}: {weight:.3f}\n"

        pvalue_info = f"\n- Average approximate p-value: {avg_pvalue:.3f}" if avg_pvalue else ""
        trace_info = f"\n- Average trace statistic: {avg_trace:.2f}"
        crit_info = f"\n- Average 95% critical value: {avg_crit_95:.2f}" if avg_crit_95 else ""

        prompt = f"""
Explain these rolling cointegration analysis results for stocks {', '.join(tickers)} to a non-technical investor:

Key Statistics:
- Average cointegration rank: {avg_rank:.2f}
- Maximum cointegration rank observed: {max_rank}
- Stocks were cointegrated {pct_cointegrated:.1f}% of the time periods analyzed{pvalue_info}{trace_info}{crit_info}
- Total number of stocks: {len(tickers)}{hedge_info}

Please explain:
1. What this means for the relationship between these stocks
2. Whether this indicates a stable or unstable relationship (consider p-values and how often cointegration occurs)
3. If cointegrating vectors are provided, explain what the hedge ratios mean for portfolio construction
4. Implications for portfolio diversification and risk
5. Whether these stocks tend to move together or independently

Keep it under 250 words and avoid excessive jargon, but be specific about the statistical findings.
"""

    return _call_gpt4o_mini(prompt, max_tokens=400)


def interpret_basket_cointegration(summary_df: pd.DataFrame) -> str:
    """
    Interpret basket-level cointegration test results.

    Args:
        summary_df: Summary DataFrame from test_basket_cointegration

    Returns:
        Plain English interpretation of the results
    """
    cointegrated = summary_df[summary_df['Coint_Rank'] > 0]
    total_baskets = len(summary_df)
    cointegrated_count = len(cointegrated)

    # Format basket info
    basket_info = []
    for _, row in summary_df.iterrows():
        basket_info.append(
            f"- {row['Basket']}: Rank {row['Coint_Rank']}, "
            f"{row['Num_Stocks']} stocks, p-value {row['P_Value']:.3f}"
        )

    basket_details = "\n".join(basket_info[:10])  # Limit to first 10

    prompt = f"""
Explain these cointegration test results for multiple stock baskets to a non-technical investor:

Overall Summary:
- Total baskets analyzed: {total_baskets}
- Baskets showing cointegration: {cointegrated_count}

Basket Details:
{basket_details}

Please explain:
1. What cointegration rank means (higher = stronger relationship)
2. Which baskets show the strongest relationships
3. What this means for portfolio construction
4. Practical implications for an investor

Keep it under 200 words and use simple language.
"""

    return _call_gpt4o_mini(prompt, max_tokens=400)


def interpret_spread_stability(stability_df: pd.DataFrame, tickers: List[str]) -> str:
    """
    Interpret spread stability analysis results.

    Args:
        stability_df: DataFrame from analyze_spread_stability
        tickers: List of the two ticker symbols

    Returns:
        Plain English interpretation of hedge ratio stability
    """
    avg_hedge = stability_df['hedge_ratio'].mean()
    std_hedge = stability_df['hedge_ratio'].std()
    min_hedge = stability_df['hedge_ratio'].min()
    max_hedge = stability_df['hedge_ratio'].max()

    # Calculate coefficient of variation as stability metric
    cv = (std_hedge / avg_hedge) * 100 if avg_hedge != 0 else 0

    prompt = f"""
Explain this hedge ratio stability analysis for stocks {tickers[0]} and {tickers[1]} to a non-technical investor:

Hedge Ratio Statistics:
- Average hedge ratio: {avg_hedge:.3f}
- Standard deviation: {std_hedge:.3f}
- Range: {min_hedge:.3f} to {max_hedge:.3f}
- Coefficient of variation: {cv:.1f}%

Please explain:
1. What a hedge ratio means in simple terms (e.g., "For every $1 of {tickers[0]}, you need $X of {tickers[1]}")
2. Whether this ratio is stable or varies a lot over time
3. What stability/instability means for pairs trading or hedging
4. Whether this relationship is reliable for trading

Keep it under 150 words and avoid technical jargon.
"""

    return _call_gpt4o_mini(prompt, max_tokens=350)


def interpret_pairs(pairs_df: pd.DataFrame, basket_name: str = "the basket") -> str:
    """
    Interpret cointegrated pairs found within a basket.

    Args:
        pairs_df: DataFrame from find_cointegrated_pairs
        basket_name: Name of the basket being analyzed

    Returns:
        Plain English interpretation of the pairs found
    """
    if len(pairs_df) == 0:
        return f"No cointegrated pairs were found in {basket_name} at the specified significance level."

    # Get top 5 pairs by p-value
    top_pairs = pairs_df.nsmallest(5, 'p_value')

    pair_details = []
    for _, row in top_pairs.iterrows():
        pair_details.append(
            f"- {row['Stock_1']} & {row['Stock_2']}: "
            f"p-value {row['p_value']:.4f}, hedge ratio {row['hedge_ratio']:.3f}"
        )

    pair_info = "\n".join(pair_details)

    prompt = f"""
Explain these cointegrated stock pairs found in {basket_name} to a non-technical investor:

Total pairs found: {len(pairs_df)}

Top pairs by statistical significance:
{pair_info}

Please explain:
1. What it means for two stocks to be "cointegrated"
2. Which pairs show the strongest relationship (lower p-value = stronger)
3. Practical trading or hedging opportunities
4. Why investors might care about these relationships

Keep it under 200 words and use simple language.
"""

    return _call_gpt4o_mini(prompt, max_tokens=400)


def interpret_pair_cointegration(
    ticker1: str,
    ticker2: str,
    score: float,
    p_value: float,
    hedge_ratio: float
) -> str:
    """
    Interpret single pair cointegration test results.

    Args:
        ticker1: First stock ticker
        ticker2: Second stock ticker
        score: ADF test statistic
        p_value: P-value from the test
        hedge_ratio: Calculated hedge ratio (beta)

    Returns:
        Plain English interpretation
    """
    is_cointegrated = p_value < 0.05
    strength = "strong" if p_value < 0.01 else "moderate" if p_value < 0.05 else "weak"

    prompt = f"""
Explain this cointegration test result for stocks {ticker1} and {ticker2} to a non-technical investor:

Test Results:
- P-value: {p_value:.4f}
- Test statistic: {score:.3f}
- Hedge ratio: {hedge_ratio:.3f}
- Cointegrated (p < 0.05): {'Yes' if is_cointegrated else 'No'}
- Relationship strength: {strength}

Please explain:
1. Whether these two stocks have a meaningful statistical relationship
2. What the hedge ratio tells us (e.g., "For every $1 of {ticker1}, you'd need ${hedge_ratio:.2f} of {ticker2}")
3. What this means practically for an investor
4. Whether this relationship is reliable enough for trading strategies

Keep it under 150 words and avoid technical terms.
"""

    return _call_gpt4o_mini(prompt, max_tokens=350)


def interpret_summary_stats(
    tickers: List[str],
    mean_returns: Dict[str, float],
    volatilities: Dict[str, float],
    correlations: pd.DataFrame
) -> str:
    """
    Interpret basic portfolio statistics.

    Args:
        tickers: List of ticker symbols
        mean_returns: Dictionary of ticker -> annualized return
        volatilities: Dictionary of ticker -> annualized volatility
        correlations: Correlation matrix

    Returns:
        Plain English interpretation
    """
    # Format statistics
    stats_lines = []
    for ticker in tickers:
        stats_lines.append(
            f"- {ticker}: {mean_returns[ticker]*100:.1f}% return, "
            f"{volatilities[ticker]*100:.1f}% volatility"
        )

    stats_info = "\n".join(stats_lines)
    avg_correlation = correlations.values[correlations.values != 1].mean()

    prompt = f"""
Explain these portfolio statistics to a non-technical investor:

Individual Stock Performance:
{stats_info}

Average correlation between stocks: {avg_correlation:.2f}

Please explain:
1. Which stocks performed best and which were most volatile
2. What the correlation means for diversification
3. Whether this is a well-diversified portfolio
4. Any risks or opportunities based on these statistics

Keep it under 200 words and use simple language.
"""

    return _call_gpt4o_mini(prompt, max_tokens=400)
