# PEP HUB NEXUS / PRIME — Padrão Corporativo Disruptivo & Executivo (v4.0)

> **Documento de Especificação Técnica e Identidade Visual para a Regional Norte**  
> *Versão de Homologação em Branch de Teste (`test/nova-identidade-visual`)*  
> *Ambiente: Preview Local Ativo (`http://localhost:8787`)*  
> *Data de Elaboração: Outubro / 2026*  
> *Status: Em Avaliação Executiva*

---

## 1. Visão Geral & Filosofia de Design Disruptivo

O **PEP HUB NEXUS (PRIME v4.0)** representa uma recriação profunda na arquitetura de UI/UX de todo o ecossistema analítico da Regional Norte. Inspirado nas plataformas mais inovadoras do mundo tech e financeiro de alta densidade (Linear App, Raycast, Vercel Dashboard, Apple macOS Pro e Bloomberg Next-Gen), o modelo une uma **estética futurista de comando escuro (Dark Executive Canvas)** à solidez e autoridade corporativa da Claro.

### Pilares da Recriação:
1. **Dark Executive Canvas & Atmosfera Imersiva**:
   - Superfície principal em **Obsidian & Carbon** (`#06080e`), enriquecida com iluminação volumétrica ambiente por malhas radiais sutis (`radial-gradient` Ruby `#e11d4812` e Blue Sky `#38bdf806`).
   - Elimina o cansaço visual de fundos brancos/cinzas estáticos em telas operacionais usadas durante longas jornadas.
2. **Telemetria Cockpit HUD em Tempo Real**:
   - O sub-header tradicional foi recriado como uma esteira de telemetria de voo:
     - `● D1 CORE ONLINE`: Status do banco de dados na borda da Cloudflare com beacon pulsante neon.
     - `EDGE LATENCY: 14ms`: Métricas de performance imediata.
     - `ZERO-TRUST ENFORCED`: Confirmação do Server-Side Gate e integridade de sessão.
     - `REGIONAL NORTE [AM·PA·MA·AP·RR]`: Escopo geográfico explícito.
3. **Bento Grid Modular (Cockpit Executivo)**:
   - Introdução do padrão **Bento Grid** no topo da Central Administrativa e dos Relatórios, trazendo cartões modulares com elevações translúcidas (`backdrop-filter: blur(20px)`), ícones temáticos luminosos, bordas com iluminação ao passar o mouse e valores métricos destacados em fonte monoespaçada.
4. **Segmented Control Island (Navegação em Pilares)**:
   - Os pilares de governança foram transformados em um dock flutuante de vidro escuro, com pílulas segmentadas, ícones iluminados e feedback tátil/visual imediato sem recarregamento da página.
5. **Tipografia Executiva de Três Camadas**:
   - **Outfit**: Headings, títulos de módulos e identidades de marca com peso expressivo e kerning refinado.
   - **Plus Jakarta Sans**: Corpo de texto, formulários e rótulos com altíssima legibilidade.
   - **JetBrains Mono**: Números tabulares (`tabular-nums`), deltas analíticos (`p.p.`), timestamps e telemetria.
6. **Autenticação Split-Screen com Efeito Aurora**:
   - Telas de acesso (`/login/`, `/register/`, etc.) integradas ao Dark Canvas, combinando canvas animado com formulário em vidro jateado e foco luminoso.

---

## 2. Tokens de Design (CSS Custom Properties)

