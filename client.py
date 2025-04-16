#client.py
import socket
import json
import threading
import time
from config import SERVER_HOST, SERVER_PORT

class TCPClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.subscribed = False
        self.subscriber_thread = None
        self.running = False
        
    def connect(self):
        """Create a persistent connection to the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.running = True
        return self.socket
        
    def disconnect(self):
        """Close the connection to the server."""
        self.running = False
        if hasattr(self, 'socket'):
            self.socket.close()
            
    def send_command(self, action, key=None, value=None, ttl=None, type=None, channel=None, message=None):
        """Send a command to the server and get the response."""
        command = {}
        
        if type == "pubsub":
            command["type"] = "pubsub"
            command["action"] = action
            if channel:
                command["channel"] = channel
            if message is not None:
                command["message"] = message
        else:
            command["action"] = action
            if key is not None:
                command["key"] = key
            if value is not None:
                command["value"] = value
            if ttl is not None:
                command["ttl"] = ttl
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json.dumps(command).encode('utf-8'))
            data = s.recv(1024)
            return json.loads(data.decode('utf-8'))
            
    def subscribe(self, channel, callback=None):
        """Subscribe to a channel and listen for messages."""
        if self.subscribed:
            print("Already subscribed to a channel. Unsubscribe first.")
            return False
            
        # Start a new thread to listen for messages
        self.subscribed = True
        self.subscriber_thread = threading.Thread(
            target=self._subscriber_loop, 
            args=(channel, callback),
            daemon=True
        )
        self.subscriber_thread.start()
        return True
        
    def _subscriber_loop(self, channel, callback):
        """Background thread to listen for published messages."""
        try:
            # Create a dedicated socket for this subscription
            sub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sub_socket.connect((self.host, self.port))
            
            # Send subscribe command
            command = {
                "type": "pubsub",
                "action": "subscribe",
                "channel": channel
            }
            sub_socket.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive subscription confirmation
            data = sub_socket.recv(1024)
            response = json.loads(data.decode('utf-8'))
            print(f"Subscription response: {response}")
            
            # Listen for messages
            sub_socket.settimeout(1.0)  # Use timeout for checking running flag
            while self.subscribed and self.running:
                try:
                    data = sub_socket.recv(1024)
                    if not data:
                        break
                        
                    message = json.loads(data.decode('utf-8'))
                    print(f"Received from {channel}: {message}")
                    
                    if callback:
                        callback(message)
                except socket.timeout:
                    continue
                except json.JSONDecodeError:
                    print("Received invalid JSON data")
                except Exception as e:
                    print(f"Error in subscriber loop: {e}")
                    break
                    
        except Exception as e:
            print(f"Subscription error: {e}")
        finally:
            self.subscribed = False
            try:
                sub_socket.close()
            except:
                pass
                
    def unsubscribe(self):
        """Stop listening for messages."""
        self.subscribed = False
        if self.subscriber_thread:
            self.subscriber_thread.join(timeout=1.0)
            self.subscriber_thread = None
        return True
        
    def publish(self, channel, message):
        """Publish a message to a channel."""
        return self.send_command(
            action="publish", 
            type="pubsub", 
            channel=channel, 
            message=message
        )
        
    def list_channels(self):
        """List all active channels."""
        return self.send_command(action="list_channels", type="pubsub")
        
    def list_subscribers(self, channel):
        """List number of subscribers for a channel."""
        return self.send_command(
            action="list_subscribers", 
            type="pubsub", 
            channel=channel
        )
        
    # Database operations
    def get(self, key):
        """Get a value from the database."""
        return self.send_command("get", key)
        
    def set(self, key, value):
        """Set a value in the database."""
        return self.send_command("set", key, value)
        
    def set_with_ttl(self, key, value, ttl):
        """Set a value with TTL in the database."""
        return self.send_command("set_with_ttl", key, value, ttl)
        
    def delete(self, key):
        """Delete a key from the database."""
        return self.send_command("delete", key)
        
    def keys(self):
        """Get all keys in the database."""
        return self.send_command("keys")

def message_handler(message):
    """Default message handler for subscriptions."""
    channel = message.get("channel", "unknown")
    data = message.get("message", {})
    print(f"\nMessage from '{channel}': {data}")
    print("> ", end="", flush=True)  # Restore prompt

def main():
    client = TCPClient()
    print("In-Memory DB Client with PubSub")
    print("Commands:")
    print("  Database: get <key>, set <key> <value>, set_with_ttl <key> <value> <ttl>, delete <key>, keys")
    print("  PubSub: subscribe <channel>, unsubscribe, publish <channel> <message>, list_channels, list_subscribers <channel>")
    print("  General: exit, help")
    
    client.running = True
    
    try:
        while client.running:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    continue
                
                parts = user_input.split()
                action = parts[0].lower()
                
                # Exit command
                if action == "exit":
                    break
                    
                # Help command
                elif action == "help":
                    print("Commands:")
                    print("  Database: get <key>, set <key> <value>, set_with_ttl <key> <value> <ttl>, delete <key>, keys")
                    print("  PubSub: subscribe <channel>, unsubscribe, publish <channel> <message>, list_channels, list_subscribers <channel>")
                    print("  General: exit, help")
                
                # Database commands
                elif action == "get" and len(parts) == 2:
                    key = parts[1]
                    response = client.get(key)
                    print(response)
                    
                elif action == "set" and len(parts) >= 3:
                    key = parts[1]
                    value = " ".join(parts[2:])
                    response = client.set(key, value)
                    print(response)
                    
                elif action == "set_with_ttl" and len(parts) >= 4:
                    key = parts[1]
                    ttl = int(parts[-1])  # Last part is TTL

                    # The value is everything between the key and TTL
                    value = " ".join(parts[2:-1])

                    print(f"Setting {key} = {value} with TTL of {ttl} seconds")
                    response = client.set_with_ttl(key, value, ttl)
                    print(response)
                    
                elif action == "delete" and len(parts) == 2:
                    key = parts[1]
                    response = client.delete(key)
                    print(response)
                    
                elif action == "keys" and len(parts) == 1:
                    response = client.keys()
                    print(response)
                
                # PubSub commands
                elif action == "subscribe" and len(parts) == 2:
                    channel = parts[1]
                    if client.subscribe(channel, message_handler):
                        print(f"Subscribed to channel: {channel}")
                    else:
                        print("Failed to subscribe")
                        
                elif action == "unsubscribe" and len(parts) == 1:
                    if client.unsubscribe():
                        print("Unsubscribed successfully")
                    else:
                        print("Failed to unsubscribe")
                        
                elif action == "publish" and len(parts) >= 3:
                    channel = parts[1]
                    message = " ".join(parts[2:])
                    response = client.publish(channel, message)
                    print(response)
                    
                elif action == "list_channels" and len(parts) == 1:
                    response = client.list_channels()
                    print(response)
                    
                elif action == "list_subscribers" and len(parts) == 2:
                    channel = parts[1]
                    response = client.list_subscribers(channel)
                    print(response)
                    
                else:
                    print("Invalid command. Type 'help' for a list of commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting client.")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    finally:
        client.running = False
        client.unsubscribe()
        print("Client shutdown complete.")

if __name__ == "__main__":
    main()