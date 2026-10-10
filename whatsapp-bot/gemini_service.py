"""
Serviço de Inteligência Artificial Generativa via Google Gemini API.
Atua como camada inteligente (Fallback e Análises Ad-Hoc Avançadas) para responder
perguntas em linguagem natural que não correspondam exatamente a comandos pré-fixados,
como cruzamentos de safras, análises customizadas de parceiros ou vendedores específicos.
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
ENV_PATH_BOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
ENV_PATH_ROOT = os.path.join(ROOT_DIR, ".env")


def get_gemini_api_key() -> Optional[str]:
    """Obtém a chave da API do Gemini a partir do config.json, .env ou variável de ambiente."""
    # 1. Variável de ambiente do sistema
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. whatsapp-bot/config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                key = cfg.get("gemini_api_key")
                if key and key.strip() and not key.startswith("COLOQUE_"):
                    return key.strip()
        except Exception:
            pass

    # 3. Arquivo .env local ou raiz
    for p in [ENV_PATH_BOT, ENV_PATH_ROOT]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    return None


def get_gemini_model_name() -> str:
    """Retorna o modelo configurado (padrão flash-lite)."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                m = cfg.get("gemini_model")
                if m and m.strip():
                    return m.strip()
        except Exception:
            pass
    return "gemini-2.5-flash-lite"


class GeminiService:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        self.model = get_gemini_model_name()

    def is_available(self) -> bool:
        """Verifica se há chave configurada."""
        self.api_key = get_gemini_api_key()
        return bool(self.api_key)

    def generate_response(self, user_query: str, context_text: str = "") -> Optional[str]:
        """Envia o prompt com contexto ao modelo Gemini e retorna a resposta formatada para WhatsApp."""
        api_key = get_gemini_api_key()
        if not api_key:
            return None

        # Lista de modelos para fallback caso o nome específico não exista na API
        candidate_models = [self.model]
        for fallback in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        system_instruction = (
            "Você é o Assistente Especialista de Inteligência de Dados de Churn e Operação Comercial da Claro / Pephub (Regional Norte: AM, PA, MA, AP, RR).\n"
            "DIRETRIZES DE GESTÃO E SEGURANÇA MÁXIMA:\n"
            "1. REGRA ABSOLUTA ANTI-ALUCINAÇÃO: Você NUNCA deve inventar, deduzir ou alterar qualquer número, quantitativo ou percentual. Use RIGOROSAMENTE e EXCLUSIVAMENTE os valores oficiais fornecidos no 'Contexto de Dados Disponíveis'. Se uma informação não estiver presente no contexto, declare expressamente: 'Não possuo esse dado na base oficial'.\n"
            "2. ANÁLISE QUALITATIVA vs QUANTITATIVA: Se o usuário perguntar sobre impactos de fatores de mercado (como inflação, concorrência, reajustes ou crise), faça a análise econômica qualitativa conectando-a DIRETAMENTE com as métricas do contexto (ex: perdas voluntárias, inadimplência e motivos do Speech Analytics de reclamação de preço/concorrência), sem criar números externos fictícios.\n"
            "3. Indicador Oficial de Safra é 'Churn Safra D120' (janela de 120 dias de observação sob responsabilidade do parceiro de venda). Nunca use 'taxa de churn' para safras; use sempre 'Churn Safra D120 (%)'. Sempre use '/' para divisão, nunca a palavra 'sobre'.\n"
            "4. TAMANHO E OBJETIVIDADE: Seja EXTREMAMENTE conciso, executivo e direto. Limite sua resposta a NO MÁXIMO 3 a 5 parágrafos ou bullets curtos (máximo de 180 a 220 palavras). NUNCA gere textos excessivamente longos. SEMPRE conclua a resposta com um fechamento claro, garantindo que nenhuma frase fique incompleta ou cortada.\n"
            "5. Otimize para o WhatsApp usando negrito com asteriscos (*texto*), itálico (_texto_) e listas com marcadores (•)."
        )

        prompt_body = f"Contexto de Dados Disponíveis:\n{context_text}\n\nPergunta do Usuário:\n{user_query}"

        for m_name in candidate_models:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_instruction}\n\n{prompt_body}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2048,
                }
            }

            try:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    endpoint,
                    data=data_bytes,
                    headers={"Content-Type": "application/json"}
                )
                # Tentativa com SSL padrão do SO e fallback para ambientes com proxy corporativo / inspeção TLS
                try:
                    ctx = ssl.create_default_context()
                    resp_handle = urllib.request.urlopen(req, timeout=15, context=ctx)
                except (ssl.SSLError, urllib.error.URLError) as ssl_err:
                    ctx = ssl._create_unverified_context()
                    resp_handle = urllib.request.urlopen(req, timeout=15, context=ctx)

                with resp_handle as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except urllib.error.HTTPError as e:
                # Se for 404 (modelo não encontrado), tenta o próximo modelo da lista candidata
                if e.code == 404:
                    continue
                print(f"[Gemini API Error] HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")
                return None
            except Exception as e:
                print(f"[Gemini API Exception] {e}")
                return None

        return None
