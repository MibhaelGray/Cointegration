"""
Parameter validation for backtesting to ensure valid configurations.
"""


def validate_backtest_parameters(
    period: str,
    data_length: int,
    window: int,
    step_size: int,
    backtest_method: str = "walk_forward",
    train_window: int = None,
    test_window: int = None,
    zscore_window: int = 20
) -> dict:
    """
    Validate that backtest parameters are compatible with the data.

    Parameters:
    -----------
    period : str
        Time period string (e.g., "1y", "2y", "6mo")
    data_length : int
        Actual number of days of data
    window : int
        Rolling cointegration window
    step_size : int
        Step size for rolling analysis
    backtest_method : str
        "walk_forward", "train_test_split", or "simple"
    train_window : int, optional
        Training window for walk-forward
    test_window : int, optional
        Testing window for walk-forward
    zscore_window : int
        Z-score calculation window

    Returns:
    --------
    dict
        Validation results with 'valid', 'warnings', and 'errors'
    """
    results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'recommendations': []
    }

    # Parse period to estimate expected days
    period_to_days = {
        '1mo': 21, '2mo': 42, '3mo': 63, '6mo': 126,
        '1y': 252, '2y': 504, '5y': 1260, '10y': 2520
    }
    expected_days = period_to_days.get(period, data_length)

    # Check 1: Basic data requirements
    if data_length < 40:
        results['valid'] = False
        results['errors'].append(
            f"Insufficient data: {data_length} days. Need at least 40 days for backtesting."
        )

    # Check 2: Z-score window
    if zscore_window >= data_length:
        results['valid'] = False
        results['errors'].append(
            f"Z-score window ({zscore_window}) >= data length ({data_length})"
        )
    elif zscore_window < 10:
        results['warnings'].append(
            f"Z-score window ({zscore_window}) is small. Consider 20+ days for stability."
        )
    elif zscore_window > 60:
        results['warnings'].append(
            f"Z-score window ({zscore_window}) is large. May be slow to react to changes."
        )

    # Check 3: Rolling cointegration analysis
    if window >= data_length:
        results['valid'] = False
        results['errors'].append(
            f"Rolling window ({window}) >= data length ({data_length})"
        )
    elif window < 30:
        results['warnings'].append(
            f"Rolling window ({window}) is small. Cointegration tests may be unreliable with <30 days."
        )

    # Minimum for reliable cointegration: ~2x number of stocks, so for pairs, min ~20-30 days
    # But realistically 60+ is better
    if window < 60 and window >= 30:
        results['warnings'].append(
            f"Rolling window ({window}) is below recommended 60+ days. Results may be noisy."
        )

    # Check 4: Step size
    if step_size <= 0:
        results['valid'] = False
        results['errors'].append(f"Step size must be positive (got {step_size})")
    elif step_size >= window:
        results['warnings'].append(
            f"Step size ({step_size}) >= window ({window}). Windows won't overlap."
        )

    # Calculate number of rolling windows
    num_windows = (data_length - window) // step_size + 1
    if num_windows < 3:
        results['warnings'].append(
            f"Only {num_windows} rolling windows. Need 5+ for reliable stability analysis."
        )
        results['recommendations'].append(
            f"Increase data period or decrease step_size for more windows."
        )

    # Check 5: Walk-forward specific
    if backtest_method == "walk_forward":
        # Use adaptive values if not provided
        if train_window is None:
            train_window = min(252, data_length // 3)
        if test_window is None:
            test_window = min(63, data_length // 10)

        # Minimum requirements
        min_train = max(60, zscore_window * 3)  # Need enough data for z-scores
        min_test = max(20, zscore_window)  # Need at least one z-score window

        if train_window < min_train:
            results['warnings'].append(
                f"Train window ({train_window}) is small. Recommend {min_train}+ days."
            )

        if test_window < min_test:
            results['warnings'].append(
                f"Test window ({test_window}) is small. Recommend {min_test}+ days."
            )

        # Check total requirement
        min_total = train_window + test_window
        if min_total > data_length:
            results['valid'] = False
            results['errors'].append(
                f"Train window ({train_window}) + test window ({test_window}) = {min_total} "
                f"exceeds data length ({data_length})"
            )

        # Calculate number of walk-forward periods
        num_periods = (data_length - train_window) // step_size
        if num_periods < 1:
            results['valid'] = False
            results['errors'].append(
                f"Cannot create any walk-forward periods. Need more data or smaller windows."
            )
        elif num_periods < 3:
            results['warnings'].append(
                f"Only {num_periods} walk-forward periods. Need 5+ for robust testing."
            )
            results['recommendations'].append(
                f"Options: (1) Increase data period, (2) Decrease train_window, (3) Decrease step_size"
            )

        # Check ratio
        if train_window < test_window * 2:
            results['warnings'].append(
                f"Train window ({train_window}) should be 2-4x test window ({test_window}) for stability."
            )

    # Check 6: Train/test split
    elif backtest_method == "train_test_split":
        train_size = int(data_length * 0.6)
        test_size = data_length - train_size

        if train_size < max(60, zscore_window * 3):
            results['warnings'].append(
                f"Training period ({train_size} days) may be too short for reliable parameter estimation."
            )

        if test_size < max(30, zscore_window * 2):
            results['warnings'].append(
                f"Testing period ({test_size} days) may be too short for reliable performance evaluation."
            )

    # Check 7: Simple backtest
    elif backtest_method == "simple":
        if data_length < zscore_window * 5:
            results['warnings'].append(
                f"Data length ({data_length}) is only {data_length/zscore_window:.1f}x z-score window. "
                "Need 10x+ for meaningful results."
            )

    # Check 8: Overall data quality expectations
    if data_length < expected_days * 0.7:
        results['warnings'].append(
            f"Only {data_length} days retrieved for period '{period}' (expected ~{expected_days}). "
            "May have missing data or non-trading days."
        )

    # Recommendations based on data length
    if data_length < 100:
        results['recommendations'].append(
            "Consider using longer time period (6mo+) for more reliable backtesting."
        )
    elif data_length < 200:
        results['recommendations'].append(
            "Data is adequate but consider 1y+ for walk-forward testing."
        )

    return results


def print_validation_results(results: dict):
    """Print validation results in a user-friendly format."""
    print("\n" + "=" * 70)
    print("PARAMETER VALIDATION")
    print("=" * 70)

    if results['valid']:
        print("\n[VALID] Configuration is valid")
    else:
        print("\n[INVALID] Configuration is INVALID - cannot proceed")

    if results['errors']:
        print("\nERRORS (must fix):")
        for i, error in enumerate(results['errors'], 1):
            print(f"  {i}. {error}")

    if results['warnings']:
        print("\nWARNINGS (review recommended):")
        for i, warning in enumerate(results['warnings'], 1):
            print(f"  {i}. {warning}")

    if results['recommendations']:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")

    if results['valid'] and not results['warnings']:
        print("\n[OK] No issues detected - configuration looks good!")

    print("=" * 70)


def suggest_parameters(data_length: int, backtest_method: str = "walk_forward") -> dict:
    """
    Suggest optimal parameters based on available data length.

    Parameters:
    -----------
    data_length : int
        Number of days of data available
    backtest_method : str
        Backtesting method to use

    Returns:
    --------
    dict
        Suggested parameters
    """
    suggestions = {
        'zscore_window': 20,
        'method': backtest_method
    }

    if backtest_method == "walk_forward":
        if data_length >= 500:
            # 2+ years: Use standard parameters
            suggestions['train_window'] = 252
            suggestions['test_window'] = 63
            suggestions['step_size'] = 21
            suggestions['rolling_window'] = 252
            suggestions['rolling_step'] = 21
            suggestions['note'] = "Standard configuration for 2+ years of data"

        elif data_length >= 300:
            # 1-2 years: Reduce windows proportionally
            suggestions['train_window'] = 180
            suggestions['test_window'] = 45
            suggestions['step_size'] = 15
            suggestions['rolling_window'] = 126
            suggestions['rolling_step'] = 21
            suggestions['note'] = "Adjusted for 1-2 years of data"

        elif data_length >= 150:
            # 6mo-1yr: Smaller windows
            suggestions['train_window'] = 90
            suggestions['test_window'] = 30
            suggestions['step_size'] = 10
            suggestions['rolling_window'] = 63
            suggestions['rolling_step'] = 10
            suggestions['note'] = "Minimum viable for walk-forward (6mo-1yr data)"

        else:
            # <6 months: Recommend different method
            suggestions['method'] = "train_test_split"
            suggestions['note'] = f"Only {data_length} days - train/test split recommended instead of walk-forward"
            suggestions['train_pct'] = 0.6
            suggestions['rolling_window'] = max(30, data_length // 5)
            suggestions['rolling_step'] = max(5, data_length // 20)

    elif backtest_method == "train_test_split":
        suggestions['train_pct'] = 0.6
        suggestions['rolling_window'] = min(252, max(63, data_length // 4))
        suggestions['rolling_step'] = max(10, data_length // 20)
        suggestions['note'] = "Train/test split - simpler than walk-forward"

    else:  # simple
        suggestions['rolling_window'] = min(252, max(63, data_length // 3))
        suggestions['rolling_step'] = max(10, data_length // 15)
        suggestions['note'] = "Simple backtest - ensure you understand the limitations"

    return suggestions


def print_suggested_parameters(suggestions: dict):
    """Print suggested parameters."""
    print("\n" + "=" * 70)
    print("SUGGESTED PARAMETERS")
    print("=" * 70)
    print(f"\n{suggestions['note']}\n")

    print("Recommended configuration:")
    for key, value in suggestions.items():
        if key != 'note':
            print(f"  {key}: {value}")

    print("\nExample usage:")
    if suggestions['method'] == 'walk_forward':
        print(f"""
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="...",  # Adjust to get sufficient data
    window={suggestions.get('rolling_window', 252)},
    step_size={suggestions.get('rolling_step', 21)},
    backtest_method="walk_forward"
)
""")
    else:
        print(f"""
results = comprehensive_cointegration_analysis(
    tickers=["STOCK_A", "STOCK_B"],
    period="...",
    window={suggestions.get('rolling_window', 126)},
    step_size={suggestions.get('rolling_step', 21)},
    backtest_method="{suggestions['method']}"
)
""")
    print("=" * 70)


if __name__ == "__main__":
    # Test various scenarios
    print("TESTING PARAMETER VALIDATION")
    print("=" * 70)

    # Scenario 1: Good configuration
    print("\n1. Good Configuration (2 years of data)")
    results = validate_backtest_parameters(
        period="2y",
        data_length=504,
        window=252,
        step_size=21,
        backtest_method="walk_forward",
        train_window=252,
        test_window=63,
        zscore_window=20
    )
    print_validation_results(results)

    # Scenario 2: Too little data
    print("\n2. Insufficient Data (3 months)")
    results = validate_backtest_parameters(
        period="3mo",
        data_length=63,
        window=252,
        step_size=21,
        backtest_method="walk_forward",
        train_window=252,
        test_window=63,
        zscore_window=20
    )
    print_validation_results(results)
    suggestions = suggest_parameters(63, "walk_forward")
    print_suggested_parameters(suggestions)

    # Scenario 3: Moderate data
    print("\n3. Moderate Data (1 year)")
    results = validate_backtest_parameters(
        period="1y",
        data_length=252,
        window=126,
        step_size=21,
        backtest_method="walk_forward",
        train_window=180,
        test_window=45,
        zscore_window=20
    )
    print_validation_results(results)
