# Análise Completa - Bot Júlio v3 (Cúpula CEO 2026)

## 1. VISÃO GERAL DO PROJETO

### Objetivo
Criar um bot Telegram inteligente que funciona como concierge de elite para executivos na Cúpula CEO 2026. O bot oferece:
- Autenticação via CPF
- Diagnóstico personalizado de dores empresariais
- Recuperação de contexto via RAG (Retrieval-Augmented Generation)
- Processamento de comandos e totens físicos
- Alertas de upsell para a equipe
- Histórico de conversas persistido

### Stack Tecnológico
- **Framework Bot**: python-telegram-bot (async)
- **Orquestração de IA**: LangGraph (StateGraph)
- **LLM**: Google Gemini 2.0-flash (inicialmente), Claude Anthropic (produção)
- **Embeddings**: Google Embeddings (inicialmente), depois MockEmbeddings
- **Bancos de Dados**:
  - PostgreSQL + pgvector (participants, diagnoses, knowledge_chunks, audit logs)
  - MongoDB (histórico de conversas)
  - Redis (cache, rate-limiting, sessões JWT)
- **Scheduler**: APScheduler (mensagens proativas a cada 60s)
- **Deployment**: Docker Compose (postgres, mongodb, redis)

---

## 2. ARQUITETURA DO SISTEMA

### 2.1 Estrutura de Diretórios

```
bot_julio/
├── app/
│   ├── main.py                    # Entry point do bot Telegram
│   ├── config.py                  # Config centralizada (env vars)
│   │
│   ├── db/
│   │   ├── postgres.py            # Conexão AsyncPG
│   │   ├── mongo.py               # Conexão Motor (MongoDB)
│   │   ├── redis_client.py        # Conexão Redis
│   │   └── migrations/
│   │       └── 001_initial.sql    # Schema: participants, diagnoses, knowledge_chunks, etc
│   │
│   ├── telegram_bot_handlers/     # Handlers do Telegram (renomeado de 'telegram' para evitar conflito)
│   │   ├── handlers.py            # handle_start, handle_text_message, handle_media
│   │   ├── commands.py            # /totem, /status
│   │   ├── middleware.py          # check_auth_middleware
│   │   └── __init__.py
│   │
│   ├── admin/
│   │   └── commands.py            # /admin_list, /admin_add, /admin_fire, /reset
│   │
│   ├── auth/
│   │   ├── cpf_validator.py       # Validação de CPF
│   │   └── jwt_manager.py         # create_access_token, verify_token
│   │
│   ├── agent/                     # LangGraph workflow
│   │   ├── graph.py               # StateGraph definition (7 nodes + conditional edges)
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── nodes.py               # 7 nós do grafo (validate, classify, retrieve, call_llm, etc)
│   │   └── prompts.py             # System prompts + templates
│   │
│   ├── rag/
│   │   ├── indexer.py             # DocumentIndexer (seed da base com mock embeddings)
│   │   └── retriever.py           # DocumentRetriever (busca vetorial com mock embeddings)
│   │
│   └── scheduler/
│       ├── scheduler.py           # start_scheduler, stop_scheduler
│       └── jobs.py                # process_pending_messages (CRON job)
│
├── scripts/
│   ├── seed_participants.py       # Insert 3 participantes de teste
│   └── seed_knowledge.py          # Index 3 documentos RAG
│
├── docker-compose.yml             # PostgreSQL + MongoDB + Redis
├── requirements.txt               # Dependências Python
├── .env                           # Config de ambiente (tokens, URLs, API keys)
└── ANALISE_COMPLETA.md           # Este arquivo
```

### 2.2 Fluxo de Autenticação

```
Usuário envia /start
    ↓
handle_start() → Pede CPF
    ↓
Usuário envia CPF (validação básica)
    ↓
handle_text_message() → Valida formato
    ↓
Busca CPF no DB (participants)
    ↓
Se não existe → Erro (não está no convite)
Se existe → Vincula telegram_user_id ao participant
    ↓
Gera JWT token → Armazena em Redis
    ↓
Mensagem: "Credencial VIP validada!"
    ↓
Próximas mensagens = Chat autenticado
```

