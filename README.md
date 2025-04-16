# In-Memory Database with PubSub

A lightweight, multi-featured in-memory database with built-in publish/subscribe functionality, implemented in Python.

## Features

- **In-Memory Key-Value Store**: Fast read and write operations
- **Time-To-Live (TTL)**: Automatically expire keys after a specific duration
- **LRU Cache**: Least Recently Used cache implementation for performance
- **Persistence**: Data automatically saved to disk to prevent data loss
- **Publish/Subscribe**: Real-time messaging system between clients
- **TCP Network Protocol**: Client-server architecture over TCP sockets
- **Multi-threading**: Handles multiple client connections concurrently

## Architecture

The system consists of two main components:

1. **Server**: Hosts the in-memory database and handles client connections
2. **Client**: Provides a command-line interface to interact with the server

### Server Components

- `main-server.py`: Entry point that initializes the server
- `network.py`: TCP socket server implementation
- `db.py`: In-memory database implementation
- `cache.py`: LRU cache implementation
- `storage.py`: Persistence functionality
- `pubsub.py`: Publish/Subscribe system
- `ttl.py`: Time-To-Live functionality
- `config.py`: Configuration settings

### Client Components

- `client.py`: TCP client with command-line interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/in-memory-db.git
   cd in-memory-db
   ```

2. No external dependencies are required (uses Python standard library)

## Usage

### Starting the Server

Run the server using:

```
python main-server.py
```

The server will start listening on the configured host and port (default: 127.0.0.1:65432).

### Using the Client

Run the client using:

```
python client.py
```

This will connect to the server and provide an interactive command prompt.

### Available Commands

#### Database Operations

- `get <key>`: Retrieve value for a key
- `set <key> <value>`: Store a key-value pair
- `set_with_ttl <key> <value> <ttl>`: Store a key-value pair with expiration time in seconds
- `delete <key>`: Remove a key-value pair
- `keys`: List all keys in the database

#### PubSub Operations

- `subscribe <channel>`: Subscribe to receive messages from a channel
- `unsubscribe`: Stop listening for messages
- `publish <channel> <message>`: Send a message to all subscribers of a channel
- `list_channels`: Show all active channels
- `list_subscribers <channel>`: Show subscriber count for a channel

#### General Commands

- `help`: Display available commands
- `exit`: Close the client

## Configuration

You can modify the settings in `config.py`:

- `SERVER_HOST`: Server hostname (default: '127.0.0.1')
- `SERVER_PORT`: Server port number (default: 65432)
- `CACHE_CAPACITY`: Maximum number of items in the LRU cache (default: 100)
- `STORAGE_FILE`: File for data persistence (default: 'persistence.json')
- `DEFAULT_TTL`: Default time-to-live in seconds (default: 3600)

## Example Usage

```
> subscribe notifications
Subscribed to channel: notifications

> publish notifications "Hello World"
{'result': 'OK'}

Message from 'notifications': Hello World

> set username john_doe
{'result': 'OK'}

> get username
{'result': 'john_doe', 'ttl_remaining': None}

> set_with_ttl temp_token abc123 60
Setting temp_token = abc123 with TTL of 60 seconds
{'result': 'OK', 'ttl_set': 60}

> keys
{'result': ['username', 'temp_token']}
```

## Data Persistence

The database automatically saves data to disk at regular intervals (default: every 60 seconds) and on graceful shutdown. The data is stored in `persistence.json`.

## Auto-Expiry with TTL

Keys with TTL are automatically removed when they expire. The server periodically checks for expired keys and removes them.

## PubSub System

The PubSub system allows clients to:

1. Subscribe to channels
2. Publish messages to channels
3. Receive real-time notifications

The system also publishes database changes to the `db_updates` channel.

## Shutting Down

- Server: Press Ctrl+C for graceful shutdown
- Client: Type `exit` or press Ctrl+C

## Future Enhancements
- Implement concurrency with the help of asyncio.
- Add support for more data types (e.g., lists, sets, hashes).
- Add authentication and security features.
- Improve performance with asynchronous I/O.
- Implement replication and clustering for high availability.
