import requests
import random
import time
from typing import Dict, Optional

class TrafficClient:
    """
    Handles the execution of HTTP requests with configurable delays and error handling.
    """
    
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        
    def execute(self, request_kwargs: Dict, timeout: int = 1, delay_range: tuple = (0.05, 0.2)):
        """
        Executes a single HTTP request and sleeps for a random duration.
        """
        try:
            self.session.request(**request_kwargs, timeout=timeout)
            
            # Simulate human/realistic traffic intervals
            if delay_range:
                time.sleep(random.uniform(*delay_range))
        except requests.RequestException:
            # We ignore request errors (e.g. server busy) during traffic generation
            # as the focus is on the packets being sent.
            pass
            
    def close(self):
        self.session.close()
