# Server Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Traffic Configuration
MIN_REQUESTS = 50
MAX_REQUESTS = 100
ATTACK_PROBABILITY = 0.3  # 30% of traffic is malicious
