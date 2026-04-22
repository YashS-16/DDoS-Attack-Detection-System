import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "../Models/attack_type_model.pkl")
le_path = os.path.join(BASE_DIR, "../Models/attack_type_label_encoder.pkl")

model = None
le = None
try:
    model = joblib.load(model_path)
    le = joblib.load(le_path)
    print("Attack type model loaded.")
except Exception as e:
    print(f"Could not load attack type model: {e}")

def classify_attack_type(data_row):
    if model is None or le is None:
        return "Unknown"
    try:
        df = pd.DataFrame([data_row])
        if hasattr(model, 'feature_names_in_'):
            df = df[model.feature_names_in_]
        pred_id = model.predict(df)[0]
        attack = le.inverse_transform([pred_id])[0]
        # Lower intensity filter
        if attack in ["DDoS Attack", "UDP Flood", "SYN Flood"]:
            if data_row.get("Flow Packets/s", 0) < 50:
                return "Normal Traffic"
        return attack
    except Exception as e:
        print(f"Attack type prediction error: {e}")
        return "Unknown"