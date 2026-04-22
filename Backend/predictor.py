import joblib
import numpy as np
import pandas as pd
import os
from anomaly import detect_anomaly_continuous
import warnings
warnings.filterwarnings("ignore")

# -------- LOAD MODELS -------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf = joblib.load(os.path.join(BASE_DIR, "../Models/random_forest.pkl"))
xgb = joblib.load(os.path.join(BASE_DIR, "../Models/xgboost.pkl"))
lr = joblib.load(os.path.join(BASE_DIR, "../Models/logistic_regression.pkl"))

# These scalers are kept for model input, but we will also use adaptive scaling later
scaler = joblib.load(os.path.join(BASE_DIR, "../Models/global_scaler.pkl"))
ae_scaler = joblib.load(os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl"))
threshold = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl"))

feature_columns = scaler.feature_names_in_

# -------- SMOOTHING & MOMENTUM -------- #
risk_history = []          # for trend detection
last_risk = 50.0           # initial guess

def compute_risk_with_momentum(current_raw_risk):
    global last_risk
    risk_history.append(current_raw_risk)
    if len(risk_history) > 5:
        risk_history.pop(0)
    
    # Trend: difference between last two risks
    if len(risk_history) >= 2:
        trend = risk_history[-1] - risk_history[-2]
        if trend > 10:               # rapid increase
            current_raw_risk += min(20, trend * 1.5)
        elif trend < -10:            # rapid drop
            current_raw_risk = max(0, current_raw_risk + trend * 0.5)
    
    # Exponential smoothing
    smoothed = 0.7 * current_raw_risk + 0.3 * last_risk
    last_risk = smoothed
    return max(0, min(100, smoothed))

# -------- PREDICTION WITH DYNAMIC RISK -------- #
def predict(data_row, pps):
    """
    data_row: dict of aggregated features (already adaptively scaled if desired)
    pps: Flow Packets/s (used as volume factor)
    """
    try:
        # Prepare DataFrame for models
        data_df = pd.DataFrame([data_row])
        # Ensure columns match training order
        data_df = data_df[feature_columns]
        data_scaled = scaler.transform(data_df)

        # Model probabilities (still useful as base signals)
        rf_prob = rf.predict_proba(data_scaled)[0][1]
        xgb_prob = xgb.predict_proba(data_scaled)[0][1]
        lr_prob = lr.predict_proba(data_scaled)[0][1]

        # Continuous anomaly error (not binary)
        anomaly_flag, anomaly_error = detect_anomaly_continuous(data_row)

        # ----- DYNAMIC RISK FORMULA -----
        avg_prob = (rf_prob + xgb_prob + lr_prob) / 3.0

        # Volume factor – makes risk sensitive to packet rate
        if rf_prob > 0.8 and xgb_prob > 0.8 and lr_prob > 0.8:
        # Ignore model probabilities – use intensity only
            if pps < 30:
                raw_risk = 20 + (pps / 30) * 20      # 20–40
            elif pps < 150:
                raw_risk = 40 + ((pps - 30) / 120) * 30   # 40–70
            else:
                raw_risk = 70 + min(30, (pps - 150) / 50 * 30)  # 70–100
        else:
            print(f"pps={pps:.1f} | avg_prob={avg_prob:.2f} | vol_factor={vol_factor:.2f} | raw_risk={raw_risk:.1f}")
    # Original dynamic formula (but with stronger volume factor)
            avg_prob = (rf_prob + xgb_prob + lr_prob) / 3.0
    # More aggressive volume factor
            vol_factor = min(1.0, pps / 150)   # 0–1 linear
            anomaly_contrib = min(25, (anomaly_error / threshold) * 15)
            raw_risk = (avg_prob * 50) + (vol_factor * 40) + anomaly_contrib
    # Apply momentum and smoothing
            final_risk = compute_risk_with_momentum(raw_risk)

        # Debug output
        print(f"RF:{rf_prob:.2f} XGB:{xgb_prob:.2f} LR:{lr_prob:.2f} | "
              f"VolFact:{vol_factor:.2f} AnomErr:{anomaly_error:.4f} | "
              f"RawRisk:{raw_risk:.1f} FinalRisk:{final_risk:.1f}")

        return {
            "rf_prob": round(rf_prob, 2),
            "xgb_prob": round(xgb_prob, 2),
            "lr_prob": round(lr_prob, 2),
            "anomaly": anomaly_flag,
            "error": round(anomaly_error, 4),
            "risk_score": round(final_risk, 2)
        }

    except Exception as e:
        print("Prediction error:", e)
        return {
            "rf_prob": 0,
            "xgb_prob": 0,
            "lr_prob": 0,
            "anomaly": False,
            "error": 0,
            "risk_score": 50 
        }