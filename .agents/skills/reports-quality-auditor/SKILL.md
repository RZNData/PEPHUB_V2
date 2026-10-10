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
