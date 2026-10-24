import os
import selectors
import signal
import subprocess
import time
from contextlib import contextmanager


def _wait_until_ready(process, interface, timeout=5):
    deadline = time.monotonic() + timeout
    with selectors.DefaultSelector() as selector:
        selector.register(process.stderr, selectors.EVENT_READ)
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"tcpdump failed to start on interface {interface}: {process.stderr.read().strip()}")
            if selector.select(timeout=0.1):
                line = process.stderr.readline()
                if "listening on" in line:
                    return
    raise RuntimeError(f"tcpdump did not become ready on interface {interface}.")


@contextmanager
def packet_capture(interface: str, output_file: str, capture_filter: str = "port 8080"):
    """Capture only after tcpdump reports readiness, and fail on incomplete files."""
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    cmd = ["tcpdump", "--immediate-mode", "-n", "-i", interface, "-w", output_file, "-U", "-s", "0", capture_filter]
    print(f"Starting capture on {interface} -> {output_file}")
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
    except FileNotFoundError as exc:
        raise RuntimeError("tcpdump is not installed or not available on PATH. Install tcpdump and retry with sudo.") from exc

    forced = False
    try:
        _wait_until_ready(process, interface)
        yield process
    finally:
        print("Stopping capture...")
        try:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
            try:
                _, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                forced = True
                os.killpg(process.pid, signal.SIGKILL)
                _, stderr = process.communicate()
        finally:
            process.stderr.close()

    if forced or process.returncode not in (0, -signal.SIGINT):
        raise RuntimeError(f"tcpdump failed while capturing: {stderr.strip()}")
    if not os.path.exists(output_file) or os.path.getsize(output_file) <= 24:
        raise RuntimeError("Capture contains no packets. Use the loopback interface (lo on Linux, lo0 on macOS).")
    print(f"Capture finished. File size: {os.path.getsize(output_file)} bytes")
