from abc import abstractmethod
from typing import Dict, Tuple, Optional
from ..traffic.base import TrafficStrategy

class BaseAttack(TrafficStrategy):
    """
    Abstract Base Class for all attack types.
    """
    
    @abstractmethod
    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates an attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        pass
