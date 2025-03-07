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

# How It Works
Server:  
The server listens for incoming client connections on a specified host and port.  
It processes commands (set, get, set_with_ttl, delete) and updates the in-memory database.  
Expired keys are automatically removed from memory and the persistent storage file.  

Client:  
The client connects to the server and sends commands.  
Users can interact with the database using a simple command-line interface.  

Persistence:  
The database state is saved to a JSON file (persistence.json) whenever a change is made.  
On server startup, the database is loaded from the file.  

# Start the Server
Run the server using the following command:  
python network.py  
The server will start listening on 127.0.0.1:65432.  

#  Start the Client
Run the client using the following command:  
python client.py  

# Future Enhancements
Add support for more data types (e.g., lists, sets, hashes).  
Implement replication and clustering for high availability.  
Implement pub-sub architecture.  
Add authentication and security features.  
Improve performance with asynchronous I/O.  

# Contributing
Contributions are welcome! If you'd like to contribute, please:  

Fork the repository.  
Create a new branch for your feature or bugfix.  
Submit a pull request.  
