import os
import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint

tickers = [
    "AMD", "NVDA", "AVGO", "MU", "INTC", "TSM", "QCOM", "MRVL", "ADI", "NET",
    "SNOW", "CRM", "AMZN", "MSFT", "GOOGL", "DDOG", "ESTC", "DOCN", "PLTR", "MDB", 
    "OKTA", "CRWD", "ZS", "PANW", "S", "FTNT", "CYBR", "APP", "U",
    "TTD", "ROKU", "PINS", "SNAP", "PUBM", "CFLT", "GTLB", "FROG", "PD",
    "NBIS", "CRWV", "ORCL"
]

# Download all data at once
data = yf.download(tickers, period="1y")[['Close']]

# Clean data - remove rows with any NaN values
data = data.dropna()

# Convert to log prices
log_prices = np.log(data)

# Save to CSV
log_prices.to_csv("data/log_price_data.csv")

# Create empty matrix for p-values
n_stocks = len(tickers)
pvalue_matrix = pd.DataFrame(index=tickers, columns=tickers)

# Test all pairs
for i, stock1 in enumerate(tickers):
    for j, stock2 in enumerate(tickers):
        if i != j:
            prices1 = log_prices[('Close', stock1)]
            prices2 = log_prices[('Close', stock2)]
            _, pvalue, _ = coint(prices1, prices2)
            pvalue_matrix.loc[stock1, stock2] = pvalue
        else:
            pvalue_matrix.loc[stock1, stock2] = 0  # Self-cointegration

print(pvalue_matrix)
# Save p-value matrix to CSV
pvalue_matrix.to_csv("data/cointegration_pvalues.csv")