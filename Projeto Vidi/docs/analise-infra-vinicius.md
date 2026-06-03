# Análise de Infraestrutura — Proposta Vinícius
**Data:** Abril 2026 | **Contexto:** Bot Júlio v4.0 — Implantação em produção

---

## 1. Contexto da Conversa com o Vinícius

O programador Vinícius trouxe uma proposta de infraestrutura baseada na experiência dele com o sistema **Atbus (AWS)**. O princípio central levantado foi:

> *"A gente sacrificou algumas possibilidades de corte de custo em troca de não precisar de pessoas para dar manutenção."*

Isso é altamente relevante para a ViDi/TecnoIT. A escolha de infraestrutura deve priorizar **autonomia operacional e custo controlado**, não performance máxima. A proposta se baseia em:

1. **VPS Contabo** como servidor próprio (custo fixo previsível)
2. **Traefik** como proxy reverso para garantir HTTPS automático
3. **Docker + docker-compose** para containerização
4. Avaliação de **Kubernetes**

---

## 2. Contabo Cloud VPS 20 — Avaliação

**Link:** https://contabo.com/en/vps/

### Especificações Estimadas do VPS 20

| Recurso | Estimativa para VPS 20 |
|---|---|
| vCPUs | 6 AMD |
| RAM | 20 GB |
| Armazenamento | 200 GB NVMe SSD |
| Tráfego | Ilimitado |
| IPv4 | 1 dedicado |
| SO | Linux (Ubuntu, Debian, etc.) |
| Preço | ~€14–18/mês (~R$ 85–110/mês) |

> ⚠️ Confirme as especificações exatas em https://contabo.com/en/vps/ — os planos mudam com frequência.

### Vantagens para o Projeto
- ✅ Preço fixo e previsível — sem surpresas como na AWS
- ✅ Sem cobrança por transferência — tráfego ilimitado
- ✅ Root access — sem limitações de PaaS
- ✅ NVMe rápido — ideal para PostgreSQL + pgvector (RAG)
- ✅ 20 GB RAM — confortável para FastAPI + PostgreSQL + Redis em containers
- ✅ Simplicidade — 1 servidor, sem orquestração complexa

### Desvantagens / Riscos
- ⚠️ Sem auto-scaling — pico de usuários simultâneos pode saturar
- ⚠️ Sem redundância automática — se o servidor cair, tudo cai
- ⚠️ Backups precisam ser configurados
- ⚠️ Data center na Europa (Alemanha) — latência de ~200ms para Brasil

### Veredicto
🟢 **RECOMENDADO** para a fase atual. Pagar R$ 400–800/mês de AWS por enquanto seria desperdício. O VPS 20 da Contabo suporta com folga todo o stack do Bot Júlio v4.0.

---

## 3. Traefik — Proxy Reverso HTTPS

**Link:** https://traefik.io/traefik/

### O que é o Traefik?
Traefik é um reverse proxy e load balancer cloud-native, popular com Docker. Ele automaticamente:
- Descobre containers Docker e gerencia rotas
- **Obtém e renova certificados SSL via Let's Encrypt** (HTTPS automático)
- Faz roteamento por domínio (ex: `api.vidiceo.com.br` → container FastAPI)

### Comparação: Traefik vs Nginx Manual

