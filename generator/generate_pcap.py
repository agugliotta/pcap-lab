import time
import random
import json
import requests
import os
import sys

# Import local modules
# Add parent directory to path to allow imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.config import SERVER_HOST, SERVER_PORT, BASE_URL, MIN_REQUESTS, MAX_REQUESTS, ATTACK_PROBABILITY
from generator.utils.seed import init_seed
from generator.utils.capture import packet_capture
from generator.utils.server import BackgroundServer
from generator.traffic import normal
from generator.attacks import sqli, xss, idor, csrf

def run_traffic(student_id: str, enabled_attacks: list = None, num_requests: int = None, attack_count: int = None, attack_ratio: float = None):
    """
    Main logic to generate traffic stream.
    Returns list of executed attacks for the answer key.
    """
    
    # Mapping of attack names to modules
    attack_map = {
        "sqli": sqli,
        "xss": xss,
        "idor": idor,
        "csrf": csrf
    }
    
    # Filter enabled attacks
    if enabled_attacks:
        available_attacks = [attack_map[a] for a in enabled_attacks if a in attack_map]
    else:
        available_attacks = list(attack_map.values())
        
    if not available_attacks:
        print("Warning: No valid attacks enabled. Running in normal traffic mode.")

    # Initialize Random Seed
    seed_val = init_seed(student_id)
    print(f"Initialized seed: {seed_val} for student: {student_id}")
    
    # Determine total requests
    if num_requests is not None:
        total_requests = num_requests
    else:
        total_requests = random.randint(MIN_REQUESTS, MAX_REQUESTS)
    print(f"Planning {total_requests} requests...")
    
    # Validate attack count and ratio
    if attack_count is not None and (attack_count < 0 or attack_count > total_requests):
        raise ValueError(f"attack_count ({attack_count}) must be between 0 and total requests ({total_requests})")
        
    if attack_ratio is not None and (attack_ratio < 0.0 or attack_ratio > 1.0):
        raise ValueError(f"attack_ratio ({attack_ratio}) must be between 0.0 and 1.0")

    final_attack_count = None
    if attack_count is not None:
        final_attack_count = attack_count
    elif attack_ratio is not None:
        final_attack_count = int(round(total_requests * attack_ratio))
        final_attack_count = max(0, min(total_requests, final_attack_count))

    # Pre-calculate attack indices if count or ratio is specified
    attack_indices = None
    if final_attack_count is not None:
        if not available_attacks:
            final_attack_count = 0
        attack_indices = set(random.sample(range(total_requests), final_attack_count))
    
    executed_attacks = []
    
    # Create a session for connection reuse (like a real browser)
    session = requests.Session()
    
    for i in range(total_requests):
        # Decide if attack or normal
        if attack_indices is not None:
            is_attack = (i in attack_indices) and available_attacks
        else:
            is_attack = random.random() < ATTACK_PROBABILITY and available_attacks
        
        request_kwargs = {}
        
        if is_attack:
            attack_module = random.choice(available_attacks)
            request_kwargs, metadata = attack_module.generate(BASE_URL)
            executed_attacks.append(metadata)
        else:
            request_kwargs = normal.generate(BASE_URL)
            
        # Execute Request
        try:
            # Add timeout to prevent hanging
            session.request(**request_kwargs, timeout=1)
            
            # Simulate human reading time (very short for speed, but non-zero)
            time.sleep(random.uniform(0.05, 0.2))
            
        except requests.RequestException:
            # Ignore errors to keep the flow going
            pass
            
    return {
        "seed": str(seed_val),
        "student_id": student_id,
        "settings": {
            "num_requests": num_requests,
            "enabled_attacks": enabled_attacks if enabled_attacks is not None else list(attack_map.keys()),
            "attack_count": attack_count,
            "attack_ratio": attack_ratio
        },
        "total_requests": total_requests,
        "attacks": executed_attacks
    }


def generate_pcap(student_id: str, interface: str, output_dir: str = "output", enabled_attacks: list = None, num_requests: int = None, attack_count: int = None, attack_ratio: float = None):
    """
    Orchestrates the server, capture and traffic generation.
    """
    student_dir = os.path.join(output_dir, student_id)
    os.makedirs(student_dir, exist_ok=True)
    
    pcap_file = os.path.join(student_dir, "traffic.pcap")
    key_file = os.path.join(student_dir, "answer_key.json")
    
    # Start Dummy Server
    server = BackgroundServer(host=SERVER_HOST, port=SERVER_PORT)
    server.start()
    print(f"Server started on {BASE_URL}")
    
    try:
        # Start Capture
        # We capture on the specified interface, filtered to our port
        with packet_capture(interface, pcap_file, capture_filter=f"port {SERVER_PORT}"):
            
            # Run Traffic Generation
            print("Generating traffic...")
            start_time = time.time()
            
            answer_data = run_traffic(student_id, enabled_attacks=enabled_attacks, num_requests=num_requests, attack_count=attack_count, attack_ratio=attack_ratio)
            
            duration = time.time() - start_time
            print(f"Traffic generation complete in {duration:.2f}s")
            
            # Save Answer Key
            with open(key_file, "w") as f:
                json.dump(answer_data, f, indent=2)
            print(f"Answer key saved to {key_file}")
            
    except Exception as e:
        print(f"\nError during generation: {e}")
        raise
    finally:
        server.stop()
        print("Server stopped.")

if __name__ == "__main__":
    # Keeping minimal compatibility for direct execution if needed
    import argparse
    parser = argparse.ArgumentParser(description="Generate PCAP traffic for a student.")
    parser.add_argument("student_id", help="Unique identifier for the student")
    parser.add_argument("interface", help="Network interface to capture")
    parser.add_argument("--output-dir", default="output", help="Base output directory")
    parser.add_argument("--requests", type=int, help="Exact number of requests to generate")
    parser.add_argument("--attack-count", type=int, help="Exact number of attacks to generate")
    parser.add_argument("--attack-ratio", type=float, help="Ratio of attacks to total requests (0.0 to 1.0)")
    args = parser.parse_args()
    
    try:
        generate_pcap(args.student_id, args.interface, args.output_dir, num_requests=args.requests, attack_count=args.attack_count, attack_ratio=args.attack_ratio)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
