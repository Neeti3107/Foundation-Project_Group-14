import pandas as pd
import os
from datetime import datetime
from pandas_profiling import ProfileReport
import subprocess
import glob

# === CONFIG ===
repo_path = r"C:\Users\neeti\Documents\ISB_Class of Summer_2025\04 Term 4\Foundation\Foundation-Project_Group-14"
data_folder = os.path.join(repo_path, "data")
clean_folder = os.path.join(data_folder, "cleaned")
report_folder = os.path.join(repo_path, "reports")
os.makedirs(clean_folder, exist_ok=True)
os.makedirs(report_folder, exist_ok=True)

# === FILE PATHS ===
today = datetime.now().strftime("%Y-%m-%d")
raw = glob.glob(os.path.join(data_folder, "wfp_food_prices_india_*.csv"))
if not raw:
    raise FileNotFoundError("❌ No raw WFP files found in data folder.")

raw_url = max(raw, key=os.path.getmtime)
print(f"📄 Loading dataset: {os.path.basename(raw_url)}")
cleaned_file = os.path.join(clean_folder, f"retail_sugar_prices_{today}.csv")
report_file = os.path.join(report_folder, f"retail_sugar_profile_{today}.html")

def clean_and_save_data():
    print("📄 Loading dataset from GitHub...")
    df = pd.read_csv(raw_url, skiprows=[1])  # Skip 2nd row if garbage

    # Clean & transform
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['commodity'] = df['commodity'].astype(str).str.strip().str.lower()
    df['pricetype'] = df['pricetype'].astype(str).str.strip().str.lower()
    df = df.dropna(subset=['date', 'price'])

    # Filter for sugar + retail
    df_filtered = df[(df['commodity'] == 'sugar') & (df['pricetype'] == 'retail')]

    # Save filtered data
    if not df_filtered.empty:
        df_filtered.to_csv(cleaned_file, index=False)
        print(f"✅ Cleaned file saved: {cleaned_file}")

        # Generate profile report
        print("📊 Generating profile report...")
        profile = ProfileReport(df_filtered, title="Retail Sugar Price Data Profile", explorative=True)
        profile.to_file(report_file)
        print(f"✅ Profile report saved: {report_file}")
    else:
        print("⚠️ No matching 'sugar' + 'retail' records found. Skipping save/report.")

    return cleaned_file, report_file if not df_filtered.empty else (None, None)

def git_push_files(files):
    os.chdir(repo_path)
    try:
        for file in files:
            if file and os.path.exists(file):
                subprocess.run(["git", "add", file], check=True)

        commit_msg = f"Automated: Cleaned data + profile report on {today}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)

        if "nothing to commit" in result.stdout.lower():
            print("ℹ️ No new changes to commit.")
        else:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("🚀 Files committed and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

if __name__ == "__main__":
    cleaned_csv, profile_html = clean_and_save_data()
    git_push_files([cleaned_csv, profile_html])