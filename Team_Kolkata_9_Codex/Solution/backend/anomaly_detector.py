from utils import calculate_deviation

def detect_anomaly(data):

    anomalies = []

    deviation = calculate_deviation(data["expected"], data["actual"])

    if deviation > 0.3:
        anomalies.append("Large deviation in processed records")

    for log in data["logs"]:
        if "ERROR" in log or "timeout" in log.lower():
            anomalies.append("Error logs detected")
            break

    return anomalies