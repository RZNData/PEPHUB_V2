"""
Script de Publicação de Relatórios e Sincronização do Arcabouço do Pephub
Uso:
  python publish_report.py <nome_relatorio>   # Ex: python publish_report.py market_share_residencial
  python publish_report.py --all              # Publica todos os relatórios e sincroniza o arcabouço
  python publish_report.py --sync             # Apenas sincroniza o catálogo em todas as ferramentas, admin e D1
  python publish_report.py --list             # Lista todos os relatórios configurados
  python publish_report.py --all --deploy     # Publica, sincroniza e executa wrangler deploy
"""

import os
import sys
import json
import re
import shutil
import subprocess

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(ROOT_DIR, "relatorios")
PUBLIC_DIR = os.path.join(ROOT_DIR, "public")
SECURITY_JS = os.path.join(ROOT_DIR, "worker", "utils", "security.js")
ADMIN_HTML = os.path.join(ROOT_DIR, "public", "admin", "index.html")

# Ferramentas operacionais nativas fixas (PeP Tools)
BUILTIN_TOOLS = [
    {
        "id": "divulgacao",
        "name": "Divulgação Corporativa (TVs)",
        "short_name": "TV Divulgação",
        "section": "PeP Tools & Operações",
        "description": "Propostas de mídia, curadoria e exibição nas TVs da Regional",
        "route": "/pep-tools/divulgacao/",
        "status": "ativo",
        "sort_order": 7,
        "bot_enabled": False
    },
    {
        "id": "tv",
        "name": "Player TV (16:9 Fullscreen)",
        "short_name": "Player TV",
        "section": "PeP Tools & Operações",
        "description": "Acesso direto ao reprodutor widescreen para recepções e salas",
        "route": "/pep-tools/divulgacao/tv.html",
        "status": "ativo",
        "sort_order": 8,
        "bot_enabled": False
    }
]

def get_all_catalog_modules():
    """Descobre todos os relatórios em relatorios/ e mescla com as ferramentas nativas."""
    modules = []
    if not os.path.exists(REPORTS_DIR):
        return BUILTIN_TOOLS

    order_idx = 1
    # Pastas de relatórios analíticos
    for item in sorted(os.listdir(REPORTS_DIR)):
        if item.startswith("_"):
            continue
        rep_path = os.path.join(REPORTS_DIR, item)
        if not os.path.isdir(rep_path):
            continue

        cfg_file = os.path.join(rep_path, "report_config.json")
        cfg = {}
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass

        mod_id = cfg.get("id", item.replace("_", "-"))
        titulo = cfg.get("titulo", item)
        short_name = cfg.get("nome_curto", titulo[:16].strip())
        section = cfg.get("categoria", "Painéis & Indicadores Analíticos")
        descricao = cfg.get("descricao", "")
        rota = cfg.get("rota_pephub", item.replace("_", "-"))
        route = f"/{rota}/"
        status = cfg.get("status", "ativo")
        sort_order = cfg.get("sort_order", order_idx)
        bot_enabled = bool(cfg.get("bot_enabled", False))

        modules.append({
            "folder": item,
            "id": mod_id,
            "name": titulo,
            "short_name": short_name,
            "section": section,
            "description": descricao,
            "route": route,
            "status": status,
            "sort_order": sort_order,
            "bot_enabled": bot_enabled
        })
        order_idx += 1

    # Adicionar ferramentas nativas
    for bt in BUILTIN_TOOLS:
        modules.append(bt)

    modules.sort(key=lambda m: (m.get("section", ""), m.get("sort_order", 999)))
    return modules

def list_reports():
    modules = get_all_catalog_modules()
    print("\n📊 Catálogo Unificado de Relatórios & Ferramentas da Regional Norte:")
    for m in modules:
        folder = m.get("folder", "[nativo]")
        bot_tag = "🤖 Bot Ativo" if m.get("bot_enabled") else "⚪ Somente Web"
        print(f"  • {m['id']:<26} [{m['section']}] -> {m['route']:<26} ({bot_tag})")
    print(f"\nTotal: {len(modules)} ferramentas catalogadas.\n")
    return modules

