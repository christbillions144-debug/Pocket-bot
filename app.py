import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Sniper Bot", layout="centered")

st.title("🎯 POCKET SNIPER BOT")

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
        time.sleep(2)
    return None

# 🔥 RSI stable
def compute_rsi(close, period=7):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🚀 bouton
if st.button("🚀 GET SNIPER SIGNAL"):

    with st.spinner("Analyse sniper..."):
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

            # 📊 INDICATEURS
            ema5 = close.ewm(span=5).mean()
            ema10 = close.ewm(span=10).mean()
            ema20 = close.ewm(span=20).mean()
            rsi = compute_rsi(close)

            # 🔥 dernières valeurs
            last_close = float(close.iloc[-1])
            last_open = float(open_price.iloc[-1])
            last_high = float(high.iloc[-1])
            last_low = float(low.iloc[-1])

            last_ema5 = float(ema5.iloc[-1])
            last_ema10 = float(ema10.iloc[-1])
            last_ema20 = float(ema20.iloc[-1])
            last_rsi = float(rsi.iloc[-1])

            # 🎯 CONDITIONS SNIPER
            trend_up = last_ema5 > last_ema10 > last_ema20
            trend_down = last_ema5 < last_ema10 < last_ema20

            candle_size = abs(last_close - last_open)
            full_range = abs(last_high - last_low)

            strong_buy_candle = last_close > last_open and candle_size > full_range * 0.6
            strong_sell_candle = last_close < last_open and candle_size > full_range * 0.6

            buy = trend_up and last_rsi > 60 and strong_buy_candle
            sell = trend_down and last_rsi < 40 and strong_sell_candle

            st.subheader("🎯 SNIPER SIGNAL")

            if buy:
                st.success(f"🟢 BUY ({duration}) 💎 SIGNAL FORT")
                st.info("👉 Clique UP maintenant")
            elif sell:
                st.error(f"🔴 SELL ({duration}) 💎 SIGNAL FORT")
                st.info("👉 Clique DOWN maintenant")
            else:
                st.warning("⚪ PAS DE SIGNAL (marché pas propre)")

        except:
            st.error("❌ Réessaie (données)")
