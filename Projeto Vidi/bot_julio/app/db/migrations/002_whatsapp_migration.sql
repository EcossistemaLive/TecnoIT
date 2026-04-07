-- Migration 002: Adaptar schema para WhatsApp (Meta Cloud API)
-- Remove dependências do Telegram; adiciona chat_history e whatsapp_phone

-- ==========================================
-- participants: adicionar coluna whatsapp_phone
-- (número vinculado após validação CPF via WhatsApp)
-- ==========================================
ALTER TABLE participants
    ADD COLUMN IF NOT EXISTS whatsapp_phone VARCHAR(20) NULL;

CREATE INDEX IF NOT EXISTS idx_participants_whatsapp_phone
    ON participants(whatsapp_phone);

-- ==========================================
-- message_dispatch_log: adicionar whatsapp_phone
-- ==========================================
ALTER TABLE message_dispatch_log
    ADD COLUMN IF NOT EXISTS whatsapp_phone VARCHAR(20) NULL;

-- ==========================================
-- TABELA: chat_history
-- Substitui MongoDB para histórico de conversas
-- ==========================================
CREATE TABLE IF NOT EXISTS chat_history (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id  VARCHAR(36) NOT NULL,
    participant_id UUID      NULL REFERENCES participants(id) ON DELETE SET NULL,
    user_phone  VARCHAR(20) NOT NULL,
    user_input  TEXT        NOT NULL,
    bot_response TEXT       NULL,
    totem_id    VARCHAR(100) NULL,
    intent      VARCHAR(50) NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_history_phone
    ON chat_history(user_phone, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_history_session
    ON chat_history(session_id);
