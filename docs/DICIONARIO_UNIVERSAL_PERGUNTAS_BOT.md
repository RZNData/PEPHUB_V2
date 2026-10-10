# Dicionário Universal de Perguntas & Contextos — Pephub Bot RAG

> **Conformidade Executiva**: Todos os relatórios, filtros, métricas e cruzamentos oficiais da Regional Norte.
> **Data de Atualização**: Outubro / 2026 | **Versão**: 3.0

## 1. Princípios de Funcionamento do Bot
- **Gatilho Obrigatório Universal**: Toda e qualquer interação com o Bot no WhatsApp DEVE iniciar obrigatoriamente com o prefixo **`#?`** (ex: `#?`, `#? 1`, `#? 2`, `#? como está Manaus?`). Mensagens que não iniciarem com `#?` são sumariamente ignoradas para proteger a privacidade de conversas pessoais e não gerar ruído em grupos.
- **Fluxo Guiado Numérico (Rota A — Sequência em 2 Passos)**:
  - **Passo 1/2 (Seleção da Base)**:
    - O bot pergunta qual base deseja consultar e apresenta as 5 bases oficiais (1. FPD, 2. Churn Banda Larga, 3. Churn Safra D120, 4. Aprovação de Crédito, 5. Market Share Anatel) com links clicáveis `wa.me` já preenchidos com `#? 1` a `#? 5`.
  - **Passo 2/2 (Seleção da Visão Analítica)**:
    - O bot pergunta o que o usuário deseja ver da base selecionada, oferecendo 7 opções padronizadas:
      - `1` ➔ **Valor mais recente**
      - `2` ➔ **Ranking Piores Parceiros**
      - `3` ➔ **Ranking Melhores Parceiros**
      - `4` ➔ **Ranking de Cidades**
      - `5` ➔ **Ranking de Produto**
      - `6` ➔ **Ranking Vendedor (Canal / PDV)**
      - `7` ➔ **Resumo Regional Norte**
      - `0` ➔ **Voltar ao menu de bases (Passo 1)**
  - **Navegação Contínua**: Em qualquer resposta analítica, o bot permite navegar diretamente entre outras visões (`#? 1` a `#? 7`) ou retornar à troca de base (`#? 0`).
- **Métrica Padrão de FPD**: FPD 60 (`taxa_fpd60`). FPD 30 somente quando solicitado explicitamente.
- **Última Safra de FPD**: **mai/26** (resolvida cronologicamente por `safra_ord DESC`).
- **FPD de Parceiros**: Consultada em `fato_churn_safra` (`visao = 'PARCEIRO'`), avaliando `taxa_d30` e `taxa_np120` na safra madura com mínimo de 30 instalações.
- **Consultas Livres**: Caso o usuário envie perguntas analíticas abertas (ex: `#? qual o FPD de Manaus?`), o Text-to-SQL + Semantic RAG processa e responde diretamente.

## 2.1 FPD (First Payment Default & Qualidade de Venda)

| Propriedade | Valor Oficial |
| :--- | :--- |
| **Tabela D1** | `fato_fpd` |
| **Métrica Padrão** | **FPD 60** (`taxa_fpd60`) |
| **Coluna de Ordenação Temporal** | `safra_ord` |

### Perguntas Suportadas e Padrões de Resposta

| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |
| :--- | :--- | :--- | :--- |
| Período e Safras | *"Qual a última safra de FPD?"* | `SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1` | Safra mais recente consolidada (mai/26) |
| Período e Safras | *"Quais safras estão disponíveis em FPD?"* | `SELECT DISTINCT safra FROM fato_fpd ORDER BY safra_ord DESC` | Lista das safras disponíveis |
| Rankings e Extremos | *"Quem tem o pior FPD 60?"* | `SELECT cidade, taxa_fpd60 FROM fato_fpd ORDER BY taxa_fpd60 DESC LIMIT 5` | Ranking com as 5 piores entidades/cidades no indicador padrão |
| Rankings e Extremos | *"Quem tem o melhor FPD 60?"* | `SELECT cidade, taxa_fpd60 FROM fato_fpd ORDER BY taxa_fpd60 ASC LIMIT 5` | Ranking com as 5 melhores entidades/cidades |
| Filtro por Cidade | *"Qual o FPD 60 de Belém?"* | `SELECT safra, cidade, taxa_fpd60 FROM fato_fpd WHERE cidade LIKE '%Belém%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para Belém no período mais recente |
| Filtro por Cidade | *"Qual o FPD 60 de Manaus?"* | `SELECT safra, cidade, taxa_fpd60 FROM fato_fpd WHERE cidade LIKE '%Manaus%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para Manaus no período mais recente |
| Filtro por Cidade | *"Qual o FPD 60 de São Luís?"* | `SELECT safra, cidade, taxa_fpd60 FROM fato_fpd WHERE cidade LIKE '%São Luís%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para São Luís no período mais recente |
| Filtro por Canal de Venda | *"Qual o FPD 60 de PAP?"* | `SELECT safra, canal, taxa_fpd60 FROM fato_fpd WHERE canal LIKE '%PAP%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para PAP no período mais recente |
| Filtro por Canal de Venda | *"Qual o FPD 60 de Lojas?"* | `SELECT safra, canal, taxa_fpd60 FROM fato_fpd WHERE canal LIKE '%Lojas%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para Lojas no período mais recente |
| Filtro por Canal de Venda | *"Qual o FPD 60 de Televendas?"* | `SELECT safra, canal, taxa_fpd60 FROM fato_fpd WHERE canal LIKE '%Televendas%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para Televendas no período mais recente |
| Filtro por Faixa de Risco | *"Qual o FPD 60 de BAIXO?"* | `SELECT safra, faixa_risco, taxa_fpd60 FROM fato_fpd WHERE faixa_risco LIKE '%BAIXO%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para BAIXO no período mais recente |
| Filtro por Faixa de Risco | *"Qual o FPD 60 de MEDIO?"* | `SELECT safra, faixa_risco, taxa_fpd60 FROM fato_fpd WHERE faixa_risco LIKE '%MEDIO%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para MEDIO no período mais recente |
| Filtro por Faixa de Risco | *"Qual o FPD 60 de ALTO?"* | `SELECT safra, faixa_risco, taxa_fpd60 FROM fato_fpd WHERE faixa_risco LIKE '%ALTO%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para ALTO no período mais recente |
| Filtro por Safra | *"Qual o FPD 60 de mai/26?"* | `SELECT safra, safra, taxa_fpd60 FROM fato_fpd WHERE safra LIKE '%mai/26%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para mai/26 no período mais recente |
| Filtro por Safra | *"Qual o FPD 60 de abr/26?"* | `SELECT safra, safra, taxa_fpd60 FROM fato_fpd WHERE safra LIKE '%abr/26%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para abr/26 no período mais recente |
| Filtro por Safra | *"Qual o FPD 60 de mar/26?"* | `SELECT safra, safra, taxa_fpd60 FROM fato_fpd WHERE safra LIKE '%mar/26%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para mar/26 no período mais recente |
| Parceiros de Venda | *"Qual o parceiro com pior FPD?"* | `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 30 ORDER BY safra_ord DESC, taxa_d30 DESC LIMIT 5` | Ranking de parceiros com maior perda de 1º pagamento (Taxa D30) e estorno (NP120) com volume mínimo de 30 instalações |
| Parceiros de Venda | *"Qual o FPD do parceiro TEL CENTRO DE CONTATOS LTDA?"* | `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND entidade_nome LIKE '%TEL CENTRO DE CONTATOS LTDA%' ORDER BY safra_ord DESC LIMIT 1` | Desempenho de 1º pagamento e estorno do parceiro TEL CENTRO DE CONTATOS LTDA |
| Parceiros de Venda | *"Qual o FPD do parceiro HITSS DO BRASIL SERVICOS TECNOLOGICOS LTDA?"* | `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND entidade_nome LIKE '%HITSS DO BRASIL SERVICOS TECNOLOGICOS LTDA%' ORDER BY safra_ord DESC LIMIT 1` | Desempenho de 1º pagamento e estorno do parceiro HITSS DO BRASIL SERVICOS TECNOLOGICOS LTDA |
| Parceiros de Venda | *"Qual o FPD do parceiro PRUDENTE SOLUCOES E INTERMEDIACAO LTDA?"* | `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND entidade_nome LIKE '%PRUDENTE SOLUCOES E INTERMEDIACAO LTDA%' ORDER BY safra_ord DESC LIMIT 1` | Desempenho de 1º pagamento e estorno do parceiro PRUDENTE SOLUCOES E INTERMEDIACAO LTDA |

