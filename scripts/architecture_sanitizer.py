#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Arquitetura de Codigo e Saneamento Corporativo v2
Audita escalabilidade, conformidade com PADRAO_DESIGN_PAINEIS.md,
performance de dados massivos, zero dependencias externas, tamanho de modulos,
duplicacao de codigo, RAG readiness do bot e estado unidirecional.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORE_FILES = {
    "worker":        os.path.join(WORKSPACE_DIR, "worker", "index.js"),
    "portal":        os.path.join(WORKSPACE_DIR, "public", "index.html"),
    "admin":         os.path.join(WORKSPACE_DIR, "public", "admin", "index.html"),
    "churn":         os.path.join(WORKSPACE_DIR, "public", "churn", "index.html"),
    "churn_bl_total":os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    "churn_bl_pme":  os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    "fpd":           os.path.join(WORKSPACE_DIR, "public", "fpd", "index.html"),
    "divulgacao":    os.path.join(WORKSPACE_DIR, "public", "pep-tools", "divulgacao", "index.html"),
    "bot":           os.path.join(WORKSPACE_DIR, "whatsapp-bot", "bot.js"),
}

DISALLOWED_LIBRARIES = [
    (r'<script[^>]*src=[\'"][^\'"]*react[^\'"]*[\'"]',    "React externo"),
    (r'<script[^>]*src=[\'"][^\'"]*vue[^\'"]*[\'"]',      "Vue externo"),
    (r'<script[^>]*src=[\'"][^\'"]*jquery[^\'"]*[\'"]',   "jQuery externo"),
    (r'<script[^>]*src=[\'"][^\'"]*bootstrap[^\'"]*[\'"]',"Bootstrap JS externo"),
    (r'<link[^>]*href=[\'"][^\'"]*bootstrap[^\'"]*[\'"]', "Bootstrap CSS externo"),
    (r'<script[^>]*src=[\'"][^\'"]*tailwind[^\'"]*[\'"]', "Tailwind CDN externo"),
    (r'<script[^>]*src=[\'"][^\'"]*chart\.js[^\'"]*[\'"]',"Chart.js externo"),
    (r'<script[^>]*src=[\'"][^\'"]*d3[^\'"]*[\'"]',       "D3.js externo"),
    (r'<script[^>]*src=[\'"][^\'"]*leaflet[^\'"]*[\'"]',  "Leaflet externo"),
    (r'<script[^>]*src=[\'"][^\'"]*mapbox[^\'"]*[\'"]',   "Mapbox externo"),
    (r'<script[^>]*src=[\'"][^\'"]*cdn\.[^\'"]+[\'"]',    "Script via CDN generico"),
    (r'<script[^>]*src=[\'"][^\'"]*unpkg\.[^\'"]+[\'"]',  "Script via unpkg"),
]

INFORMAL_EMOJI_RE = re.compile(
    r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|'
    r'[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|'
    r'[\U0001FA70-\U0001FAFF]'
)

# Limites de tamanho de arquivo
FILE_SIZE_LIMITS = {
    "worker": {"warn": 1500, "crit": 2000},  # Worker JS
    "admin":  {"warn": 1800, "crit": 2500},  # Admin HTML
    "analytical": {"warn": 3200, "crit": 4000},  # Paineis HTML
    "bot":    {"warn": 400,  "crit": 600},   # Bot JS
}