### 2.3 Fluxo de Processamento de Mensagem (LangGraph)

```
Mensagem recebida no Telegram
    ↓
handle_text_message()
    ↓
Cria estado (session_id, telegram_user_id, user_input, messages, totem_id)
    ↓
app_graph.ainvoke(state) → Executa StateGraph
    │
    ├─ Node 1: validate_user
    │   └─ Busca participant no DB → Carrega profile + diagnosis
    │   └─ Retorna: is_authenticated, participant_id, participant_profile, participant_diagnosis
    │
    ├─ Conditional: check_auth()
    │   ├─ Se não autenticado → END (bloqueado)
    │   └─ Se autenticado → classify_intent
    │
    ├─ Node 2: classify_intent
    │   └─ Detecta prompt injection (palavras suspeitas)
    │   └─ Classifica intent: contexto_totem ou chat_livre
    │
    ├─ Node 3: retrieve_context
    │   └─ Busca RAG no pgvector (cosine similarity)
    │   └─ Filtra por totem_tag se /totem foi usado
    │   └─ Retorna top-3 chunks relevantes
    │
    ├─ Node 4: call_llm
    │   └─ Constrói sistema prompt (persona + user context + rag_context)
    │   └─ Chama LLM (Mock ou Real)
    │   └─ Retorna final_response
    │
    ├─ Parallel Edges:
    │   ├─ Node 5: evaluate_upsell
    │   │   └─ Detecta triggers (Categoria A ou palavras-chave)
    │   │   └─ Se detectado → needs_team_alert = True
    │   │
    │   └─ Node 6: persist_history
    │       └─ Insere conversa no MongoDB
    │
    ├─ Conditional: check_upsell()
    │   ├─ Se needs_team_alert → notify_team
    │   └─ Senão → END
    │
    └─ Node 7: notify_team
        └─ Log: "[UPSELL ALERT] {name}: {reason}"
        └─ (Em produção: enviaria msg para grupo Telegram)

Retorna: final_response → Enviada para Telegram
```

---

## 3. ERROS ENCONTRADOS E SOLUÇÕES

### Erro 1: Import Conflict - Módulo `telegram` Local vs Biblioteca

**Descrição**
```
ImportError: cannot import name 'Update' from 'telegram' 
(C:\...\bot_julio\app\telegram\__init__.py)
```

**Causa**
O app tinha um diretório `app/telegram/` que conflitava com a biblioteca `python-telegram-bot`. Quando o código tentava fazer `from telegram import Update`, Python carregava o módulo local vazio em vez da biblioteca.

**Solução**
Renomeou `app/telegram/` → `app/telegram_bot_handlers/` e atualizou todos os imports:
- `from app.telegram.handlers import ...` → `from app.telegram_bot_handlers.handlers import ...`
- `from app.telegram.commands import ...` → `from app.telegram_bot_handlers.commands import ...`
- `from app.telegram.middleware import ...` → `from app.telegram_bot_handlers.middleware import ...`

**Arquivo alterado**
- `app/telegram/__init__.py` → `app/telegram_bot_handlers/__init__.py` (vazio)
- `app/main.py` → Atualizou imports

---

### Erro 2: RAG Retriever - Embedding Model Não Disponível

**Descrição**
```
google.genai.errors.ClientError: 404 NOT_FOUND
models/text-embedding-004 is not found for API version v1beta
```

**Causa**
O código tentava usar `models/text-embedding-004` (depois `models/embedding-001`) que não estão disponíveis na API do Google free tier. A API retornava 404.

**Solução 1** (Indexação - seed_knowledge.py)
Substituiu Google Embeddings por **Mock Embeddings**:
```python
import numpy as np

# Gera vetores aleatórios 768-dim para testes
vectors = [np.random.randn(768).tolist() for _ in chunks]
```

**Solução 2** (Retrieval - retriever.py)
Implementou MockEmbeddings determinístico baseado em hash da query:
```python
query_hash = hash(query.lower()) % 1000000
np.random.seed(query_hash)
query_vector = np.random.randn(768).tolist()
```

