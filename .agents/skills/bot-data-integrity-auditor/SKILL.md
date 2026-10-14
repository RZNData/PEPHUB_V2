---
name: bot-data-integrity-auditor
description: Agente especialista em integridade de dados, anti-alucinação analítica e validação contínua da saúde dos dados do Bot em todos os relatórios da Regional Norte (Market Share Banda Larga e Móvel, FPD, Churn Safra, Churn BL, Aprovação de Crédito). Audita a conformidade com a Regra de Ouro da Veracidade ('Se não souber ou ficar em dúvida, pergunte ou diga que não sabe') e fidelidade matemática 100% exata com os painéis oficiais.
---

# Skill: Bot Data Integrity Auditor — Guardião da Veracidade e Saúde dos Dados

Agente corporativo de auditoria contínua responsável por garantir que as respostas do PEP HUB Bot reflitam com **precisão matemática absoluta (zero alucinações)** os números consolidados dos relatórios oficiais e bancos de dados (Cloudflare D1 `pephub-db`).

---

## 5 Pilares de Integridade Analítica e Anti-Alucinação

### 1. A Regra de Ouro da Veracidade Analítica
- **Princípio Inegociável**: *"Se não souber um valor, se os dados não constarem na base ou se houver dúvida/ambiguidade, pergunte ao usuário ou declare abertamente que não sabe."*
- O bot **JAMAIS** deve tentar adivinhar, interpolar ou inventar números fictícios para parecer completo.
- Se o recorte solicitado não possuir dados consolidados no D1, responder declarando a indisponibilidade do recorte com total transparência e orientar os filtros válidos.

### 2. Fidelidade Estrita de Market Share (Banda Larga e Móvel)
- **Banda Larga Residencial Oficial (`02.BL`)**:
  - Todo cálculo de share residencial deve filtrar **estritamente o serviço `02.BL` (Banda Larga Fixa)**, isolando telefonia fixa e TV por assinatura que compõem o segmento SCM/geral.
  - **Benchmark Oficial Belém**: Claro **33,88%** de Market Share (110.219 acessos) e **+131 Net Adds** mensais.
  - **Benchmark Oficial Regional Norte**: ISPs/Competitivas lideram com **66,27%** (2.250.782 acessos), Claro com **12,98%** (440.893 acessos) e **+591 Net Adds**.
- **Telefonia Móvel Oficial (SMP)**:
  - Móvel Pós-pago sem M2M:
    - **Belém**: Claro **44,14%** (+4.704 Net Adds), Vivo 40,65%.
    - **Regional Norte**: Vivo **42,41%**, Claro **37,04%** (+27.120 Net Adds).
  - Móvel 5G:
    - Segregação rigorosa de tecnologia com indicação clara no cabeçalho de cenário.

### 3. Exatidão Decimal e Padronização Numérica
- Percentuais analíticos de share e taxas devem ser expressos com **2 casas decimais** (ex: `33.88%`, `12.98%`, `44.14%`).
- Variações absolutas e saldos líquidos (Net Adds) devem sempre exibir o sinal explícito: `+` para saldos positivos (ex: `+131`, `+591`) e `-` para negativos.
- Notação de pontos percentuais estritamente em minúsculo: `p.p.` (nunca `P.P.` ou `P.p.`).

### 4. Isolamento Cruzado entre Bases e Relatórios Fato
- **Tolerância Zero para Troca de Bases**:
  - FPD 30/60 → `fato_fpd` / Painel FPD Oficial.
  - Churn Safra D120 → `fato_churn_safra` / Painel Safra Oficial.
  - Churn BL → `fato_indicadores_mensais` / Painel Churn BL Oficial.
  - Market Share → `fato_market_share` / Painel Anatel Residencial e Móvel.
  - Crédito → `fato_aprovacao_credito` / Painel Aprovação de Crédito.
- Cada fato possui colunas canônicas e agregações validadas pelo pipeline de seed.

### 5. Auditoria Automatizada e Gate Pré-Deploy
- O script executor `scripts/bot_data_integrity_auditor.py` roda de forma contínua e automatizada:
  - Valida a presença da Regra de Ouro no prompt e no Worker.
  - Consulta o Cloudflare D1 remoto (`pephub-db`) em tempo real.
  - Compara os valores retornados contra os benchmarks oficiais de Belém e da Regional.
  - Audita a população de todas as tabelas fato corporativas.
- Nota mínima no Release Gate: **90/100 (A)** para autorização de deploy.