## 2.2 Churn Banda Larga Total & PME

| Propriedade | Valor Oficial |
| :--- | :--- |
| **Tabela D1** | `fato_indicadores_mensais` |
| **Métrica Padrão** | **Taxa de Churn Real** (`taxa_real`) |
| **Coluna de Ordenação Temporal** | `mes_referencia` |

### Perguntas Suportadas e Padrões de Resposta

| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |
| :--- | :--- | :--- | :--- |
| Período e Safras | *"Qual a última safra de Churn?"* | `SELECT DISTINCT mes_referencia, mes_referencia FROM fato_indicadores_mensais ORDER BY mes_referencia DESC LIMIT 1` | Safra mais recente consolidada (Setembro / 2026) |
| Período e Safras | *"Quais safras estão disponíveis em Churn?"* | `SELECT DISTINCT mes_referencia FROM fato_indicadores_mensais ORDER BY mes_referencia DESC` | Lista das safras disponíveis |
| Rankings e Extremos | *"Quem tem o pior Taxa de Churn Real?"* | `SELECT cidade, taxa_real FROM fato_indicadores_mensais ORDER BY taxa_real DESC LIMIT 5` | Ranking com as 5 piores entidades/cidades no indicador padrão |
| Rankings e Extremos | *"Quem tem o melhor Taxa de Churn Real?"* | `SELECT cidade, taxa_real FROM fato_indicadores_mensais ORDER BY taxa_real ASC LIMIT 5` | Ranking com as 5 melhores entidades/cidades |
| Filtro por Segmento | *"Qual o Taxa de Churn Real de Banda Larga Total?"* | `SELECT mes_referencia, segmento, taxa_real FROM fato_indicadores_mensais WHERE segmento LIKE '%Banda Larga Total%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Banda Larga Total no período mais recente |
| Filtro por Segmento | *"Qual o Taxa de Churn Real de Banda Larga PME?"* | `SELECT mes_referencia, segmento, taxa_real FROM fato_indicadores_mensais WHERE segmento LIKE '%Banda Larga PME%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Banda Larga PME no período mais recente |
| Filtro por Tipo de Visão | *"Qual o Taxa de Churn Real de TOTAL?"* | `SELECT mes_referencia, tipo_visao, taxa_real FROM fato_indicadores_mensais WHERE tipo_visao LIKE '%TOTAL%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para TOTAL no período mais recente |
| Filtro por Tipo de Visão | *"Qual o Taxa de Churn Real de VOLUNTARIO?"* | `SELECT mes_referencia, tipo_visao, taxa_real FROM fato_indicadores_mensais WHERE tipo_visao LIKE '%VOLUNTARIO%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para VOLUNTARIO no período mais recente |
| Filtro por Tipo de Visão | *"Qual o Taxa de Churn Real de INVOLUNTARIO?"* | `SELECT mes_referencia, tipo_visao, taxa_real FROM fato_indicadores_mensais WHERE tipo_visao LIKE '%INVOLUNTARIO%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para INVOLUNTARIO no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Churn Real de Regional Norte?"* | `SELECT mes_referencia, cidade, taxa_real FROM fato_indicadores_mensais WHERE cidade LIKE '%Regional Norte%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Regional Norte no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Churn Real de Belém?"* | `SELECT mes_referencia, cidade, taxa_real FROM fato_indicadores_mensais WHERE cidade LIKE '%Belém%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Belém no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Churn Real de Manaus?"* | `SELECT mes_referencia, cidade, taxa_real FROM fato_indicadores_mensais WHERE cidade LIKE '%Manaus%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Manaus no período mais recente |

