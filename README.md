# 🛡️ NetGuard Sentinel – Real-Time DDoS Detection System

## 📌 Overview

This project detects and analyzes potential Distributed Denial of Service (DDoS) attacks in real-time, utilizing powerful machine learning combinations:

* Machine Learning Models (Random Forest, XGBoost, Logistic Regression)
* Autoencoder-based anomaly detection (for zero-day patterns)
* Live packet capture and feature extraction via Scapy
* A modern, high-performance React + TypeScript Frontend
* Flask Backend API for process management and data offloading

## ⚙️ Features

* **Live Traffic Monitoring**: Dynamic flow capture from your network interface.
* **Risk Scoring System**: Mathematical risk assessment scaling from 0 to 100.
* **Attack Type Classification**: Intelligent label tracking to categorize the form of DDoS (SYN Flood, UDP Flood, Slowloris).
* **Real-Time Dashboard**: Beautiful UI powered by React, Tailwind CSS, and Recharts.
* **Subprocess Management**: Direct capability to start and stop the backend capture directly from the UI.
* **Alert Feed**: Chronological logging of all critical network events.

## 🚀 Quick Start (Single Command Launch)

Our automated launch scripts instantiate the Python virtual environment, install requirements, and boot both the backend API and frontend dashboard simultaneously.

### Prerequisites

* Python 3.8+ 
* Node.js 18+
* Terminal running as **Administrator/sudo** (critical for raw socket access by Scapy)

### Windows

Double click, or run from an administrative command prompt:
```bat
launch.bat
```

### Linux / macOS

Give execution permissions and run as `sudo`:
```bash
chmod +x launch.sh
sudo ./launch.sh
```

## 🛠️ Testing with Two Virtual Machines

To effectively test the DDoS detection capabilities, we recommend setting up two Virtual Machines on a Host-Only or Internal Network.

**Setup Requirements:**
1. **VM1 (Victim)**: Runs NetGuard Sentinel. Ensure firewall allows incoming requests on test ports (e.g., port 80).
2. **VM2 (Attacker)**: Runs Kali Linux or has testing tools like `hping3` or `slowloris` installed.

**Steps:**
1. Finding IPs: Run `ipconfig` (Windows) or `ifconfig` (Linux) on VM1 to get the target IP address.
2. Start NetGuard on VM1 using the launch scripts and click the "Start Capture" button on the UI.
3. On VM2, execute an attack simulation command targeting VM1.
    * *Example SYN Flood:* `sudo hping3 -S --flood -p 80 <VM1_IP>`
4. Observe the NetGuard dashboard on VM1. You will see traffic spikes, risk scores elevating, and the Alert Feed flagging the attack.

For detailed breakdown, view [INSTRUCTIONS.md](INSTRUCTIONS.md).

---

## ⚠️ Important Notes

* Always run the launching process as **Administrator / Root**. Network sniffer mechanisms mandate raw socket access.
* Works exclusively on **local network** interface bindings.
* **Ethics Warning**: Do NOT run attack simulations against public networks or addresses you do not own. This tool is built purely for academic and defensive demonstration purposes.
