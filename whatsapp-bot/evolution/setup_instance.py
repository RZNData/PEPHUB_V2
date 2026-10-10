"""
Script de Inicialização e Configuração da Instância do Pephub na Evolution API.
Executa o fluxo completo:
1. Verifica se a Evolution API está online (localhost:8080).
2. Cria ou recupera a instância 'pephub-bot'.
3. Registra o Webhook apontando para http://host.docker.internal:8085/webhook.
4. Gera o QR Code em página HTML para escanear pelo celular.
"""

import os
import sys
import webbrowser
from evolution_client import EvolutionClient

QR_HTML_PATH = os.path.join(os.path.dirname(__file__), "qr_evolution.html")


def save_qr_html(base64_img: str):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Conectar WhatsApp — Evolution API</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0c1317; color: #e9edef; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
    .card {{ background: #111b21; padding: 36px; border-radius: 12px; text-align: center; box-shadow: 0 8px 30px rgba(0,0,0,0.5); max-width: 420px; }}
    h2 {{ color: #00a884; margin-top: 0; }}
    p {{ color: #8696a0; font-size: 14px; line-height: 1.5; }}
    .qr-box {{ background: #fff; padding: 16px; border-radius: 8px; display: inline-block; margin: 18px 0; }}
    .qr-box img {{ display: block; width: 260px; height: 260px; }}
    .badge {{ background: #1f2c34; color: #ffd279; padding: 6px 12px; border-radius: 16px; font-size: 12px; display: inline-block; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>Conectar Bot ao WhatsApp</h2>
    <p>1. Abra o WhatsApp no seu celular<br>2. Toque em <b>Aparelhos Conectados</b> &gt; <b>Conectar um Aparelho</b><br>3. Aponte a câmera para o código abaixo:</p>
    <div class="qr-box">
      <img src="{base64_img}" alt="QR Code WhatsApp" />
    </div>
    <div class="badge">Instância: pephub-bot</div>
  </div>
</body>
</html>"""
    with open(QR_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n📱 QR Code salvo em: {QR_HTML_PATH}")


def main():
    client = EvolutionClient()
    instance_name = "pephub-bot"

    print("\n" + "=" * 65)
    print("🤖 CONFIGURAÇÃO DA EVOLUTION API — PEPHUB CHURN BOT")
    print("=" * 65)

    print("\n1. Verificando status da Evolution API em http://localhost:8080...")
    if not client.is_online():
        print("❌ A Evolution API não está respondendo em http://localhost:8080.")
        print("💡 Para iniciar o container:")
        print("   cd whatsapp-bot/evolution")
        print("   docker compose up -d\n")
        sys.exit(1)

    print("✅ Evolution API está online e pronta!")

    print(f"\n2. Verificando / Criando instância '{instance_name}'...")
    res_create = client.create_instance(instance_name)
    if "error" in res_create and "already in use" not in str(res_create):
        print(f"⚠️ Nota: {res_create.get('error', res_create)}")
    else:
        print(f"✅ Instância '{instance_name}' configurada com sucesso!")

    print("\n3. Configurando Webhook para o Cloudflare Worker do Pephub...")
    default_webhook = os.environ.get("WORKER_WEBHOOK_URL", "https://pephub.cloud/api/bot/webhook/evolution")
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else default_webhook
    res_webhook = client.set_webhook(instance_name, webhook_url)
    print(f"✅ Webhook apontado para: {webhook_url}")

    print("\n4. Verificando estado da conexão do WhatsApp...")
    res_status = client.get_connection_status(instance_name)
    state = res_status.get("instance", {}).get("state") or res_status.get("state")

    if state == "open":
        print("🎉 [WHATSAPP JÁ CONECTADO!] A instância já está autenticada e pronta para responder no grupo!")
    else:
        print("⏳ Obtendo QR Code para autenticação...")
        res_connect = client.connect(instance_name)
        base64_qr = res_connect.get("base64") or res_connect.get("qrcode", {}).get("base64")
        if base64_qr:
            save_qr_html(base64_qr)
            try:
                webbrowser.open(f"file://{os.path.abspath(QR_HTML_PATH)}")
            except Exception:
                pass
            print("👉 Abra o arquivo 'qr_evolution.html' no navegador e escaneie com seu WhatsApp!")
        else:
            print("⚠️ QR Code não retornado imediatamente. Resposta da API:", res_connect)

    print("\n" + "=" * 65)
    print("✅ Ambiente Evolution API pronto!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
