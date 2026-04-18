import pandas as pd
import time
import datetime
import random
from predictor import predict
from alert import generate_alert, get_severity
from logger import log_result
from threshold import check_threshold
from attacker import get_top_attacker
from autoblock import autoblock
from early_detection import early_warning
from attack_type import classify_attack_type 
from timeline import get_attack_timeline
import warnings
warnings.filterwarnings("ignore")

def generate_ip():
    return f"192.168.1.{random.randint(1, 255)}"

print("DDoS Detection System Running...\n")

data = pd.read_csv(r'Data\test_data_stream.csv')
data = data.sample(n=20)

for i, row in data.iterrows():

    ip = generate_ip()
    result = predict(row)

    attack_type = classify_attack_type(row)
    alert = generate_alert(result, attack_type)
    severity = get_severity(result)

    # Properly closed dictionary
    output = {
        "packet_id": int(i + 1),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": alert,
        "risk_score": float(round(result["risk_score"], 2)),
        "severity": severity.replace("🟠 ", "").replace("🔴 ", "").replace("🟢 ", ""),
        "alert": alert,
        "anomaly": bool(result["anomaly"]),
        "reconstruction_error": float(round(result["error"], 3)),
        "models": {
            "rf_prob": float(result["rf_prob"]),
            "xgb_prob": round(float(result["xgb_prob"]), 4),
            "lr_prob": float(result["lr_prob"])
        }, 
        "ip": ip, 
        "attack_type": attack_type,
    }

    # Log once
    log_result(output)
    
    block_msg = autoblock(ip, output["risk_score"])
    if block_msg:
        print(block_msg)

    # Threshold
    threshold_alert = check_threshold()

    #  Top attacker (fixed variable)
    top_attacker = get_top_attacker()
    if top_attacker:
        top_ip, count = top_attacker
        print(f'\n🔥 Top Attacker: {top_ip} | Requests: {count}')

    if threshold_alert:
        print("\n🚨 THRESHOLD ALERT:")
        print(threshold_alert)
    
    early_alert = early_warning()

    if early_alert:
        print("\n🟡 EARLY DETECTION:")
        print(early_alert)

    print(f'Attack Type: {attack_type}')

    timeline = get_attack_timeline()
    print('\n Attack Timeline (last 5): ')
    print('Time       Risk       Severity')

    for t in timeline[-5:]:
        line = f"{t['time']}       {t['risk']:>3}       {t['severity']}"

        if t['escalation']:
            line += f"   <- {t['escalation']}"
        
        print(line)

    print("\nOUTPUT:")
    print(output)
    print("-" * 40)

    time.sleep(1)