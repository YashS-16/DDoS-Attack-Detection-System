from log_reader import read_logs_tail

def early_warning():
    logs = read_logs_tail(5)

    if len(logs) < 5:
        return None

    risks = [entry["risk_score"] for entry in logs]


    # 1. Increasing trend
    increasing = all(risks[i] < risks[i+1] for i in range(len(risks)-1))

    # 2. Gradual rise
    if risks[-1] > risks[0] + 15:
        return "EARLY WARNING: Rapid increase in risk detected"

    # 3. Consistent increase pattern
    if increasing:
        return "EARLY WARNING: Gradual attack buildup detected"

    return None

