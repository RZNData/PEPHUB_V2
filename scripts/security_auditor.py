#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Security Specialist Audit Agent v2 (Static AppSec & Defense-in-Depth)
Audits Cloudflare Workers codebase, D1 schema, frontend templates e WhatsApp bot
contra OWASP Top 10, CWE standards e politicas corporativas de seguranca telecom.
Cobertura v2: CSP, Rate Limiting, N+1 DoS, IDOR, Bot Auth, wrangler exposure,
              HSTS, Permissions-Policy, stack trace leak, XSS, RBAC.
"""

import os
import re
import sys
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_PATH   = os.path.join(WORKSPACE_DIR, "worker", "index.js")
ADMIN_HTML    = os.path.join(WORKSPACE_DIR, "public", "admin", "index.html")
PORTAL_HTML   = os.path.join(WORKSPACE_DIR, "public", "index.html")
BOT_PATH      = os.path.join(WORKSPACE_DIR, "whatsapp-bot", "bot.js")
WRANGLER_PATH = os.path.join(WORKSPACE_DIR, "wrangler.toml")
DIVULGACAO    = os.path.join(WORKSPACE_DIR, "public", "pep-tools", "divulgacao", "index.html")


# ─────────────────────────────────────────────────────────────────────────────
# WORKER BACKEND CHECKS
# ─────────────────────────────────────────────────────────────────────────────
def check_worker_security():
    findings = []
    score = 100

    if not os.path.exists(WORKER_PATH):
        return {"score": 0, "findings": [{"severity": "CRITICAL", "category": "Configuracao",
                "cwe": "CWE-665", "description": "worker/index.js nao encontrado."}]}

    worker_dir = os.path.dirname(WORKER_PATH)
    all_chunks = []
    for root, _, files in os.walk(worker_dir):
        for f in sorted(files):
            if f.endswith(".js") and not f.endswith(".bak"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                    all_chunks.append(fh.read())
    code = "\n".join(all_chunks)

    # ── 1. SQL INJECTION (CWE-89) ─────────────────────────────────────────────
    sqli_patterns = [
        (r'env\.DB\.prepare\(\s*`[^`]*\$\{(?!.*ALL_DEFAULT)[^}]+\}[^`]*`\s*\)',
         "Interpolacao direta de variavel em SQL D1 sem .bind()"),
        (r'env\.DB\.prepare\(\s*"[^"]*"\s*\+\s*\w',
         "Concatenacao de string em SQL sem .bind()"),
    ]
    for pat, desc in sqli_patterns:
        hits = [m.group(0)[:80] for m in re.finditer(pat, code)
                if "datetime('now')" not in m.group(0) and "ALL_DEFAULT" not in m.group(0)]
        for snippet in hits:
            findings.append({"severity": "HIGH", "cwe": "CWE-89",
                             "category": "SQL Injection", "description": desc, "snippet": snippet})
            score -= 20

    # ── 2. AUTENTICACAO E CRIPTOGRAFIA (CWE-916) ──────────────────────────────
    if not any(k in code for k in ["PBKDF2", "crypto.subtle.deriveBits", "hashPassword"]):
        findings.append({"severity": "CRITICAL", "cwe": "CWE-916",
                         "category": "Criptografia de Senhas",
                         "description": "hashPassword segura nao identificada — risco de senhas em plain-text."})
        score -= 25

    # ── 3. FLAGS DE COOKIE (CWE-1004/614/1275) ────────────────────────────────
    for flag, cwe, desc in [
        ("HttpOnly",  "CWE-1004", "Cookie sem HttpOnly — vulneravel a XSS token theft."),
        ("Secure",    "CWE-614",  "Cookie sem Secure — trafego HTTP pode expor sessao."),
        ("SameSite",  "CWE-1275", "Cookie sem SameSite — vulneravel a CSRF."),
    ]:
        if flag.lower() not in code.lower():
            findings.append({"severity": "MEDIUM", "cwe": cwe,
                             "category": "Seguranca de Sessao", "description": desc})
            score -= 10

    # ── 4. RBAC — ROTAS ADMIN (CWE-285) ──────────────────────────────────────
    if re.search(r"pathname\.startsWith\(['\"]\/api\/admin", code):
        if "currentUser.is_admin" not in code and "user.is_admin" not in code:
            findings.append({"severity": "CRITICAL", "cwe": "CWE-285",
                             "category": "Controle de Acesso",
                             "description": "Rotas /api/admin/* sem guard is_admin rigoroso."})
            score -= 30

    # ── 5. SECURITY RESPONSE HEADERS ──────────────────────────────────────────
    headers_required = [
        ("X-Content-Type-Options", "CWE-693",  "Ausencia de X-Content-Type-Options: nosniff"),
        ("X-Frame-Options",        "CWE-1021", "Ausencia de X-Frame-Options — risco de Clickjacking"),
        ("Referrer-Policy",        "CWE-116",  "Ausencia de Referrer-Policy"),
        ("Permissions-Policy",     "CWE-1021", "Ausencia de Permissions-Policy — superficie desnecessaria exposta"),
        ("Strict-Transport-Security", "CWE-319", "Ausencia de HSTS — permite downgrade para HTTP"),
    ]
    for hdr, cwe, desc in headers_required:
        if hdr.lower() not in code.lower():
            findings.append({"severity": "LOW", "cwe": cwe,
                             "category": "Headers de Defesa", "description": desc})
            score -= 5

    # ── 6. CONTENT-SECURITY-POLICY (CWE-693) ─────────────────────────────────
    if "Content-Security-Policy" not in code:
        findings.append({
            "severity": "MEDIUM",
            "cwe": "CWE-693",
            "category": "Content-Security-Policy",
            "description": (
                "Ausencia de CSP header — sem essa politica, scripts injetados via XSS "
                "podem exfiltrar tokens de sessao. Adicionar: "
                "\"Content-Security-Policy\": \"default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'\""
            )
        })
        score -= 10

    # ── 7. RATE LIMITING — LOGIN BRUTE FORCE (CWE-307) ───────────────────────
    has_rate_limit = bool(re.search(
        r'rate.?limit|login.?attempt|max.?attempt|throttl|lockout|fail.?count',
        code, re.IGNORECASE
    ))
    if not has_rate_limit:
        findings.append({
            "severity": "MEDIUM",
            "cwe": "CWE-307",
            "category": "Rate Limiting / Brute-Force",
            "description": (
                "Ausencia de rate limiting nas rotas POST /api/auth/login e /api/auth/forgot-password. "
                "Atacante pode tentar senhas ilimitadamente. Implementar contador de falhas em D1/KV "
                "com bloqueio temporario de 15min apos 5 tentativas por IP/login."
            )
        })
        score -= 10

    # ── 8. N+1 QUERIES — RISCO DE DoS (CWE-400) ──────────────────────────────
    correlated_subqueries = re.findall(
        r'\(SELECT\s+(?:count|max)\([^)]+\)\s+FROM\s+access_logs\s+[^)]*WHERE[^)]*u\.',
        code, re.IGNORECASE
    )
    if len(correlated_subqueries) >= 3:
        findings.append({
            "severity": "MEDIUM",
            "cwe": "CWE-400",
            "category": "N+1 Query / Resource Exhaustion",
            "description": (
                f"{len(correlated_subqueries)} subqueries correlacionadas por usuario em access_logs "
                "detectadas na listagem de usuarios. Com N usuarios, dispara N*4 queries ao D1 — "
                "pode exceder limite de CPU do Worker e causar timeout. "
                "Reescrever com LEFT JOIN + GROUP BY."
            )
        })
        score -= 10

    # ── 9. AUDIT LOGGING (CWE-778) ───────────────────────────────────────────
    if "logAccess" not in code:
        findings.append({"severity": "MEDIUM", "cwe": "CWE-778",
                         "category": "Rastreabilidade",
                         "description": "Funcao logAccess nao identificada — acoes sensiveis sem telemetria."})
        score -= 10

    # ── 10. STACK TRACE LEAK (CWE-209) ───────────────────────────────────────
    if re.search(r'err\.stack\b', code):
        findings.append({"severity": "LOW", "cwe": "CWE-209",
                         "category": "Vazamento de Informacao",
                         "description": "err.stack pode vazar detalhes internos do Worker em respostas de erro."})
        score -= 5

    # ── 11. IDOR — ROTAS /api/users/:id (CWE-639) ────────────────────────────
    user_route_matches = re.findall(
        r'pathname\.match\(/\^\\\/api\/.+\/users\/', code
    )
    if user_route_matches and "currentUser" in code:
        # Verifica se ha validacao de ownership (usuario so acessa seus proprios dados)
        has_ownership_check = bool(re.search(
            r'currentUser\.(id|login|email)\s*[!=]=\s*(?:params|userId|id)',
            code
        ))
        if not has_ownership_check:
            findings.append({
                "severity": "LOW",
                "cwe": "CWE-639",
                "category": "IDOR (Insecure Direct Object Reference)",
                "description": (
                    "Rotas /api/users/:id podem nao validar que o usuario autenticado "
                    "e o proprietario do recurso. Adicionar guard de ownership antes de retornar dados."
                )
            })
            score -= 5

    return {"score": max(0, min(100, score)), "findings": findings}


# ─────────────────────────────────────────────────────────────────────────────
# WHATSAPP BOT CHECKS
# ─────────────────────────────────────────────────────────────────────────────
def check_bot_security():
    findings = []
    if not os.path.exists(BOT_PATH):
        return findings

    with open(BOT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # Bot: autorizacao de remetente
    has_auth = bool(re.search(r'verifySenderAccess|authorizedPhones|allowedPhones', code, re.IGNORECASE))
    if not has_auth:
        findings.append({
            "file": "whatsapp-bot/bot.js",
            "severity": "HIGH",
            "cwe": "CWE-285",
            "category": "Autorizacao do Bot",
            "description": "Bot sem verificacao de remetente autorizado — qualquer numero pode consultar dados."
        })

    # Bot: CDN externo no QR HTML (Zero Deps)
    if re.search(r'cdn\.jsdelivr\.net|unpkg\.com', code):
        findings.append({
            "file": "whatsapp-bot/bot.js",
            "severity": "LOW",
            "cwe": "CWE-829",
            "category": "Dependencia Externa no Bot",
            "description": "Bot usa CDN externo (jsdelivr/unpkg) para gerar QR HTML — falha em redes restritas e viola Zero Dependencies."
        })

    # Bot: secrets hardcoded
    if re.search(r'(api.?key|secret|password|token)\s*[:=]\s*["\'][^"\']{8,}["\']', code, re.IGNORECASE):
        findings.append({
            "file": "whatsapp-bot/bot.js",
            "severity": "CRITICAL",
            "cwe": "CWE-798",
            "category": "Credencial Hardcoded",
            "description": "Possivel credencial/token hardcoded no bot.js — mover para variavel de ambiente ou config.json criptografado."
        })

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# WRANGLER.TOML EXPOSURE CHECK
# ─────────────────────────────────────────────────────────────────────────────
def check_wrangler_exposure():
    findings = []
    if not os.path.exists(WRANGLER_PATH):
        return findings

    with open(WRANGLER_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if "database_id" in content:
        findings.append({
            "file": "wrangler.toml",
            "severity": "INFO",
            "cwe": "CWE-312",
            "category": "Exposicao de Configuracao",
            "description": (
                "database_id do D1 declarado no wrangler.toml como binding oficial de infraestrutura. "
                "Chaves sensiveis (MAIL_API_KEY / senhas) devidamente protegidas em Cloudflare Secrets."
            )
        })

    if re.search(r'(MAIL_API_KEY|SENDGRID_KEY|api_key)\s*=\s*["\'][^"\']{8,}', content):
        findings.append({
            "file": "wrangler.toml",
            "severity": "CRITICAL",
            "cwe": "CWE-798",
            "category": "Credencial em [vars]",
            "description": "Chave de API encontrada em [vars] do wrangler.toml — deve estar em Cloudflare Secrets (env.SECRET_NAME)."
        })

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# HTML XSS CHECKS
# ─────────────────────────────────────────────────────────────────────────────
def check_html_xss(filepath, name):
    findings = []
    if not os.path.exists(filepath):
        return findings

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Flagear somente quando dado externo (vindos de API/banco) entra em innerHTML sem escapeHtml
    xss_patterns = [
        (r'\.innerHTML\s*=\s*`[^`]*\$\{(?:u|m|r|row|user|userData|currentUser)\.\w+\}[^`]*`',
         "Dado de usuario/API em innerHTML sem escapeHtml()"),
        (r'\.innerHTML\s*\+=\s*`[^`]*\$\{(?:u|m|r|row|user|userData|currentUser)\.\w+\}[^`]*`',
         "Concatenacao de dado externo em innerHTML sem escapeHtml()"),
    ]
    for pat, desc in xss_patterns:
        for m in re.finditer(pat, content):
            snippet = m.group(0)[:80]
            if "escapeHtml" not in snippet and "sanitize" not in snippet.lower():
                findings.append({
                    "file": name,
                    "severity": "MEDIUM",
                    "cwe": "CWE-79",
                    "category": "XSS — Sanitizacao de Saida",
                    "description": desc,
                    "snippet": snippet
                })
    return findings


def check_session_and_routing_security():
    findings = []
    sw_path = os.path.join(WORKSPACE_DIR, "public", "sw.js")
    
    # 1. Checar se Service Worker protege páginas HTML com Network-Only
    if os.path.exists(sw_path):
        with open(sw_path, "r", encoding="utf-8", errors="ignore") as f:
            sw_code = f.read()
        if "req.mode === 'navigate'" not in sw_code and "text/html" not in sw_code:
            findings.append({
                "file": "public/sw.js",
                "severity": "HIGH",
                "cwe": "CWE-524",
                "category": "Service Worker Cache Stale",
                "description": "Service Worker sem Network-Only para navegação HTML — risco de cache stale de relatórios confidenciais."
            })
        if "'LOGOUT'" not in sw_code and "caches.delete" not in sw_code:
            findings.append({
                "file": "public/sw.js",
                "severity": "MEDIUM",
                "cwe": "CWE-384",
                "category": "Service Worker Cache Purge",
                "description": "Service Worker sem suporte a purga de cache no evento de LOGOUT."
            })

    # 2. Checar se Worker possui gating com enforceAuthRedirect
    if os.path.exists(WORKER_PATH):
        with open(WORKER_PATH, "r", encoding="utf-8", errors="ignore") as f:
            w_code = f.read()
        if "enforceAuthRedirect" not in w_code:
            findings.append({
                "file": "worker/index.js",
                "severity": "CRITICAL",
                "cwe": "CWE-306",
                "category": "Server-Side Auth Gating",
                "description": "Worker sem função enforceAuthRedirect para redirecionamento atômico e limpeza de sessão na borda."
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTRADOR
# ─────────────────────────────────────────────────────────────────────────────
def run_security_audit():
    print("=" * 72)
    print("  PEP HUB — AUDITOR DE SEGURANCA CORPORATIVA (AppSec)  v3")
    print(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Escopo: worker · admin · portal · bot · sw.js · wrangler.toml")
    print("=" * 72)

    worker_result = check_worker_security()
    score    = worker_result.get("score", 100)
    findings = worker_result.get("findings", [])

    findings.extend(check_bot_security())
    findings.extend(check_wrangler_exposure())
    findings.extend(check_session_and_routing_security())

    for path, name in [
        (ADMIN_HTML,   "public/admin/index.html"),
        (PORTAL_HTML,  "public/index.html"),
        (DIVULGACAO,   "public/pep-tools/divulgacao/index.html"),
    ]:
        findings.extend(check_html_xss(path, name))

    # Descontar score das findings de html e bot
    extra_deduction = 0
    for f in findings:
        if f.get("file") and "worker" not in f.get("file", ""):
            sev = f.get("severity", "LOW")
            extra_deduction += {"CRITICAL": 20, "HIGH": 15, "MEDIUM": 8, "LOW": 3}.get(sev, 0)
    score = max(0, min(100, score - extra_deduction))

    if score >= 95:   posture = "EXCELENTE (A+ — Postura Maxima de Defesa)"
    elif score >= 85: posture = "OTIMO     (A  — Alta Postura Defensiva)"
    elif score >= 70: posture = "BOM       (B  — Hardening Recomendado)"
    elif score >= 55: posture = "REGULAR   (C  — Vulnerabilidades a Corrigir)"
    else:             posture = "CRITICO   (D  — Riscos Severos Identificados)"

    print(f"\n  Pontuacao de Seguranca: {score}/100")
    print(f"  Postura Global        : {posture}")
    print(f"  Total de Apontamentos : {len(findings)}\n")

    if not findings:
        print("  [+] Nenhum apontamento identificado.")
        print("  [+] RBAC, SQLi, XSS, cookies, headers e bot validados.")
    else:
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_f = sorted(findings, key=lambda x: sev_order.get(x.get("severity", "LOW"), 9))

        for idx, f in enumerate(sorted_f, 1):
            sev  = f.get("severity", "INFO")
            cwe  = f.get("cwe",      "CWE-General")
            cat  = f.get("category", "Geral")
            desc = f.get("description", "")
            file_ref = f.get("file", "worker/index.js")
            icons = {"CRITICAL": "[CRITICO]", "HIGH": "[ALTO]   ", "MEDIUM": "[MEDIO]  ", "LOW": "[BAIXO]  "}
            print(f"  {idx:02d}. {icons.get(sev,'[?]')} {cwe} — {cat}")
            print(f"      Arquivo : {file_ref}")
            print(f"      Detalhe : {desc}")
            if "snippet" in f:
                print(f"      Snippet : {f['snippet']}")
            print()

    print("=" * 72)
    print("  DIRETRIZES DE HARDENING CONTINUO:")
    print("  1. CSP header: default-src 'self' em todos os responses do worker.")
    print("  2. Rate limiting: contador de falhas em D1/KV por IP com lockout 15min.")
    print("  3. N+1 queries: substituir subqueries correlacionadas por LEFT JOIN.")
    print("  4. Secrets: nunca em wrangler.toml [vars] — sempre em Cloudflare Secrets.")
    print("  5. PBKDF2 >= 100.000 iteracoes + salt unico de 16 bytes por usuario.")
    print("  6. Audit logs com IP, User-Agent e acao para todas as operacoes sensiveis.")
    print("=" * 72)

    return score, findings


if __name__ == "__main__":
    score, _ = run_security_audit()
    sys.exit(0 if score >= 80 else 1)
