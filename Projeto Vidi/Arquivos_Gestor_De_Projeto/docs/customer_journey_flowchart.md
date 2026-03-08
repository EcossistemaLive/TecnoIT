# Jornada do Cliente: VIDI & Cúpula CEO (The Catalyst)

Este documento detalha o fluxo de experiência do cliente, desde a atração inicial até as mentorias de alta cúpula, conforme definido no planejamento de Fevereiro/2026.

## 📊 Fluxograma Visual da Jornada

```mermaid
graph TD
    %% Estilos
    classDef attraction fill:#f9f,stroke:#333,stroke-width:2px;
    classDef event fill:#00e800,stroke:#06192a,stroke-width:2px,color:#06192a;
    classDef upsell fill:#c5a059,stroke:#05070a,stroke-width:2px,color:#fff;
    classDef downsell fill:#ff5722,stroke:#05070a,stroke-width:2px,color:#fff;
    classDef core fill:#0A243D,stroke:#00e800,stroke-width:2px,color:#fff;
    classDef step fill:#e1d5e7,stroke:#9673a6,stroke-width:2px;

    %% Planejamento e Atração
    P[Planejamento] --> A1[Google Ads - Regional]
    P --> A2[Lives de Aquecimento]
    A1 --> B[Lead Captação]
    A2 --> B
    
    %% Evento de Entrada
    B --> C{Cúpula CEO - 1 Dia}
    class C event;
    
    C --> NX[Próximo Passo]
    class NX step;

    NX --> C1[Standard Experience]
    NX --> C2[VIP Experience]

    %% Upsells
    C2 --> U1[Upsell: VIP Pass]
    C2 --> U2[Upsell: Cúpula - Dinner]
    C2 --> U3[Upsell: Pacote Sócio]
    C2 --> U4[Upsell: Diagnóstico Catalyst]
    
    class U1,U2,U3,U4 upsell;

    %% Downsells
    C1 --> D1[Downsell: Virtual Pass]
    C1 --> D2[Downsell: CEO Toolkit]
    
    class D1,D2 downsell;

    %% Meio de Funil e Topo
    C1 & C2 --> NX2[Próximo Passo]
    class NX2 step;

    NX2 --> E[Mentoria Liderança Antifrágil]
    NX2 --> F[Mentoria The Catalyst]
    NX2 --> G[Consultoria + Mentoria]
    
    class E,F,G core;

    E --> E1[Cultura de Alta Performance]
    E1 --> F
    F --> F1[Cadeira no Conselho]
    F1 --> H[Equity & Exit Strategy]
    
    class H core;

    %% Aplicação de Estilos
    class P,A1,A2,B attraction;
```

---

## 🧭 Detalhamento das Fases & Produtos

### 1. Ingressos & Lotes (Cúpula CEO)
*   **Lote 1 (Early Bird):** R$ 1.197 (Apenas os 50 primeiros).
*   **Lote Nomad (Padrão):** R$ 1.497.
*   **Sócio:** 50% de desconto no segundo ingresso (apenas categoria Standard).

### 2. Upsells Estratégicos
*   **VIP Pass (+ R$ 997):**
    *   Acesso a áreas exclusivas.
    *   Coffee break e Almoço com palestrantes e CEOs.
*   **Upgrade Cúpula (+ R$ 7.997):**
    *   Inclui VIP Pass.
    *   Jantar exclusivo com a cúpula do evento e CEOs.
*   **Diagnóstico Catalyst (R$ 297):**
    *   Pré-diagnóstico empresarial via IA.
    *   Possibilidade do case ser analisado ao vivo pelos CEOs no palco.

### 3. Downsell (Recuperação)
*   **Virtual Pass (R$ 997):**
    *   Acesso online ao evento.
    *   Bônus: Acesso ao curso completo.

### 4. Mentoria & Consultoria
*   **Mentoria Liderança Antifrágil (Luiz Portal):** R$ 39.997.
*   **Mentoria The Catalyst (Ibrahim Boufleur):** R$ 100.000.
*   **Consultoria Customizada:** Sob consulta.

---

## 🎮 Gamificação do Evento
Para incentivar o engajamento e a conclusão de tarefas durante o evento:

*   **Regras:** Check-in obrigatório em todas as palestras e tarefas cumpridas.
*   **Brindes por Engajamento:**
    *   Acesso ao curso (para quem cumprir tarefas).
    *   Análise do pré-diagnóstico (para quem já adquiriu o Diagnóstico Catalyst).
    *   Livro autografado.
*   **Premiação Top 3 (Ranking de Gamificação):**
    *   **Diagnóstico Completo** feito pelo time de especialistas da Catalyst.

