import streamlit as st
import yfinance as yf
import pandas as pd
import time
from ta.momentum import RSIIndicator

st.set_page_config(page_title="Pocket Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT")

# Choix utilisateur
symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# 🔁 Fonction stable pour récupérer données
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

# 🚀 Bouton
if st.button("🚀 GET SIGNAL"):
    data = get_data(symbol)

    if data is None or data.empty:
        st.error("❌ Données indisponibles, réessaie dans quelques secondes")
    else:
        data = data.dropna()

        if len(data) < 20:
            st.warning("⚠️ Pas assez de données")
        else:
            try:
                # 🔥 FIX FORMAT DATA
                close = data["Close"]
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close = pd.Series(close).astype(float)

                # 📊 INDICATEURS
                data['EMA5'] = close.ewm(span=5).mean()
                data['EMA10'] = close.ewm(span=10).mean()
                data['RSI'] = RSIIndicator(close, window=7).rsi()

                # 🔥 VALEURS PROPRES
                last_close = close.iloc[-1]
                last_open = data['Open'].iloc[-1]
                last_ema5 = data['EMA5'].iloc[-1]
                last_ema10 = data['EMA10'].iloc[-1]
                last_rsi = data['RSI'].iloc[-1]

                # 🎯 STRATÉGIE
                buy = (
                    last_ema5 > last_ema10 and
                    last_rsi > 55 and
                    last_close > last_open
                )

                sell = (
                    last_ema5 < last_ema10 and
                    last_rsi < 45 and
                    last_close < last_open
                )

                st.subheader("📡 SIGNAL")

                if buy:
                    st.success(f"🟢 BUY ({duration}) 💰")
                    st.info("👉 Clique UP")
                elif sell:
                    st.error(f"🔴 SELL ({duration}) ⚡")
                    st.info("👉 Clique DOWN")
                else:
                    st.warning("⚪ ATTENDS (pas de bon signal)")

            except Exception as e:
                st.error("❌ Petite erreur technique, réessaie")
