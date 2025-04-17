import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from keras.models import Sequential
from keras.layers import LSTM, Dense
import joblib
import os
import re
import requests
from datetime import datetime
import random
import tensorflow as tf

# === Set Seed for Reproducibility ===
SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# === Helper: Get Latest Cleaned CSV from GitHub ===
def get_latest_cleaned_csv_url(user, repo, path="data/cleaned"):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    response = requests.get(api_url)
    files = response.json()
    csv_files = []
    for file in files:
        name = file['name']
        if name.startswith("retail_sugar_prices_") and name.endswith(".csv"):
            match = re.search(r"(\d{4}-\d{2}-\d{2})", name)
            if match:
                csv_files.append((match.group(1), name))
    if not csv_files:
        raise ValueError("❌ No cleaned CSV files found.")
    latest_date, latest_file = sorted(csv_files)[-1]
    print(f"📁 Latest file found: {latest_file}")
    return f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}/{latest_file}"

# === Load Latest Data ===
user = "Neeti3107"
repo = "Foundation-Project_Group-14"
latest_csv_url = get_latest_cleaned_csv_url(user, repo)
df_filtered = pd.read_csv(latest_csv_url, parse_dates=['date'])

# === Monthly Aggregation ===
df_filtered['month'] = df_filtered['date'].dt.to_period('M')
df_country = df_filtered.groupby('month')['price'].mean().reset_index()
df_country['month'] = df_country['month'].dt.to_timestamp()
df_country.set_index('month', inplace=True)
df_data = df_country.copy()

# === Prepare Rolling Mean Differenced Series ===
df_data['rolling_mean'] = df_data['price'].rolling(window=12).mean()
df_data['rolling_mean_diff'] = df_data['rolling_mean'] - df_data['rolling_mean'].shift()
rolling_diff = df_data['rolling_mean_diff'].dropna()

# === Train-Test Split ===
split_date = pd.to_datetime("2019-01-01")
series = rolling_diff
train_series = series[series.index < split_date]

# === Scale and Sequence Preparation ===
scaler = MinMaxScaler()
scaled_series = scaler.fit_transform(train_series.values.reshape(-1, 1))

def create_sequences(data, seq_length=12):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i])
        y.append(data[i])
    return np.array(X), np.array(y)

seq_len = 12
X, y = create_sequences(scaled_series, seq_len)
X = X.reshape((X.shape[0], X.shape[1], 1))

# === LSTM Model Training ===
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(seq_len, 1)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=50, batch_size=16, verbose=0)

# === Save Model and Scaler ===
model_path = "models"
os.makedirs(model_path, exist_ok=True)
model_file = os.path.join(model_path, f"lstm_model_rolling_diff_2025-04-16.h5")
scaler_file = os.path.join(model_path, f"lstm_scaler_rolling_diff_2025-04-16.pkl")

model.save(model_file)
joblib.dump(scaler, scaler_file)
print(f"✅ Model saved to: {model_file}")
print(f"✅ Scaler saved to: {scaler_file}")
