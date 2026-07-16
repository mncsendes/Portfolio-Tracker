import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Page title
st.set_page_config(page_title="My Portfolio Tracker", layout="wide")
st.title("📊 My Personal Portfolio Dashboard")

# Stock tickers (you can change these later)
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "VOO"]

# Download data
st.subheader("📈 Stock Performance (Last 3 Months)")
data = yf.download(tickers, period="3mo")["Close"]

# Show the latest prices in a table
st.write("### Latest Prices")
st.dataframe(data.iloc[-1:].T.rename(columns={data.index[-1]: "Price ($)"}))

# Plot the chart
fig, ax = plt.subplots(figsize=(12, 6))
data.plot(ax=ax)
ax.set_title("Stock Price Trends")
ax.set_xlabel("Date")
ax.set_ylabel("Price ($)")
ax.grid(True)
st.pyplot(fig)

# Calculate your portfolio value (customize these numbers later)
st.subheader("💰 Your Portfolio Value")
shares = {"AAPL": 10, "MSFT": 5, "GOOGL": 3, "NVDA": 2, "VOO": 8}
latest_prices = data.iloc[-1]
total_value = sum(shares[ticker] * latest_prices[ticker] for ticker in shares)

st.metric("Total Portfolio Value", f"${total_value:,.2f}")

# Show breakdown
st.write("### Breakdown by Stock")
breakdown = pd.DataFrame({
    "Shares": shares,
    "Price": latest_prices,
    "Value": [shares[t] * latest_prices[t] for t in shares]
})
st.dataframe(breakdown)

st.caption("Built with ❤️ using Python + Streamlit")