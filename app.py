import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Bot Ultra", layout="centered")

st.title("⚡ POCKET BOT ULTRA AGRESSIF")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 récupération rapide
def get_data(symbol):
    for _ in range(5):
        try:
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data is not None and not data.empty:
                return data.dropna()
        except:
            pass
        time.sleep(1)
    return None

# 🔥 RSI rapide
def compute_rsi(close, period=5):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🚀 bouton
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

        # 📊 indicateurs rapides
        ema3 = close.ewm(span=3).mean()
        ema7 = close.ewm(span=7).mean()
        rsi = compute_rsi(close)

        last_close = float(close.iloc[-1])
        last_open = float(open_price.iloc[-1])
        last_ema3 = float(ema3.iloc[-1])
        last_ema7 = float(ema7.iloc[-1])
        last_rsi = float(rsi.iloc[-1])

        st.subheader("📡 SIGNAL")

        # 🔥 LOGIQUE ULTRA AGRESSIVE (toujours signal)
        score_buy = 0
        score_sell = 0

        if last_ema3 > last_ema7:
            score_buy += 1
        else:
            score_sell += 1

        if last_rsi > 50:
            score_buy += 1
        else:
            score_sell += 1

        if last_close > last_open:
            score_buy += 1
        else:
            score_sell += 1

        # 🎯 décision FORCÉE
        if score_buy >= score_sell:
            st.success(f"🟢 BUY ({duration}) ⚡")
            st.info("👉 Clique UP")
        else:
            st.error(f"🔴 SELL ({duration}) ⚡")
            st.info("👉 Clique DOWN")
