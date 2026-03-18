import asyncpg
import logging
from app.config import config

logger = logging.getLogger(__name__)

class PostgresDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            try:
                # asyncpg usa 'postgresql://' no DSN
                dsn = config.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
                self.pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=25)
                logger.info("Conectado ao PostgreSQL (AsyncPG pool).")
            except Exception as e:
                logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
                raise

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Desconectado do PostgreSQL.")

    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

db = PostgresDB()
