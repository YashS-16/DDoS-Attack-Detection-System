# NetGuard Sentinel - DDoS Attack Detection Manual

## Project Overview
NetGuard Sentinel is a real-time DDoS detection system that uses Machine Learning (Random Forest, XGBoost, Logistic Regression) and Anomaly Detection (AutoEncoders) to monitor network traffic for malicious patterns. It features a modern React dashboard for live threat visibility.

## System Prerequisites
- **Operating System**: Linux (Ubuntu 20.04+ recommended) or Windows 10/11.
- **Python**: 3.9+ 
- **Node.js**: 18+ (for the dashboard)
- **Privileges**: Administrator (Windows) or Root (Linux) is required for Scapy packet sniffing.

## Installation Steps (Ubuntu VM)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YashS-16/DDoS-Attack-Detection-System.git
   cd DDoS-Attack-Detection-System
   ```

2. **Backend Setup**:
   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Running the System

1. **Start the application**:
   - **Linux**: `sudo ./launch.sh`
   - **Windows**: Run `launch.bat` as Administrator.

2. **Access the Dashboard**:
   Open your browser to `http://localhost:5173`.

3. **Start Monitoring**:
   Click the **Start Capture** button on the dashboard.

## DDoS Simulation Testing (Two-VM Setup)

To test the system, you need two VMs in the same internal network:
- **VM 1 (Victim)**: Running NetGuard Sentinel. IP: `192.168.1.10`
- **VM 2 (Attacker)**: Running Kali Linux.

### Attack 1: SYN Flood
Exhausts server connections by flooding SYN packets.
```bash
sudo hping3 -S --flood -V -p 80 192.168.1.10
```

### Attack 2: UDP Flood
Saturates bandwidth with connectionless traffic.
```bash
sudo hping3 --udp --flood -p 53 192.168.1.10
```

### Attack 3: Spoofed Source IP Flood
Hides the attacker's true IP.
```bash
sudo hping3 -S --flood --rand-source -p 80 192.168.1.10
```

## Troubleshooting

- **Scapy Permission Error**: Ensure you are running with `sudo` (Linux) or as Administrator (Windows). Packet sniffing requires raw socket access.
- **JSONDecodeError**: This has been resolved by implementing a robust JSONL (JSON Lines) reader. If you see this, ensure `logs.json` is being written line-by-line.
- **Interface Not Found**: If Scapy fails to find your network card, manually specify the interface in `Backend/live_capture.py` (e.g., `iface="eth0"`).
- **Port 5000/5173 Conflict**: Ensure no other services are using the Flask or Vite ports.
