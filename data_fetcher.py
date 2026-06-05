import yfinance as yf

def get_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetch historical stock data for a given ticker.
    
    ticker   → stock symbol e.g. "AAPL", "TSLA", "INFY"
    period   → how far back: "1d", "5d", "1mo", "3mo", "6mo", "1y"
    interval → candle size: "1m", "5m", "15m", "1h", "1d"
    """
    stock = yf.Ticker(ticker)
    stock_df = stock.history(period=period, interval=interval)
    
    # Clean up
    stock_df.index = stock_df.index.tz_localize(None)  # remove timezone info
    stock_df = stock_df[["Open", "High", "Low", "Close", "Volume"]]  # keep only what we need
    
    return stock_df


def get_stock_info(ticker):
    """
    Fetch basic company info — name, sector, current price etc.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "name": info.get("longName", ticker),
        "sector": info.get("sector", "N/A"),
        "current_price": info.get("currentPrice", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
    }

def get_currency_symbol(ticker):
    """
    Returns correct currency symbol based on ticker suffix.
    """
    ticker = ticker.upper()
    
    if any(x in ticker for x in [".NS", ".BO", "^NSEI", "^BSESN"]):
        return "₹"  # Indian Rupee
    elif any(x in ticker for x in [".L", "^FTSE", "^FTMC"]):
        return "£"  # British Pound
    elif any(x in ticker for x in [".T", "^N225"]):
        return "¥"  # Japanese Yen
    else:
        return "$"  # US Dollar (default)
    
# Indian number system uses Lakhs & Crores, not Millions & Billions
def format_market_cap(value, currency_symbol):
    """
    Formats market cap:
    Indian stocks → Crores (₹)
    Others        → Billions ($)
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