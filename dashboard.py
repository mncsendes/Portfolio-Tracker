import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="My Portfolio Tracker", layout="wide")
st.title("📊 My Personal Portfolio Dashboard")

# API KEY FROM ALPHA VANTAGE
API_KEY = "JP7LLLD9RTL1U2EY" 

tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "VOO"]
data = pd.DataFrame()

st.info("Fetching data... This may take 15-20 seconds.")

# Fetch data for each ticker
for ticker in tickers:
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=compact"
        response = requests.get(url)
        json_data = response.json()
        
        if "Time Series (Daily)" in json_data:
            daily_data = json_data["Time Series (Daily)"]
            df = pd.DataFrame.from_dict(daily_data, orient="index")
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df["4. close"] = df["4. close"].astype(float)
            data[ticker] = df["4. close"]
        else:
            st.warning(f"Could not load {ticker}")
        
        time.sleep(1)  # Rate limit: 1 request per second
        
    except Exception as e:
        st.warning(f"Error loading {ticker}: {str(e)}")

if not data.empty:
    st.success(f"✅ Loaded {len(data.columns)} stocks!")
    
    st.subheader("📈 Stock Performance (Last 100 Days)")
    
    # Show latest prices
    latest = data.iloc[-1]
    st.write("### Latest Prices")
    st.dataframe(latest.to_frame("Price ($)"))
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    data.plot(ax=ax)
    ax.set_title("Stock Price Trends")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.grid(True)
    st.pyplot(fig)
    
    # Portfolio
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
    
    # Show data freshness
    st.caption(f"Data as of: {data.index[-1].strftime('%Y-%m-%d')}")
    
else:
    st.error("❌ Unable to load any stock data.")
    st.info("""
    **Troubleshooting:**
    1. Make sure you copied your API key correctly
    2. Alpha Vantage has a limit of 5 requests per minute—wait 60 seconds and refresh
    3. Check your internet connection
    """)

st.caption("Built with ❤️ using Python + Streamlit")
