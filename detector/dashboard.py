from flask import Flask, jsonify, render_template
import psutil
import json
import os
import time

app = Flask(__name__)
START_TIME = time.time()

@app.route('/')
def index():
    # Serves our HTML page
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    # 1. Get Uptime, CPU, and RAM
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    # 2. Get the Brain's metrics
    brain_metrics = {"global_rps": 0, "top_ips": [], "mean": 0, "stddev": 0}
    if os.path.exists("metrics.json"):
        try:
            with open("metrics.json", "r") as f:
                brain_metrics = json.load(f)
        except:
            pass

    # 3. Get the Bouncer's ban list
    banned_ips = []
    if os.path.exists("ban_state.json"):
        try:
            with open("ban_state.json", "r") as f:
                state = json.load(f)
                banned_ips = [ip for ip, data in state.items() if data.get('currently_banned')]
        except:
            pass

    # Send it all to the webpage
    return jsonify({
        "uptime": uptime_str,
        "cpu": cpu,
        "ram": ram,
        "banned_ips": banned_ips,
        "global_rps": brain_metrics["global_rps"],
        "top_ips": brain_metrics["top_ips"],
        "mean": brain_metrics["mean"],
        "stddev": brain_metrics["stddev"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)