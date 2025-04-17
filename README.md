# 🧂 Retail Sugar Price Forecasting (India)

A complete pipeline to forecast monthly retail sugar prices in India using LSTM-based time series modeling. Built with a modular structure that automates the entire workflow—from data download to visualization and deployment.

---

## 🚀 Features

- 📦 End-to-end pipeline: `run_pipeline.py`
- 📉 LSTM model trained on rolling mean differenced price series
- 🔮 Single-step and multi-month forecasting
- 🧠 Drift detection for incoming data
- 🌐 FastAPI deployment for real-time inference
- 🎨 Streamlit dashboard with interactive forecasting
- 📄 Embedded EDA report and forecast logs

---

## 📁 Project Structure

Foundation-Project_Group-14/
├── data/
│   └── cleaned/                      # Cleaned WFP files pushed from pipeline
├── models/                          # Trained LSTM model + scaler (.h5, .pkl)
├── notebooks/
│   ├── eda_report.html              # EDA summary
│   └── *.ipynb                      # Training, Prediction notebooks (for submission)
├── app.py                           # Streamlit dashboard
├── serve_model.py                   # FastAPI endpoint
├── predict.py                       # Predict future sugar prices
├── train.py                         # Train LSTM model on latest data
├── clean_data.py                    # Clean and filter raw sugar price data
├── download_and_push_wfp_data.py    # Pull latest dataset from WFP
├── run_pipeline.py                  # Master orchestrator script
├── forecast_log.csv                 # Log of all forecasts
├── requirements.txt                 # Python dependencies
└── README.md                        # This file

---

## 🧩 How It Works

1. **Data Download**  
   `download_and_push_wfp_data.py` downloads latest WFP CSV and commits to GitHub.

2. **Data Cleaning**  
   `clean_data.py` filters only **retail sugar prices**, formats types, generates an EDA report.

3. **Training**  
   `train.py` trains an LSTM model on the rolling mean differenced series and saves model + scaler.

4. **Prediction**  
   `predict.py` supports single and multi-month recursive forecasts.

5. **Serving via API**  
   `serve_model.py` provides `/predict?n=6` for dynamic forecasting via FastAPI.

6. **Interactive UI**  
   `app.py` (Streamlit) lets users:
   - Choose forecast horizon (1–12 months)
   - View forecast tables and line charts
   - Compare against previous year
   - Explore historical trends
   - Download logs and EDA reports

---

## 🛠️ Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/Neeti3107/Foundation-Project_Group-14.git
cd Foundation-Project_Group-14

# 2. Create and activate environment
conda create -n sugar-forecast python=3.9 -y
conda activate sugar-forecast

# 3. Install requirements
pip install -r requirements.txt

# 4. Run pipeline to retrain model
python run_pipeline.py

# 5. Start FastAPI server (in a new terminal)
uvicorn serve_model:app --reload

# 6. Launch Streamlit dashboard
streamlit run app.py

