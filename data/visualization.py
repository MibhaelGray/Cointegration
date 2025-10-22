"""
Visualization functions for cointegration analysis results.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os


def plot_price_series(data, title=None, figsize=(12, 6), save_path=None):
    """
    Plot price series for multiple stocks.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data
    title : str, optional
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    plt.figure(figsize=figsize)
    for col in data.columns:
        plt.plot(data.index, data[col], label=col, linewidth=2, alpha=0.8)

    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Log Price', fontsize=11)

    if title is None:
        title = f"{', '.join(data.columns)} - Log Prices"

    plt.title(title, fontsize=13, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_rolling_pair_results(results_df, tickers, window=252, step_size=21, figsize=(14, 9), save_path=None):
    """
    Plot rolling cointegration results for a pair.

    Parameters:
    -----------
    results_df : pd.DataFrame
        Results from rolling_cointegration_analysis
    tickers : list
        List of 2 tickers
    window : int
        Window size used (for title)
    step_size : int
        Step size used (for title)
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

    # P-value plot
    ax1.plot(results_df.index, results_df['p_value'], linewidth=2, color='steelblue')
    ax1.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='p=0.05 threshold')
    ax1.fill_between(results_df.index, 0, 0.05, alpha=0.2, color='green', label='Cointegrated')
    ax1.set_ylabel('P-value', fontsize=11)
    ax1.set_title(f'Rolling Cointegration: {" vs ".join(tickers)} ({window}d window, {step_size}d step)',
                 fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Beta plot
    ax2.plot(results_df.index, results_df['beta'], linewidth=2, color='purple')
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Beta (Hedge Ratio)', fontsize=11)
    ax2.set_title('Rolling Beta/Hedge Ratio', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_rolling_basket_results(results_df, tickers, window=252, step_size=21, figsize=(14, 9), save_path=None):
    """
    Plot rolling cointegration results for a basket.

    Parameters:
    -----------
    results_df : pd.DataFrame
        Results from rolling_cointegration_analysis
    tickers : list
        List of tickers
    window : int
        Window size used (for title)
    step_size : int
        Step size used (for title)
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

    # Trace statistic
    ax1.plot(results_df.index, results_df['trace_stat'], linewidth=2, color='steelblue')
    ax1.set_ylabel('Trace Statistic', fontsize=11)
    ax1.set_title(f'Rolling Cointegration: {", ".join(tickers)} ({window}d window, {step_size}d step)',
                 fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Cointegration rank
    ax2.plot(results_df.index, results_df['coint_rank'], linewidth=2, color='green',
            marker='o', markersize=4)
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Cointegration Rank', fontsize=11)
    ax2.set_title('Number of Cointegrating Relationships', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-0.5, len(tickers) + 0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_rolling_results(results_df, tickers, window=252, step_size=21, figsize=(14, 9), save_path=None):
    """
    Automatically detect type and plot rolling cointegration results.

    Parameters:
    -----------
    results_df : pd.DataFrame
        Results from rolling_cointegration_analysis
    tickers : list
        List of tickers
    window : int
        Window size used (for title)
    step_size : int
        Step size used (for title)
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    is_pair = 'p_value' in results_df.columns

    if is_pair:
        plot_rolling_pair_results(results_df, tickers, window, step_size, figsize, save_path)
    else:
        plot_rolling_basket_results(results_df, tickers, window, step_size, figsize, save_path)


def plot_spread(spread, title="Price Spread", figsize=(12, 5), save_path=None):
    """
    Plot the spread between two cointegrated stocks.

    Parameters:
    -----------
    spread : pd.Series
        The spread time series
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    plt.figure(figsize=figsize)
    plt.plot(spread.index, spread, linewidth=1.5, color='steelblue')
    plt.axhline(y=spread.mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    plt.axhline(y=spread.mean() + spread.std(), color='orange', linestyle='--', linewidth=1, alpha=0.7, label='+1 Std')
    plt.axhline(y=spread.mean() - spread.std(), color='orange', linestyle='--', linewidth=1, alpha=0.7, label='-1 Std')

    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Spread', fontsize=11)
    plt.title(title, fontsize=13, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_zscore(zscore, title="Spread Z-Score", figsize=(12, 5), save_path=None):
    """
    Plot the z-score of the spread with trading thresholds.

    Parameters:
    -----------
    zscore : pd.Series
        The z-score time series
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    plt.figure(figsize=figsize)
    plt.plot(zscore.index, zscore, linewidth=1.5, color='steelblue')

    # Add threshold lines
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    plt.axhline(y=2, color='red', linestyle='--', linewidth=2, label='Entry threshold (+2σ)')
    plt.axhline(y=-2, color='red', linestyle='--', linewidth=2, label='Entry threshold (-2σ)')
    plt.axhline(y=0.5, color='green', linestyle='--', linewidth=1, alpha=0.7, label='Exit threshold (±0.5σ)')
    plt.axhline(y=-0.5, color='green', linestyle='--', linewidth=1, alpha=0.7)

    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Z-Score', fontsize=11)
    plt.title(title, fontsize=13, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_cointegration_heatmap(summary_df, figsize=(10, 8), save_path=None):
    """
    Plot a heatmap of cointegration ranks across baskets.

    Parameters:
    -----------
    summary_df : pd.DataFrame
        Summary DataFrame with basket names and cointegration ranks
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    fig, ax = plt.subplots(figsize=figsize)

    # Create color map
    colors = ['white', 'lightgreen', 'green', 'darkgreen']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('coint', colors, N=n_bins)

    # Plot bars
    bars = ax.barh(summary_df['Basket'], summary_df['Coint_Rank'],
                   color=plt.cm.viridis(summary_df['Coint_Rank'] / summary_df['Coint_Rank'].max()))

    ax.set_xlabel('Cointegration Rank', fontsize=12)
    ax.set_ylabel('Basket', fontsize=12)
    ax.set_title('Cointegration Rank by Basket', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()


def plot_spread_analysis(data, hedge_ratio=None, zscore_window=20, figsize=(14, 10), save_path=None):
    """
    Comprehensive plot showing prices, spread, and z-score for a pair.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with 2 columns
    hedge_ratio : float, optional
        Hedge ratio (if None, will be calculated)
    zscore_window : int
        Window for z-score calculation
    figsize : tuple
        Figure size
    save_path : str, optional
        If provided, save plot to this path instead of displaying
    """
    from rolling_analysis import calculate_spread, calculate_zscore

    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks")

    # Calculate spread and z-score
    spread = calculate_spread(data, hedge_ratio)
    zscore = calculate_zscore(spread, window=zscore_window)

    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize)

    # Plot 1: Prices
    ax1.plot(data.index, data.iloc[:, 0], label=data.columns[0], linewidth=2)
    ax1.plot(data.index, data.iloc[:, 1], label=data.columns[1], linewidth=2)
    ax1.set_ylabel('Log Price', fontsize=11)
    ax1.set_title(f'Price Series: {" vs ".join(data.columns)}', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Spread
    ax2.plot(spread.index, spread, linewidth=1.5, color='steelblue')
    ax2.axhline(y=spread.mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    ax2.axhline(y=spread.mean() + spread.std(), color='orange', linestyle='--', alpha=0.7)
    ax2.axhline(y=spread.mean() - spread.std(), color='orange', linestyle='--', alpha=0.7)
    ax2.set_ylabel('Spread', fontsize=11)
    ax2.set_title('Price Spread', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Z-Score
    ax3.plot(zscore.index, zscore, linewidth=1.5, color='steelblue')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax3.axhline(y=2, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax3.axhline(y=-2, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax3.set_xlabel('Date', fontsize=11)
    ax3.set_ylabel('Z-Score', fontsize=11)
    ax3.set_title(f'Spread Z-Score ({zscore_window}d window)', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved plot to {save_path}")
        plt.close()
    else:
        plt.show()
