import pandas as pd
import datetime
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
from predictor import predict
from alert import generate_alert, get_severity
from logger import log_result
from threshold import check_threshold
from autoblock import autoblock
from early_detection import early_warning
from attack_type import classify_attack_type
import os
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

print("Writing logs to:", os.path.abspath(LOG_FILE))

# -------- TIME-BASED WINDOW (instead of packet count) -------- #
WINDOW_DURATION = 3.0          # seconds
window_packets = []
window_start = time.time()

# -------- ADAPTIVE SCALING BUFFERS -------- #
# Keep last 100 values of each feature for running z-score
feature_buffers = {}
feature_columns = None   # will be set after loading scaler in predictor

def init_adaptive_scaler(cols):
    global feature_buffers
    feature_buffers = {col: deque(maxlen=100) for col in cols}

def adaptive_scale(features_dict):
    """Convert raw features to z-scores based on recent history."""
    scaled = {}
    for col, val in features_dict.items():
        buf = feature_buffers.get(col)
        if buf is None:
            scaled[col] = val
            continue
        buf.append(val)
        if len(buf) < 10:
            scaled[col] = val
        else:
            mean = sum(buf) / len(buf)
            variance = sum((x - mean) ** 2 for x in buf) / len(buf)
            std = variance ** 0.5 + 1e-6
            scaled[col] = (val - mean) / std
    return scaled

# Required keys for DataFrame
REQUIRED_KEYS = [
    'timestamp', 'Protocol', 'Total Length', 'SYN Flag Count',
    'ACK Flag Count', 'Destination Port', 'Source IP'
]

def extract_features_from_packet(packet):
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

def aggregate_features(df):
    """Aggregate packet-level DataFrame into one row of features."""
    time_span = df["timestamp"].max() - df["timestamp"].min()
    if time_span <= 0:
        time_span = 1.0

    aggregated = {}
    aggregated["Flow Packets/s"] = len(df) / time_span
    aggregated["Flow Bytes/s"] = df["Total Length"].sum() / time_span
    aggregated["Average Packet Size"] = df["Total Length"].mean()

    proto_mode = df["Protocol"].mode()
    aggregated["Protocol"] = proto_mode[0] if not proto_mode.empty else 0

    aggregated["SYN Flag Count"] = df["SYN Flag Count"].sum()
    aggregated["ACK Flag Count"] = df["ACK Flag Count"].sum()

    port_mode = df["Destination Port"].mode()
    aggregated["Destination Port"] = port_mode[0] if not port_mode.empty else 0

    # Add extra features for sensitivity
    aggregated["Packet Size Std"] = df["Total Length"].std() if len(df) > 1 else 0
    aggregated["SYN_ACK_Ratio"] = (
        aggregated["SYN Flag Count"] / (aggregated["ACK Flag Count"] + 1e-6)
    )
    # Unique source IPs (approximation – you can improve)
    aggregated["Unique IPs"] = df["Source IP"].nunique()

    # Ensure all required feature columns are present (fill missing with 0)
    from predictor import feature_columns as req_cols
    for col in req_cols:
        if col not in aggregated:
            aggregated[col] = 0
    return aggregated

def process_packet(packet):
    """Called by Scapy for each packet. Stores packet in current window."""
    global window_packets
    pkt = extract_features_from_packet(packet)
    window_packets.append(pkt)
    # Prevent memory blow
    if len(window_packets) > 5000:
        window_packets = window_packets[-2000:]

def process_buffer():
    """Periodically called: if window duration elapsed, aggregate & predict."""
    global window_packets, window_start
    now = time.time()
    if now - window_start < WINDOW_DURATION:
        return
    if len(window_packets) < 5:
        # Not enough data – reset timer but keep existing packets?
        window_start = now
        return

    # Take snapshot and clear
    buffer_copy = window_packets.copy()
    window_packets = []
    window_start = now

    # Create DataFrame
    try:
        df = pd.DataFrame(buffer_copy)
        for col in REQUIRED_KEYS:
            if col not in df.columns:
                df[col] = 0
        df = df.fillna(0)
    except Exception as e:
        print("DataFrame error:", e)
        return

    # Aggregate features
    aggregated = aggregate_features(df)
    pps = aggregated["Flow Packets/s"]

    # Adaptive scaling
    if not feature_buffers:
        # Initialize buffers with feature names from predictor
        from predictor import feature_columns as fc
        init_adaptive_scaler(fc)
    # Use raw aggregated features (no adaptive scaling)
        result = predict(aggregated, pps)
    if not isinstance(result, dict):
        return

    # Extract source IP (most frequent)
    ip = df["Source IP"].mode()[0] if "Source IP" in df.columns else "UNKNOWN"

    # Attack type classification
    raw_attack = classify_attack_type(aggregated)
    risk = result["risk_score"]

    # Determine final attack type based on risk
    if risk < 30:
        attack_type = "Normal Traffic"
    elif risk < 60:
        attack_type = "Suspicious Traffic"
    else:
        attack_type = raw_attack if raw_attack not in ["Normal Traffic", "Unknown"] else "DDoS Attack"

    # Generate alert and severity
    alert = generate_alert(result, attack_type)
    severity = get_severity(result)

    output = {
        "packet_id": int(time.time() * 1000) % 10000,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": str(alert),
        "risk_score": float(round(risk, 2)),
        "severity": str(severity).replace("🟠", "").replace("🔴", "").replace("🟢", ""),
        "alert": str(alert),
        "anomaly": bool(result.get("anomaly", False)),
        "reconstruction_error": float(round(result.get("error", 0), 4)),
        "models": {
            "rf_prob": float(result["rf_prob"]),
            "xgb_prob": float(result["xgb_prob"]),
            "lr_prob": float(result["lr_prob"])
        },
        "ip": str(ip),
        "attack_type": str(attack_type),
    }

    log_result(output)

    # Additional system checks
    threshold_alert = check_threshold()
    if threshold_alert:
        print("🚨 THRESHOLD ALERT:", threshold_alert)

    early = early_warning()
    if early:
        print("⚠️ EARLY WARNING:", early)

    print("\n" + "=" * 60)
    print(f"[LIVE] {output['timestamp']}")
    print(f"IP: {ip}")
    print(f"Attack Type: {attack_type}")
    print(f"Risk Score: {output['risk_score']}")
    print(f"Anomaly Error: {output['reconstruction_error']}")
    print("=" * 60)

def start_sniffing():
    try:
        sniff(iface="enp0s8", prn=process_packet, store=False)
    except OSError:
        print("Interface 'enp0s8' not found. Trying 'eth0'...")
        sniff(iface="eth0", prn=process_packet, store=False)

if __name__ == "__main__":
    print("🚀 Starting LIVE DDoS Detection with Dynamic Risk...")
    print("Press Ctrl+C to stop\n")
    threading.Thread(target=start_sniffing, daemon=True).start()
    while True:
        process_buffer()
        time.sleep(0.5)   # check every 0.5 sec