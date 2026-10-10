---
name: sync-bot-reports
description: Sincroniza automaticamente a base de dados do bot WhatsApp no Cloudflare D1 (pephub-db) sempre que novos relatórios ou bases (Churn BL Total, PME, FPD, Churn Safra, etc.) forem atualizados no Pephub. Garante dados 100% reais e elimina alucinações.
---

# Skill: Sync Bot Reports — Sincronização Contínua Bot & Relatórios

Esta skill automatiza a extração e a carga das bases analíticas corporativas dos painéis da Regional Norte para o banco de dados remoto **Cloudflare D1 (`pephub-db`)**, mantendo a inteligência do bot WhatsApp sempre alinhada com as últimas tendências e safras publicadas.

---

## Quando Ativar Esta Skill

Ative esta skill sempre que:
1. Um novo arquivo de Churn Banda Larga Total ou PME (ex: `1Tend_Out26_Acompanhamento Churn Horizontal...`) for inserido.
2. Uma nova base de microdados FPD (ex: `BASE_FPD_JUN25_JUN26.csv`) for atualizada.
3. Uma nova safra de Churn Safra D120 for carregada.
4. Qualquer relatório for compilado ou publicado via painel ou pipeline.
5. O usuário solicitar: "atualize a base do bot", "sincronize os dados do bot", ou "o bot está desatualizado".

---

## Como Executar a Sincronização

Execute o comando mestre de sincronização na raiz do projeto:

```bash
# Executa a extração completa e publica no D1 remoto
python scripts/sync_bot_data.py
```

O script executa automaticamente as seguintes etapas:
1. **Extração das Fontes**: Lê os payloads compactados de `Painel_Churn_Banda_Larga_Total.html`, `Painel_Churn_Banda_Larga_PME.html` e `Painel_FPD_Regional_Norte.html`.
2. **Geração de Lotes SQL**: Cria o arquivo `scripts/seed_real_corporate_data.sql` contendo os statements para todas as tabelas de fatos.
3. **Carga em Lotes no D1**: Subdivide o script em lotes seguros e aplica via `npx wrangler d1 execute pephub-db --remote`.
4. **Validação Automática**: Consulta o D1 remoto e confirma os valores da última safra/mês de referência.

---

## Tabelas Fato Sincronizadas no Cloudflare D1

| Tabela D1 | Origem dos Dados | Granularidade / Conteúdo |
|---|---|---|
| `fato_indicadores_mensais` | Churn BL Total & PME | Realizado, Orçado, RxO, MoM, YoY, YTD, Taxa de Churn por Cidade e Segmento (últimos 3 meses). |
| `fato_fpd` | Painel FPD (133k+ registros) | Aging30, Aging60, Cura, Canais (PAP, Lojas, Televendas), Cidades, Produtos (Dados, TV Box, Tradicional). |
| `fato_motivos_os` | Sumário Call Center S4 | 6 motivos de procura na URA (Cobrança, Sinal/Lentidão, Financeiro, etc.) e taxa de geração de OS. |
| `fato_speech_analytics` | Call Center Speech Analytics | Mix percentual das demandas dos clientes e variação MoM por cidade. |
| `fato_aprovacao_credito` | Taxa de Aprovação Residencial | Consultas, aprovações, recusas de política e antifraude por canal e cidade. |

---

## Verificação Rápida Pós-Sincronização

Para testar se os números mais recentes estão ativos no bot:

```bash
# Verificar últimos registros de Churn Banda Larga Total
npx wrangler d1 execute pephub-db --remote --command="SELECT mes_referencia, segmento, tipo_visao, vol_real, taxa_real FROM fato_indicadores_mensais WHERE cidade='Regional Norte' AND tipo_visao='TOTAL' ORDER BY mes_referencia DESC LIMIT 3;"

# Verificar última safra de FPD
npx wrangler d1 execute pephub-db --remote --command="SELECT safra, familia_produto, instalacoes, fpd30, taxa_fpd30, fpd60, taxa_fpd60 FROM fato_fpd WHERE cidade='Regional Norte' AND canal='TODOS' ORDER BY safra_ord DESC LIMIT 3;"
```

---

## Regras de Integridade Analítica (Zero Alucinação)

1. **JAMAIS misturar métricas de bases distintas**: Churn Safra D120 pertence à safra de instalação D120; Churn Banda Larga é desconexão mensal do parque ativo; FPD é inadimplência de primeira fatura (aging 30/60).
2. **Sempre referenciar a safra/mês ativo**: As respostas do bot devem citar explicitamente o mês (ex: `Outubro / 2026 - T1` ou `Safra mai/26`).
3. **Sempre rodar `sync_bot_data.py` antes de deploy em produção**.
