from log_reader import read_logs_tail

def early_warning():
    logs = read_logs_tail(6)
    if len(logs) < 5:
        return None
    risks = [entry["risk_score"] for entry in logs]
    increasing = all(risks[i] <= risks[i+1] for i in range(len(risks)-1))
    if risks[-1] > risks[0] + 20:
        return "⚠️ EARLY WARNING: Rapid Risk Growth"
    if increasing and risks[-1] > 40:
        return "⚠️ EARLY WARNING: Gradual Attack Build-up"
    return None