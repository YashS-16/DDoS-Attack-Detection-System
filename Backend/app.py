from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from log_reader import read_logs_tail, clear_logs
from live_capture import start_capture, stop_capture, is_running

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
CORS(app)

# ------------------ LOGS ------------------
@app.route('/logs', methods=['GET'])
def get_logs():
    """Return last 100 log entries (frontend expects array)"""
    logs = read_logs_tail(100)
    return jsonify(logs)   # directly return list, not {logs: logs}

# ------------------ CLEAR LOGS ------------------
@app.route('/clear_logs', methods=['POST'])
def clear_log_data():
    if clear_logs():
        return jsonify({"status": "success", "message": "Logs cleared"})
    else:
        return jsonify({"status": "error", "message": "Failed to clear logs"}), 500

# ------------------ START ------------------
@app.route('/start', methods=['POST'])
def start_monitoring():
    result = start_capture()
    if result["status"] == "started" or result["status"] == "already running":
        return jsonify({"status": "started", "message": result.get("message", "Monitoring started")})
    else:
        return jsonify({"status": "error", "message": "Failed to start"}), 500

# ------------------ STOP ------------------
@app.route('/stop', methods=['POST'])
def stop_monitoring():
    result = stop_capture()
    return jsonify({"status": result["status"], "message": result.get("message", "")})

# ------------------ STATUS ------------------
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(is_running())

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)