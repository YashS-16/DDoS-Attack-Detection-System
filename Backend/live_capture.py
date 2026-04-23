import pandas as pd
import datetime
import time
import threading
import json
import os
from scapy.all import sniff, IP, TCP, UDP

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

running = True
window_packets = []
window_start = time.time()
WINDOW_DURATION = 2.0

# ------------------ FEATURE EXTRACTION ------------------
def extract_features_from_packet(packet):
    return {
        'timestamp': time.time(),
        'Protocol': packet[IP].proto if IP in packet else 0,
        'Total Length': len(packet),
        'SYN Flag Count': 1 if TCP in packet and packet[TCP].flags.S else 0,
        'ACK Flag Count': 1 if TCP in packet and packet[TCP].flags.A else 0,
        'Destination Port': packet[TCP].dport if TCP in packet else (packet[UDP].dport if UDP in packet else 0),
        'Source IP': packet[IP].src if IP in packet else "0.0.0.0"
    }

# ------------------ AGGREGATION & RISK ------------------
def aggregate_features(df):
    time_span = max(df["timestamp"].max() - df["timestamp"].min(), 1.0)
    pps = len(df) / time_span

    # Dynamic risk based on packets per second
    if pps < 10:
        risk = 20 + (pps / 10) * 15
    elif pps < 50:
        risk = 35 + ((pps - 10) / 40) * 30
    elif pps < 150:
        risk = 65 + ((pps - 50) / 100) * 20
    else:
        risk = 85 + min(15, (pps - 150) / 50 * 15)

    risk = max(0, min(100, risk))
    return {
        "risk_score": round(risk, 2),
        "packets_per_second": round(pps, 1),
        "attack_type": "DDoS Attack" if risk > 50 else "Normal Traffic",
        "ip": df["Source IP"].mode()[0] if not df["Source IP"].mode().empty else "0.0.0.0"
    }

# ------------------ PACKET HANDLER ------------------
def packet_handler(packet):
    global window_packets
    if not running:
        return
    window_packets.append(extract_features_from_packet(packet))
    if len(window_packets) > 5000:
        window_packets = window_packets[-2000:]

# ------------------ PROCESS WINDOW ------------------
def process_buffer():
    global window_packets, window_start
    if not running:
        return
    now = time.time()
    if now - window_start < WINDOW_DURATION or len(window_packets) < 5:
        return

    buffer_copy = window_packets.copy()
    window_packets = []
    window_start = now

    df = pd.DataFrame(buffer_copy)
    agg = aggregate_features(df)

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": agg["risk_score"],
        "packets_per_second": agg["packets_per_second"],
        "attack_type": agg["attack_type"],
        "ip": agg["ip"],
        "anomaly": False,
        "reconstruction_error": 0,
        "models": {"rf_prob": 0, "xgb_prob": 0, "lr_prob": 0}
    }

    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass

    print(f"[RISK: {agg['risk_score']}] [PPS: {agg['packets_per_second']}]")

# ------------------ SNIFF LOOP ------------------
def sniff_loop():
    while running:
        try:
            # Change 'enp0s8' to your interface (or use None for auto)
            sniff(iface="enp0s8", prn=packet_handler, store=False, timeout=1)
        except Exception as e:
            print(f"Sniff error: {e}")
            time.sleep(1)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    print("🚀 DDoS Capture Started")
    sniff_thread = threading.Thread(target=sniff_loop, daemon=True)
    sniff_thread.start()

    while running:
        process_buffer()
        time.sleep(0.5)