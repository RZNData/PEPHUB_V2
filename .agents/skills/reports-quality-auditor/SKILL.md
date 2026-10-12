---
name: reports-quality-auditor
description: Agente especialista em qualidade técnica, integridade analítica e conformidade de dados para todos os relatórios do PEP HUB (FPD, Churn Safra, Churn BL, Market Share). Audita subtotais em linhas agrupadoras, alinhamento numérico à direita, notação 'p.p.' estritamente em minúsculo, layout rígido de colunas, filtros dependentes, reatividade de benchmark e zero dependências externas.
---

# Skill: Reports Quality Auditor — Agente Universal de Qualidade de Relatórios v1.0

Agente corporativo especializado em garantir a integridade analítica, padronização de dados e excelência visual de todos os relatórios e painéis analíticos do PEP HUB da Regional Norte.

---

## 7 Pilares Universais de Qualidade de Relatórios

### 1. Subtotais e Agregações em Linhas Agrupadoras
- **Regra**: Em todas as visões (visão geral, abas de canais ou visões detalhadas 1 a 6), linhas de agrupamento (ex: *Grandes Mercados*, *Mercados em Desenvolvimento*, *Sem Cabo*, *Canais Presenciais*, *Canais Remotos*, *Outros*) **DEVEM conter dados calculados e preenchidos**.
- **Proibição**: Nenhuma linha agrupadora pode ficar vazia, com hífen ou com células em branco nas colunas de métrica foco e histórico.
- **Validação**: Linhas com classe `.grp-header`, `.grp-header-sub`, `.grp-total-row` devem calcular a agregação real de suas entidades filhas.

### 2. Alinhamento Numérico Estrito à Direita
- **Regra**: Todo dado quantitativo (taxas percentuais, volumes, instalações, churn, aging, variações MoM e YoY) deve ser alinhado à direita (`text-align: right`).
- **Exceção**: Apenas a coluna de identificação/rótulo (nome da praça, canal, parceiro) possui alinhamento à esquerda (`td.l`, `th.l`).
- **Atenção Especial**: Linhas de subtotais e agrupamentos (`.grp-total-row td`, `.grp-header td`) não podem ter valores numéricos centralizados ou à esquerda.

### 3. Notação de Variação em Pontos Percentuais Estritamente em Minúsculo (`p.p.`)
- **Regra**: Indicadores de variação percentual devem grafar `p.p.` estritamente em letras minúsculas (ex: `+0,45 p.p.`, `-1,20 p.p.`, `0,00 p.p.`).
- **Proibição**: Jamais usar maiúsculas como `P.P.`, `P.p.`, `PP` ou `Pp`.
- **CSS / JS**: Forçar no CSS `.d-val { text-transform: lowercase !important; }` e nos formatadores JS `${val.toFixed(2)} p.p.`.

### 4. Layout Fixo de Colunas e Alinhamento com Benchmark (`table-layout: fixed`)
- **Regra**: Tabelas analíticas devem utilizar `table-layout: fixed` com larguras rígidas para colunas de ranking, nome, métrica foco, deltas MoM/YoY e histórico mensal.
- **Correspondência**: Em relatórios comparativos (ex: Tabela Regional e Tabela Benchmark Brasil), as larguras de colunas devem ser milimetricamente idênticas para que a leitura vertical seja perfeita e os dados não sofram deslocamento lateral.

### 5. Filtros Dependentes Inteligentes com Ordenação
- **Regra**: Filtros de seleção múltipla (cidade, canal, subcanal, empresa, produto, multi) devem ser interdependentes.
- **Comportamento**: Itens sem dados no recorte atual devem ser movidos para o fim da lista e destacados com a classe `.na` (cinza / desabilitado), mantendo no topo as opções com volumetria ativa.

### 6. Benchmark Nacional Reativo e Filtros Travados
- **Regra**: O benchmark nacional deve reagir dinamicamente aos filtros permitidos (como combinação de produto e multi), refletindo o valor real do cenário filtrado.
- **Visões Específicas**: Em abas exclusivas de um canal ou modalidade, o seletor correspondente deve ser bloqueado com a classe `.filter-locked` e badge explicativo, impedindo seleção cruzada contraditória.

### 7. Zero Dependências Externas & Performance O(N)
- **Regra**: O relatório HTML deve ser 100% autônomo, sem requisições a CDNs externas (unpkg, cdnjs, google fonts, tailwind).
- **Desempenho**: Operações de filtro e cálculo em cubos de dados devem rodar no navegador em tempo linear O(N), garantindo resposta visual instantânea (<50ms).
- **Segurança**: Resposta com cabeçalhos anti-cache (`no-store, no-cache, must-revalidate`) e proteção estrita de sessão.

### 8. Numeração Sequencial de Indicadores de KPI
- **Regra**: Todo cartão/indicador de KPI em qualquer relatório corporativo deve possuir um prefixo numérico sequencial (`1. `, `2. `, etc.).
- **Objetivo**: Elimina ambiguidades nas reuniões e orientações da liderança executiva quando o gestor solicitar ações específicas sobre determinada métrica.

### 9. Cabeçalho Padronizado e Ausência de Exportação HTML em Relatórios
- **Regra**: Todo cabeçalho de relatório analítico deve conter estritamente o botão "Voltar ao Catálogo" (`.btn-nav-catalog`) e o widget com botão "Sair".
- **Proibição**: Proibido link textual redundante `‹ Portal Pephub` no `.hd-sub` e proibida qualquer opção de "Exportar HTML" ou "Download HTML" nos relatórios (reservadas com exclusividade para telas de admin e gestão).