## 2.3 Churn Safra D120 (Sobrevivência & Estorno)

| Propriedade | Valor Oficial |
| :--- | :--- |
| **Tabela D1** | `fato_churn_safra` |
| **Métrica Padrão** | **Não Pagamento 120 dias (NP120)** (`taxa_np120`) |
| **Coluna de Ordenação Temporal** | `safra_ord` |

### Perguntas Suportadas e Padrões de Resposta

| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |
| :--- | :--- | :--- | :--- |
| Período e Safras | *"Qual a última safra de Churn?"* | `SELECT DISTINCT safra, safra_ord FROM fato_churn_safra ORDER BY safra_ord DESC LIMIT 1` | Safra mais recente consolidada (mai/26) |
| Período e Safras | *"Quais safras estão disponíveis em Churn?"* | `SELECT DISTINCT safra FROM fato_churn_safra ORDER BY safra_ord DESC` | Lista das safras disponíveis |
| Rankings e Extremos | *"Quem tem o pior Não Pagamento 120 dias (NP120)?"* | `SELECT cidade, taxa_np120 FROM fato_churn_safra ORDER BY taxa_np120 DESC LIMIT 5` | Ranking com as 5 piores entidades/cidades no indicador padrão |
| Rankings e Extremos | *"Quem tem o melhor Não Pagamento 120 dias (NP120)?"* | `SELECT cidade, taxa_np120 FROM fato_churn_safra ORDER BY taxa_np120 ASC LIMIT 5` | Ranking com as 5 melhores entidades/cidades |
| Filtro por Visão | *"Qual o Não Pagamento 120 dias (NP120) de PARCEIRO?"* | `SELECT safra, visao, taxa_np120 FROM fato_churn_safra WHERE visao LIKE '%PARCEIRO%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para PARCEIRO no período mais recente |
| Filtro por Visão | *"Qual o Não Pagamento 120 dias (NP120) de CIDADE?"* | `SELECT safra, visao, taxa_np120 FROM fato_churn_safra WHERE visao LIKE '%CIDADE%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para CIDADE no período mais recente |
| Filtro por Visão | *"Qual o Não Pagamento 120 dias (NP120) de REGIONAL?"* | `SELECT safra, visao, taxa_np120 FROM fato_churn_safra WHERE visao LIKE '%REGIONAL%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para REGIONAL no período mais recente |
| Filtro por Parceiro / Cidade | *"Qual o Não Pagamento 120 dias (NP120) de TEL CENTRO DE CONTATOS LTDA?"* | `SELECT safra, entidade_nome, taxa_np120 FROM fato_churn_safra WHERE entidade_nome LIKE '%TEL CENTRO DE CONTATOS LTDA%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para TEL CENTRO DE CONTATOS LTDA no período mais recente |
| Filtro por Parceiro / Cidade | *"Qual o Não Pagamento 120 dias (NP120) de HITSS DO BRASIL?"* | `SELECT safra, entidade_nome, taxa_np120 FROM fato_churn_safra WHERE entidade_nome LIKE '%HITSS DO BRASIL%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para HITSS DO BRASIL no período mais recente |
| Filtro por Parceiro / Cidade | *"Qual o Não Pagamento 120 dias (NP120) de CCH Mendes?"* | `SELECT safra, entidade_nome, taxa_np120 FROM fato_churn_safra WHERE entidade_nome LIKE '%CCH Mendes%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para CCH Mendes no período mais recente |
| Filtro por Status da Safra | *"Qual o Não Pagamento 120 dias (NP120) de MADURA?"* | `SELECT safra, status_safra, taxa_np120 FROM fato_churn_safra WHERE status_safra LIKE '%MADURA%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para MADURA no período mais recente |
| Filtro por Status da Safra | *"Qual o Não Pagamento 120 dias (NP120) de EM_ABERTO?"* | `SELECT safra, status_safra, taxa_np120 FROM fato_churn_safra WHERE status_safra LIKE '%EM_ABERTO%' ORDER BY safra_ord DESC LIMIT 1` | Resultado analítico para EM_ABERTO no período mais recente |

## 2.4 Aprovação de Crédito & Antifraude

| Propriedade | Valor Oficial |
| :--- | :--- |
| **Tabela D1** | `fato_aprovacao_credito` |
| **Métrica Padrão** | **Taxa de Aprovação** (`taxa_aprovacao`) |
| **Coluna de Ordenação Temporal** | `mes_referencia` |

### Perguntas Suportadas e Padrões de Resposta

| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |
| :--- | :--- | :--- | :--- |
| Período e Safras | *"Qual a última safra de Aprovação?"* | `SELECT DISTINCT mes_referencia, mes_referencia FROM fato_aprovacao_credito ORDER BY mes_referencia DESC LIMIT 1` | Safra mais recente consolidada (2026-09) |
| Período e Safras | *"Quais safras estão disponíveis em Aprovação?"* | `SELECT DISTINCT mes_referencia FROM fato_aprovacao_credito ORDER BY mes_referencia DESC` | Lista das safras disponíveis |
| Rankings e Extremos | *"Quem tem o pior Taxa de Aprovação?"* | `SELECT cidade, taxa_aprovacao FROM fato_aprovacao_credito ORDER BY taxa_aprovacao DESC LIMIT 5` | Ranking com as 5 piores entidades/cidades no indicador padrão |
| Rankings e Extremos | *"Quem tem o melhor Taxa de Aprovação?"* | `SELECT cidade, taxa_aprovacao FROM fato_aprovacao_credito ORDER BY taxa_aprovacao ASC LIMIT 5` | Ranking com as 5 melhores entidades/cidades |
| Filtro por Canal | *"Qual o Taxa de Aprovação de Agente Autorizado?"* | `SELECT mes_referencia, canal, taxa_aprovacao FROM fato_aprovacao_credito WHERE canal LIKE '%Agente Autorizado%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Agente Autorizado no período mais recente |
| Filtro por Canal | *"Qual o Taxa de Aprovação de D2D Parceiros?"* | `SELECT mes_referencia, canal, taxa_aprovacao FROM fato_aprovacao_credito WHERE canal LIKE '%D2D Parceiros%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para D2D Parceiros no período mais recente |
| Filtro por Canal | *"Qual o Taxa de Aprovação de Lojas Próprias?"* | `SELECT mes_referencia, canal, taxa_aprovacao FROM fato_aprovacao_credito WHERE canal LIKE '%Lojas Próprias%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Lojas Próprias no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Aprovação de Belém?"* | `SELECT mes_referencia, cidade, taxa_aprovacao FROM fato_aprovacao_credito WHERE cidade LIKE '%Belém%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Belém no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Aprovação de Manaus?"* | `SELECT mes_referencia, cidade, taxa_aprovacao FROM fato_aprovacao_credito WHERE cidade LIKE '%Manaus%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Manaus no período mais recente |
| Filtro por Cidade | *"Qual o Taxa de Aprovação de São Luís?"* | `SELECT mes_referencia, cidade, taxa_aprovacao FROM fato_aprovacao_credito WHERE cidade LIKE '%São Luís%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para São Luís no período mais recente |

## 2.5 Market Share & Concorrência (Anatel)

| Propriedade | Valor Oficial |
| :--- | :--- |
| **Tabela D1** | `fato_market_share` |
| **Métrica Padrão** | **Participação de Mercado (Share)** (`market_share_pct`) |
| **Coluna de Ordenação Temporal** | `mes_referencia` |

### Perguntas Suportadas e Padrões de Resposta

| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |
| :--- | :--- | :--- | :--- |
| Período e Safras | *"Qual a última safra de Market?"* | `SELECT DISTINCT mes_referencia, mes_referencia FROM fato_market_share ORDER BY mes_referencia DESC LIMIT 1` | Safra mais recente consolidada (2026-08) |
| Período e Safras | *"Quais safras estão disponíveis em Market?"* | `SELECT DISTINCT mes_referencia FROM fato_market_share ORDER BY mes_referencia DESC` | Lista das safras disponíveis |
| Rankings e Extremos | *"Quem tem o pior Participação de Mercado (Share)?"* | `SELECT cidade, market_share_pct FROM fato_market_share ORDER BY market_share_pct DESC LIMIT 5` | Ranking com as 5 piores entidades/cidades no indicador padrão |
| Rankings e Extremos | *"Quem tem o melhor Participação de Mercado (Share)?"* | `SELECT cidade, market_share_pct FROM fato_market_share ORDER BY market_share_pct ASC LIMIT 5` | Ranking com as 5 melhores entidades/cidades |
| Filtro por Operadora | *"Qual o Participação de Mercado (Share) de CLARO?"* | `SELECT mes_referencia, operadora, market_share_pct FROM fato_market_share WHERE operadora LIKE '%CLARO%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para CLARO no período mais recente |
| Filtro por Operadora | *"Qual o Participação de Mercado (Share) de VIVO?"* | `SELECT mes_referencia, operadora, market_share_pct FROM fato_market_share WHERE operadora LIKE '%VIVO%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para VIVO no período mais recente |
| Filtro por Operadora | *"Qual o Participação de Mercado (Share) de OI?"* | `SELECT mes_referencia, operadora, market_share_pct FROM fato_market_share WHERE operadora LIKE '%OI%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para OI no período mais recente |
| Filtro por Cidade | *"Qual o Participação de Mercado (Share) de Belém?"* | `SELECT mes_referencia, cidade, market_share_pct FROM fato_market_share WHERE cidade LIKE '%Belém%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Belém no período mais recente |
| Filtro por Cidade | *"Qual o Participação de Mercado (Share) de Manaus?"* | `SELECT mes_referencia, cidade, market_share_pct FROM fato_market_share WHERE cidade LIKE '%Manaus%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para Manaus no período mais recente |
| Filtro por Cidade | *"Qual o Participação de Mercado (Share) de São Luís?"* | `SELECT mes_referencia, cidade, market_share_pct FROM fato_market_share WHERE cidade LIKE '%São Luís%' ORDER BY mes_referencia DESC LIMIT 1` | Resultado analítico para São Luís no período mais recente |

