import streamlit as st
import yfinance as yf
from ta.momentum import RSIIndicator

# CONFIG
st.set_page_config(page_title="Pocket Bot", layout="centered")

st.title("⚡ POCKET SIGNAL BOT")

# CHOIX
symbol = st.selectbox("📊 Actif", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
duration = st.selectbox("⏱ Durée", ["1 min", "5 min"])

# BOUTON
if st.button("🚀 GET SIGNAL"):
    data = yf.download(symbol, period="1d", interval="1m")

    # 🔒 Sécurité (évite crash)
    if data is None or data.empty or len(data) < 20:
        st.warning("⚠️ Pas assez de données, réessaie dans quelques secondes")
    else:
        # INDICATEURS
        data['EMA5'] = data['Close'].ewm(span=5).mean()
        data['EMA10'] = data['Close'].ewm(span=10).mean()

        try:
            rsi = RSIIndicator(data['Close'], window=7)
            data['RSI'] = rsi.rsi()
        except:
            st.error("❌ Erreur calcul RSI, réessaie")
            st.stop()

        last = data.iloc[-1]

        # LOGIQUE SCALPING
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
            st.warning("⚪ ATTENDS (pas de bon signal)")

# FOOTER
st.caption("⚠️ Trade avec gestion du risque")

