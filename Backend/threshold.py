from log_reader import read_logs_tail

def check_threshold():
    # Take last 100 logs (or default n) and slice the last 5 for this logic
    logs = read_logs_tail(5)

    # Need minimum data
    if len(logs) < 5:
        return None

    # Processing logs
    risks = [entry["risk_score"] for entry in logs]


    high_count = sum(1 for r in risks if r > 70)

    alert = None
    if high_count >= 3:
        return "🚨 BURST ATTACK: Multiple High-Risk Packets Detected"

    if all(40 <= r <= 70 for r in risks):
        return "⚠️ CONTINUOUS ATTACK: Sustained Medium Risk Traffic"

    if risks[-1] - risks[0] > 15:
        return "⚠️ SPIKE DETECTED: Sudden Increase in Risk"

    return alert