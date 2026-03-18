import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.db.postgres import db
from app.config import config

logger = logging.getLogger(__name__)

async def check_admin(update: Update):
    """Retorna True se user é admin"""
    if update.effective_user.id == config.TELEGRAM_ADMIN_USER_ID:
        return True
    await update.message.reply_text("Acesso negado. Ação restrita a Staff/Admin ViDi.")
    return False

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista participantes no BD"""
    if not await check_admin(update): return
    
    rows = await db.fetch("SELECT full_name, cpf, upsell_category FROM participants LIMIT 50")
    if not rows:
        await update.message.reply_text("Nenhum participante cadastrado.")
        return
        
    msg = "*Participantes:* \n"
    for r in rows:
        msg += f"- {r['full_name']} (Cat {r['upsell_category']}) CPF: {r['cpf']}\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update): return
    
    args = context.args
    # Ex: /admin_add "Joao da Silva" 12345678909 556299999999 A
    if len(args) < 4:
        await update.message.reply_text("Uso: /admin_add <nome> <cpf> <telefone_wpp> <upsell_A_B_C>")
        return
        
    nome = " ".join(args[:-3])
    cpf = args[-3]
    tel = args[-2]
    up = args[-1]
    
    try:
        await db.execute("""
            INSERT INTO participants (full_name, cpf, whatsapp_primary, upsell_category)
            VALUES ($1, $2, $3, $4)
        """, nome, cpf, tel, up)
        await update.message.reply_text(f"Participante {nome} inserido.")
    except Exception as e:
        await update.message.reply_text(f"Erro ao inserir: {e}")

async def admin_fire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dispara uma mensagem agendada forçadamente."""
    if not await check_admin(update): return
    
    if not context.args:
        await update.message.reply_text("Uso: /admin_fire <message_key>")
        return
        
    msg_key = context.args[0]
    await update.message.reply_text(f"Comando simulado: O scheduler deve assumir a key {msg_key}.")
    # Em uma implementação avançada, mudaria o status do db para agora
    await db.execute("UPDATE scheduled_messages SET scheduled_at = NOW() WHERE message_key = $1", msg_key)

async def admin_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reseta o próprio usuário tirando o telegram ID dele (deslogar)"""
    tel_id = update.effective_user.id
    
    # Admin resetando os testes dele:
    if context.args:
        cpf_alvo = context.args[0]
        await db.execute("UPDATE participants SET telegram_user_id = NULL WHERE cpf = $1", cpf_alvo)
        await update.message.reply_text(f"CPF {cpf_alvo} resetado (desvinculado do telegram_id).")
    else:
        await db.execute("UPDATE participants SET telegram_user_id = NULL WHERE telegram_user_id = $1", tel_id)
        from app.db.redis_client import redis_client
        await redis_client.client.delete(f"auth_token:{tel_id}")
        await redis_client.client.delete(f"cpf_attempts:{tel_id}")
        await update.message.reply_text("Sua própria sessão foi resetada para testes de onboarding.")
