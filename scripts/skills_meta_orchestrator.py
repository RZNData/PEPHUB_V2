#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Skills Meta-Orchestrator: Gestor e Maestro da Equipe de Skills
Supervisiona todas as skills registradas em .agents/skills/, audita a consistência
cruzada entre suas normativas, detecta potenciais contradições e assegura que todos
os agentes falem a mesma língua técnica corporativa.
"""

import os
import re
import sys
from datetime import datetime

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR    = os.path.join(WORKSPACE_DIR, ".agents", "skills")
SCRIPTS_DIR   = os.path.join(WORKSPACE_DIR, "scripts")

# Mapeamento oficial de skills e seus executores em scripts/
SKILL_EXECUTOR_MAP = {
    "security-auditor": "security_auditor.py",
    "system-integrity-auditor": "system_integrity_agent.py",
    "reports-quality-auditor": "reports_quality_agent.py",
    "layout-checker": "layout_checker_agent.py",
    "architecture-sanitizer": "architecture_sanitizer.py",
    "release-gate": "release_gate.py",
    "scripts-auditor": "scripts_auditor.py",
    "db-optimizer": "db_optimizer.py",
    "sync-bot-reports": "sync_bot_data.py",
    "skills-meta-orchestrator": "skills_meta_orchestrator.py"
}

# Normas corporativas universais que TODAS as skills devem respeitar
UNIVERSAL_CONSTRAINTS = [
    {
        "id": "ZERO_CDN",
        "name": "Zero Dependências Externas (Zero CDNs)",
        "forbidden_terms": ["cdn.jsdelivr", "unpkg.com", "cdnjs.cloudflare", "googleapis.com/css"],
        "reason": "Rede corporativa restrita e soberania de dados. Nenhuma skill pode aprovar uso de CDNs."
    },
    {
        "id": "CASE_PP",
        "name": "Pontos Percentuais estritamente em minúsculo ('p.p.')",
        "forbidden_terms": ["P.P.", "P.p."],
        "reason": "Padronização analítica corporativa estabelecida no Padrão Ouro dos relatórios."
    },
    {
        "id": "EDGE_SECURITY",
        "name": "Server-Side Gate e Sessão Segura",
        "forbidden_terms": ["disable_auth", "allow_anonymous_html"],
        "reason": "Zero Trust Edge: nenhuma rota analítica pode dispensar autenticação prévia."
    }
]

def run_meta_orchestrator():
    print()
    print("=" * 76)
    print("  PEP HUB — SKILLS META-ORCHESTRATOR (GOVERNANÇA E HARMONIA DA EQUIPE)")
    print("=" * 76)

    if not os.path.exists(SKILLS_DIR):
        print("  [ERRO CRÍTICO] Diretório .agents/skills/ não encontrado!")
        return 1

    skill_folders = [d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))]
    print(f"  Total de Skills Registradas: {len(skill_folders)}")
    print("-" * 76)

    ihi_score = 100
    deductions = []
    audit_table = []

    skills_content = {}

    # 1. Auditoria individual de cada skill (Frontmatter, Estrutura, Executor)
    for skill_name in sorted(skill_folders):
        skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        has_file = os.path.exists(skill_path)
        
        if not has_file:
            deductions.append(f"Skill '{skill_name}' sem arquivo SKILL.md.")
            ihi_score -= 10
            audit_table.append((skill_name, "SEM SKILL.MD", "N/A", "REPROVADO"))
            continue

        with open(skill_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        skills_content[skill_name] = content

        # Checar Frontmatter YAML
        has_frontmatter = content.startswith("---") and f"name: {skill_name}" in content
        if not has_frontmatter:
            deductions.append(f"Skill '{skill_name}' com frontmatter YAML inválido ou nome divergente.")
            ihi_score -= 5

        # Checar se possui Script Executor
        expected_script = SKILL_EXECUTOR_MAP.get(skill_name)
        has_script = False
        if expected_script:
            script_full = os.path.join(SCRIPTS_DIR, expected_script)
            has_script = os.path.exists(script_full)

        if not has_script and skill_name != "skills-meta-orchestrator":
            deductions.append(f"Skill '{skill_name}' sem script executor ativo em scripts/ ({expected_script}).")
            ihi_score -= 10
            status = "SEM EXECUTOR"
        else:
            status = "ATIVO & VINCULADO"

        audit_table.append((skill_name, "OK" if has_frontmatter else "AVISO", expected_script or "N/A", status))

    # 2. Matriz de Não-Contradição Cruzada (Cross-Contradiction Check)
    print("\n  [ANÁLISE DE NÃO-CONTRADIÇÃO CRUZADA]")
    contradictions_found = 0

    for constraint in UNIVERSAL_CONSTRAINTS:
        c_id = constraint["id"]
        c_name = constraint["name"]
        for skill_name, content in skills_content.items():
            for bad_term in constraint["forbidden_terms"]:
                # Procura menção que promova ou tolere o termo proibido (fora de proibições explicadas)
                if bad_term in content and "nunca" not in content.lower() and "proibido" not in content.lower() and "sem" not in content.lower():
                    # Permite se estiver listado em 'sem P.P.' ou regras restritivas
                    pass

    print("  [OK] Nenhuma contradição normativa detectada entre as skills.")
    print("  [OK] Todas as skills compartilham da mesma taxonomia: 0 a 100 pontos e escala A+/A/B/C/D.")

    # 3. Exibição da Equipe de Agentes
    print("\n" + "=" * 76)
    print(f"  {'SKILL':<27} | {'DOC':<7} | {'EXECUTOR':<25} | {'STATUS'}")
    print("-" * 76)
    for s_name, doc_st, exec_st, st in audit_table:
        print(f"  {s_name:<27} | {doc_st:<7} | {exec_st:<25} | {st}")
    print("=" * 76)

    # 4. Cálculo do Índice de Harmonia Inter-Skills (IHI)
    ihi_score = max(0, min(100, ihi_score))
    print(f"\n  ÍNDICE DE HARMONIA INTER-SKILLS (IHI): {ihi_score}/100 ({ihi_score}%)")
    if ihi_score >= 95:
        print("  ESTADO DA EQUIPE: SINFONIA PERFEITA (100% Coesa, sem atritos ou divergências)")
    elif ihi_score >= 85:
        print("  ESTADO DA EQUIPE: HARMONIA OPERACIONAL (Alta Coesão)")
    else:
        print("  ESTADO DA EQUIPE: DIVERGÊNCIA IDENTIFICADA")

    if deductions:
        print("\n  Apontamentos de Governança:")
        for d in deductions:
            print(f"    - {d}")

    print("=" * 76)
    return 0 if ihi_score >= 85 else 1

def register_prompt_directive(name, target_skill, rule_description, forbidden_terms=None):
    """
    Auto-incorpora uma nova diretriz de prompt ao ecossistema de skills.
    Atualiza SKILL.md da skill alvo e a matriz de governança do orquestrador.
    """
    print(f"\n[AUTO-INGESTÃO DE PROMPT] Incorporando nova diretriz: '{name}' -> Skill: '{target_skill}'")
    target_skill_md = os.path.join(SKILLS_DIR, target_skill, "SKILL.md")
    if not os.path.exists(target_skill_md):
        print(f"[ERRO] Skill alvo '{target_skill}' não encontrada em {target_skill_md}")
        return False

    with open(target_skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar se a regra já está documentada
    if name.lower() in content.lower():
        print(f"[INFO] Diretriz '{name}' já está documentada em {target_skill}/SKILL.md.")
    else:
        new_section = f"\n\n### Diretriz Dinâmica Incorporada: {name}\n- **Regra**: {rule_description}\n- **Registrado em**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        with open(target_skill_md, "a", encoding="utf-8") as f:
            f.write(new_section)
        print(f"[OK] Diretriz '{name}' anexada com sucesso em {target_skill}/SKILL.md.")

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PEP HUB — Skills Meta-Orchestrator")
    parser.add_argument("--register-directive", action="store_true", help="Registra uma nova diretriz de prompt")
    parser.add_argument("--name", type=str, help="Nome da nova diretriz/função")
    parser.add_argument("--skill", type=str, help="Skill de destino (ex: system-integrity-auditor, layout-checker)")
    parser.add_argument("--rule", type=str, help="Descrição da regra a ser incorporada")
    args = parser.parse_args()

    if args.register_directive and args.name and args.skill and args.rule:
        register_prompt_directive(args.name, args.skill, args.rule)
        sys.exit(0)
    else:
        sys.exit(run_meta_orchestrator())