def sync_architecture(execute_d1_remote=True):
    """
    Sincroniza automaticamente todo o arcabouço da plataforma:
    1. worker/utils/security.js (ALL_SYSTEM_MODULES, DEFAULT_SYSTEM_MODULES)
    2. public/admin/index.html (SYSTEM_SECTIONS fallback, delegationScopeSelect)
    3. Cloudflare D1 (system_modules remote upsert)
    """
    print("\n🔄 Sincronizando todo o arcabouço da plataforma Pephub...")
    modules = get_all_catalog_modules()

    # 1. Sincronizar worker/utils/security.js
    if os.path.exists(SECURITY_JS):
        try:
            with open(SECURITY_JS, "r", encoding="utf-8") as f:
                sec_code = f.read()

            all_ids = [m["id"] for m in modules]
            ids_js = ",\n  ".join([f"'{mid}'" for mid in all_ids])
            new_all_sys = f"export const ALL_SYSTEM_MODULES = [\n  {ids_js}\n];"

            sec_code = re.sub(
                r"export const ALL_SYSTEM_MODULES = \[\s*[\s\S]*?\s*\];",
                new_all_sys,
                sec_code
            )

            # Sincronizar DEFAULT_SYSTEM_MODULES
            tuples_list = []
            for m in modules:
                name_esc = m['name'].replace("'", "\\'")
                short_esc = m['short_name'].replace("'", "\\'")
                desc_esc = m['description'].replace("'", "\\'")
                tuples_list.append(
                    f"  ['{m['id']}', '{name_esc}', '{short_esc}', '{m['section']}', '{desc_esc}', '{m['route']}', '{m['status']}', {m['sort_order']}]"
                )
            tuples_js = ",\n".join(tuples_list)
            new_def_mods = f"export const DEFAULT_SYSTEM_MODULES = [\n{tuples_js}\n];"

            sec_code = re.sub(
                r"export const DEFAULT_SYSTEM_MODULES = \[\s*[\s\S]*?\s*\];",
                new_def_mods,
                sec_code
            )

            with open(SECURITY_JS, "w", encoding="utf-8") as f:
                f.write(sec_code)
            print("  ✅ worker/utils/security.js atualizado com sucesso.")
        except Exception as e:
            print(f"  ⚠️ Erro ao atualizar security.js: {e}")

    # 2. Sincronizar public/admin/index.html
    if os.path.exists(ADMIN_HTML):
        try:
            with open(ADMIN_HTML, "r", encoding="utf-8") as f:
                admin_code = f.read()

            # Agrupar por seção
            sections_map = {}
            for m in modules:
                sec = m["section"]
                if sec not in sections_map:
                    sec_key = re.sub(r"[^a-z0-9]", "_", sec.lower())
                    sections_map[sec] = {
                        "name": sec,
                        "key": sec_key,
                        "modules": []
                    }
                sections_map[sec]["modules"].append({
                    "id": m["id"],
                    "name": m["name"],
                    "short": m["short_name"],
                    "desc": m["description"]
                })

            sections_json = json.dumps(list(sections_map.values()), ensure_ascii=False, indent=2)
            new_sec_js = f"let SYSTEM_SECTIONS = {sections_json};"

            admin_code = re.sub(
                r"let SYSTEM_SECTIONS = \[\s*[\s\S]*?\s*\];",
                new_sec_js,
                admin_code
            )

            # Atualizar opções estáticas do delegationScopeSelect
            scope_opts = ['              <option value="ALL">Todos os Relatórios & Insumos (Geral)</option>']
            for m in modules:
                scope_opts.append(f'              <option value="{m["id"]}">{m["name"]}</option>')
            scope_opts.append('              <option value="bot-knowledge">Base de Regras do Bot RAG</option>')
            new_select_inner = "\n".join(scope_opts)

            admin_code = re.sub(
                r'(<select id="delegationScopeSelect"[^>]*>)([\s\S]*?)(</select>)',
                rf'\1\n{new_select_inner}\n            \3',
                admin_code
            )

            with open(ADMIN_HTML, "w", encoding="utf-8") as f:
                f.write(admin_code)
            print("  ✅ public/admin/index.html (fallback de autorização e delegação) atualizado com sucesso.")
        except Exception as e:
            print(f"  ⚠️ Erro ao atualizar admin/index.html: {e}")

    # 3. Sincronizar Cloudflare D1 (system_modules)
    if execute_d1_remote:
        print("  🌐 Sincronizando catálogo diretamente no Cloudflare D1 (pephub-db remoto)...")
        sql_stmts = []
        for m in modules:
            desc_escaped = m["description"].replace("'", "''")
            name_escaped = m["name"].replace("'", "''")
            short_escaped = m["short_name"].replace("'", "''")
            sec_escaped = m["section"].replace("'", "''")
            sql_stmts.append(
                f"INSERT INTO system_modules (id, name, short_name, section, description, route, status, sort_order) "
                f"VALUES ('{m['id']}', '{name_escaped}', '{short_escaped}', '{sec_escaped}', '{desc_escaped}', '{m['route']}', '{m['status']}', {m['sort_order']}) "
                f"ON CONFLICT(id) DO UPDATE SET "
                f"name = excluded.name, short_name = excluded.short_name, section = excluded.section, "
                f"description = excluded.description, route = excluded.route, status = excluded.status, "
                f"sort_order = excluded.sort_order;"
            )

        full_sql = " ".join(sql_stmts)
        try:
            res = subprocess.run(
                ["npx", "wrangler", "d1", "execute", "pephub-db", "--remote", "--command", full_sql],
                cwd=ROOT_DIR,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                shell=True
            )
            if res.returncode == 0:
                print("  ✅ Banco de Dados D1 atualizado: todas as ferramentas integradas em produção!")
            else:
                print(f"  ⚠️ Alerta D1: {res.stderr.strip() or res.stdout.strip()}")
        except Exception as e:
            print(f"  ⚠️ Erro ao executar comando no D1: {e}")

    print("✨ Sincronização de arcabouço concluída com sucesso!\n")

