import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import QuantileTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

print(" --- Autoencoder Model ---")

# ------ FUNCTIONS ------ #

def evaluate_model(name, y_train, y_train_pred,
                   y_test, y_test_pred):

    print(f"\n====== {name} PERFORMANCE ======\n")

    def metrics(split, y_true, y_pred):
        print(f"\n--- {split} ---")
        print("Accuracy :", accuracy_score(y_true, y_pred))
        print("Precision:", precision_score(y_true, y_pred))
        print("Recall   :", recall_score(y_true, y_pred))
        print("F1 Score :", f1_score(y_true, y_pred))

    metrics("TRAIN", y_train, y_train_pred)
    metrics("TEST", y_test, y_test_pred)


def plot_confusion(y_true, y_pred, title):
    plt.figure()
    sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d')
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

# Saving models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "../Models/autoencoder_mlp.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "../Models/quantile_scaler.pkl")
THRESHOLD_PATH = os.path.join(BASE_DIR, "../Models/autoencoder_threshold_mlp.pkl")

# ------ LOAD DATA ------ #

DATA_PATH = os.path.join(BASE_DIR, "../Data/cleaned_data/processed_data.csv")

data = pd.read_csv(DATA_PATH)
X = data.drop('Label', axis=1)
y = data['Label']

# Clip outliers
for col in X.columns:
    X[col] = X[col].clip(X[col].quantile(0.001), X[col].quantile(0.999))

# Sample data
X, _, y, _ = train_test_split(X, y, train_size=0.3, stratify=y, random_state=42)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ------ SCALING ------ #

scaler = QuantileTransformer(output_distribution='normal', random_state=42)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ------ TRAIN ------ #

X_train_normal = X_train_scaled[y_train == 0]

autoencoder = MLPRegressor(
    hidden_layer_sizes=(64, 32, 16, 32, 64),
    max_iter=50,
    batch_size=256,
    early_stopping=True,
    random_state=42,
    verbose=True
)

print("Training...")
autoencoder.fit(X_train_normal, X_train_normal)

# ------ PREDICT ------ #

# Validation threshold
recon_val = autoencoder.predict(X_train_normal[:5000])
val_errors = np.mean((X_train_normal[:5000] - recon_val)**2, axis=1)
threshold = np.percentile(val_errors, 90)

# Train errors
train_recon = autoencoder.predict(X_train_scaled)
train_errors = np.mean((X_train_scaled - train_recon)**2, axis=1)
y_train_pred = (train_errors > threshold).astype(int)

# Test errors
recon_test = autoencoder.predict(X_test_scaled)
test_errors = np.mean((X_test_scaled - recon_test)**2, axis=1)
y_test_pred = (test_errors > threshold).astype(int)

# ------ EVALUATE ------ #

evaluate_model("Autoencoder",
               y_train, y_train_pred,
               y_test, y_test_pred)

print("\n--- Classification Report ---")
print(classification_report(y_test, y_test_pred))

# ------ PLOTS ------ #

plot_confusion(y_test, y_test_pred, "Autoencoder Confusion Matrix")

plt.figure()
sns.histplot(test_errors[y_test == 0], bins=50, alpha=0.5, label="Normal")
sns.histplot(test_errors[y_test == 1], bins=50, alpha=0.5, label="Attack")
plt.axvline(threshold, linestyle='--')
plt.title("Reconstruction Error Distribution")
plt.legend()
plt.show()

# ------ SAVE ------ #

os.makedirs(os.path.join(BASE_DIR, "../Models"), exist_ok=True)
joblib.dump(autoencoder, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
joblib.dump(threshold, THRESHOLD_PATH)

print("All saved.")