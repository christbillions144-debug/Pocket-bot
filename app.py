import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="ELITE AI BOT", layout="centered")

st.title("💎 ELITE AI TRADING BOT")

pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD"]
duration = st.selectbox("⏱️ Durée", ["1m", "5m"])

# ======================
# DATA
# ======================
def get_data(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="1m", progress=False)
        if data is None or data.empty:
            return None
        return data.dropna()
    except:
        return None

# ======================
# FEATURES
# ======================
def create_features(df):
    df["return"] = df["Close"].pct_change()
    df["ma5"] = df["Close"].rolling(5).mean()
    df["ma10"] = df["Close"].rolling(10).mean()
    df["volatility"] = df["return"].rolling(10).std()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(7).mean() / loss.rolling(7).mean()
    df["rsi"] = 100 - (100 / (1 + rs))

    df = df.dropna()
    df["target"] = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)

    return df

# ======================
# MODEL
# ======================
def train_model(df):
    features = ["return", "ma5", "ma10", "volatility", "rsi"]
    X = df[features]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=150)
    model.fit(X, y)

    return model

# ======================
# ANALYSE ELITE
# ======================
def analyze(symbol):
    data = get_data(symbol)

    if data is None or len(data) < 50:
        return None

    df = create_features(data)
    model = train_model(df)

    features = ["return", "ma5", "ma10", "volatility", "rsi"]

    last = df[features].iloc[-1].values.reshape(1, -1)

    prediction = model.predict(last)[0]
    proba = model.predict_proba(last)[0]

    confidence = max(proba)

    # 🔥 FILTRE QUALITÉ
    if confidence < 0.6:
        return {"pair": symbol, "signal": "WAIT", "conf": confidence}

    if prediction == 1:
        signal = "CALL"
    else:
        signal = "PUT"

    return {
        "pair": symbol,
        "signal": signal,
        "conf": round(confidence, 2)
    }

# ======================
# BUTTON
# ======================
if st.button("💎 SCAN ELITE AI"):

    results = []

    with st.spinner("Analyse IA en cours..."):
        for p in pairs:
            res = analyze(p)
            if res:
                results.append(res)

    if len(results) == 0:
        st.error("❌ Aucune donnée")
    else:
        # 🏆 meilleur signal
        best = max(results, key=lambda x: x["conf"])

        st.subheader("🏆 MEILLEUR SIGNAL")

        if best["signal"] == "CALL":
            st.success(f"🟢 CALL {best['pair']} (confiance {best['conf']})")
            st.info("👉 Clique UP")
        elif best["signal"] == "PUT":
            st.error(f"🔴 PUT {best['pair']} (confiance {best['conf']})")
            st.info("👉 Clique DOWN")
        else:
            st.warning("⚪ Aucun signal fiable")

        # 📊 détails
        st.subheader("📊 ANALYSE")

        for r in results:
            if r["signal"] == "WAIT":
                st.write(f"⚪ {r['pair']} → WAIT ({r['conf']})")
            elif r["signal"] == "CALL":
                st.write(f"🟢 {r['pair']} → CALL ({r['conf']})")
            else:
                st.write(f"🔴 {r['pair']} → PUT ({r['conf']})")
