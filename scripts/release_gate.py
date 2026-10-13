#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Release Gate: Checklist Pre-Deploy Corporativo
Executa todos os agentes de auditoria (layout, seguranca, arquitetura)
e so aprova o deploy se os 3 atingirem as notas minimas definidas.
Retorna exit code 0 (OK) ou 1 (BLOQUEADO).
"""

import os
import sys
import subprocess
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR   = os.path.join(WORKSPACE_DIR, "scripts")

# Notas minimas para aprovacao do release
MIN_LAYOUT_SCORE   = 85   # B ou acima
MIN_SECURITY_SCORE = 90   # A
MIN_ARCH_SCORE     = 80   # B ou acima
MIN_FPD_SCORE      = 90   # A

def run_agent(script_name, label):
    path = os.path.join(SCRIPTS_DIR, script_name)
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", path],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=WORKSPACE_DIR, timeout=60
        )
        output = result.stdout + result.stderr
        # Extrair score da saida
        import re
        scores = re.findall(r'(?:Score|Pontua[cç][aã]o|Índice|Indice)[^\d\n\r]*(\d{1,3})(?:/100|%)', output, re.IGNORECASE)
        score = int(scores[0]) if scores else None
        return score, result.returncode, output
    except Exception as e:
        return None, 1, str(e)

def run_release_gate():
    print()
    print("=" * 72)
    print("  PEP HUB — RELEASE GATE: CHECKLIST PRE-DEPLOY CORPORATIVO")
    print(f"  Data     : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Workspace: {WORKSPACE_DIR}")
    print("=" * 72)

    agents = [
        ("layout_checker_agent.py",     "UX/UI & Layout",                   MIN_LAYOUT_SCORE),
        ("security_auditor.py",         "Seguranca AppSec",                 MIN_SECURITY_SCORE),
        ("architecture_sanitizer.py",   "Arquitetura",                      MIN_ARCH_SCORE),
        ("fpd_quality_agent.py",        "FPD Qualidade & Dados",            MIN_FPD_SCORE),
        ("reports_quality_agent.py",    "Qualidade Universal de Relatorios", 85),
        ("system_integrity_agent.py",   "Integridade do Sistema & Auth",    90),
        ("scalability_auditor.py",      "Escalabilidade & Concorrencia",    85),
        ("skills_meta_orchestrator.py", "Meta-Orquestrador de Skills",      90),
    ]

    results = []
    for script, label, min_score in agents:
        print(f"\n  Executando: {label}...")
        score, rc, output = run_agent(script, label)

        if score is None:
            status = "ERRO"
            passed = False
        elif score >= min_score:
            status = f"APROVADO ({score}/100 >= {min_score})"
            passed = True
        else:
            status = f"REPROVADO ({score}/100 < {min_score} minimo)"
            passed = False

        results.append((label, score, min_score, passed, status))
        icon = "  [OK]" if passed else "  [X]"
        print(f"  {icon} {label}: {status}")

    print("\n" + "=" * 72)
    print("  RESULTADO FINAL DO RELEASE GATE")
    print("=" * 72)

    all_passed = all(r[3] for r in results)
    blockers = [r for r in results if not r[3]]

    for label, score, min_score, passed, status in results:
        bar_filled = (score or 0) // 5
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        grade = (
            "A+" if (score or 0) >= 93 else
            "A"  if (score or 0) >= 85 else
            "B"  if (score or 0) >= 72 else
            "C"  if (score or 0) >= 60 else "D"
        )
        ok = "OK" if passed else "X "
        print(f"  [{ok}] [{grade}] {(score or 0):3d}/100  [{bar}]  {label}")

    print()
    if all_passed:
        print("  DEPLOY AUTORIZADO — Todos os gates aprovados.")
        print("  O sistema esta em conformidade com os padroes corporativos PEP HUB.")
    else:
        print(f"  DEPLOY BLOQUEADO — {len(blockers)} gate(s) reprovado(s):")
        for label, score, min_score, _, _ in blockers:
            delta = min_score - (score or 0)
            print(f"    - {label}: precisa de +{delta} pontos para atingir {min_score}/100")
        print()
        print("  Corrija os apontamentos criticos e execute novamente antes do deploy.")

    print("=" * 72 + "\n")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_release_gate())
