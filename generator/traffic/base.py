from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

class TrafficStrategy(ABC):
    """
    Abstract Base Class for all traffic generation strategies (Normal and Attack).
    """
    
    @abstractmethod
    def generate(self, base_url: str) -> Tuple[Dict, Optional[Dict]]:
        """
        Generates traffic request configuration.
        
        Returns:
            Tuple containing:
            - request_kwargs (Dict): Arguments for requests.request (method, url, headers, etc.)
            - metadata (Optional[Dict]): Metadata for the answer key. None for normal traffic.
        """
        pass
