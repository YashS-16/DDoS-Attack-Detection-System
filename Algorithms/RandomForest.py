import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, auc, precision_recall_curve
)

print('Model Training Started....')

# ------ FUNCTIONS ------ #

def evaluate_model(name, y_train, y_train_pred, y_train_prob,
                   y_test, y_test_pred, y_test_prob):

    print(f"\n------ {name} PERFORMANCE ------n")

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


# ------ LOAD DATA ------ #

data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')

small_data = data.sample(frac=0.5, random_state=42).drop_duplicates()
X = small_data.drop('Label', axis=1)
y = small_data['Label']

# ------ SPLIT ------ #

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ------ TRAIN ------ #

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ------ PREDICT ------ #

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

y_train_pred = model.predict(X_train)
y_train_prob = model.predict_proba(X_train)[:, 1]

# ------ EVALUATE ------ #

evaluate_model("Random Forest",
               y_train, y_train_pred, y_train_prob,
               y_test, y_pred, y_prob)

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

# ------ PLOTS ------ #

plot_confusion(y_train, y_train_pred, "RF Train CM")
plot_confusion(y_test, y_pred, "RF Test CM")

plot_roc(y_test, y_prob, "RF ROC")
plot_pr(y_test, y_prob, "RF PR")

# ------ MODEL QUALITY CHECK ------ #

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

# ------ FEATURE IMPORTANCE ------ #

importance = model.feature_importances_
feat_imp = pd.Series(importance, index=X.columns).sort_values(ascending=False)

print("\nTop 20 Features:\n", feat_imp.head(20))

feat_imp.head(20).plot(kind='bar')
plt.title('Top 20 Important Features')
plt.show()

# ------ CROSS VALIDATION ------ #

scores = cross_val_score(
    RandomForestClassifier(n_estimators=100, random_state=42),
    X, y, cv=5
)

print("Cross-validation scores:", scores)
print("Average:", scores.mean())

# ------ SAVE ------ #

os.makedirs('Models', exist_ok=True)
joblib.dump(model, 'Models/random_forest.pkl')

print('Random Forest Model Saved!!')

