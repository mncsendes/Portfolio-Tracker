import streamlit as st
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="My Portfolio Tracker", layout="wide")

# ---------- DARK MODE TOGGLE (FULL PAGE) ----------
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .css-1d391kg, .css-1lcbmhc, .stSidebar {
        background-color: #1E1E2E !important;
        color: #FAFAFA !important;
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #FAFAFA !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #2D2D44 !important;
        color: #FAFAFA !important;
        border-color: #444466 !important;
    }
    .stDataFrame, .dataframe {
        background-color: #1E1E2E !important;
        color: #FAFAFA !important;
    }
    .dataframe th {
        background-color: #2D2D44 !important;
        color: #FAFAFA !important;
    }
    .dataframe td {
        background-color: #1E1E2E !important;
        color: #FAFAFA !important;
    }
    .stButton button {
        background-color: #2D2D44 !important;
        color: #FAFAFA !important;
        border-color: #444466 !important;
    }
    .stButton button:hover {
        background-color: #3D3D5A !important;
    }
    .stAlert {
        background-color: #1E1E2E !important;
        color: #FAFAFA !important;
    }
    [data-testid="metric-container"] {
        background-color: #1E1E2E !important;
        color: #FAFAFA !important;
        border: 1px solid #444466 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("📊 My Personal Portfolio Dashboard")

# ---------- SIDEBAR: MANAGE STOCKS ----------
st.sidebar.header("📊 Manage Stocks")

if "tickers" not in st.session_state:
    st.session_state.tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "VOO"]

new_ticker = st.sidebar.text_input("Add a stock ticker (e.g., AMZN)", value="").upper()
if st.sidebar.button("➕ Add Stock") and new_ticker:
    if new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
        st.sidebar.success(f"✅ Added {new_ticker}!")
        st.cache_data.clear()  # Clear cache so new stock gets fetched
        time.sleep(0.5)
        st.rerun()
    else:
        st.sidebar.warning(f"⚠️ {new_ticker} already in list.")

remove_ticker = st.sidebar.selectbox("Remove a stock", ["None"] + st.session_state.tickers)
if st.sidebar.button("🗑️ Remove Stock") and remove_ticker != "None":
    st.session_state.tickers.remove(remove_ticker)
    st.sidebar.success(f"✅ Removed {remove_ticker}!")
    st.cache_data.clear()
    time.sleep(0.5)
    st.rerun()

st.sidebar.write("**Current stocks:**")
for t in st.session_state.tickers:
    st.sidebar.write(f"- {t}")

# ---------- API KEY ----------
API_KEY = "YOUR_ACTUAL_KEY_HERE"  # <-- PASTE YOUR KEY HERE

# ---------- CACHED DATA FETCHING ----------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(tickers, api_key):
    """Fetch stock data from Alpha Vantage with caching."""
    data = pd.DataFrame()
    failed_stocks = []
    
    for ticker in tickers:
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}&outputsize=compact"
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
                failed_stocks.append(ticker)
            
            time.sleep(1)
            
        except Exception as e:
            failed_stocks.append(ticker)
    
    return data, failed_stocks

# ---------- FETCH DATA (USING CACHE) ----------
with st.spinner("📡 Fetching data..."):
    data, failed_stocks = fetch_stock_data(st.session_state.tickers, API_KEY)

if failed_stocks:
    st.warning(f"⚠️ Could not load: {', '.join(failed_stocks)}. Showing available data.")

