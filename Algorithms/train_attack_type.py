import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
import os

print("=== Training Attack Type Classifier (Heuristic) ===")

data = pd.read_csv(r'Data/cleaned_data\processed_data.csv')

# Create heuristic attack types (since your dataset may not have AttackType column)
data['AttackType'] = 'Benign'
attack_mask = data['Label'] == 1
data.loc[attack_mask & (data['Protocol'] == 6) & (data['SYN Flag Count'] > 10), 'AttackType'] = 'SYN Flood'
data.loc[attack_mask & (data['Protocol'] == 17), 'AttackType'] = 'UDP Flood'
data.loc[attack_mask & (data['Destination Port'].isin([80,443])), 'AttackType'] = 'HTTP Flood'
data.loc[attack_mask & (data['AttackType'] == 'Benign'), 'AttackType'] = 'DDoS Attack'

# Keep only attack samples
attack_data = data[data['Label'] == 1].copy()
X = attack_data.drop(['Label', 'AttackType'], axis=1)
y = attack_data['AttackType']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))

os.makedirs("Models", exist_ok=True)
joblib.dump(model, "Models/attack_type_model.pkl")
joblib.dump(le, "Models/attack_type_label_encoder.pkl")
print("Attack type model saved.")