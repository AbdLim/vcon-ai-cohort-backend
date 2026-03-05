import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
    
    async def close(self):
        await self.redis.aclose()

redis_client = RedisClient()
