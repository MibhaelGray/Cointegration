"""
Backtesting framework for pairs trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def backtest_pairs_strategy(
    data: pd.DataFrame,
    hedge_ratio: float,
    entry_zscore: float = 2.0,
    exit_zscore: float = 0.5,
    stop_loss_zscore: float = 4.0,
    transaction_cost: float = 0.001,
    initial_capital: float = 100000
) -> Dict:
    """
    Backtest a z-score based pairs trading strategy.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data with exactly 2 columns (log prices)
    hedge_ratio : float
        Hedge ratio (beta) for the pair
    entry_zscore : float
        Z-score threshold for entering positions (default 2.0)
    exit_zscore : float
        Z-score threshold for exiting positions (default 0.5)
    stop_loss_zscore : float
        Z-score threshold for stop loss (default 4.0)
    transaction_cost : float
        Transaction cost as percentage (default 0.1% = 0.001)
    initial_capital : float
        Starting capital (default $100,000)

    Returns:
    --------
    dict
        Backtesting results including trades, returns, and performance metrics
    """
    if len(data.columns) != 2:
        raise ValueError("Data must contain exactly 2 stocks")

    # Calculate spread and z-score
    spread = data.iloc[:, 0] - hedge_ratio * data.iloc[:, 1]
    spread_mean = spread.mean()
    spread_std = spread.std()
    zscore = (spread - spread_mean) / spread_std

    # Initialize tracking variables
    position = 0  # 0 = no position, 1 = long spread, -1 = short spread
    entry_price = 0
    entry_zscore_val = 0
    trades = []
    equity_curve = [initial_capital]
    current_capital = initial_capital

    # Track actual prices for position sizing
    price_a = np.exp(data.iloc[:, 0])  # Convert log prices back
    price_b = np.exp(data.iloc[:, 1])

    for i in range(1, len(data)):
        current_zscore = zscore.iloc[i]
        prev_zscore = zscore.iloc[i-1]

        # Entry logic
        if position == 0:
            # Enter long spread (buy A, sell B) when z-score is very negative
            if current_zscore < -entry_zscore:
                position = 1
                entry_zscore_val = current_zscore
                entry_price = spread.iloc[i]

                # Calculate position sizes (dollar-neutral)
                capital_per_leg = current_capital / 2
                shares_a = capital_per_leg / price_a.iloc[i]
                shares_b = (capital_per_leg / price_b.iloc[i]) * hedge_ratio

                # Record entry
                trades.append({
                    'entry_date': data.index[i],
                    'entry_zscore': current_zscore,
                    'position_type': 'LONG_SPREAD',
                    'shares_a': shares_a,
                    'shares_b': shares_b,
                    'entry_price_a': price_a.iloc[i],
                    'entry_price_b': price_b.iloc[i],
                    'capital_allocated': current_capital
                })

            # Enter short spread (sell A, buy B) when z-score is very positive
            elif current_zscore > entry_zscore:
                position = -1
                entry_zscore_val = current_zscore
                entry_price = spread.iloc[i]

                # Calculate position sizes
                capital_per_leg = current_capital / 2
                shares_a = capital_per_leg / price_a.iloc[i]
                shares_b = (capital_per_leg / price_b.iloc[i]) * hedge_ratio

                trades.append({
                    'entry_date': data.index[i],
                    'entry_zscore': current_zscore,
                    'position_type': 'SHORT_SPREAD',
                    'shares_a': shares_a,
                    'shares_b': shares_b,
                    'entry_price_a': price_a.iloc[i],
                    'entry_price_b': price_b.iloc[i],
                    'capital_allocated': current_capital
                })

        # Exit logic
        elif position != 0:
            exit_triggered = False
            exit_reason = None

            # Take profit: mean reversion occurred
            if position == 1 and current_zscore > -exit_zscore:
                exit_triggered = True
                exit_reason = 'TAKE_PROFIT'
            elif position == -1 and current_zscore < exit_zscore:
                exit_triggered = True
                exit_reason = 'TAKE_PROFIT'

            # Stop loss: spread moved against us
            elif position == 1 and current_zscore < -stop_loss_zscore:
                exit_triggered = True
                exit_reason = 'STOP_LOSS'
            elif position == -1 and current_zscore > stop_loss_zscore:
                exit_triggered = True
                exit_reason = 'STOP_LOSS'

            if exit_triggered:
                # Calculate P&L
                trade = trades[-1]
                exit_price_a = price_a.iloc[i]
                exit_price_b = price_b.iloc[i]

                if position == 1:  # Long spread
                    pnl_a = trade['shares_a'] * (exit_price_a - trade['entry_price_a'])
                    pnl_b = -trade['shares_b'] * (exit_price_b - trade['entry_price_b'])
                else:  # Short spread
                    pnl_a = -trade['shares_a'] * (exit_price_a - trade['entry_price_a'])
                    pnl_b = trade['shares_b'] * (exit_price_b - trade['entry_price_b'])

                gross_pnl = pnl_a + pnl_b

                # Apply transaction costs (4 transactions: entry buy/sell + exit buy/sell)
                costs = trade['capital_allocated'] * transaction_cost * 4
                net_pnl = gross_pnl - costs

                # Update capital
                current_capital += net_pnl

                # Record exit
                trade['exit_date'] = data.index[i]
                trade['exit_zscore'] = current_zscore
                trade['exit_price_a'] = exit_price_a
                trade['exit_price_b'] = exit_price_b
                trade['gross_pnl'] = gross_pnl
                trade['costs'] = costs
                trade['net_pnl'] = net_pnl
                trade['return_pct'] = (net_pnl / trade['capital_allocated']) * 100
                trade['holding_days'] = (data.index[i] - trade['entry_date']).days
                trade['exit_reason'] = exit_reason

                # Reset position
                position = 0

        # Update equity curve
        if position == 0:
            equity_curve.append(current_capital)
        else:
            # Mark to market current position
            trade = trades[-1]
            if position == 1:
                mtm_pnl = (
                    trade['shares_a'] * (price_a.iloc[i] - trade['entry_price_a']) +
                    -trade['shares_b'] * (price_b.iloc[i] - trade['entry_price_b'])
                )
            else:
                mtm_pnl = (
                    -trade['shares_a'] * (price_a.iloc[i] - trade['entry_price_a']) +
                    trade['shares_b'] * (price_b.iloc[i] - trade['entry_price_b'])
                )
            equity_curve.append(current_capital + mtm_pnl)

    # Close any open position at the end
    if position != 0:
        trade = trades[-1]
        trade['exit_date'] = data.index[-1]
        trade['exit_zscore'] = zscore.iloc[-1]
        trade['exit_price_a'] = price_a.iloc[-1]
        trade['exit_price_b'] = price_b.iloc[-1]
        trade['exit_reason'] = 'END_OF_PERIOD'

        if position == 1:
            pnl_a = trade['shares_a'] * (trade['exit_price_a'] - trade['entry_price_a'])
            pnl_b = -trade['shares_b'] * (trade['exit_price_b'] - trade['entry_price_b'])
        else:
            pnl_a = -trade['shares_a'] * (trade['exit_price_a'] - trade['entry_price_a'])
            pnl_b = trade['shares_b'] * (trade['exit_price_b'] - trade['entry_price_b'])

        gross_pnl = pnl_a + pnl_b
        costs = trade['capital_allocated'] * transaction_cost * 4
        net_pnl = gross_pnl - costs
        current_capital += net_pnl

        trade['gross_pnl'] = gross_pnl
        trade['costs'] = costs
        trade['net_pnl'] = net_pnl
        trade['return_pct'] = (net_pnl / trade['capital_allocated']) * 100
        trade['holding_days'] = (trade['exit_date'] - trade['entry_date']).days

    # Calculate performance metrics
    trades_df = pd.DataFrame(trades)
    equity_series = pd.Series(equity_curve, index=data.index)

    metrics = calculate_performance_metrics(
        trades_df, equity_series, initial_capital, len(data)
    )

    return {
        'trades': trades_df,
        'equity_curve': equity_series,
        'metrics': metrics,
        'parameters': {
            'hedge_ratio': hedge_ratio,
            'entry_zscore': entry_zscore,
            'exit_zscore': exit_zscore,
            'stop_loss_zscore': stop_loss_zscore,
            'transaction_cost': transaction_cost,
            'initial_capital': initial_capital
        }
    }


def calculate_performance_metrics(
    trades_df: pd.DataFrame,
    equity_curve: pd.Series,
    initial_capital: float,
    total_days: int
) -> Dict:
    """
    Calculate comprehensive performance metrics.

    Parameters:
    -----------
    trades_df : pd.DataFrame
        DataFrame containing all trades
    equity_curve : pd.Series
        Equity curve over time
    initial_capital : float
        Starting capital
    total_days : int
        Total number of days in backtest

    Returns:
    --------
    dict
        Performance metrics
    """
    if len(trades_df) == 0:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_return': 0,
            'total_return_pct': 0,
            'annual_return_pct': 0,
            'sharpe_ratio': 0,
            'calmar_ratio': 0,
            'max_drawdown_pct': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'avg_return_per_trade': 0,
            'avg_holding_days': 0,
            'profit_factor': 0,
            'avg_win_loss_ratio': 0
        }

    # Basic metrics
    final_capital = equity_curve.iloc[-1]
    total_return = final_capital - initial_capital
    total_return_pct = (total_return / initial_capital) * 100

    # Returns
    returns = equity_curve.pct_change().dropna()
    avg_return = returns.mean()
    std_return = returns.std()

    # Sharpe ratio (annualized)
    sharpe_ratio = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

    # Maximum drawdown
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = drawdown.min() * 100

    # Trade statistics
    completed_trades = trades_df[trades_df['net_pnl'].notna()]
    if len(completed_trades) > 0:
        wins = completed_trades[completed_trades['net_pnl'] > 0]
        losses = completed_trades[completed_trades['net_pnl'] <= 0]

        win_rate = len(wins) / len(completed_trades) * 100
        avg_win = wins['net_pnl'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['net_pnl'].mean()) if len(losses) > 0 else 0
        avg_return_per_trade = completed_trades['return_pct'].mean()
        avg_holding_days = completed_trades['holding_days'].mean()

        # Profit factor
        total_wins = wins['net_pnl'].sum() if len(wins) > 0 else 0
        total_losses = abs(losses['net_pnl'].sum()) if len(losses) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else np.inf

        # Risk-adjusted metrics
        avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else np.inf

    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        avg_return_per_trade = 0
        avg_holding_days = 0
        profit_factor = 0
        avg_win_loss_ratio = 0

    # Calmar ratio (return / max drawdown)
    annual_return = (total_return_pct / total_days) * 252
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

    return {
        'total_trades': len(completed_trades),
        'winning_trades': len(wins) if len(completed_trades) > 0 else 0,
        'losing_trades': len(losses) if len(completed_trades) > 0 else 0,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'annual_return_pct': annual_return,
        'sharpe_ratio': sharpe_ratio,
        'calmar_ratio': calmar_ratio,
        'max_drawdown_pct': max_drawdown,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_return_per_trade': avg_return_per_trade,
        'avg_holding_days': avg_holding_days,
        'profit_factor': profit_factor,
        'avg_win_loss_ratio': avg_win_loss_ratio
    }


def optimize_parameters(
    data: pd.DataFrame,
    hedge_ratio: float,
    entry_zscores: list = [1.5, 2.0, 2.5],
    exit_zscores: list = [0.3, 0.5, 0.7],
    stop_loss_zscores: list = [3.0, 4.0, 5.0]
) -> pd.DataFrame:
    """
    Optimize trading parameters through grid search.

    Parameters:
    -----------
    data : pd.DataFrame
        Price data
    hedge_ratio : float
        Hedge ratio to use
    entry_zscores : list
        Entry thresholds to test
    exit_zscores : list
        Exit thresholds to test
    stop_loss_zscores : list
        Stop loss thresholds to test

    Returns:
    --------
    pd.DataFrame
        Results for all parameter combinations
    """
    results = []

    for entry_z in entry_zscores:
        for exit_z in exit_zscores:
            for stop_z in stop_loss_zscores:
                if exit_z < entry_z < stop_z:  # Logical constraint
                    backtest_result = backtest_pairs_strategy(
                        data, hedge_ratio, entry_z, exit_z, stop_z
                    )

                    metrics = backtest_result['metrics']
                    results.append({
                        'entry_zscore': entry_z,
                        'exit_zscore': exit_z,
                        'stop_loss_zscore': stop_z,
                        'total_return_pct': metrics['total_return_pct'],
                        'sharpe_ratio': metrics['sharpe_ratio'],
                        'max_drawdown_pct': metrics['max_drawdown_pct'],
                        'win_rate': metrics['win_rate'],
                        'total_trades': metrics['total_trades'],
                        'profit_factor': metrics['profit_factor']
                    })

    return pd.DataFrame(results).sort_values('sharpe_ratio', ascending=False)


def print_backtest_summary(backtest_results: Dict):
    """
    Print a formatted summary of backtest results.

    Parameters:
    -----------
    backtest_results : dict
        Results from backtest_pairs_strategy
    """
    metrics = backtest_results['metrics']
    params = backtest_results['parameters']

    print("\n" + "=" * 70)
    print("BACKTEST SUMMARY")
    print("=" * 70)

    print("\nSTRATEGY PARAMETERS:")
    print(f"  Entry Z-score Threshold: ±{params['entry_zscore']:.1f}")
    print(f"  Exit Z-score Threshold: ±{params['exit_zscore']:.1f}")
    print(f"  Stop Loss Z-score: ±{params['stop_loss_zscore']:.1f}")
    print(f"  Hedge Ratio: {params['hedge_ratio']:.4f}")
    print(f"  Transaction Cost: {params['transaction_cost']*100:.2f}%")
    print(f"  Initial Capital: ${params['initial_capital']:,.0f}")

    print("\nPERFORMANCE METRICS:")
    print(f"  Total Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")
    print(f"  Annualized Return: {metrics['annual_return_pct']:.2f}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"  Calmar Ratio: {metrics['calmar_ratio']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")

    print("\nTRADING STATISTICS:")
    print(f"  Total Trades: {metrics['total_trades']}")
    print(f"  Winning Trades: {metrics['winning_trades']}")
    print(f"  Losing Trades: {metrics['losing_trades']}")
    print(f"  Win Rate: {metrics['win_rate']:.1f}%")
    print(f"  Average Win: ${metrics['avg_win']:,.2f}")
    print(f"  Average Loss: ${metrics['avg_loss']:,.2f}")
    print(f"  Win/Loss Ratio: {metrics['avg_win_loss_ratio']:.2f}")
    print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"  Avg Return per Trade: {metrics['avg_return_per_trade']:.2f}%")
    print(f"  Avg Holding Period: {metrics['avg_holding_days']:.1f} days")

    print("\n" + "=" * 70)
