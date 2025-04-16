#main-server.py
import signal
import sys
from network import TCPServer

def signal_handler(sig, frame):
    print('Shutting down server...')
    if server:
        server.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    server = None
    try:
        # Register signal handler for shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the server
        server = TCPServer()
        print("In-Memory DB Server with PubSub started")
        server.start()
    except KeyboardInterrupt:
        if server:
            server.shutdown()
    except Exception as e:
        print(f"Server error: {e}")
        if server:
            server.shutdown()