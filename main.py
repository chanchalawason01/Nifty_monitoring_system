import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD

symbols = [
    "^NSEI",
    "RELIANCE.NS",
    "TCS.NS"
]

def market_open():

    now = datetime.now()

    hour = now.hour
    minute = now.minute

    current_minutes = hour * 60 + minute

    market_start = 9 * 60 + 15
    market_end = 15 * 60 + 30

    return market_start <= current_minutes <= market_end

#CSV FILE =========
def create_csv(symbol):

    file_name = f"{symbol.replace('.', '_')}.csv"

    if not os.path.exists(file_name):

        df = pd.DataFrame(columns=[
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ])

        df.to_csv(file_name, index=False)

    return file_name

#FETCHING DATA =========
def fetch_data(symbol):

    data = yf.download(
        tickers=symbol,
        period="1d",
        interval="1m",
        progress=False
    )

    latest = data.tail(1)

    return latest


# ========= SAVE DATA =========

def save_data(latest, file_name):

    if latest.empty:
        return

    if os.path.exists(file_name):

        existing = pd.read_csv(file_name)

        latest_time = str(latest.index[0])

        existing_times = existing.iloc[:, 0].astype(str).values

        if latest_time in existing_times:

            print("⚠ Duplicate candle skipped")

            return

    latest.to_csv(
        file_name,
        mode='a',
        header=False
    )

    print("✅ New candle saved")


# ========= LOAD DATA =========

def load_data(file_name):

    df = pd.read_csv(file_name)

    return df


# ========= EMA CALCULATION =========

def calculate_ema(df):

    df['EMA9'] = df['Close'].ewm(span=9).mean()

    df['EMA20'] = df['Close'].ewm(span=20).mean()

    df['EMA50'] = df['Close'].ewm(span=50).mean()

    return df


# ========= RSI CALCULATION =========

def calculate_rsi(df):

    rsi = RSIIndicator(close=df['Close'])

    df['RSI'] = rsi.rsi()

    return df


# ========= MACD CALCULATION =========

def calculate_macd(df):

    macd = MACD(close=df['Close'])

    df['MACD'] = macd.macd()

    df['MACD_SIGNAL'] = macd.macd_signal()

    return df


# ========= VOLUME ANALYSIS =========

def volume_analysis(df):

    avg_volume = df['Volume'].mean()

    latest_volume = df['Volume'].iloc[-1]

    if latest_volume > avg_volume:

        print("🔥 High Volume Activity")

    else:

        print("📊 Normal Volume")


# ========= SIGNAL GENERATION =========

def generate_signal(df):

    latest = df.iloc[-1]

    if latest['EMA9'] > latest['EMA20']:

        print("📈 Bullish Signal")

    elif latest['EMA9'] < latest['EMA20']:

        print("📉 Bearish Signal")

    else:

        print("➖ Neutral Signal")


# ========= RSI ANALYSIS =========

def analyze_rsi(df):

    latest_rsi = df['RSI'].iloc[-1]

    if latest_rsi > 70:

        print("⚠ Overbought Market")

    elif latest_rsi < 30:

        print("⚠ Oversold Market")

    else:

        print("✅ RSI Neutral")


# ========= DISPLAY OUTPUT =========

def display_output(df, symbol):

    latest = df.iloc[-1]

    print("\n===================================")

    print(f"📌 STOCK: {symbol}")

    print("===================================")

    print("Close Price :", latest['Close'])

    print("EMA9        :", latest['EMA9'])

    print("EMA20       :", latest['EMA20'])

    print("EMA50       :", latest['EMA50'])

    print("RSI          :", latest['RSI'])

    print("MACD         :", latest['MACD'])

    print("MACD Signal  :", latest['MACD_SIGNAL'])

    print("Volume       :", latest['Volume'])

    print("===================================\n")


# ========= MAIN PROGRAM =========

print("\n🚀 REALTIME STOCK MONITORING SYSTEM STARTED\n")


while True:

    try:

        if market_open():

            for symbol in symbols:

                print(f"\n🔄 Fetching data for {symbol}")

                file_name = create_csv(symbol)

                latest = fetch_data(symbol)

                save_data(latest, file_name)

                df = load_data(file_name)

                # Convert numeric columns properly

                numeric_columns = [
                    'Open',
                    'High',
                    'Low',
                    'Close',
                    'Volume'
                ]

                for col in numeric_columns:

                    df[col] = pd.to_numeric(
                        df[col],
                        errors='coerce'
                    )

                # Indicator Calculations

                df = calculate_ema(df)

                df = calculate_rsi(df)

                df = calculate_macd(df)

                # Analysis

                display_output(df, symbol)

                generate_signal(df)

                analyze_rsi(df)

                volume_analysis(df)

                print("\n-----------------------------------")

        else:

            print("\n⏰ Market Closed")

        # Wait 60 seconds

        time.sleep(60)

    except Exception as e:

        print("\n❌ ERROR:", e)

        time.sleep(60)

    