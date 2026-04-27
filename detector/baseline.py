import time
import statistics
import threading
from collections import deque

# This stores the average requests-per-second for the last 30 minutes
history_30m = deque(maxlen=30)

# The prompt asks us to keep track of baselines per hour (e.g., "14" for 2 PM)
hourly_baselines = {}

# We set safe default values so the math doesn't crash during the first few minutes
current_mean = 1.0 
current_stddev = 0.1 

def recalculate_baseline(detector_global_window):
    """Runs continuously in the background, updating our math every 60 seconds."""
    global current_mean, current_stddev
    
    while True:
        time.sleep(60) # Wait exactly 60 seconds
        
        # 1. Look at the detector's global pipe to see the last minute's RPS
        current_rps = len(detector_global_window) / 60.0
        
        # 2. Add it to our 30-minute history book
        history_30m.append(current_rps)
        
        # 3. If we have at least 2 minutes of data, calculate the new normal
        if len(history_30m) >= 2:
            current_mean = statistics.mean(history_30m)
            current_stddev = statistics.stdev(history_30m)
            
            # Standard deviation can't be exactly zero, or our Z-score math will divide by zero and crash!
            if current_stddev == 0:
                current_stddev = 0.1 
        
        # 4. Save this to the current hour's slot
        current_hour = time.strftime("%H")
        hourly_baselines[current_hour] = {"mean": current_mean, "stddev": current_stddev}
        
        print(f"📈 [BASELINE RECALCULATED] Mean: {current_mean:.2f} | StdDev: {current_stddev:.2f} | Hour: {current_hour}")

        # The prompt requires an audit log of baselines being recalculated. 
        # We write that to a file here:
        with open("audit.log", "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] BASELINE system | recalculated | rate: {current_rps:.2f} | baseline: {current_mean:.2f} | duration: N/A\n")

def get_z_score(current_rate):
    """Calculates how unusual the current traffic is. Over 3.0 is bad!"""
    return (current_rate - current_mean) / current_stddev