import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

def get_attack_timeline():
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
    
    timeline = []

    for i, entry in enumerate(logs):
        time = entry['timestamp'].split(" ")[1] # Extracting time in HH:MM:SS format
        risk = entry['risk_score']
        severity = entry['severity']

        escalation = ""

        if i> 0:
            prev_risk = logs[i-1]['risk_score']
            if risk > prev_risk + 15:
                escalation = 'Sudden Spike...'

            elif risk > 70 and prev_risk < 50:
                escalation = 'Attack Escalation...'
        
        timeline.append(
            {
                "time":time,
                "risk":int(risk),
                "severity": severity,
                "escalation": escalation
            }
        )
    return timeline