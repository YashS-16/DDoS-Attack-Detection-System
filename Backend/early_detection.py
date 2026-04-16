import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

def early_warning():

    if not os.path.exists(LOG_FILE):
        return None

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    if len(logs) < 5:
        return None

    recent = logs[-5:]

    risks = [entry["risk_score"] for entry in recent]

    # 1. Increasing trend
    increasing = all(risks[i] < risks[i+1] for i in range(len(risks)-1))

    # 2. Gradual rise
    if risks[-1] > risks[0] + 15:
        return "⚠️ EARLY WARNING: Rapid increase in risk detected"

    # 3. Consistent increase pattern
    if increasing:
        return "⚠️ EARLY WARNING: Gradual attack buildup detected"

    return None

