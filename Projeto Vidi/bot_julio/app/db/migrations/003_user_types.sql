-- Migration 003: Sistema de múltiplos modos de usuário
-- Adiciona user_type e has_event_access à tabela participants
-- Adiciona access_level à tabela knowledge_chunks para controle de acesso RAG

-- =============================================================
-- TABELA: participants
-- =============================================================
ALTER TABLE participants
    ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) NOT NULL DEFAULT 'participant',
    ADD COLUMN IF NOT EXISTS has_event_access BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE participants
    ADD CONSTRAINT chk_user_type
    CHECK (user_type IN ('lead', 'participant', 'mentored', 'staff'));

COMMENT ON COLUMN participants.user_type IS
    'Modo de atendimento do usuário: lead (prospect), participant (evento), mentored (mentorado), staff (equipe interna)';

COMMENT ON COLUMN participants.has_event_access IS
    'Indica se o usuário tem acesso ao conteúdo do evento (relevante para mentorados que não participam da Cúpula)';

-- Atualiza registros existentes para garantir consistência
UPDATE participants SET user_type = 'participant' WHERE user_type IS NULL OR user_type = '';

-- =============================================================
-- TABELA: knowledge_chunks
-- =============================================================
ALTER TABLE knowledge_chunks
    ADD COLUMN IF NOT EXISTS access_level VARCHAR(20) NOT NULL DEFAULT 'participant';

ALTER TABLE knowledge_chunks
    ADD CONSTRAINT chk_access_level
    CHECK (access_level IN ('public', 'participant', 'mentored', 'internal'));

COMMENT ON COLUMN knowledge_chunks.access_level IS
    'Nível de acesso ao chunk: public (todos), participant (participantes+), mentored (mentorados+), internal (staff)';

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_access_level ON knowledge_chunks(access_level);

-- Chunks de apresentação pública e marketing → public
-- Chunks de agenda/sessões/totems → participant (default, já está certo)
-- Chunks de frameworks de mentoria → mentored
-- Chunks de procedimentos internos/escalação → internal
