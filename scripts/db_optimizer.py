#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente Otimizador de Queries D1 (Cloudflare D1 / SQLite)
Varre o worker/index.js em busca de anti-patterns de performance:
N+1, SELECT *, LIKE sufixo, queries sem LIMIT, falta de indices,
e gera o SQL de correcao correspondente.
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_PATH   = os.path.join(WORKSPACE_DIR, "worker", "index.js")


def find_n_plus_one(code):
    """Detecta subqueries correlacionadas executadas N vezes por registro pai"""
    findings = []
    # Pattern: (SELECT ... FROM table WHERE ... u. ou a.user_id = u.id)
    matches = re.finditer(
        r'\(SELECT\s+([\w\s,*()]+)\s+FROM\s+(\w+)\s+([^)]+WHERE[^)]+(?:u\.|user_id\s*=))[^)]*\)',
        code, re.IGNORECASE
    )
    for m in matches:
        agg   = m.group(1).strip()
        table = m.group(2).strip()
        findings.append({
            "type": "N+1 Subquery Correlacionada",
            "severity": "HIGH",
            "snippet": m.group(0)[:100],
            "table": table,
            "agg": agg,
            "fix": (
                f"Substituir por LEFT JOIN:\n"
                f"  SELECT u.*, COUNT(a.id) as total\n"
                f"  FROM users u\n"
                f"  LEFT JOIN {table} a ON a.user_id = u.id\n"
                f"  GROUP BY u.id"
            )
        })
    return findings


def find_select_star(code):
    """SELECT * retorna colunas desnecessarias, aumentando payload"""
    findings = []
    for m in re.finditer(r'SELECT\s+\*\s+FROM\s+(\w+)', code, re.IGNORECASE):
        table = m.group(1)
        if table in ("access_logs", "users"):
            findings.append({
                "type": "SELECT * em Tabela de Alto Volume",
                "severity": "MEDIUM",
                "snippet": m.group(0)[:60],
                "table": table,
                "fix": f"Listar apenas as colunas necessarias: SELECT id, email_claro, recurso, created_at FROM {table}"
            })
    return findings


def find_like_suffix(code):
    """LIKE '%texto%' e LIKE '%texto' nao usam indice B-tree — full scan"""
    findings = []
    for m in re.finditer(r"LIKE\s+['\"]%[^'\"]+['\"]", code, re.IGNORECASE):
        findings.append({
            "type": "LIKE Sufixo (Full Scan)",
            "severity": "MEDIUM",
            "snippet": m.group(0)[:60],
            "table": "?",
            "fix": (
                "Se possivel, adicionar coluna booleana indexada (ex: is_export) "
                "ao inves de LIKE '%DOWNLOAD%'. "
                "SQLite so usa indice em LIKE 'prefixo%', nao em '%sufixo'."
            )
        })
    return findings


def find_no_limit(code):
    """SELECT de multiplas linhas sem LIMIT pode causar timeout do Worker"""
    findings = []
    # Pegar todos os SELECTs que retornam .all() mas sem LIMIT na query
    for m in re.finditer(
        r'env\.DB\.prepare\(\s*[`\'"]([^`\'"]{10,})[`\'"]\s*\)(?:[^;]+)\.all\(\)',
        code, re.DOTALL
    ):
        sql_body = m.group(1).upper()
        if "LIMIT" not in sql_body and "COUNT(" not in sql_body:
            table_match = re.search(r'FROM\s+(\w+)', sql_body)
            table = table_match.group(1) if table_match else "?"
            if table in ("ACCESS_LOGS", "USERS", "SESSIONS"):
                findings.append({
                    "type": "Query Multi-Row sem LIMIT",
                    "severity": "HIGH",
                    "snippet": m.group(1)[:80],
                    "table": table.lower(),
                    "fix": f"Adicionar LIMIT 500 OFFSET $offset e implementar paginacao cursor no response."
                })
    return findings


def find_missing_indexes(code):
    """Colunas frequentemente filtradas sem indice declarado"""
    findings = []
    declared_indexes = set(re.findall(r'CREATE INDEX[^\n]+ON\s+\w+\s*\(([^)]+)\)', code, re.IGNORECASE))
    declared_cols = set()
    for idx_def in declared_indexes:
        declared_cols.update(c.strip().lower() for c in idx_def.split(","))

    # Colunas usadas em WHERE
    where_cols = set(re.findall(r'WHERE\s+(?:\w+\.)?(\w+)\s*[=<>!]', code, re.IGNORECASE))

    high_frequency = {"email_claro", "user_id", "recurso", "created_at", "status", "login_claro"}
    missing = high_frequency & where_cols - declared_cols

    for col in missing:
        findings.append({
            "type": "Coluna Filtrada sem Indice",
            "severity": "MEDIUM",
            "snippet": f"WHERE {col} = ?",
            "table": "access_logs / users",
            "fix": f"CREATE INDEX IF NOT EXISTS idx_al_{col} ON access_logs ({col});"
        })
    return findings


def run_db_optimizer():
    print("=" * 72)
    print("  PEP HUB — OTIMIZADOR DE QUERIES D1  v1")
    print(f"  Data  : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Alvo  : worker/index.js")
    print("=" * 72)

    if not os.path.exists(WORKER_PATH):
        print("  [ERRO] worker/index.js nao encontrado.")
        sys.exit(1)

    worker_dir = os.path.dirname(WORKER_PATH)
    all_chunks = []
    for root, _, files in os.walk(worker_dir):
        for f in sorted(files):
            if f.endswith(".js") and not f.endswith(".bak"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    all_chunks.append(fh.read())
    code = "\n".join(all_chunks)

    findings = []
    findings += find_n_plus_one(code)
    findings += find_select_star(code)
    findings += find_like_suffix(code)
    findings += find_no_limit(code)
    findings += find_missing_indexes(code)

    sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda x: sev_order.get(x.get("severity","LOW"), 9))

    print(f"\n  Total de anti-patterns D1 detectados: {len(findings)}\n")
    icons = {"HIGH": "[ALTO]   ", "MEDIUM": "[MEDIO]  ", "LOW": "[BAIXO]  "}

    if not findings:
        print("  [OK] Nenhum anti-pattern de performance encontrado nas queries D1.")
    else:
        for i, f in enumerate(findings, 1):
            sev = f.get("severity", "LOW")
            print(f"  {i:02d}. {icons.get(sev,'[?]')} {f['type']}")
            print(f"      Tabela  : {f.get('table', '?')}")
            print(f"      Snippet : {f.get('snippet', '')}")
            print(f"      Correcao: {f.get('fix', '')}\n")

    print("=" * 72)
    print("  BOAS PRATICAS D1 (Cloudflare SQLite):")
    print("  1. Nunca SELECT * em tabelas de alto volume — projetar apenas colunas necessarias.")
    print("  2. LIMIT obrigatorio em toda query que retorna multiplas linhas (.all()).")
    print("  3. LIKE '%sufixo' causa full scan — preferir coluna booleana indexada.")
    print("  4. LEFT JOIN + GROUP BY ao inves de N subqueries correlacionadas.")
    print("  5. Indices compostos para filtros frequentes (created_at DESC, email_claro).")
    print("=" * 72 + "\n")

    return len([f for f in findings if f.get("severity") == "HIGH"])


if __name__ == "__main__":
    highs = run_db_optimizer()
    sys.exit(1 if highs > 0 else 0)
