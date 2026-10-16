# PEP HUB PRIME — Padrão Corporativo de Design System Executivo (v3.0)

> **Documento de Especificação Técnica e Identidade Visual para a Regional Norte**  
> *Versão de Homologação em Branch de Teste (`test/nova-identidade-visual`)*  
> *Data de Elaboração: Outubro / 2026*  
> *Status: Em Avaliação Executiva*

---

## 1. Visão Geral & Filosofia de Design

O **PEP HUB PRIME** foi desenvolvido para transformar o ecossistema analítico da Regional Norte em uma plataforma corporativa executiva de nível mundial. Inspirado nas melhores experiências de produtos de dados e dashboards modernos de alta densidade (Stripe Dashboard, Linear App, Datadog Enterprise e Vercel Analytics), o sistema prioriza:

1. **Claridade Executiva e Ausência de Fadiga Visual**:
   - Eliminação de fundos cinzentos pesados (`#f4f5f7`) em favor de uma superfície repousante Slate (`#f8fafc`).
   - Substituição de gradientes horizontais estridentes (arco-íris vermelho-amarelo) pelo padrão **Obsidian & Ruby**, transmitindo sofisticação, seriedade e prestígio corporativo.
2. **Tipografia Precisa com Alinhamento Numérico Nativo**:
   - Ativação obrigatória de `font-variant-numeric: tabular-nums` para que dígitos não oscilem em colunas e cartões de KPI.
   - Escala modular de tamanhos de fonte com tracking negativo sutil em números e rótulos curtos em maiúsculas com espaçamento expandido.
3. **Superfícies em Camadas e Ergonometria Visual**:
   - Cantos arredondados modernos (8px em painéis e KPIs, 12px em cartões de catálogo e modais).
   - Sombras atmosféricas suaves em camadas (`--prime-shadow-xs` a `--prime-shadow-lg`), eliminando o aspecto de bordas duras artificiais.
4. **Semântica Analítica Refinada**:
   - Verde esmeralda suave (`#059669` / `#ecfdf5`) para retenção, metas e fechamento.
   - Carmesim Claro Ruby (`#e11d48` / `#fff1f2`) para churn e desvios críticos.
   - Âmbar corporativo (`#d97706` / `#fffbeb`) para safras imaturas e dados parciais.
   - Azul corporativo (`#2563eb` / `#eff6ff`) para contratos ativos e foco analítico.
5. **Zero Dependências Externas (Self-Contained)**:
   - Mantém 100% da premissa arquitetural do PEP HUB: CSS puro Vanilla sem Tailwind, React ou bibliotecas pesadas de terceiros.

---

## 2. Tokens de Design (CSS Custom Properties)

A folha de estilos unificada fica localizada em `/css/pephub-prime.css` e padroniza as seguintes variáveis globais:

### 2.1 Superfícies & Cores Neutras
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-bg` | `#f8fafc` | Fundo geral da página (Slate 50) |
| `--prime-surface` | `#ffffff` | Superfície primária de painéis, tabelas e cartões |
| `--prime-surface-subtle` | `#f1f5f9` | Cabeçalhos de tabelas, drawers e fundos secundários (Slate 100) |
| `--prime-surface-hover` | `#f8fafc` | Estado de hover sutil em linhas de tabelas e botões secundários |
| `--prime-border` | `#e2e8f0` | Bordas estruturais de contorno (Slate 200) |
| `--prime-border-subtle` | `#f1f5f9` | Divisórias internas discretas |
| `--prime-border-hover` | `#cbd5e1` | Bordas ao passar o mouse ou receber foco |

### 2.2 Tipografia & Tinta (Slate Neutral)
| Token | Valor Hex | Finalidade |
| :--- | :--- | :--- |
| `--prime-ink-primary` | `#0f172a` | Texto principal, títulos e valores de destaque (Slate 900) |
| `--prime-ink-secondary` | `#475569` | Rótulos de KPI, subtítulos e dados auxiliares (Slate 600) |
| `--prime-ink-muted` | `#94a3b8` | Placeholders, notas técnicas e legendas (Slate 400) |
| `--prime-ink-inverse` | `#ffffff` | Textos claros sobre superfícies escuras |

