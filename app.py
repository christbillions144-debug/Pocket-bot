import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Pro Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT PRO")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 récupération ultra sécurisée
def get_data(symbol):
    for _ in range(5):
        try:
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data is not None and not data.empty:
                data = data.dropna()
                if len(data) > 30:
                    return data
        except:
            pass
        time.sleep(2)
    return None

# 🔥 RSI simple stable
def compute_rsi(close):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(7).mean()
    loss = (-delta.clip(upper=0)).rolling(7).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🚀 GET SIGNAL"):

    with st.spinner("Analyse en cours..."):
        data = get_data(symbol)

    if data is None:
        st.error("❌ Marché indisponible, réessaie dans 10 secondes")
    else:
        try:
            close = data["Close"]
            open_price = data["Open"]

            # 🔥 forcer format propre
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            if isinstance(open_price, pd.DataFrame):
                open_price = open_price.iloc[:, 0]

            close = close.astype(float)
            open_price = open_price.astype(float)

            # 📊 indicateurs
            ema5 = close.ewm(span=5).mean()
            ema10 = close.ewm(span=10).mean()
            ema20 = close.ewm(span=20).mean()
            rsi = compute_rsi(close)

            # 🔥 dernières valeurs
            last_close = float(close.iloc[-1])
            last_open = float(open_price.iloc[-1])
            last_ema5 = float(ema5.iloc[-1])
            last_ema10 = float(ema10.iloc[-1])
            last_ema20 = float(ema20.iloc[-1])
            last_rsi = float(rsi.iloc[-1])

            # 🎯 logique sniper
            trend_up = last_ema5 > last_ema10 > last_ema20
            trend_down = last_ema5 < last_ema10 < last_ema20

            buy = trend_up and last_rsi > 60 and last_close > last_open
            sell = trend_down and last_rsi < 40 and last_close < last_open

            st.subheader("📡 SIGNAL")

            if buy:
                st.success(f"🟢 BUY ({duration})")
            elif sell:
                st.error(f"🔴 SELL ({duration})")
            else:
                st.warning("⚪ ATTENDS (pas de signal fiable)")

        except:
            st.error("❌ Problème données, réessaie")
