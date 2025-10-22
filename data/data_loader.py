"""
Data loading and downloading utilities for stock price data.
"""

import os
import warnings
import yfinance as yf
import pandas as pd
import numpy as np

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


def get_close_price_data(tickers, period="1y", max_missing=25, log_prices=True, save_csv=True):
    """
    Download close prices for a list of tickers and optionally save to CSV.

    Parameters:
    -----------
    tickers : list
        List of stock tickers
    period : str
        Time period ("1y", "2y", "6mo", etc.)
    max_missing : int
        Maximum missing values allowed per stock
    log_prices : bool
        Convert to log prices (default True)
    save_csv : bool
        Save to CSV file (default True)

    Returns:
    --------
    pd.DataFrame
        Close prices (log-transformed if specified)
    """
    try:
        print(f"Downloading close prices for {len(tickers)} stocks...")

        # Download data with auto_adjust=True to suppress warning
        data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

        # Handle single ticker case
        if len(tickers) == 1:
            close_data = data[["Close"]].copy()
            close_data.columns = tickers
        else:
            close_data = data["Close"].copy()

        # Drop stocks with too many missing values
        missing = close_data.isnull().sum()
        stocks_to_drop = missing[missing > max_missing].index.tolist()

        if stocks_to_drop:
            print(f"  Dropping {len(stocks_to_drop)} stocks with >{max_missing} missing values: {stocks_to_drop}")
            close_data = close_data.drop(stocks_to_drop, axis=1)

        # Forward fill remaining missing values
        close_data = close_data.ffill()

        # Apply log transformation
        if log_prices:
            close_data = np.log(close_data)

        # Save to CSV with ticker names in filename
        if save_csv:
            filename = "_".join(close_data.columns.tolist()) + ".csv"
            close_data.to_csv(filename)
            print(f"  Saved to {filename}")

        print(f"  Final dataset: {len(close_data.columns)} stocks, {len(close_data)} days\n")

        return close_data

    except Exception as e:
        print(f"  Error: {e}\n")
        return None


def download_all_baskets(basket_list, period="1y", max_missing=25):
    """
    Download close prices for all baskets in the list.

    Parameters:
    -----------
    basket_list : list
        List of baskets (each basket is a list of tickers)
    period : str
        Time period for download
    max_missing : int
        Maximum missing values allowed per stock

    Returns:
    --------
    dict
        Dictionary mapping basket names to DataFrames
    """
    all_data = {}

    for i, basket in enumerate(basket_list, 1):
        print(f"Basket {i}/{len(basket_list)}:")
        data = get_close_price_data(basket, period=period, max_missing=max_missing)
        if data is not None:
            basket_name = "_".join(data.columns.tolist())
            all_data[basket_name] = data

    print(f"\nDownload complete: {len(all_data)} baskets saved")
    return all_data


def load_all_csv(folder_path="."):
    """
    Load all basket CSVs from folder into a dictionary of DataFrames.

    Parameters:
    -----------
    folder_path : str
        Path to folder containing CSV files

    Returns:
    --------
    dict
        Dictionary mapping basket names to DataFrames
    """
    dfs = {}
    for file in os.listdir(folder_path):
        if file.endswith('.csv') and '_' in file and file != 'data.csv':
            basket_name = file.replace('.csv', '')
            df = pd.read_csv(os.path.join(folder_path, file), index_col=0, parse_dates=True)
            dfs[basket_name] = df
    print(f"Loaded {len(dfs)} baskets from CSV files")
    return dfs


def load_basket_csv(basket_name, folder_path="."):
    """
    Load a specific basket CSV file.

    Parameters:
    -----------
    basket_name : str
        Name of the basket (without .csv extension)
    folder_path : str
        Path to folder containing CSV file

    Returns:
    --------
    pd.DataFrame
        Price data for the basket
    """
    file_path = os.path.join(folder_path, f"{basket_name}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path, index_col=0, parse_dates=True)
    else:
        print(f"File not found: {file_path}")
        return None
