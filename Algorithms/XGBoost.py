import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, recall_score, roc_auc_score, roc_curve, auc
from xgboost import XGBClassifier

def generate_alert(prob):
    if prob > 0.9:
        return "HIGH RISK 🚨"
    elif prob > 0.6:
        return "MEDIUM RISK ⚠"
    else:
        return "LOW RISK ✅"

# Load Data
data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')

print('Duplicate rows:', data.duplicated().sum())

# Remove duplicates
data = data.drop_duplicates()

# Shuffle BEFORE split
data = data.sample(frac=1, random_state=42)

# Features & Target
X = data.drop('Label', axis=1)
y = data['Label']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train = pd.DataFrame(X_train, columns=X.columns)
X_test = pd.DataFrame(X_test, columns=X.columns)

# Handle Imbalance (IMPORTANT)
scale_pos_weight = len(y[y == 0]) / len(y[y == 1])


# Model
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

def predict_attack(model, input_data, threshold=0.3):
    prob = model.predict_proba(input_data)[:, 1]
    pred = (prob > threshold).astype(int)
    
    alert = generate_alert(prob[0])
    
    return pred[0], prob[0], alert

# Predictions
y_pred = xgb_model.predict(X_test)
y_prob = xgb_model.predict_proba(X_test)[:, 1]

# Custom Threshold
threshold = 0.3
y_pred_custom = (y_prob > threshold).astype(int)

# Evaluation
print("*** XGBoost Default ***")
print("Recall:", recall_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print(classification_report(y_test, y_pred))

print("\n*** XGBoost Custom Threshold (0.3) ***")
print("Recall:", recall_score(y_test, y_pred_custom))
print(classification_report(y_test, y_pred_custom))

# Confusion Matrix (Custom)
cm = confusion_matrix(y_test, y_pred_custom)

plt.figure()
sns.heatmap(cm, annot=True, fmt='d')
plt.title("XGBoost Confusion Matrix (Custom)")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
plt.plot([0, 1], [0, 1], '--')
plt.xlabel("FPR")
plt.ylabel("TPR")
plt.title("ROC Curve - XGBoost")
plt.legend()
plt.show()

# Feature Importance
importance = xgb_model.feature_importances_
feat_imp = pd.Series(importance, index=X.columns).sort_values(ascending=False)

print("\nTop 20 Features:\n")
print(feat_imp.head(20))

feat_imp.head(20).plot(kind='bar')
plt.title("Top 20 Feature Importance")
plt.show()

# Cross Validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(xgb_model, X, y, cv=skf, scoring='recall')

print("\nCross-validation scores:", scores)
print("Average Recall:", scores.mean())

print("\n---- SYSTEM TEST ----\n")

# One real sample
sample = X_test.iloc[[0]]

pred, prob, alert = predict_attack(xgb_model, sample)

print("Prediction (0=Normal,1=Attack):", pred)
print("Probability:", round(prob, 4))
print("Alert Level:", alert)


# Saving the Model

joblib.dump(xgb_model, 'Models/xgboost.pkl')
print('XGBoost Model Saved!!')
