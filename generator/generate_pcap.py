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

def run_traffic(student_id: str, enabled_attacks: list = None):
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
    total_requests = random.randint(MIN_REQUESTS, MAX_REQUESTS)
    print(f"Planning {total_requests} requests...")
    
    executed_attacks = []
    
    # Create a session for connection reuse (like a real browser)
    session = requests.Session()
    
    for i in range(total_requests):
        # Decide if attack or normal
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
        "total_requests": total_requests,
        "attacks": executed_attacks
    }

def generate_pcap(student_id: str, interface: str, output_dir: str = "output", enabled_attacks: list = None):
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
            
            answer_data = run_traffic(student_id, enabled_attacks=enabled_attacks)
            
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
    args = parser.parse_args()
    
    try:
        generate_pcap(args.student_id, args.interface, args.output_dir)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
