# Task: Strategic Consulting (C.R.A.F.T.)
id: consulting
agent: consultant-support
trigger: /consultor [query]

## Description
Ativa o modo de consultoria estratégica C.R.A.F.T., realizando busca contextual no Google Drive para enriquecer as respostas com documentos relevantes do cliente.

## Input
- Query do usuário via Telegram (texto livre sobre estratégia, diagnóstico, etc.)

## Output
- Resposta consultiva baseada no framework C.R.A.F.T., enriquecida com dados do Drive

## Steps
1. Receber query do usuário no Telegram
2. Buscar documentos relevantes no Google Drive (RAG)
3. Contextualizar resposta com dados encontrados
4. Gerar resposta consultiva no tom AgeQuodAgis
