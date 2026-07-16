import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import time

# Page title
st.set_page_config(page_title="My Portfolio Tracker", layout="wide")
st.title("📊 My Personal Portfolio Dashboard")

# Stock tickers
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "VOO"]

# Add a small delay to avoid rate limiting
st.info("Fetching latest data...")
time.sleep(1)

# Download data with error handling
try:
    data = yf.download(tickers, period="3mo", group_by="ticker", progress=False)
    
    # Check if data is empty
    if data.empty:
        st.error("No data downloaded. Trying alternative method...")
        # Alternative: download one by one
        data = pd.DataFrame()
        for ticker in tickers:
            temp = yf.download(ticker, period="3mo", progress=False)["Close"]
            data[ticker] = temp
        data = data.dropna()
    
    # Check again
    if data.empty:
        st.error("Still unable to download data. Please try again in a few minutes.")
        st.stop()
    
    # Show latest prices
    st.subheader("📈 Stock Performance (Last 3 Months)")
    latest = data.iloc[-1]
    st.write("### Latest Prices")
    st.dataframe(latest.to_frame("Price ($)"))
    
    # Plot the chart
    fig, ax = plt.subplots(figsize=(12, 6))
    data.plot(ax=ax)
    ax.set_title("Stock Price Trends")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.grid(True)
    st.pyplot(fig)
    
    # Portfolio value
    st.subheader("💰 Your Portfolio Value")
    shares = {"AAPL": 10, "MSFT": 5, "GOOGL": 3, "NVDA": 2, "VOO": 8}
    latest_prices = data.iloc[-1]
    total_value = sum(shares[ticker] * latest_prices[ticker] for ticker in shares)
    
    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    
    # Breakdown
    st.write("### Breakdown by Stock")
    breakdown = pd.DataFrame({
        "Shares": shares,
        "Price": latest_prices,
        "Value": [shares[t] * latest_prices[t] for t in shares]
    })
    st.dataframe(breakdown)
    
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Try refreshing in a few minutes. Yahoo Finance sometimes blocks requests.")

st.caption("Built with ❤️ using Python + Streamlit")
