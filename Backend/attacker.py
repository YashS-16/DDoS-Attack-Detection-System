import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")


def get_top_attacker():

    if not os.path.exists(LOG_FILE):
        return None

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except Exception:
        return None

    ip_count = {}

    for entry in logs:

        ip = entry.get("ip")
        attack_type = entry.get("attack_type")

        if not ip or ip in ["UNKNOWN", "0.0.0.0", "LIVE_TRAFFIC"]:
            continue
        
        if attack_type not in ["Normal Traffic", "Benign"]:
            ip_count[ip] = ip_count.get(ip, 0) + 1

    if not ip_count:
        return None

    # Find top attacker
    top_ip = max(ip_count, key=ip_count.get)

    return top_ip, ip_count[top_ip]