import requests
import yaml

# Load the webhook URL from our rulebook
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

WEBHOOK_URL = config['slack_webhook_url']

def send_alert(message):
    """Sends a message to Slack."""
    # If you haven't put a real Slack URL in yet, just print it to the screen
    if WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_HERE" or not WEBHOOK_URL:
        print(f"🔕 [Mock Slack Alert] {message}")
        return
    
    payload = {"text": message}
    try:
        requests.post(WEBHOOK_URL, json=payload)
        print("📨 Slack alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")