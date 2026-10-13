---
name: scalability-auditor
description: Agente especialista em escalabilidade, alta concorrência e stress testing para Cloudflare Workers e Cloudflare D1. Audita proteção contra lock contention no SQLite do D1 (Single-Writer Protection), in-memory session caching, fast-bypass de assets na borda (<0.1ms de CPU), desacoplamento de telemetria via ctx.waitUntil, índices B-Tree e limites de varredura.
---

# Skill: Scalability & High Concurrency Auditor v1

## Objetivo
Garantir que a plataforma PEP HUB e todos os seus 10 painéis analíticos suportem milhares de acessos diários simultâneos sem gargalos de banco de dados, sem estouro de limites de CPU do Cloudflare Workers e com latência ultra-baixa na borda global.

## Como Executar

```bash
python scripts/scalability_auditor.py
```

## Os 4 Pilares de Escalabilidade Corporativa

### [1] D1 Concurrency & Single-Writer Protection (30 pontos)
- **In-Memory Session Caching:** Armazenamento volátil de sessões válidas no isolado do Worker (TTL 30s) para evitar queries repetidas ao D1 a cada clique do usuário.
- **Telemetria Desacoplada (`ctx.waitUntil`):** A gravação de logs de auditoria (`logAccess`) nunca bloqueia a resposta HTTP enviada ao navegador.
- **Fail-Open Telemetry:** Se o banco de dados atingir contenção momentânea de escrita, a falha do log é suprimida silenciosamente em bloco `catch` defensivo, garantindo que o usuário nunca receba erro 500.
- **Debounce de Presença:** O registro de heartbeat de usuários online é controlado para evitar tempestades de `UPDATE` no D1 quando múltiplos colaboradores alternam abas.

### [2] Fast-Path na Borda & Latência (<10ms) (25 pontos)
- **Fast Bypass de Assets Estáticos:** Requisições para `.css`, `.js`, `.png`, `.svg`, `.ico`, `.woff2` são servidas diretamente via `env.ASSETS` sem tocar no banco de dados e consumindo <0.1ms de CPU.
- **Lazy Schema Execution:** Migrações e checagens estruturais de tabela (`ensureAppSchema`) são executadas estritamente sob demanda em rotas administrativas `/api/admin/`, nunca em rotas de consulta analítica.
- **Healthcheck Instantâneo:** Rota `/health` responde em 0ms para monitoramento de liveness e status de edge.

### [3] Limites de Varredura D1 & Índices B-Tree (25 pontos)
- **Índices Estratégicos:** Cobertura de índices B-Tree em todas as colunas frequentes de busca (`sessions.token`, `access_logs.created_at`, `access_logs.email_claro`, `users.login_claro`, `access_requests.status`).
- **`LIMIT` Explícito:** Nenhuma consulta de auditoria ou listagem multi-row pode executar `.all()` sem cláusula `LIMIT`, prevenindo estouro de limites de leitura e estouro de memória do Worker (128MB).
- **Cache-Control em Assets:** Imagens, ícones e fontes com cabeçalho de cache longo (`max-age=604800, stale-while-revalidate=86400`) para descarregar a rede corporativa.

### [4] Client-Side Computing Offloading (20 pontos)
- **Computação no Navegador:** Os 10 relatórios analíticos são autônomos. Todos os cálculos matemáticos, cruzamentos de dados, agrupamentos, subtotais e renderizações SVG ocorrem 100% no cliente (JavaScript nativo).
- **Consumo Zero de CPU do Backend:** Durante a navegação analítica e aplicação de filtros, o consumo de CPU do Cloudflare Worker é de exatamente 0%.
- **Intervalo Estrito de Heartbeat:** O frontend limita sinais de presença a intervalos de 60 segundos com debounce contra eventos espúrios de `visibilitychange`.

## Escala de Classificação

| Score | Grau | Status |
|---|---|---|
| **93 - 100** | **A+** | Escalabilidade Exemplar — Apto para concorrência massiva |
| **85 - 92** | **A** | Aprovado para Alta Carga |
| **75 - 84** | **B** | Risco de Contenção sob Picos |
| **< 75** | **C/D** | Bloqueado — Otimização Obrigatória |
