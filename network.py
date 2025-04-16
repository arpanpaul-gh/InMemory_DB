#network.py
import socket
import json
import time
import threading
from db import InMemoryDB
from storage import Storage
from config import SERVER_HOST, SERVER_PORT
from pubsub import PubSub

class TCPServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.db = InMemoryDB()
        self.storage = Storage()
        self.pubsub = PubSub()
        self.load_data()
        self.running = False
        self.clients = set()
        self.clients_lock = threading.Lock()

    def load_data(self):
        data = self.storage.load()
        for key, value in data.items():
            self.db.set(key, value)

    def save_data(self):
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self.db.ttl_data.items()
            if expiry_time < current_time
        ]
        for key in expired_keys:
            del self.db.data[key]
            del self.db.ttl_data[key]
        self.storage.save(self.db.data)

    def start(self):
        self.running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server listening on {self.host}:{self.port}")
            
            # Start periodic data saving in a separate thread
            save_thread = threading.Thread(target=self.periodic_save, daemon=True)
            save_thread.start()
            
            #added
            ttl_cleanup_thread = threading.Thread(target=self.periodic_ttl_cleanup, daemon=True)
            ttl_cleanup_thread.start()

            try:
                while self.running:
                    try:
                        s.settimeout(1.0)  # Allow checking self.running every second
                        conn, addr = s.accept()
                        with self.clients_lock:
                            self.clients.add(conn)
                        client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                        client_thread.daemon = True
                        client_thread.start()
                    except socket.timeout:
                        continue
            except KeyboardInterrupt:
                print("Server shutdown initiated")
            finally:
                self.running = False
                print("Server shutdown complete")

    def periodic_save(self, interval=60):
        """Periodically save data to disk"""
        while self.running:
            time.sleep(interval)
            self.save_data()
            print(f"Periodic data save completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    #added
    def periodic_ttl_cleanup(self, interval=1):
        while self.running:
            time.sleep(interval)
            # Get current time once to avoid inconsistencies
            current_time = time.time()
            expired_keys = [
                key for key, expiry_time in list(self.db.ttl_data.items())
                if expiry_time < current_time
            ]

            for key in expired_keys:
                if key in self.db.data:
                    del self.db.data[key]
                    del self.db.ttl_data[key]
                    print(f"TTL expired for key: {key}")
                    self.db.notify_observers("expire", key)


    def handle_client(self, conn, addr):
        """Handle communication with a client."""
        try:
            print(f"Connected by {addr}")
            while self.running:
                try:
                    conn.settimeout(1.0)
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    command = json.loads(data.decode('utf-8'))
                    print(f"Received command: {command}")
                    
                    # Check if it's a PubSub command
                    if command.get("type") == "pubsub":
                        response = self.pubsub.handle_command(command, conn)
                    else:
                        response = self.handle_db_command(command)
                        
                        # If it was a data modification command, publish an update
                        if command.get("action") in ["set", "set_with_ttl", "delete"]:
                            key = command.get("key", "")
                            self.pubsub.publish("db_updates", {
                                "operation": command.get("action"),
                                "key": key,
                                "timestamp": time.time()
                            })
                    
                    conn.sendall(json.dumps(response).encode('utf-8'))
                except socket.timeout:
                    continue
                except json.JSONDecodeError:
                    conn.sendall(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                except Exception as e:
                    print(f"Error handling client {addr}: {e}")
                    conn.sendall(json.dumps({"error": str(e)}).encode('utf-8'))
        except Exception as e:
            print(f"Connection error with {addr}: {e}")
        finally:
            with self.clients_lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            conn.close()
            print(f"Connection closed with {addr}")

    def handle_db_command(self, command):
        """Handle database commands."""
        action = command.get("action")
        key = command.get("key")
        value = command.get("value")
        ttl = command.get("ttl")
    
        if action == "get":
            result = self.db.get(key)
            # Add TTL information if available
            remaining_ttl = None
            if key in self.db.ttl_data:
                remaining_ttl = max(0, int(self.db.ttl_data[key] - time.time()))
            return {"result": result, "ttl_remaining": remaining_ttl}
        elif action == "set":
            self.db.set(key, value)
            self.save_data()
            return {"result": "OK"}
        elif action == "set_with_ttl":
            if ttl is None:
                return {"error": "TTL not provided"}
            try:
                ttl_value = int(ttl)
                self.db.set(key, value, ttl_value)
                self.save_data()
                return {"result": "OK", "ttl_set": ttl_value}
            except ValueError:
                return {"error": "TTL must be an integer"}
        elif action == "delete":
            success = self.db.delete(key)
            self.save_data()
            return {"result": "OK" if success else "Key not found"}
        elif action == "keys":
            keys = self.db.keys()
            return {"result": keys}
        else:
            return {"error": "Invalid action"}

    def shutdown(self):
        """Gracefully shutdown the server."""
        self.running = False
        self.save_data()
        print("Server is shutting down...")
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass

if __name__ == "__main__":
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()