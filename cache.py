#cache.py
from collections import OrderedDict
from config import CACHE_CAPACITY

class LRUCache:
    def __init__(self, capacity=CACHE_CAPACITY):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)