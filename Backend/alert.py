def generate_alert(result, attack_type):

    if not isinstance(result, dict):
        return "Normal Traffic"

    score = result.get('risk_score', 0)

    if score < 40:
        return "Normal Traffic"

    if attack_type == "Normal Traffic":
        return "Normal Traffic"

    if score >= 75:
        return f"{attack_type} Detected"
    elif score >= 50:
        return "Suspicious Traffic"
    elif score >= 35:
        return "Low Suspicion"
    elif result.get('anomaly'):
        return "UNKNOWN ATTACK"

    return "Normal Traffic"


def get_severity(result):

    if not isinstance(result, dict):
        return "LOW"

    score = result.get('risk_score', 0)

    if score >= 75:
        return "HIGH"
    elif score >= 45:
        return "MEDIUM"
    else:
        return "LOW"