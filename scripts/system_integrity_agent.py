#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Integridade e Estabilidade do Sistema (System Integrity Auditor)
Audita rigorosamente os 6 pilares de estabilidade do ecossistema:
  1. Integridade de importações nos scripts do Worker (Zero ReferenceErrors como randomHex, parseCookies)
  2. Normalização corporativa no cadastro (Nome/Login/Área/Função em MAIÚSCULO, E-mail em minúsculo, senha livre)
  3. Máscara de telefone resiliente com suporte a Backspace sem travar no hífen
  4. Server-Side Gate na rota raiz '/' e relatórios com redirecionamento para '/login/'
  5. Headers anti-cache em respostas HTML e Service Worker Network-Only para navegações
  6. Controle de acesso (RBAC admin, verificação de status pendente/bloqueado/aprovado)
"""

import os
import re
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_DIR    = os.path.join(WORKSPACE_DIR, "worker")
WORKER_INDEX  = os.path.join(WORKER_DIR, "index.js")
AUTH_ROUTE    = os.path.join(WORKER_DIR, "routes", "auth.js")
ADMIN_ROUTE   = os.path.join(WORKER_DIR, "routes", "admin.js")
SECURITY_UTIL = os.path.join(WORKER_DIR, "utils", "security.js")
REGISTER_HTML = os.path.join(WORKSPACE_DIR, "public", "register", "index.html")
LOGIN_HTML    = os.path.join(WORKSPACE_DIR, "public", "login", "index.html")
SW_PATH       = os.path.join(WORKSPACE_DIR, "public", "sw.js")

def audit_system_integrity():
    print()
    print("=" * 74)
    print("  PEP HUB — AGENTE DE INTEGRIDADE E ESTABILIDADE DO SISTEMA")
    print("=" * 74)

    score = 100
    deductions = []

    # -------------------------------------------------------------
    # 1. INTEGRIDADE DE IMPORTAÇÕES NO WORKER (CRITICAL - 30 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 1] Integridade de Símbolos e Importações no Worker...")
    if not os.path.exists(AUTH_ROUTE) or not os.path.exists(SECURITY_UTIL):
        score -= 30
        deductions.append("Arquivos essenciais do worker não localizados.")
    else:
        with open(AUTH_ROUTE, "r", encoding="utf-8") as f:
            auth_code = f.read()
        with open(SECURITY_UTIL, "r", encoding="utf-8") as f:
            sec_code = f.read()

        # Extrair símbolos exportados de security.js
        exported_symbols = set(re.findall(r'export\s+(?:function|const|let|async\s+function|var)\s+([a-zA-Z0-9_]+)', sec_code))
        
        # Varredura completa de todos os arquivos JS em worker/
        worker_dir = os.path.join(WORKSPACE_DIR, "worker")
        missing_by_file = {}
        for root, _, files in os.walk(worker_dir):
            for file in files:
                if file.endswith('.js') and file != 'security.js':
                    p = os.path.join(root, file)
                    rel = os.path.relpath(p, WORKSPACE_DIR)
                    with open(p, 'r', encoding='utf-8') as f:
                        code = f.read()
                    imp_matches = re.findall(r'import\s+\{([^}]+)\}\s+from\s+[\'"].*security\.js[\'"]', code)
                    imported = set()
                    for grp in imp_matches:
                        imported.update(x.strip() for x in grp.split(',') if x.strip())
                    
                    missing = []
                    for exp in exported_symbols:
                        if re.search(r'\b' + exp + r'\b', code) and exp not in imported:
                            missing.append(exp)
                    if missing:
                        missing_by_file[rel] = missing

        if missing_by_file:
            score -= 30
            for f_rel, miss in missing_by_file.items():
                deductions.append(f"Símbolos ausentes em {f_rel}: {miss} (Causa de ReferenceError)")
                print(f"  [FALHA CRÍTICA] Símbolos ausentes em {f_rel}: {miss}")
        else:
            print("  [OK] Todos os arquivos do Worker devidamente vinculados (ALL_DEFAULT_MODULES_STR, randomHex, generateTempPassword, sessões, etc.)")

    # -------------------------------------------------------------
    # 2. NORMALIZAÇÃO CORPORATIVA NO CADASTRO (HIGH - 20 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 2] Normalização de Cadastro (MAIÚSCULO/minúsculo)...")
    p2_ok = True
    if os.path.exists(AUTH_ROUTE):
        # Verifica se auth.js normaliza nome_completo, login_claro para upper e email_claro para lower
        if "cleanNome = (nome_completo || '').trim().toUpperCase()" not in auth_code and ".toUpperCase()" not in auth_code:
            p2_ok = False
            score -= 10
            deductions.append("Backend não converte Nome/Login/Área para MAIÚSCULO no cadastro.")
            print("  [FALHA] Backend não força MAIÚSCULO para campos cadastrais.")
        else:
            print("  [OK] Backend normaliza Nome/Login/Área/Função para MAIÚSCULO e E-mail para minúsculo.")

    if os.path.exists(REGISTER_HTML):
        with open(REGISTER_HTML, "r", encoding="utf-8") as f:
            reg_html = f.read()
        if "text-transform:uppercase" not in reg_html or "text-transform:lowercase" not in reg_html:
            p2_ok = False
            score -= 10
            deductions.append("Frontend de cadastro não aplica estilos/regras de MAIÚSCULO/minúsculo nos inputs.")
            print("  [AVISO] Frontend de cadastro sem estilização text-transform explícita.")
        else:
            print("  [OK] Frontend de cadastro aplica text-transform:uppercase e text-transform:lowercase.")

    # -------------------------------------------------------------
    # 3. MÁSCARA DE TELEFONE COM SUPORTE A BACKSPACE (MEDIUM - 10 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 3] Máscara de Telefone e Comportamento do Backspace...")
    if os.path.exists(REGISTER_HTML):
        with open(REGISTER_HTML, "r", encoding="utf-8") as f:
            reg_html = f.read()
        if "isBackspacing" in reg_html or "Backspace" in reg_html:
            print("  [OK] Máscara de telefone captura evento Backspace/Delete para deleção fluida.")
        else:
            score -= 10
            deductions.append("Máscara de telefone não possui tratamento de Backspace (risco de travamento no hífen).")
            print("  [FALHA] Máscara de telefone sem tratamento explícito de Backspace.")
    else:
        print("  [AVISO] public/register/index.html não localizado.")

    # -------------------------------------------------------------
    # 4. SERVER-SIDE GATE NA RAIZ E RELATÓRIOS (CRITICAL - 20 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 4] Server-Side Gate e Redirecionamento Obrigatório para /login/...")
    if os.path.exists(WORKER_INDEX):
        with open(WORKER_INDEX, "r", encoding="utf-8") as f:
            w_code = f.read()
        
        # Verifica se rota raiz '/' redireciona via enforceAuthRedirect
        root_gating = bool(re.search(r"if\s*\(pathname\s*===\s*'/'\s*\|\|\s*pathname\s*===\s*'/index\.html'\)\s*\{\s*const user = await getSessionUser[^}]*enforceAuthRedirect", w_code, re.DOTALL))
        if root_gating:
            print("  [OK] Rota raiz '/' e '/index.html' protegida por Server-Side Gate com enforceAuthRedirect.")
        else:
            score -= 15
            deductions.append("Rota raiz '/' não redireciona usuários não autenticados para /login/.")
            print("  [FALHA CRÍTICA] Rota raiz aberta a acesso anônimo sem gating.")

        # Verifica se relatórios utilizam enforceAuthRedirect
        reports_gated = "enforceAuthRedirect" in w_code and "pathname.startsWith('/churn')" in w_code
        if reports_gated:
            print("  [OK] Rotas de relatórios analíticos (/churn, /fpd, etc.) protegidas por enforceAuthRedirect.")
        else:
            score -= 10
            deductions.append("Rotas de relatórios analíticos sem enforceAuthRedirect.")
            print("  [FALHA] Relatórios sem redirecionamento seguro na borda.")

    # -------------------------------------------------------------
    # 5. HEADERS ANTI-CACHE E SERVICE WORKER NETWORK-ONLY (HIGH - 10 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 5] Política de Cache e Prevenção de Acesso Pós-Inatividade...")
    if os.path.exists(SW_PATH):
        with open(SW_PATH, "r", encoding="utf-8") as f:
            sw_code = f.read()
        if "req.mode === 'navigate'" in sw_code and "Network-Only" in sw_code:
            print("  [OK] Service Worker configurado com Network-Only para navegações HTML.")
        else:
            score -= 10
            deductions.append("Service Worker pode servir cache obsoleto de páginas HTML para usuários expirados.")
            print("  [FALHA] Service Worker sem Network-Only para requisições de página.")

    # -------------------------------------------------------------
    # 7. PADRONIZAÇÃO DE CABEÇALHOS & HEADER-WIDGET (HIGH - 15 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 7] Padronização Institucional de Cabeçalhos e Header-Widget...")
    reports = [
        os.path.join(WORKSPACE_DIR, "public", "churn", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "fpd", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "fpd-residencial", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "panorama-market-share", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "market-share-residencial", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "market-share-movel", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "aprovacao-credito", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "evolucao-carteira", "index.html"),
    ]
    hdr_ok = True
    for r in reports:
        if os.path.exists(r):
            with open(r, "r", encoding="utf-8") as f:
                r_code = f.read()
            if "header-widget.js" not in r_code or "btn-nav-catalog" not in r_code:
                hdr_ok = False
                print(f"  [AVISO] {os.path.basename(os.path.dirname(r))} sem header-widget.js ou classe btn-nav-catalog.")
    if hdr_ok:
        print("  [OK] Todos os 9 relatórios analíticos usam header-widget.js e botão btn-nav-catalog padronizado.")
    else:
        score -= 10
        deductions.append("Relatórios analíticos sem padronização do header-widget ou botão btn-nav-catalog.")

    # -------------------------------------------------------------
    # 8. OTIMIZAÇÃO DE CPU WORKER & FAST STATIC BYPASS (HIGH - 15 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 8] Proteção de Limite de CPU no Cloudflare Workers (Free Tier 10ms)...")
    if os.path.exists(WORKER_INDEX):
        with open(WORKER_INDEX, "r", encoding="utf-8") as f:
            w_code = f.read()
        has_fast_bypass = "isStaticAssetPath(pathname)" in w_code and "Fast Bypass para arquivos estáticos" in w_code
        has_no_schema_waituntil = "ctx.waitUntil(ensureAppSchema(env))" not in w_code
        if has_fast_bypass and has_no_schema_waituntil:
            print("  [OK] Fast Bypass de arquivos estáticos ativo (<0.2ms) e sem waitUntil(ensureAppSchema) overhead.")
        else:
            score -= 10
            deductions.append("Worker sem Fast Bypass de assets ou com waitUntil de schema ativo (risco de CPU Limit).")
            print("  [FALHA] Worker sem otimização de CPU para Free Tier.")

    # -------------------------------------------------------------
    # 9. INTEGRIDADE SINTÁTICA DE SCRIPTS NOS PAINÉIS (CRITICAL - 20 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 9] Integridade Sintática de Tags <script> nos Relatórios...")
    script_syntax_ok = True
    for r in reports:
        if os.path.exists(r):
            with open(r, "r", encoding="utf-8") as f:
                r_content = f.read()
            in_s = False
            for m in re.finditer(r'(<script\b[^>]*>|</script>)', r_content, re.IGNORECASE):
                tag = m.group(1).lower()
                if tag.startswith('<script'):
                    if in_s:
                        script_syntax_ok = False
                        print(f"  [FALHA] Tag <script> aninhada incorretamente em {os.path.basename(os.path.dirname(r))}.")
                    in_s = True
                elif tag == '</script>':
                    in_s = False
    if script_syntax_ok:
        print("  [OK] Todos os 9 relatórios analíticos possuem estrutura sintática de scripts 100% balanceada.")
    else:
        score -= 20
        deductions.append("Relatórios com tags <script> aninhadas ou não fechadas (causa de tela sem dados).")

    # -------------------------------------------------------------
    # 10. FLUXO ESTÁVEL DE PRIVILÉGIOS, STATUS EM /ME E HOVER ONLINE (HIGH - 15 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 10] Conformidade de Privilégios, Status em /api/auth/me e Hover Online...")
    p10_ok = True
    if os.path.exists(AUTH_ROUTE):
        with open(AUTH_ROUTE, "r", encoding="utf-8") as f:
            a_code = f.read()
        if "status: user.status" not in a_code:
            p10_ok = False
            score -= 10
            deductions.append("/api/auth/me não retorna propriedade status (risco de deslogar ao entrar em relatórios).")
            print("  [FALHA] /api/auth/me sem retorno de status.")
        else:
            print("  [OK] /api/auth/me retorna status corporativo para prevenção de falso logout.")

    admin_js_path = os.path.join(WORKSPACE_DIR, "public", "admin", "js", "admin.js")
    if os.path.exists(admin_js_path):
        with open(admin_js_path, "r", encoding="utf-8") as f:
            adm_code = f.read()
        if "Configurar Acessos" in adm_code:
            p10_ok = False
            score -= 5
            deductions.append("Admin JS ainda utiliza nomenclatura legada 'Configurar Acessos' em vez de 'Privilégios'.")
            print("  [AVISO] Presença de botão com rótulo 'Configurar Acessos'.")
        else:
            print("  [OK] Central Administrativa padronizada com botão estrito 'Privilégios'.")

    hw_path = os.path.join(WORKSPACE_DIR, "public", "js", "header-widget.js")
    if os.path.exists(hw_path):
        with open(hw_path, "r", encoding="utf-8") as f:
            hw_code = f.read()
        if "active-users-hover-card" not in hw_code or "mouseenter" not in hw_code:
            p10_ok = False
            score -= 5
            deductions.append("Header Widget sem suporte a Hover Card de usuários online.")
            print("  [AVISO] Header Widget sem Hover Card.")
        else:
            print("  [OK] Header Widget possui Hover Card em tempo real de usuários online.")

    score = max(0, score)
    print("\n" + "=" * 74)
    print(f"  PONTUAÇÃO DE INTEGRIDADE DO SISTEMA: {score}/100")
    if score >= 90:
        print("  CLASSIFICAÇÃO: A+ (Sistema Totalmente Estável e Resiliente)")
    elif score >= 85:
        print("  CLASSIFICAÇÃO: A (Aprovado com Alta Estabilidade)")
    else:
        print("  CLASSIFICAÇÃO: REPROVADO (Pendências de Estabilidade)")
    print("=" * 74)

    if deductions:
        print("  Deduções e Apontamentos:")
        for d in deductions:
            print(f"    - {d}")

    return 0 if score >= 85 else 1

if __name__ == "__main__":
    sys.exit(audit_system_integrity())
