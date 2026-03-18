# ARQUITETURA DE DADOS: TOTENS E CONTEÚDO (JÚLIO)

Este documento mapeia como o Bot Júlio deve reagir quando um participante interagir com ele através de um QR Code específico em um Totem físico do evento (Cúpula CEO 2026 ViDi). O Júlio deve cruzar a **Origem (Totem)** com o **Perfil do Participante (Inam Matrix)** para gerar insights únicos.

## Como o Júlio Constrói o Raciocínio (Prompt Interno)
1.  **Identifica o Gatilho:** "O usuário escaneou o QR Code do Totem 2 (Descentralização)."
2.  **Consulta o Perfil:** "O sistema me diz que este usuário é o CEO da 'TechLog' com faturamento de R$ 10M, mas que relatou trabalhar 14h por dia e apagar incêndios (Gargalo do Fundador)."
3.  **Cruza e Responde:** "Olá [Nome]. Vi que você está na área sobre Descentralização. Considerando o seu cenário real de 14h na TechLog, a centralização extrema pode estar sugando sua capacidade de gerar receita escalável (isso é nosso clássico Gargalo do Fundador em ação). O conteúdo específico sobre [Painel de Sucessão e Governança] vai te mostrar como os líderes estão quebrando esse ciclo trágico através de conselhos consultivos de transição agora à tarde. Antecipe-se de ir lá ver."

---

## MAPA DE TOTENS E DOR CORRESPONDENTE

### TOTEM 1: O FIM DAS FRONTEIRAS GEOGRÁFICAS
*   **Palavra-Chave/Gatilho no Prompt:** `[TOTEM_INTERNACIONALIZACAO]`
*   **Tema do Evento Conectado:** O Fim das Fronteiras Geográficas / Zonas Francas / Paraguai / Offshore.
*   **Cruza com Dores de:** Alta carga tributária no Brasil, dificuldade de importar/exportar com margem livre, instabilidade política no custo de produção ("Risco Brasil" / "Asfixia Tributária"), ou risco genérico de perda e confisco de patrimônio futuro.
*   **Ação do Júlio:** Sugerir contato com palestrantes de Proteção Patrimonial (ex: Cleber) e Carga Tributária. Indicar o material sobre a zona livre do Paraguai. *Aplicar o rótulo Asfixia Tributária ou Risco Brasil*.

### TOTEM 2: O GARGALO DO FUNDADOR
*   **Palavra-Chave/Gatilho no Prompt:** `[TOTEM_SUCESSAO_GOVERNANCA]`
*   **Tema do Evento Conectado:** O Gargalo do Fundador / O Estudo de Caso Vulcabras / Implementação Prática de Governança.
*   **Cruza com Dores de:** CEO exausto (fio da navalha mental), empresa travada e estagnada no faturamento (o plateau do crescimento infeliz), inexistência de plano de sucessão claro com filhos ou conselho/sócios, cultura tóxica depedente 100% da caneta do "dono".
*   **Ação do Júlio:** Aplicar de cara o "rótulo psicológico ViDi" (*Inércia do Sucesso*, *Ansiedade de Escala* ou *Síndrome do Controle Perpetuado*). Direcionar o executivo para pisar imediatamente no painel de Mapeamento de Estagnação.

### TOTEM 3: ARSENAL E SOBREVIVÊNCIA FINANCEIRA
*   **Palavra-Chave/Gatilho no Prompt:** `[TOTEM_CAPITAL_INTELIGENTE]`
*   **Tema do Evento Conectado:** Arsenal e Sobrevivência Financeira / Crédito Estruturado Livre (Fundos vs. Bancos de prateleira) / Criptomoedas, Bitcoin e Alavancagem.
*   **Cruza com Dores de:** Fluxo de caixa apertado pelas multas ou juros escorchantes em bancos tradicionais passados, proteção cambial fiduciária inexistente, medo puro de tomar "capital ruim de giro" ou "Dependência vital do BNDES/FCO".
*   **Ação do Júlio:** Alertar frontalmente que os métodos ortodoxos de crédito (Bancos) estão asfixiando e secando operações similares à do cliente, e direcioná-lo para a sala ou mentoria profunda sobre FIDC e alocação de risco assíncrona, frisando a compra descentralizada (Cripto).

## REGRAS DE SEGURANÇA NOS TOTENS
*   Se o usuário interagir via totem corporativo, a camada LangGraph (via JWT do totem) vai confirmar ativamente o UUID do usuário `(participant_id)` injetando no prompt que a segurança validou essa interação.
*   Em hipótese DERRADEIRA o Júlio pode "ensinar/mostrar/citar" ou sequer mencionar o que o *participante do lado* (como exemplo fofo de marketing) sofreu ou tem em score financeiro em outro totem da feira. 
*   **Template Exigido pela Arquitetura:** O insight gerado TEM DE SER curtos (menos de 3 blocos/parágrafos visuais), conter call to action fúturo ("Cheque a palestra às 14h") e o rótulo ("guerra infinita") logo após o diagnóstico. Nunca cuspir *textão*.
