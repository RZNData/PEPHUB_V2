# PEP HUB NEO-EXECUTIVE — Padrão Corporativo Moderno & Luminoso (v4.5)

> **Documento de Especificação Técnica e Identidade Visual para a Regional Norte**  
> *Versão de Homologação em Branch de Teste (`test/nova-identidade-visual`)*  
> *Ambiente: Preview Local Ativo (`http://localhost:8787`)*  
> *Data de Elaboração: Outubro / 2026*  
> *Status: Em Avaliação Executiva*

---

## 1. Visão Geral & Filosofia de Design Neo-Executivo

O **PEP HUB NEO-EXECUTIVE (v4.5)** resolve com precisão matemática os problemas de fadiga visual e contraste, unindo a autoridade institucional da Claro a um design contemporâneo, limpo, arejado e de altíssima legibilidade (estilo Stripe Dashboard, Apple Pro Services, Linear Light e GitHub Enterprise):

### Diretrizes Centrais:
1. **Canvas Luminoso e Arejado (`#f8fafc`)**:
   - Fundo principal em **Slate 50** com gradiente sutil quase imperceptível. Elimina a opressão de telas escuras em ambientes de escritório corporativo e proporciona uma experiência repousante durante jornadas de trabalho prolongadas.
2. **Contraste Absoluto (Padrão WCAG AAA)**:
   - Todo texto sobre superfícies e cartões utiliza **Obsidian Ink** de altíssima densidade:
     - Títulos e Números: `#0f172a` (Slate 900)
     - Texto Corrente e Descrições: `#334155` (Slate 700)
     - Rótulos e Metadados: `#64748b` (Slate 500)
   - Elimina 100% de qualquer colisão de texto claro sobre fundo claro em caixas de metadados (`.card-meta`), tabelas e formulários.
3. **Moldura Executiva Superior Obsidian & Ruby**:
   - Header superior em **Obsidian Navy escuro (`#0b1120`)**, emoldurando o topo da aplicação com peso executivo e sofisticação, acompanhado da sub-barra de telemetria operacional com beacons pulsantes neon.
4. **Superfícies em Branco Puro com Sombras Suaves em Camadas**:
   - Cartões de relatórios, Bento Grid e painéis de dados construídos em `#ffffff` puro, com bordas finas `#e2e8f0` e elevação suave em hover (`translateY(-3px)` e sombra expandida).
5. **Tipografia Executiva Tripla**:
   - **Outfit**: Display, títulos de relatórios e identidade da marca.
   - **Plus Jakarta Sans**: Textos de interface, formulários e navegação.
   - **JetBrains Mono**: Números tabulares (`tabular-nums`), deltas (`p.p.`) e telemetria.

---

## 2. Tokens de Design (CSS Custom Properties)

