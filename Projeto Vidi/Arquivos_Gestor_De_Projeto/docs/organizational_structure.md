# Estrutura Organizacional: VIDI & Cúpula CEO

Este documento detalha as funções, responsabilidades e a hierarquia da equipe dedicada ao projeto.

## 📊 Organograma Funcional

```mermaid
graph TD
    %% Estilos
    classDef strategic fill:#0A243D,stroke:#c5a059,stroke-width:3px,color:#fff;
    classDef operational fill:#00e800,stroke:#06192a,stroke-width:2px,color:#06192a;
    classDef staff fill:#f9f,stroke:#333,stroke-width:2px;
    classDef pending fill:#eee,stroke:#999,stroke-dasharray: 5 5;

    %% Nível Estratégico
    STRAT[Estratégia & Mentoria]
    STRAT --- IB[Ibrahim]
    STRAT --- LP[Luiz Portal]
    class STRAT,IB,LP strategic;

    %% Nível Operacional
    STRAT --> ADM[Adm & Financeiro]
    STRAT --> EVT[Eventos]
    STRAT --> MKT[Marketing]
    STRAT --> TEC[Tecnologia]
    STRAT --> COM[Comercial]
    STRAT --> CST[Consultoria]

    ADM --- ANA[Ana]
    EVT --- JOAO[João]
    MKT --- BRUNO[Bruno L.]
    MKT --- GUI[Guilherme - Tráfego]
    TEC --- CLEBER[Cléber]
    COM --- MARI[Mariana]
    CST --- PEND[Aguardando Especialistas]

    class ADM,EVT,MKT,TEC,COM,ANA,JOAO,BRUNO,GUI,CLEBER,MARI operational;
    class CST,PEND pending;

    %% Célula de Staff (Transversal)
    subgraph STF_CELL [Célula de Staff]
        STF_ANA[Ana]
        STF_JOAO[João]
        STF_CLEBER[Cléber]
        STF_SOPHIA[Sophia]
    end
    class STF_CELL,STF_ANA,STF_JOAO,STF_CLEBER,STF_SOPHIA staff;

    %% Conexões de Suporte
    IB -.-> STF_CELL
    LP -.-> STF_CELL
```

---

## 👥 Atribuições e Responsabilidades

### 🏛️ Estratégico (Conselho & Mentores)
*   **Ibrahim:** Visão master, estratégia de Equity/Exit e mentor principal do *ViDi*.
*   **Luiz Portal:** Estratégia executiva, cultura organizacional e mentor de *Liderança Antifrágil*.

### ⚙️ Operacional (Lideranças de Setor)
*   **Ana (Adm & Financeiro):** Gestão de caixa, contratos e saúde administrativa do projeto.
*   **João (Organização de Eventos):** Logística, produção e entrega da *Cúpula CEO* e imersões.
*   **Bruno L. (Marketing):** Branding, posicionamento e comunicação estratégica.
*   **Guilherme (Tráfego):** Gestão de anúncios e aquisição de leads qualificados.
*   **Cléber (Tech):** Infraestrutura digital, governança via IA (ClickUp/AIOS) e automações.
*   **Mariana (Comercial):** Vendas, fechamento de mentorias e relacionamento com clientes.
*   **Consultoria (Em aberto):** Setor aguardando a entrada de especialistas para entrega técnica pontual aos mentorados.

### 🍱 Célula de Staff (Suporte Transversal)
Grupo focado na execução de suporte direto aos fundadores e suporte operacional ao evento.
*   **Integrantes:** Ana (Adm), João (Eventos), Cléber (Tech) e Sophia.
