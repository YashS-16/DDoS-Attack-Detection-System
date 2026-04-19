from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'logs.json')

app = Flask(__name__)
# Enable CORS so the React frontend on Vite (port 5173) can communicate with Flask
CORS(app)
    
capture_process = None

@app.route('/api/data')
def get_data():
    if not os.path.exists(LOG_FILE):
        return jsonify({"logs": []})
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except:
        logs = []
    
    return jsonify({
        "logs": logs[-50:]  # Send last 50 logs for the dashboard
    })

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    global capture_process
    if capture_process is None or capture_process.poll() is not None:
        try:
            capture_process = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'live_capture.py')])
            return jsonify({"status": "started", "message": "Monitoring started successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "running", "message": "Monitoring is already running."})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global capture_process
    if capture_process and capture_process.poll() is None:
        capture_process.terminate()
        capture_process.wait()
        capture_process = None
        return jsonify({"status": "stopped", "message": "Monitoring stopped successfully."})
    
    return jsonify({"status": "stopped", "message": "Monitoring is not currently running."})

@app.route('/api/status', methods=['GET'])
def get_status():
    global capture_process
    is_running = capture_process is not None and capture_process.poll() is None
    return jsonify({"is_running": is_running})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)