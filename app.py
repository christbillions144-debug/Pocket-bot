import streamlit as st
import yfinance as yf
import pandas as pd
import time
from ta.momentum import RSIIndicator

st.set_page_config(page_title="Pocket Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

def get_data(symbol):
    for _ in range(3):
        data = yf.download(symbol, period="1d", interval="1m")
        if data is not None and not data.empty:
            return data
        time.sleep(2)
    return None

if st.button("🚀 GET SIGNAL"):
    data = get_data(symbol)

    if data is None or data.empty:
        st.error("❌ Données indisponibles")
    else:
        data = data.dropna()

        if len(data) < 20:
            st.warning("⚠️ Pas assez de données")
        else:
            try:
                # 🔥 FIX IMPORTANT
                close = data["Close"]
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close = pd.Series(close).astype(float)

                # INDICATEURS
                data['EMA5'] = close.ewm(span=5).mean()
                data['EMA10'] = close.ewm(span=10).mean()
                data['RSI'] = RSIIndicator(close, window=7).rsi()

                last = data.iloc[-1]

                buy = (
                    last['EMA5'] > last['EMA10'] and
                    last['RSI'] > 55 and
                    last['Close'] > last['Open']
                )

                sell = (
                    last['EMA5'] < last['EMA10'] and
                    last['RSI'] < 45 and
                    last['Close'] < last['Open']
                )

                st.subheader("📡 SIGNAL")

                if buy:
                    st.success(f"🟢 BUY ({duration}) 💰")
                elif sell:
                    st.error(f"🔴 SELL ({duration}) ⚡")
                else:
                    st.warning("⚪ ATTENDS")

            except Exception as e:
                st.error("❌ Erreur corrigée automatiquement, réessaie")