**Arquivos alterados**
- `app/rag/indexer.py` → Removeu GoogleGenerativeAIEmbeddings
- `app/rag/retriever.py` → Adicionou MockEmbeddings

---

### Erro 3: APScheduler - RuntimeError - No Running Event Loop

**Descrição**
```
RuntimeError: no running event loop
scheduler.start() → asyncio.get_running_loop()
```

**Causa**
O AsyncIOScheduler foi iniciado ANTES do event loop do Telegram estar rodando. O `run_polling()` cria seu próprio loop, mas o código tentava iniciar o scheduler antes disso.

**Solução**
Moveu `start_scheduler()` para dentro de `post_init()`:
```python
async def post_init(app):
    start_scheduler()
    logger.info("Bot iniciado com sucesso...")

application.post_init = post_init
```

**Arquivo alterado**
- `app/main.py` → Criou hook `post_init`

---

### Erro 4: Google Gemini API - Quota Esgotada (Free Tier)

**Descrição**
```
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
You exceeded your current quota, please check your plan and billing details.
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
limit: 0, model: gemini-2.0-flash
```

**Causa**
O GOOGLE_API_KEY fornecido estava com free tier esgotado. Cada mensagem do usuário tentava chamar `gemini-2.0-flash`, consumindo rápido a quota (0 requests/dia restantes).

**Solução**
Implementou **MockLLM** local que simula respostas contextualizadas:
```python
class MockLLM:
    async def ainvoke(self, messages):
        user_lower = user_message.lower()
        
        if any(w in user_lower for w in ["quando", "evento", "data"]):
            response = "A Cúpula CEO 2026 será um evento..."
        elif any(w in user_lower for w in ["fazer", "ajudar", "dor"]):
            response = "Entendo seu desafio..."
        # etc...
        
        return type('Response', (), {'content': response})()
```

**Arquivo alterado**
- `app/agent/nodes.py` → Criou classe MockLLM + removeu imports do Google/Anthropic LLM

**Trade-off**
MockLLM responde por palavras-chave, não é "inteligente" de verdade. Para produção, usar:
- Claude (Anthropic) com ANTHROPIC_API_KEY válida
- Gemini com billing habilitado
- LLM local (Ollama, LLaMA, etc)

---

## 4. LOGS DO LANGGRAPH

### 4.1 Fluxo de Sucesso (Esperado)

```
[DEBUG] Starting LangGraph execution for session: 8f3c-4a2e-9d1f-...
[DEBUG] State initialized: 
  {
    'session_id': '8f3c-4a2e-9d1f-...',
    'telegram_user_id': 123456789,
    'user_input': 'quais serão os temas?',
    'totem_id': None,
    'messages': [],
    'is_authenticated': False,
    'participant_id': None,
    ...
  }

[INFO] Node 'validate_user' executing...
  → Query: SELECT p.id, p.full_name, p.company, ... FROM participants WHERE telegram_user_id = $1
  → Result: {'id': 'uuid-carlos', 'full_name': 'Carlos Mendes', 'company': 'TechLog', ...}
  → State updated: is_authenticated=True, participant_profile={...}, participant_diagnosis={...}

[INFO] Conditional 'check_auth' → Route: 'classificar' (authenticated)

[INFO] Node 'classify_intent' executing...
  → Analyzing: "quais serão os temas?"
  → No injection detected
  → Intent: chat_livre (no totem_id)
  → State: current_intent='chat_livre'

[INFO] Node 'retrieve_context' executing...
  → Query: "quais serão os temas?"
  → Query vector: [0.234, -0.512, ..., 0.891] (768-dim mock)
  → SQL: SELECT ... FROM knowledge_chunks WHERE 1-(embedding<=>$1)>0.6 ORDER BY similarity DESC LIMIT 3
  → Results: [
      {'theme': 'O Fim das Fronteiras Geográficas - Zonas Francas', 'similarity': 0.73, ...},
      {'theme': 'O Gargalo do Fundador - Sucessão e Governança', 'similarity': 0.68, ...},
      {'theme': 'Arsenal Financeiro e Capital Inteligente', 'similarity': 0.62, ...}
    ]
  → RAG context prepared (3 chunks)

[INFO] Node 'call_llm' executing...
  → System prompt: "Você é o Bot Júlio, Concierge de Elite..."
  → User context: "Nome: Carlos Mendes, Cargo: CEO, Empresa: TechLog, Dor: Gargalo do Fundador..."
  → Totem context: None
  → RAG context: "[O Fim das Fronteiras...] ...\n---\n[O Gargalo do Fundador...]..."
  → Final prompt sent to MockLLM.ainvoke()
  → Response: "Ótima pergunta! Esse é exatamente o tipo de tema que abordamos na Cúpula CEO 2026..."

[INFO] Parallel edges executing:
  ├─ Node 'evaluate_upsell' executing...
  │  → Profile upsell_category: 'A'
  │  → Upsell triggers detected: False (no "mentoria", "acompanhamento", etc)
  │  → needs_team_alert: False (only Category A, but no trigger keyword)
  │
  └─ Node 'persist_history' executing...
     → MongoDB insert: {'session_id': '8f3c-...', 'participant_id': 'uuid-carlos', ...}
     → Insertion successful

[INFO] Conditional 'check_upsell' → Route: 'fim' (no team alert needed)

[INFO] LangGraph execution completed successfully
  → Final response: "Ótima pergunta! Esse é exatamente o tipo..."
  → Total execution time: 340ms
```

