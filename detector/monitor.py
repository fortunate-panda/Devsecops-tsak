import time
import json
import os
import detector  

# This is the shared volume folder Nginx is writing to
LOG_FILE = "logs/hng-access.log"

def tail_log():
    """Watches the log file for new lines, just like a security camera."""
    
    # Wait until Nginx actually creates the file
    while not os.path.exists(LOG_FILE):
        print("Waiting for Nginx to create the log file...")
        time.sleep(1)
        
    print(f"Found log file at {LOG_FILE}. Monitoring for traffic...")
    
    with open(LOG_FILE, 'r') as f:
        # seek(0, 2) means "go to the very end of the file"
        # We only care about NEW traffic, not old traffic.
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            
            # If there is no new line, wait 0.1 seconds and check again
            if not line:
                time.sleep(0.1)
                continue
            
            try:
                # Nginx wrote this as JSON, so we decode it into a Python dictionary
                data = json.loads(line)
                print(f" Saw traffic: IP {data['source_ip']} visited {data['path']} (Status: {data['status']})")
                
                # IN THE NEXT STEP: We will send this 'data' to our sliding window memory!
                detector.process_request(data['source_ip'], 200)
                
            except json.JSONDecodeError:
                # If Nginx writes a weird line, just ignore it and don't crash
                pass

if __name__ == "__main__":
    tail_log()