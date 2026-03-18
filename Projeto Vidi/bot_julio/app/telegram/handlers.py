import logging
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from app.db.postgres import db
from app.db.redis_client import redis_client
from app.auth.cpf_validator import is_valid_cpf
from app.telegram.middleware import check_auth_middleware
from app.agent.graph import app_graph
from app.auth.jwt_manager import create_access_token
from app.config import config

logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com /start e inicializa onboarding"""
    tel_id = update.effective_user.id
    if await check_auth_middleware(update, context):
        await update.message.reply_text("Você já está credenciado. Como posso ajudar com a Cúpula CEO hoje?")
        return
        
    await update.message.reply_text("Olá! Sou o Júlio, seu concierge na Cúpula CEO 2026. Para liberar seu acesso, por favor digite seu CPF (apenas números ou com pontuação).")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto: Onboarding ou LangGraph"""
    tel_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Verifica bloqueio MUTE (3 tentativas erradas de CPF)
    is_muted = await redis_client.client.get(f"mute:{tel_id}")
    if is_muted:
        await update.message.reply_text("Sua conta está bloqueada temporariamente devido a tentativas inválidas. Tente novamente em 30 minutos.")
        return

    # Se não está autenticado, assume que a mensagem é a tentativa de CPF
    if not await check_auth_middleware(update, context):
        if not is_valid_cpf(text):
            await update.message.reply_text("CPF num formato inválido. Tente novamente.")
            await _increment_attempts(tel_id)
            return
            
        # Busca no banco se CPF existe
        cpf_clean = "".join(filter(str.isdigit, text))
        
        row = await db.fetchrow("SELECT id, full_name FROM participants WHERE cpf = $1", cpf_clean)
        if not row:
            await update.message.reply_text("Não encontrei esse CPF na lista de convidados VIP da Cúpula. Procure a recepção.")
            await _increment_attempts(tel_id)
            return
            
        # Check se já tem telegram id associado diferente
        existing_tel = await db.fetchrow("SELECT telegram_user_id FROM participants WHERE cpf = $1", cpf_clean)
        if existing_tel and existing_tel["telegram_user_id"] and existing_tel["telegram_user_id"] != tel_id:
            await update.message.reply_text("Este CPF já está vinculado a outro aparelho Telegram. Procure a equipe.")
            return

        # CPF Válido e livre. Vincula
        await db.execute("UPDATE participants SET telegram_user_id = $1 WHERE cpf = $2", tel_id, cpf_clean)
        
        # Gera sessão JWT / Redis
        token = create_access_token({"sub": str(row["id"]), "tel_id": tel_id})
        await redis_client.client.set(f"auth_token:{tel_id}", token, ex=config.JWT_EXPIRE_HOURS * 3600)
        
        await update.message.reply_text(f"Credencial VIP validada, {row['full_name']}! Acesso liberado ao ambiente Júlio.")
        return

    # Se autenticado, envia a mensagem para o LangGraph
    state = {
        "session_id": str(uuid.uuid4()),
        "telegram_user_id": tel_id,
        "user_input": text,
        "totem_id": None, # Sem Totem a menos que comando /totem seja usado
        "messages": []
    }
    
    try:
        # Tenta interceptar mensagens perigosas via sanitização básica
        suspicious = ["system:", "assistant:", "<script>"]
        if any(s in text.lower() for s in suspicious):
            await update.message.reply_text("Não entendi a formatação da sua mensagem. Podemos focar na sua vivência no evento?")
            return
            
        result = await app_graph.ainvoke(state)
        response = result.get("final_response", "Erro interno ao formular resposta.")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Erro no LangGraph: {e}")
        await update.message.reply_text("Desculpe, a linha com os mentores está ruidosa agora. Pode repetir?")

async def _increment_attempts(tel_id: int):
    val = await redis_client.client.incr(f"cpf_attempts:{tel_id}")
    if val >= 3:
        await redis_client.client.set(f"mute:{tel_id}", "1", ex=1800) # 30 mins
        await redis_client.client.delete(f"cpf_attempts:{tel_id}")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pega links/imagens e documenta q nao suporta"""
    await update.message.reply_text("Desculpe, minha matriz atual atende apenas por texto. O que posso fazer por você?")
