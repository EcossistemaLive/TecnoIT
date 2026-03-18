import redis.asyncio as redis
import logging
from app.config import config

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.client = None

    async def connect(self):
        if not self.client:
            try:
                self.client = redis.from_url(config.REDIS_URL, decode_responses=True)
                await self.client.ping()
                logger.info("Conectado ao Redis.")
            except Exception as e:
                logger.error(f"Erro ao conectar ao Redis: {e}")
                raise

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("Desconectado do Redis.")

redis_client = RedisCache()
