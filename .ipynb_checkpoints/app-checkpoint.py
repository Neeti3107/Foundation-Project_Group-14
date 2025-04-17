# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import re
import os
from datetime import datetime
from streamlit.components.v1 import html

st.set_page_config(page_title="Sugar Price Forecast", layout="wide")

# === Header ===
st.title("🧂 Retail Sugar Price Forecast (India)")
st.caption("Powered by LSTM + FastAPI + Streamlit")

# === 1. Forecast Horizon Inputs ===
st.sidebar.header("🔁 Forecast Controls")
forecast_type = st.sidebar.radio("Select Forecast Horizon", ["Short-term (1–6 months)", "Long-term (6+ months)"])
months_ahead = st.sidebar.slider("How many months ahead?", min_value=1, max_value=12,
                                  value=1 if "Short" in forecast_type else 6)
st.sidebar.success(f"⏳ Forecasting {months_ahead} month(s) ahead")

st.info(f"🔄 You selected **{forecast_type}** → Forecasting **{months_ahead} month(s)** ahead.")

# === Helper Function to Get Latest CSV from GitHub ===
def get_latest_csv_url(user, repo, path="data/cleaned"):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    files = requests.get(api_url).json()
    csv_files = [(f['name'], re.search(r'(\d{4}-\d{2}-\d{2})', f['name'])) for f in files if f['name'].endswith(".csv")]
    latest = sorted([f for f in csv_files if f[1]], key=lambda x: x[1].group(1))[-1][0]
    return f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}/{latest}"

# === Load Historical Data for Comparison ===
@st.cache_data
def load_historical_df():
    csv_url = get_latest_csv_url("Neeti3107", "Foundation-Project_Group-14")
    df = pd.read_csv(csv_url, parse_dates=['date'])
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df.dropna(subset=['date', 'price'])

# ✅ Load the historical dataset
df = load_historical_df()

try:
    api_url = f"http://127.0.0.1:8000/predict?n={months_ahead}"
    response = requests.get(api_url)
    forecast = response.json()

    # === Single Month Forecast ===
    if months_ahead == 1:
        st.subheader("🔮 Latest Forecast")
        first = forecast["forecasts"][0]

        col1, col2 = st.columns(2)
        col1.success(f"📅 Forecast Month: **{first['month']}**")
        col2.metric("Predicted Price (INR)", f"₹{first['price']}")

        # 🔙 Add Actual Price Last Year Column (No Graph)
        st.subheader("📄 Forecast vs Last Year (Single Month)")
        forecast_month_dt = pd.to_datetime(first["month"], format='%B %Y')
        last_year_month_dt = forecast_month_dt - pd.DateOffset(years=1)

        df['month'] = df['date'].dt.to_period('M')
        df_monthly = df.groupby('month')['price'].mean().reset_index()
        df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

        actual_last_year = df_monthly[df_monthly['month'] == last_year_month_dt]['price'].values
        actual_last_year = actual_last_year[0] if len(actual_last_year) > 0 else None

        table_data = {
            "Forecast Month": [first["month"]],
            "Forecasted Price (INR)": [first["price"]],
            "Actual Price (Last Year)": [f"{actual_last_year:.2f}" if actual_last_year else "N/A"]
        }
        st.table(pd.DataFrame(table_data))

    # === Multi-Month Forecast ===
    elif months_ahead > 1:
        st.subheader("📊 Multi-month Forecast")
        df_multi = pd.DataFrame(forecast["forecasts"])
        st.dataframe(df_multi)

        # 📉 Line Chart using Matplotlib
        import matplotlib.pyplot as plt
        st.subheader("📉 Forecasted Sugar Prices (Matplotlib)")

        df_multi['month'] = pd.to_datetime(df_multi['month'], format='%B %Y', errors='coerce')
        df_multi['price'] = pd.to_numeric(df_multi['price'], errors='coerce')
        df_multi = df_multi.dropna(subset=['month', 'price'])

        if len(df_multi) > 1:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_multi['month'], df_multi['price'], marker='o', linestyle='-', color='teal')
            ax.set_title("Forecasted Retail Sugar Prices")
            ax.set_xlabel("Month")
            ax.set_ylabel("Price (INR)")
            ax.grid(True)
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        else:
            st.info("ℹ️ Forecast chart is available for 2+ months.")

        # 🔙 Compare with Last Year's Price
        st.subheader("📉 Forecast vs. Same Month Last Year")
        df['month'] = df['date'].dt.to_period('M')
        df_monthly = df.groupby('month')['price'].mean().reset_index()
        df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

        actual_lookup = dict(zip(df_monthly['month'], df_monthly['price']))
        last_year_months = df_multi['month'] - pd.DateOffset(years=1)
        actual_prices_last_year = [actual_lookup.get(m, None) for m in last_year_months]

        df_compare = pd.DataFrame({
            "Forecast Month": df_multi['month'],
            "Forecasted Price": df_multi['price'].values,
            "Actual Price (Last Year)": actual_prices_last_year
        }).dropna()

        if not df_compare.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_compare['Forecast Month'], df_compare['Forecasted Price'], marker='o', label='Forecasted Price', color='teal')
            ax.plot(df_compare['Forecast Month'], df_compare['Actual Price (Last Year)'], marker='o', label='Actual Price Last Year', color='orange')
            ax.set_title("Forecast vs. Last Year’s Retail Sugar Prices")
            ax.set_xlabel("Month")
            ax.set_ylabel("Price (INR)")
            ax.legend()
            ax.grid(True)
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        else:
            st.warning("⚠️ No matching historical data available for same months last year.")

