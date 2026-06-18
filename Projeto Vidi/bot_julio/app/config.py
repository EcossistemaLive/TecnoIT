import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ============================================
    # LLM — Google Gemini (primário, Cat. B e C)
    # ============================================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

    # ============================================
    # LLM — Anthropic Claude (upsell Cat. A)
    # ============================================
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

    # Parâmetros compartilhados de geração
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "600"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # ============================================
    # WhatsApp — Evolution API
    # ============================================
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://evolution:8080")
    EVOLUTION_GLOBAL_API_KEY = os.getenv("EVOLUTION_GLOBAL_API_KEY")

    # WhatsApp — Meta Cloud API (Fallback/Antigo)
    # ============================================
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "julio_vidi_webhook_2026")
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v19.0")

    # Número admin para alertas de upsell (formato: 5562999999999)
    ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP")

    # ============================================
    # Banco de Dados — Supabase (PostgreSQL + pgvector)
    # ============================================
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:senha@localhost:5432/botjulio_test")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

    # ============================================
    # Segurança (Auth e LGPD)
    # ============================================
    JWT_SECRET = os.getenv("JWT_SECRET", "julio_vidi_cupula_ceo_2026_secret_super_seguro_64chars_minimo")
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    CPF_ENCRYPTION_KEY = os.getenv("CPF_ENCRYPTION_KEY")  # Chave base64 de 32 bytes (Fernet)

    # ============================================
    # RAG
    # ============================================
    RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.75"))
    MAX_RAG_CHUNKS = int(os.getenv("MAX_RAG_CHUNKS", "5"))

    # ============================================
    # Observabilidade — Langfuse
    # ============================================
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    # ============================================
    # Ambiente
    # ============================================
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @property
    def is_production(self):
        return self.ENVIRONMENT == "production"

config = Config()
