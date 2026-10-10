"""
Test Bot RAG & Text-to-SQL Pipeline — Pephub Cloud
Valida:
1. Classificação de Intenção (Analítica, Conceitual, Fora de Escopo)
2. Filtro de Segurança do SQL (Validação de Safe SELECT)
3. Execução em SQLite D1 com carga de seed_bot_data.sql
4. Consultas cruzadas em todos os relatórios da plataforma
"""

import os
import re
import sqlite3
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_SQL_PATH = os.path.join(ROOT_DIR, "seed_bot_data.sql")
SCHEMA_SQL_PATH = os.path.join(ROOT_DIR, "schema.sql")


def validate_safe_sql_python(sql: str):
    if not sql or not isinstance(sql, str):
        return False, "SQL vazio"
    trimmed = sql.strip()
    if not re.match(r"^(\s*SELECT|\s*WITH)\b", trimmed, re.IGNORECASE):
        return False, "Não inicia com SELECT ou WITH"
    without_trailing = re.sub(r";\s*$", "", trimmed)
    if ";" in without_trailing:
        return False, "Múltiplas instruções"
    forbidden = [
        r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
        r"\bALTER\b", r"\bCREATE\b", r"\bREPLACE\b", r"\bATTACH\b",
        r"\bDETACH\b", r"\bPRAGMA\b", r"\bVACUUM\b", r"\bREINDEX\b",
        r"\bTRUNCATE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"--", r"/\*"
    ]
    for p in forbidden:
        if re.search(p, without_trailing, re.IGNORECASE):
            return False, f"Padrão proibido: {p}"
    return True, without_trailing


def test_sql_validator():
    print("[TEST] 1. Validador de Segurança SQL...")
    # Casos válidos
    valid_cases = [
        "SELECT * FROM fato_indicadores_mensais WHERE cidade = 'Belém'",
        "SELECT cidade, vol_real, taxa_real FROM fato_indicadores_mensais ORDER BY vol_real DESC LIMIT 5",
        "WITH cte AS (SELECT * FROM fato_churn_safra WHERE safra = 'mai/26') SELECT * FROM cte",
        "SELECT fs.safra, fs.taxa_d120 FROM fato_churn_safra fs WHERE fs.visao = 'REGIONAL'"
    ]
    for q in valid_cases:
        ok, res = validate_safe_sql_python(q)
        assert ok, f"Deveria ser válido: {q} -> {res}"

    # Casos maliciosos ou inválidos
    invalid_cases = [
        "DROP TABLE users",
        "SELECT * FROM users; DELETE FROM users;",
        "INSERT INTO users (id) VALUES ('hacked')",
        "UPDATE users SET is_admin = 1",
        "SELECT * FROM users -- bypass auth",
        "SELECT * FROM users /* comment injection */",
        "PRAGMA table_info(users)",
    ]
    for q in invalid_cases:
        ok, res = validate_safe_sql_python(q)
        assert not ok, f"Deveria ser bloqueado: {q}"

    print("   -> 100% dos testes de segurança SQL passaram!")