### 10. Propagação Universal e Reatividade de Filtros em Todas as Tabelas Analíticas
- **Regra**: Todo controle de filtro dimensional (segmento, produto, tendência, mês/ano, regional ou canal) posicionado na barra de controle (`.control-bar`) ou drawer **DEVE propagar suas mudanças dinamicamente para TODAS as tabelas analíticas e visões do relatório**.
- **Comportamento Multidimensional**: Em relatórios com múltiplas abas ou visões (ex: Sumário Executivo, Net Adds Regional, Desdobramento por Segmento, B2B Corporativo, Matriz de Migração):
  - O filtro selecionado deve afetar simultaneamente os KPIs executivos, as linhas e as colunas das tabelas filhas.
  - Visões especializadas (como Matriz de Migração ou B2B) devem filtrar os fluxos/mercados correspondentes ou exibir avisos contextuais claros (`.info-banner`) indicando o recorte ativo e oferecendo atalho de restauração ("Ver Consolidado Geral").
- **Proibição**: Proibido manter tabelas analíticas inertes, órfãs de listeners de alteração ou desconectadas do estado global de filtros (`appState`).
- **Validação**: Auditoria automática verifica a presença de manipuladores reativos e conexão de todas as tabelas analíticas ao motor de filtragem do relatório.

### 11. Separação Dimensional Estrita: Segmento de Mercado vs. Produto / Plataforma
- **Regra**: Filtro de Segmento de Mercado e Filtro de Produto/Plataforma **DEVEM SER RIGOROSAMENTE APARTADOS em seletores independentes**.
- **Proibição**: É expressamente proibido aglutinar "Segmento e Produto" no mesmo elemento `<select>` ou controle dimensional híbrido (ex: rótulos como `SEGMENTO / PRODUTO`).
- **Dimensões Corporativas Padronizadas**:
  - **Segmento**: Consumo Massivo (PF), PME (PE + ME), Grandes Empresas (GE).
  - **Produto**: Controle (AUTOC / CTLFC), Pós-pago / Conta, Flex, Pré-pago.
- **Validação**: Verificação algorítmica barra seletores que misturem palavras-chave de segmento e produto no mesmo seletor ou rótulo.

### 12. Arquitetura e Mecânica de Cards e Filtros Padrão Churn Safra
- **Regra**: Filtros e cartões de KPI devem seguir estritamente o layout, semântica e mecânica do Churn Safra:
  - **Filtros**: Painel `.panel#pnFiltros` contendo grade `.filters-row`, itens `.f` com rótulo em caixa alta e badge `.cnt`, barra `.fbar` com botão `.primary`, reset `.fbtn` e lista de tags interativas `.chips > .chip` (com `×` para remoção instantânea).
  - **Cards de KPI**: Encapsulados dentro de `.panel > h2 Indicadores` em grade contínua `.kpis`, cartões `.kpi` com bordas limpas e sem sombras soltas, rótulo `.k` numerado sequencialmente (`1.`, `2.`...), valor `.v` em 22px tabular-nums e detalhe `.d` em 11px. Cores semânticas obrigatórias: `.acc` (alerta/queda), `.pos` (positivo/adições), `.np` (inadimplência), `.parc` (fundo parcial) e `.pc` (badge parcial).

---

## Como Executar a Auditoria

```bash
# Auditar todos os relatórios do projeto
python scripts/reports_quality_agent.py

# Auditar um relatório específico
python scripts/reports_quality_agent.py public/fpd-residencial/index.html
python scripts/reports_quality_agent.py public/churn/index.html
python scripts/reports_quality_agent.py public/churn-bl-total/index.html
```

---

## Tabela de Pontuação por Severidade (100 pontos base)

| # | Verificação | Severidade | Impacto |
|---|---|---|---|
| 1 | Subtotais preenchidos em linhas agrupadoras | CRITICAL | -25 |
| 2 | Alinhamento numérico à direita em dados e subtotais | ERROR | -15 |
| 3 | Notação 'p.p.' estritamente em minúsculo (sem P.P.) | ERROR | -15 |
| 4 | Largura fixa de colunas e tabela (table-layout: fixed) | WARNING | -10 |
| 5 | Filtros dependentes com reordenação (.na no final) | WARNING | -10 |
| 6 | Benchmark reativo aos filtros aplicáveis | WARNING | -10 |
| 7 | Zero CDNs e dependências externas de terceiros | CRITICAL | -15 |

---

## Escala de Classificação

- **A+ (95–100%)**: Relatório com excelência técnica e visual padrão corporativo.
- **A (85–94%)**: Aprovado para publicação e deploy corporativo.
- **B (70–84%)**: Necessita pequenos ajustes de formatação antes do deploy.
- **C/D (<70%)**: Bloqueado pelo Release Gate.


### Diretriz Dinâmica Incorporada: Numeracao_Sequencial_Indicadores_KPI
- **Regra**: Todos os indicadores e cartoes de KPI devem possuir prefixo numerico sequencial (1., 2., 3...) para identificacao clara e univoca.
- **Registrado em**: 09/10/2026 14:41:38


### Diretriz Dinâmica Incorporada: Propagacao_Universal_Reatividade_Filtros_Tabelas
- **Regra**: Todos os seletores dimensionais em paineis analiticos devem propagar reatividade para 100% das tabelas filhas e visoes, sendo vedadas tabelas inertes ou orfas de filtros.
- **Registrado em**: 12/10/2026 02:16:07


### Diretriz Dinâmica Incorporada: Separacao_Filtros_Segmento_Produto_Cards_Churn_Safra
- **Regra**: Vedado aglutinar Segmento e Produto em um mesmo seletor. Ambos devem ser apartados e independentes. Cards de KPI e painel de filtros devem seguir estritamente o layout e mecânica continua do Churn Safra (.panel#pnFiltros, .filters-row, .kpis, .kpi, .k, .v, .d).
- **Registrado em**: 12/10/2026 02:42:52