---

# 3. Árvore Oficial de Navegação Interativa (Rota A Guiada)

Para garantir máxima agilidade, consistência e evitar erros de digitação em telas de smartphones, o bot opera primariamente via **Navegação Numérica Guiada com Links Diretos (`wa.me`)** estruturada em múltiplos níveis analíticos.

## 3.1 Base 1: FPD (First Payment Default)

```
1 - FPD
  1.1 - Produto Banda Larga | 1.2 - TV Tradicional | 1.3 - TV Box | 1.4 - Todos os Produtos
    1.X.1 - Resumo Executivo:
            • FPD 30 % e FPD 60 % oficial
            • Canais com pior e melhor desempenho no FPD 60
            • Cidades com pior desempenho no FPD 60
            • Empresas/Parceiros com maior e menor inadimplência
            • Vendedores/Canais com pior e melhor desempenho
    1.X.2 - Últimos 3 meses de FPD 60 (Evolução Temporal safras mai/26, abr/26, mar/26)
    1.X.3 - Ranking 10 Piores Parceiros:
            1.X.3.1 - Selecionar Canal (PAP, Lojas, Televendas, Agente Autorizado)
                      1.X.3.1.1 - Selecionar Cidade (14 Cidades: GM e MD)
                      1.X.3.1.2 - Todas as Cidades (Regional Norte Consolidada)
            1.X.3.2 - Todos os Canais
                      1.X.3.2.1 - Selecionar Cidade (14 Cidades: GM e MD)
                      1.X.3.2.2 - Todas as Cidades (Regional Norte Consolidada)
    1.X.4 - Ranking Canais FPD 60 (Últimos 3 meses):
            1.X.4.1 - Todas as Cidades (Regional Norte Consolidada)
            1.X.4.2 - Selecionar Cidade (14 Cidades: Grandes Mercados e Mercados em Desenvolvimento)
    1.X.5 - Ranking Cidades FPD 60 (Últimos 3 meses):
            1.X.5.1 - Todos os Canais
            1.X.5.2 - Selecionar Canal (PAP, Lojas, Televendas, Agente Autorizado)
```

