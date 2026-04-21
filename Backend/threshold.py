import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

def check_threshold():

    # If no logs → skip
    if not os.path.exists(LOG_FILE):
        return None

    logs = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    except Exception as e:
        print(f"Error reading logs in threshold: {e}")
        return None

    # Need minimum data
    if len(logs) < 5:
        return None

    # Take last 5 entries
    recent = logs[-5:]
    risks = [entry["risk_score"] for entry in recent]

    high_count = sum(1 for r in risks if r > 70)

    alert = None
    if high_count >= 3:
        return "🚨 BURST ATTACK: Multiple High-Risk Packets Detected"

    if all(40 <= r <= 70 for r in risks):
        return "⚠️ CONTINUOUS ATTACK: Sustained Medium Risk Traffic"

    if risks[-1] - risks[0] > 15:
        return "⚠️ SPIKE DETECTED: Sudden Increase in Risk"

    return alert