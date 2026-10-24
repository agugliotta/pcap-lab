import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

class QuietHandler(BaseHTTPRequestHandler):
    """
    A simple HTTP handler that returns 200 OK for everything
    and suppresses default logging to stderr.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        # Read body to simulate processing
        content_length = int(self.headers.get('Content-Length', 0))
        self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')

    def log_message(self, format, *args):
        # Override to suppress logging
        pass

class BackgroundServer:
    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Starts the server in a background thread."""
        self.server = HTTPServer((self.host, self.port), QuietHandler)
        # If port was 0, retrieve the port actually assigned by the OS
        self.port = self.server.server_port
        
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
        # Poll until server is ready (max 2 seconds)
        import socket
        start_time = time.time()
        while time.time() - start_time < 2:
            try:
                with socket.create_connection((self.host, self.port), timeout=0.1):
                    break
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(0.05)

    def stop(self):
        """Stops the background server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
