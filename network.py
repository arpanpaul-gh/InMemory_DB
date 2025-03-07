
import socket
import json
import time
from db import InMemoryDB
from storage import Storage
from config import SERVER_HOST, SERVER_PORT

class TCPServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.db = InMemoryDB()
        self.storage = Storage()
        self.load_data()

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        try:
                            command = json.loads(data.decode('utf-8'))
                            response = self.handle_command(command)
                            conn.sendall(json.dumps(response).encode('utf-8'))
                        except Exception as e:
                            conn.sendall(json.dumps({"error": str(e)}).encode('utf-8'))

    def handle_command(self, command):
        action = command.get("action")
        key = command.get("key")
        value = command.get("value")
        ttl = command.get("ttl")

        if action == "get":
            result = self.db.get(key)
            self.save_data()
            return {"result": result}
        elif action == "set":
            self.db.set(key, value)
            self.save_data()
            return {"result": "OK"}
        elif action == "set_with_ttl":
            if ttl is None:
                return {"error": "TTL not provided"}
            self.db.set(key, value, ttl)
            self.save_data()
            return {"result": "OK"}
        elif action == "delete":
            self.db.delete(key)
            self.save_data()
            return {"result": "OK"}
        else:
            return {"error": "Invalid action"}

if __name__ == "__main__":
    server = TCPServer()
    server.start()