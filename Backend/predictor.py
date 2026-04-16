import joblib
import numpy as np
import pandas as pd
from anomaly import detect_anomaly
import warnings
warnings.filterwarnings("ignore")
import random

# Load models
rf = joblib.load("Models/random_forest.pkl")
xgb = joblib.load("Models/xgboost.pkl")
lr = joblib.load("Models/logistic_regression.pkl")
autoencoder = joblib.load("Models/autoencoder.pkl")
scaler = joblib.load("Models/scaler.pkl")

feature_columns = scaler.feature_names_in_

def predict(data_row):
    # Convert to DataFrame with proper shape
    data_df = pd.DataFrame([data_row])
    data_df = data_df[feature_columns]

    # Scale
    data_scaled = scaler.transform(data_df)
    data_scaled = pd.DataFrame(data_scaled, columns=feature_columns)

    # Predictions
    rf_prob = rf.predict_proba(data_scaled.values)[0][1]
    xgb_prob = xgb.predict_proba(data_scaled.values)[0][1]
    lr_prob = lr.predict_proba(data_scaled.values)[0][1]

    # Anomaly
    anomaly, error = detect_anomaly(data_row)

    # Risk score (0-100)
    risk_score = (0.6 * rf_prob + 0.4 * xgb_prob) * 100

    risk_score += random.uniform(-3, 3)
    risk_score = max(0, min(100, risk_score))
    
    if rf_prob < 0.6 and xgb_prob < 0.6:
        risk_score *= 0.5
    if anomaly:
        risk_score += 10
    risk_score = min(risk_score, 100)

    return {
        "rf_prob": round(rf_prob, 2),
        "xgb_prob": round(xgb_prob, 2),
        "lr_prob": round(lr_prob, 2),
        "anomaly": anomaly,
        "error": round(error, 2),
        "risk_score": round(risk_score, 2),
        "models": {
            "rf_prob": round(rf_prob, 2),
            "xgb_prob": round(xgb_prob, 2),
            "lr_prob": round(lr_prob, 2),
        }
    }