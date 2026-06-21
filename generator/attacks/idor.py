import random
from typing import Dict, Tuple
from .base import BaseAttack
from ..utils.obfuscator import Obfuscator

class IDORAttack(BaseAttack):
    # IDOR targets usually involve iterating IDs
    ENDPOINTS_TEMPLATES = [
        "/user/{id}",
        "/api/invoice/{id}",
        "/messages/{id}",
        "/order/view?id={id}"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates an IDOR attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        template = random.choice(self.ENDPOINTS_TEMPLATES)
        # Simulate accessing a sensitive ID that isn't ours (e.g., 1-1000)
        target_id = str(random.randint(1, 10000))
        obfuscated_id = Obfuscator.obfuscate(target_id, self.obfuscation_level)
        
        if "?id=" in template:
            endpoint = template.format(id=obfuscated_id).split("?")[0]
            params = {"id": obfuscated_id}
            url = f"{base_url}{endpoint}"
        else:
            endpoint = template.format(id=obfuscated_id)
            params = None
            url = f"{base_url}{endpoint}"

        request_kwargs = {
            "method": "GET",
            "url": url,
            "params": params
        }
        
        metadata = {
            "type": "IDOR",
            "endpoint": endpoint,
            "payload": obfuscated_id,
            "method": "GET"
        }
        
        return request_kwargs, metadata
