#!/usr/bin/env python3
"""
PEP HUB - Preview Local & Visual Identity Showcase Launcher
Servidor de preview local ultra-rápido, zero dependências externas.
Permite visualizar imediatamente a nova identidade visual PEP HUB PRIME
em todos os painéis, relatórios, portal e telas administrativas.
"""

import os
import sys
import json
import mimetypes
import argparse
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

MOCK_USER = {
    "authenticated": True,
    "success": True,
    "id": "admin-preview-prime",
    "login_claro": "F138138",
    "email_claro": "arthur.rezende@claro.com.br",
    "nome_completo": "Arthur Rezende (Preview Prime)",
    "area": "DIRETORIA",
    "funcao": "GERENTE REGIONAL",
    "telefone": "(91) 98111-2233",
    "foto": "",
    "status": "aprovado",
    "is_admin": True,
    "must_change_password": False,
    "modules_allowed": "all,churn,churn-bl-total,churn-bl-pme,fpd,divulgacao,tv,panorama-market-share,aprovacao-credito",
    "profile_metadata": {},
    "needs_profile_completion": False,
    "missing_profile_fields": []
}

class PepHubPreviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        try:
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {format % args}\n")
        except Exception:
            pass

    def end_headers_with_security(self, content_type="text/html; charset=utf-8", cache=True, set_cookie=True):
        self.send_header("Content-Type", content_type)
        if cache:
            self.send_header("Cache-Control", "public, max-age=0, must-revalidate")
        else:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        if set_cookie:
            self.send_header("Set-Cookie", "pephub_session=preview_prime_session; Path=/; SameSite=Lax")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers_with_security(cache=False, set_cookie=False)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Mock de Login para testes locais do formulário de autenticação
        if path == "/api/auth/login":
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False, set_cookie=True)
            response = {
                "success": True,
                "message": "Autenticado com sucesso no modo Preview!",
                "redirect": "/",
                "user": MOCK_USER
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # Mock de Heartbeat e Logout
        if path in ["/api/auth/heartbeat", "/api/auth/logout", "/api/auth/register"]:
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False, set_cookie=True)
            self.wfile.write(json.dumps({"success": True, "status": "ok"}).encode("utf-8"))
            return

        # Fallback para outros POSTs
        self.send_response(200)
        self.end_headers_with_security("application/json", cache=False, set_cookie=True)
        self.wfile.write(json.dumps({"success": True}).encode("utf-8"))

    def do_HEAD(self):
        self.handle_get_or_head(is_head=True)

    def do_GET(self):
        self.handle_get_or_head(is_head=False)

    def handle_get_or_head(self, is_head=False):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. API Mocks para evitar erros de console e redirecionamento de tela
        if path == "/api/auth/me":
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False, set_cookie=True)
            if not is_head:
                self.wfile.write(json.dumps(MOCK_USER).encode("utf-8"))
            return

        if path.startswith("/api/notifications"):
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False)
            if not is_head:
                self.wfile.write(json.dumps({"notifications": [], "unread_count": 0}).encode("utf-8"))
            return

        if path.startswith("/api/admin/users"):
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False)
            if not is_head:
                self.wfile.write(json.dumps({"users": [MOCK_USER]}).encode("utf-8"))
            return

        if path == "/health":
            self.send_response(200)
            self.end_headers_with_security("application/json", cache=False)
            if not is_head:
                self.wfile.write(json.dumps({"status": "ok", "mode": "preview-prime"}).encode("utf-8"))
            return

        # 2. Resolução de Arquivo Físico em ./public
        clean_path = path.lstrip("/")
        if clean_path == "":
            clean_path = "index.html"

        candidate_file = os.path.join(PUBLIC_DIR, clean_path.replace("/", os.sep))

        # Se for um diretório, busca index.html dentro dele
        if os.path.isdir(candidate_file):
            candidate_file = os.path.join(candidate_file, "index.html")
        elif not os.path.exists(candidate_file) and os.path.exists(candidate_file + ".html"):
            candidate_file = candidate_file + ".html"
        elif not os.path.exists(candidate_file) and os.path.exists(os.path.join(candidate_file, "index.html")):
            candidate_file = os.path.join(candidate_file, "index.html")

        if os.path.isfile(candidate_file):
            # Descobrir MIME type correto
            mime_type, _ = mimetypes.guess_type(candidate_file)
            if not mime_type:
                if candidate_file.endswith(".js"):
                    mime_type = "application/javascript"
                elif candidate_file.endswith(".css"):
                    mime_type = "text/css"
                elif candidate_file.endswith(".webmanifest"):
                    mime_type = "application/manifest+json"
                elif candidate_file.endswith(".svg"):
                    mime_type = "image/svg+xml"
                else:
                    mime_type = "application/octet-stream"

            if mime_type.startswith("text/") or mime_type in ["application/javascript", "application/json"]:
                mime_type += "; charset=utf-8"

            try:
                with open(candidate_file, "rb") as f:
                    content = f.read()

                self.send_response(200)
                self.end_headers_with_security(mime_type, cache=False)
                if not is_head:
                    self.wfile.write(content)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers_with_security("text/plain")
                if not is_head:
                    self.wfile.write(f"Erro lendo arquivo: {e}".encode("utf-8"))
                return

        # 404 Not Found
        self.send_response(404)
        self.end_headers_with_security("text/html; charset=utf-8")
        html_404 = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8">
          <title>404 - Rota Não Encontrada | PEP HUB Preview</title>
          <link rel="stylesheet" href="/css/pephub-prime.css">
          <style>
            body {{ font-family: 'Inter', -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #0b0f19; color: #f8fafc; text-align: center; }}
            .box {{ background: #111827; border: 1px solid #1f2937; padding: 40px; border-radius: 12px; max-width: 480px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #e11d48; margin-top: 0; font-size: 28px; }}
            p {{ color: #94a3b8; font-size: 14px; line-height: 1.6; }}
            a {{ display: inline-block; margin-top: 20px; background: #e11d48; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px; }}
            a:hover {{ background: #be123c; }}
          </style>
        </head>
        <body>
          <div class="box">
            <h1>404 · Rota não encontrada</h1>
            <p>A rota solicitada (<code>{path}</code>) não foi localizada no diretório de assets do PEP HUB.</p>
            <a href="/">Ir para o Portal Inicial</a>
          </div>
        </body>
        </html>
        """
        self.wfile.write(html_404.encode("utf-8"))


def run_wrangler_dev(port=8787):
    """Fallback opcional para quem deseja rodar o Worker completo no Miniflare."""
    import subprocess
    cmd = "npx wrangler dev --port " + str(port)
    print(f"Executando Wrangler: {cmd}")
    subprocess.run(cmd, shell=True)


if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="PEP HUB Preview Server")
    parser.add_argument("--port", type=int, default=8787, help="Porta local (padrao: 8787)")
    parser.add_argument("--wrangler", action="store_true", help="Rodar via Cloudflare Wrangler em vez do servidor Python nativo")
    parser.add_argument("--no-browser", action="store_true", help="Nao abrir navegador automaticamente")
    args = parser.parse_args()

    if args.wrangler:
        run_wrangler_dev(args.port)
        return

    port = args.port
    server = None
    for p in [port, 8080, 8000, 5000]:
        try:
            server = HTTPServer(("127.0.0.1", p), PepHubPreviewHandler)
            port = p
            break
        except OSError:
            continue

    if not server:
        print("[ERRO] Nao foi possivel vincular a nenhuma porta local (8787, 8080, 8000, 5000).")
        sys.exit(1)

    url = f"http://localhost:{port}"

    print("=" * 70)
    print("PEP HUB PRIME v3.0 -- SERVIDOR DE PREVIEW LOCAL ATIVO")
    print("=" * 70)
    print(f"[*] URL Principal:        {url}/")
    print(f"[*] Painel Churn Safra:   {url}/churn/")
    print(f"[*] Painel FPD:           {url}/fpd/")
    print(f"[*] Churn BL Total:       {url}/churn-bl-total/")
    print(f"[*] Churn BL PME:         {url}/churn-bl-pme/")
    print(f"[*] Painel Admin:         {url}/admin/")
    print(f"[*] Tela de Login:        {url}/login/")
    print(f"[*] Perfil Corporativo:   {url}/perfil/")
    print("=" * 70)
    print("[i] Todas as telas estao pre-autenticadas para livre avaliacao.")
    print("[i] Pressione CTRL + C para interromper o preview.")
    print("=" * 70)

    if not args.no_browser:
        def open_browser():
            time.sleep(1.2)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado.")
        server.server_close()


if __name__ == "__main__":
    main()
