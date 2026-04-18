import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, auc, precision_recall_curve
)
from xgboost import XGBClassifier

print(" ---- XG Boost Model ---- ")

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


def generate_alert(prob):
    if prob > 0.9:
        return "HIGH RISK "
    elif prob > 0.6:
        return "MEDIUM RISK "
    else:
        return "LOW RISK "


# ------ LOAD DATA ------ #

data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')
data = data.drop_duplicates().sample(frac=1, random_state=42)

X = data.drop('Label', axis=1)
y = data['Label']

# ------ SPLIT ------ #
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ------ MODEL ------ #
scale_pos_weight = len(y[y == 0]) / len(y[y == 1])

xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)

print("\nModel Training Started...\n")
xgb_model.fit(X_train, y_train)

# ------ PREDICT ------ #
y_prob = xgb_model.predict_proba(X_test)[:, 1]
y_train_prob = xgb_model.predict_proba(X_train)[:, 1]

threshold = 0.3
y_pred = (y_prob > threshold).astype(int)
y_train_pred = (y_train_prob > threshold).astype(int)

# ------ EVALUATE ------ #
evaluate_model("XGBoost",
               y_train, y_train_pred, y_train_prob,
               y_test, y_pred, y_prob)

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

# ------ PLOTS ------ #
plot_confusion(y_train, y_train_pred, "XGB Train CM")
plot_confusion(y_test, y_pred, "XGB Test CM")

plot_roc(y_test, y_prob, "XGB ROC")
plot_pr(y_test, y_prob, "XGB PR")

# ------ MODEL QUALITY CHECK ------ #
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc_score = roc_auc_score(y_test, y_prob)
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_pred)

print("\n------ MODEL QUALITY CHECK ------\n")

if recall > 0.90:
    print("Excellent Recall (Best for DDoS)")
elif recall > 0.80:
    print("Moderate Recall")
else:
    print("Poor Recall")

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

print(f"\nSummary → Recall: {recall:.3f} | F1: {f1:.3f} | AUC: {auc_score:.3f}")

# ------ FEATURE IMPORTANCE ------ #
importance = xgb_model.feature_importances_
feat_imp = pd.Series(importance, index=X.columns).sort_values(ascending=False)

print("\nTop 20 Features:\n", feat_imp.head(20))

feat_imp.head(20).plot(kind='bar')
plt.title("Top 20 Feature Importance")
plt.show()

# ------ CROSS VALIDATION ------ #
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(
    XGBClassifier(**xgb_model.get_params()),
    X, y,
    cv=skf,
    scoring='recall'
)

print("\nCross-validation scores:", scores)
print("Average Recall:", scores.mean())

# ------ SYSTEM TEST ------ #
sample = X_test.iloc[[0]]
prob = xgb_model.predict_proba(sample)[:, 1][0]
pred = int(prob > threshold)
alert = generate_alert(prob)

print("\n---- SYSTEM TEST ----\n")
print("Prediction:", pred)
print("Probability:", round(prob, 4))
print("Alert Level:", alert)

# ------ SAVE ------ #
joblib.dump(xgb_model, 'Models/xgboost.pkl')
print('XGBoost Model Saved!!')