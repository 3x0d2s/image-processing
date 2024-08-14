import redis.asyncio as redis
from app.config import config


class RedisPubSubClient:
    pool: redis.ConnectionPool
    stream_name: str

    def __init__(self, redis_dsn: str, stream_name: str):
        self.pool = redis.ConnectionPool.from_url(redis_dsn)
        self.stream_name = stream_name

    async def add_to_stream(self, data: dict):
        client = redis.Redis(connection_pool=self.pool)
        await client.xadd(self.stream_name, data)
        await client.aclose()

    async def close_connection(self):
        await self.pool.aclose()


redis_client = RedisPubSubClient(redis_dsn=str(config.REDIS_DSN),
                                 stream_name=config.REDIS_STREAM_NAME
                                 )
