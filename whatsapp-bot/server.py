"""
Servidor HTTP / Webhook para o Bot de WhatsApp Pephub.
Permite integração direta com:
- Evolution API (Webhook de mensagens recebidas)
- Z-API (Webhook de mensagens recebidas)
- Testes via navegador ou cURL: GET /query?q=como+esta+manaus
"""

import json
import os
import sys
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Garantir UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent import ChurnAgent

agent = ChurnAgent()

# Cache de números autorizados via banco de usuários da Pephub
AUTHORIZED_CACHE = {"timestamp": 0, "phones": set()}

def is_phone_authorized(phone: str, backend_url: str = None) -> bool:
    if not phone:
        return True  # Consultas locais ou sem telefone (ex: simulator) são permitidas
    
    clean_p = "".join(filter(str.isdigit, phone))
    if not clean_p:
        return True

    now = time.time()
    backend = backend_url or os.environ.get("PEPHUB_API_URL", "http://localhost:8787")
    
    # Atualiza lista de autorizados a cada 60 segundos
    if now - AUTHORIZED_CACHE["timestamp"] > 60:
        try:
            req = urllib.request.Request(f"{backend}/api/auth/authorized-phones", headers={"User-Agent": "PephubBot/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                phones = set()
                for item in data.get("phones", []):
                    num = "".join(filter(str.isdigit, item.get("telefone", "")))
                    if num:
                        phones.add(num)
                        if num.startswith("55"):
                            phones.add(num[2:])
                AUTHORIZED_CACHE["phones"] = phones
                AUTHORIZED_CACHE["timestamp"] = now
        except Exception as e:
            sys.stderr.write(f"[Auth] Não foi possível consultar API de telefones ({e}). Mantendo cache.\n")
    
    allowed = AUTHORIZED_CACHE["phones"]
    if not allowed:
        # Se não há números retornados ou API offline na primeira execução, mantém permissivo com aviso
        return True

    return clean_p in allowed or (clean_p.startswith("55") and clean_p[2:] in allowed)


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        response_body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ["/", "/index.html", "/simulator"]:
            sim_path = os.path.join(os.path.dirname(__file__), "simulator.html")
            if os.path.exists(sim_path):
                with open(sim_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        if parsed.path == "/query":
            params = parse_qs(parsed.query)
            q = params.get("q", [""])[0]
            if not q:
                return self._send_json(400, {"error": "Parâmetro 'q' ausente."})
            answer = agent.process_message(q)
            return self._send_json(200, {"query": q, "response": answer})

        if parsed.path == "/health":
            return self._send_json(200, {"status": "ok", "service": "Pephub WhatsApp Bot"})

        self._send_json(404, {"error": "Rota não encontrada. Use /query?q=... ou /health"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            payload = json.loads(body) if body else {}
        except Exception:
            return self._send_json(400, {"error": "Payload JSON inválido."})

        # Extração de texto para diferentes gateways (Evolution API / Z-API)
        text = ""
        remote_jid = ""
        from_me = False
        instance_name = payload.get("instance", "pephub-bot")

        # 1. Formato Evolution API
        if "data" in payload and isinstance(payload["data"], dict):
            key = payload["data"].get("key", {})
            remote_jid = key.get("remoteJid", "")
            from_me = key.get("fromMe", False)
            msg = payload["data"].get("message", {})
            text = (
                msg.get("conversation")
                or msg.get("extendedTextMessage", {}).get("text")
                or ""
            )
        # 2. Formato Z-API
        elif "text" in payload and isinstance(payload["text"], dict):
            text = payload["text"].get("message", "")
            remote_jid = payload.get("phone", "")
        # 3. Formato direto simples { "text": "como esta manaus?" }
        elif "text" in payload:
            text = str(payload.get("text", ""))

        triggers = ["#?", "#dados", "!dados", "!churn", "!pep", "/dados", "/churn", "@bot"]
        matched_trigger = None
        lower_text = (text or "").lower()
        for trig in triggers:
            if lower_text.startswith(trig):
                matched_trigger = trig
                break

        is_group = remote_jid.endswith("@g.us")
        should_respond = False
        clean_query = text

        if from_me:
            # Mensagem enviada pelo próprio usuário (ex: teste no chat consigo mesmo no WhatsApp)
            if matched_trigger and matched_trigger != "@bot":
                should_respond = True
                clean_query = text[len(matched_trigger):].strip()
            else:
                return self._send_json(200, {"status": "ignored", "reason": "Mensagem própria sem prefixo de comando"})
        elif is_group:
            # Mensagens de grupo
            if matched_trigger and matched_trigger != "@bot":
                should_respond = True
                clean_query = text[len(matched_trigger):].strip()
            elif "@bot" in lower_text:
                should_respond = True
                clean_query = text.replace("@bot", "").strip()
        else:
            # Mensagens privadas 1:1 de terceiros:
            # Exige prefixo rígido (#? ou #dados) para NUNCA interferir nas conversas pessoais/profissionais normais
            if matched_trigger and matched_trigger != "@bot":
                should_respond = True
                clean_query = text[len(matched_trigger):].strip()

        if not should_respond:
            return self._send_json(200, {"status": "ignored", "reason": "Sem gatilho (#? ou #dados)"})

        if not clean_query:
            clean_query = "ajuda"

        # Extrair telefone do remetente
        sender_target = remote_jid
        if is_group and "data" in payload and isinstance(payload["data"], dict):
            part = payload["data"].get("key", {}).get("participant", "")
            if part:
                sender_target = part
        
        sender_phone = "".join(filter(str.isdigit, sender_target.split("@")[0])) if sender_target else ""

        # Verificação de Autorização Corporativa
        if sender_phone and not from_me and not is_phone_authorized(sender_phone):
            sys.stderr.write(f"[Auth] Bloqueio: Número não autorizado tentou consulta: {sender_phone}\n")
            unauth_msg = (
                "🔒 *Acesso Corporativo Pephub — Regional Norte*\n\n"
                f"Olá! O número *+{sender_phone}* não está cadastrado ou aprovado para consultas de inteligência no WhatsApp.\n\n"
                "👉 *Como solicitar liberação:*\n"
                "1. Acesse o portal institucional em: https://pephub.com.br/register/\n"
                "2. Realize a solicitação de cadastro informando este mesmo número no campo *Telefone / WhatsApp Corporativo*.\n"
                "3. Assim que o gestor aprovar seu acesso, este número será liberado automaticamente.\n\n"
                "_Plataforma de Inteligência Regional Norte — Claro Brasil_"
            )
            if remote_jid:
                try:
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "evolution"))
                    from evolution_client import EvolutionClient
                    evo = EvolutionClient()
                    evo.send_message(instance_name, remote_jid, unauth_msg)
                except Exception as e:
                    sys.stderr.write(f"[Server] Erro ao enviar aviso de bloqueio via Evolution: {e}\n")
            return self._send_json(403, {"status": "unauthorized", "phone": sender_phone})

        answer = agent.process_message(clean_query)

        # Se a mensagem veio do WhatsApp via Evolution API, envia de volta ao chat/grupo
        if remote_jid:
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), "evolution"))
                from evolution_client import EvolutionClient
                evo = EvolutionClient()
                evo.send_message(instance_name, remote_jid, answer)
                sys.stderr.write(f"[Server] Resposta enviada ao WhatsApp: {remote_jid}\n")
            except Exception as e:
                sys.stderr.write(f"[Server] Erro ao enviar resposta via Evolution: {e}\n")

        return self._send_json(200, {"response": answer, "sent_to": remote_jid})

    def log_message(self, format, *args):
        # Log limpo no terminal
        sys.stderr.write(f"[Server] {self.address_string()} - {args[0]} {args[1]}\n")


def run_server(port: int = 8085):
    server = HTTPServer(("0.0.0.0", port), WhatsAppWebhookHandler)
    print(f"\n🚀 Servidor de Webhook ativo em: http://localhost:{port}")
    print(f"👉 Teste no navegador: http://localhost:{port}/query?q=como+esta+manaus")
    print(f"👉 Endpoint para Evolution API / Z-API: http://localhost:{port}/webhook\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor finalizado.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    run_server(port)
