"""
Cliente Python para interação com a Evolution API v2.
Permite criar instâncias, gerar QR Codes, configurar webhooks e enviar mensagens.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_EVOLUTION_URL = "http://localhost:8080"
DEFAULT_API_KEY = "pephub_secret_token_2026"


class EvolutionClient:
    def __init__(self, base_url: str = DEFAULT_EVOLUTION_URL, api_key: str = DEFAULT_API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key,
        }

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode("utf-8")
                return json.loads(res_body) if res_body else {"status": "ok"}
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            try:
                return json.loads(err_content)
            except Exception:
                return {"error": f"HTTP {e.code}: {e.reason}", "details": err_content}
        except Exception as e:
            return {"error": str(e)}

    def is_online(self) -> bool:
        """Verifica se o servidor da Evolution API está acessível."""
        res = self._request("GET", "/")
        return "status" in res or "version" in res or "name" in res or "error" not in res

    def create_instance(self, instance_name: str = "pephub-bot") -> Dict[str, Any]:
        """Cria uma nova instância do WhatsApp se ainda não existir."""
        payload = {
            "instanceName": instance_name,
            "token": "",
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
        }
        return self._request("POST", "/instance/create", payload)

    def get_connection_status(self, instance_name: str = "pephub-bot") -> Dict[str, Any]:
        """Obtém o estado atual da conexão (open, close, connecting)."""
        return self._request("GET", f"/instance/connectionState/{instance_name}")

    def connect(self, instance_name: str = "pephub-bot") -> Dict[str, Any]:
        """Inicia a conexão e obtém o QR Code em base64 / texto."""
        return self._request("GET", f"/instance/connect/{instance_name}")

    def set_webhook(
        self,
        instance_name: str = "pephub-bot",
        webhook_url: str = "http://host.docker.internal:8085/webhook",
    ) -> Dict[str, Any]:
        """Configura a URL de webhook para onde as mensagens recebidas devem ser enviadas."""
        payload = {
            "enabled": True,
            "url": webhook_url,
            "webhookByEvents": False,
            "events": [
                "MESSAGES_UPSERT"
            ],
        }
        return self._request("POST", f"/webhook/set/{instance_name}", payload)

    def send_message(self, instance_name: str, remote_jid: str, text: str) -> Dict[str, Any]:
        """Envia uma mensagem de texto (para número individual ou grupo @g.us)."""
        payload = {
            "number": remote_jid,
            "text": text,
        }
        return self._request("POST", f"/message/sendText/{instance_name}", payload)
