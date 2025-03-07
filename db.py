
import time

class InMemoryDB:
    def __init__(self):
        self.data = {}
        self.ttl_data = {}

    def get(self, key):
        if key in self.ttl_data and self.ttl_data[key] < time.time():
            del self.data[key]
            del self.ttl_data[key]
            return None
        return self.data.get(key, None)

    def set(self, key, value, ttl=None):
        self.data[key] = value
        if ttl is not None:
            self.ttl_data[key] = time.time() + ttl
        else:
            self.ttl_data.pop(key, None)
        return True

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self.ttl_data.pop(key, None)
            return True
        return False

    def keys(self):
        return list(self.data.keys())