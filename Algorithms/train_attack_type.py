import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from xgboost import XGBClassifier

print("------ Training Attack Type Classifier ------")

# ------ PATH SETUP ------ #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../Models")
DATA_PATH = os.path.join(BASE_DIR, "../Data/cleaned_data/processed_data.csv")

os.makedirs(MODEL_DIR, exist_ok=True)

# ------ LOAD DATA ------ #

data = pd.read_csv(DATA_PATH)

# ------ CREATE ATTACK TYPES ------ #

data['AttackType'] = 'Benign'
attack_mask = data['Label'] == 1

data.loc[attack_mask & (data['Protocol'] == 6) & (data['SYN Flag Count'] > 10), 'AttackType'] = 'SYN Flood'
data.loc[attack_mask & (data['Protocol'] == 17), 'AttackType'] = 'UDP Flood'
data.loc[attack_mask & (data['Destination Port'].isin([80, 443])), 'AttackType'] = 'HTTP Flood'
data.loc[attack_mask & (data['AttackType'] == 'Benign'), 'AttackType'] = 'DDoS Attack'

# ------ FILTER ATTACK DATA ------ #

attack_data = data[data['Label'] == 1].copy()

X = attack_data.drop(['Label', 'AttackType'], axis=1)
y = attack_data['AttackType']

# ------ ENCODE LABELS ------ #

le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ------ SPLIT ------ #

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

# ------ TRAIN ------ #

model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1,
    objective='multi:softmax',  
    num_class=len(le.classes_)
)

model.fit(X_train, y_train)

# ------ PREDICT ------ #

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# ------ EVALUATION ------ #

print("\n--- Train Accuracy ---")
print(accuracy_score(y_train, y_train_pred))

print("\n--- Test Accuracy ---")
print(accuracy_score(y_test, y_test_pred))

print("\n--- Classification Report ---")
print(classification_report(y_test, y_test_pred, target_names=le.classes_))

# ------ CONFUSION MATRIX ------ #

cm = confusion_matrix(y_test, y_test_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=le.classes_,
            yticklabels=le.classes_)
plt.title("Attack Type Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# ------ MODEL QUALITY CHECK ------ #

train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)

print("\n------ MODEL QUALITY CHECK ------\n")

if abs(train_acc - test_acc) < 0.05:
    print("No Overfitting")
else:
    print("❌ Overfitting Detected")

if test_acc > 0.90:
    print("Strong Multi-class Model")
elif test_acc > 0.80:
    print("Moderate Model")
else:
    print("Weak Model")

# ------ SAVE ------ #

joblib.dump(model, os.path.join(MODEL_DIR, "attack_type_model.pkl"))
joblib.dump(le, os.path.join(MODEL_DIR, "attack_type_label_encoder.pkl"))

print("Attack type model saved successfully.")