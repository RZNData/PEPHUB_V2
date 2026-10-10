#!/usr/bin/env python3
"""
PEP HUB - Preview Local & Staging Launcher
Permite iniciar o servidor de preview local instantâneo ou visualizar o ambiente secundário.
"""

import sys
import subprocess
import webbrowser
import time

def run_local_preview():
    print("=" * 65)
    print("🚀 INICIANDO SERVIDOR DE PREVIEW LOCAL PEP HUB (Wrangler Dev)")
    print("=" * 65)
    print("📍 URL Local: http://localhost:8787")
    print("🌐 Ambiente Cloud Staging: https://pephub-regional-staging.hurn--afra.workers.dev")
    print("💡 Pressione CTRL + C para encerrar o preview quando terminar.")
    print("=" * 65)
    
    # Abrir navegador após 2 segundos
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8787")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Executar wrangler dev na porta 8787
    cmd = ["npx", "wrangler", "dev", "--port", "8787"]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor de preview encerrado com sucesso.")

if __name__ == "__main__":
    run_local_preview()