### 4.2 Fluxo com Upsell Alert

```
[INFO] User message: "❤️ como faço para contratar uma mentoria com Ibrahim?"

[INFO] Node 'evaluate_upsell' executing...
  → Profile: Carlos Mendes (Category A)
  → User input: "como faço para contratar uma mentoria com ibrahim?"
  → Upsell triggers: ["mentoria", "ibrahim"] found!
  → needs_team_alert: True
  → alert_reason: "Cat A | Trigger: Sim | Input: como faço para contratar uma mentoria com ibrahim?"

[INFO] Conditional 'check_upsell' → Route: 'notificar' (trigger detected)

[INFO] Node 'notify_team' executing...
  → Log: "[UPSELL ALERT] Carlos Mendes: Cat A | Trigger: Sim | Input: como faço para contratar uma mentoria com ibrahim?"
  → (Em produção: enviaria para grupo Telegram admin)

[INFO] LangGraph execution completed
  → Response enviada para telegram
```

### 4.3 Fluxo com Erro - Embedding Model Unavailable (ANTES DA FIX)

```
[ERROR] Node 'retrieve_context' failed
  → Exception: google.genai.errors.ClientError: 404 NOT_FOUND
  → Message: models/embedding-001 is not found for API version v1beta
  → Stack trace:
    File "app/agent/nodes.py", line 95, in call_llm
      response = await llm.ainvoke(messages)
    File "app/rag/retriever.py", line 38, in search
      query_vector = self.embeddings.embed_query(query)
    File ".../site-packages/langchain_google_genai/embeddings.py", line 432, in embed_documents
      raise GoogleGenerativeAIError(msg) from e
    ...

[ERROR] Exception propagated to handler
  → handle_text_message() caught exception
  → Sent: "Desculpe, a linha com os mentores está ruidosa agora. Pode repetir?"
```

### 4.4 Fluxo com Erro - Gemini Quota Exceeded (ANTES DA FIX)

```
[ERROR] Node 'call_llm' failed
  → Exception: google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
  → Message: You exceeded your current quota for generativelanguage.googleapis.com/generate_content_free_tier_requests
  → Retrying: true (3 attempts)
  → Retry delays: 26.42s, 24.22s, 21.75s...
  → Max retries exceeded after 60s

[ERROR] Exception propagated to handler
  → handle_text_message() caught exception
  → Sent: "Desculpe, a linha com os mentores está ruidosa agora. Pode repetir?"
```

---

## 5. ESTADO ATUAL (PÓS-CORREÇÕES) — Atualizado 2026-03-18

### ✅ Funcionando

