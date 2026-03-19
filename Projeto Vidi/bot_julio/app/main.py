import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import config
from app.db.postgres import db
from app.db.mongo import mongo_db
from app.db.redis_client import redis_client
from app.scheduler.scheduler import start_scheduler, stop_scheduler

from app.telegram_bot_handlers.commands import cmd_totem, cmd_status
from app.admin.commands import admin_list, admin_add, admin_fire, admin_reset
from app.telegram_bot_handlers.handlers import handle_start, handle_text_message, handle_media

# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_databases():
    await db.connect()
    await mongo_db.connect()
    await redis_client.connect()

async def close_databases():
    await db.disconnect()
    await mongo_db.disconnect()
    await redis_client.disconnect()

def main():
    """Start the bot."""
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN was not set in .env")
        return

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Comandos Globais
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("totem", cmd_totem))
    application.add_handler(CommandHandler("status", cmd_status))
    
    # Comandos Admin
    application.add_handler(CommandHandler("admin_list", admin_list))
    application.add_handler(CommandHandler("admin_add", admin_add))
    application.add_handler(CommandHandler("admin_fire", admin_fire))
    application.add_handler(CommandHandler("reset", admin_reset))

    # Textos e Mídia
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.ATTACHMENT | filters.PHOTO | filters.Document.ALL | filters.VOICE, handle_media))

    # Inicia o loop para os DBs antes de rodar o polling
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_databases())
    
    # Async init: startup hook
    async def post_init(app):
        start_scheduler()
        logger.info("Bot Julio v3 iniciado com sucesso (Polling ativo)...")

    application.post_init = post_init
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        stop_scheduler()
        loop.run_until_complete(close_databases())

if __name__ == "__main__":
    main()
