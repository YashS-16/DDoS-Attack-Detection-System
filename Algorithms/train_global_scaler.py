import pandas as pd
import joblib
import os

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

print("--- Training Global Scaler ---")

# ------ PATH SETUP (IMPORTANT) ------ #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../Data/cleaned_data/processed_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "../Models")

os.makedirs(MODEL_DIR, exist_ok=True)

# ------ LOAD DATA ------ #

data = pd.read_csv(DATA_PATH)

X = data.drop('Label', axis=1)
y = data['Label']

# ------ SPLIT ------ #

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ------ TRAIN SCALER ------ #

scaler = StandardScaler()
scaler.fit(X_train)

# ------ SAVE ------ #

SCALER_PATH = os.path.join(MODEL_DIR, "global_scaler.pkl")

joblib.dump(scaler, SCALER_PATH)

print(f"Global scaler saved to {SCALER_PATH}")