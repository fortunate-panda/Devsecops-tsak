#   DevSecOps: Nextcloud Anomaly Detection Engine

An intelligent, real-time traffic monitoring and anomaly detection engine built to protect a public-facing Nextcloud deployment. This system continuously tails Nginx JSON access logs, learns what "normal" traffic looks like over time, and dynamically blocks malicious IP addresses using Linux `iptables`.

##  Live Deployment Links
* **Metrics Dashboard:** [https://monitor.yourdomain.com] *(Replace with your actual domain)*
* **Nextcloud Server IP:** `[YOUR.SERVER.IP.ADDRESS]`
* **GitHub Repository:** [Link to this public repo]
* **Technical Blog Post:** [Link to your Dev.to / Medium / Hashnode post]

---

## 🛠️ Technology Stack & Language Choice
**Language:** Python 3  
**Infrastructure:** Docker, Docker Compose, Nginx, Nextcloud (kefaslungu/hng-nextcloud)

### Why Python?
Python was chosen over Go because of its highly expressive standard library, which is perfectly suited for time-series data and statistical analysis:
1. **The Sliding Window:** Python's `collections.deque` provides highly efficient $O(1)$ appends and pops from either end, making the eviction of expired timestamps incredibly fast without needing an external rate-limiting library.
2. **The Baseline Math:** The built-in `statistics` module allows for clean, readable calculation of rolling means and standard deviations without pulling in heavy external dependencies.

---

##  Core Engine Logic

### 1. The Sliding Window (Traffic Memory)
The detection engine tracks request rates in real-time over a **60-second sliding window**. 
* **Structure:** It uses two `deque` objects—one global deque for all server traffic, and a dictionary of individual deques mapped to specific IP addresses.
* **Eviction Logic:** Every time a new request is parsed from the Nginx log, the current UNIX timestamp is appended to the right side of the deque. Immediately after, a `while` loop checks the left side (the oldest timestamps). Any timestamp older than 60.0 seconds is popped off (`popleft()`). The remaining length of the deque is divided by 60 to determine the exact Requests Per Second (RPS).

### 2. The Rolling Baseline (Machine Learning)
To spot anomalies, the system must understand normal traffic patterns. 
* **Window Size:** The baseline stores the global RPS over a rolling **30-minute window**.
* **Recalculation:** A background daemon thread recalculates the effective mean and standard deviation every **60 seconds**.
* **Floor Values:** To prevent mathematical crashes (such as a `ZeroDivisionError` when calculating the Z-Score during periods of zero traffic), the engine enforces safe floor values: `current_mean` initializes at `1.0`, and `current_stddev` cannot drop below `0.1`.

### 3. Detection & Response
When a request is processed, the system calculates the IP's **Z-Score** based on the current baseline.
An IP is blocked if:
1. Its Z-Score exceeds **3.0**.
2. Its RPS is more than **5x** the baseline mean (Hard Multiplier).

*Action:* The engine immediately executes `sudo iptables -A INPUT -s <IP> -j DROP`, writes to the structured `audit.log`, and fires a Slack Webhook alert.

### 4. Exponential Backoff (Auto-Unban)
A timekeeper daemon checks the ban state every 10 seconds. Bans are released on a strict schedule:
* **1st Offense:** 10 minutes
* **2nd Offense:** 30 minutes
* **3rd Offense:** 2 hours
* **4th Offense:** Permanent Ban

---

##  Setup Instructions (From Fresh VPS)

If you are starting with a fresh Ubuntu VPS (22.04 or 24.04), follow these steps to deploy the complete stack:

### Step 1: System Updates & Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose python3-venv python3-pip -y
```

### Step 2: Clone the Repository
```bash
git clone [YOUR_GITHUB_REPO_LINK] hng-task
cd hng-task
```

### Step 3: Start the Docker Infrastructure
This spins up Nextcloud and the Nginx reverse proxy, creating a shared volume for the JSON logs.
```bash
sudo docker-compose up -d
```

### Step 4: Configure the Python Environment
```bash
cd detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Configure Thresholds & Slack
Edit the `config.yaml` file to include your Slack Webhook URL.
```yaml
slack_webhook_url: "[https://hooks.slack.com/services/](https://hooks.slack.com/services/)..."
thresholds:
  z_score: 3.0
  hard_multiplier: 5.0
```

### Step 6: Run the Daemon
Start the main engine, which handles log tailing, baseline recalculation, auto-unbanning, and the Flask UI dashboard simultaneously.
```bash
python3 main.py
```
*Note: The UI dashboard will be accessible via your configured domain name on port 80.*

---

##  Repository Structure
```text
detector/
  ├── main.py           # Master thread controller
  ├── monitor.py        # Log tailing & JSON parsing
  ├── baseline.py       # 30-min rolling math calculations
  ├── detector.py       # Sliding window & Z-score logic
  ├── blocker.py        # iptables execution & audit logging
  ├── unbanner.py       # Backoff schedule timekeeper
  ├── notifier.py       # Slack webhook integration
  ├── dashboard.py      # Flask UI & server stats
  ├── config.yaml       # User-defined thresholds
  ├── requirements.txt  
  └── templates/
      └── index.html    # Frontend auto-refreshing dashboard
nginx/
  └── nginx.conf        # Proxy & JSON log formatting
docs/
  └── architecture.png
screenshots/
  ├── Tool-running.png
  ├── Ban-slack.png
  ├── Unban-slack.png
  ├── Global-alert-slack.png
  ├── Iptables-banned.png
  ├── Audit-log.png
  └── Baseline-graph.png
docker-compose.yml
README.md
```
```