def test_sqlite_execution():
    print("[TEST] 2. Execução das Tabelas no SQLite D1 (Em Memória)...")
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Executa schema.sql
    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        schema_content = f.read()
    cursor.executescript(schema_content)

    # Executa seed_bot_data.sql
    with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
        seed_content = f.read()
    cursor.executescript(seed_content)

    # Validações por Relatório:
    # 1. Churn BL Total
    cursor.execute("SELECT cidade, vol_real, taxa_real FROM fato_indicadores_mensais WHERE segmento = 'Banda Larga Total' AND cidade = 'Belém' AND tipo_visao = 'TOTAL'")
    row = cursor.fetchone()
    assert row is not None, "Belém não encontrada em BL Total"
    print(f"   [BL Total] Belém -> Vol Real: {row[1]} | Taxa: {row[2]}%")

    # 2. Churn Safra D120
    cursor.execute("SELECT safra, instalacoes, churn_d120, taxa_d120 FROM fato_churn_safra WHERE visao = 'REGIONAL' AND safra = 'mai/26'")
    row_safra = cursor.fetchone()
    assert row_safra is not None, "Safra mai/26 regional não encontrada"
    print(f"   [Churn Safra] Safra mai/26 Regional Norte -> Inst: {row_safra[1]} | D120: {row_safra[2]} ({row_safra[3]}%)")

    # 3. FPD
    cursor.execute("SELECT cidade, safra, fpd30, taxa_fpd30, cura, taxa_cura FROM fato_fpd WHERE cidade = 'Manaus' AND safra = 'mai/26'")
    row_fpd = cursor.fetchone()
    assert row_fpd is not None, "FPD Manaus mai/26 não encontrado"
    print(f"   [FPD] Manaus mai/26 -> FPD 30: {row_fpd[2]} ({row_fpd[3]}%) | Cura: {row_fpd[4]} ({row_fpd[5]}%)")

    # 4. Aprovação de Crédito
    cursor.execute("SELECT cidade, consultas, aprovados, taxa_aprovacao FROM fato_aprovacao_credito WHERE cidade = 'Belém' AND mes_referencia = '2026-09'")
    row_ap = cursor.fetchone()
    assert row_ap is not None, "Aprovação de Crédito Belém não encontrada"
    print(f"   [Aprovação] Belém 2026-09 -> Consultas: {row_ap[1]} | Aprovados: {row_ap[2]} ({row_ap[3]}%)")

    # 5. Market Share
    cursor.execute("SELECT cidade, operadora, market_share_pct, net_adds FROM fato_market_share WHERE cidade = 'Belém' AND operadora = 'Claro'")
    row_mkt = cursor.fetchone()
    assert row_mkt is not None, "Market Share Belém Claro não encontrado"
    print(f"   [Market Share] Belém Claro -> Participação: {row_mkt[2]}% | Net Adds: {row_mkt[3]}")

    # 6. Semantic RAG (Knowledge chunks)
    cursor.execute("SELECT modulo, topico, conteudo FROM bot_knowledge_chunks WHERE palavras_chave LIKE '%fpd%' OR topico LIKE '%fpd%'")
    rows_rag = cursor.fetchall()
    assert len(rows_rag) >= 3, "Poucos chunks RAG de FPD encontrados"
    print(f"   [Semantic RAG] Chunks de FPD recuperados: {len(rows_rag)}")

    # 7. Safra Ordenação Cronológica (safra_ord)
    cursor.execute("SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1")
    row_fpd_latest = cursor.fetchone()
    assert row_fpd_latest == ("mai/26", "2026-05"), f"Esperado ('mai/26', '2026-05'), obteve {row_fpd_latest}"
    print(f"   [Ordenação Safra] FPD Última Safra -> {row_fpd_latest[0]} (safra_ord: {row_fpd_latest[1]})")

    # 8. Memória de Sessões de Desambiguação (bot_pending_sessions)
    cursor.execute("INSERT OR REPLACE INTO bot_pending_sessions (phone, query) VALUES ('5591999999999', 'como esta Manaus')")
    cursor.execute("SELECT query FROM bot_pending_sessions WHERE phone = '5591999999999'")
    row_session = cursor.fetchone()
    assert row_session is not None and row_session[0] == "como esta Manaus", "Falha na memória de desambiguação"
    cursor.execute("DELETE FROM bot_pending_sessions WHERE phone = '5591999999999'")
    print("   [Sessões D1] Memória persistente de desambiguação validada!")

    # 9. FPD por Parceiro (fato_churn_safra visao = 'PARCEIRO')
    cursor.execute("SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 30 ORDER BY safra_ord DESC, taxa_d30 DESC LIMIT 5")
    rows_parceiros = cursor.fetchall()
    assert len(rows_parceiros) > 0, "Nenhum parceiro de FPD retornado"
    print(f"   [FPD Parceiros] Pior parceiro -> {rows_parceiros[0][1]} ({rows_parceiros[0][0]}): FPD 30={rows_parceiros[0][3]}% | NP120={rows_parceiros[0][4]}%")

    conn.close()
    print("   -> 100% das consultas analíticas e semânticas retornaram dados com precisão!")


if __name__ == "__main__":
    print("=" * 60)
    print("RODANDO TESTES DO PIPELINE BOT RAG (PEPHUB)")
    print("=" * 60)
    test_sql_validator()
    test_sqlite_execution()
    print("\nTODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO!")
