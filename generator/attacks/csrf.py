import random
from typing import Dict, Tuple
from .base import BaseAttack

class CSRFAttack(BaseAttack):
    ACTIONS = [
        "transfer",
        "change_email",
        "delete_account",
        "update_password"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates a CSRF attack configuration.
        CSRF often involves a state-changing request without a token.
        Returns: (request_kwargs, answer_key_metadata)
        """
        action = random.choice(self.ACTIONS)
        endpoint = f"/account/{action}"
        url = f"{base_url}{endpoint}"
        
        # CSRF is typically a POST request
        method = "POST"
        
        data = {
            "amount": random.randint(100, 10000),
            "to_account": random.randint(1000, 9999)
        }
        
        # Crucially, no CSRF token is included in headers/data
        headers = {
            "Referer": "http://evil.com/exploit.html",
            "Cookie": "session_id=valid_session_12345"
        }

        request_kwargs = {
            "method": method,
            "url": url,
            "data": data,
            "headers": headers
        }
        
        metadata = {
            "type": "CSRF",
            "endpoint": endpoint,
            "payload": "Missing CSRF Token",
            "method": method
        }
        
        return request_kwargs, metadata
