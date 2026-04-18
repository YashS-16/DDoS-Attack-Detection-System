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

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate_model(name, y_train, y_train_pred, y_train_prob,
                   y_test, y_test_pred, y_test_prob):
    
    print(f"\n====== {name} PERFORMANCE ======\n")

    def print_metrics(split, y_true, y_pred, y_prob):
        print(f"\n--- {split} ---")
        print("Accuracy :", accuracy_score(y_true, y_pred))
        print("Precision:", precision_score(y_true, y_pred))
        print("Recall   :", recall_score(y_true, y_pred))
        print("F1 Score :", f1_score(y_true, y_pred))
        
        if y_prob is not None:
            print("ROC-AUC  :", roc_auc_score(y_true, y_prob))

    print_metrics("TRAIN", y_train, y_train_pred, y_train_prob)
    print_metrics("TEST", y_test, y_test_pred, y_test_prob)

