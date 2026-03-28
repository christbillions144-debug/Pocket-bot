import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.title("⚡ POCKET BOT (NO WAIT MODE)")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

def get_data(symbol):
    for _ in range(5):
        try:
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data is not None and not data.empty:
                data = data.dropna()
                if len(data) > 20:
                    return data
        except:
            pass
        time.sleep(1)
    return None

def compute_rsi(close, period=7):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🚀 GET SIGNAL"):

    data = get_data(symbol)

    if data is None:
        st.error("❌ Erreur marché")
    else:
        close = data["Close"]
        open_price = data["Open"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(open_price, pd.DataFrame):
            open_price = open_price.iloc[:, 0]

        close = close.astype(float)
        open_price = open_price.astype(float)

        ema5 = close.ewm(span=5).mean()
        ema10 = close.ewm(span=10).mean()
        rsi = compute_rsi(close)

        last_close = float(close.iloc[-1])
        last_ema5 = float(ema5.iloc[-1])
        last_ema10 = float(ema10.iloc[-1])
        last_rsi = float(rsi.iloc[-1])

        st.subheader("📡 SIGNAL")

        # 🔥 FORCER SIGNAL
        if last_ema5 > last_ema10:
            st.success(f"🟢 BUY ({duration})")
            st.info("👉 Clique UP")
        else:
            st.error(f"🔴 SELL ({duration})")
            st.info("👉 Clique DOWN")
