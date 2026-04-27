import subprocess
import time
import json
import os
import notifier

STATE_FILE = "ban_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def ban_ip(ip, condition, rate, baseline_mean):
    state = load_state()
    
    # If they are currently banned, do nothing
    if ip in state and state[ip].get('currently_banned', False):
        return
        
    print(f" THE BOUNCER IS BANNING {ip}...")
    
    # Increase their strike count (starts at 0, goes to 1, 2, 3, etc.)
    strikes = state.get(ip, {}).get('strikes', 0)
    
    # Calculate duration based on strikes (0=10m, 1=30m, 2=120m, 3+=permanent)
    if strikes == 0: duration = "10 min"
    elif strikes == 1: duration = "30 min"
    elif strikes == 2: duration = "2 hours"
    else: duration = "permanent"
    
    # 1. The Block Command
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    
    # 2. Update the record book
    state[ip] = {
        'strikes': strikes + 1,
        'banned_at': time.time(),
        'currently_banned': True,
        'duration': duration
    }
    save_state(state)
    
    # 3. The Audit Log
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] BAN {ip} | {condition} | rate: {rate:.2f} | baseline: {baseline_mean:.2f} | duration: {duration}\n"
    with open("audit.log", "a") as f:
        f.write(log_line)
        
    # 4. Slack Alert
    slack_msg = f" *NEW BAN* \n*IP:* {ip}\n*Reason:* {condition}\n*Rate:* {rate:.2f} req/s\n*Duration:* {duration}"
    notifier.send_alert(slack_msg)