import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Scanner Bot", layout="centered")

st.title("⚡ POCKET SCANNER BOT")

symbols = ["EURUSD=X", "GBPUSD=X", "BTC-USD"]
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 récupération stable
def get_data(symbol):
    for _ in range(3):
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

def analyze(symbol):
    data = get_data(symbol)
    if data is None:
        return None

    close = data["Close"]
    open_price = data["Open"]
    high = data["High"]
    low = data["Low"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if isinstance(open_price, pd.DataFrame):
        open_price = open_price.iloc[:, 0]

    close = close.astype(float)
    open_price = open_price.astype(float)
    high = high.astype(float)
    low = low.astype(float)

    ema5 = close.ewm(span=5).mean()
    ema10 = close.ewm(span=10).mean()
    rsi = compute_rsi(close)

    last_close = float(close.iloc[-1])
    last_open = float(open_price.iloc[-1])
    last_high = float(high.iloc[-1])
    last_low = float(low.iloc[-1])
    last_ema5 = float(ema5.iloc[-1])
    last_ema10 = float(ema10.iloc[-1])
    last_rsi = float(rsi.iloc[-1])

    trend_up = last_ema5 > last_ema10
    trend_down = last_ema5 < last_ema10

    candle_size = abs(last_close - last_open)
    range_size = abs(last_high - last_low)
    candle_ok = candle_size > range_size * 0.3

    score = 0

    if trend_up:
        score += 1
    if trend_down:
        score += 1
    if last_rsi > 50:
        score += 1
    if last_rsi < 50:
        score += 1
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

# 🚀 bouton
if st.button("🚀 SCAN MARKET"):

    results = []

    for s in symbols:
        res = analyze(s)
        if res:
            results.append(res)

    if len(results) == 0:
        st.error("❌ Aucune donnée")
    else:
        best = max(results, key=lambda x: x["score"])

        st.subheader("🏆 MEILLEUR SIGNAL")

        if best["signal"] == "BUY":
            st.success(f"🟢 BUY {best['symbol']} ({duration})")
        elif best["signal"] == "SELL":
            st.error(f"🔴 SELL {best['symbol']} ({duration})")
        else:
            st.warning("⚪ Aucun bon signal")

        st.subheader("📊 AUTRES ACTIFS")

        for r in results:
            st.write(f"{r['symbol']} → {r['signal']} (score: {r['score']})")
