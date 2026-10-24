import random
import time
from typing import Dict, Optional

import requests

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
            self._session.trust_env = False
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
            response = self.session.request(**request_kwargs, timeout=timeout)
            response.close()
        except requests.RequestException as exc:
            raise RuntimeError(f"HTTP request failed: {exc}") from exc
        finally:
            if delay_range:
                time.sleep(random.uniform(*delay_range))

    def close(self):
        if self._session is not None:
            self._session.close()
