# Redis as Message Broker

This project demonstrates **two different approaches** for a message-broker setup using Redis with a Node.js publisher and a Python subscriber running in Docker containers.

## 🏗️ Architecture Overview

This project includes **two implementations** showcasing different Redis messaging patterns:

### **Approach 1: Redis Lists (Simple Queue)**

- **Data Structure**: Redis Lists (`LPUSH`/`BRPOP`)
- **Behavior**: Simple FIFO queue - fire-and-forget
- **Message Lifecycle**: Messages are **permanently removed** when consumed
- **Acknowledgment**: ❌ None - if consumer crashes, message is **lost forever**
- **Use Case**: Fast, lightweight messaging where occasional message loss is acceptable

### **Approach 2: Redis Streams (Reliable Queue)**

- **Data Structure**: Redis Streams (`XADD`/`XREADGROUP`)
- **Behavior**: Advanced message queue with consumer groups and acknowledgment
- **Message Lifecycle**: Messages **persist** until explicitly acknowledged with `XACK`
- **Acknowledgment**: ✅ Required - messages remain in stream until acknowledged
- **Use Case**: Enterprise-grade messaging where reliability and message delivery guarantees are crucial

## 📁 Project Structure

```text
redis-queue-test/
├── docker-compose-lists.yml           # Redis Lists approach
├── docker-compose-streams.yml         # Redis Streams approach  
├── nodejs-publisher/                  # Simple publisher (Lists)
│   ├── app.js
│   ├── package.json
│   └── Dockerfile
├── python-subscriber/                 # Simple subscriber (Lists)
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── nodejs-publisher-streams/          # Advanced publisher (Streams)
│   ├── app.js
│   ├── package.json
│   └── Dockerfile
├── python-subscriber-streams/         # Advanced subscriber (Streams)
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## 🚀 Quick Start

### **Option 1: Redis Lists (Simple Queue)**

```bash
# Build and run Redis Lists version
docker-compose -f docker-compose-lists.yml up --build

# Run in detached mode
docker-compose -f docker-compose-lists.yml up --build -d

# View logs
docker-compose -f docker-compose-lists.yml logs -f

# View specific service logs
docker-compose -f docker-compose-lists.yml logs -f nodejs-publisher
docker-compose -f docker-compose-lists.yml logs -f python-subscriber

# Stop services
docker-compose -f docker-compose-lists.yml down
```

### **Option 2: Redis Streams (Reliable Queue)**

```bash
# Build and run Redis Streams version
docker-compose -f docker-compose-streams.yml up --build

# Run in detached mode
docker-compose -f docker-compose-streams.yml up --build -d

# View logs
docker-compose -f docker-compose-streams.yml logs -f

# View specific service logs
docker-compose -f docker-compose-streams.yml logs -f nodejs-publisher-streams
docker-compose -f docker-compose-streams.yml logs -f python-subscriber-streams

# Stop services
docker-compose -f docker-compose-streams.yml down
```

## 🔄 How Each Approach Works

### **Redis Lists Approach:**

1. **Node.js Publisher**: Uses `LPUSH` to add messages to `message_queue` list
2. **Python Subscriber**: Uses `BRPOP` to consume messages (blocking pop)
3. **Message Flow**: `Publisher → Redis List → Consumer` (message deleted on consumption)

### **Redis Streams Approach:**

1. **Node.js Publisher**: Uses `XADD` to add messages to `message_stream`
2. **Python Subscriber**: Uses `XREADGROUP` to consume messages from consumer group
3. **Message Flow**: `Publisher → Redis Stream → Consumer Group → XACK` (message persists until acknowledged)

## 📊 Feature Comparison

| Feature | Redis Lists | Redis Streams |
|---------|-------------|---------------|
| **Message Persistence** | Deleted on consumption | Persists until ACK |
| **Consumer Groups** | ❌ No | ✅ Yes |
| **Message Acknowledgment** | ❌ No | ✅ Yes (`XACK`) |
| **Failure Recovery** | ❌ Messages lost | ✅ Unacked messages reprocessed |
| **Message IDs** | ❌ No built-in | ✅ Auto-generated |
| **Message Replay** | ❌ No | ✅ Yes |
| **Performance** | Faster (simpler) | Slightly slower (more features) |

### 🎯 When to Use Which Approach

**Choose Redis Lists when:**

- ✅ High throughput is priority
- ✅ Simple use case
- ✅ Occasional message loss is acceptable
- ✅ Low latency required

**Choose Redis Streams when:**

- ✅ Message delivery guarantees required
- ✅ Need consumer groups for load balancing
- ✅ Message replay capability needed
- ✅ Enterprise/production environment
- ✅ Failure recovery is important

## 📨 Message Format

**Redis Lists** (JSON string):

```json
{
  "id": 1,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "content": "Hello from Node.js publisher! Message #1",
  "sender": "nodejs-app"
}
```

**Redis Streams** (key-value fields):

```text
id: "1"
timestamp: "2024-01-01T12:00:00.000Z"
content: "Hello from Node.js publisher! Message #1"
sender: "nodejs-app"
```

## 🐳 Docker Services

### **Lists Version:**

- **redis**: Redis 8 Alpine (exposed port 6380 – internal port 6379)
- **nodejs-publisher**: Node.js 22 Alpine
- **python-subscriber**: Python 3.11 Alpine

### **Streams Version:**

- **redis**: Redis 8 Alpine (exposed port 6380 – internal port 6379)
- **nodejs-publisher-streams**: Node.js 22 Alpine
- **python-subscriber-streams**: Python 3.11 Alpine

## 🛠️ Development

### **For Lists version:**

```bash
# Make changes, then rebuild
docker-compose -f docker-compose-lists.yml build nodejs-publisher
docker-compose -f docker-compose-lists.yml build python-subscriber
docker-compose -f docker-compose-lists.yml up
```

### **For Streams version:**

```bash
# Make changes, then rebuild
docker-compose -f docker-compose-streams.yml build nodejs-publisher-streams
docker-compose -f docker-compose-streams.yml build python-subscriber-streams
docker-compose -f docker-compose-streams.yml up
```
