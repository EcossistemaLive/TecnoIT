import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.db.postgres import db
from app.db.redis_client import redis_client
from app.auth.jwt_manager import verify_token
from app.config import config

logger = logging.getLogger(__name__)

async def get_participant_by_telegram_id(telegram_id: int):
    """Busca participante atrelado ao telegram_id"""
    query = "SELECT id, full_name, role, upsell_category FROM participants WHERE telegram_user_id = $1"
    return await db.fetchrow(query, telegram_id)

async def check_auth_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Valida se o usuário tem token/sessão ativa. Caso não tenha, barra as requisições normais."""
    if not update.effective_user:
        return False
        
    tel_id = update.effective_user.id
    
    # Verifica cache Redis
    token = await redis_client.client.get(f"auth_token:{tel_id}")
    if token:
        # Token existe no cache, vamos validar
        decoded = verify_token(token)
        if decoded:
            return True # Válido e autenticado
            
    # Se não tem cache, valida diretamente no POSTGRES
    participant = await get_participant_by_telegram_id(tel_id)
    if participant:
        # Renova a sessão de cara já que o cara acessou
        # Na vida real gerariamos um JWT e poríamos no redis. Vamos ignorar JWT se o vinculo ja existir no banco Telegram -> Participant
        from app.auth.jwt_manager import create_access_token
        new_token = create_access_token({"sub": str(participant["id"]), "tel_id": tel_id})
        await redis_client.client.set(f"auth_token:{tel_id}", new_token, ex=config.JWT_EXPIRE_HOURS * 3600)
        return True

    return False
