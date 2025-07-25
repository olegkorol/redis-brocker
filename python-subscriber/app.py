import redis
import json
import time
import os
import signal
import sys
from datetime import datetime

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

def main():
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Connect to Redis with retry logic
    redis_client = connect_to_redis()
    
    print("Connected to Redis, waiting for messages...")
    
    # Subscribe to messages
    while True:
        try:
            # Use brpop to block and wait for messages (blocking right pop)
            result = redis_client.brpop('message_queue', timeout=1)
            
            if result:
                queue_name, message_data = result
                message = json.loads(message_data)
                
                print(f"Received message #{message['id']} from queue {queue_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
                print(f"  Timestamp: {message['timestamp']}")
                print(f"  Sender: {message['sender']}")
                print(f"  Content: {message['content']}")
                print("-" * 50)
                
                # Simulate some processing time
                time.sleep(0.5)
                
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            time.sleep(1)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
