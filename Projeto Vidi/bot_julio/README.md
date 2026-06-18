# Bot Júlio V4.0 — ViDi / Cúpula CEO 2026

Assistente inteligente via WhatsApp para os executivos da ViDi (Ibrahim Boufleur e Luiz Portal).
Atua como Concierge de Elite + Co-Produtor da Experiência da Cúpula CEO 2026.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Orquestração do Agente | LangGraph |
| LLM Premium (Cat. A) | Anthropic Claude Sonnet 4 |
| LLM Principal (Cat. B/C) | Google Gemini 2.0 Flash |
| RAG / Embeddings | pgvector (PostgreSQL) + Gemini Embeddings |
| Banco de Dados | PostgreSQL 16 (asyncpg) |
| Cache / Rate Limit | Redis 7 |
| Webhook WhatsApp | Meta Cloud API v19 + FastAPI |
| Jobs Proativos | APScheduler |
| **Painel Admin** | **FastAPI + Vanilla HTML/CSS/JS (Glassmorphism)** |

---

## 🚀 Admin Dashboard

Um painel administrativo premium integrado para gestão de participantes e agendamentos.

- **Acesso:** `http://localhost:8080/dashboard`
- **Funcionalidades:**
    - Visão geral de métricas (Participantes, Mensagens Pendentes).
    - Gestão completa de base de dados de participantes.
    - Monitoramento de mensagens agendadas e automações.
    - Pesquisa dinâmica e interface otimizada para Desktop.

## Sistema de Modos de Usuário

O bot possui 4 modos de atendimento, selecionados automaticamente pelo `user_type` cadastrado no banco:

| Modo | user_type | Objetivo | Acesso RAG |
|---|---|---|---|
| Lead | `lead` | Gerar interesse, validar dor, direcionar ao próximo passo | `public` |
| Participante | `participant` | Maximizar experiência no evento, guiar por sessões/totems, identificar upsell | `public` + `participant` |
| Mentorado | `mentored` | Suporte à implementação, accountability, aprofundamento ViDi | `public` + `mentored` (+ `participant` se `has_event_access=true`) |
| Staff | `staff` | Suporte operacional rápido, acesso total | todos os níveis |

### Níveis de Acesso RAG (knowledge_chunks.access_level)

| Nível | Conteúdo |
|---|---|
| `public` | Apresentação ViDi, bio dos mentores, visão geral do evento |
| `participant` | Agenda completa, sessões, totems, conteúdo do evento |
| `mentored` | Frameworks de mentoria, ferramentas de implementação, metodologia ViDi |
| `internal` | Procedimentos operacionais, escalações, fluxos internos (staff only) |

---

## Instalação Local

### Pré-requisitos
- Python 3.11+
- Docker Desktop (para PostgreSQL + Redis)

### Passos

```bash
# 1. Subir infraestrutura local
docker-compose up -d

# 2. Criar ambiente virtual e instalar dependências
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com as credenciais

# 4. Aplicar migrations (em ordem)
psql $DATABASE_URL -f app/db/migrations/001_initial.sql
psql $DATABASE_URL -f app/db/migrations/002_whatsapp_migration.sql
psql $DATABASE_URL -f app/db/migrations/003_user_types.sql

# 5. Popular base de dados
python scripts/seed_participants.py
python scripts/seed_knowledge.py

# 6. Iniciar o servidor
uvicorn app.main:app --reload --port 8080
```

---

## Deploy (Produção — Google Cloud Run)

```bash
# Build e push da imagem
docker build -t gcr.io/julio-bot-ecd02/bot-julio:latest .
docker push gcr.io/julio-bot-ecd02/bot-julio:latest

# Deploy no Cloud Run
gcloud run deploy bot-julio \
  --image gcr.io/julio-bot-ecd02/bot-julio:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

**Após o deploy:** aplicar a migration `003_user_types.sql` no banco de produção.

---

## Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (Claude) |
| `GOOGLE_API_KEY` | Chave da API Google (Gemini) |
| `DATABASE_URL` | URL do PostgreSQL (asyncpg) |
| `REDIS_URL` | URL do Redis |
| `WHATSAPP_TOKEN` | Token de acesso Meta Cloud API |
| `WHATSAPP_PHONE_NUMBER_ID` | ID do número WhatsApp Business |
| `WHATSAPP_VERIFY_TOKEN` | Token de verificação do webhook |
| `ADMIN_WHATSAPP` | Número do admin para alertas (ex: 5562999999999) |
| `JWT_SECRET` | Segredo JWT (mínimo 64 chars) |

---

## Estrutura do Projeto

```
bot_julio/
├── app/
│   ├── api/                # Endpoints administrativos e integração
│   │   └── admin.py        # API do Dashboard
│   ├── agent/
│   │   ├── graph.py        # Grafo LangGraph (fluxo do agente)
│   │   ├── nodes.py        # Nós do grafo (validate, classify, llm, etc.)
│   │   ├── prompts.py      # 4 system prompts por modo + builder dinâmico
│   │   └── state.py        # TypedDict do estado do agente
│   ├── db/
│   │   └── migrations/
│   │       ├── 001_initial.sql           # Schema base
│   │       ├── 002_whatsapp_migration.sql # Adaptação WhatsApp
│   │       └── 003_user_types.sql         # Modos de usuário + controle RAG
│   ├── rag/
│   │   ├── indexer.py      # Indexação de documentos (com access_level)
│   │   └── retriever.py    # Busca vetorial filtrada por user_type
│   ├── whatsapp_handlers/  # Webhook e envio de mensagens
│   ├── scheduler/          # Jobs proativos (APScheduler)
│   ├── config.py           # Configurações via .env
│   └── main.py             # FastAPI app
├── scripts/
│   ├── seed_participants.py
│   ├── seed_knowledge.py
│   └── test_scenarios.py
├── static/                 # Arquivos estáticos do Dashboard
│   └── admin/              # Interface do Painel
├── Dockerfile
├── docker-compose.yml      # Infraestrutura local (PG + Redis)
└── requirements.txt
```

---

## Migrations

| Arquivo | Descrição |
|---|---|
| `001_initial.sql` | Schema base: participants, diagnoses, knowledge_chunks, totem_interactions |
| `002_whatsapp_migration.sql` | chat_history, whatsapp_phone em participants |
| `003_user_types.sql` | user_type + has_event_access em participants; access_level em knowledge_chunks |
