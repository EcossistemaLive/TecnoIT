import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ============================================
    # GOOGLE GEMINI (Versão de Testes — Telegram)
    # ============================================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

    # ============================================
    # ANTHROPIC (Produção — WhatsApp) — não usado no teste
    # ============================================
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")  # produção

    # Parâmetros de geração (compartilhados)
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "800"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    _admin_raw = os.getenv("TELEGRAM_ADMIN_USER_ID", "0")
    TELEGRAM_ADMIN_USER_ID = int(_admin_raw) if _admin_raw and _admin_raw.strip().lstrip('-').isdigit() else 0

    # Bancos de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:senha@localhost:5432/botjulio_test")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/botjulio_test")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

    # Auth
    JWT_SECRET = os.getenv("JWT_SECRET", "julio_vidi_cupula_ceo_2026_secret_super_seguro_64chars_minimo")
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # RAG
    RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.6"))
    MAX_RAG_CHUNKS = int(os.getenv("MAX_RAG_CHUNKS", "5"))

    # Alertas
    UPSELL_ALERT_TELEGRAM_CHAT_ID = os.getenv("UPSELL_ALERT_TELEGRAM_CHAT_ID")

    # Ambiente
    ENVIRONMENT = os.getenv("ENVIRONMENT", "test")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @property
    def is_test_mode(self):
        return self.ENVIRONMENT == "test"

config = Config()
