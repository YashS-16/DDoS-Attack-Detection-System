import numpy as np
import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

autoencoder = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_mlp.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl"))
threshold = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl"))



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