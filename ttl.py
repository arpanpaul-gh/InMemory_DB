#ttl.py
import time
from config import DEFAULT_TTL

class TTL:
    def __init__(self):
        self.ttl_data = {}

    def set_ttl(self, key, ttl=DEFAULT_TTL):
        self.ttl_data[key] = time.time() + ttl

    def is_expired(self, key):
        if key in self.ttl_data:
            return time.time() > self.ttl_data[key]
        return False

    def delete_ttl(self, key):
        if key in self.ttl_data:
            del self.ttl_data[key]