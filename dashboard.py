import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# PAGE SETTINGS

st.set_page_config(
    page_title="Realtime Market Dashboard",
    layout="wide"
)


# TITLE

st.title("📈 AI Powered Realtime Market Dashboard")


# STOCK SELECTOR

stock = st.sidebar.selectbox(
    "Select Stock",
    ["^NSEI", "RELIANCE.NS", "TCS.NS"]
)


# DOWNLOAD DATA

data = yf.download(
    tickers=stock,
    period="1d",
    interval="1m",
    progress=False
)


# RESET INDEX

data.reset_index(inplace=True)


# FIX MULTI-INDEX COLUMNS

data.columns = [
    col[0] if isinstance(col, tuple) else col
    for col in data.columns
]


# CONVERT NUMERIC COLUMNS

numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']

for col in numeric_cols:

    data[col] = pd.to_numeric(
        data[col],
        errors='coerce'
    )


# EMA CALCULATIONS

data['EMA9'] = data['Close'].ewm(span=9).mean()

data['EMA20'] = data['Close'].ewm(span=20).mean()

data['EMA50'] = data['Close'].ewm(span=50).mean()


# SHOW DATA

st.subheader("📊 Realtime Market Data")

st.dataframe(data.tail())


# CREATE CHART

fig = go.Figure()


# CLOSE PRICE LINE

fig.add_trace(
    go.Scatter(
        x=data['index'],
        y=data['Close'],
        mode='lines',
        name='Close Price'
    )
)


# EMA9

fig.add_trace(
    go.Scatter(
        x=data['index'],
        y=data['EMA9'],
        mode='lines',
        name='EMA9'
    )
)


# EMA20

fig.add_trace(
    go.Scatter(
        x=data['index'],
        y=data['EMA20'],
        mode='lines',
        name='EMA20'
    )
)


# EMA50

fig.add_trace(
    go.Scatter(
        x=data['index'],
        y=data['EMA50'],
        mode='lines',
        name='EMA50'
    )
)


# CHART LAYOUT

fig.update_layout(

    title="Realtime Stock Analysis",

    xaxis_title="Time",

    yaxis_title="Price",

    height=600
)


# DISPLAY CHART

st.plotly_chart(
    fig,
    use_container_width=True
)

from ta.momentum import RSIIndicator

rsi = RSIIndicator(close=data['Close'])

data['RSI'] = rsi.rsi()

latest_rsi = data['RSI'].iloc[-1]

st.metric("RSI", round(latest_rsi,2))

latest = data.iloc[-1]

if latest['EMA9'] > latest['EMA20']:

    st.success("📈 Bullish Signal")

else:

    st.error("📉 Bearish Signal")


from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=60000)

st.set_page_config(
    page_title="Realtime Stock Dashboard",
    layout="wide"
)
fig = go.Figure(data=[
    go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )
])