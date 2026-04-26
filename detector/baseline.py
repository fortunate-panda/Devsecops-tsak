import statistics
from collections import deque

class TrafficBaseline:
    def __init__(self, window_size_minutes=30):
        # We store one data point per minute for 30 minutes
        self.history = deque(maxlen=window_size_minutes)
        self.error_history = deque(maxlen=window_size_minutes)

    def add_data_point(self, total_requests, total_errors):
        self.history.append(total_requests)
        self.error_history.append(total_errors)

    def get_stats(self):
        if len(self.history) < 2:  # Need at least 2 points for Std Dev
            return 0, 1, 0  # Default mean, std_dev, error_mean
        
        mean = statistics.mean(self.history)
        std_dev = statistics.stdev(self.history)
        error_mean = statistics.mean(self.error_history)
        
        # Avoid division by zero if traffic is perfectly flat
        return mean, (std_dev if std_dev > 0 else 1), error_mean