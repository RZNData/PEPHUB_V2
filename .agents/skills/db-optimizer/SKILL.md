---
name: db-optimizer
description: Detecta anti-patterns de performance em queries D1 (Cloudflare SQLite): N+1 correlacionadas, SELECT *, LIKE de sufixo, queries sem LIMIT e colunas filtradas sem índice. Gera SQL de correção para cada achado.
---

# Skill: D1 Query Optimizer — Otimizador de Performance de Banco

Analisa estaticamente o `worker/index.js` e detecta padrões de query que causam degradação de performance no Cloudflare D1 (SQLite).

## Como Executar

```bash
python scripts/db_optimizer.py
```

## Anti-Patterns Detectados

### 🔴 N+1 Subqueries Correlacionadas
**Problema:** `(SELECT count(*) FROM access_logs WHERE user_id = u.id)` executada N vezes por usuário na listagem.

**Correção gerada:**
```sql
SELECT u.*,
  COUNT(a.id) as total_accesses,
  MAX(a.created_at) as last_access
FROM users u
LEFT JOIN access_logs a ON a.user_id = u.id
GROUP BY u.id
ORDER BY u.created_at DESC
```

### 🔴 SELECT * em Tabelas de Alto Volume
**Problema:** `SELECT * FROM access_logs` retorna colunas desnecessárias, aumentando payload e tempo de transferência.

**Correção:** Projetar apenas colunas necessárias: `SELECT id, email_claro, recurso, created_at FROM access_logs`

### 🟡 LIKE Sufixo (Full Scan)
**Problema:** `LIKE '%DOWNLOAD%'` não usa índice B-tree do SQLite — realiza full scan.

**Correção:** Adicionar coluna booleana `is_export BOOLEAN` indexada separadamente.

### 🔴 Query Multi-Row sem LIMIT
**Problema:** `.all()` sem `LIMIT` em tabelas `access_logs`, `users`, `sessions` pode retornar ilimitadas linhas.

**Correção:** Sempre `LIMIT 500 OFFSET $offset` com paginação cursor.

### 🟡 Colunas Filtradas sem Índice
**Problema:** Filtros frequentes em colunas sem índice causam full scan progressivo.

**Correção gerada:**
```sql
CREATE INDEX IF NOT EXISTS idx_al_recurso ON access_logs (recurso);
CREATE INDEX IF NOT EXISTS idx_al_created_at ON access_logs (created_at DESC);
```

## Boas Práticas D1 (Cloudflare SQLite)

1. Nunca `SELECT *` em tabelas de alto volume
2. `LIMIT` obrigatório em toda query que retorna múltiplas linhas
3. `LIKE '%sufixo'` → coluna booleana indexada
4. LEFT JOIN + GROUP BY ao invés de N subqueries correlacionadas
5. Índices compostos para filtros frequentes
6. CPU target: < 10ms por request no Worker
