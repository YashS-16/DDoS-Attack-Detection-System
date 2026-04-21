from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import sys
from log_reader import read_logs_tail, clear_logs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
CORS(app)

capture_process = None

# ------------------ GET DATA ------------------
@app.route('/api/data')
def get_data():
    logs = read_logs_tail(50)
    return jsonify({"logs": logs})

# ------------------ CLEAR LOGS ------------------
@app.route('/api/logs/clear', methods=['POST'])
def clear_log_data():
    if clear_logs():
        return jsonify({"status": "success", "message": "Logs cleared"})
    else:
        return jsonify({"status": "error", "message": "Failed to clear logs"}), 500

# ------------------ START ------------------
@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    global capture_process

    if capture_process is None or capture_process.poll() is not None:
        try:
            # IMPORTANT: run live_capture with sudo on Linux, but here we just run it
            capture_process = subprocess.Popen([
                sys.executable,
                os.path.join(BASE_DIR, 'live_capture.py')
            ])

            return jsonify({"status": "started", "message": "Monitoring started successfully."})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "running", "message": "Already running"})

# ------------------ STOP ------------------
@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global capture_process

    if capture_process and capture_process.poll() is None:
        capture_process.terminate()
        capture_process.wait()
        capture_process = None
        return jsonify({"status": "stopped"})

    return jsonify({"status": "stopped", "message": "Not running"})

# ------------------ STATUS ------------------
@app.route('/api/status', methods=['GET'])
def get_status():
    global capture_process
    is_running = capture_process is not None and capture_process.poll() is None
    return jsonify({"is_running": is_running})

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)