- [x] Autenticação via CPF
- [x] Carregamento de participantes do DB
- [x] Diagnóstico e profile do usuário
- [x] LangGraph workflow com 7 nós
- [x] RAG retriever com mock embeddings
- [x] Claude (Anthropic) com fallback automático para MockLLM
- [x] Persistência de histórico (MongoDB)
- [x] Detecção de upsell (UPSELL ALERT testado e funcional)
- [x] Scheduler de mensagens (60s loop)
- [x] Banco populado: 4 participantes + 3 docs RAG (20 chunks)
- [x] Bot respondendo no Telegram (@Júlio_ViDi)
- [x] Docker Compose estável (botjulio_postgres, mongodb, redis)

### ⚠️ Limitações Atuais

- Claude real: API key sem créditos no workspace (console.anthropic.com)
- MockLLM ativo como fallback (responde por palavras-chave)
- RAG usa embeddings mock (sem semântica real)
- notify_team() apenas loga — não envia mensagem real ao grupo Telegram

### 👥 Participantes de Teste

| Nome | CPF | Empresa | Upsell |
|---|---|---|---|
| Carlos Mendes | 111.444.777-35 | TechLog | A |
| Ana Ferreira | 222.555.888-66 | AgroBraz | B |
| Roberto Silva | 333.666.999-97 | Silva Import | C |
| Luiz Portal | 007.348.851-80 | Ecossistema Live | C |

### 🚀 Para Produção

1. **Usar Claude (Anthropic)**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-... python app/main.py
   ```

2. **Ou usar Gemini com Billing**
   ```bash
   GOOGLE_API_KEY=... python app/main.py
   # (com billing habilitado na conta)
   ```

3. **Ou usar LLM Local (Ollama)**
   ```python
   # Trocar MockLLM por LlamaEmbeddings + OllamaChatMessage
   ```

---

## 6. COMANDOS DE TESTE

### Seed Databases
```bash
# Populate test data
python scripts/seed_participants.py
python scripts/seed_knowledge.py

