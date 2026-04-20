import pandas as pd
import datetime
import random
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
from predictor import predict, feature_columns
from alert import generate_alert, get_severity
from logger import log_result
from threshold import check_threshold
from autoblock import autoblock
from early_detection import early_warning
from attack_type import classify_attack_type
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

print("Writing logs to:", os.path.abspath(LOG_FILE))

# GLOBAL BUFFER
packet_buffer = []
WINDOW_SIZE = 50
WINDOW_TIMEOUT = 5.0

# REQUIRED KEYS (CONSISTENCY FIX)
REQUIRED_KEYS = [
    'timestamp',
    'Protocol',
    'Total Length',
    'SYN Flag Count',
    'ACK Flag Count',
    'Destination Port',
    'Source IP'
]

# PACKET FEATURE EXTRACTION
def extract_features_from_packet(packet):

    # Always same structure
    features = {
        'timestamp': time.time(),
        'Protocol': 0,
        'Total Length': 0,
        'SYN Flag Count': 0,
        'ACK Flag Count': 0,
        'Destination Port': 0,
        'Source IP': "0.0.0.0"
    }

    if IP in packet:
        features['Protocol'] = packet[IP].proto
        features['Total Length'] = len(packet)
        features['Source IP'] = packet[IP].src

    if TCP in packet:
        features['SYN Flag Count'] = 1 if packet[TCP].flags.S else 0
        features['ACK Flag Count'] = 1 if packet[TCP].flags.A else 0
        features['Destination Port'] = packet[TCP].dport

    elif UDP in packet:
        features['Destination Port'] = packet[UDP].dport

    return features


# AGGREGATION FUNCTION
def aggregate_features(df):

    aggregated_raw = {}

    # Time normalization (IMPORTANT)
    time_span = df["timestamp"].max() - df["timestamp"].min()
    if time_span <= 0:
        time_span = 1.0

    aggregated_raw["Flow Packets/s"] = len(df) / time_span
    aggregated_raw["Flow Bytes/s"] = df["Total Length"].sum() / time_span
    aggregated_raw["Average Packet Size"] = df["Total Length"].mean()

    proto_mode = df["Protocol"].mode()
    aggregated_raw["Protocol"] = proto_mode[0] if not proto_mode.empty else 0

    aggregated_raw["SYN Flag Count"] = df["SYN Flag Count"].sum()
    aggregated_raw["ACK Flag Count"] = df["ACK Flag Count"].sum()

    port_mode = df["Destination Port"].mode()
    aggregated_raw["Destination Port"] = port_mode[0] if not port_mode.empty else 0

    # Force correct feature order
    aggregated = {}
    for col in feature_columns:
        aggregated[col] = aggregated_raw.get(col, 0)
    
    print("Flow Packets/s:", aggregated["Flow Packets/s"])

    return aggregated



# PACKET HANDLER (LIGHTWEIGHT)
def process_packet(packet):
    print("Packet captured")
    global packet_buffer

    pkt = extract_features_from_packet(packet)
    packet_buffer.append(pkt)

    # Prevent memory overflow
    if len(packet_buffer) > 2000:
        packet_buffer = packet_buffer[-1000:]


# MAIN PROCESSING LOOP
def process_buffer():
    print("Process cycle running...")
    global packet_buffer

    # Wait for enough data
    if len(packet_buffer) < WINDOW_SIZE:
        if not packet_buffer:
            return

        if time.time() - packet_buffer[0]['timestamp'] < WINDOW_TIMEOUT:
            return

    # Ensure consistent keys (CRITICAL FIX)
    for pkt in packet_buffer:
        for key in REQUIRED_KEYS:
            if key not in pkt:
                pkt[key] = 0

    # Create DataFrame safely
    try:
        df = pd.DataFrame(packet_buffer)
    except Exception as e:
        print(f"DataFrame error: {e}. Clearing buffer.")
        packet_buffer.clear()
        return

    aggregated = aggregate_features(df)

    # 🚫 Ignore very low traffic (reduces false positives)
    if aggregated["Flow Packets/s"] < 3:
        print("Low Traffic detected - logging as normal traffic")
        # packet_buffer.clear()
    try:
        result = predict(aggregated)
        if not isinstance(result, dict):
            print("Invalid prediction output:", result)
            packet_buffer.clear()
            return
    except Exception as e:
        print("Prediction error:", e)
        packet_buffer.clear()
        return

    # Real IP tracking
    if "Source IP" in df.columns:
        ip = df["Source IP"].mode()[0]
    else:
        ip = "UNKNOWN"

    print("DEBUG result:", result)
    print("TYPE:", type(result))

   # Raw model prediction
    raw_attack = classify_attack_type(aggregated)

    risk = result.get("risk_score", 0) * 1.5
    if risk < 40:
        attack_type = "Normal Traffic"
    elif risk < 70:
        attack_type = "Suspicious Traffic"
    else:
        attack_type = raw_attack

# Alerts & severity
    alert = generate_alert(result, attack_type)
    severity = get_severity(result)

    output = {
        "packet_id": random.randint(1000, 9999),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": str(alert),
        "risk_score": float(round(risk, 2)),
        "severity": str(severity.replace("🟠", "").replace("🔴", "").replace("🟢", "")),
        "alert": str(alert),
        "anomaly": bool(result.get("anomaly", False)),
        "reconstruction_error": float(round(result.get("error",0),3)),
        "models": {
            "rf_prob": float(result["rf_prob"]),
            "xgb_prob": float(result["xgb_prob"]),
            "lr_prob": float(result["lr_prob"])
        },
        "ip": str(ip),
        "attack_type": str(attack_type),
    }

    # LOGGING + SYSTEM FEATURES
    log_result(output)

    threshold_alert = check_threshold()
    if threshold_alert:
        print("\n🚨 THRESHOLD ALERT:", threshold_alert)

    early = early_warning()
    if early:
        print("⚠️ EARLY WARNING:", early)
        
    top_attacker = (ip, len(packet_buffer))
    if top_attacker:
        ip_attacker, count = top_attacker
        print(f"🔥 Top Attacker: {ip_attacker} | Requests: {count}")

    block_msg = autoblock(ip, output["risk_score"])
    if block_msg:
        print(block_msg)

    # OUTPUT DISPLAY
    print("\n" + "=" * 60)
    print(f"[LIVE] {output['timestamp']}")
    print(f"IP: {ip}")
    print(f"Attack Type: {attack_type}")
    print(f"Alert: {alert}")
    print(f"Risk Score: {output['risk_score']}")
    print(f"Severity: {severity}")
    print("=" * 60)
    print("Processing buffer with size:", len(packet_buffer))
    
    if risk < 40:
        print("Normal traffic processed")
    packet_buffer = packet_buffer.clear[-20:]

# SNIFFING THREAD
def start_sniffing():
    try:
        sniff(iface="enp0s8", prn=process_packet, store=False)
    except OSError:
        print("Interface issue. Trying 'Wi-Fi'...")
        sniff(iface="enp0s8", prn=process_packet, store=False)

if __name__ == "__main__":
    print("🚀 Starting LIVE DDoS Detection...")
    print("Press Ctrl+C to stop\n")

    threading.Thread(target=start_sniffing, daemon=True).start()

    while True:
        process_buffer()
        time.sleep(2)
