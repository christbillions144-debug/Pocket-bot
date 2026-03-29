import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Bot Mix", layout="centered")

st.title("⚡ POCKET BOT (MIX PRO)")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 récupération stable
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

# 🔥 RSI
def compute_rsi(close, period=6):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🚀 bouton
if st.button("🚀 GET SIGNAL"):

    with st.spinner("Analyse..."):
        data = get_data(symbol)

    if data is None:
        st.error("❌ Données indisponibles")
    else:
        try:
            close = data["Close"]
            open_price = data["Open"]
            high = data["High"]
            low = data["Low"]

            # 🔥 FIX FORMAT
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            if isinstance(open_price, pd.DataFrame):
                open_price = open_price.iloc[:, 0]

            close = close.astype(float)
            open_price = open_price.astype(float)
            high = high.astype(float)
            low = low.astype(float)

            # 📊 INDICATEURS RAPIDES
            ema5 = close.ewm(span=5).mean()
            ema10 = close.ewm(span=10).mean()
            rsi = compute_rsi(close)

            # 🔥 dernières valeurs
            last_close = float(close.iloc[-1])
            last_open = float(open_price.iloc[-1])
            last_high = float(high.iloc[-1])
            last_low = float(low.iloc[-1])

            last_ema5 = float(ema5.iloc[-1])
            last_ema10 = float(ema10.iloc[-1])
            last_rsi = float(rsi.iloc[-1])

            # 🎯 CONDITIONS MIX
            trend_up = last_ema5 > last_ema10
            trend_down = last_ema5 < last_ema10

            candle_size = abs(last_close - last_open)
            range_size = abs(last_high - last_low)

            candle_ok = candle_size > range_size * 0.3  # plus souple que sniper

            buy = trend_up and last_rsi > 50 and candle_ok
            sell = trend_down and last_rsi < 50 and candle_ok

            st.subheader("📡 SIGNAL")

            if buy:
                st.success(f"🟢 BUY ({duration}) ⚡")
                st.info("👉 Clique UP")
            elif sell:
                st.error(f"🔴 SELL ({duration}) ⚡")
                st.info("👉 Clique DOWN")
            else:
                st.warning("⚪ SIGNAL FAIBLE (évite)")

        except:
            st.error("❌ Réessaie")