### 2.3 Identidade da Marca Claro Prime
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-brand` | `#e11d48` | Claro Ruby / Rose 600 corporativo |
| `--prime-brand-hover` | `#be123c` | Estado de hover em botões primários e interações |
| `--prime-brand-glow` | `rgba(225, 29, 72, 0.16)` | Halo luminoso sutil em foco de inputs e botões |
| `--prime-hd-bg` | `linear-gradient(...)` | Obsidian degradê (`#0b0f19` a `#270c14`) |
| `--prime-hd-accent` | `linear-gradient(...)` | Friso linear rubi (`#e11d48` a `#fb7185`) |
| `--prime-hd-sub-bg` | `#090d16` | Fundo obsidian sólido da barra de metadados |

### 2.4 Elevações & Sombras
| Token | Valor CSS | Aplicação |
| :--- | :--- | :--- |
| `--prime-shadow-xs` | `0 1px 2px 0 rgba(15, 23, 42, 0.04)` | Chips e botões pequenos |
| `--prime-shadow-sm` | `0 1px 3px 0 rgba(15, 23, 42, 0.06)` | Painéis e cartões em repouso |
| `--prime-shadow-md` | `0 4px 6px -1px rgba(15, 23, 42, 0.06)` | Cartões ao passar o mouse |
| `--prime-shadow-lg` | `0 10px 15px -3px rgba(15, 23, 42, 0.06)` | Tooltips flutuantes e menus |
| `--prime-shadow-modal`| `0 25px 50px -12px rgba(15, 23, 42, 0.28)` | Janelas modais e diálogos |

---

## 3. Especificação de Componentes

### 3.1 Cabeçalho Institucional Obsidian & Ruby
- **Faixa Principal (`.hd-bar`)**:
  - Fundo em degradê escuro acetinado: `linear-gradient(135deg, #0b0f19 0%, #151120 40%, #270c14 85%, #350812 100%)`.
  - Friso inferior acentuado de 2px com gradiente carmesim ruby.
  - Ícone de marca circular com efeito glassmorphism (`backdrop-filter: blur(4px); border: 1.5px solid rgba(255,255,255,0.28)`).
  - Título principal com tipografia estilizada (`font-weight: 800` com preenchimento gradiente suave e complemento institucional claro).
- **Sub-barra de Metadados (`.hd-sub`)**:
  - Fundo `#090d16`, texto `#94a3b8`, separadores circulares sutis.
  - Botões de navegação (`.btn-nav-catalog`, `.hd-btn`) com acabamento translúcido e raio de 8px.

### 3.2 Painéis Analíticos (`.panel`)
- Fundo `#ffffff`, borda sólida `1px solid var(--prime-border)`, raio de curvatura `8px` e sombra `var(--prime-shadow-sm)`.
- Cabeçalho `h2` integrado com título em maiúsculas (`letter-spacing: 0.02em`), nota complementar e botão de ajuda `?` (`.hlp`) moderno e circular.

### 3.3 Cartões de KPI (`.kpis` e `.kpi`)
- Grid responsivo flexível sem bordas externas brutas.
- Cartões com padding ergonômico (14px 18px), raio de 8px e hover lift sutil (`transform: translateY(-2px)`).
- Rótulo superior curto em maiúsculas (`.k`).
- Valor em destaque (`.v`) com 26px, peso 800 e `font-variant-numeric: tabular-nums`.
- Linha de detalhamento (`.d`) com micro-pills arredondados (`.tag-pos`, `.tag-neg`, `.pc`) contendo bordas suaves e fundos em tom pastel.

