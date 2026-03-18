from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.jobs import process_pending_messages
import logging

logger = logging.getLogger(__name__)

# Configura o Scheduler
scheduler = AsyncIOScheduler()

def start_scheduler():
    """Inicia o CRON que verifica a fila no DB."""
    # Roda a cada 60 segundos conforme documento
    scheduler.add_job(process_pending_messages, "interval", seconds=60, id="process_scheduled_messages", replace_existing=True)
    scheduler.start()
    logger.info("APScheduler iniciado. Loop de 60s ativado para upsells e mensagens var.")
    
def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler desligado.")
