from collections import deque, defaultdict
import time
import json

# Dictionary to store a deque of timestamps for each IP
# deque of timestamps
ip_history = defaultdict(deque)

def monitor_traffic(log_file_path):
    for line in tail_log(log_file_path):
        try:
            
            log_data = json.loads(line)
            ip = log_data['source_ip']
            current_time = time.time()

            # Append the current timestamp to this IP's deque
            ip_history[ip].append(current_time)

            #- Remove timestamps older than 60 seconds
            while ip_history[ip] and ip_history[ip][0] < current_time - 60:
                ip_history[ip].popleft()

           
            rpm = len(ip_history[ip]) # Total requests in the last 60s
            rps = rpm / 60.0
            
            print(f"IP: {ip} | RPM: {rpm} | RPS: {rps:.2f}")
            
            
        except (json.JSONDecodeError, KeyError) as e:
          
            continue

if __name__ == "__main__":
    # Use the path from your config.yaml
    LOG_PATH = "/var/log/nginx/hng-access.log"
    monitor_traffic(LOG_PATH)