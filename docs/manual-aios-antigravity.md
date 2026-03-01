# Manual: Sincronização e Atualização AIOS-core & AntiGravity

Este guia detalha como extrair o máximo do **AntiGravity** dentro do ecossistema AIOS, garantindo que as funcionalidades e agentes estejam sempre sincronizados e operando com precisão. Em conformidade com as regras de projeto da **Tecno IT**, as orientações de segurança aplicam-se à estrutura de Departamentos.

---

## ⚙️ Entenda o AntiGravity
O AntiGravity opera em modo **workflow-based**. Diferente de outras plataformas, ele não possui hooks automáticos de ciclo de vida. Esta é uma arquitetura deliberada, integrada nativamente ao ecossistema Google Cloud (Firebase, Google MCP).

### Características no AntiGravity:
- ❌ Sem verificações automáticas pré/pós-ação.
- ❌ Sem rastreamento automático de sessão.
- ❌ Sem audit trail nativo.
- ✅ Acesso aos 11 agentes especialistas.
- ✅ Sistema completo de Stories, Workflows e Squads.
- ✅ Lógica de qualidade em 3 camadas.

> [!TIP]
> A compensação para a falta de hooks é simples: rode os validadores manualmente e carregue o contexto com intenção.

---

## 📦 Passo 1: Instalação e Atualização
Mantenha o AIOS atualizado para garantir a paridade de funcionalidades.

### Novo Projeto:
```bash
npx @synkra/aios-core init meu-projeto
```

### Projeto Existente:
```bash
cd seu-projeto
npx @synkra/aios-core install
```

### Atualização (Antes de sessões importantes):
```bash
npx aios-core@latest install
```
*O instalador preserva suas customizações (`.bak`) e configurações do projeto.*

---

## 🔧 Passo 2: Sincronização (Sync)
A fonte da verdade dos agentes reside em `.aios-core/development/agents/`. Sempre que atualizar o framework ou modificar agentes, propague as mudanças para o AntiGravity.

### Sincronizar:
```bash
npm run sync:ide:antigravity
```

### Verificar Sincronia:
```bash
npm run sync:ide:check
```

### Sincronizar Todas as IDEs:
```bash
npm run sync:ide
```

---

## 🧠 Passo 3: Ativação de Agentes
No AntiGravity, a ativação é orientada por **Workflows** localizados em `.agent/workflows/`.

1. **Localize o workflow:** Cada agente tem seu arquivo `.md`.
2. **Carregue explicitamente:** "Abra o workflow de `[nome-do-agente]` em `.agent/workflows/` e carregue como contexto desta sessão."

### Agentes Disponíveis:
| Comando          | Agente | Função                  |
| :--------------- | :----- | :---------------------- |
| `@dev`           | Dex    | Implementação de código |
| `@qa`            | Quinn  | Qualidade e testes      |
| `@architect`     | Aria   | Arquitetura técnica     |
| `@po`            | Nova   | Backlog e produto       |
| `@pm`            | Morgan | Estratégia de produto   |
| `@sm`            | River  | Facilitação de processo |
| `@analyst`       | Zara   | Análise de negócio      |
| `@data-engineer` | Dara   | Engenharia de dados     |
| `@devops`        | Felix  | CI/CD e operações       |
| `@ux-expert`     | Uma    | Design e UX             |
| `@aios-master`   | Pax    | Orquestração geral      |

---

## 🔁 Passo 4: Fluxo de Trabalho Completo

### Fase 1: Planejamento
Ative em sequência: `@analyst` → `@pm` → `@architect` → `@ux-expert`.
- **Output:** PRD, arquitetura e critérios de aceite salvos em `/docs` (ou nos subdiretórios dos departamentos na Tecno IT).

### Fase 2: Preparação (Stories)
Use `@aios-master *create-story` ou `@sm`.
- **Destino:** `docs/stories/STORY-XX.md`.

### Fase 3: Desenvolvimento (AntiGravity)
1. Abra a Story no contexto.
2. Ative o `@dev`: `Carregue .agent/workflows/dev.md e execute a story docs/stories/STORY-42.md`.
3. Valide com `@qa`: `Carregue .agent/workflows/qa.md e revise a entrega da STORY-42`.
4. Atualize o progresso: `[ ]` → `[x]`.

---

## ✅ Passo 5: Validação Manual
Substitua os hooks automáticos por estes comandos manuais:

- **Antes da sessão:** `npx aios-core doctor`
- **Paridade de config:** `npm run validate:parity`
- **Após alterações:** `npm run sync:ide:antigravity`
- **Ao finalizar Story:** `npm run validate:parity`, `npm test`, `npm run lint`

---

## 🔑 Passo 6: Configuração do MCP (Google)
Configure em `.antigravity/antigravity.json`:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/sse"
    }
  }
}
```
Verifique o status: `aios mcp status`

---

## 🛡️ Passo 7: Quality Gates
1. **Camada 1 (Local):** `npm run lint`, `npm run build`
2. **Camada 2 (Pré-push):** `npm run validate:parity`, `npm test`
3. **Camada 3 (CI/CD):** Rodado via GitHub Actions após sucesso nas camadas 1 e 2. O acesso para execução dos deploys deve se submeter aos `CODEOWNERS` no repositório Tecno IT.

---

## ⚡ As 5 Regras de Ouro
1. **Contexto Explícito Sempre:** Reabra workflows e stories a cada sessão.
2. **Um Agente por Vez:** Nunca misture instruções entre agentes.
3. **Stories são a Verdade:** Se não está na story, não existe para o agente.
4. **Valide Antes de Fechar:** Rode `npm run validate:parity` ao encerrar.
5. **Atualize Sempre:** `npx aios-core@latest install` em novos projetos.

---

## 🔍 Diagnóstico Rápido
- **Agente não responde:** Verifique `.agent/workflows/` e rode `npm run sync:ide:antigravity`.
- **Conflito de Sync:** `npm run sync:ide -- --dry-run`.
- **Rebuild de Contexto:** `rm -rf .aios-core/core/cache/` seguido de `aios rebuild`.
