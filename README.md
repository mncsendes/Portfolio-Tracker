# Personal Portfolio Dashboard

A real-time stock portfolio tracker built with Python and Streamlit. This dashboard lets you track stock prices, calculate your portfolio value, and monitor profit/loss—all from a clean, interactive web interface.


---

## ✨ Features

- **Live Stock Data** — Fetches real-time prices via Alpha Vantage API
- **Interactive Portfolio** — Enter your share counts and see your total value instantly
- **Profit/Loss Tracking** — Compare current value against your purchase price
- **Beautiful Charts** — Visualize stock performance over time with Matplotlib
- **Session Persistence** — Your share counts are saved even when you refresh
- **Dark Mode** — Toggle between light and dark themes
- **Responsive Design** — Works on desktop, tablet, and mobile
- **News Feed** — Stay updated with the latest market headlines
- **Expandable Tickers** — Add or remove stocks dynamically

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Backend logic and data processing |
| **Streamlit** | Web app framework and UI |
| **Pandas** | Data manipulation and analysis |
| **Matplotlib** | Data visualization (stock charts) |
| **Requests** | API calls to fetch stock data |
| **Alpha Vantage** | Free stock price API |
| **NewsAPI** | Market news headlines |


---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- A free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/portfolio-dashboard.git
   cd portfolio-dashboard

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt

3. **Add Your API Key**

4. **Run the app**
     ```bash
    streamlit run dashboard.py
