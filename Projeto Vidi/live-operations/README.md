# 🚀 Squad: Live Operations

Squad operacional central da **Live Consultoria**, responsável pelo bot Telegram e todas as integrações com serviços Google.

## 🎯 Missão
Fornecer um assistente de IA completo via Telegram que atua como consultor estratégico, recrutador, gerador de propostas e gerente de documentos — tudo integrado com Google Drive e Calendar.

## 👥 Agente

### Consultant Support (`/start`, `/consultor`, `/rh`, `/proposta`, `/doc`, `/agenda`)
- **Plataforma:** Telegram Bot
- **Personalidade:** Professional, Efficient, Strategic (AgeQuodAgis)
- **Motor de IA:** Gemini 2.5 Flash

## 🧠 Modos de Operação

| Modo | Comando | Prompt | Especialidade |
|------|---------|--------|---------------|
| **C.R.A.F.T.** | `/consultor` | `live-craft.md` | Consultoria estratégica + Drive Search |
| **Recruiter** | `/rh` | `live-recruiter.md` | Análise de perfis, JDs, metodologia STAR |
| **Proposals** | `/proposta` | `live-proposals.md` | Framework M.A.P.C.A para propostas |
| **Status** | — | `live-status.md` | Status operacional do projeto |
| **Router** | — | `router.md` | Roteamento inteligente entre modos |

## 🔗 Integrações

```
Telegram ←→ [Bot] ←→ Gemini API
                  ←→ Google Drive (RAG)
                  ←→ Google Calendar (Agenda)
```

## 🚀 Início Rápido

1. Configurar variáveis no `.env`:
   ```
   TELEGRAM_BOT_TOKEN=seu_token
   GEMINI_API_KEY=sua_chave
   GOOGLE_APPLICATION_CREDENTIALS=./path/credentials.json
   ```

2. Iniciar o bot:
   ```bash
   node .aios-core/scripts/telegram-bot.js
   ```

3. No Telegram, enviar `/start` para abrir o menu interativo.

## 📋 Requisitos
- Node.js instalado
- Bot criado via @BotFather no Telegram
- Google Cloud Project com Drive e Calendar APIs ativas
- Credenciais de serviço (JSON) para Google APIs
