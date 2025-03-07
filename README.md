# InMemory_DB
In-Memory Database This project is a simple in-memory database inspired by Redis, with functionalities such as key-value storage, TTL (Time-To-Live) for keys, LRU (Least Recently Used) caching, and persistence to a JSON file. It is built using Python and consists of modular components that work together to provide a lightweight database system.

# Features
1. Key-Value Storage:
Store and retrieve key-value pairs in memory.
Supports basic operations: set, get, and delete.

2. TTL (Time-To-Live):
Set an expiration time for keys.
Automatically removes expired keys from memory and persistent storage.

3. LRU Cache:
Implements a Least Recently Used (LRU) cache with a configurable capacity.
Evicts the least recently used item when the cache is full.

4. Persistence:
Saves the in-memory database to a JSON file (db.json).
Loads data from the file when the server starts.

5. TCP Server:
A simple TCP server listens for incoming connections and processes commands.
Supports multiple clients connecting simultaneously.

6. Client Interface:
A command-line client allows users to interact with the database.
Supports commands like set, get, set_with_ttl, and delete.

# Project Structure

db.py: Core in-memory database implementation with key-value storage and TTL support.  
cache.py: LRU cache implementation for efficient key-value storage.  
network.py: TCP server that handles client connections and processes commands.  
storage.py: Persistence layer that saves and loads data to/from a JSON file.  
ttl.py: TTL management for expiring keys.  
client.py: Command-line client to interact with the database.  
config.py: Configuration file for server host, port, cache capacity, and storage file.  
