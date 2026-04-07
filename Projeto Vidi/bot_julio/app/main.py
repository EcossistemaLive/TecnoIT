import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Response

from app.config import config
from app.db.postgres import db
from app.db.redis_client import redis_client
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.whatsapp_handlers.handlers import handle_whatsapp_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Conecta bancos e inicia scheduler na subida; desconecta na descida."""
    await db.connect()
    await redis_client.connect()
    start_scheduler()
    logger.info("Bot Julio v4 iniciado (Meta Cloud API)")
    yield
    stop_scheduler()
    await db.disconnect()
    await redis_client.disconnect()
    logger.info("Bot Julio v4 encerrado")


app = FastAPI(title="Bot Julio v4", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Health check — Cloud Run exige resposta 200 na porta 8080
# ---------------------------------------------------------------------------

@app.get("/")
async def health():
    return {"status": "ok", "version": "4.0"}


# ---------------------------------------------------------------------------
# Webhook Meta — GET: verificação inicial no painel Meta for Developers
# ---------------------------------------------------------------------------

@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(default=None, alias="hub.mode"),
    hub_token: str = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str = Query(default=None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook Meta verificado com sucesso")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning(f"Webhook verify falhou — token recebido: {hub_token}")
    raise HTTPException(status_code=403, detail="Token inválido")


# ---------------------------------------------------------------------------
# Webhook Meta — POST: mensagens recebidas dos usuários
# ---------------------------------------------------------------------------

@app.post("/webhook/whatsapp")
async def receive_message(payload: dict, background_tasks: BackgroundTasks):
    """
    Meta envia POST para cada evento (mensagem, status de entrega, etc.).
    Responde imediatamente com 200 e processa em background para não exceder
    o timeout de 20s da Meta.
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            # Notificação de status (entregue, lido) — ignorar silenciosamente
            return {"status": "ok"}

        msg = messages[0]
        phone = msg.get("from")
        msg_type = msg.get("type")

        # Ignorar mídias (áudio, imagem, documento)
        if msg_type != "text":
            logger.debug(f"Mídia ignorada de {phone}: tipo={msg_type}")
            return {"status": "ok"}

        text = msg.get("text", {}).get("body", "").strip()

        if not phone or not text:
            return {"status": "ok"}

        background_tasks.add_task(handle_whatsapp_message, phone, text)
        return {"status": "accepted"}

    except Exception as e:
        logger.error(f"Erro ao parsear payload Meta: {e}")
        return {"status": "ok"}  # Sempre 200 para a Meta não reenviar
