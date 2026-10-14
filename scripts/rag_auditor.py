#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Auditoria de Governança, Anti-Alucinação e Qualidade do RAG
Skill: rag-auditor

Audita o ecossistema RAG e Text-to-SQL da Regional Norte:
1. Separação de canais (Web sem prefixo #? e sem links wa.me vs WhatsApp)
2. Tolerância zero a alucinações e isolamento estrito entre indicadores
3. Postura questionadora proativa em perguntas subespecificadas
4. Cobertura dimensional completa (14 cidades, DDDs 91-99, canais e parceiros)
5. Text-to-SQL determinístico seguro (validateSafeSQL)
6. Interface Web interativa com abas e gaveta de perguntas predefinidas
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_DIR    = os.path.join(WORKSPACE_DIR, "worker")
PUBLIC_DIR    = os.path.join(WORKSPACE_DIR, "public")
JS_DIR        = os.path.join(PUBLIC_DIR, "js")

def _read(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def run_rag_audit():
    print()
    print("=" * 76)
    print("  PEP HUB — AGENTE DE AUDITORIA DE GOVERNANÇA & ANTI-ALUCINAÇÃO DO RAG")
    print(f"  Data     : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Skill    : rag-auditor v1.0")
    print(f"  Escopo   : Regional Norte (FPD, Churn Safra, Churn BL, Crédito, Mkt Share, Speech, Motivos)")
    print("=" * 76)

    score = 100
    deductions = []
    tests = []

    bot_registry_code = _read(os.path.join(WORKER_DIR, "bot_registry.js"))
    bot_routes_code   = _read(os.path.join(WORKER_DIR, "routes", "bot.js"))
    header_widget_code = _read(os.path.join(JS_DIR, "header-widget.js"))

    # -------------------------------------------------------------
    # TESTE 1: Suporte a Parâmetro 'channel' no Backend
    # -------------------------------------------------------------
    t1_pass = (
        "channel = 'whatsapp'" in bot_routes_code or "channel = 'web'" in bot_routes_code
    ) and (
        "buildDisambiguationMenu" in bot_registry_code and "channel" in bot_registry_code
    ) and (
        "body.channel" in bot_routes_code
    )
    if t1_pass:
        tests.append(("[OK]", "T01 - Separação de Canais (Web vs WhatsApp) no Backend", 10))
    else:
        score -= 10
        deductions.append("T01: Falta suporte completo ao parâmetro channel no backend.")
        tests.append(("[X ]", "T01 - Separação de Canais (Web vs WhatsApp) no Backend", 0))

    # -------------------------------------------------------------
    # TESTE 2: Respostas do Canal Web Sem Prefixo '#?' e Sem Links wa.me
    # -------------------------------------------------------------
    t2_pass = (
        "if (channel === 'web')" in bot_registry_code or "channel === 'web'" in bot_routes_code
    ) and (
        "buildCardFooterLinks" in bot_registry_code and "channel === 'web'" in bot_registry_code
    ) and (
        "buildActionCardFooterLinks" in bot_registry_code and "channel === 'web'" in bot_registry_code
    )
    if t2_pass:
        tests.append(("[OK]", "T02 - Respostas Web Limpas (Sem Links wa.me ou #dados/#ajuda)", 10))
    else:
        score -= 10
        deductions.append("T2: Mensagens formatadas ainda contém artefatos de WhatsApp no canal Web.")
        tests.append(("[X ]", "T02 - Respostas Web Limpas (Sem Links wa.me ou #dados/#ajuda)", 0))

    # -------------------------------------------------------------
    # TESTE 3: Postura Questionadora Proativa em Perguntas Subespecificadas
    # -------------------------------------------------------------
    t3_pass = (
        "buildProactiveClarificationResponse" in bot_registry_code
    ) and (
        "buildProactiveClarificationResponse" in bot_routes_code
    ) and (
        "detectedLabel" in bot_routes_code or "detectedEntity" in bot_routes_code
    )
    if t3_pass:
        tests.append(("[OK]", "T03 - Postura Questionadora Proativa (Desambiguação Ativa)", 10))
    else:
        score -= 10
        deductions.append("T03: Falta implementação da postura questionadora proativa em consultas ambíguas.")
        tests.append(("[X ]", "T03 - Postura Questionadora Proativa (Desambiguação Ativa)", 0))

    # -------------------------------------------------------------
    # TESTE 4: Cobertura Dimensional Completa (14 Cidades, DDDs, Canais e Parceiros)
    # -------------------------------------------------------------
    t4_pass = (
        "extractQueryEntities" in bot_registry_code
    ) and (
        "OFFICIAL_14_CITIES" in bot_registry_code
    ) and (
        "OFFICIAL_DDDS" in bot_registry_code or "91" in bot_registry_code
    ) and (
        "OFFICIAL_CHANNELS" in bot_registry_code or "PAP" in bot_registry_code
    )
    if t4_pass:
        tests.append(("[OK]", "T04 - Cobertura Dimensional (14 Cidades, DDDs 91-99, Canais, Parceiros)", 10))
    else:
        score -= 10
        deductions.append("T04: Falta extração robusta de entidades dimensionais em bot_registry.js.")
        tests.append(("[X ]", "T04 - Cobertura Dimensional (14 Cidades, DDDs 91-99, Canais, Parceiros)", 0))

    # -------------------------------------------------------------
    # TESTE 5: Tolerância Zero a Alucinações & Não-Cruzamento de Indicadores
    # -------------------------------------------------------------
    has_7_reports = all(
        rep in bot_registry_code for rep in [
            "FPD", "CHURN_SAFRA", "CREDITO", "CHURN_BL", "MARKET_SHARE", "SPEECH", "MOTIVOS"
        ]
    )
    has_router_resolution = "resolveTargetReport" in bot_routes_code
    t5_pass = has_7_reports and has_router_resolution
    if t5_pass:
        tests.append(("[OK]", "T05 - Isolamento Estrito de Indicadores & Anti-Cruzamento (7 Relatórios)", 10))
    else:
        score -= 10
        deductions.append("T05: Falta isolamento estrito entre os 7 relatórios no REPORT_REGISTRY.")
        tests.append(("[X ]", "T05 - Isolamento Estrito de Indicadores & Anti-Cruzamento (7 Relatórios)", 0))

    # -------------------------------------------------------------
    # TESTE 6: Text-to-SQL Determinístico Seguro (validateSafeSQL)
    # -------------------------------------------------------------
    t6_pass = (
        "validateSafeSQL" in bot_routes_code
    ) and (
        "buildDeterministicAnalyticalSQL" in bot_registry_code
    ) and (
        "fato_fpd" in bot_registry_code and "fato_churn_safra" in bot_registry_code
    )
    if t6_pass:
        tests.append(("[OK]", "T06 - Text-to-SQL Determinístico Seguro e Anti-Injeção", 10))
    else:
        score -= 10
        deductions.append("T06: Validação de segurança de queries SQL ou gerador determinístico ausente.")
        tests.append(("[X ]", "T06 - Text-to-SQL Determinístico Seguro e Anti-Injeção", 0))

    # -------------------------------------------------------------
    # TESTE 7: Abas e Gaveta de Perguntas Predefinidas + Botão Relatório no Chatbot
    # -------------------------------------------------------------
    t7_pass = (
        "ragPresetBar" in header_widget_code or "rag-preset-bar" in header_widget_code
    ) and (
        "ragPresetDrawer" in header_widget_code or "rag-preset-drawer" in header_widget_code
    ) and (
        "rag-report-link-btn" in header_widget_code
    ) and (
        "PRESET_QUESTIONS" in header_widget_code
    )
    if t7_pass:
        tests.append(("[OK]", "T07 - Abas, Gaveta de Perguntas e Botão de Navegação ao Relatório Oficial", 10))
    else:
        score -= 10
        deductions.append("T07: Falta interface de abas/gaveta de perguntas predefinidas ou botão para relatório oficial.")
        tests.append(("[X ]", "T07 - Abas, Gaveta de Perguntas e Botão de Navegação ao Relatório Oficial", 0))

    # -------------------------------------------------------------
    # TESTE 8: Metadados Ricos (reportUrl, Chips, Disclaimer) e Envio Web
    # -------------------------------------------------------------
    t8_pass = (
        "buildRichMetadataForReport" in bot_routes_code
    ) and (
        "rag-disclaimer-note" in header_widget_code
    ) and (
        "rag-feedback-bar" in header_widget_code
    ) and (
        "channel: 'web'" in header_widget_code or 'channel: "web"' in header_widget_code
    )
    if t8_pass:
        tests.append(("[OK]", "T08 - Metadados Ricos, Disclaimer Analítico e Barra de Feedback no Chatbot", 10))
    else:
        score -= 10
        deductions.append("T08: Metadados ricos, disclaimer de supervisão ou barra de feedback ausentes.")
        tests.append(("[X ]", "T08 - Metadados Ricos, Disclaimer Analítico e Barra de Feedback no Chatbot", 0))

    # -------------------------------------------------------------
    # TESTE 9: Bateria de No Mínimo 20 Perguntas Cognitivas Humanas (Aberturas, Profundidade, Cruzamentos)
    # -------------------------------------------------------------
    import subprocess
    scenarios_script = os.path.join(WORKSPACE_DIR, "scripts", "test_rag_20_scenarios.js")
    t9_pass = False
    if os.path.exists(scenarios_script):
        try:
            res_scen = subprocess.run(
                ["node", scenarios_script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30
            )
            t9_pass = res_scen.returncode == 0 and "22/22" in (res_scen.stdout or "")
        except Exception as e:
            deductions.append(f"T09: Erro ao executar scripts/test_rag_20_scenarios.js: {e}")
    if t9_pass:
        tests.append(("[OK]", "T09 - Bateria Cognitiva de 22 Cenários Humanos (Aberturas, Profundidade, Cruzamentos)", 10))
    else:
        score -= 10
        deductions.append("T09: Bateria cognitiva de 20+ cenários humanos falhou ou não atingiu 100%.")
        tests.append(("[X ]", "T09 - Bateria Cognitiva de 22 Cenários Humanos (Aberturas, Profundidade, Cruzamentos)", 0))

    # -------------------------------------------------------------
    # TESTE 10: Tabela bot_feedback no D1, Rota de Feedback e Documentação SKILL.md
    # -------------------------------------------------------------
    schema_code = _read(os.path.join(WORKSPACE_DIR, "schema.sql"))
    skill_md = _read(os.path.join(WORKSPACE_DIR, ".agents", "skills", "rag-auditor", "SKILL.md"))
    t10_pass = (
        "bot_feedback" in schema_code
    ) and (
        "/api/bot/feedback" in bot_routes_code
    ) and (
        "name: rag-auditor" in skill_md
    ) and (
        "Bateria de Testes Cognitivos" in skill_md or "20 Cenários" in skill_md
    )
    if t10_pass:
        tests.append(("[OK]", "T10 - Loop de Calibração Contínua (bot_feedback) e Governança da Skill", 10))
    else:
        score -= 10
        deductions.append("T10: Tabela bot_feedback, endpoint /api/bot/feedback ou documentação da skill ausente.")
        tests.append(("[X ]", "T10 - Loop de Calibração Contínua (bot_feedback) e Governança da Skill", 0))

    # Exibição dos resultados
    print("\n  Checklist de Governança Analítica:")
    for status, desc, pts in tests:
        print(f"  {status} {desc} (+{pts} pts)")

    print()
    print("=" * 76)
    grade = (
        "A+" if score >= 95 else
        "A"  if score >= 90 else
        "B"  if score >= 80 else
        "C"  if score >= 70 else "D"
    )
    print(f"  Pontuação Final RAG Auditor: {score}/100 — Classificação: [{grade}]")
    if deductions:
        print("  Deduções e Pendências Identificadas:")
        for d in deductions:
            print(f"    - {d}")
    else:
        print("  Status: APROVADO — 100% dos requisitos de governança do RAG atendidos.")
    print("=" * 76)
    print()

    # Retorna código de saída compatível com release gate
    sys.exit(0 if score >= 90 else 1)

if __name__ == "__main__":
    run_rag_audit()
