-- Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- TABELA: participants
-- ==========================================
CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_user_id BIGINT UNIQUE NULL, -- Para a versão Telegram (vinculado após validar CPF)
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    whatsapp_primary VARCHAR(20) NOT NULL,
    whatsapp_alt VARCHAR(20) NULL,
    company VARCHAR(255) NULL,
    role VARCHAR(100) NULL,
    annual_revenue_bracket VARCHAR(50) NULL,
    upsell_category VARCHAR(20) NOT NULL, -- A, B, ou C
    event_status VARCHAR(20) NOT NULL DEFAULT 'pre_event',
    registered_by VARCHAR(100) NOT NULL DEFAULT 'system',
    registered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    locked BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_participants_cpf ON participants(cpf);
CREATE INDEX IF NOT EXISTS idx_participants_telegram_id ON participants(telegram_user_id);

-- ==========================================
-- TABELA: diagnoses
-- ==========================================
CREATE TABLE IF NOT EXISTS diagnoses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID REFERENCES participants(id) ON DELETE CASCADE,
    pain_label VARCHAR(100) NOT NULL,
    pain_description TEXT NOT NULL,
    governance_score NUMERIC(5,2) NULL,
    succession_urgency NUMERIC(5,2) NULL,
    financial_stress NUMERIC(5,2) NULL,
    work_hours_per_day NUMERIC(4,2) NULL,
    raw_responses JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diagnoses_participant_id ON diagnoses(participant_id);

-- ==========================================
-- TABELA: knowledge_chunks (RAG)
-- ==========================================
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding VECTOR(768), -- Google text-embedding-004 = 768d | OpenAI 3-small = 1536d (trocar se mudar provider)
    source_document VARCHAR(255) NOT NULL,
    theme VARCHAR(100) NOT NULL,
    totem_tag VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índice IVFFlat para busca vetorial rápida
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_totem_tag ON knowledge_chunks(totem_tag);

-- ==========================================
-- TABELA: totem_interactions
-- ==========================================
CREATE TABLE IF NOT EXISTS totem_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    participant_id UUID REFERENCES participants(id) ON DELETE CASCADE,
    totem_id VARCHAR(50) NOT NULL,
    scanned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    insight_generated TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_totem_interactions_participant_tmp ON totem_interactions(participant_id, scanned_at DESC);

-- ==========================================
-- TABELA: scheduled_messages
-- ==========================================
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_key VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NULL,
    template TEXT NOT NULL,
    scheduled_type VARCHAR(20) NOT NULL, -- fixed, relative, variable
    scheduled_at TIMESTAMP NULL,
    relative_to VARCHAR(50) NULL,
    relative_offset_hours INTEGER NULL,
    target_upsell_categories VARCHAR(10)[] NOT NULL,
    target_event_status VARCHAR(20)[] NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    admin_release_at TIMESTAMP NULL,
    allow_admin_override BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100) NULL,
    last_modified_at TIMESTAMP NULL
);

-- ==========================================
-- TABELA: message_dispatch_log
-- ==========================================
CREATE TABLE IF NOT EXISTS message_dispatch_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheduled_message_id UUID REFERENCES scheduled_messages(id),
    participant_id UUID REFERENCES participants(id),
    telegram_user_id BIGINT NULL,
    status VARCHAR(20) NOT NULL, -- pending, sent, failed, skipped
    sent_at TIMESTAMP NULL,
    evolution_message_id VARCHAR(100) NULL, -- mantido o nome por padrao
    failure_reason TEXT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_dispatch ON message_dispatch_log(scheduled_message_id, participant_id);

-- ==========================================
-- TABELA: admin_audit_log
-- ==========================================
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id BIGINT NOT NULL, -- telegram_user_id do admin
    action VARCHAR(255) NOT NULL,
    target_participant_id UUID NULL,
    details JSONB NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE totem_interactions ENABLE ROW LEVEL SECURITY;

-- Nota: Como o app gerencia a identidade via Telegram e backend
-- A política RLS num context de API normalmente é gerida pela role
-- Para simplificar testes, RLS será emulado na camada de repositório FastAPI.
