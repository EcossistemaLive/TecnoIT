import logging
from app.db.postgres import db
from app.db.redis_client import redis_client
from app.auth.jwt_manager import verify_token, create_access_token

logger = logging.getLogger(__name__)


async def get_participant_by_phone(phone: str):
    """Busca participante pelo número WhatsApp vinculado."""
    row = await db.fetchrow(
        "SELECT id, full_name, company, role, upsell_category "
        "FROM participants WHERE whatsapp_phone = $1",
        phone,
    )
    if row:
        return dict(row)
    return None


async def check_auth_middleware(phone: str) -> bool:
    """Valida se o usuário tem sessão ativa (JWT no Redis)."""
    token = await redis_client.client.get(f"session:{phone}")
    if token and verify_token(token):
        return True

    # Sem sessão válida: tenta reconectar pelo vínculo já existente
    participant = await get_participant_by_phone(phone)
    if participant:
        new_token = create_access_token({"sub": str(participant["id"]), "phone": phone})
        await redis_client.client.set(f"session:{phone}", new_token, ex=86400)
        return True

    return False