except Exception as e:
    st.error("⚠️ Could not fetch forecast from API.")
    st.text(str(e))


    
except Exception as e:
    st.error("⚠️ Could not fetch forecast from API.")
    st.text(str(e))


# === 3. Historical Price Trend ===
st.subheader("📊 Historical Trend of Monthly Prices")

def get_latest_csv_url(user, repo, path="data/cleaned"):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    files = requests.get(api_url).json()
    csv_files = [(f['name'], re.search(r'(\d{4}-\d{2}-\d{2})', f['name'])) for f in files if f['name'].endswith(".csv")]
    latest = sorted([f for f in csv_files if f[1]], key=lambda x: x[1].group(1))[-1][0]
    return f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}/{latest}"

try:
    csv_url = get_latest_csv_url("Neeti3107", "Foundation-Project_Group-14")
    st.caption(f"📁 Using data from: {csv_url.split('/')[-1]}")

    df = pd.read_csv(csv_url, parse_dates=['date'])

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'price'])

    df['month'] = df['date'].dt.to_period('M')
    df_monthly = df.groupby('month')['price'].mean().reset_index()
    df_monthly['month'] = df_monthly['month'].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=df_monthly, x='month', y='price', marker='o', ax=ax)
    ax.set_title("Average Monthly Retail Sugar Price")
    ax.set_xlabel("Month")
    ax.set_ylabel("Price (INR)")
    ax.grid(True)
    st.pyplot(fig)

except Exception as e:
    st.error("❌ Error loading historical data.")
    st.text(str(e))

# === 4. Forecast Log Viewer + Download ===
st.subheader("🗂 Forecast Log")

try:
    df_log = pd.read_csv("forecast_log.csv")
    st.dataframe(df_log.sort_values("timestamp", ascending=False), use_container_width=True)

    # ✅ Download button
    st.download_button(
        label="⬇️ Download Forecast Log as CSV",
        data=df_log.to_csv(index=False),
        file_name="forecast_log.csv",
        mime="text/csv"
    )
except FileNotFoundError:
    st.warning("⚠️ Forecast log not found yet. Run a forecast first.")

# === 5. Embedded EDA Report + Download Button ===
st.subheader("📄 EDA Report")

eda_path = os.path.join("notebooks", "eda_report.html")

if os.path.exists(eda_path):
    # ✅ Embed report
    with open(eda_path, 'r', encoding='utf-8') as f:
        eda_html = f.read()
        html(eda_html, height=600, scrolling=True)

    # ✅ Add download button
    with open(eda_path, "rb") as file:
        btn = st.download_button(
            label="⬇️ Download EDA Report (HTML)",
            data=file,
            file_name="eda_report.html",
            mime="text/html"
        )
else:
    st.info("ℹ️ EDA report not found. Make sure it's saved as `notebooks/eda_report.html`.")
