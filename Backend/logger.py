import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

def log_result(data):
    """
    Append-only logger using JSON Lines format.
    Each entry is a single JSON object followed by a newline.
    """
    try:
        with open(LOG_FILE, "a") as f:
            json.dump(data, f)
            f.write("\n")
    except Exception as e:
        print(f"Error logging result: {e}")
