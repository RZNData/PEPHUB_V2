#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Limpeza e Inventario do Diretorio scripts/
Identifica scripts obsoletos, duplicados por funcao, e organiza
em categorias para facilitar manutencao e onboarding.
"""

import os
import sys
import re
from collections import defaultdict
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR   = os.path.join(WORKSPACE_DIR, "scripts")

# Scripts oficiais (mantidos, nao marcar como candidatos a remocao)
OFFICIAL_SCRIPTS = {
    "layout_checker_agent.py",
    "security_auditor.py",
    "architecture_sanitizer.py",
    "release_gate.py",
    "db_optimizer.py",
    "scripts_auditor.py",  # este proprio
    "extract_churn_data.py",
    "build_fpd_definitive.py",
    "generate_fpd_from_churn_safra.py",
    "seed-access-telemetry.js",
    "validate_js_syntax.py",
}

# Prefixos que indicam scripts temporarios/diagnosticos
TEMP_PREFIXES = [
    "check_", "find_", "diagnose_", "investigate_",
    "inspect_", "test_", "verify_", "list_", "locate_"
]

# Sufixos de versao antiga
OLD_VERSION_PATTERN = re.compile(r'_(v[0-9]|old|bkp|backup|orig|legacy|temp|tmp)\.(py|js)$', re.IGNORECASE)


def categorize_scripts():
    all_files = sorted(os.listdir(SCRIPTS_DIR))
    py_files  = [f for f in all_files if f.endswith(".py")]
    js_files  = [f for f in all_files if f.endswith(".js")]

    categories = defaultdict(list)

    for fname in py_files + js_files:
        if fname in OFFICIAL_SCRIPTS:
            categories["official"].append(fname)
        elif OLD_VERSION_PATTERN.search(fname):
            categories["old_version"].append(fname)
        elif any(fname.startswith(p) for p in TEMP_PREFIXES):
            categories["diagnostic_temp"].append(fname)
        else:
            categories["utility"].append(fname)

    return dict(categories), len(all_files)


def find_duplicates(py_files):
    """Identifica scripts com funcoes idênticas pelo nome da funcao principal"""
    func_map = defaultdict(list)
    for fname in py_files:
        path = os.path.join(SCRIPTS_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            main_funcs = re.findall(r'^def (\w+)\(', content, re.MULTILINE)
            for fn in main_funcs:
                func_map[fn].append(fname)
        except Exception:
            pass

    return {fn: files for fn, files in func_map.items() if len(files) > 1}


def get_file_size_kb(fname):
    path = os.path.join(SCRIPTS_DIR, fname)
    return os.path.getsize(path) // 1024 if os.path.exists(path) else 0


def run_scripts_auditor():
    print("=" * 72)
    print("  PEP HUB — INVENTARIO & AUDITORIA DO DIRETORIO scripts/  v1")
    print(f"  Data  : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Alvo  : {SCRIPTS_DIR}")
    print("=" * 72)

    categories, total = categorize_scripts()
    all_py = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py")]

    print(f"\n  Total de arquivos em scripts/: {total}")
    print(f"    Scripts oficiais     : {len(categories.get('official', []))}")
    print(f"    Utilitarios de build : {len(categories.get('utility', []))}")
    print(f"    Diagnosticos/temp    : {len(categories.get('diagnostic_temp', []))}")
    print(f"    Versoes antigas      : {len(categories.get('old_version', []))}")

    print("\n" + "-" * 72)
    print("  SCRIPTS OFICIAIS (nao remover):")
    for f in sorted(categories.get("official", [])):
        kb = get_file_size_kb(f)
        print(f"    [OK] {f:<45} {kb:>5} KB")

    print("\n" + "-" * 72)
    print("  VERSOES ANTIGAS (candidatos a remocao):")
    old = categories.get("old_version", [])
    if old:
        for f in sorted(old):
            kb = get_file_size_kb(f)
            print(f"    [DEL] {f:<44} {kb:>5} KB")
    else:
        print("    Nenhum identificado.")

    print("\n" + "-" * 72)
    print("  SCRIPTS DIAGNOSTICOS / TEMPORARIOS (revisar se ainda sao uteis):")
    diag = categories.get("diagnostic_temp", [])
    if diag:
        for f in sorted(diag)[:20]:  # mostrar so os primeiros 20
            kb = get_file_size_kb(f)
            print(f"    [REV] {f:<44} {kb:>5} KB")
        if len(diag) > 20:
            print(f"    ... e mais {len(diag)-20} scripts diagnosticos.")
    else:
        print("    Nenhum identificado.")

    print("\n" + "-" * 72)
    print("  FUNCOES DUPLICADAS ENTRE SCRIPTS:")
    duplicates = find_duplicates(all_py)
    # Filtrar funcoes genericas
    ignore_fns = {"main", "run", "test", "check", "read", "write", "get", "set", "load"}
    real_dups = {fn: files for fn, files in duplicates.items()
                 if fn not in ignore_fns and len(fn) > 4}

    if real_dups:
        for fn, files in list(real_dups.items())[:10]:
            print(f"    [DUP] def {fn}() encontrada em: {files}")
    else:
        print("    Nenhuma duplicata relevante de funcoes encontrada.")

    # Recomendacoes
    total_temp_kb = sum(get_file_size_kb(f) for f in diag)
    total_old_kb  = sum(get_file_size_kb(f) for f in old)

    print("\n" + "=" * 72)
    print("  RECOMENDACOES:")
    if old:
        print(f"  1. Remover {len(old)} versoes antigas — libera ~{total_old_kb}KB no repositorio.")
    if diag:
        print(f"  2. Revisar {len(diag)} scripts diagnosticos (~{total_temp_kb}KB):")
        print(f"     Mover para scripts/archive/ os que nao sao mais necessarios.")
    if real_dups:
        print(f"  3. Consolidar {len(real_dups)} funcoes duplicadas em modulo utilitario compartilhado.")
    print("  4. Rodar 'python scripts/release_gate.py' antes de todo deploy.")
    print("=" * 72 + "\n")

    return len(old) + len(real_dups)


if __name__ == "__main__":
    issues = run_scripts_auditor()
    sys.exit(0 if issues == 0 else 0)  # Sempre exit 0 (nao bloqueia pipeline)
