from flask import Flask, jsonify, render_template
import time

app = Flask(__name__)

# This data would ideally be imported from your monitor/detector logic
stats = {
    "banned_ips": ["192.168.1.50", "45.33.22.11"],
    "global_rps": 12.5,
    "top_ips": {"1.1.1.1": 450, "8.8.8.8": 300},
    "start_time": time.time()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def metrics():
    uptime = int(time.time() - stats["start_time"])
    return jsonify({
        "banned_count": len(stats["banned_ips"]),
        "rps": stats["global_rps"],
        "top_ips": stats["top_ips"],
        "uptime": f"{uptime} seconds"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)