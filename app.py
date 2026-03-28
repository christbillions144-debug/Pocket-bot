import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pocket Pro Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT PRO")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 récupération sécurisée
def get_data(symbol):
    for _ in range(3):
        try:
            data = yf.download(symbol, period="1d", interval="1m")
            if data is not None and not data.empty:
                return data
        except:
            pass
        time.sleep(2)
    return None

# 🔥 RSI manuel (stable)
def compute_rsi(close, period=7):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🚀 bouton
if st.button("🚀 GET SIGNAL"):
    data = get_data(symbol)

    if data is None or data.empty:
        st.error("❌ Données indisponibles")
    else:
        data = data.dropna()

        if len(data) < 30:
            st.warning("⚠️ Pas assez de données")
        else:
            try:
                close = data["Close"]
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close = pd.Series(close).astype(float)

                open_price = data["Open"].astype(float)
                high = data["High"].astype(float)
                low = data["Low"].astype(float)

                # 📊 INDICATEURS
                ema5 = close.ewm(span=5).mean()
                ema10 = close.ewm(span=10).mean()
                ema20 = close.ewm(span=20).mean()
                rsi = compute_rsi(close)

                # 🔥 dernières valeurs
                last_close = close.iloc[-1]
                last_open = open_price.iloc[-1]
                last_high = high.iloc[-1]
                last_low = low.iloc[-1]

                last_ema5 = ema5.iloc[-1]
                last_ema10 = ema10.iloc[-1]
                last_ema20 = ema20.iloc[-1]
                last_rsi = rsi.iloc[-1]

                # 🎯 FILTRE PUISSANT (SNIPER)
                trend_up = last_ema5 > last_ema10 > last_ema20
                trend_down = last_ema5 < last_ema10 < last_ema20

                strong_candle_buy = last_close > last_open and (last_close - last_open) > (last_high - last_low) * 0.6
                strong_candle_sell = last_close < last_open and (last_open - last_close) > (last_high - last_low) * 0.6

                buy = trend_up and last_rsi > 60 and strong_candle_buy
                sell = trend_down and last_rsi < 40 and strong_candle_sell

                st.subheader("📡 SIGNAL")

                if buy:
                    st.success(f"🟢 BUY ({duration}) 💰 SIGNAL FORT")
                elif sell:
                    st.error(f"🔴 SELL ({duration}) ⚡ SIGNAL FORT")
                else:
                    st.warning("⚪ PAS DE SIGNAL FIABLE")

            except:
                st.error("❌ Réessaie (marché ou connexion)")
