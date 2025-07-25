const redis = require('redis');

async function connectToRedis() {
    const client = redis.createClient({
        socket: {
            host: process.env.REDIS_HOST || 'redis',
            port: process.env.REDIS_PORT || 6379,
            reconnectStrategy: (retries) => {
                console.log(`Attempting to reconnect to Redis (attempt ${retries})`);
                return Math.min(retries * 50, 500);
            }
        }
    });

    client.on('error', (err) => {
        console.error('Redis Client Error:', err);
    });

    client.on('connect', () => {
        console.log('Connected to Redis');
    });

    client.on('reconnecting', () => {
        console.log('Reconnecting to Redis...');
    });

    // Retry connection with exponential backoff
    let retries = 0;
    const maxRetries = 10;
    
    while (retries < maxRetries) {
        try {
            await client.connect();
            console.log('Successfully connected to Redis');
            return client;
        } catch (error) {
            retries++;
            console.log(`Failed to connect to Redis (attempt ${retries}/${maxRetries}):`, error.message);
            if (retries < maxRetries) {
                const delay = Math.min(1000 * Math.pow(2, retries), 10000);
                console.log(`Waiting ${delay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            } else {
                throw error;
            }
        }
    }
}

async function main() {
    const client = await connectToRedis();

    // Publish messages every 3 seconds
    let messageCount = 1;
    
    setInterval(async () => {
        const message = {
            id: messageCount,
            timestamp: new Date().toISOString(),
            content: `Hello from Node.js publisher! Message #${messageCount}`,
            sender: 'nodejs-app'
        };

        try {
            await client.lPush('message_queue', JSON.stringify(message));
            console.log(`Published message #${messageCount}:`, message.content);
            messageCount++;
        } catch (error) {
            console.error('Error publishing message:', error);
        }
    }, 3000);

    // Graceful shutdown
    process.on('SIGINT', async () => {
        console.log('\nShutting down publisher...');
        await client.quit();
        process.exit(0);
    });
}

main().catch(console.error);
