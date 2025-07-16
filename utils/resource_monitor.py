import psutil
import threading
import time
import pandas as pd

class ResourceMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self.data = []

    def _record(self):
        while self.running:
            self.data.append({
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=None),
                'mem_mb': psutil.virtual_memory().used / (1024 * 1024)
            })
            time.sleep(self.interval)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def get_data(self):
        return pd.DataFrame(self.data)
