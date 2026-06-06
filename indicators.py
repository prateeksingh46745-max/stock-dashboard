import pandas as pd

def add_moving_averages(stock_df):
    # MA20 catches short term moves, MA50 shows the bigger trend
    stock_df["MA20"] = stock_df["Close"].rolling(window=20).mean()
    stock_df["MA50"] = stock_df["Close"].rolling(window=50).mean()
    return stock_df


def add_rsi(stock_df, period=14):
    """
    RSI (Relative Strength Index) → momentum indicator
    Above 70 = overbought (price may drop)
    Below 30 = oversold (price may rise)
    """
    delta = stock_df["Close"].diff()

    gain = delta.where(delta > 0, 0)   # keep only positive changes
    loss = -delta.where(delta < 0, 0)  # keep only negative changes (as positive)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    stock_df["RSI"] = 100 - (100 / (1 + rs))
    return stock_df


def add_bollinger_bands(stock_df, window=20):
    """
    Bollinger Bands → shows volatility
    Price near upper band = possibly overbought
    Price near lower band = possibly oversold
    """
    stock_df["BB_Mid"] = stock_df["Close"].rolling(window=window).mean()
    std = stock_df["Close"].rolling(window=window).std()
    stock_df["BB_Upper"] = stock_df["BB_Mid"] + (2 * std)
    stock_df["BB_Lower"] = stock_df["BB_Mid"] - (2 * std)
    return stock_df


def apply_all_indicators(stock_df):
    """
    Run all indicators at once — call this in the main app.
    """
    stock_df = add_moving_averages(stock_df)
    stock_df = add_rsi(stock_df)
    stock_df = add_bollinger_bands(stock_df)
    return stock_df