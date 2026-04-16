import numpy as np
import pandas as pd
import joblib

autoencoder = joblib.load("Models/autoencoder_mlp.pkl")
scaler = joblib.load("Models/quantile_scaler.pkl")
threshold = joblib.load("Models/autoencoder_threshold_mlp.pkl")

def compute_error(data_row):
    df = pd.DataFrame([data_row])
    scaled = scaler.transform(df)
    recon = autoencoder.predict(scaled)
    error = np.mean((scaled - recon) ** 2)
    return error

def detect_anomaly(data_row):
    error = compute_error(data_row)
    is_anomaly = error > threshold
    return int(is_anomaly), error