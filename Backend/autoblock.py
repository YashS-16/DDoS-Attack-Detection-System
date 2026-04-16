blocked_ips = set()

def autoblock(ip, risk_score):

    # Rule 1: High risk
    if risk_score > 80:
        blocked_ips.add(ip)
        return f"BLOCKED {ip} (High Risk)"

    # Rule 2: Already flagged frequently
    if ip in blocked_ips:
        return f"{ip} already blocked"

    return None