def generate_alert(result, attack_type):
    if not isinstance(result, dict):
        return "Normal Traffic"
    score = result.get('risk_score', 0)
    if score < 30:
        return "Normal Traffic"
    if score < 50:
        return "Low Suspicion"
    if score < 70:
        return "⚠️ Suspicious Traffic"
    # High risk
    if attack_type != "Normal Traffic":
        return f"🚨 {attack_type} Detected"
    return "🚨 High Risk Traffic"

def get_severity(result):
    if not isinstance(result, dict):
        return "LOW"
    score = result.get('risk_score', 0)
    if score >= 70:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    else:
        return "LOW"