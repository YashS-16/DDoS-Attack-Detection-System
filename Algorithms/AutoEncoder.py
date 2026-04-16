import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, QuantileTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import classification_report, confusion_matrix

print(" --- Autoencoder Model ---")

# 1. Load data
data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')
X = data.drop('Label', axis=1)
y = data['Label']

# 2. Clip extreme outliers: cap at 99.9th percentile per feature
for col in X.columns:
    upper = X[col].quantile(0.999)
    lower = X[col].quantile(0.001)
    X[col] = X[col].clip(lower, upper)

# 3. Use a sample (e.g., 30% for speed)
X, _, y, _ = train_test_split(X, y, train_size=0.3, random_state=42, stratify=y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Use QuantileTransformer to map to Gaussian-like distribution (handles extremes)
scaler = QuantileTransformer(output_distribution='normal', random_state=42)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Use only normal samples for training, and take a reasonable sample
X_train_normal = X_train_scaled[y_train == 0]
sample_size = 50000  # adjust based on memory/time
if len(X_train_normal) > sample_size:
    X_train_normal = X_train_normal[:sample_size]
print(f"Training on {len(X_train_normal)} normal samples, {X_train_normal.shape[1]} features")

# 6. Build a shallow autoencoder (smaller = more stable)
autoencoder = MLPRegressor(
    hidden_layer_sizes=(64, 32, 16, 32, 64),  # symmetric
    activation='relu',
    solver='adam',
    alpha=0.001,           # L2 regularization
    batch_size=256,
    learning_rate='adaptive',
    learning_rate_init=0.001,
    max_iter=50,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=10,
    tol=0.0001,
    random_state=42,
    verbose=True
)

print("Training...")
autoencoder.fit(X_train_normal, X_train_normal)

# 7. Compute reconstruction error on a validation subset (from training normal)
val_size = min(5000, len(X_train_normal))
X_val = X_train_normal[:val_size]
recon_val = autoencoder.predict(X_val)
val_errors = np.mean((X_val - recon_val) ** 2, axis=1)
threshold = np.percentile(val_errors, 90)
print(f"Threshold (99th percentile): {threshold:.6f}")

# 8. Evaluate on test subset
test_size = min(10000, len(X_test_scaled))
X_test_sub = X_test_scaled[:test_size]
y_test_sub = y_test[:test_size]

recon_test = autoencoder.predict(X_test_sub)
test_errors = np.mean((X_test_sub - recon_test) ** 2, axis=1)
y_pred = (test_errors > threshold).astype(int)

print("\n--- Classification Report ---")
print(classification_report(y_test_sub, y_pred))

cm = confusion_matrix(y_test_sub, y_pred)
sns.heatmap(cm, annot=True, fmt='d')
plt.title("Autoencoder Confusion Matrix")
plt.show()

# 9. Plot error distribution
plt.figure()
sns.histplot(test_errors[y_test_sub == 0], color='green', label='Normal', bins=50, alpha=0.5)
sns.histplot(test_errors[y_test_sub == 1], color='red', label='Attack', bins=50, alpha=0.5)
plt.axvline(threshold, color='blue', linestyle='--', label='Threshold')
plt.title("Reconstruction Error Distribution")
plt.legend()
plt.show()

# 10. Save model, scaler, threshold
os.makedirs("Models", exist_ok=True)
joblib.dump(autoencoder, "Models/autoencoder_mlp.pkl")
joblib.dump(scaler, "Models/quantile_scaler.pkl")
joblib.dump(threshold, "Models/autoencoder_threshold_mlp.pkl")
print("All saved.")