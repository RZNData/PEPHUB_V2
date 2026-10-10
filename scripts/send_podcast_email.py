#!/usr/bin/env python3
"""
Disparo de E-mail Corporativo com o Podcast PEP HUB Deep Dive v2.0 em Anexo.
Utiliza a Resend API para enviar o arquivo MP3 e as notas do episódio
para o endereço configurado do administrador.
"""

import os
import sys
import ssl
import json
import base64
import urllib.request
import urllib.error

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_PATH = os.path.join(ROOT_DIR, "public", "podcast", "pephub_deepdive_podcast.mp3")
ENV_PATH = os.path.join(ROOT_DIR, "whatsapp-bot", ".env")

def get_config():
    api_key = None
    target_email = "arthur.rezende.analista@gmail.com"
    
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("RESEND_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("RESEND_TARGET_EMAIL="):
                    target_email = line.split("=", 1)[1].strip().strip('"').strip("'")
                    
    return api_key, target_email

def main():
    print("=" * 60)
    print("📧 PREPARANDO ENVIO DO PODCAST VIA RESEND API")
    print("=" * 60)
    
    api_key, target_email = get_config()
    if not api_key:
        print("❌ Erro: RESEND_API_KEY não localizada em whatsapp-bot/.env")
        sys.exit(1)
        
    if not os.path.exists(AUDIO_PATH):
        print(f"❌ Erro: Arquivo de áudio não encontrado em {AUDIO_PATH}")
        sys.exit(1)
        
    audio_size_bytes = os.path.getsize(AUDIO_PATH)
    audio_size_mb = audio_size_bytes / (1024 * 1024)
    print(f"📁 Arquivo de áudio: {AUDIO_PATH}")
    print(f"⚖️ Tamanho: {audio_size_mb:.2f} MB")
    print(f"📬 Destinatário: {target_email}")
    
    print("⏳ Codificando áudio em Base64 para anexo corporativo...")
    with open(AUDIO_PATH, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("ascii")
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; color: #1c2430; margin: 0; padding: 24px; }}
        .card {{ background: #ffffff; border-radius: 8px; border: 1px solid #dfe3e8; max-width: 640px; margin: 0 auto; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
        .header {{ background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%); padding: 24px 28px; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }}
        .header p {{ margin: 6px 0 0; font-size: 13px; color: rgba(255,255,255,0.92); }}
        .body {{ padding: 24px 28px; line-height: 1.55; font-size: 13.5px; }}
        .badge {{ display: inline-block; background: #eaf2ec; color: #235c44; border: 1px solid #c9dfd2; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 3px; text-transform: uppercase; margin-bottom: 14px; }}
        .topic-box {{ background: #f8fafc; border-left: 4px solid #da291c; border-radius: 0 4px 4px 0; padding: 12px 16px; margin: 16px 0; font-size: 13px; }}
        .topic-box strong {{ color: #1c2430; display: block; margin-bottom: 4px; }}
        .btn {{ display: inline-block; background: #1b2430; color: #ffffff !important; text-decoration: none; padding: 10px 20px; border-radius: 4px; font-weight: 700; font-size: 13px; margin: 18px 0 10px; }}
        .footer {{ background: #fafbfc; border-top: 1px solid #eceef1; padding: 16px 28px; font-size: 11px; color: #8b95a3; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>🎙️ PEP HUB Deep Dive — Episódio Definitivo da Plataforma</h1>
          <p>Áudio Overview Oficial da Arquitetura, Engenharia & Painéis da Regional Norte</p>
        </div>
        <div class="body">
          <span class="badge">Deploy em Produção Homologado · Grau A+</span>
          <p>Olá, Arthur!</p>
          <p>Conforme solicitado, geramos o <strong>Podcast Oficial Completo do Manual do PEP HUB</strong> no consagrado formato <em>Google NotebookLM Audio Overview</em>, apresentado pelos hosts neurais <strong>Carol e Lucas</strong>.</p>
          
          <div class="topic-box">
            <strong>📋 Destaques do Episódio:</strong>
            <ul style="margin:6px 0;padding-left:20px">
              <li><strong>A Gênese do PEP HUB:</strong> Por que soluções de mercado como PowerBI e Tableau falham em campo (lentidão de 30s, travamentos no 4G e custos de licença) e como o PEP HUB entrega carregamento em menos de 300ms com funcionamento 100% offline.</li>
              <li><strong>Engenharia de Alto Desempenho:</strong> Zero dependências externas (sem React/Tailwind/Chart.js), gráficos em SVG nativo, mapas em Canvas 2D Web Mercator e economia de 80% de RAM via Typed Arrays e compressão Deflate.</li>
              <li><strong>Tour pelos 6 Painéis Analíticos:</strong> Regras do Churn Safra D120, a segregação estrita do FPD (FPD 30 vs FPD 60 sem mistura de colunas), a janela crítica de carência no mês 11 da Banda Larga PME (78,2% das desconexões), o Panorama Market Share e a Taxa de Aprovação de Crédito sem capa decorativa e com ordenação nativa por volume de PDV.</li>
              <li><strong>PeP Tools de Produtividade:</strong> O novo Auxiliar de PPT (exportação direta de infográficos em SVG/PNG para slides) e o Gerador de Cards 16:9 sem cortes para as TVs dos prédios da Claro.</li>
              <li><strong>O Cérebro do Bot WhatsApp:</strong> A rodovia de duas vias com Safe SQL determinístico no Cloudflare D1 (precisão matemática de 100% contra alucinações de LLM) e RAG semântico para regras de negócio, com carteirização por telefone.</li>
              <li><strong>Central de Cargas & Segurança Bancária:</strong> Uploads fatiados em 500 KB no D1 (custo zero de S3/R2), delegação granular RBAC e nota A+ em todos os pilares do Release Gate.</li>
            </ul>
          </div>

          <p>O arquivo de áudio está anexado diretamente a esta mensagem (<strong>pephub_deepdive_podcast.mp3</strong> - {audio_size_mb:.2f} MB) e também pode ser escutado com transcrição interativa através do portal oficial:</p>

          <p style="text-align:center">
            <a href="https://pephub.cloud/podcast/" class="btn">▶️ Ouvir no Player Web Interativo</a>
          </p>
          
          <p style="font-size:12px;color:#5b6675">Link direto do arquivo MP3: <br><a href="https://pephub.cloud/podcast/pephub_deepdive_podcast.mp3" style="color:#2a5d8f">https://pephub.cloud/podcast/pephub_deepdive_podcast.mp3</a></p>
        </div>
        <div class="footer">
          Claro Brasil — Regional Norte · Diretoria & Operações · pephub.cloud
        </div>
      </div>
    </body>
    </html>
    """

    payload = {
        "from": "Pephub Deep Dive <onboarding@resend.dev>",
        "to": [target_email],
        "subject": "🎙️ Episódio Completo: Podcast Oficial do Sistema PEP HUB (Áudio Anexo)",
        "html": html_content,
        "attachments": [
            {
                "filename": "pephub_deepdive_podcast_completo.mp3",
                "content": audio_b64
            }
        ]
    }

    print("🚀 Enviando e-mail via Resend API...")
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data_bytes,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PephubEmailer/1.0"
        }
    )

    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            resp_body = resp.read().decode("utf-8")
            print("✅ E-mail enviado com sucesso!")
            print(f"Status HTTP: {resp.status}")
            print(f"Resposta Resend: {resp_body}")
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP ao enviar e-mail: {e.code} - {e.reason}")
        print(f"Detalhes: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
