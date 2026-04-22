import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, auc,
    confusion_matrix, classification_report,
    precision_recall_curve
)

print("--- Logistic Regression Training ---")

# ------ FUNCTIONS ------ #

def evaluate_model(name, y_train, y_train_pred, y_train_prob,
                   y_test, y_test_pred, y_test_prob):

    print(f"\n------ {name} PERFORMANCE ------\n")

    def metrics(split, y_true, y_pred, y_prob):
        print(f"\n--- {split} ---")
        print("Accuracy :", accuracy_score(y_true, y_pred))
        print("Precision:", precision_score(y_true, y_pred))
        print("Recall   :", recall_score(y_true, y_pred))
        print("F1 Score :", f1_score(y_true, y_pred))

        if y_prob is not None:
            print("ROC-AUC  :", roc_auc_score(y_true, y_prob))

    metrics("TRAIN", y_train, y_train_pred, y_train_prob)
    metrics("TEST", y_test, y_test_pred, y_test_prob)


def plot_confusion(y_true, y_pred, title):
    plt.figure()
    sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d')
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()


def plot_roc(y_true, y_prob, title):
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
    plt.plot([0, 1], [0, 1], '--')
    plt.legend()
    plt.title(title)
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.show()


def plot_pr(y_true, y_prob, title):
    p, r, _ = precision_recall_curve(y_true, y_prob)

    plt.figure()
    plt.plot(r, p)
    plt.title(title)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.show()

# Saving models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../Models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ------ LOAD DATA ------ #

DATA_PATH = os.path.join(BASE_DIR, "../Data/cleaned_data/processed_data.csv")

data = pd.read_csv(DATA_PATH)
X = data.drop('Label', axis=1)
y = data['Label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------ SCALING ------ #

scaler = joblib.load("Models/global_scaler.pkl")

X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=X.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

# ------ TRAIN ------ #

base_model = LogisticRegression(
    C=0.01,
    max_iter=1000,
    class_weight='balanced',
    random_state=42
)

base_model.fit(X_train_scaled, y_train)

model = CalibratedClassifierCV(base_model, method='sigmoid', cv='prefit')
model.fit(X_train_scaled, y_train)

# ------ PREDICT ------ #

y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

y_train_pred = model.predict(X_train_scaled)
y_train_prob = model.predict_proba(X_train_scaled)[:, 1]

# ------ EVALUATE ------ #

evaluate_model("Logistic Regression",
               y_train, y_train_pred, y_train_prob,
               y_test, y_pred, y_prob)

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

# ------ PLOTS ------ #

plot_confusion(y_train, y_train_pred, "LR Train CM")
plot_confusion(y_test, y_pred, "LR Test CM")

plot_roc(y_test, y_prob, "LR ROC")
plot_pr(y_test, y_prob, "LR PR Curve")

# ------ MODEL QUALITY CHECK ------ #

recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc_score = roc_auc_score(y_test, y_prob)
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_pred)

print("\n------ MODEL QUALITY CHECK ------\n")

if recall > 0.90:
    print("Excellent Recall (Good for DDoS detection)")
elif recall > 0.80:
    print("Moderate Recall (Can improve)")
else:
    print("Poor Recall (Missing attacks)")

if abs(train_acc - test_acc) < 0.05:
    print("No Overfitting")
else:
    print("Overfitting Detected")

if auc_score > 0.90:
    print("Strong Model (High ROC-AUC)")
elif auc_score > 0.80:
    print("Average Model")
else:
    print("Weak Model")

print(f"\nFinal Summary:")
print(f"Recall: {recall:.3f} | F1: {f1:.3f} | AUC: {auc_score:.3f}")

# ------ SAVE ------ #

joblib.dump(model, os.path.join(MODEL_DIR, "logistic_regression.pkl"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "global_scaler.pkl"))

