import joblib
import numpy as np
import pandas as pd
import os
from anomaly import detect_anomaly
import warnings
warnings.filterwarnings("ignore")

# Load models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rf = joblib.load("../Models/random_forest.pkl")
xgb = joblib.load("../Models/xgboost.pkl")
lr = joblib.load("../Models/logistic_regression.pkl")
autoencoder = joblib.load("../Models/autoencoder.pkl")
scaler = joblib.load("../Models/scaler.pkl")
ae_scaler = joblib.load(os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl"))
threshold = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl"))

feature_columns = scaler.feature_names_in_

# smoothing buffer
risk_history = []

def smooth_score(score):
    risk_history.append(score)
    if len(risk_history) > 5:
        risk_history.pop(0)
    return sum(risk_history) / len(risk_history)


def predict(data_row):
    data_df = pd.DataFrame([data_row])
    data_df = data_df[feature_columns]

    data_scaled = scaler.transform(data_df)
    data_scaled = pd.DataFrame(data_scaled, columns=feature_columns)

    rf_prob = rf.predict_proba(data_scaled.values)[0][1]
    xgb_prob = xgb.predict_proba(data_scaled.values)[0][1]
    lr_prob = lr.predict_proba(data_scaled.values)[0][1]

    anomaly, error = detect_anomaly(data_row)

    # 🔥 CLEAN RISK CALCULATION
    risk_score = (0.5 * rf_prob + 0.4 * xgb_prob + 0.1 * lr_prob) * 100

    # Reduce false positives
    if rf_prob < 0.6 and xgb_prob < 0.6:
        risk_score *= 0.3

    # anomaly boost (controlled)
    if anomaly and error > 5:
        risk_score += 8

    # clamp
    risk_score = max(0, min(100, risk_score))

    # smoothing
    risk_score = smooth_score(risk_score)

    return {
        "rf_prob": round(rf_prob, 2),
        "xgb_prob": round(xgb_prob, 2),
        "lr_prob": round(lr_prob, 2),
        "anomaly": anomaly,
        "error": round(error, 2),
        "risk_score": round(risk_score, 2)
    }