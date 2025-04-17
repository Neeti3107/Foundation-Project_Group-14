import requests
import os
import subprocess
from datetime import datetime
import pandas as pd
from scipy.stats import ks_2samp

# === Setup Paths and File Names ===
repo_path = r"C:\Users\neeti\Documents\ISB_Class of Summer_2025\04 Term 4\Foundation\Foundation-Project_Group-14"
data_folder = os.path.join(repo_path, "data")
log_path = os.path.join(repo_path, "drift_log.csv")

timestamp = datetime.now().strftime("%Y-%m-%d")
save_filename = f"wfp_food_prices_india_{timestamp}.csv"
save_path = os.path.join(data_folder, save_filename)

# WFP Download URL
url = "https://data.humdata.org/dataset/dc663585-4b6f-46ae-a6d6-b2f3e4ea32b5/resource/3b1ff071-6b01-4998-aa62-2f3efb5d4888/download/wfp_food_prices_ind.csv"

# === Step 1: Download the dataset ===
def download_csv():
    os.makedirs(data_folder, exist_ok=True)
    print("📡 Downloading WFP dataset...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ File downloaded and saved to: {save_path}")
    else:
        print(f"❌ Failed to download. Status code: {response.status_code}")
        exit()

# === Step 2: Detect data drift ===
def detect_price_drift():
    all_files = sorted([
        f for f in os.listdir(data_folder)
        if f.startswith("wfp_food_prices_india_") and f.endswith(".csv")
    ])

    if len(all_files) < 2:
        print("ℹ️ Not enough historical data to check for drift.")
        return None

    previous_file = all_files[-2]
    previous_path = os.path.join(data_folder, previous_file)

    try:
        df_old = pd.read_csv(previous_path)
        df_new = pd.read_csv(save_path)

        old_prices = df_old['price'].dropna().astype(float)
        new_prices = df_new['price'].dropna().astype(float)

        stat, p_value = ks_2samp(old_prices, new_prices)
        drift_detected = p_value < 0.05

        print(f"📊 Drift Detection - p-value: {p_value:.4f}")
        if drift_detected:
            print("⚠️ Drift Detected! Price distributions changed significantly.")
        else:
            print("✅ No significant drift detected.")

        # === Step 3: Log to drift_log.csv ===
        log_drift_result(timestamp, p_value, drift_detected)

        return drift_detected

    except Exception as e:
        print(f"⚠️ Drift detection failed: {e}")
        return None

def log_drift_result(date, p_value, drift_flag):
    log_exists = os.path.exists(log_path)
    with open(log_path, 'a') as f:
        if not log_exists:
            f.write("date,p_value,drift_detected\n")
        f.write(f"{date},{p_value:.4f},{drift_flag}\n")
    print("📝 Drift result logged.")

# === Step 4: Push file to GitHub ===
def git_push_file():
    os.chdir(repo_path)
    try:
        subprocess.run(["git", "add", save_path], check=True)
        subprocess.run(["git", "add", log_path], check=True)  # also track drift log

        commit_msg = f"Automated: Updated WFP dataset on {timestamp}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )

        if "nothing to commit" in result.stdout.lower():
            print("ℹ️ No changes to commit.")
        else:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("🚀 File committed and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")

# === Main ===
if __name__ == "__main__":
    download_csv()
    detect_price_drift()
    git_push_file()

