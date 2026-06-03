# Story: ST-002 - Finalização do Bot Júlio v4.0 (Infra & Orquestração)

## Descrição
Finalizar a transição para a arquitetura v4.0, garantindo segurança na API, remoção de débitos técnicos e orquestração otimizada.

## Checklist
- [x] Criar orquestrador nativo em `app/agent/orchestrator.py`
- [x] Remover `app/agent/graph.py` e dependência `langgraph`
- [x] Remover `app/db/mongo.py` e `app/telegram_bot_handlers/`
- [x] Corrigir SQL Injection no `list_participants` (`app/api/admin.py`)
- [x] Implementar `active_sessions` count no `get_stats` via Redis
- [ ] Criar script de teste de carga básico (simulado via API)
- [ ] Atualizar checklist da story após conclusão

## Arquivos Afetados
- `bot_julio/app/agent/orchestrator.py` (criado)
- `bot_julio/app/api/admin.py` (modificando)
- `bot_julio/app/whatsapp_handlers/handlers.py` (atualizado)
- `bot_julio/requirements.txt` (atualizado)

## Status
Em Andamento
