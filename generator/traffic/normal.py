import random
from typing import Dict, Tuple, Optional
from .base import TrafficStrategy

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

PATHS = [
    "/",
    "/home",
    "/about",
    "/contact",
    "/products",
    "/services",
    "/static/style.css",
    "/static/logo.png",
    "/static/app.js",
    "/blog/post/1",
    "/blog/post/2"
]

class NormalTraffic(TrafficStrategy):
    """
    Generates normal, non-malicious HTTP traffic.
    """
    
    def generate(self, base_url: str) -> Tuple[Dict, Optional[Dict]]:
        path = random.choice(PATHS)
        url = f"{base_url}{path}"
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

        # Occasionally add a Referer
        if random.random() > 0.5:
            headers["Referer"] = base_url + random.choice(PATHS)

        request_kwargs = {
            "method": "GET",
            "url": url,
            "headers": headers
        }
        
        return request_kwargs, None

# Legacy function wrapper for compatibility if needed, but we'll phase it out
def generate(base_url: str) -> Dict:
    return NormalTraffic().generate(base_url)[0]
