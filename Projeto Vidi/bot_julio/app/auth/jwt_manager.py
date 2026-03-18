import jwt
from datetime import datetime, timedelta
from app.config import config
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict) -> str:
    """Cria um token JWT com expiração de 24 horas por padrão."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict | None:
    """Decodifica e verifica a validade de um token JWT."""
    try:
        decoded_data = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return decoded_data
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado.")
        return None
    except jwt.PyJWTError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None
