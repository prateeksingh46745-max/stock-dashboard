import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)  # cache for 5 minutes
def get_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetch historical stock data for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        df.index = df.index.tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        return df
    except Exception:
        return None

@st.cache_data(ttl=300)  # cache for 5 minutes
def get_stock_info(ticker):
    """
    Fetch basic company info — name, sector, current price etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
    except Exception:
        return {
            "name": ticker,
            "sector": "N/A",
            "current_price": "N/A",
            "market_cap": "N/A",
            "52w_high": "N/A",
            "52w_low": "N/A",
        }

def get_currency_symbol(ticker):
    """
    Returns correct currency symbol based on ticker suffix.
    """
    ticker = ticker.upper()
    if any(x in ticker for x in [".NS", ".BO", "^NSEI", "^BSESN"]):
        return "₹"
    elif any(x in ticker for x in [".L", "^FTSE", "^FTMC"]):
        return "£"
    elif any(x in ticker for x in [".T", "^N225"]):
        return "¥"
    else:
        return "$"

def format_market_cap(value, currency_symbol):
    """
    Formats market cap in Crores for Indian, Billions for others.
    """
    if value == "N/A" or not value:
        return "N/A"
    if currency_symbol == "₹":
        crores = value / 1e7
        if crores >= 1_00_000:
            return f"₹{crores/1_00_000:.2f} Lakh Cr"
        return f"₹{crores:,.0f} Cr"
    else:
        billions = value / 1e9
        return f"${billions:.2f}B"