import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    recall_score,
    roc_auc_score,
    roc_curve,
    auc
)
from sklearn.model_selection import cross_val_score

print('Model Training Started....')

data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')

small_data = data.sample(frac=0.5, random_state=42)
small_data = small_data.drop_duplicates()
X = small_data.drop('Label', axis=1)
y = small_data['Label']
# X_small = small_data.drop('Label', axis=1)
# y_small = small_data['Label']


X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train = pd.DataFrame(X_train, columns=X.columns)
X_test = pd.DataFrame(X_test, columns=X.columns)


random_forest_model = RandomForestClassifier(
    n_estimators= 100,
    random_state=42,
    n_jobs=-1
)

random_forest_model.fit(X_train, y_train)

y_pred_rf = random_forest_model.predict(X_test)
y_prob_ref = random_forest_model.predict_proba(X_test)[:, 1]

# Basic metrices
print('Recall: ', recall_score(y_test, y_pred_rf))
print('ROC Curve: ', roc_curve(y_test, y_pred_rf))
print('ROC-AUC Score: ', roc_auc_score(y_test, y_pred_rf))

# Classification Report
print('\n***Classification Report***\n')
print(classification_report(y_test, y_pred_rf))

# Confusion Matrix
con_matrix = confusion_matrix(y_test, y_pred_rf)
plt.figure()
sns.heatmap(con_matrix, annot=True, fmt='d')
plt.title('Confusion Matrix (Default)')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Custom Threshold
threshold = 0.3

y_pred_rf_custom_threshold = (y_prob_ref>threshold).astype(int)

print('\n***Custom Threshold***\n')
print('Recall: ', recall_score(y_test, y_pred_rf_custom_threshold))
print('ROC-AUC: ', roc_auc_score(y_test, y_pred_rf_custom_threshold))
print('Classification report: \n', classification_report(y_test, y_pred_rf_custom_threshold))

# from sklearn.metrics import 

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob_ref)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.4f})")
plt.plot([0, 1], [0, 1], linestyle='--')  # random line

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Random Forest")
plt.legend()
plt.show()

# Custom Confusion Matrix

con_matrix_custom = confusion_matrix(y_test, y_pred_rf_custom_threshold)

plt.figure()
sns.heatmap(con_matrix_custom, annot=True, fmt='d')
plt.title('Confusion Matrix(Custom)')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Feature Importance

importance = random_forest_model.feature_importances_
feature_names = X.columns

feat_imp = pd.Series(importance, index=feature_names)
feat_imp = feat_imp.sort_values(ascending=False)

print('\n***Feature Importance***\n')
print(feat_imp.head(20))

feat_imp.head(20).plot(kind='bar')
plt.title('Top 20 Important Features')
plt.show()


scores = cross_val_score(random_forest_model, X, y, cv=5)

print("Cross-validation scores:", scores)
print("Average:", scores.mean())


# Saving the model

os.makedirs('Models', exist_ok=True)
joblib.dump(random_forest_model, 'Models/random_forest.pkl')

print('Random Forest Model Saved!!')