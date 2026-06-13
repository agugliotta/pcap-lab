import os
import json
import time
from typing import Optional
from .config import SERVER_HOST, SERVER_PORT, BASE_URL
from .utils.server import BackgroundServer
from .utils.capture import packet_capture
from .traffic_engine import TrafficEngine

class PcapGenerator:
    """
    Orchestrates the server, packet capture, and traffic engine.
    """
    
    def __init__(self, engine: TrafficEngine, interface: str, output_dir: str = "output"):
        self.engine = engine
        self.interface = interface
        self.output_dir = output_dir
        
        # Setup output paths
        self.student_dir = os.path.join(self.output_dir, self.engine.student_id)
        self.pcap_file = os.path.join(self.student_dir, "traffic.pcap")
        self.key_file = os.path.join(self.student_dir, "answer_key.json")
        
        os.makedirs(self.student_dir, exist_ok=True)

    def generate(self):
        """
        Runs the full generation process.
        """
        server = BackgroundServer(host=SERVER_HOST, port=SERVER_PORT)
        server.start()
        print(f"Server started on {BASE_URL}")
        
        try:
            # Start Capture
            with packet_capture(self.interface, self.pcap_file, capture_filter=f"port {SERVER_PORT}"):
                
                print(f"Generating traffic for student: {self.engine.student_id}...")
                start_time = time.time()
                
                # Execute Traffic
                answer_data = self.engine.run()
                
                duration = time.time() - start_time
                print(f"Traffic generation complete in {duration:.2f}s")
                
                # Save Answer Key
                with open(self.key_file, "w") as f:
                    json.dump(answer_data, f, indent=2)
                print(f"Answer key saved to {self.key_file}")
                
        except Exception as e:
            print(f"\nError during generation: {e}")
            raise
        finally:
            server.stop()
            print("Server stopped.")
