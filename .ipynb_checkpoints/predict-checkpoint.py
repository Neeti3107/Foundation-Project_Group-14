"""predict.py -- multi‑month rolling‑mean LSTM forecast

Usage:
    python predict.py                # 1‑month forecast
    python predict.py 6              # 6‑month forecast

Key functions
-------------
forecast_n_months(n) -> list[dict]
    returns list of {'month': 'May 2025', 'price': 45.12}

forecast_next_month(return_results=True|False)
    backwards‑compat wrapper (n=1)

The script locks random seed for reproducibility and is
imported by FastAPI & Streamlit.
"""

import os, random, re, requests
from datetime import datetime
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import load_model
import joblib

# === reproducible seed ===
SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# ------------------------------------------------------------
# helper: latest cleaned csv from GitHub
# ------------------------------------------------------------
def get_latest_cleaned_csv_url(user, repo, path="data/cleaned"):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    files = requests.get(api_url).json()
    csv_files = [
        (f['name'], re.search(r"(\d{4}-\d{2}-\d{2})", f['name']))
        for f in files if f['name'].endswith('.csv')
    ]
    latest = sorted([f for f in csv_files if f[1]], key=lambda x: x[1].group(1))[-1][0]
    return f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}/{latest}"

# ------------------------------------------------------------
# load model + scaler (latest)
# ------------------------------------------------------------
def get_latest_model_files(model_dir="models"):
    files = os.listdir(model_dir)
    models = sorted([f for f in files if f.startswith('lstm_model_rolling_diff') and f.endswith('.h5')])
    scalers = sorted([f for f in files if f.startswith('lstm_scaler_rolling_diff') and f.endswith('.pkl')])
    if not models or not scalers:
        raise FileNotFoundError("No saved model/scaler found in models/")
    return os.path.join(model_dir, models[-1]), os.path.join(model_dir, scalers[-1])

# ------------------------------------------------------------
# core forecasting
# ------------------------------------------------------------
def forecast_n_months(n=1):
    """Return list of dicts for next n months."""
    if n < 1:
        raise ValueError("n must be >=1")
    # data
    url = get_latest_cleaned_csv_url("Neeti3107", "Foundation-Project_Group-14")
    df = pd.read_csv(url, parse_dates=['date'])
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    df['month'] = df['date'].dt.to_period('M')
    df_m = df.groupby('month')['price'].mean().reset_index()
    df_m['month'] = df_m['month'].dt.to_timestamp()
    df_m.set_index('month', inplace=True)
    # rolling mean diff
    df_m['rolling_mean'] = df_m['price'].rolling(12).mean()
    df_m['rolling_mean_diff'] = df_m['rolling_mean'] - df_m['rolling_mean'].shift()
    series = df_m['rolling_mean_diff'].dropna()
    # load model
    model_path, scaler_path = get_latest_model_files()
    model = load_model(model_path, compile=False)
    scaler = joblib.load(scaler_path)
    # recursive forecasting
    results = []
    last_rolling_mean = df_m['rolling_mean'].iloc[-1]
    last_diff_series = series.copy()
    for i in range(n):
        last12 = last_diff_series[-12:].values.reshape(-1,1)
        scaled = scaler.transform(last12)
        X_input = scaled.reshape((1, 12, 1))
        pred_scaled = model.predict(X_input, verbose=0)
        pred_diff = scaler.inverse_transform(pred_scaled).flatten()[0]
        # update series
        next_month = last_diff_series.index[-1] + pd.DateOffset(months=1)
        last_diff_series.loc[next_month] = pred_diff
        # compute price
        last_rolling_mean = last_rolling_mean + pred_diff
        results.append({
            'month': next_month.strftime('%B %Y'),
            'price': round(last_rolling_mean, 2)
        })
    return results

# backwards‑compat: 1‑step
def forecast_next_month(return_results=False):
    res = forecast_n_months(1)
    if return_results:
        return res[0]['month'], res[0]['price']
    print(f"📅 {res[0]['month']} → ₹{res[0]['price']}")

# CLI usage
if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = forecast_n_months(n)
    for row in out:
        print(f"📅 {row['month']} → ₹{row['price']}")
