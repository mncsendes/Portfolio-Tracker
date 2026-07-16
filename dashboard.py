import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="My Portfolio Tracker", layout="wide")
st.title("📊 My Personal Portfolio Dashboard")

# API KEY
API_KEY = "JP7LLLD9RTL1U2EY" 

# Stock tickers to track
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "VOO"]
data = pd.DataFrame()

# ---------- DATA FETCHING ----------
st.info("Fetching data... This may take 15-20 seconds.")

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
        
        time.sleep(1)
        
    except Exception as e:
        st.warning(f"Error loading {ticker}: {str(e)}")

# ---------- IF DATA LOADED ----------
if not data.empty:
    st.success(f"✅ Loaded {len(data.columns)} stocks!")
    
    # Show the chart
    st.subheader("📈 Stock Performance")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    data.plot(ax=ax)
    ax.set_title("Stock Price Trends")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.grid(True)
    st.pyplot(fig)
    
    # ---------- PORTFOLIO INPUT SECTION ----------
    st.subheader("💰 Your Portfolio Value")
    
    # Get the latest prices
    latest_prices = data.iloc[-1]
    
    # Display current prices
    st.write("### Current Stock Prices")
    price_df = latest_prices.to_frame("Price ($)")
    st.dataframe(price_df)
    
    # ---------- INPUT FIELDS FOR SHARES ----------
    st.write("### Enter Your Share Counts")
    
    # Create input fields for each stock
    shares = {}
    cols = st.columns(len(tickers))
    
    for i, ticker in enumerate(tickers):
        with cols[i]:
            shares[ticker] = st.number_input(
                f"{ticker} shares",
                min_value=0,
                value=0,
                step=1,
                key=f"shares_{ticker}"
            )
    
    # Calculate portfolio if any shares are entered
    total_value = 0
    has_shares = False
    
    for ticker in shares:
        if shares[ticker] > 0:
            has_shares = True
            total_value += shares[ticker] * latest_prices[ticker]
    
    # ---------- SHOW RESULTS ----------
    if has_shares:
        st.success(f"### Total Portfolio Value: **${total_value:,.2f}**")
        
        # Breakdown table
        st.write("### Breakdown by Stock")
        breakdown_data = {
            "Ticker": [],
            "Shares": [],
            "Price ($)": [],
            "Value ($)": []
        }
        
        for ticker in shares:
            if shares[ticker] > 0:
                price = latest_prices[ticker]
                value = shares[ticker] * price
                breakdown_data["Ticker"].append(ticker)
                breakdown_data["Shares"].append(shares[ticker])
                breakdown_data["Price ($)"].append(f"${price:.2f}")
                breakdown_data["Value ($)"].append(f"${value:.2f}")
        
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df)
        
    else:
        st.info("💡 Enter your share counts above to see your portfolio value.")
    
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
