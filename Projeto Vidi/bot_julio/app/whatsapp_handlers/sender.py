import logging
import httpx
from app.config import config

logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com/v19.0"


async def send_whatsapp_message(to: str, text: str) -> bool:
    """Envia mensagem de texto via Meta Cloud API."""
    url = f"{GRAPH_URL}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Meta API erro {resp.status_code}: {resp.text}")
                return False
            return True
    except Exception as e:
        logger.error(f"Falha ao enviar mensagem WhatsApp: {e}")
        return False
