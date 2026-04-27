import time
import yaml
import threading
from collections import deque, defaultdict
import baseline  
import os
import blocker


# Get the path of the folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# Load our rulebook
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
    
    
    
Z_SCORE_LIMIT = config['thresholds']['z_score']
HARD_MULTIPLIER = config['thresholds']['hard_multiplier']

ip_windows = defaultdict(deque)
global_window = deque()

# <-- NEW: Start the baseline engine in the background so it ticks every 60 seconds
threading.Thread(target=baseline.recalculate_baseline, args=(global_window,), daemon=True).start()

def clean_old_requests(current_time):
    cutoff_time = current_time - 10.0
    while global_window and global_window[0] < cutoff_time:
        global_window.popleft()

    for ip in list(ip_windows.keys()):
        while ip_windows[ip] and ip_windows[ip][0] < cutoff_time:
            ip_windows[ip].popleft()
        if not ip_windows[ip]:
            del ip_windows[ip]

def process_request(ip, status_code):
    current_time = time.time()
    global_window.append(current_time)
    ip_windows[ip].append(current_time)
    
    clean_old_requests(current_time)
    
    global_rps = len(global_window) / 1.0
    ip_rps = len(ip_windows[ip]) / 1.0
    
    # <-- NEW: Calculate the Z-Score for this IP!
    ip_z_score = baseline.get_z_score(ip_rps)
    
    # <-- NEW: Check if they broke the rules!
    # Rule 1: Z-score is greater than 3.0
    # Rule 2: Their speed is 5x higher than the normal average
    #if ip_z_score > 2:
     #   blocker.ban_ip(ip, condition="Z-Score Exceeded (>3.0)", rate=ip_rps, baseline_mean=baseline.current_mean)
   # elif ip_rps > (baseline.current_mean * HARD_MULTIPLIER):
      #  blocker.ban_ip(ip, condition="Hard Multiplier Exceeded (>5x)", rate=ip_rps, baseline_mean=baseline.current_mean)
    #else:
        # Just standard traffic
     #   pass
     
# ... previous code calculating ip_rps and ip_z_score ...

    # Check if they broke the rules!
    if ip_z_score > 3.0: # You can keep your original logic here
        blocker.ban_ip(ip, condition="Z-Score Exceeded", rate=ip_rps, baseline_mean=baseline.current_mean)
    
    # TEMPORARY TEST: Trigger if RPS is higher than 2
    # This should be at the same indentation level as the 'if' above
    if ip_rps > 2.0:
        blocker.ban_ip(ip, condition="Manual Trigger Test", rate=ip_rps, baseline_mean=baseline.current_mean)
        
        
        
        
        
        
import json

def metrics_dumper():
    """Saves the current brain stats to a file every 2 seconds for the dashboard."""
    while True:
        time.sleep(2)
        global_rps = len(global_window) / 60.0
        
        # Calculate Top 10 IPs
        ip_rates = {ip: len(window)/60.0 for ip, window in ip_windows.items()}
        # Sort them from highest to lowest RPS
        top_ips = sorted(ip_rates.items(), key=lambda x: x[1], reverse=True)[:10]

        metrics = {
            "global_rps": global_rps,
            "top_ips": top_ips,
            "mean": baseline.current_mean,
            "stddev": baseline.current_stddev
        }
        
        with open("metrics.json", "w") as f:
            json.dump(metrics, f)

# Start the dumper in the background
threading.Thread(target=metrics_dumper, daemon=True).start()




global_z = baseline.get_z_score(global_rps)
    if global_z > Z_SCORE_LIMIT or global_rps > (baseline.current_mean * HARD_MULTIPLIER):
        # We only send an alert, we don't ban for global spikes (it might just be a viral tweet!)
        import notifier
        notifier.send_alert(f" *GLOBAL TRAFFIC SPIKE* \nRate: {global_rps:.2f} req/s | Mean: {baseline.current_mean:.2f}")