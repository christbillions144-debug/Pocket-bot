import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

# CONFIG
st.set_page_config(page_title="Pocket Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT")

symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

if st.button("🚀 GET SIGNAL"):
    data = yf.download(symbol, period="1d", interval="1m")

    # 🔒 Nettoyage des données
    if data is None or data.empty:
        st.error("❌ Données indisponibles, réessaie")
    else:
        data = data.dropna()

        if len(data) < 20:
            st.warning("⚠️ Pas assez de données")
        else:
            try:
                close = pd.Series(data['Close']).astype(float)

                data['EMA5'] = close.ewm(span=5).mean()
                data['EMA10'] = close.ewm(span=10).mean()

                rsi = RSIIndicator(close, window=7)
                data['RSI'] = rsi.rsi()

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
                    st.info("👉 Clique UP maintenant")
                elif sell:
                    st.error(f"🔴 SELL ({duration}) ⚡")
                    st.info("👉 Clique DOWN maintenant")
                else:
                    st.warning("⚪ ATTENDS")

            except Exception as e:
                st.error("❌ Erreur technique, réessaie dans 5 secondes")

