import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import get_stock_data, get_stock_info, get_currency_symbol, format_market_cap
from indicators import apply_all_indicators

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 15px;
        }
        
        /* Metric label */
        [data-testid="stMetricLabel"] {
            color: #8b949e;
            font-size: 13px;
        }
        
        /* Metric value */
        [data-testid="stMetricValue"] {
            color: #e6edf3;
            font-size: 22px;
            font-weight: 600;
        }

        /* Title */
        h1 {
            color: #e6edf3;
            font-weight: 700;
        }

        /* Divider */
        hr {
            border-color: #30363d;
        }

        /* Expander */
        [data-testid="stExpander"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar setup
st.sidebar.title("📈 Stock Dashboard")

# Region selector
st.sidebar.subheader("🌍 Select Market")
market_region = st.sidebar.selectbox(
    "Region",
    options=["🇮🇳 India", "🇺🇸 US", "🇬🇧 UK", "🇯🇵 Japan"]
)

# Stock lists per region
market_stocks = {
    "🇮🇳 India": {
        "NIFTY 50"        : "^NSEI",
        "SENSEX"          : "^BSESN",
        "Reliance"        : "RELIANCE.NS",
        "TCS"             : "TCS.NS",
        "Infosys"         : "INFY.NS",
        "HDFC Bank"       : "HDFCBANK.NS",
        "Wipro"           : "WIPRO.NS",
        "SBI"             : "SBIN.NS",
        "Bajaj Finance"   : "BAJFINANCE.NS",
        "Tata Motors"     : "TATAMOTORS.NS",
        "Maruti Suzuki"   : "MARUTI.NS",
        "Adani Ports"     : "ADANIPORTS.NS",
    },
    "🇺🇸 US": {
        "S&P 500"         : "^GSPC",
        "NASDAQ"          : "^IXIC",
        "Dow Jones"       : "^DJI",
        "Apple"           : "AAPL",
        "Tesla"           : "TSLA",
        "Microsoft"       : "MSFT",
        "Google"          : "GOOGL",
        "Amazon"          : "AMZN",
        "Meta"            : "META",
        "NVIDIA"          : "NVDA",
        "Netflix"         : "NFLX",
        "Berkshire"       : "BRK-B",
    },
    "🇬🇧 UK": {
        "FTSE 100"        : "^FTSE",
        "FTSE 250"        : "^FTMC",
        "HSBC"            : "HSBA.L",
        "BP"              : "BP.L",
        "Shell"           : "SHEL.L",
        "Barclays"        : "BARC.L",
        "Unilever"        : "ULVR.L",
        "AstraZeneca"     : "AZN.L",
        "Rolls Royce"     : "RR.L",
        "Tesco"           : "TSCO.L",
        "Vodafone"        : "VOD.L",
        "Rio Tinto"       : "RIO.L",
    },
    "🇯🇵 Japan": {
        "Nikkei 225"      : "^N225",
        "Toyota"          : "7203.T",
        "Sony"            : "6758.T",
        "SoftBank"        : "9984.T",
        "Honda"           : "7267.T",
        "Panasonic"       : "6752.T",
        "Nintendo"        : "7974.T",
        "Mitsubishi"      : "8058.T",
        "Canon"           : "7751.T",
        "Fujitsu"         : "6702.T",
        "Hitachi"         : "6501.T",
        "Nissan"          : "7201.T",
    }
}


selected_stocks = market_stocks[market_region]
selected_quick = st.sidebar.selectbox(
    "Quick Select",
    options=["-- Select --"] + list(selected_stocks.keys())
)

st.sidebar.divider()


default_ticker = selected_stocks[selected_quick] if selected_quick != "-- Select --" else list(selected_stocks.values())[0]
ticker = st.sidebar.text_input("Or Enter Any Ticker", value=default_ticker).upper()

# using 3mo as default because 1mo doesn't have enough data for MA50
period = st.sidebar.selectbox(
    "Time Period",
    options=["1mo", "3mo", "6mo", "1y", "2y"],
    index=1
)

interval = st.sidebar.selectbox(
    "Interval",
    options=["1d", "1wk"],
    index=0
)

auto_refresh = st.sidebar.checkbox("Auto Refresh (every 60s)", value=False)

if auto_refresh:
    st.sidebar.info("Auto-refresh is ON")

st.sidebar.divider()
st.sidebar.subheader("📊 Compare Stocks")
compare_ticker = st.sidebar.text_input("Compare with (optional)", value="").upper()

# Auto refresh
if auto_refresh:
    import time
    st.sidebar.info("Auto-refresh is ON")

# Load the data
with st.spinner(f"Fetching data for {ticker}..."):
    stock_df = get_stock_data(ticker, period=period, interval=interval)
    info = get_stock_info(ticker)
    stock_df = apply_all_indicators(stock_df)

# Show header
st.title(f"{info['name']} ({ticker})")
st.caption(f"Sector: {info['sector']}")

# Currency detection
currency = get_currency_symbol(ticker)

# Metric cards 
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Current Price", f"{currency}{info['current_price']}")
col2.metric("52W High",      f"{currency}{info['52w_high']}")
col3.metric("52W Low",       f"{currency}{info['52w_low']}")
col4.metric("Market Cap",    format_market_cap(info['market_cap'], currency))

latest_rsi = round(stock_df["RSI"].dropna().iloc[-1], 2)
rsi_signal = "🔴 Overbought" if latest_rsi > 70 else ("🟢 Oversold" if latest_rsi < 30 else "🟡 Neutral")
col5.metric("RSI (14)", f"{latest_rsi} — {rsi_signal}")

st.divider()

# MA Chart
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[0.6, 0.2, 0.2],
    vertical_spacing=0.05,
    subplot_titles=("Price & Indicators", "Volume", "RSI")
)


