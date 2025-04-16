#storage.py
import json
from config import STORAGE_FILE

class Storage:
    def __init__(self, filename=STORAGE_FILE):
        self.filename = filename

    def save(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                if not content.strip():
                    return {} 
                return json.loads(content)
        except FileNotFoundError:
            return {} 
        except json.JSONDecodeError:
            return {} 