def _read(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _line_count(content):
    return content.count("\n") + 1 if content else 0

def _read_worker_bundle():
    worker_dir = os.path.join(WORKSPACE_DIR, "worker")
    chunks = []
    for root, _, files in os.walk(worker_dir):
        for f in sorted(files):
            if f.endswith(".js") and not f.endswith(".bak"):
                c = _read(os.path.join(root, f))
                if c:
                    chunks.append(c)
    return "\n".join(chunks)


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 1: ZERO DEPENDENCIAS EXTERNAS
# ─────────────────────────────────────────────────────────────────────────────
def audit_zero_dependencies():
    findings, score = [], 100
    for key, path in CORE_FILES.items():
        if not path.endswith(".html") or not os.path.exists(path):
            continue
        content = _read(path)
        rel = os.path.relpath(path, WORKSPACE_DIR)
        for pat, desc in DISALLOWED_LIBRARIES:
            if re.search(pat, content, re.IGNORECASE):
                findings.append({
                    "pillar": "Zero Dependencias Externas",
                    "file": rel, "severity": "CRITICAL",
                    "issue": f"Dependencia nao-autorizada: {desc}",
                    "remediation": "Substituir por implementacao nativa: SVG, Canvas 2D, Vanilla JS."
                })
                score -= 25
    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 2: SOBRIEDADE E IDENTIDADE VISUAL
# ─────────────────────────────────────────────────────────────────────────────
def audit_design_system():
    findings, score = [], 100
    for key, path in CORE_FILES.items():
        if not os.path.exists(path):
            continue
        content = _read(path)
        rel = os.path.relpath(path, WORKSPACE_DIR)

        # Emojis informais
        if path.endswith(".html"):
            emojis = []
            for m in INFORMAL_EMOJI_RE.finditer(content):
                ctx = content[max(0, m.start()-30):m.end()+30]
                if not re.search(r"[A-Za-z0-9+/=]{40,}", ctx):
                    emojis.append(m.group(0))
            if emojis:
                findings.append({
                    "pillar": "Sobriedade Visual",
                    "file": rel, "severity": "MEDIUM",
                    "issue": f"Emojis informais ({len(emojis)} ocorrencia(s))",
                    "remediation": "Substituir por simbolos vetoriais SVG: ▲ ▼ ▶ ⟳ ⤢ ✎ ou icones <svg>."
                })
                score -= 10

        # Tipografia
        if "font-family" in content or ":root" in content:
            if not any(f in content for f in ["Segoe UI", "Roboto", "sans-serif"]):
                findings.append({
                    "pillar": "Sobriedade Visual",
                    "file": rel, "severity": "LOW",
                    "issue": "Tipografia corporativa (Segoe UI/Roboto) nao declarada",
                    "remediation": "Adicionar: font-family: 'Segoe UI', Roboto, Arial, sans-serif"
                })
                score -= 5

        # Paleta incompleta (--purple e --blue sao criticos para BL)
        if path.endswith(".html") and "churn-bl" in path:
            for var in ["--purple", "--blue"]:
                if var not in content:
                    findings.append({
                        "pillar": "Sobriedade Visual",
                        "file": rel, "severity": "MEDIUM",
                        "issue": f"Variavel semantica '{var}' ausente no painel BL",
                        "remediation": f"Adicionar '{var}' ao :root conforme PADRAO_DESIGN_PAINEIS.md."
                    })
                    score -= 5

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 3: PERFORMANCE DE DADOS MASSIVOS
# ─────────────────────────────────────────────────────────────────────────────
def audit_analytics_performance():
    findings, score = [], 100
    analytical = ["churn", "churn_bl_total", "churn_bl_pme", "fpd"]

    for key in analytical:
        path = CORE_FILES.get(key)
        if not path or not os.path.exists(path):
            continue
        content = _read(path)
        rel = os.path.relpath(path, WORKSPACE_DIR)
        size = len(content)

        # DecompressionStream para payloads grandes
        has_decomp = any(k in content for k in ["DecompressionStream", "deflate", "pako"])
        if not has_decomp and size > 500_000:
            findings.append({
                "pillar": "Performance & Dados Massivos",
                "file": rel, "severity": "HIGH",
                "issue": f"Payload de {size//1024}KB sem DecompressionStream (deflate/zlib)",
                "remediation": "Compactar colunas em Base64 zlib/deflate e hidratar via DecompressionStream nativa."
            })
            score -= 15

        # TypedArrays
        has_typed = any(t in content for t in ["Uint8Array","Uint16Array","Uint32Array","Float32Array"])
        if not has_typed and size > 500_000:
            findings.append({
                "pillar": "Performance & Dados Massivos",
                "file": rel, "severity": "MEDIUM",
                "issue": "Colecoes de dados numericos sem TypedArrays (RAM 5x maior)",
                "remediation": "Usar Uint16Array/Uint32Array para indices e metricas numericas."
            })
            score -= 10

        # Estado unidirecional sel = {}
        has_sel = bool(re.search(r'\b(?:let|const|var)\s+sel\s*=\s*\{', content))
        if not has_sel:
            findings.append({
                "pillar": "Estado Unidirecional (Single Source of Truth)",
                "file": rel, "severity": "MEDIUM",
                "issue": "Objeto 'sel' de estado dimensional nao identificado",
                "remediation": "Centralizar: let sel = { dimensao: new Set() } como unica fonte de verdade."
            })
            score -= 8

        # Filtros em passe unico (refreshAvailability)
        has_slicer = bool(re.search(r'refreshAvailability|sliceO|filterPass', content))
        if not has_slicer:
            findings.append({
                "pillar": "Filtros de Passe Unico O(N)",
                "file": rel, "severity": "LOW",
                "issue": "Funcao refreshAvailability de filtro O(N) nao identificada",
                "remediation": "Implementar varredura linear unica para desabilitar opcoes mutuamente exclusivas."
            })
            score -= 5

        # Canvas para mapas geoespaciais
        has_canvas_map = bool(re.search(r'drawMap|getContext\([\'"]2d', content))
        if not has_canvas_map and "mapa" in content.lower():
            findings.append({
                "pillar": "Mapa Geoespacial (Canvas 2D)",
                "file": rel, "severity": "LOW",
                "issue": "Secao de mapa sem Canvas 2D nativo detectado",
                "remediation": "Implementar mapa via Canvas.getContext('2d') com projecao Web Mercator pura."
            })
            score -= 5

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 4: ESCALABILIDADE BACKEND (CLOUDFLARE WORKERS & D1)
# ─────────────────────────────────────────────────────────────────────────────
def audit_worker_scalability():
    findings, score = [], 100
    code = _read_worker_bundle()
    if not code:
        return 0, [{"pillar":"Backend","file":"worker/index.js","severity":"CRITICAL",
                    "issue":"worker/index.js nao encontrado","remediation":"Criar o arquivo."}]

    # Prepared statements
    if "env.DB.prepare" not in code:
        findings.append({
            "pillar": "Escalabilidade D1", "file": "worker/index.js", "severity": "CRITICAL",
            "issue": "Prepared statements nao encontrados",
            "remediation": "Usar env.DB.prepare(sql).bind(...params) em todas as consultas."
        })
        score -= 25

    # Indices D1
    if "idx_access_logs_created" not in code or "idx_users_login" not in code:
        findings.append({
            "pillar": "Escalabilidade D1", "file": "worker/index.js", "severity": "MEDIUM",
            "issue": "Indices D1 ausentes para access_logs e users",
            "remediation": "Adicionar indices em email_claro, created_at, recurso, status no ensureAppSchema."
        })
        score -= 10

    # Queries sem LIMIT em access_logs (selects de linhas, nao counts)
    unbounded = []
    for m in re.finditer(r'SELECT\s+\*\s+FROM\s+access_logs([^;`"\']+)', code, re.IGNORECASE):
        body = m.group(1).upper()
        if "LIMIT" not in body and ".FIRST(" not in body and ".ALL(" not in body:
            unbounded.append(m.group(0)[:70])
    if unbounded:
        findings.append({
            "pillar": "Escalabilidade D1", "file": "worker/index.js", "severity": "HIGH",
            "issue": f"SELECT * em access_logs sem LIMIT ({len(unbounded)} ocorrencia(s))",
            "remediation": "Aplicar LIMIT + paginacao cursor/offset em todas as queries de listagem."
        })
        score -= 15

    # N+1 subqueries correlacionadas
    corr = re.findall(
        r'\(SELECT\s+(?:count|max)\([^)]+\)\s+FROM\s+access_logs\s+[^)]*WHERE[^)]*u\.',
        code, re.IGNORECASE
    )
    if len(corr) >= 3:
        findings.append({
            "pillar": "Escalabilidade D1 — N+1", "file": "worker/index.js", "severity": "HIGH",
            "issue": f"{len(corr)} subqueries correlacionadas por usuario em access_logs",
            "remediation": (
                "Reescrever com LEFT JOIN + GROUP BY:\n"
                "SELECT u.*, COUNT(a.id) as total_accesses, MAX(a.created_at) as last_access\n"
                "FROM users u LEFT JOIN access_logs a ON a.user_id = u.id GROUP BY u.id"
            )
        })
        score -= 15

    # Cache-Control para assets estaticos
    if "Cache-Control" not in code:
        findings.append({
            "pillar": "Escalabilidade — Cache", "file": "worker/index.js", "severity": "LOW",
            "issue": "Cabecalhos Cache-Control nao encontrados para assets estaticos",
            "remediation": "Adicionar Cache-Control: public, max-age=86400 para assets imutaveis."
        })
        score -= 5

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 5: HIGIENE E TAMANHO DE MODULOS
# ─────────────────────────────────────────────────────────────────────────────
def audit_code_hygiene():
    findings, score = [], 100

    for key, path in CORE_FILES.items():
        if not os.path.exists(path):
            continue
        content = _read(path)
        lines = _line_count(content)
        rel = os.path.relpath(path, WORKSPACE_DIR)

        # Tamanho de arquivo
        if key == "worker":
            lim = FILE_SIZE_LIMITS["worker"]
        elif key == "admin":
            lim = FILE_SIZE_LIMITS["admin"]
        elif key == "bot":
            lim = FILE_SIZE_LIMITS["bot"]
        else:
            lim = FILE_SIZE_LIMITS["analytical"]

        if lines > lim["crit"]:
            findings.append({
                "pillar": "Higiene — Tamanho de Modulo",
                "file": rel, "severity": "HIGH",
                "issue": f"Arquivo com {lines} linhas — acima do limite critico de {lim['crit']}",
                "remediation": "Decompor em modulos menores (ver sugestoes de decomposicao na SKILL.md)."
            })
            score -= 15
        elif lines > lim["warn"]:
            findings.append({
                "pillar": "Higiene — Tamanho de Modulo",
                "file": rel, "severity": "MEDIUM",
                "issue": f"Arquivo com {lines} linhas — acima do limite recomendado de {lim['warn']}",
                "remediation": "Planejar decomposicao modular antes do proximo release."
            })
            score -= 8

        # debugger esquecido
        if re.search(r'\bdebugger\b', content):
            findings.append({
                "pillar": "Higiene — Debug", "file": rel, "severity": "HIGH",
                "issue": "Instrucao 'debugger' em codigo de producao",
                "remediation": "Remover imediatamente antes do deploy."
            })
            score -= 15

        # console.log excessivo em backend
        if key == "worker":
            clogs = len(re.findall(r'console\.log\(', content))
            if clogs > 20:
                findings.append({
                    "pillar": "Higiene — Logs", "file": rel, "severity": "LOW",
                    "issue": f"{clogs} console.log em producao no worker",
                    "remediation": "Substituir por telemetria estruturada (logAccess) e silenciar debug logs."
                })
                score -= 5

    # Arquivos HTML duplicados (index.html + Painel_*.html no mesmo diretorio)
    for module_dir in ["public/churn", "public/churn-bl-total", "public/churn-bl-pme", "public/fpd"]:
        full_dir = os.path.join(WORKSPACE_DIR, module_dir.replace("/", os.sep))
        if not os.path.isdir(full_dir):
            continue
        html_files = [f for f in os.listdir(full_dir) if f.endswith(".html")]
        if len(html_files) > 1:
            findings.append({
                "pillar": "Higiene — Arquivos Duplicados",
                "file": module_dir, "severity": "MEDIUM",
                "issue": f"{len(html_files)} arquivos HTML no mesmo modulo: {html_files}",
                "remediation": "Definir index.html como canonico e remover ou converter o(s) duplicado(s)."
            })
            score -= 8

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 6 (NOVO): BOT RAG READINESS
# ─────────────────────────────────────────────────────────────────────────────
def audit_bot_rag_readiness():
    findings, score = [], 100
    code = _read(CORE_FILES.get("bot", ""))
    worker_code = _read_worker_bundle()

    if not code:
        return 100, []

    # Contexto analitico (endpoint /api/bot/context ou similar)
    has_context_endpoint = bool(
        worker_code and re.search(r"/api/bot/|/bot/context|/api/kpis", worker_code, re.IGNORECASE)
    )
    if not has_context_endpoint:
        findings.append({
            "pillar": "Bot RAG Readiness",
            "file": "worker/index.js + bot.js", "severity": "HIGH",
            "issue": "Endpoint /api/bot/context nao encontrado — bot nao tem acesso a KPIs consolidados",
            "remediation": (
                "Criar GET /api/bot/context no worker retornando JSON com KPIs por modulo: "
                "{ churn: {...}, fpd: {...}, bl_total: {...} }. Bot consome a cada mensagem relevante."
            )
        })
        score -= 20

    # Estado conversacional (sessoes por remetente)
    has_session = bool(re.search(r'Map\b|session|conversationState|chatHistory', code, re.IGNORECASE))
    if not has_session:
        findings.append({
            "pillar": "Bot RAG Readiness — Estado",
            "file": "whatsapp-bot/bot.js", "severity": "MEDIUM",
            "issue": "Bot sem estado conversacional por remetente (stateless)",
            "remediation": (
                "Implementar: const sessions = new Map(); "
                "sessions.set(jid, { history: [], lastSeen: Date.now() }). "
                "Expirar sessoes com TTL de 10min."
            )
        })
        score -= 12

    # Handler de comandos estruturado (switch/case ou mapa de handlers)
    has_command_map = bool(re.search(r'commandHandlers|commands\[|switch\s*\(cmd', code, re.IGNORECASE))
    if not has_command_map:
        findings.append({
            "pillar": "Bot RAG Readiness — Estrutura",
            "file": "whatsapp-bot/bot.js", "severity": "LOW",
            "issue": "Bot sem mapa estruturado de comandos — dificil adicionar novos comandos para RAG",
            "remediation": (
                "Criar: const COMMANDS = { '/churn': handleChurn, '/fpd': handleFpd, '/ajuda': handleHelp }. "
                "Facilita adicionar comandos RAG como /pergunte, /filtrar, /resumo."
            )
        })
        score -= 8

    # Arquivo de contexto JSON (KPIs pre-calculados para fallback offline)
    context_json = os.path.join(WORKSPACE_DIR, "whatsapp-bot", "context.json")
    if not os.path.exists(context_json):
        findings.append({
            "pillar": "Bot RAG Readiness — Contexto Offline",
            "file": "whatsapp-bot/context.json", "severity": "LOW",
            "issue": "context.json ausente — bot sem fallback de KPIs se o worker estiver indisponivel",
            "remediation": (
                "Criar whatsapp-bot/context.json com KPIs consolidados atualizados via cron/webhook. "
                "Bot usa como fallback quando /api/bot/context nao responde."
            )
        })
        score -= 5

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# PILAR 7 (NOVO): PADRONIZACAO ENTRE PAINEIS (CROSS-PANEL CONFORMITY)
# ─────────────────────────────────────────────────────────────────────────────
def audit_cross_panel_conformity():
    findings, score = [], 100
    analytical = {
        "churn":         CORE_FILES["churn"],
        "churn_bl_total":CORE_FILES["churn_bl_total"],
        "churn_bl_pme":  CORE_FILES["churn_bl_pme"],
        "fpd":           CORE_FILES["fpd"],
    }

    # Verificar quais paineis possuem cada feature critica
    features = {
        "DecompressionStream": [],
        "Uint8Array|Uint16Array|Uint32Array": [],
        "let sel = ": [],
        "refreshAvailability": [],
        "drawer": [],
        "createObjectURL|Blob": [],
    }

    panel_features = {}
    for key, path in analytical.items():
        if not os.path.exists(path):
            continue
        content = _read(path)
        panel_features[key] = {}
        for feat, missing_list in features.items():
            has = bool(re.search(feat, content))
            panel_features[key][feat] = has
            if not has:
                missing_list.append(key)

    # Inconsistencias: feature presente em alguns mas nao em outros
    for feat, missing in features.items():
        present = [k for k in analytical if k not in missing and os.path.exists(analytical[k])]
        if present and missing:
            findings.append({
                "pillar": "Conformidade Cruzada Entre Paineis",
                "file": "multi-painel", "severity": "HIGH",
                "issue": (
                    f"Feature '{feat}' presente em [{', '.join(present)}] "
                    f"mas AUSENTE em [{', '.join(missing)}]"
                ),
                "remediation": f"Aplicar '{feat}' em todos os paineis para uniformidade arquitetural."
            })
            score -= 12

    return max(0, score), findings


# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTRADOR
# ─────────────────────────────────────────────────────────────────────────────
def run_architecture_sanitizer():
    print("=" * 72)
    print("  PEP HUB — ARQUITETURA & SANEAMENTO CORPORATIVO  v2")
    print(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("  Normativo: PADRAO_DESIGN_PAINEIS.md & Enterprise Web Scalability")
    print("=" * 72)

    dep_sc,    dep_f    = audit_zero_dependencies()
    design_sc, design_f = audit_design_system()
    perf_sc,   perf_f   = audit_analytics_performance()
    work_sc,   work_f   = audit_worker_scalability()
    hyg_sc,    hyg_f    = audit_code_hygiene()
    rag_sc,    rag_f    = audit_bot_rag_readiness()
    cross_sc,  cross_f  = audit_cross_panel_conformity()

    all_findings = dep_f + design_f + perf_f + work_f + hyg_f + rag_f + cross_f

    # Score ponderado (7 pilares)
    global_score = round(
        dep_sc    * 0.15 +
        design_sc * 0.10 +
        perf_sc   * 0.20 +
        work_sc   * 0.20 +
        hyg_sc    * 0.10 +
        rag_sc    * 0.10 +
        cross_sc  * 0.15
    )

    if global_score >= 93:   grade = "A+ (Excelente — Arquitetura Exemplar)"
    elif global_score >= 85: grade = "A  (Excelente — Alta Escalabilidade e Conformidade)"
    elif global_score >= 72: grade = "B  (Bom — Debito Tecnico Secundario)"
    elif global_score >= 60: grade = "C  (Regular — Debito Tecnico Identificado)"
    else:                    grade = "D  (Critico — Riscos Imediatos de Performance/Conformidade)"

    print(f"\n  Indice Global: {global_score}/100  |  {grade}\n")
    print("-" * 72)
    print("  PONTUACAO POR PILAR:")
    print(f"  [1] Zero Dependencias Externas          : {dep_sc:3d}/100")
    print(f"  [2] Sobriedade & Identidade Visual      : {design_sc:3d}/100")
    print(f"  [3] Performance de Dados Massivos       : {perf_sc:3d}/100")
    print(f"  [4] Escalabilidade Backend (CF Workers) : {work_sc:3d}/100")
    print(f"  [5] Higiene & Tamanho de Modulos        : {hyg_sc:3d}/100")
    print(f"  [6] Bot RAG Readiness                   : {rag_sc:3d}/100")
    print(f"  [7] Conformidade Cruzada Entre Paineis  : {cross_sc:3d}/100")
    print("-" * 72)
    print(f"\n  Total de Apontamentos: {len(all_findings)}\n")

    if not all_findings:
        print("  [+] Base de codigo 100% conforme com PADRAO_DESIGN_PAINEIS.md.")
    else:
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        sorted_f = sorted(all_findings, key=lambda x: sev_order.get(x.get("severity","LOW"), 9))
        icons = {"CRITICAL":"[CRITICO]","HIGH":"[ALTO]   ","MEDIUM":"[MEDIO]  ","LOW":"[BAIXO]  "}

        for idx, f in enumerate(sorted_f, 1):
            sev    = f.get("severity", "LOW")
            pillar = f.get("pillar", "Geral")
            file_r = f.get("file", "-")
            issue  = f.get("issue", "")
            remed  = f.get("remediation", "")
            print(f"  {idx:02d}. {icons.get(sev,'[?]')} {pillar}")
            print(f"      Arquivo : {file_r}")
            print(f"      Problema: {issue}")
            print(f"      Acao    : {remed}\n")

    print("=" * 72)
    print("  BOAS PRATICAS PERMANENTES:")
    print("  1. Monolitos autossuficientes — zero chamadas de rede externas nos paineis.")
    print("  2. Toda query D1 com projecao restrita de colunas e LIMIT explicito.")
    print("  3. SVG com viewBox parametrico para fluidez em qualquer resolucao.")
    print("  4. Estado reativo derivado de 'sel' — filtros em passe unico O(N).")
    print("  5. Bot com endpoint /api/bot/context para RAG conversacional.")
    print("  6. Modulos acima de 2000 linhas decompostos antes do proximo release.")
    print("  7. Conformidade cruzada: toda feature aplicada uniformemente em todos os paineis.")
    print("=" * 72)

    return global_score, all_findings


if __name__ == "__main__":
    score, _ = run_architecture_sanitizer()
    sys.exit(0 if score >= 80 else 1)