## 3.2 Base 2: Churn Safra D120 (Sobrevivência & Estorno)

Não requer filtro de produto. Acesso direto ao menu analítico da safra:

```
2 - Churn Safra D120
  2.1 - Resumo Executivo:
        • Desconexão D120 %, Perda NP120 % (Estorno), D30 % e D60 %
        • Cidades com maior desconexão D120
        • Empresas/Parceiros com maior churn e melhor sobrevivência
  2.2 - Últimos 3 meses de Churn Safra D120 (Safras maduras e em aberto)
  2.3 - Ranking 10 Piores Parceiros (D120 / NP120):
        2.3.1 - Selecionar Canal -> Cidades (14 cidades vs todas)
        2.3.2 - Todos os Canais -> Cidades (14 cidades vs todas)
  2.4 - Ranking Canais Churn Safra (Últimos 3 meses):
        2.4.1 - Todas as Cidades
        2.4.2 - Selecionar Cidade (14 Cidades)
  2.5 - Ranking Cidades Churn Safra D120 (Últimos 3 meses):
        2.5.1 - Todos os Canais
        2.5.2 - Selecionar Canal
```

## 3.3 Base 3: Taxa de Aprovação & Crédito

Possui filtro de produto (Banda Larga, TV Tradicional, TV Box, Todos os Produtos):

