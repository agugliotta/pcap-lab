import subprocess
import time
import os
import signal
from contextlib import contextmanager

@contextmanager
def packet_capture(interface: str, output_file: str, capture_filter: str = "port 8080"):
    """
    Context manager to run tcpdump during the execution of a block of code.
    
    Args:
        interface: The network interface to capture on (e.g., 'lo', 'eth0').
        output_file: Path to save the .pcap file.
        capture_filter: BPF filter string for tcpdump.
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Remove existing file if present
    if os.path.exists(output_file):
        os.remove(output_file)

    # Start tcpdump
    # -i: interface
    # -w: write to file
    # -U: packet-buffered (write immediately)
    # -s 0: snaplen (default 262144 is usually fine, 0 means full packet)
    cmd = [
        "tcpdump",
        "-i", interface,
        "-w", output_file,
        "-U",
        "-s", "0",
        capture_filter
    ]
    
    print(f"Starting capture on {interface} -> {output_file}")
    
    # Start process
    # stdout=subprocess.DEVNULL suppresses packet count output
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True  # Start in new session to kill process group later
    )
    
    # Wait for tcpdump to initialize
    # 0.5s is usually enough for tcpdump to start on modern systems
    time.sleep(0.5)
    
    # Check if process died early (e.g. permission denied)
    if process.poll() is not None:
        stderr = process.stderr.read()
        print(f"Error: tcpdump failed to start: {stderr.strip()}")
    
    try:
        yield process
    finally:
        # Stop tcpdump
        print("Stopping capture...")
        try:
            # Kill the process group to ensure sudo tcpdump dies
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=2)
        except Exception:
            # Force kill if needed
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except:
                pass
        
        # Verify file creation
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"Capture finished. File size: {size} bytes")
        else:
            print("Warning: PCAP file was not created.")
