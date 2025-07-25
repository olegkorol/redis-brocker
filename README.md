# Redis Queue as Message Broker (RQMB)

This project demonstrates a message-broker setup using Redis with a Node.js publisher and Python subscriber running in Docker containers.

## Architecture

- **Redis**: Message broker using Redis lists as queues
- **Node.js Publisher**: Sends messages to the Redis queue every 3 seconds
- **Python Subscriber**: Consumes messages from the Redis queue

## Project Structure

```text
rqmb-docker/
├── docker-compose.yml
├── nodejs-publisher/
│   ├── app.js
│   ├── package.json
│   └── Dockerfile
├── python-subscriber/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## Quick Start

1. **Build and run all services:**

   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**

   ```bash
   docker-compose up --build -d
   ```

3. **View logs:**

   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f nodejs-publisher
   docker-compose logs -f python-subscriber
   ```

4. **Stop the services:**

   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes:**

   ```bash
   docker-compose down -v
   ```

## How it Works

1. **Node.js Publisher** (`nodejs-publisher`):
   - Connects to Redis
   - Publishes a new message every 3 seconds
   - Uses `LPUSH` to add messages to the `message_queue` list

2. **Python Subscriber** (`python-subscriber`):
   - Connects to Redis
   - Uses `BRPOP` (blocking right pop) to consume messages
   - Processes messages and displays them with timestamps

3. **Redis**:
   - Acts as the message broker
   - Uses Redis lists to implement a FIFO queue
   - Persists data using AOF (Append Only File)

## Message Format

Messages are JSON objects with the following structure:

```json
{
  "id": 1,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "content": "Hello from Node.js publisher! Message #1",
  "sender": "nodejs-app"
}
```

## Docker Services

- **redis**: Redis 8 Alpine with persistence enabled
- **nodejs-publisher**: Node.js 22 Alpine with Redis client
- **python-subscriber**: Python 3.11 Slim with Redis client

All services are connected through a custom bridge network for secure communication.

## Development

To modify the applications:

1. Make changes to the source code
2. Rebuild the specific service:

   ```bash
   docker-compose build nodejs-publisher
   # or
   docker-compose build python-subscriber
   ```

3. Restart the services:

   ```bash
   docker-compose up
   ```