```
3 - Taxa de Aprovação & Crédito
  3.1 - Produto Banda Larga | 3.2 - TV Tradicional | 3.3 - TV Box | 3.4 - Todos os Produtos
    3.X.1 - Resumo Executivo:
            • Taxa de Aprovação Regional %, Recusas Antifraude, Recusas por Política/Score, Mix Alto Risco
            • Canais com menor aprovação
            • Cidades com menor aprovação
            • PDVs/Parceiros com menor e maior aprovação
    3.X.2 - Últimos 3 meses de Taxa de Aprovação e Fraude
    3.X.3 - Ranking 10 Piores PDVs/Parceiros (Menor Aprovação / Maior Antifraude):
            3.X.3.1 - Selecionar Canal -> Cidades
            3.X.3.2 - Todos os Canais -> Cidades
    3.X.4 - Ranking Canais Aprovação (Últimos 3 meses):
            3.X.4.1 - Todas as Cidades
            3.X.4.2 - Selecionar Cidade (14 Cidades)
    3.X.5 - Ranking Cidades Menor Aprovação (Últimos 3 meses):
            3.X.5.1 - Todos os Canais
            3.X.5.2 - Selecionar Canal
```

## 3.4 Base 4: Churn Banda Larga Total & PME

Sem dimensão de canal, vendedor ou produto (exclusivo Banda Larga). Segregação por Segmento:

