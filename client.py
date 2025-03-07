
import socket
import json

class TCPClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port

    def send_command(self, action, key, value=None, ttl=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port)) 
            command = {"action": action, "key": key}
            if value is not None:
                command["value"] = value
            if ttl is not None:
                command["ttl"] = ttl
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(1024)
            return json.loads(data.decode('utf-8'))

def main():
    client = TCPClient()
    print("In-Memory DB Client")
    print("Commands: get <key>, set <key> <value>, set_with_ttl <key> <value> <ttl>, delete <key>")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            parts = user_input.split()
            action = parts[0].lower()
            if action == "get" and len(parts) == 2:
                key = parts[1]
                response = client.send_command("get", key)
                print(response)
            elif action == "set" and len(parts) >= 3:
                key = parts[1]
                value = " ".join(parts[2:]) 
                response = client.send_command("set", key, value)
                print(response)
            elif action == "set_with_ttl" and len(parts) >= 4:
                key = parts[1]
                value = " ".join(parts[2:-1])  
                ttl = int(parts[-1])  
                response = client.send_command("set_with_ttl", key, value, ttl)
                print(response)
            elif action == "delete" and len(parts) == 2:
                key = parts[1]
                response = client.send_command("delete", key)
                print(response)
            else:
                print("Invalid command. Usage: get <key>, set <key> <value>, set_with_ttl <key> <value> <ttl>, delete <key>")
        except KeyboardInterrupt:
            print("\nExiting client.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()