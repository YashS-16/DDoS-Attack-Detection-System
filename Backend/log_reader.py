import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'logs.json')

def read_logs_tail(n=100):
    """
    Return the last n log entries as a list of dictionaries (newest last).
    Reads the file line-by-line to safely handle JSONL format.
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    entries = []
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip malformed lines instead of crashing
                        continue
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []

    # Return only the last n entries
    return entries[-n:]

def clear_logs():
    """
    Truncate the log file to reset monitoring data.
    """
    try:
        with open(LOG_FILE, 'w') as f:
            f.truncate(0)
        return True
    except Exception as e:
        print(f"Error clearing logs: {e}")
        return False
