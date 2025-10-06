import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.vector_ar.vecm import coint_johansen

# Your existing functions
def get_close_price_data(tickers, period="1y", max_missing=25, log_prices=True):
    try:
        data = yf.download(tickers, period=period, progress=False)
        close_data = data["Close"]
        missing = close_data.isnull().sum()
        close_data = close_data.drop(missing[missing > max_missing].index, axis=1)
        close_data = close_data.ffill()
        
        if log_prices:
            close_data = np.log(close_data)
        
        return close_data
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def analyze_basket(tickers, period="1y", crit_level=1, k_ar_diff=5):
    data = get_close_price_data(tickers, period=period)
    
    if data is None or len(data.columns) < 2:
        st.error("Insufficient data")
        return None, None, None
    
    result = coint_johansen(data, det_order=0, k_ar_diff=k_ar_diff)
    n_coint = sum(result.lr1 > result.cvt[:, crit_level])
    
    vectors = None
    if n_coint > 0:
        vectors = pd.DataFrame(
            result.evec[:, :n_coint],
            index=data.columns,
            columns=[f"Vector_{i+1}" for i in range(n_coint)]
        )
    
    return data, n_coint, vectors

# Streamlit App
st.title("Stock Basket Cointegration Analysis")

st.sidebar.header("Parameters")

# Ticker input
ticker_input = st.sidebar.text_input(
    "Enter tickers (comma-separated)", 
    "NET,SNOW,DDOG"
)
tickers = [t.strip().upper() for t in ticker_input.split(",")]

# Parameters
period = st.sidebar.selectbox(
    "Time Period",
    ["6mo", "1y", "2y", "5y"],
    index=1
)

crit_level = st.sidebar.selectbox(
    "Confidence Level",
    [("90%", 0), ("95%", 1), ("99%", 2)],
    index=1,
    format_func=lambda x: x[0]
)[1]

k_ar_diff = st.sidebar.slider("Lag Length", 1, 10, 5)

# Run analysis
if st.sidebar.button("Run Analysis"):
    with st.spinner("Analyzing..."):
        data, n_coint, vectors = analyze_basket(tickers, period, crit_level, k_ar_diff)
        
        if data is not None:
            # Display results
            st.subheader("Results")
            st.metric("Cointegration Rank", n_coint)
            
            if vectors is not None:
                st.subheader("Cointegrating Vectors")
                st.dataframe(vectors)
            else:
                st.info("No cointegrating relationships found")
            
            # Plot with better styling
            st.subheader("Log Prices")
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Use a nice color palette
            colors = plt.cm.Set2(range(len(data.columns)))
            
            for idx, col in enumerate(data.columns):
                ax.plot(data.index, data[col], label=col, linewidth=2.5, color=colors[idx])
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Log Price', fontsize=12, fontweight='bold')
            ax.set_title(f"{', '.join(tickers)} - Log Prices", fontsize=14, fontweight='bold', pad=20)
            ax.legend(fontsize=11, frameon=True, shadow=True, loc='best')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Better spacing
            plt.tight_layout()
            st.pyplot(fig)