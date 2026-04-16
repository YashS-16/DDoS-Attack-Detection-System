def generate_alert(result, attack_type):

    score = result['risk_score']

    # ✅ MOST IMPORTANT FIX
    # If traffic is normal → ALWAYS return normal
    if attack_type == "Normal Traffic":
        return "Normal Traffic"

    # 🔥 High confidence attack
    if score >= 75:
        return f"🚨 {attack_type} Detected"

    # ⚠️ Medium suspicion
    elif score >= 50:
        return "⚠️ Suspicious Traffic"

    # ⚠️ Low suspicion (optional but useful for realism)
    elif score >= 30:
        return "Low Suspicion"

    # ❓ Unknown anomaly (fallback)
    elif result['anomaly']:
        return "UNKNOWN ATTACK: Anomaly Detected"

    # ✅ Default
    return "Normal Traffic"


def get_severity(result):

    score = result['risk_score']

    if score >= 75:
        return "🔴 HIGH"
    elif score >= 45:
        return "🟠 MEDIUM"
    else:
        return "🟢 LOW"