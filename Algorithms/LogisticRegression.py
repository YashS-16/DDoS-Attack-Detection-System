import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV

print("--- Logistic Regression Training ---")

# Load data
data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')
X = data.drop('Label', axis=1)
y = data['Label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load scaler
scaler = joblib.load("Models/global_scaler.pkl")

# ✅ FIX: Keep DataFrame format (IMPORTANT)
X_train_scaled = pd.DataFrame(
    scaler.transform(X_train),
    columns=X.columns
)

X_test_scaled = pd.DataFrame(
    scaler.transform(X_test),
    columns=X.columns
)

# ✅ STEP 1: Train base model
base_model = LogisticRegression(
    C=0.01,
    max_iter=1000,
    class_weight='balanced',
    random_state=42
)

base_model.fit(X_train_scaled, y_train)

# ✅ STEP 2: Proper calibration
model = CalibratedClassifierCV(base_model, method='sigmoid', cv='prefit')
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d')
plt.title("Logistic Regression Confusion Matrix")
plt.show()

# Save model
joblib.dump(model, "Models/logistic_regression.pkl")
print("LR model saved.")