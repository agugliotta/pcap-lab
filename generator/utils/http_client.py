import requests
import random
import time
from typing import Dict, Optional

class TrafficClient:
    """
    Handles the execution of HTTP requests with configurable delays and error handling.
    """
    
    def __init__(self, session: Optional[requests.Session] = None):
        self._session = session
        
    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session
        
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the session since it's not pickleable
        state['_session'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        
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
        if self._session is not None:
            self._session.close()