# ---------- REFRESH BUTTON ----------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ---------- IF DATA LOADED ----------
if not data.empty:
    st.success(f"✅ Loaded {len(data.columns)} stocks!")
    
    # ---------- CHART ----------
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
    
    latest_prices = data.iloc[-1]
    
    st.write("### Current Stock Prices")
    price_df = latest_prices.to_frame("Price ($)")
    st.dataframe(price_df)
    
    st.write("### Enter Your Share Counts")
    
    if "shares" not in st.session_state:
        st.session_state.shares = {ticker: 0 for ticker in st.session_state.tickers}
    
    # Only show input fields for stocks that loaded
    loaded_tickers = list(data.columns)
    
    if loaded_tickers:
        # Use columns with max 5 per row
        cols = st.columns(min(len(loaded_tickers), 5))
        
        for i, ticker in enumerate(loaded_tickers):
            with cols[i % len(cols)]:
                st.session_state.shares[ticker] = st.number_input(
                    f"{ticker} shares",
                    min_value=0,
                    value=st.session_state.shares.get(ticker, 0),
                    step=1,  # Whole shares only
                    key=f"shares_{ticker}"
                )
    
    # Calculate portfolio
    total_value = 0
    has_shares = False
    
    for ticker in st.session_state.shares:
        if st.session_state.shares.get(ticker, 0) > 0 and ticker in latest_prices.index:
            has_shares = True
            total_value += st.session_state.shares[ticker] * latest_prices[ticker]
    
    if has_shares:
        st.success(f"### Total Portfolio Value: **${total_value:,.2f}**")
        
        st.write("### Breakdown by Stock")
        breakdown_data = {
            "Ticker": [],
            "Shares": [],
            "Price ($)": [],
            "Value ($)": []
        }
        
        for ticker in st.session_state.shares:
            if st.session_state.shares.get(ticker, 0) > 0 and ticker in latest_prices.index:
                price = latest_prices[ticker]
                value = st.session_state.shares[ticker] * price
                breakdown_data["Ticker"].append(ticker)
                breakdown_data["Shares"].append(st.session_state.shares[ticker])
                breakdown_data["Price ($)"].append(f"${price:.2f}")
                breakdown_data["Value ($)"].append(f"${value:.2f}")
        
        if breakdown_data["Ticker"]:
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df)
        
        # ---------- PROFIT/LOSS ----------
        st.write("### Profit / Loss")
        st.write("Enter what you paid per share (optional):")
        
        stocks_with_shares = [t for t in st.session_state.shares if st.session_state.shares.get(t, 0) > 0 and t in latest_prices.index]
        
        if stocks_with_shares:
            cols2 = st.columns(min(len(stocks_with_shares), 5))
            purchase_prices = {}
            
            for i, ticker in enumerate(stocks_with_shares):
                with cols2[i % len(cols2)]:
                    purchase_prices[ticker] = st.number_input(
                        f"{ticker} buy price",
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        key=f"buy_{ticker}"
                    )
            
            has_purchase = False
            total_cost = 0
            total_current = 0
            
            for ticker in purchase_prices:
                if purchase_prices[ticker] > 0 and st.session_state.shares.get(ticker, 0) > 0:
                    has_purchase = True
                    total_cost += purchase_prices[ticker] * st.session_state.shares[ticker]
                    total_current += latest_prices[ticker] * st.session_state.shares[ticker]
            
            if has_purchase:
                profit_loss = total_current - total_cost
                profit_pct = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
                
                if profit_loss >= 0:
                    st.success(f"💰 Total Profit: **+${profit_loss:,.2f}** (+{profit_pct:.1f}%)")
                else:
                    st.error(f"📉 Total Loss: **-${abs(profit_loss):,.2f}** ({profit_pct:.1f}%)")
                
                pl_data = {
                    "Ticker": [],
                    "Shares": [],
                    "Buy Price": [],
                    "Current Price": [],
                    "P&L ($)": [],
                    "P&L (%)": []
                }
                
                for ticker in purchase_prices:
                    if purchase_prices[ticker] > 0 and st.session_state.shares.get(ticker, 0) > 0:
                        buy = purchase_prices[ticker]
                        current = latest_prices[ticker]
                        shares_count = st.session_state.shares[ticker]
                        pl = (current - buy) * shares_count
                        pl_pct = ((current - buy) / buy) * 100 if buy > 0 else 0
                        
                        pl_data["Ticker"].append(ticker)
                        pl_data["Shares"].append(shares_count)
                        pl_data["Buy Price"].append(f"${buy:.2f}")
                        pl_data["Current Price"].append(f"${current:.2f}")
                        pl_data["P&L ($)"].append(f"${pl:+.2f}")
                        pl_data["P&L (%)"].append(f"{pl_pct:+.1f}%")
                
                if pl_data["Ticker"]:
                    pl_df = pd.DataFrame(pl_data)
                    st.dataframe(pl_df)
            else:
                st.info("💡 Enter your purchase prices above to track profit/loss.")
        else:
            st.info("💡 Enter share counts first, then add purchase prices.")
        
    else:
        st.info("💡 Enter your share counts above to see your portfolio value.")
    
    st.caption(f"📅 Data as of: {data.index[-1].strftime('%Y-%m-%d')}")
    
else:
    st.error("❌ Unable to load any stock data.")
    st.info("""
    **Troubleshooting:**
    1. Make sure you copied your API key correctly
    2. Alpha Vantage has a limit of 5 requests per minute—wait 60 seconds and refresh
    3. Check your internet connection
    4. Try with just one stock first (e.g., AAPL) to test
    """)

st.caption("Built with ❤️ using Python + Streamlit")
