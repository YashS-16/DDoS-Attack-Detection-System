import joblib
import numpy as np
import pandas as pd
import os
from anomaly import detect_anomaly
import warnings
warnings.filterwarnings("ignore")

# -------- LOAD MODELS -------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf = joblib.load(os.path.join(BASE_DIR, "../Models/random_forest.pkl"))
xgb = joblib.load(os.path.join(BASE_DIR, "../Models/xgboost.pkl"))
lr = joblib.load(os.path.join(BASE_DIR, "../Models/logistic_regression.pkl"))

scaler = joblib.load(os.path.join(BASE_DIR, "../Models/global_scaler.pkl"))
ae_scaler = joblib.load(os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl"))
threshold = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl"))

feature_columns = scaler.feature_names_in_

print(type(rf))
print(type(xgb))
print(type(lr))

# -------- SMOOTHING -------- #
risk_history = []

def smooth_score(score):
    risk_history.append(score)
    if len(risk_history) > 3:
        risk_history.pop(0)
    return sum(risk_history) / len(risk_history)


# -------- PREDICTION -------- #
def predict(data_row):
    try:
        # -------- PREPROCESS -------- #
        data_df = pd.DataFrame([data_row])
        data_df = data_df[feature_columns]

        data_scaled = scaler.transform(data_df)
        data_scaled = pd.DataFrame(data_scaled, columns=feature_columns)

        # -------- MODEL OUTPUT -------- #
        rf_prob = rf.predict_proba(data_scaled.values)[0][1]
        xgb_prob = xgb.predict_proba(data_scaled.values)[0][1]
        lr_prob = lr.predict_proba(data_scaled.values)[0][1]

        anomaly, error = detect_anomaly(data_row)

        # -------- BASE SCORE -------- #
        base_score = (rf_prob + xgb_prob + lr_prob) / 3 * 100

        # -------- NORMALIZE -------- #
        base_score = base_score * 0.6

        # -------- BOOST -------- #
        boost = 0

        if anomaly:
            boost += 10

        if error > 5:
            boost += 5

        # -------- FINAL SCORE -------- #
        risk_score = base_score + boost

        # -------- CONTROL -------- #
        risk_score = max(0, min(100, risk_score))
        risk_score = smooth_score(risk_score)

        # -------- DEBUG -------- #
        print("RF:", rf_prob, "XGB:", xgb_prob, "LR:", lr_prob,
              "Base:", base_score, "Final:", risk_score)

        return {
            "rf_prob": round(rf_prob, 2),
            "xgb_prob": round(xgb_prob, 2),
            "lr_prob": round(lr_prob, 2),
            "anomaly": anomaly,
            "error": round(error, 2),
            "risk_score": round(risk_score, 2)
        }

    except Exception as e:
        print("Prediction error:", e)

        return {
            "rf_prob": 0,
            "xgb_prob": 0,
            "lr_prob": 0,
            "anomaly": False,
            "error": 0,
            "risk_score": 0
        }