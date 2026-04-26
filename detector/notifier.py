import requests
import json

def send_slack_alert(webhook_url, details):
    """
    details should be a dictionary containing: 
    ip, rate, baseline, and ban_duration.
    """
    payload = {
        "text": "*Anomaly Detected & IP Blocked* ",
        "attachments": [{
            "color": "#f21b1b",
            "fields": [
                {"title": "Attacker IP", "value": details['ip'], "short": True},
                {"title": "Current Rate", "value": f"{details['rate']} RPS", "short": True},
                {"title": "Baseline Mean", "value": f"{details['baseline']} RPS", "short": True},
                {"title": "Action", "value": f"Banned for {details['duration']} mins", "short": False}
            ]
        }]
    }
    
    response = requests.post(webhook_url, data=json.dumps(payload),
                             headers={'Content-Type': 'application/json'})
    return response.status_code == 200