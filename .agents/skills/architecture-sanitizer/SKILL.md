---
name: architecture-sanitizer
description: Agente especialista em arquitetura de código, saneamento e escalabilidade analítica. Versão 2 com 7 pilares incluindo Bot RAG Readiness e Conformidade Cruzada Entre Painéis. Audita conformidade com PADRAO_DESIGN_PAINEIS.md, zero dependências externas, processamento massivo via streams e typed arrays, N+1 queries, tamanho de módulos e boas práticas de Cloudflare Workers e D1.
---

# Skill: Architecture & Sanitization Auditor v2

## Como Executar

```bash
python scripts/architecture_sanitizer.py
```

## Os 7 Pilares de Engenharia (v2)

### [1] Zero Dependências Externas (Self-Contained)
- Nenhuma lib CDN: React, Vue, jQuery, Bootstrap, Tailwind, Chart.js, D3.js, Leaflet, Mapbox
- Gráficos em SVG nativo com `viewBox` responsivo
- Mapas em Canvas 2D com projeção Web Mercator pura

### [2] Sobriedade & Identidade Visual (Claro Design System)
- Paleta completa com 14 variáveis CSS, incluindo `--purple` e `--blue`
- `--purple: #6b4b8a` obrigatório em painéis com segmento NP (inadimplência)
- Zero emojis — apenas símbolos vetoriais técnicos (`▲ ▼ ▶ ⟳ ⤢ ✎`)
- Tipografia: `"Segoe UI", Roboto, Arial, sans-serif` nativa

### [3] Performance de Dados Massivos
- `DecompressionStream('deflate')` para payloads > 500KB
- `Uint8Array / Uint16Array / Uint32Array` para armazenamento colunar indexado
- Estado único `sel = { dimensao: Set() }` desacoplado do DOM
- `refreshAvailability` — filtros em passe único O(N)
- Canvas 2D com drawMap() para módulo geoespacial

### [4] Escalabilidade Backend (Cloudflare Workers & D1)
- Prepared statements `env.DB.prepare().bind()` obrigatórios
- Índices D1 em colunas frequentemente filtradas
- `LIMIT` explícito em toda query multi-row em tabelas de alto volume
- **N+1 subqueries correlacionadas → LEFT JOIN + GROUP BY**
- Cache-Control para assets estáticos

### [5] Higiene & Tamanho de Módulos
- Limites por tipo: worker ≤ 2000L, admin ≤ 2500L, painéis ≤ 3200L, bot ≤ 600L
- Zero `debugger` em código de produção
- Arquivos HTML duplicados no mesmo módulo → definir canônico e remover

### [6] Bot RAG Readiness *(NOVO v2)*
- `GET /api/bot/context` no worker retornando KPIs consolidados por módulo
- Estado conversacional `Map<jid, context>` com TTL de 10min
- Mapa estruturado de comandos `COMMANDS = { '/churn': handler, ... }`
- `whatsapp-bot/context.json` para fallback offline

### [7] Conformidade Cruzada Entre Painéis *(NOVO v2)*
- Detecta features presentes em alguns painéis mas ausentes em outros
- `DecompressionStream`, `TypedArrays`, `sel`, `refreshAvailability`, `drawer`, `Blob`
- Garante evolução uniforme de todos os módulos analíticos

## Escala de Classificação

| Score | Grau |
|---|---|
| 93–100 | **A+** Arquitetura Exemplar |
| 85–92 | **A** Alta Escalabilidade e Conformidade |
| 72–84 | **B** Débito Técnico Secundário |
| 60–71 | **C** Débito Técnico Identificado |
| 0–59 | **D** Riscos Imediatos |

## Checklist Pre-Release

```bash
python scripts/layout_checker_agent.py     # Nota mínima: 85/100 (Grau A)
python scripts/security_auditor.py         # Nota mínima: 90/100 (Grau A)
python scripts/architecture_sanitizer.py   # Nota mínima: 80/100 (Grau B)
python scripts/db_optimizer.py             # Zero findings HIGH
python scripts/release_gate.py             # Gate final antes do deploy
```
