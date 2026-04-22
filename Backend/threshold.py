from log_reader import read_logs_tail

def check_threshold():
    logs = read_logs_tail(10)
    if len(logs) < 5:
        return None
    risks = [entry["risk_score"] for entry in logs]
    high_count = sum(1 for r in risks if r > 70)
    medium_count = sum(1 for r in risks if r > 50)
    if high_count >= 3:
        return "🚨 BURST ATTACK: Multiple High-Risk Events"
    if medium_count >= 5:
        return "⚠️ CONTINUOUS ATTACK: Sustained Suspicious Traffic"
    if risks[-1] - risks[0] > 20:
        return "⚠️ SPIKE DETECTED: Rapid Traffic Escalation"
    return None