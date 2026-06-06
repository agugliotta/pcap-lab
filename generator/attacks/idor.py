import random
from typing import Dict, Tuple

# IDOR targets usually involve iterating IDs
ENDPOINTS_TEMPLATES = [
    "/user/{id}",
    "/api/invoice/{id}",
    "/messages/{id}",
    "/order/view?id={id}"
]

def generate(base_url: str) -> Tuple[Dict, Dict]:
    """
    Generates an IDOR attack configuration.
    Returns: (request_kwargs, answer_key_metadata)
    """
    template = random.choice(ENDPOINTS_TEMPLATES)
    # Simulate accessing a sensitive ID that isn't ours (e.g., 1-1000)
    target_id = random.randint(1, 10000)
    
    if "?id=" in template:
        endpoint = template.format(id=target_id).split("?")[0]
        params = {"id": target_id}
        url = f"{base_url}{endpoint}"
    else:
        endpoint = template.format(id=target_id)
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
        "payload": str(target_id),
        "method": "GET"
    }
    
    return request_kwargs, metadata
