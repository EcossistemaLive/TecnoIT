import logging
from app.db.postgres import db

logger = logging.getLogger(__name__)


async def dispatch_scheduled_message(
    message_id: str, participant_id: str, phone: str, template: str, full_name: str
):
    """Envia mensagem proativa via WhatsApp e registra log."""
    from app.whatsapp_handlers.sender import send_whatsapp_message

    text = template.replace("{participant.name}", full_name).replace("{name}", full_name)

    try:
        await send_whatsapp_message(phone, text)

        await db.execute(
            """
            INSERT INTO message_dispatch_log
                (scheduled_message_id, participant_id, whatsapp_phone, status, sent_at)
            VALUES ($1, $2, $3, 'sent', NOW())
            """,
            message_id,
            participant_id,
            phone,
        )
        logger.info(f"Mensagem proativa enviada para {full_name} ({phone})")

    except Exception as e:
        logger.error(f"Falha ao enviar mensagem para {full_name}: {e}")
        await db.execute(
            """
            INSERT INTO message_dispatch_log
                (scheduled_message_id, participant_id, whatsapp_phone, status, failure_reason)
            VALUES ($1, $2, $3, 'failed', $4)
            """,
            message_id,
            participant_id,
            phone,
            str(e),
        )


async def process_pending_messages():
    """Busca no DB as mensagens prontas para envio e as dispara."""
    logger.debug("Verificando mensagens agendadas pendentes...")

    query = """
    SELECT m.id, m.template, m.target_upsell_categories
    FROM scheduled_messages m
    WHERE m.is_active = TRUE
    AND (
        (m.scheduled_type = 'fixed'    AND m.scheduled_at    <= NOW())
        OR
        (m.scheduled_type = 'variable' AND m.admin_release_at <= NOW())
    )
    """
    pending_msgs = await db.fetch(query)

    if not pending_msgs:
        return

    for msg in pending_msgs:
        target_cats = msg["target_upsell_categories"]

        p_query = """
            SELECT p.id, p.whatsapp_phone, p.full_name
            FROM participants p
            LEFT JOIN message_dispatch_log l
                ON l.participant_id = p.id AND l.scheduled_message_id = $1
            WHERE p.upsell_category = ANY($2)
            AND p.whatsapp_phone IS NOT NULL
            AND l.id IS NULL
        """
        participants = await db.fetch(p_query, msg["id"], target_cats)

        for p in participants:
            await dispatch_scheduled_message(
                msg["id"], p["id"], p["whatsapp_phone"], msg["template"], p["full_name"]
            )