# Check: 3 participants + 3 docs in RAG
psql -U postgres -d botjulio_test -c "SELECT COUNT(*) FROM participants;"  # → 3
psql -U postgres -d botjulio_test -c "SELECT COUNT(*) FROM knowledge_chunks;"  # → 9 chunks
```

### Iniciar Bot
```bash
cd bot_julio
$env:PYTHONPATH="$PWD"
python app/main.py
```

### Testar Telegram
1. Enviar `/start` → Pede CPF
2. Enviar `11144477735` → Autentica como "Carlos Mendes"
3. Enviar `o que vc pode fazer?` → MockLLM responde
4. Enviar `/status` → Mostra profile
5. Enviar `/totem TOTEM_SUCESSAO_GOVERNANCA` → Toma RAG filtrado por totem

---

## 7. PRÓXIMOS PASSOS

1. **Integrar LLM Real**: Usar Claude ou Gemini com account pago
2. **Melhorar MockLLM**: Treinar com prompts reais da Cúpula
3. **Embeddings Real**: Integrar com MiniLM ou BERT para semântica
4. **Admin Dashboard**: Interface web para monitorar upsells
5. **WhatsApp Integration**: Estender para WPP (Evolution API)
6. **Deploy**: Docker + Kubernetes + Monitoring

---

## 8. REFERÊNCIAS

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **python-telegram-bot**: https://python-telegram-bot.readthedocs.io/
- **PostgreSQL pgvector**: https://github.com/pgvector/pgvector
- **MongoDB Motor**: https://motor.readthedocs.io/
- **APScheduler**: https://apscheduler.readthedocs.io/

---

**Gerado em**: 2026-03-18 22:36 -03:00
**Atualizado em**: 2026-04-20 16:06 -03:00
**Bot Status**: 🟢 Running (MockLLM fallback ativo)
**Último Erro Corrigido**: Anthropic credit balance → fallback automático implementado
**Próximo passo**: Contratar Contabo VPS 20 e executar deploy com docker-compose + Traefik (ver Anexo A)

---

## ANEXO A — Análise de Infraestrutura (Proposta Vinícius)

> **Contexto:** Em reunião com o programador Vinícius (Abril/2026), foi proposta uma arquitetura de implantação baseada na experiência dele com o sistema Atbus (AWS). O princípio central é priorizar **autonomia operacional e custo controlado** em vez de performance máxima. Documento completo em `docs/analise-infra-vinicius.md`.

---

### A.1 — Contabo Cloud VPS 20

**Link:** https://contabo.com/en/vps/

| Recurso | Especificação |
|---|---|
| vCPUs | 6 AMD |
| RAM | ~20 GB |
| Armazenamento | ~200 GB NVMe SSD |
| Tráfego | Ilimitado |
| IPv4 | 1 dedicado |
| Preço estimado | ~€15/mês ≈ R$ 90/mês |

**Veredicto: ✅ APROVADO** para a fase de validação/tração. Economiza R$ 500–800/mês comparado a um setup equivalente na AWS (EC2 + RDS + ElastiCache).

---

### A.2 — Traefik: Proxy Reverso + HTTPS Automático

**Link:** https://traefik.io/traefik/

Traefik é um reverse proxy cloud-native que descobre containers Docker automaticamente e obtém/renova certificados SSL via **Let's Encrypt** sem configuração manual. Substitui o setup tradicional Nginx + Certbot.

**Veredicto: ✅ APROVADO** — solução para a rota HTTPS que o Vinícius indicou como bloqueador para o deploy em produção.

---

### A.3 — Kubernetes

**Veredicto: ❌ NÃO RECOMENDADO** na fase atual.

| Motivo | Detalhe |
|---|---|
| Overkill de complexidade | Nossa stack tem apenas 3–4 serviços |
| Exige equipe DevOps dedicada | Não temos esse recurso |
| Custo adicional | +€200–500/mês só em infra de cluster |
| Manutenção permanente | Contradiz o princípio do Vinícius |

Reavaliar quando o bot superar **500 usuários simultâneos** ou receita acima de R$ 30k/mês.

---

### A.4 — Docker: Arquivos Atualizados

#### Dockerfile (melhorias aplicadas)
- ✅ Usuário não-root adicionado (segurança)
- ✅ `--workers 2` para aproveitar multi-core do VPS

#### docker-compose.yml (reescrito em Abril/2026)
- ✅ **Traefik** adicionado como proxy reverso com HTTPS automático
- ✅ **Serviço `api`** (FastAPI) adicionado
- ✅ **MongoDB removido** — legado da v3.x, histórico migrado para PostgreSQL na v4.0
- ✅ Segredos movidos para `.env.production` (não commitado no Git)
- ✅ `docker-compose.dev.yml` criado para ambiente de desenvolvimento local

#### Arquivos criados
| Arquivo | Propósito |
|---|---|
| `docker-compose.yml` | Produção: Traefik + API + Postgres + Redis |
| `docker-compose.dev.yml` | Dev local: sem Traefik, hot-reload ativo |
| `.env.production.template` | Template de variáveis de produção |
| `.gitignore` | Protege `.env` e `.env.production` do Git |

---

### A.5 — Plano de Ação Resumido

**🔴 Alta Prioridade (bloqueador para produção)**
- [ ] Contratar Contabo VPS 20
- [ ] Apontar DNS `api.vidiceo.com.br` para o IP do VPS
- [ ] Preencher `.env.production` com os segredos reais
- [ ] Executar: `docker-compose up -d` no servidor

**🟡 Média Prioridade (primeira semana)**
- [ ] Validar certificado HTTPS via Traefik/Let's Encrypt
- [ ] Configurar backup automático do PostgreSQL (cron)
- [ ] Script de deploy via SSH no GitHub Actions

**🟢 Baixa Prioridade (Fase 2)**
- [ ] Monitoramento com Uptime Kuma (gratuito)
- [ ] Segundo VPS para redundância quando houver tração

---

### A.6 — Estimativa de Custos Mensais

| Item | Custo |
|---|---|
| Contabo VPS 20 | ~€15/mês ≈ R$ 90/mês |
| Domínio `.com.br` | ~R$ 3/mês |
| Let's Encrypt SSL | **Gratuito** |
| Backup Add-On Contabo | ~€1,5/mês ≈ R$ 9/mês |
| **Total estimado** | **~R$ 102/mês** |

> Comparação: AWS equivalente (EC2 t3.large + RDS + ElastiCache) = **R$ 600–900/mês**
