#db.py
import time

class InMemoryDB:
    def __init__(self):
        self.data = {}
        self.ttl_data = {}
        self.observers = []  # For observer pattern to notify of changes
        
    def add_observer(self, observer):
        """Add an observer that will be notified of data changes."""
        if observer not in self.observers:
            self.observers.append(observer)
            
    def remove_observer(self, observer):
        """Remove an observer."""
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observers(self, operation, key, value=None):
        """Notify all observers of a change."""
        for observer in self.observers:
            observer(operation, key, value)

    def get(self, key):
        """Get a value from the database."""
        current_time = time.time()
        if key in self.ttl_data:
            if self.ttl_data[key] < current_time:
                # Key has expired
                print(f"Key '{key}' has expired and is being removed")
                del self.data[key]
                del self.ttl_data[key]
                self.notify_observers("expire", key)
                return None
            else:
                # Show remaining TTL if the key has one
                remaining = int(self.ttl_data[key] - current_time)
                print(f"Key '{key}' TTL: {remaining} seconds remaining")
        return self.data.get(key, None)
    
    def set(self, key, value, ttl=None):
        """Set a value in the database."""
        self.data[key] = value
        if ttl is not None:
            expiry_time = time.time() + ttl
            self.ttl_data[key] = expiry_time
            expiry_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry_time))
            print(f"Set TTL for key '{key}': expires at {expiry_datetime} ({ttl} seconds)")
        else:
            self.ttl_data.pop(key, None)
        self.notify_observers("set", key, value)
        return True     

    def delete(self, key):
        """Delete a key from the database."""
        if key in self.data:
            del self.data[key]
            self.ttl_data.pop(key, None)
            self.notify_observers("delete", key)
            return True
        return False

    def keys(self):
        """Get all keys in the database."""
        # First, cleanup expired keys
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in list(self.ttl_data.items())
            if expiry_time < current_time
        ]
        
        for key in expired_keys:
            del self.data[key]
            del self.ttl_data[key]
            self.notify_observers("expire", key)
            
        return list(self.data.keys())
        
    def clear(self):
        """Clear all data from the database."""
        keys = list(self.data.keys())
        self.data.clear()
        self.ttl_data.clear()
        for key in keys:
            self.notify_observers("delete", key)
        return True