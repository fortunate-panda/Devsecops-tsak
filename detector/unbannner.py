import time
import subprocess
from threading import Thread

# tracking dictionary: { "IP": count_of_offenses }
offense_tracker = {}

# scheduled unbans: [ {"ip": "1.1.1.1", "unban_at": 171234567}, ... ]
scheduled_unbans = []

def get_ban_duration(offense_count):
    """Returns duration in seconds based on phase 6 rules."""
    if offense_count == 1:
        return 10 * 60  # 10 minutes
    elif offense_count == 2:
        return 30 * 60  # 30 minutes
    elif offense_count == 3:
        return 120 * 60 # 2 hours
    else:
        return None     # Never unban (4th offense)

def schedule_unban(ip):
    # Increment offense count
    offense_tracker[ip] = offense_tracker.get(ip, 0) + 1
    duration = get_ban_duration(offense_tracker[ip])
    
    if duration:
        unban_time = time.time() + duration
        scheduled_unbans.append({"ip": ip, "unban_at": unban_time})
        print(f"Scheduled unban for {ip} in {duration/60} minutes.")
    else:
        print(f"IP {ip} is now permanently banned (4th offense).")