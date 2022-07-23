import os
import redis
from rq import Worker, Queue, Connection

# List of queues for workers to listen on
listen = ["default"]

# Looks for env var, but will default to localhost:6379
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis connection
conn = redis.from_url(redis_url)

# USED FOR TESTING
if __name__ == "__main__":
    # Creates worker, connects to the Redis server, and listens to 'default' queue
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