### 3.4 Tabelas Analíticas Executivas
- Cabeçalhos `th` com `position: sticky; top: 0`, fundo `var(--prime-surface-subtle)` e tipografia maiúscula com espaçamento expandido.
- Células `td` com espaçamento arejado, alinhamento tabular e transição suave no hover (`rgba(241, 245, 249, 0.8)`).
- Rodapé de totais `tfoot` demarcado com borda superior dupla elegante e texto em peso 700.

### 3.5 Gaveta de Filtros Retrátil & Chips
- Drawer integrado com botão estilizado `.drawer-btn`.
- Chips de filtros ativos arredondados (`border-radius: 9999px`) com botão de descarte rápido (`×`).
- Caixas de dimensões (`.filter-box`) com cabeçalho limpo, campo de busca com borda de foco suave ruby e scroll interno refinado.

### 3.6 Janelas Modais & Tooltips
- Modais com backdrop blur escuro (`rgba(15, 23, 42, 0.6)`), cantos de 12px e cabeçalho obsidian integrado.
- Tooltips flutuantes (`.gtip`) com fundo obsidian puro (`#0f172a`), borda fina translúcida e desfoque nativo, evitando oclusão agressiva.

### 3.7 Catálogo Principal & Módulos Administrativos
- Cartões de relatórios no portal com elevação em camadas e transições em curva de aceleração cúbica (`cubic-bezier(0.16, 1, 0.3, 1)`).
- Painel Administrativo com pilares de navegação modernos (`.nav-pillars-wrap`), badges circulares e tabelas de governança alinhadas à nova identidade.
- Telas de Autenticação (Login, Registro e Recuperação) com canvas institucional obsidian e harmonia de acentos ruby.

---

## 4. Matriz Comparativa: Padrão Anterior vs PEP HUB PRIME

| Aspecto | Padrão Anterior (2024) | PEP HUB PRIME (2026) |
| :--- | :--- | :--- |
| **Fundo Geral** | Cinza chapado `#f4f5f7` | Slate repousante `#f8fafc` |
| **Cabeçalho** | Gradiente saturado vermelho-amarelo | Obsidian acetinado com friso Claro Ruby |
| **Raios de Canto** | 3px / 4px (muito rígido) | 8px (painéis/KPIs) / 12px (modais/cards) |
| **Sombras** | Praticamente nulas ou duras | Sistema em camadas (`xs`, `sm`, `md`, `lg`) |
| **KPIs** | Cartões simples com bordas rígidas | Cards modernos com micro-pills e hover lift |
| **Tabelas** | Linhas condensadas, hover cinza escuro | Cabeçalho slate-100, hover suave, tabular-nums |
| **Filtros e Chips** | Tags retangulares simples | Chips em pílula com remoção suave |
| **Modais** | Telas clássicas sem blur | Glassmorphism com cabeçalho obsidian |
| **Integração** | Estilos espalhados em cada HTML | Arquivo mestre centralizado `/css/pephub-prime.css` |

---

## 5. Roteiro para Atualização Futura das Skills de Layout

Se o modelo PEP HUB PRIME for homologado pelo usuário, os seguintes agentes de auditoria deverão ser atualizados:

1. **`layout-checker` (`.agents/skills/layout-checker/SKILL.md`)**:
   - Atualizar a verificação de paleta de cores para aceitar os tokens `--prime-*`.
   - Considerar a faixa Obsidian & Ruby (`linear-gradient(135deg, #0b0f19 ... #270c14)`) como o padrão oficial de cabeçalho.
   - Validar raios ergonômicos de 8px e 12px como conformes.
2. **`reports-quality-auditor` (`.agents/skills/reports-quality-auditor/SKILL.md`)**:
   - Incluir checagem da presença da tag `<link rel="stylesheet" href="/css/pephub-prime.css">` antes de `</head>`.
3. **`architecture-sanitizer` (`.agents/skills/architecture-sanitizer/SKILL.md`)**:
   - Validar a conformidade cruzada do CSS global e a ausência de bibliotecas externas.

---

*Fim da documentação oficial da nova identidade visual PEP HUB PRIME.*
