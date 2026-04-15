import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Scanner Pro", layout="centered")

st.title("⚡ POCKET SCANNER BOT PRO")

symbols = ["EURUSD=X", "GBPUSD=X", "BTC-USD"]
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 DATA SAFE
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

# 🔥 RSI SAFE
def compute_rsi(close, period=6):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🔍 ANALYSE SAFE
def analyze(symbol):
    data = get_data(symbol)

    if data is None or len(data) < 20:
        return None

    try:
        close = data["Close"]
        open_price = data["Open"]
        high = data["High"]
        low = data["Low"]

        # 🔧 FIX FORMAT
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(open_price, pd.DataFrame):
            open_price = open_price.iloc[:, 0]
        if isinstance(high, pd.DataFrame):
            high = high.iloc[:, 0]
        if isinstance(low, pd.DataFrame):
            low = low.iloc[:, 0]

        close = close.astype(float)
        open_price = open_price.astype(float)
        high = high.astype(float)
        low = low.astype(float)

        # 📊 INDICATEURS
        ema5 = close.ewm(span=5).mean()
        ema10 = close.ewm(span=10).mean()
        rsi = compute_rsi(close)

        # 📌 DERNIÈRES VALEURS
        last_close = float(close.iloc[-1])
        last_open = float(open_price.iloc[-1])
        last_high = float(high.iloc[-1])
        last_low = float(low.iloc[-1])
        last_ema5 = float(ema5.iloc[-1])
        last_ema10 = float(ema10.iloc[-1])
        last_rsi = float(rsi.iloc[-1])

        # 🎯 LOGIQUE MIX
        trend_up = last_ema5 > last_ema10
        trend_down = last_ema5 < last_ema10

        candle_size = abs(last_close - last_open)
        range_size = abs(last_high - last_low)

        candle_ok = candle_size > range_size * 0.3

        score = 0

        if trend_up:
            score += 2
        if trend_down:
            score += 2
        if last_rsi > 55:
            score += 2
        if last_rsi < 45:
            score += 2
        if candle_ok:
            score += 1

        if trend_up and last_rsi > 50:
            signal = "BUY"
        elif trend_down and last_rsi < 50:
            signal = "SELL"
        else:
            signal = "WAIT"

        return {
            "symbol": symbol,
            "signal": signal,
            "score": score
        }

    except:
        return None

# 🚀 BOUTON
if st.button("🚀 SCAN MARKET"):

    with st.spinner("Analyse du marché..."):
        results = []

        for s in symbols:
            res = analyze(s)
            if res:
                results.append(res)

    if len(results) == 0:
        st.error("❌ Aucune donnée disponible")
    else:
        # 🏆 MEILLEUR SIGNAL
        best = max(results, key=lambda x: x["score"])

        st.subheader("🏆 MEILLEUR TRADE")

        if best["signal"] == "BUY":
            st.success(f"🟢 BUY {best['symbol']} ({duration})")
            st.info("👉 Clique UP sur Pocket Broker")
        elif best["signal"] == "SELL":
            st.error(f"🔴 SELL {best['symbol']} ({duration})")
            st.info("👉 Clique DOWN sur Pocket Broker")
        else:
            st.warning("⚪ Marché pas clair")

        # 📊 AUTRES RÉSULTATS
        st.subheader("📊 ANALYSE COMPLÈTE")

        for r in results:
            if r["signal"] == "BUY":
                st.write(f"🟢 {r['symbol']} → BUY (score {r['score']})")
            elif r["signal"] == "SELL":
                st.write(f"🔴 {r['symbol']} → SELL (score {r['score']})")
            else:
                st.write(f"⚪ {r['symbol']} → WAIT")