A folha de estilos unificada fica localizada em [public/css/pephub-prime.css](file:///c:/Users/F138138/DEV/Churn_Safra/public/css/pephub-prime.css) e padroniza as seguintes variáveis globais:

### 2.1 Superfícies & Cores Neutras (Dark Canvas)
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-bg` | `#06080e` | Fundo geral imersivo (Obsidian Dark) |
| `--prime-bg-elevated` | `#0a0e18` | Fundo de sub-barras e cabeçalhos |
| `--prime-surface` | `#0d121f` | Superfície primária de painéis, tabelas e cartões |
| `--prime-surface-glass` | `rgba(13, 18, 31, 0.78)` | Superfície em vidro jateado translúcido com blur de 20px |
| `--prime-surface-hover` | `#151d30` | Hover suave em linhas e cartões |
| `--prime-border` | `rgba(255, 255, 255, 0.08)` | Bordas sutis estruturais estilo lâmina |
| `--prime-border-hover` | `rgba(225, 29, 72, 0.4)` | Destaque de borda em hover com glow Ruby |
| `--prime-border-active` | `#e11d48` | Borda de foco e estado selecionado |

### 2.2 Tipografia & Tinta
| Token | Valor Hex | Finalidade |
| :--- | :--- | :--- |
| `--prime-ink-primary` | `#f8fafc` | Texto principal, títulos e valores de destaque (Slate 50) |
| `--prime-ink-secondary` | `#94a3b8` | Rótulos de KPI, subtítulos e dados auxiliares (Slate 400) |
| `--prime-ink-muted` | `#64748b` | Placeholders, notas técnicas e legendas (Slate 500) |
| `--prime-ink-inverse` | `#06080e` | Texto escuro sobre botões e badges claros |

### 2.3 Identidade Claro Ruby & Semântica Analítica Neon
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-brand` | `#e11d48` | Claro Ruby / Rose 600 corporativo |
| `--prime-brand-glow` | `rgba(225, 29, 72, 0.3)` | Halo luminoso em botões e elementos ativos |
| `--prime-green` | `#10b981` | Sucesso, Retenção, Meta Atingida, Beacon Online |
| `--prime-red` | `#f43f5e` | Churn, Bloqueios Críticos, Cancelamento |
| `--prime-amber` | `#f59e0b` | Atenção, Parcial, Safra em Foco |
| `--prime-blue` | `#38bdf8` | Links, Seleções, Contratos Ativos, Latência |
| `--prime-purple` | `#a855f7` | Inteligência Artificial, RAG, Few-Shot Gabaritos |

---

## 3. Guia de Componentes Chave

### 3.1 Cockpit Bento Grid
```html
<div class="bento-grid">
  <div class="bento-card">
    <div class="bento-header">
      <span class="bento-label">Colaboradores & Acessos</span>
      <div class="bento-icon"><svg>...</svg></div>
    </div>
    <div class="bento-value">142</div>
    <div class="bento-subtext">
      <span class="telemetry-beacon"></span>
      <span>98.6% com acesso regular homologado</span>
    </div>
  </div>
</div>
```

### 3.2 Telemetry Pills com Beacon Pulsante
```html
<span class="telemetry-pill">
  <span class="telemetry-beacon"></span> D1 CORE ONLINE
</span>
<span class="telemetry-pill">EDGE: 14ms</span>
<span class="telemetry-pill">ZERO-TRUST ENFORCED</span>
```

### 3.3 Botões com Efeito Specular Glow
```html
<button class="btn-primary">
  <svg>...</svg> Salvar Alterações
</button>
<button class="btn-secondary">Cancelar</button>
```

---

## 4. Regras Corporativas Inegociáveis

1. **Notação de Pontos Percentuais:**
   - Estritamente `p.p.` em minúsculo, com espaço não-quebrável antes da unidade (`+0,42 p.p.`).
2. **Alinhamento Numérico:**
   - Todo dado quantitativo, contagem, valor em reais ou percentual deve ter alinhamento à direita (`class="num"` ou `style="text-align:right"`) e utilizar `font-variant-numeric: tabular-nums`.
3. **Zero Dependências:**
   - Nenhum bundle externo de Tailwind, React, Bootstrap ou bibliotecas volumosas. Apenas CSS puro de alto desempenho e JavaScript Vanilla.
4. **Respeito aos IDs de Sistema:**
   - Todas as classes e IDs existentes nos arquivos de lógica (`admin.js`, `header-widget.js`, `app-mobile.js`) devem ser mantidos sem refatoração que quebre funcionalidades.

---

## 5. Como Testar no Navegador Local

O servidor de preview rápido e auto-autenticado já está ativo:
- **Central Administrativa:** [http://localhost:8787/admin/](http://localhost:8787/admin/)
- **Portal Executivo:** [http://localhost:8787/](http://localhost:8787/)
- **Painel Churn Safra:** [http://localhost:8787/churn/](http://localhost:8787/churn/)
- **Tela de Login Corporativo:** [http://localhost:8787/login/](http://localhost:8787/login/)
