"""
Serviço de Disparo de E-mails via Resend API para Notificação de Erros e Inconsistências de Dados.
Envia automaticamente um relatório com o contexto da consulta, pergunta do usuário e divergência reportada.
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH_BOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
ENV_PATH_ROOT = os.path.join(ROOT_DIR, ".env")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_reports.log")


def get_resend_api_key() -> Optional[str]:
    """Obtém a chave da API Resend do .env, config.json ou variável de ambiente."""
    env_key = os.environ.get("RESEND_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    for p in [ENV_PATH_BOT, ENV_PATH_ROOT]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("RESEND_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                val = cfg.get("resend_api_key")
                if val and val.strip():
                    return val.strip()
        except Exception:
            pass

    return None


def get_target_email() -> str:
    """Retorna o e-mail de destino configurado."""
    env_target = os.environ.get("RESEND_TARGET_EMAIL")
    if env_target and env_target.strip():
        return env_target.strip()

    for p in [ENV_PATH_BOT, ENV_PATH_ROOT]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("RESEND_TARGET_EMAIL="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    return "arthur.rezende.analista@gmail.com"


class ResendService:
    def __init__(self):
        self.api_key = get_resend_api_key()
        self.target_email = get_target_email()

    def send_error_report(
        self,
        user_message: str,
        bot_response: str,
        context: Dict[str, Any],
        error_details: str = "Inconsistência ou divergência apontada pelo usuário"
    ) -> Dict[str, Any]:
        """Dispara e-mail via Resend API relatando o erro com detalhes da auditoria."""
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        target_city = context.get("city_name") or context.get("city_id", "Regional Norte")
        target_month = context.get("month_label", "Set/26")
        target_seg = context.get("segment", "Banda Larga")

        # Registro em log local de auditoria sempre
        log_entry = (
            f"[{now_str}] COMUNICADO DE ERRO\n"
            f"Cidade/Contexto: {target_city} | Mês: {target_month} | Segmento: {target_seg}\n"
            f"Pergunta: {user_message}\n"
            f"Detalhe do Erro: {error_details}\n"
            f"Resposta do Bot:\n{bot_response}\n"
            f"{'='*60}\n"
        )
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

        api_key = get_resend_api_key()
        if not api_key:
            # Se não houver chave cadastrada no Resend, grava log e retorna simulação com sucesso
            return {
                "success": True,
                "simulated": True,
                "recipient": self.target_email,
                "message": (
                    f"⚠️ *COMUNICADO DE ERRO REGISTRADO!*\n\n"
                    f"O erro foi gravado no log de auditoria do sistema para a gestão.\n"
                    f"📧 *Destinatário Cadastrado:* `{self.target_email}`\n"
                    f"📌 *Cidade / Mês:* {target_city} ({target_month})\n"
                    f"📝 *Detalhe:* {error_details}\n\n"
                    f"💡 _Para disparo direto via SMTP/API do Resend em tempo real, adicione a `RESEND_API_KEY` no arquivo `.env`._"
                )
            }

        # Template HTML corporativo
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="background-color: #d9534f; color: white; padding: 15px; border-radius: 6px 6px 0 0; text-align: center;">
                <h2 style="margin: 0;">⚠️ Alerta de Inconsistência / Erro Reportado</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Pephub WhatsApp Data Bot — Regional Norte</p>
            </div>
            <div style="padding: 20px; background-color: #fdfdfd;">
                <p><strong>Data/Hora do Registro:</strong> {now_str}</p>
                <p><strong>Praça / Contexto:</strong> {target_city} ({target_month}) — Segmento: {target_seg}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">
                
                <h4 style="color: #333; margin-bottom: 5px;">Pergunta Realizada pelo Usuário:</h4>
                <div style="background-color: #f5f5f5; padding: 10px; border-left: 4px solid #337ab7; border-radius: 4px; font-family: monospace;">
                    {user_message}
                </div>

                <h4 style="color: #333; margin-top: 15px; margin-bottom: 5px;">Detalhes do Problema / Divergência Apontada:</h4>
                <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-left: 4px solid #ffeeba; border-radius: 4px;">
                    {error_details}
                </div>

                <h4 style="color: #333; margin-top: 15px; margin-bottom: 5px;">Resposta Gerada pelo Bot:</h4>
                <div style="background-color: #f9f9f9; padding: 10px; border: 1px solid #eee; border-radius: 4px; white-space: pre-wrap; font-size: 13px;">
                    {bot_response}
                </div>
            </div>
            <div style="background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 6px 6px;">
                E-mail automático gerado pelo sistema Pephub Churn Intelligence Bot.
            </div>
        </div>
        """

        text_content = (
            f"ALERTA DE INCONSISTÊNCIA / ERRO REPORTADO\n"
            f"Data: {now_str}\n"
            f"Praça/Mês: {target_city} ({target_month})\n"
            f"Pergunta: {user_message}\n"
            f"Detalhe: {error_details}\n\n"
            f"Resposta do Bot:\n{bot_response}\n"
        )

        payload = {
            "from": "Pephub Churn Bot <onboarding@resend.dev>",
            "to": [self.target_email],
            "subject": f"⚠️ [Pephub Bot] Divergência Reportada: {target_city} ({target_month})",
            "html": html_content,
            "text": text_content,
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=data_bytes,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            try:
                ctx = ssl.create_default_context()
                resp_handle = urllib.request.urlopen(req, timeout=15, context=ctx)
            except (ssl.SSLError, urllib.error.URLError):
                ctx = ssl._create_unverified_context()
                resp_handle = urllib.request.urlopen(req, timeout=15, context=ctx)

            with resp_handle as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                email_id = res_body.get("id", "OK")
                return {
                    "success": True,
                    "simulated": False,
                    "recipient": self.target_email,
                    "id": email_id,
                    "message": (
                        f"✅ *COMUNICADO DE ERRO ENVIADO COM SUCESSO!*\n\n"
                        f"Um relatório técnico detalhado com o contexto da consulta foi enviado via Resend para:\n"
                        f"📧 *{self.target_email}*\n\n"
                        f"📌 *Identificador do Envio:* `{email_id}`\n"
                        f"A equipe de engenharia e gestão de dados foi notificada para averiguação imediata."
                    )
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            return {
                "success": False,
                "error": f"HTTP {e.code}: {err_msg}",
                "message": (
                    f"⚠️ *REGISTRADO LOCALMENTE!*\n"
                    f"O erro foi arquivado no log de auditoria do sistema, mas a API do Resend retornou HTTP {e.code}.\n"
                    f"📧 E-mail cadastrado: *{self.target_email}*"
                )
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": (
                    f"⚠️ *REGISTRADO NO LOG DO BOT!*\n"
                    f"O erro foi arquivado com sucesso no histórico da praça para análise da gestão."
                )
            }