def validate_html_content(html_path):
    """Verifica se o HTML possui dados reais preenchidos em RAW_DATA."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "<html" not in content.lower():
            return False, "Arquivo não contém estrutura HTML válida."

        # Procurar const RAW_DATA ou const DATA
        idx = content.find("const RAW_DATA =")
        offset = 17
        if idx == -1:
            idx = content.find("const DATA =")
            offset = 13

        if idx != -1:
            end_idx = content.find("};", idx)
            if end_idx != -1:
                raw_json = content[idx + offset : end_idx + 1].strip()
                if raw_json.endswith(";"):
                    raw_json = raw_json[:-1].strip()
                data = json.loads(raw_json)
                # Checar se listas principais estão vazias
                for key, val in data.items():
                    if isinstance(val, list) and len(val) == 0:
                        return False, f"Campo de dados '{key}' está vazio (lista vazia []). Execute o build.py do relatório antes de publicar!"
                return True, "Dados verificados e preenchidos com integridade."

        return True, "Documento HTML válido."
    except Exception as e:
        return False, f"Falha na validação de integridade: {e}"

def publish_single(folder_name):
    rep_path = os.path.join(REPORTS_DIR, folder_name)
    if not os.path.exists(rep_path):
        print(f"❌ Erro: Relatório '{folder_name}' não encontrado em relatorios/")
        return False

    cfg_file = os.path.join(rep_path, "report_config.json")
    cfg = {}
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            print(f"⚠️ Aviso: Falha ao ler report_config.json: {e}")

    rota = cfg.get("rota_pephub", folder_name.replace("_", "-"))
    target_dir = os.path.join(PUBLIC_DIR, rota)
    os.makedirs(target_dir, exist_ok=True)

    src_html = os.path.join(rep_path, "index.html")
    if not os.path.exists(src_html):
        html_files = [f for f in os.listdir(rep_path) if f.endswith(".html")]
        if html_files:
            src_html = os.path.join(rep_path, html_files[0])
        else:
            print(f"❌ Erro: Nenhum arquivo index.html encontrado em {rep_path}")
            return False

    valid, msg = validate_html_content(src_html)
    if not valid:
        print(f"❌ Erro de Validação em {folder_name}: {msg}")
        return False
    else:
        print(f"   [Validação de Dados] {msg}")

    target_html = os.path.join(target_dir, "index.html")
    shutil.copy2(src_html, target_html)
    size_kb = os.path.getsize(target_html) / 1024

    print(f"✅ [{folder_name}] Publicado com sucesso!")
    print(f"   Origem:  relatorios/{folder_name}/{os.path.basename(src_html)}")
    print(f"   Destino: public/{rota}/index.html ({size_kb:.1f} KB)")
    print(f"   URL:     https://pephub.cloud/{rota}/")

    # Copiar assets locais caso existam
    for asset_dir in ["assets", "css", "img", "js"]:
        src_asset = os.path.join(rep_path, asset_dir)
        if os.path.exists(src_asset) and os.path.isdir(src_asset):
            dst_asset = os.path.join(target_dir, asset_dir)
            shutil.copytree(src_asset, dst_asset, dirs_exist_ok=True)
            print(f"   Assets:  {asset_dir}/ sincronizado para public/{rota}/{asset_dir}/")

    return True

def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        list_reports()
        return

    if "--list" in args:
        list_reports()
        return

    if "--sync" in args:
        sync_architecture(execute_d1_remote=True)
        return

    do_deploy = "--deploy" in args
    filtered_args = [a for a in args if not a.startswith("--")]

    if "--all" in args:
        # Sincroniza o arcabouço completo primeiro
        sync_architecture(execute_d1_remote=True)

        modules = get_all_catalog_modules()
        report_folders = [m["folder"] for m in modules if "folder" in m]
        success_count = 0
        for name in report_folders:
            if publish_single(name):
                success_count += 1
        print(f"\n🎉 Concluído: {success_count}/{len(report_folders)} relatórios publicados no Pephub.")
    elif filtered_args:
        target = filtered_args[0]
        # Sincroniza o arcabouço antes ou depois de publicar
        success = publish_single(target)
        if success:
            sync_architecture(execute_d1_remote=True)
        else:
            sys.exit(1)
    else:
        print("Especifique um relatório para publicar. Use --list para listar todos.")
        return

    if do_deploy:
        print("\n🚀 Executando deploy em produção (npx wrangler deploy)...")
        res = subprocess.run(["npx", "wrangler", "deploy"], cwd=ROOT_DIR, shell=True)
        if res.returncode == 0:
            print("🌟 Deploy em produção concluído com sucesso!")
        else:
            print("❌ Erro durante o deploy.")

if __name__ == "__main__":
    main()
