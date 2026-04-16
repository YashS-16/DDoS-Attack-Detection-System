import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

print("--- Training Global Scaler --- ")

# Load data
data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')
X = data.drop('Label', axis=1)
y = data['Label']

# Split to get training set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Fit scaler on X_train
scaler = StandardScaler()
scaler.fit(X_train)

# Save
import os
os.makedirs("Models", exist_ok=True)
joblib.dump(scaler, "Models/global_scaler.pkl")
print("Global scaler saved to Models/global_scaler.pkl")