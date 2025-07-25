import redis
import json
import time
import os
import signal
import sys
from datetime import datetime
import uuid

def signal_handler(sig, frame):
    print('\nShutting down subscriber...')
    sys.exit(0)

def connect_to_redis():
    """Connect to Redis with retry logic"""
    max_retries = 10
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test the connection
            redis_client.ping()
            print(f"Successfully connected to Redis on attempt {attempt + 1}")
            return redis_client
            
        except redis.RedisError as e:
            print(f"Failed to connect to Redis (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 10)  # Exponential backoff
            else:
                raise

def setup_consumer_group(redis_client):
    """Setup consumer group for Redis Streams"""
    try:
        # Create consumer group if it doesn't exist
        redis_client.xgroup_create('message_stream', 'processors', id='0', mkstream=True)
        print('Created consumer group "processors"')
    except redis.RedisError as e:
        if 'BUSYGROUP' in str(e):
            print('Consumer group "processors" already exists')
        else:
            raise

def main():
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Connect to Redis with retry logic
    redis_client = connect_to_redis()
    
    # Setup consumer group
    setup_consumer_group(redis_client)
    
    # Generate unique consumer name
    consumer_name = f"consumer-{uuid.uuid4().hex[:8]}"
    print(f"Starting consumer: {consumer_name}")
    print("Connected to Redis Streams, waiting for messages...")
    
    # Subscribe to messages using Redis Streams
    while True:
        try:
            # XREADGROUP reads messages from stream with acknowledgment support
            # '>' means read only new messages for this consumer group
            messages = redis_client.xreadgroup(
                'processors',                    # consumer group name
                consumer_name,                   # consumer name
                {'message_stream': '>'},         # stream and position
                count=1,                         # read 1 message at a time
                block=1000                       # block for 1 second if no messages
            )
            
            if messages:
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        print(f"🔄 Processing message {message_id} from {stream_name}:")
                        print(f"  ID: {fields.get('id')}")
                        print(f"  Content: {fields.get('content')}")
                        print(f"  Timestamp: {fields.get('timestamp')}")
                        print(f"  Sender: {fields.get('sender')}")
                        print(f"  Received at: {datetime.now()}")
                        
                        # Simulate processing work
                        time.sleep(0.5)
                        
                        # IMPORTANT: Acknowledge the message after successful processing
                        try:
                            redis_client.xack('message_stream', 'processors', message_id)
                            print(f"✅ Acknowledged message {message_id}")
                        except redis.RedisError as e:
                            print(f"❌ Failed to acknowledge message {message_id}: {e}")
                        
                        print("-" * 60)
                        
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
