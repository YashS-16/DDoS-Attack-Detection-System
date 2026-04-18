# NetGuard DDoS Testing Instructions

This document provides a highly comprehensive walk-through on how to simulate and test DDoS detection mechanisms using two virtual machines. DO NOT test against external servers.

## Network Preparation

1. **Virtualization Software**: You can use VirtualBox or VMware.
2. **Network Adapter Settings**:
   - Go to your VM settings.
   - For both VM1 (Victim) and VM2 (Attacker), set the Network connection to **Internal Network** or **Host-Only Adapter**. This ensures traffic runs completely isolated from your home router and ISP.
3. **VM1 Operating System**: Windows 10/11 or Ubuntu. You will run the NetGuard Sentinel application here.
4. **VM2 Operating System**: Kali Linux is highly recommended as it comes pre-packaged with offensive tools.

## Step 1: Setting up VM1 (Victim)

1. Clone or copy the NetGuard repository into VM1.
2. Open PowerShell or Command Prompt as **Administrator** (Windows) or Terminal as **Root** (Linux). Scapy needs high privileges to sniff raw sockets.
3. Run the launch script (`launch.bat` or `sudo ./launch.sh`).
4. Wait for both the Flask Backend and React Dashboard to initialize.
5. Identify the VM's IPv4 Address (`ipconfig` or `ip a`). *Let's assume VM1 is `192.168.1.5`.*
6. Open your browser on VM1 to the React Dashboard port (usually `http://localhost:5173`).
7. Click the **Start Capture** button. The radar pulse should activate.

## Step 2: Preparing VM2 (Attacker)

1. Log in to your Attacker VM.
2. Ensure you can reach VM1. Ping the victim:
   ```bash
   ping 192.168.1.5
   ```
   *Note: If Windows Firewall blocks ICMP, allow it or simply rely on TCP mapping.*

## Step 3: Simulating Network Attacks

Here are three distinct attack vectors you can test to verify the detection logic.

### Attack 1: Classic SYN Flood
Uses `hping3` to rapidly fire TCP SYN requests, exhausting the victim's connection queue.
```bash
sudo hping3 -S --flood -V -p 80 192.168.1.5
```
*Verification*: Check the Dashboard. The Packets/sec should skyrocket. After a few seconds, the Attack Classification should switch to "Anomaly" or "Suspicious Traffic" with high severity.

### Attack 2: UDP Flood
Floods the victim's UDP ports, which are connectionless, rapidly causing interface saturation.
```bash
sudo hping3 --udp --flood -p 53 192.168.1.5
```
*Verification*: Watch the protocol metrics update on the backend and risk scores adapt differently based on UDP flows.

### Attack 3: Random Source IP Flood
Hides the true origin of the attack by generating random source IP spoofing.
```bash
sudo hping3 -S --flood --rand-source -p 80 192.168.1.5
```
*Verification*: Keep an eye on the "Targeted IP" panel on the dashboard. It will rapidly rotate or display anomalous origin data.

## Step 4: System Response & Stop

1. Once the attack is detected and shown on the React Dashboard, hit `CTRL+C` on the Attacker VM (VM2) to cease the packet bombardment.
2. Observe the flow metrics in the dashboard cooling down, and the risk score slowly depleting as the window buffer recedes to normal baselines.
3. To stop logging altogether, press **Stop Capture** on your Dashboard in VM1.

## Troubleshooting

- **No Data in Dashboard**: Ensure CORS is enabled on the backend (`app.py`), and look at the browser developer console via `F12`.
- **Capture not working**: Check that the script on VM1 was started with Administrative/Root privileges and `live_capture.py` is successfully hooked to the primary network interface.
- **Port Conflicts**: Ensure nothing else is using port 5000 (Flask) and port 5173 (Vite Node).
