import threading
import monitor
import unbanner
import dashboard

print(" Starting HNG DevSecOps Detection Engine...")

# Start the unbanner in the background
unban_thread = threading.Thread(target=unbanner.check_and_unban, daemon=True)
unban_thread.start()

# Start the log monitor (this will run forever in the main thread)
try:
    monitor.tail_log()
except KeyboardInterrupt:
    print("\n Shutting down engine...")