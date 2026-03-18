from datetime import datetime
from app.db.postgres import db
import logging
from telegram import Bot
from app.config import config

logger = logging.getLogger(__name__)
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

async def dispatch_scheduled_message(message_id: str, participant_id: str, telegram_id: int, template: str, full_name: str):
    """Envia a mensagem proativa pelo telegram e registra log."""
    text = template.replace("{participant.name}", full_name).replace("{name}", full_name)
    
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
        
        # Log success
        await db.execute("""
            INSERT INTO message_dispatch_log (scheduled_message_id, participant_id, telegram_user_id, status, sent_at)
            VALUES ($1, $2, $3, 'sent', NOW())
        """, message_id, participant_id, telegram_id)
        logger.info(f"Mensagem proativa enviada para {full_name}")
        
    except Exception as e:
        logger.error(f"Falha ao enviar mensagem para {full_name}: {e}")
        await db.execute("""
            INSERT INTO message_dispatch_log (scheduled_message_id, participant_id, telegram_user_id, status, failure_reason)
            VALUES ($1, $2, $3, 'failed', $4)
        """, message_id, participant_id, telegram_id, str(e))


async def process_pending_messages():
    """Busca no DB as mensagens prontas para envio e as dispara."""
    logger.debug("Verificando mensagens agendadas pendentes...")
    
    query = """
    SELECT m.id, m.template, m.target_upsell_categories 
    FROM scheduled_messages m
    WHERE m.is_active = TRUE 
    AND (
        (m.scheduled_type = 'fixed' AND m.scheduled_at <= NOW()) OR
        (m.scheduled_type = 'variable' AND m.admin_release_at <= NOW())
    )
    """
    
    pending_msgs = await db.fetch(query)
    
    if not pending_msgs:
        return
        
    for msg in pending_msgs:
        # Puxa participantes que devem receber e que tem telegram_id, e NUNCA receberam esta msg
        target_cats = msg["target_upsell_categories"]
        
        p_query = """
            SELECT p.id, p.telegram_user_id, p.full_name 
            FROM participants p
            LEFT JOIN message_dispatch_log l 
                ON l.participant_id = p.id AND l.scheduled_message_id = $1
            WHERE p.upsell_category = ANY($2) 
            AND p.telegram_user_id IS NOT NULL
            AND l.id IS NULL
        """
        
        participants_to_receive = await db.fetch(p_query, msg["id"], target_cats)
        
        for p in participants_to_receive:
            await dispatch_scheduled_message(msg["id"], p["id"], p["telegram_user_id"], msg["template"], p["full_name"])
