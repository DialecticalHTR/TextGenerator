import time


class RateLimiter:
    def __init__(self, wait_time: float):
        self.wait_time: float = wait_time
        self.start_time: time.time = time.time() - self.wait_time
    
    def __enter__(self):
        while time.time() < self.start_time + self.wait_time:
            continue
        self.start_time = time.time()
    
    def __exit__(self, *_):
        pass