| Critério | Traefik | Nginx Manual |
|---|---|---|
| HTTPS automático | ✅ Sim (Let's Encrypt) | ⚠️ Manual (Certbot) |
| Configuração | Labels no docker-compose | Arquivos .conf |
| Atualização de rotas | Automática | Restart manual |
| Dashboard visual | ✅ Incluso | ❌ Nenhum |
| Suporte a múltiplos domínios | ✅ Nativo | ⚠️ Configuração manual |

### Veredicto
🟢 **RECOMENDADO**. Para o setup VPS + Docker, Traefik é a solução mais eficiente. Resolve a rota HTTPS sem configuração manual de certificados.

---

## 4. Kubernetes — Necessário?

### Análise para o Bot Júlio v4.0

| Critério | Nossa Situação | Kubernetes Resolve? |
|---|---|---|
| Número de serviços | 3–4 (API, Postgres, Redis, Traefik) | K8s é overkill para <5 serviços |
| Número de servidores | 1 VPS | K8s precisa de pelo menos 3 nodes |
| Equipe DevOps | Sem equipe dedicada | K8s exige expertise permanente |
| Budget de infra | Mínimo | K8s adiciona €200–500/mês só em infra |

### Quando considerar Kubernetes (no futuro)
- Quando tivermos >500 usuários simultâneos constantes
- Quando o bot estiver gerando >R$ 30k/mês de receita
- Quando precisarmos de múltiplas instâncias regionais
- Quando tivermos um DevOps dedicado na equipe

### Veredicto
🔴 **NÃO RECOMENDADO** para a fase atual. Kubernetes seria sobreengenharia cara e complexa. O próprio Vinícius disse que K8s requer "pessoas para dar manutenção" — exatamente o que queremos evitar.

**Alternativas mais leves (se precisarmos de resiliência no futuro):**
- Docker Swarm (orquestração simples, mesmo docker-compose)
- 2 VPS com Traefik em modo ativo-passivo
- Render.com ou Railway (PaaS se quisermos delegar a infra)

---

## 5. Dockerfile — Avaliação do Existente

**Arquivo:** `bot_julio/Dockerfile`

O Dockerfile atual usa `python:3.11-slim`, cacheia layers corretamente e faz limpeza do apt. É um bom ponto de partida.

### Melhorias Recomendadas para Produção

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuário não-root (segurança)
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8080

# 2 workers para aproveitar multi-core do VPS 20
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

**Mudanças principais:** usuário não-root para segurança e `--workers 2` para aproveitar os vCPUs.

---

## 6. docker-compose.yml — Avaliação do Existente

**Arquivo:** `bot_julio/docker-compose.yml`

### Problemas Identificados
- ❌ **MongoDB ainda presente** — foi removido na migração v4.0 (legado)
- ❌ **Sem serviço da API** (FastAPI) — o compose só sobe os bancos
- ❌ **Sem Traefik** — sem HTTPS
- ❌ **Sem .env.production** referenciado para segredos

### docker-compose.yml Recomendado para Produção

```yaml
version: "3.9"

services:
  # Traefik — Proxy Reverso + HTTPS Automático
  traefik:
    image: traefik:v3.0
    container_name: botjulio_traefik
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=${LETSENCRYPT_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_letsencrypt:/letsencrypt
    restart: unless-stopped

  # Bot Júlio — FastAPI (App Principal)
  api:
    build: .
    container_name: botjulio_api
    env_file: .env.production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.vidiceo.com.br`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=8080"

  # PostgreSQL + pgvector (RAG)
  postgres:
    image: pgvector/pgvector:pg16
    container_name: botjulio_postgres
    env_file: .env.production
    volumes:
      - botjulio_pg_data:/var/lib/postgresql/data
      - ./app/db/migrations:/docker-entrypoint-initdb.d:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (cache, rate-limit, sessões)
  redis:
    image: redis:7-alpine
    container_name: botjulio_redis
    volumes:
      - botjulio_redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  botjulio_pg_data:
  botjulio_redis_data:
  traefik_letsencrypt:
```

---

## 7. Plano de Ação — Prioridades (Status Atualizado)

### 🔴 Alta Prioridade (Bloqueador para produção)
- [ ] **Contratar Contabo VPS 20** (ou equivalente com 16–20 GB RAM)
- [ ] **Registrar/apontar domínio** de API (ex: `api.vidiceo.com.br`) para o IP do VPS
- [x] **Atualizar docker-compose.yml** — remover MongoDB, adicionar serviço `api` e Traefik (Concluído)
- [x] **Criar `.env.example`** com variáveis de produção preparadas (Concluído, `.env.production` a ser criado na VPS)
- [x] **Integração de Webhook Evolution API** + Agente de Processamento Assíncrono (BackgroundTasks)
- [x] **Implementação de Criptografia de CPF (LGPD)** no banco de dados e fluxos de conversa.

### 🟡 Média Prioridade (Primeira semana após VPS)
- [x] **Atualizar Dockerfile** — usuário não-root + `--workers 2` (Concluído)
- [ ] **Configurar Traefik** com Let's Encrypt para HTTPS automático (Aguardando Deploy na VPS)
- [ ] **Script de deploy** — `docker-compose pull && docker-compose up -d` via SSH
- [ ] **Backup automático** do PostgreSQL (cron + Contabo Backup Add-On)

### 🟢 Baixa Prioridade (Fase 2)
- [ ] Monitoramento com **Uptime Kuma** (gratuito, roda no mesmo VPS)
- [ ] **GitHub Actions** para CI/CD via SSH
- [ ] Avaliar **segundo VPS** para redundância quando tiver tração real

---

## 8. Estimativa de Custos Mensais

| Item | Custo |
|---|---|
| Contabo VPS 20 | ~€15/mês ≈ R$ 90/mês |
| Domínio `.com.br` | ~R$ 40/ano ≈ R$ 3/mês |
| Let's Encrypt SSL | **Gratuito** |
| Backup Add-On Contabo | ~€1,5/mês ≈ R$ 9/mês |
| **Total estimado** | **~R$ 102/mês** |

**Comparação com AWS equivalente:** EC2 t3.large + RDS + ElastiCache = R$ 600–900/mês

**Economia estimada: R$ 500–800/mês** ao adotar Contabo + Docker.

---

## 9. Links de Referência

- 🔗 **Contabo VPS:** https://contabo.com/en/vps/
- 🔗 **Traefik:** https://traefik.io/traefik/
- 🔗 **Traefik + Docker Docs:** https://doc.traefik.io/traefik/providers/docker/
- 🔗 **Let's Encrypt:** https://letsencrypt.org/

---
*Documento gerado em: Abril 2026 | ViDi / TecnoIT*
