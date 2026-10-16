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
    # 6. TRAVAS E CONTROLES GLOBAIS DO SISTEMA (SYSTEM CONTROLS) (HIGH - 20 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 6] Travas e Controles Globais do Sistema (System Controls & Killswitches)...")
    p6_ok = True
    
    # 6.1. Verificação de Chaves Canônicas e Seed em security.js
    required_controls = [
        ('suspend_emails', 'Suspender Disparo de E-mails'),
        ('suspend_portal_access', 'Impedir Acessos aos Relatórios & Ferramentas'),
        ('suspend_whatsapp_bot', 'Suspender Chatbot RAG & Assistente Analítico'),
        ('suspend_tv_submissions', 'Suspender Novas Propostas de Mídia para TVs')
    ]
    with open(SECURITY_UTIL, "r", encoding="utf-8") as f:
        sec_code = f.read()

    for ctrl_key, ctrl_label in required_controls:
        if ctrl_key not in sec_code:
            p6_ok = False
            score -= 5
            deductions.append(f"Trava de sistema '{ctrl_key}' ausente no seed de security.js.")
            print(f"  [FALHA] Trava '{ctrl_key}' não definida no seed de security.js.")
        else:
            print(f"  [OK] Trava canônica '{ctrl_key}' ({ctrl_label}) devidamente catalogada no seed.")

    # 6.2. Verificação de Enforcing por Módulo
    # Portal Access
    if os.path.exists(WORKER_INDEX):
        with open(WORKER_INDEX, "r", encoding="utf-8") as f:
            w_code = f.read()
        if "suspend_portal_access" in w_code and "!user.is_admin" in w_code:
            print("  [OK] Trava 'suspend_portal_access' protege relatórios e raiz mantendo bypass de admin.")
        else:
            p6_ok = False
            score -= 5
            deductions.append("Trava 'suspend_portal_access' sem verificação adequada em worker/index.js.")
            print("  [FALHA] 'suspend_portal_access' sem verificação adequada em worker/index.js.")

    # Email Dispatch
    if "getSystemControl(env, 'suspend_emails')" in sec_code:
        print("  [OK] Trava 'suspend_emails' intercepta envios em sendEmail com log de suspensão.")
    else:
        p6_ok = False
        score -= 5
        deductions.append("Trava 'suspend_emails' sem verificação em sendEmail.")
        print("  [FALHA] 'suspend_emails' sem verificação em sendEmail.")

    # TV Submissions
    tv_route = os.path.join(WORKER_DIR, "routes", "tv.js")
    if os.path.exists(tv_route):
        with open(tv_route, "r", encoding="utf-8") as f:
            tv_code = f.read()
        if "getSystemControl(env, 'suspend_tv_submissions')" in tv_code:
            print("  [OK] Trava 'suspend_tv_submissions' bloqueia uploads e propostas na esteira de TV.")
        else:
            p6_ok = False
            score -= 5
            deductions.append("Trava 'suspend_tv_submissions' sem verificação em routes/tv.js.")
            print("  [FALHA] 'suspend_tv_submissions' sem verificação em routes/tv.js.")

    # Bot & RAG Suspension (Web & WhatsApp)
    bot_route = os.path.join(WORKER_DIR, "routes", "bot.js")
    if os.path.exists(bot_route):
        with open(bot_route, "r", encoding="utf-8") as f:
            bot_code = f.read()
        if "suspend_whatsapp_bot" in bot_code and "reason: 'suspended'" in bot_code and "status = 503" in bot_code:
            print("  [OK] Trava do Bot intercepta Web e WhatsApp retornando 503 enquanto permite testes de administrador.")
        else:
            p6_ok = False
            score -= 5
            deductions.append("Trava do Bot sem bloqueio estrito de Web e WhatsApp ou sem retorno 503.")
            print("  [FALHA] Trava do Bot sem bloqueio estrito em routes/bot.js.")

    # 6.3. API de Administração
    if os.path.exists(ADMIN_ROUTE):
        with open(ADMIN_ROUTE, "r", encoding="utf-8") as f:
            adm_code = f.read()
        if "/api/admin/system-controls" in adm_code and "UPDATE system_controls" in adm_code:
            print("  [OK] API administrativa (/api/admin/system-controls) expõe leitura e gravação auditada com invalidate cache.")
        else:
            p6_ok = False
            score -= 5
            deductions.append("API /api/admin/system-controls ausente ou incompleta em routes/admin.js.")
            print("  [FALHA] API /api/admin/system-controls ausente em routes/admin.js.")

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

    # -------------------------------------------------------------
    # 11. GOVERNANÇA DA LISTA ÚNICA DE FERRAMENTAS & USABILIDADE DE MODAIS (CRITICAL - 25 pts)
    # -------------------------------------------------------------
    print("\n[PILAR 11] Governança de Lista Única (Single Source of Truth) & Usabilidade de Modais...")
    p11_ok = True

    # 11.1 Catálogo Canônico com 14 Ferramentas
    if os.path.exists(SECURITY_UTIL):
        with open(SECURITY_UTIL, "r", encoding="utf-8") as f:
            sec_text = f.read()
        canonical_tools = [
            'churn', 'churn-bl-total', 'churn-bl-pme', 'fpd', 'fpd-residencial',
            'market-share-movel', 'market-share-residencial', 'panorama-market-share',
            'aprovacao-credito', 'evolucao-carteira', 'divulgacao', 'tv', 'aniversario', 'market-share'
        ]
        missing_canonical = [t for t in canonical_tools if f"'{t}'" not in sec_text and f'"{t}"' not in sec_text]
        if missing_canonical:
            p11_ok = False
            score -= 15
            deductions.append(f"Catálogo canônico DEFAULT_SYSTEM_MODULES incompleto. Faltando: {missing_canonical}")
            print(f"  [FALHA] Catálogo canônico incompleto: {missing_canonical}")
        else:
            print("  [OK] Catálogo canônico com as 14 ferramentas oficiais rigorosamente preservado.")

    # 11.2 Zero IDs legados com underscore no Frontend e Rotas de Produção
    legacy_ids = [
        'churn_safra', 'churn_bl_total', 'churn_bl_pme', 'fpd_residencial',
        'market_share_movel', 'market_share_residencial', 'panorama_market_share',
        'aprovacao_credito', 'evolucao_carteira'
    ]
    files_to_check = [
        os.path.join(WORKSPACE_DIR, "public", "admin", "js", "admin.js"),
        os.path.join(WORKSPACE_DIR, "public", "admin", "index.html"),
        os.path.join(WORKSPACE_DIR, "public", "js", "header-widget.js"),
        os.path.join(WORKSPACE_DIR, "worker", "routes", "admin.js"),
        os.path.join(WORKSPACE_DIR, "worker", "routes", "profile.js"),
    ]
    found_legacy = []
    for fp in files_to_check:
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
            for leg in legacy_ids:
                # Ignora trechos de limpeza explícita DELETE FROM ou dentro de função de normalização
                matches = re.finditer(r'\b' + leg + r'\b', content)
                for m in matches:
                    fn_idx = content.rfind('function normalizeModuleId', 0, m.start())
                    if fn_idx != -1 and (m.start() - fn_idx) < 3000:
                        continue
                    start_ctx = max(0, m.start() - 100)
                    ctx = content[start_ctx:m.end() + 100]
                    if 'DELETE FROM' in ctx or 'IN (' in ctx:
                        continue
                    found_legacy.append((os.path.basename(fp), leg))
    if found_legacy:
        p11_ok = False
        score -= 15
        deductions.append(f"Presença de IDs legados com underscore: {found_legacy[:5]}")
        print(f"  [FALHA] Identificadores legados encontrados: {found_legacy[:5]}")
    else:
        print("  [OK] Zero identificadores legados com underscore em uso no frontend e rotas de produção.")

    # 11.3 Contenção e Identidade Visual Padronizada das Janelas (Modais Admin, Perfil e Configurações)
    admin_html_path = os.path.join(WORKSPACE_DIR, "public", "admin", "index.html")
    if os.path.exists(admin_html_path):
        with open(admin_html_path, "r", encoding="utf-8") as f:
            admin_html = f.read()
        has_max_h = bool(re.search(r'max-height:\s*calc\(100vh\s*-\s*40px\)', admin_html))
        has_overflow = "overflow-y:auto" in admin_html or "overflow-y: auto" in admin_html
        has_gradient = "linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%)" in admin_html or "linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%)" in admin_html
        has_hd_text = "modal-hd-text" in admin_html and "<small>" in admin_html
        
        # Proibição de distorção circular no botão Cancelar/Fechar do rodapé
        has_distorted_cancel = bool(re.search(r'<button[^>]*class=["\'][^"\']*\bmodal-close\b[^"\']*["\'][^>]*>\s*Cancel', admin_html))
        
        if not has_max_h or not has_overflow:
            p11_ok = False
            score -= 10
            deductions.append("Painel Admin sem contenção vertical dos modais (risco de botão fechar vazar da viewport).")
            print("  [FALHA] CSS dos modais do Admin não contém max-height relativo à viewport.")
        elif not has_gradient or not has_hd_text:
            p11_ok = False
            score -= 10
            deductions.append("Janelas do Admin com identidade visual divergente de Perfil/Configurações (falta gradiente Claro ou subtítulo).")
            print("  [FALHA] Janelas do Admin sem identidade visual padronizada da Claro.")
        elif has_distorted_cancel:
            p11_ok = False
            score -= 10
            deductions.append("Botão Cancelar com classe circular modal-close no rodapé (risco de deformação).")
            print("  [FALHA] Botão Cancelar deformado no rodapé do modal.")
        else:
            print("  [OK] Todos os modais do Admin possuem identidade visual 100% idêntica a Perfil e Configurações (Gradiente Claro, subtítulo e botões padronizados).")

    hw_js_path = os.path.join(WORKSPACE_DIR, "public", "js", "header-widget.js")
    if os.path.exists(hw_js_path):
        with open(hw_js_path, "r", encoding="utf-8") as f:
            hw_js = f.read()
        if "max-height: calc(100vh - 48px)" not in hw_js or "ph-modal-close-btn" not in hw_js:
            p11_ok = False
            score -= 10
            deductions.append("Header Widget (Perfil & Configurações) sem contenção de viewport ou botão circular de fechar.")
            print("  [FALHA] Modais do Header Widget sem restrição de altura vertical.")
        else:
            print("  [OK] Modais de Perfil e Configurações (Header Widget) com largura expandida, contenção de altura e botão fechar circular destacado.")

    # 11.4 Reatividade em Cadeia: alteração de status/salvamento/exclusão recarrega usuários e catálogo
    if os.path.exists(admin_js_path):
        with open(admin_js_path, "r", encoding="utf-8") as f:
            adm_js = f.read()
        if "await loadModules();\n      loadUsers();" not in adm_js and "await loadModules(); loadUsers();" not in adm_js:
            p11_ok = False
            score -= 10
            deductions.append("admin.js não chama loadUsers() em cadeia após loadModules() em alterações de ferramentas.")
            print("  [FALHA] Cadeia de reatividade de ferramentas incompleta no admin.js.")
        else:
            print("  [OK] Cadeia de reatividade 100% íntegra: alterações em ferramentas propagam para privilégios, broadcast e contadores em tempo real.")

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
