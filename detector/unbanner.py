import time
import json
import subprocess
import os
import notifier

STATE_FILE = "ban_state.json"

# Times in seconds (10 mins, 30 mins, 2 hours)
BAN_DURATIONS = [10 * 60, 30 * 60, 120 * 60]

def check_and_unban():
    """Runs continuously, checking if anyone's timeout is over."""
    print("⏳ Timekeeper started. Watching for expired bans...")
    
    while True:
        time.sleep(10) # Check every 10 seconds
        
        if not os.path.exists(STATE_FILE):
            continue
            
        with open(STATE_FILE, 'r') as f:
            try:
                state = json.load(f)
            except:
                continue
                
        changes_made = False
        current_time = time.time()
        
        for ip, data in state.items():
            if not data.get('currently_banned', False):
                continue
                
            strikes = data.get('strikes', 1)
            
            # If they have 4 or more strikes, they are permanently banned. Skip them.
            if strikes > len(BAN_DURATIONS):
                continue
                
            # Calculate how long they should be banned
            ban_length_seconds = BAN_DURATIONS[strikes - 1]
            time_banned = data.get('banned_at', current_time)
            
            # Has enough time passed?
            if current_time - time_banned >= ban_length_seconds:
                print(f" Time is up for {ip}. Unbanning!")
                
                # 1. Unban command: sudo iptables -D INPUT -s <IP> -j DROP
                subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
                
                # 2. Update state
                state[ip]['currently_banned'] = False
                changes_made = True
                
                # 3. Write to Audit Log
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                log_line = f"[{timestamp}] UNBAN {ip} | timeout expired | rate: 0.00 | baseline: 0.00 | duration: N/A\n"
                with open("audit.log", "a") as f:
                    f.write(log_line)
                    
                # 4. Slack Alert
                notifier.send_alert(f" *UNBAN* \n*IP:* {ip} has served their time and is unbanned.")
                
        if changes_made:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f)

if __name__ == "__main__":
    check_and_unban()