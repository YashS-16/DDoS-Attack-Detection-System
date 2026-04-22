import numpy as np
import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

autoencoder = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_mlp.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl"))
threshold = joblib.load(os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl"))

def compute_error(data_row):
    """Returns reconstruction error (MSE) for the given feature row."""
    df = pd.DataFrame([data_row])
    # Use only features that the autoencoder was trained on
    # (Assume the scaler has feature_names_in_)
    if hasattr(scaler, 'feature_names_in_'):
        df = df[scaler.feature_names_in_]
    scaled = scaler.transform(df)
    recon = autoencoder.predict(scaled, verbose=0)
    error = np.mean((scaled - recon) ** 2)
    return float(error)

def detect_anomaly_continuous(data_row):
    """
    Returns:
        is_anomaly (bool): True if error > threshold
        error (float): raw reconstruction error
    """
    error = compute_error(data_row)
    is_anomaly = error > threshold
    return is_anomaly, error