```
4 - Churn Banda Larga
  4.1 - Banda Larga Total | 4.2 - Banda Larga PME
    4.X.1 - Resumo Executivo:
            • Taxa Real % vs Meta Orçada (Desvio em pp)
            • Volume Real vs Orçado com Desvio RxO (delta e %)
            • Comparativo MoM (Mês Anterior: delta e %)
            • Comparativo YoY (Ano Anterior: delta e %)
            • Acumulado YTD (Ano até a safra: Real vs Orçado)
            • Cidades com maior churn e melhor desempenho
    4.X.2 - Últimos 3 meses de Churn (Taxas, volumes e desvios RxO)
    4.X.3 - Ranking de Cidades de Churn (Últimos 3 meses nas 14 cidades)
```

## 3.5 Base 5: Market Share & Concorrência (Anatel)

```
5 - Market Share & Concorrência
  5.1 - Resumo Regional Geral:
        • Market Share Claro vs Concorrentes Principais (Vivo, Oi, ISPs/Competitivas)
        • Volume de Net Adds (Saldo de adições líquidas) Claro e Concorrentes
        • Volume de Base (Acessos ativos) Claro e Concorrentes
        • Consolidado Regional Norte Móvel e Residencial
  5.2 - Market Share Residencial (14 Cidades Monitoradas):
        5.2.1 - Todas as Cidades (Consolidado das 14 cidades GM e MD)
        5.2.2 - Selecionar Cidade (Abertura por operadora para a cidade selecionada)
  5.3 - Market Share Móvel (Abertura por DDD):
        5.3.1 - Todos os DDDs da Regional Norte (DDD 91 ao DDD 99)
        5.3.2 - Selecionar DDD (DDD 91 a 99 individual)
```

## 3.6 Base 6: Speech Analytics (Motivos Transcritos)

```
6 - Speech Analytics
  6.1 - Resumo Geral (Todas as Cidades / Regional Norte):
        • Abertura motivo a motivo transcrito nos últimos 3 meses
        • Percentual de Mix (%) de cada motivo no mês atual e histórico
        • Variação MoM (pp) e indicador de tendência (Alta, Queda, Estável)
  6.2 - Filtrar por Cidade Específica:
        • Seleção entre as 14 Cidades Monitoradas (6 GM + 8 MD)
        • Abertura motivo a motivo transcrito daquela cidade nos últimos 3 meses
        • Comparativo MoM (pp) e evolução temporal
```

## 3.7 Base 7: Motivos de Procura & Taxa de OS (Atendimento)

```
7 - Motivos de Procura & Taxa de OS
  7.1 - Resumo Geral (Todas as Cidades / Regional Norte):
        • Motivos de procura na URA / Atendimento
        • Volume de ligações e Mix (%)
        • Volume de Ordens de Serviço (OS) geradas
        • Taxa de OS (%) = (OS ÷ Ligações) × 100 nos últimos 3 meses
        • Variação MoM (pp) e status operacional (Crítico, Alto, Moderado, Controlado)
  7.2 - Filtrar por Cidade Específica:
        • Seleção entre as 14 Cidades Monitoradas (6 GM + 8 MD)
        • Taxa de conversão em OS motivo a motivo na cidade nos últimos 3 meses
        • Comparativo MoM e alertas operacionais
```

## 3.8 Padrões de Navegação e Retorno (`0` / `voltar`)

A navegação respeita o stack hierárquico passo a passo:
- **Links 100% Clicáveis:** Todas as opções de menu, submenus, listas e botões de voltar e menu principal contêm links diretos `https://wa.me/{bot_phone}?text=%23%3F%20{opcao}` para que o usuário navegue apenas tocando na tela sem precisar digitar.
- Enviar **`0`** ou **`voltar`** em qualquer lista ou card retorna exatamente ao menu pai imediato.
- Enviar **`menu`**, **`inicio`** ou **`bases`** a qualquer momento limpa o estado de navegação da sessão e retorna diretamente ao menu inicial raiz.
- No WhatsApp, o bot somente responde a mensagens iniciadas pelo prefixo oficial **`#?`** (ex: `#? 1`, `#? 2`, `#? menu`). Todos os links interativos gerados já vêm pré-formatados com a URL `https://wa.me/{numero}?text=%23%3F%20{opcao}`.



