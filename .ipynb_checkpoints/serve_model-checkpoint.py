# serve_model.py

# serve_model.py -- FastAPI for sugar price forecasts (multi-step)
from fastapi import FastAPI, Query
from predict import forecast_n_months
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sugar Price Forecast API",
              description="Predict next n months of retail sugar price in INR",
              version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Sugar Forecast API up"}

@app.get("/predict")
def predict(n: int = Query(1, ge=1, le=12, description="Number of months ahead to forecast (1‑12)")):
    res = forecast_n_months(n)
    return {"forecasts": res}