fig.add_trace(go.Candlestick(
    x=stock_df.index,
    open=stock_df["Open"], high=stock_df["High"],
    low=stock_df["Low"], close=stock_df["Close"],
    name="Price"
), row=1, col=1)


fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df["MA20"], name="MA20",
    line=dict(color="orange", width=1.5)), row=1, col=1)

fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df["MA50"], name="MA50",
    line=dict(color="blue", width=1.5)), row=1, col=1)

# Bollinger Bands
fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df["BB_Upper"], name="BB Upper",
    line=dict(color="gray", width=1, dash="dash")), row=1, col=1)

fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df["BB_Lower"], name="BB Lower",
    line=dict(color="gray", width=1, dash="dash"),
    fill="tonexty", fillcolor="rgba(128,128,128,0.1)"), row=1, col=1)

if compare_ticker:
    stock_df_compare = get_stock_data(compare_ticker, period=period, interval=interval)
    # Normalize to percentage change for fair comparison
    stock_df_compare["Normalized"] = (stock_df_compare["Close"] / stock_df_compare["Close"].iloc[0]) * 100
    stock_df["Normalized"] = (stock_df["Close"] / stock_df["Close"].iloc[0]) * 100

    fig.add_trace(go.Scatter(
        x=stock_df_compare.index,
        y=stock_df_compare["Normalized"],
        name=compare_ticker,
        line=dict(color="yellow", width=1.5)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=stock_df.index,
        y=stock_df["Normalized"],
        name=ticker,
        line=dict(color="cyan", width=1.5)
    ), row=1, col=1)

fig.add_trace(go.Bar(
    x=stock_df.index, y=stock_df["Volume"],
    name="Volume", marker_color="rgba(100, 149, 237, 0.6)"
), row=2, col=1)


fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df["RSI"], name="RSI",
    line=dict(color="purple", width=1.5)), row=3, col=1)


fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

fig.update_layout(
    height=700,
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    showlegend=True
)

st.plotly_chart(fig, width='stretch')

# Raw Data Table 
with st.expander("📊 View Raw Data"):
    st.dataframe(stock_df.tail(20), width='stretch')

# Export 
st.subheader("📥 Export Data")

csv = stock_df.to_csv().encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"{ticker}_stock_data.csv",
    mime="text/csv"
)    
# Latest News 
st.subheader(f"📰 Latest News — {ticker}")

try:
    stock_news = yf.Ticker(ticker).news

    if stock_news:
        for article in stock_news[:5]:
            # yfinance new structure has content nested
            content = article.get("content", {})
            
            title = content.get("title") or article.get("title", "No Title")
            publisher = content.get("provider", {}).get("displayName") or article.get("publisher", "Unknown Source")
            
            # get link safely
            link = (
                content.get("canonicalUrl", {}).get("url") or
                article.get("link") or
                article.get("url") or
                "#"
            )

            st.markdown(f"""
            <div style="background-color:#161b22; padding:15px; border-radius:10px; 
                        margin-bottom:10px; border:1px solid #30363d;">
                <a href="{link}" target="_blank" 
                   style="color:#58a6ff; font-weight:600; text-decoration:none;">
                    {title}
                </a>
                <p style="color:#8b949e; font-size:12px; margin-top:5px;">
                    {publisher}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent news found for this ticker.")

except Exception as e:
    st.warning(f"Couldn't load news right now. Try refreshing.")

# Footer
st.divider()
st.markdown("""
    <div style="text-align:center; color:#8b949e; font-size:13px;">
        Built by <strong style="color:#58a6ff;">Prateek Singh Chouhan</strong> · 
        Data via yfinance · 
        <a href="https://github.com/prateeksingh46745-max" 
           style="color:#58a6ff;">GitHub</a>
    </div>
""", unsafe_allow_html=True)