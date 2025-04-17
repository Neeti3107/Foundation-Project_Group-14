import subprocess
from datetime import datetime
import pandas as pd
import os

# === Step 1: Download Data ===
print("\n📥 Step 1: Downloading latest WFP data...")
subprocess.run(["python", "download_and_push_wfp_data.py"], check=True)

# === Step 2: Clean Data ===
print("\n🧹 Step 2: Cleaning data...")
subprocess.run(["python", "clean.py"], check=True)

# === Step 3: Re-run EDA Notebook on Latest Data ===
print("\n📊 Step 3: Running EDA on latest cleaned data...")
subprocess.run([
    "jupyter", "nbconvert",
    "--execute",                        # ✅ Run the notebook
    "--to", "html",                     # ✅ Convert to HTML
    "--output", "eda_report",          # ✅ Output name (no extension)
    "notebooks/EDA_Report.ipynb"       # ✅ Your notebook path
], check=True)
print("✅ EDA notebook re-executed and saved as HTML.")

# === Step 4: Train Model ===
print("\n🧠 Step 3: Training model...")
subprocess.run(["python", "train.py"], check=True)

# === Step 5: Predict & Extract Output ===
print("\n🔮 Step 4: Forecasting...")
from predict import forecast_next_month  # direct function import

predicted_month, predicted_price = forecast_next_month(return_results=True)

# === Step 6: Log Forecast ===
log_path = "forecast_log.csv"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

log_row = {
    "timestamp": timestamp,
    "forecast_month": predicted_month,
    "predicted_price": round(predicted_price, 2)
}

# Save to CSV
if os.path.exists(log_path):
    df_log = pd.read_csv(log_path)
    df_log = pd.concat([df_log, pd.DataFrame([log_row])], ignore_index=True)
else:
    df_log = pd.DataFrame([log_row])

df_log.to_csv(log_path, index=False)
print(f"\n🗂 Forecast logged to: {log_path}")
