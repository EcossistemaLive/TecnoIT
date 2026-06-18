import logging
import uuid

from app.db.postgres import db
from app.db.redis_client import redis_client
from app.auth.cpf_validator import is_valid_cpf
from app.auth.jwt_manager import create_access_token
from app.whatsapp_handlers.middleware import check_auth_middleware
from app.whatsapp_handlers.sender import send_whatsapp_message
from app.agent.orchestrator import orchestrator
from app.utils.crypto import cpf_encryptor

logger = logging.getLogger(__name__)

VALID_TOTEMS = [
    "TOTEM_INTERNACIONALIZACAO",
    "TOTEM_SUCESSAO_GOVERNANCA",
    "TOTEM_CAPITAL_INTELIGENTE",
]

# ---------------------------------------------------------------------------
# Rate limiting (Redis — chave = phone)
# ---------------------------------------------------------------------------

RATE_LIMIT_KEY = "rate_limit:{phone}"
MUTE_KEY = "mute:{phone}"
RATE_WINDOW = 1800  # 30 min em segundos
MAX_ATTEMPTS = 3


async def _is_muted(phone: str) -> bool:
    val = await redis_client.client.get(MUTE_KEY.format(phone=phone))
    return val is not None


async def _increment_attempts(phone: str):
    key = RATE_LIMIT_KEY.format(phone=phone)
    attempts = await redis_client.client.incr(key)
    if attempts == 1:
        await redis_client.client.expire(key, RATE_WINDOW)
    if attempts >= MAX_ATTEMPTS:
        await redis_client.client.set(
            MUTE_KEY.format(phone=phone), "1", ex=RATE_WINDOW
        )
        await redis_client.client.delete(key)


async def _clear_rate_limit(phone: str):
    await redis_client.client.delete(RATE_LIMIT_KEY.format(phone=phone))
    await redis_client.client.delete(MUTE_KEY.format(phone=phone))


# ---------------------------------------------------------------------------
# Handler principal
# ---------------------------------------------------------------------------

async def handle_whatsapp_message(phone: str, text: str):
    """
    Ponto central de processamento de mensagens recebidas via WhatsApp.

    Fluxo:
      1. Verifica rate limit / mute
      2. Se não autenticado → trata como tentativa de CPF
      3. Se autenticado → verifica totem ou chat livre → LangGraph
    """
    text = text.strip()

    # 1. Rate limit
    if await _is_muted(phone):
        await send_whatsapp_message(
            phone,
            "Sua conta está bloqueada temporariamente devido a tentativas inválidas. "
            "Tente novamente em 30 minutos.",
        )
        return

    # 2. Onboarding (CPF)
    if not await check_auth_middleware(phone):
        await _handle_cpf_attempt(phone, text)
        return

    # 3. Comando de totem (QR code envia o ID do totem como texto)
    if text.upper() in VALID_TOTEMS:
        await _handle_totem(phone, text.upper())
        return

    # 4. Comando de status
    if text.lower() in ("status", "/status"):
        await _handle_status(phone)
        return

    # 5. Chat livre via LangGraph
    await _handle_chat(phone, text)


# ---------------------------------------------------------------------------
# Sub-handlers
# ---------------------------------------------------------------------------

async def _handle_cpf_attempt(phone: str, text: str):
    """Valida CPF e vincula ao número WhatsApp."""
    if not is_valid_cpf(text):
        await send_whatsapp_message(
            phone,
            "Olá! Sou o Júlio, seu concierge na Cúpula CEO 2026.\n"
            "Para liberar seu acesso, envie seu CPF (apenas números ou com pontuação).",
        )
        await _increment_attempts(phone)
        return

    cpf_clean = "".join(filter(str.isdigit, text))
    encrypted_cpf = cpf_encryptor.encrypt(cpf_clean)

    # Busca tanto o criptografado quanto o plano (para casos legados ou de desenvolvimento)
    row = await db.fetchrow(
        "SELECT id, full_name, company, role, upsell_category, whatsapp_phone "
        "FROM participants WHERE cpf = $1 OR cpf = $2",
        encrypted_cpf, cpf_clean
    )

    if not row:
        await send_whatsapp_message(
            phone,
            "Não encontrei esse CPF na lista de convidados VIP da Cúpula. "
            "Procure a recepção.",
        )
        await _increment_attempts(phone)
        return

    existing_phone = row["whatsapp_phone"]
    if existing_phone and existing_phone != phone:
        await send_whatsapp_message(
            phone,
            "Este CPF já está vinculado a outro número WhatsApp. "
            "Procure a equipe.",
        )
        return

    # Vincula o número ao participante
    await db.execute(
        "UPDATE participants SET whatsapp_phone = $1 WHERE id = $2",
        phone,
        row["id"],
    )

    # Limpa rate limit
    await _clear_rate_limit(phone)

    # Gera sessão JWT no Redis (TTL = 24h)
    token = create_access_token({"sub": str(row["id"]), "phone": phone})
    await redis_client.client.set(f"session:{phone}", token, ex=86400)

    await send_whatsapp_message(
        phone,
        f"Credencial VIP validada, {row['full_name']}! "
        "Acesso liberado ao ambiente Júlio.\n\n"
        "Pode me enviar sua dúvida ou escanear um dos totens do evento.",
    )


async def _handle_totem(phone: str, totem_id: str):
    """Processa contexto de totem escaneado via QR Code."""
    state = {
        "session_id": str(uuid.uuid4()),
        "user_id": phone,
        "user_input": (
            f"Acabei de escanear o totem {totem_id}. "
            "Pode me dar um contexto rápido do que tratar aqui?"
        ),
        "totem_id": totem_id,
        "messages": [],
    }
    result = await orchestrator.ainvoke(state)
    response = result.get("final_response", "Erro interno ao processar totem.")
    await send_whatsapp_message(phone, response)


async def _handle_status(phone: str):
    """Exibe o perfil do participante."""
    row = await db.fetchrow(
        "SELECT full_name, company, role, upsell_category "
        "FROM participants WHERE whatsapp_phone = $1",
        phone,
    )
    if row:
        msg = (
            f"Meu Perfil - ViDi\n\n"
            f"Nome: {row['full_name'] or 'N/A'}\n"
            f"Empresa: {row['company'] or 'N/A'}\n"
            f"Cargo: {row['role'] or 'N/A'}\n"
            f"Credencial VIP: Categoria {row['upsell_category'] or 'N/A'}"
        )
    else:
        msg = "Perfil não encontrado."
    await send_whatsapp_message(phone, msg)


async def _handle_chat(phone: str, text: str):
    """Envia mensagem para o workflow LangGraph."""
    suspicious = ["system:", "assistant:", "<script>"]
    if any(s in text.lower() for s in suspicious):
        await send_whatsapp_message(
            phone,
            "Não entendi a formatação da sua mensagem. "
            "Podemos focar na sua vivência no evento?",
        )
        return

    state = {
        "session_id": str(uuid.uuid4()),
        "user_id": phone,
        "user_input": text,
        "totem_id": None,
        "messages": [],
    }

    try:
        result = await orchestrator.ainvoke(state)
        response = result.get("final_response", "Erro interno ao formular resposta.")
        await send_whatsapp_message(phone, response)
    except Exception as e:
        logger.error(f"Erro no LangGraph: {e}")
        await send_whatsapp_message(
            phone,
            "Desculpe, a linha com os mentores está ruidosa agora. Pode repetir?",
        )
