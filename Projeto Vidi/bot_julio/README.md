# Bot Júlio V3.0 - ViDi (Telegram Test Version)

Esta é a versão de testes do agente Júlio, adaptada para Telegram com base nas especificações arquitetônicas da Cúpula CEO 2026.

## Pré-Requisitos
1. Python 3.11+
2. PostgreSQL 15+ (com pgvector)
3. MongoDB 6+
4. Redis 7+

## Instalação e Execução
1. Crie um ambiente virtual: `python -m venv venv` e ative-o (ex: `.\venv\Scripts\activate` no Windows).
2. Instale as dependências: `pip install -r requirements.txt`.
3. Copie o `.env.example` para `.env` e preencha as credenciais.
4. Rode a migração inicial do banco: conecte-se ao Postgres e execute `app/db/migrations/001_initial.sql`.
5. Execute os seeds na ordem:
   ```bash
   python scripts/seed_participants.py
   python scripts/seed_knowledge.py
   ```
6. Inicialize a aplicação: `python app/main.py`.

## Stack e Arquitetura
- **Orquestração e Agente:** LangGraph + LangChain.
- **LLM e RAG:** Anthropic Claude (Sonnet 3.5/4) + OpenAI Embeddings (3-small) + Postgres PGVector.
- **Autenticação:** JWT após validação de CPF atrelado ao `telegram_user_id`.
- **Jobs Proativos:** APScheduler avaliando filas no Postgres.
- **Estados Persistentes:** MongoDB (histórico), Redis (cache/rate limiting).
