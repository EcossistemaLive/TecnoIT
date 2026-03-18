import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import config

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        if not self.client:
            try:
                self.client = AsyncIOMotorClient(config.MONGODB_URI)
                db_name = config.MONGODB_URI.split('/')[-1].split('?')[0]
                if not db_name:
                    db_name = 'botjulio_test'
                self.db = self.client[db_name]
                
                # Criar indíces (TTL 24h e session_id)
                await self.db.chat_sessions.create_index("session_id")
                await self.db.chat_sessions.create_index("updated_at", expireAfterSeconds=86400)
                
                logger.info(f"Conectado ao MongoDB. Banco: {db_name}")
            except Exception as e:
                logger.error(f"Erro ao conectar ao MongoDB: {e}")
                raise

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("Desconectado do MongoDB.")

mongo_db = MongoDB()
