import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, auc, precision_recall_curve
)

print('Model Training Started....')

# ---------------- SETTINGS ---------------- #

FAST_MODE = True      # 🔥 change to False for final run
SHOW_PLOTS = False    # disable plots for speed

# ---------------- FUNCTIONS ---------------- #

def evaluate_model(name, y_train, y_train_pred, y_train_prob,
                   y_test, y_test_pred, y_test_prob):

    print(f"\n------ {name} PERFORMANCE ------\n")

    def metrics(split, y_true, y_pred, y_prob):
        print(f"\n--- {split} ---")
        print("Accuracy :", accuracy_score(y_true, y_pred))
        print("Precision:", precision_score(y_true, y_pred, zero_division=0))
        print("Recall   :", recall_score(y_true, y_pred, zero_division=0))
        print("F1 Score :", f1_score(y_true, y_pred, zero_division=0))

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


# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../Models")
DATA_PATH = os.path.join(BASE_DIR, "../Data/cleaned_data/processed_data.csv")

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------- LOAD DATA ---------------- #

data = pd.read_csv(DATA_PATH)

X = data.drop('Label', axis=1)
y = data['Label']

# ---------------- SPLIT ---------------- #

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ---------------- TRAIN ---------------- #

model = RandomForestClassifier(
    n_estimators=50 if FAST_MODE else 100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ---------------- LEAKAGE TEST ---------------- #

print("\nRunning Leakage Test...")

if FAST_MODE:
    X_cv = X.sample(frac=0.3, random_state=42)
    y_cv = y.loc[X_cv.index]
else:
    X_cv = X
    y_cv = y

y_shuffled = y_cv.sample(frac=1, random_state=42).values

model_leak = RandomForestClassifier(n_estimators=50, random_state=42)

leak_scores = cross_val_score(model_leak, X_cv, y_shuffled, cv=3 if FAST_MODE else 5)

print("Leakage test score:", leak_scores.mean())

# ---------------- PREDICT ---------------- #

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

y_train_pred = model.predict(X_train)
y_train_prob = model.predict_proba(X_train)[:, 1]

# ---------------- EVALUATE ---------------- #

evaluate_model("Random Forest",
               y_train, y_train_pred, y_train_prob,
               y_test, y_pred, y_prob)

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

# ---------------- MODEL CHECK ---------------- #

recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc_score = roc_auc_score(y_test, y_prob)
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_pred)

print("\n====== MODEL QUALITY CHECK ======\n")

if recall > 0.90:
    print("Excellent Recall (Good for DDoS detection)")
elif recall > 0.80:
    print("Moderate Recall")
else:
    print("Poor Recall (Misses attacks)")

if abs(train_acc - test_acc) < 0.05:
    print("No Overfitting")
else:
    print("Overfitting Detected")

if auc_score > 0.90:
    print("Strong Model")
elif auc_score > 0.80:
    print("Average Model")
else:
    print("Weak Model")

print(f"\nSummary: Recall: {recall:.3f} | F1: {f1:.3f} | AUC: {auc_score:.3f}")

# ---------------- FEATURE IMPORTANCE ---------------- #

if SHOW_PLOTS:
    importance = model.feature_importances_
    feat_imp = pd.Series(importance, index=X.columns).sort_values(ascending=False)

    print("\nTop 20 Features:\n", feat_imp.head(20))

    feat_imp.head(20).plot(kind='bar')
    plt.title('Top 20 Important Features')
    plt.show()

# ---------------- CROSS VALIDATION ---------------- #

print("\nRunning Cross Validation...")

cv = StratifiedKFold(n_splits=3 if FAST_MODE else 5, shuffle=True, random_state=42)

cv_scores = cross_val_score(
    RandomForestClassifier(n_estimators=50, random_state=42),
    X_cv, y_cv, cv=cv
)

print("Cross-validation scores:", cv_scores)
print("Average:", cv_scores.mean())

# ---------------- SAVE ---------------- #

joblib.dump(model, os.path.join(MODEL_DIR, "random_forest.pkl"))

print('\nRandom Forest Model Saved!!')