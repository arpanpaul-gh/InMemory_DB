#pubsub.py
import threading
import json
import socket
from collections import defaultdict

class PubSub:
    def __init__(self):
        self.channels = defaultdict(set)  # Dictionary to store channels and their subscribers
        self.lock = threading.Lock()

    def subscribe(self, channel, client):
        """Subscribe a client to a channel."""
        with self.lock:
            self.channels[channel].add(client)
            return True

    def unsubscribe(self, channel, client):
        """Unsubscribe a client from a channel."""
        with self.lock:
            if channel in self.channels and client in self.channels[channel]:
                self.channels[channel].remove(client)
                if not self.channels[channel]:
                    del self.channels[channel]
                return True
            return False

    def publish(self, channel, message):
        """Publish a message to all clients subscribed to a channel."""
        clients_to_remove = []
        with self.lock:
            if channel in self.channels:
                for client in self.channels[channel]:
                    try:
                        client.sendall(json.dumps({"channel": channel, "message": message}).encode('utf-8'))
                    except Exception as e:
                        print(f"Error sending message to client: {e}")
                        clients_to_remove.append((channel, client))
                
                # Clean up disconnected clients
                for ch, client in clients_to_remove:
                    if ch in self.channels and client in self.channels[ch]:
                        self.channels[ch].remove(client)
                        if not self.channels[ch]:
                            del self.channels[ch]
                return True
            return False

    def broadcast(self, message):
        """Broadcast a message to all channels and clients."""
        with self.lock:
            for channel in list(self.channels.keys()):
                self.publish(channel, message)
            return True

    def list_subscribers(self, channel):
        """Return the count of subscribers for a given channel."""
        with self.lock:
            if channel in self.channels:
                return len(self.channels[channel])
            return 0

    def list_channels(self):
        """Return a list of all active channels."""
        with self.lock:
            return list(self.channels.keys())

    def handle_command(self, command, client):
        """Handle PubSub commands."""
        action = command.get("action")
        channel = command.get("channel")
        message = command.get("message")
        
        if action == "subscribe" and channel:
            success = self.subscribe(channel, client)
            return {"result": "OK" if success else "ERROR", "action": "subscribe", "channel": channel}
        
        elif action == "unsubscribe" and channel:
            success = self.unsubscribe(channel, client)
            return {"result": "OK" if success else "ERROR", "action": "unsubscribe", "channel": channel}
        
        elif action == "publish" and channel and message is not None:
            success = self.publish(channel, message)
            return {"result": "OK" if success else "ERROR", "action": "publish", "channel": channel}
        
        elif action == "broadcast" and message is not None:
            success = self.broadcast(message)
            return {"result": "OK" if success else "ERROR", "action": "broadcast"}
        
        elif action == "list_channels":
            channels = self.list_channels()
            return {"result": "OK", "action": "list_channels", "channels": channels}
        
        elif action == "list_subscribers" and channel:
            count = self.list_subscribers(channel)
            return {"result": "OK", "action": "list_subscribers", "channel": channel, "count": count}
        
        else:
            return {"error": "Invalid PubSub command"}