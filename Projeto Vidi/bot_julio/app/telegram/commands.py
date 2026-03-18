import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.db.postgres import db
from app.telegram.middleware import check_auth_middleware
from app.agent.graph import app_graph
import uuid

logger = logging.getLogger(__name__)

async def cmd_totem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simula o scan de um QR Code físico."""
    if not await check_auth_middleware(update, context):
        await update.message.reply_text("Você precisa estar credenciado. Use /start para identificar-se com seu CPF.")
        return

    if not context.args:
        await update.message.reply_text("Uso correto: /totem <TOTEM_ID>\nExemplos: TOTEM_INTERNACIONALIZACAO, TOTEM_SUCESSAO_GOVERNANCA, TOTEM_CAPITAL_INTELIGENTE")
        return

    totem_id = context.args[0]
    valid_totems = ["TOTEM_INTERNACIONALIZACAO", "TOTEM_SUCESSAO_GOVERNANCA", "TOTEM_CAPITAL_INTELIGENTE"]
    
    if totem_id not in valid_totems:
        await update.message.reply_text(f"Totem desconhecido. Totens válidos: {', '.join(valid_totems)}")
        return

    tel_id = update.effective_user.id
    
    # Gera sessao RAG no LangGraph
    state = {
        "session_id": str(uuid.uuid4()),
        "telegram_user_id": tel_id,
        "user_input": f"Acabei de escanear o totem {totem_id}. Pode me dar um contexto rápido do que tratar aqui?",
        "totem_id": totem_id,
        "messages": []
    }
    
    result = await app_graph.ainvoke(state)
    response = result.get("final_response", "Erro interno ao processar totem.")
    
    await update.message.reply_text(response)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta o status do próprio perfil"""
    if not await check_auth_middleware(update, context):
        await update.message.reply_text("Identifique-se primeiro com /start.")
        return

    tel_id = update.effective_user.id
    row = await db.fetchrow("SELECT full_name, role, company, upsell_category FROM participants WHERE telegram_user_id = $1", tel_id)
    
    msg = (
        f"📋 *Meu Perfil - ViDi*\n\n"
        f"Nome: {row['full_name']}\n"
        f"Empresa: {row['company']}\n"
        f"Cargo: {row['role']}\n"
        f"Credencial Vip (Upsell): Categoria {row['upsell_category']}"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')
