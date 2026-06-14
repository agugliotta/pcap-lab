import os
import json
import time
from concurrent.futures import ProcessPoolExecutor
from .config import SERVER_HOST
from .utils.server import BackgroundServer
from .utils.capture import packet_capture
from .traffic_engine import TrafficEngine

class PcapGenerator:
    """
    Orchestrates the server, packet capture, and traffic engine.
    """
    
    def __init__(self, interface: str, output_dir: str = "output"):
        self.interface = interface
        self.output_dir = output_dir
        
    def _generate_single(self, engine: TrafficEngine):
        """
        Runs the full generation process for a single student engine.
        This method is designed to be called in a separate process.
        """
        student_dir = os.path.join(self.output_dir, engine.student_id)
        pcap_file = os.path.join(student_dir, "traffic.pcap")
        key_file = os.path.join(student_dir, "answer_key.json")
        
        os.makedirs(student_dir, exist_ok=True)
        
        server = BackgroundServer(host=SERVER_HOST, port=0)
        server.start()
        print(f"Server started on http://{server.host}:{server.port} for student: {engine.student_id}")
        
        try:
            # Start Capture
            with packet_capture(self.interface, pcap_file, capture_filter=f"port {server.port}"):
                
                print(f"Generating traffic for student: {engine.student_id}...")
                start_time = time.time()
                
                # Execute Traffic
                answer_data = engine.run()
                
                duration = time.time() - start_time
                print(f"Traffic generation complete for student {engine.student_id} in {duration:.2f}s")
                
                # Save Answer Key
                with open(key_file, "w") as f:
                    json.dump(answer_data, f, indent=2)
                print(f"Answer key saved to {key_file}")
                
        except Exception as e:
            print(f"\nError during generation for student {engine.student_id}: {e}")
            raise
        finally:
            server.stop()
            print(f"Server stopped for student: {engine.student_id}")

    def generate_batch(self, engines: list[TrafficEngine], jobs: int = 1):
        """
        Runs the generation process for multiple engines (sequential or parallel).
        """
        if jobs <= 1:
            for engine in engines:
                self._generate_single(engine)
        else:
            with ProcessPoolExecutor(max_workers=jobs) as executor:
                executor.map(self._generate_single, engines)