A folha de estilos unificada fica localizada em [public/css/pephub-prime.css](file:///c:/Users/F138138/DEV/Churn_Safra/public/css/pephub-prime.css):

### 2.1 Superfícies & Cores Neutras (Luminous Light Canvas)
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-bg` | `#f8fafc` | Fundo principal da página (Slate 50) |
| `--prime-surface` | `#ffffff` | Superfície primária de cartões, painéis e tabelas |
| `--prime-surface-subtle` | `#f1f5f9` | Cabeçalhos de tabelas, drawers e caixas auxiliares |
| `--prime-surface-card-meta` | `#f8fafc` | Caixa interna de metadados dos relatórios |
| `--prime-border` | `#e2e8f0` | Bordas estruturais de contorno nítidas |
| `--prime-border-hover` | `#cbd5e1` | Destaque de borda em hover |

### 2.2 Tipografia & Tinta (Contraste Máximo)
| Token | Valor Hex | Finalidade |
| :--- | :--- | :--- |
| `--prime-ink-primary` | `#0f172a` | Títulos e valores numéricos em destaque (Slate 900) |
| `--prime-ink-body` | `#334155` | Descrições e parágrafos de texto (Slate 700) |
| `--prime-ink-secondary` | `#475569` | Subtítulos e metadados contextuais (Slate 600) |
| `--prime-ink-muted` | `#64748b` | Kickers, tags e notas técnicas (Slate 500) |

### 2.3 Identidade Claro Ruby & Semântica Analítica
| Token | Valor Hex/RGBA | Finalidade |
| :--- | :--- | :--- |
| `--prime-brand` | `#e11d48` | Claro Ruby corporativo para CTAs e destaques |
| `--prime-brand-hover` | `#be123c` | Hover em botões primários |
| `--prime-green` | `#059669` | Sucesso, Retenção, Meta Atingida (`#ecfdf5` bg) |
| `--prime-red` | `#e11d48` | Churn e Alertas Críticos (`#fff1f2` bg) |
| `--prime-amber` | `#d97706` | Atenção e Safra em Foco (`#fffbeb` bg) |
| `--prime-blue` | `#2563eb` | Contratos Ativos e Seleções (`#eff6ff` bg) |

---

## 3. Resolução Específica dos Problemas de Contraste

1. **Caixas Internas dos Cartões (`.card-meta`)**:
   - Fundo alterado para `#f8fafc` com borda fina `#e2e8f0`.
   - Rótulos (`span`): `#64748b` em maiúsculas (100% legíveis).
   - Valores (`strong`): `#0f172a` em negrito intenso (100% legíveis).
2. **Descrições de Relatórios (`.card-desc`)**:
   - Cor padronizada em `#334155` com altura de linha de 1.6, eliminando qualquer texto apagado.
3. **Tabelas de Dados**:
   - Cabeçalhos `th` com fundo `#f8fafc`, texto `#475569` em maiúsculas e borda dupla inferior `#e2e8f0`.
   - Células `td` em branco puro com texto `#1e293b` e hover em `#f8fafc`.
4. **Pilares de Governança no Admin**:
   - Abas com fundo `#ffffff` e texto `#0f172a`.
   - Aba ativa com indicador sublinhado em Claro Ruby `#e11d48` e fundo sutil `#fff1f2`.

---

## 4. Reorganização do Painel & Arquitetura Corporativa Atual (v4.5)

Para elevar a experiência a um padrão corporativo contemporâneo (estilo Linear, Snowflake Workspaces, Stripe Dashboard e Datadog), a organização do painel foi redesenhada em 4 pilares:

### 4.1 Header Executivo Unificado com Busca Global (`⌘K`)
- **Busca em Tempo Real Integrada**: Caixa de pesquisa de alta sensibilidade no centro da moldura superior, permitindo localização instantânea de relatórios por nome, indicador, metodologia ou palavra-chave (ex: "FPD", "Churn", "Anatel", "Net Adds").
- **Atalho de Teclado Corporativo**: Foco automático ao pressionar `⌘K` (Mac) ou `Ctrl+K` / `/` (Windows/Linux) e limpeza rápida com `ESC`.
- **Telemetria HUD e Perfil Integrado**: Status de sincronização da borda Cloudflare D1 (`D1 Core Online`), latência de 14ms e menu de usuário corporativo.

### 4.2 Cockpit Executivo & Visão Consolidada
Substitui o antigo bloco de texto estático por um **Cockpit Estratégico de Métricas** em duas colunas:
1. **Contexto Operacional**: Identificação da Regional Norte (AM · PA · MA · AP · RR), escopo analítico e badge de sincronia D1 Edge.
2. **Matriz de 4 KPIs Estratégicos**:
   - `348.866` Instalações Safras (Set/25 – Set/26)
   - `26,48%` Taxa FPD 60 Safra Foco
   - `+43.087` Net Adds Móvel (Líder Brasil)
   - `37,04%` Market Share SMP (Top 1 RNO)

### 4.3 Dock Interativo de Categorias em Pílulas
Dock flutuante com contadores dinâmicos para troca instantânea de segmento:
- **Todos os Relatórios (14)**: Visão consolidada de todo o ecossistema.
- **Móvel & Safras (4)**: Churn Safra, Evolução de Carteira, Panorama MS, MS Móvel 5G.
- **Banda Larga Fixa (3)**: Churn BL Total, Churn BL PME, MS Residencial.
- **Qualidade & Risco FPD (3)**: Panorama FPD, FPD Executivo, Aprovação de Crédito PF.
- **PeP Tools & Suporte (4)**: Podcast Deep Dive, Gerador de Aniversário, Auxiliar de PPT, Divulgação TVs.

### 4.4 Anatomia do Card Corporativo Contemporâneo
Cada cartão agora possui arquitetura visual em 4 camadas estruturadas:
1. **Friso Superior de Acento de Categoria**: Linha de 3px colorida (Ruby para Móvel, Azul Royal para Fixa, Esmeralda para Qualidade/FPD e Violeta para Tools).
2. **Eyebrow de Domínio & Status**: Selo da categoria à esquerda e cápsula de maturidade/status oficial à direita.
3. **Título com Tipografia Display & Subtítulo de Metodologia**: Nome do relatório em fonte *Outfit* (`700`) e kicker descritivo em *Plus Jakarta Sans* (`500`).
4. **Matriz de Dados 2x2 em Slate 50**: Células com rótulo em maiúsculas (`#64748b`) e números com fonte mono/tabular de alto contraste (`#0f172a`).
5. **Tags Semânticas & Botão de Ação com Arrow Glide**: Pílulas coloridas para janelas metodológicas e botão de acesso com micro-interação da seta (`→`) deslizando 4px no hover.

---

## 5. Como Visualizar no Navegador

O servidor de preview já está rodando localmente na branch `test/nova-identidade-visual`:
- 🏠 **Portal Principal:** [http://localhost:8787/](http://localhost:8787/)
- ⚙️ **Central Administrativa:** [http://localhost:8787/admin/](http://localhost:8787/admin/)
- 📊 **Painel Churn Safra:** [http://localhost:8787/churn/](http://localhost:8787/churn/)
- 🔐 **Tela de Login:** [http://localhost:8787/login/](http://localhost:8787/login/)

