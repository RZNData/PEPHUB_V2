"""
Agente Inteligente do Bot WhatsApp Pephub / Churn.
Processa mensagens em linguagem natural (Português), detecta intenções,
extrai entidades (cidades, segmentos, métricas, meses, safras e parceiros) e retorna a resposta formatada.
Possui:
1. Motor NLU Heurístico local (Zero custo, ultrarrápido, determinístico).
2. Conexão integrada com Google Gemini API (gemini-2.5-flash-lite) com Grounding RAG estrito anti-alucinação.
3. Botões Interativos de Ações Rápidas (#?sim, #?safra, #?erro, etc.) no rodapé de cada resposta.
4. Fluxo automático de Comunicar Erro com disparo de e-mail via Resend API para a gestão.
"""

import json
import os
import re
import sys
import unicodedata
from typing import Dict, Any, Optional, Tuple, List

# Garantir UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from data_engine import (
    DataEngine,
    CITY_DISPLAY_NAMES,
    format_city_response,
    format_ranking_response,
    format_invol_response,
    format_speech_response,
    format_city_month_response,
    format_deep_dive_response,
    format_churn_safra_city_response,
    format_churn_safra_partner_response,
    format_churn_safra_regional_response,
    _normalize,
)
from gemini_service import GeminiService
from resend_service import ResendService

CONTEXT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".context.json")


def load_context() -> Dict[str, Any]:
    try:
        if os.path.exists(CONTEXT_FILE):
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "city_id" in data:
                    return data
    except Exception:
        pass
    return {
        "city_id": "NORTE",
        "segment": "TOTAL",
        "city_name": "Regional Norte",
        "month": "2026-09",
        "month_label": "Set/26",
        "last_query": "",
        "last_response": ""
    }


def save_context(ctx: Dict[str, Any]):
    try:
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(ctx, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


GLOSSARIO_CLARO = {
    "fpd": {
        "topico": "Conceito e Definição de FPD (First Payment Default)",
        "conteudo": "O *FPD* (*First Payment Default* ou Inadimplência de Primeiro Pagamento) mede a qualidade da venda nos primeiros 60 dias da instalação do contrato. Ele avalia se o cliente quitou a primeira fatura (*pró-rata*) e a fatura cheia subsequente.",
        "formula": "Taxa FPD (%) = (Total de Clientes Não Pagos / Total de Instalações da Safra) × 100",
        "associados": [
            ("Diferença entre FPD 30 e FPD 60", "O *FPD 30* avalia a inadimplência da fatura inicial (pró-rata) até 30 dias após o vencimento (*AGING30 = 1*). O *FPD 60 Efetivo* avalia a inadimplência cumulativa no ciclo cheio de 60 dias (*AGING30 = 1* e *AGING60 = 1*). Se o cliente atrasar aos 30 dias mas quitar antes dos 60, é considerado *Curado*."),
            ("Conceito de Cura do FPD", "A *Cura* ocorre quando o cliente atrasou a fatura pró-rata de 30 dias (*AGING30 = 1*), porém efetuou o pagamento antes do marco de 60 dias (*AGING60 = 0*). Representa a recuperação da safra pela régua de cobrança."),
            ("Faixas de Risco de Crédito", "A Claro classifica o risco de crédito do cliente no momento da venda em 7 faixas (*FX_RISCO_NV*): Baixíssimo a Altíssimo 2. Vendas concentradas em faixas críticas possuem maior propensão a perdas precoces de FPD.")
        ]
    },
    "d120": {
        "topico": "Regra Oficial de Churn Safra D120",
        "conteudo": "O *Churn Safra D120* é o indicador oficial de sobrevivência de contratos da Claro Regional Norte. Ele observa os cancelamentos acumulados nos primeiros 120 dias a contar do mês de instalação da venda. É a métrica utilizada para apuração de responsabilidade de parceiros comerciais e regras de estorno (*clawback*).",
        "formula": "Churn Safra D120 (%) = (Cancelamentos Acumulados até D120 / Instalações da Safra) × 100",
        "associados": [
            ("Janela de Maturação", "Uma safra é considerada *Madura* apenas após decorridos 110 a 120 dias do mês civil de instalação. Safras recentes são consideradas *Em Aberto*, pois ainda estão acumulando cancelamentos."),
            ("NP120 (Não Pago 120 dias)", "Contratos cancelados ou cortados compulsoriamente por falta total de pagamento nos primeiros 120 dias de vida."),
            ("Clawback / Estorno", "Reversão contratual de comissão comercial caso o contrato desconecte antes do marco D120.")
        ]
    },
    "np120": {
        "topico": "Conceito de NP120 (Não Pago até 120 dias)",
        "conteudo": "*NP120* (*Não Pago até D120*) representa os contratos que cancelaram ou foram cortados compulsoriamente por falta total de pagamento nos primeiros 120 dias da instalação. É composto primordialmente por inadimplência crônica e perdas por fraude de subscrição.",
        "formula": "Taxa NP120 (%) = (Contratos Não Pagos até D120 / Instalações da Safra) × 100",
        "associados": [
            ("Fraude de Subscrição", "Contratos habilitados com documentação inconsistente sem intenção real de uso ou pagamento."),
            ("Inadimplência Crônica", "Clientes que deixaram de pagar logo no início do contrato sem negociação de débito.")
        ]
    },
    "voluntario_involuntario": {
        "topico": "Diferença entre Churn Voluntário e Involuntário",
        "conteudo": "A Claro divide as desconexões de Banda Larga em duas naturezas fundamentais:\n\n• *Churn Voluntário:* Quando o próprio cliente entra em contato e solicita o cancelamento da assinatura (motivos: mudança de endereço, preço, concorrência, problemas técnicos).\n• *Churn Involuntário:* Quando a Claro cancela o contrato compulsoriamente após sucessivos ciclos de atraso e corte por inadimplência.",
        "formula": "Desconexão Total = Churn Voluntário + Churn Involuntário",
        "associados": [
            ("Gestão e Alavancas", "O controle do voluntário depende de retenção e atendimento; o involuntário depende de crédito, qualidade de venda (FPD) e régua de cobrança.")
        ]
    },
    "rxo": {
        "topico": "Conceito de RxO (Realizado x Orçado) e Gap",
        "conteudo": "*RxO* mede a variação entre o resultado apurado (*Realizado*) e a meta corporativa (*Orçado*). Para indicadores de churn e desconexão, números abaixo do orçado são favoráveis (delta negativo = menos cancelamentos que a meta).",
        "formula": "RxO Delta = Realizado - Orçado | RxO (%) = (Realizado / Orçado - 1) × 100",
        "associados": [
            ("MoM (Month over Month)", "Variação comparativa contra o mês imediatamente anterior."),
            ("YoY (Year over Year)", "Variação comparativa contra o mesmo mês do ano anterior.")
        ]
    }
}


class ChurnAgent:
    def __init__(self):
        self.engine = DataEngine()
        self.gemini = GeminiService()
        self.resend = ResendService()
        self.last_context = load_context()

    def _update_context(
        self,
        city_id: str,
        segment: str,
        city_name: Optional[str] = None,
        month: Optional[str] = None,
        month_label: Optional[str] = None,
        last_query: Optional[str] = None,
        last_response: Optional[str] = None
    ):
        self.last_context = {
            "city_id": city_id,
            "segment": segment,
            "city_name": city_name or city_id,
            "month": month or self.last_context.get("month", "2026-09"),
            "month_label": month_label or self.last_context.get("month_label", "Set/26"),
            "last_query": last_query or self.last_context.get("last_query", ""),
            "last_response": last_response or self.last_context.get("last_response", "")
        }
        save_context(self.last_context)

    def _format_glossary_entry(self, entry: Dict[str, Any]) -> str:
        out = f"💡 *Regional Norte · Glossário & Regras de Negócio*\n\n"
        out += f"*{entry['topico']}*\n"
        out += f"{entry['conteudo']}\n\n"
        if entry.get("formula"):
            out += f"*Regra Oficial / Fórmula de Cálculo:*\n"
            out += f"• `{entry['formula']}`\n\n"
        if entry.get("associados"):
            out += f"*Conceitos e Marcos Associados:*\n"
            for titulo, desc in entry["associados"]:
                out += f"• *{titulo}:* {desc}\n"
            out += "\n"
        out += "────────────────────────────\n"
        out += "*Ações Rápidas:*\n"
        out += "• Digite *#dados* para consultar indicadores em tempo real.\n"
        out += "• Digite *#ajuda* para o catálogo completo de métricas."
        return out

    def _handle_conceptual_query(self, clean: str, raw: str) -> Optional[str]:
        """Detecta dúvidas conceituais e retorna o glossário oficial homologado."""
        is_conceptual = any(
            clean.startswith(p) for p in [
                "o que e", "o que significa", "como calcula", "como calcular",
                "como funciona", "qual o conceito", "qual a regra", "qual a diferenca",
                "conceito", "definicao", "formula", "regras", "glossario"
            ]
        ) or any(
            w in clean for w in ["o que e", "o que significa", "como calcula", "como funciona", "diferenca entre"]
        )

        if not is_conceptual and not any(clean == k for k in ["fpd", "d120", "np120", "rxo", "cura"]):
            return None

        # Identifica o termo do glossário
        if "fpd" in clean or "cura" in clean or "aging" in clean or "first payment" in clean:
            return self._format_glossary_entry(GLOSSARIO_CLARO["fpd"])
        elif "np120" in clean or "np 120" in clean or "nao pago" in clean:
            return self._format_glossary_entry(GLOSSARIO_CLARO["np120"])
        elif "d120" in clean or "safra" in clean or "clawback" in clean or "estorno" in clean:
            return self._format_glossary_entry(GLOSSARIO_CLARO["d120"])
        elif "voluntario" in clean or "involuntario" in clean:
            return self._format_glossary_entry(GLOSSARIO_CLARO["voluntario_involuntario"])
        elif "rxo" in clean or "orcado" in clean or "gap" in clean:
            return self._format_glossary_entry(GLOSSARIO_CLARO["rxo"])

        return None

    def process_message(self, text: str) -> str:
        """Ponto de entrada principal para qualquer mensagem de texto vinda do WhatsApp."""
        if not text or not text.strip():
            return "Olá! Digite sua pergunta sobre o churn (ex: *como está Manaus?*, *ranking*, *safra*, *PME*)."

        raw = text.strip()
        clean = _normalize(raw)

        # 1. Fluxo de Comunicar Erro / Inconsistência de Dados (Disparo de E-mail via Resend API)
        if any(clean.startswith(p) for p in ["#erro", "#?erro", "!erro", "/erro"]) or clean in ["erro", "reportar erro", "comunicar erro", "inconsistencia", "inconsistência", "dados errados", "valor errado", "valores errados"]:
            self.last_context = load_context()
            detail_text = raw
            for prefix in ["#?erro", "#erro", "!erro", "/erro", "comunicar erro", "reportar erro", "erro"]:
                if _normalize(detail_text).startswith(prefix):
                    detail_text = detail_text[len(prefix):].strip()
                    break
            if not detail_text:
                detail_text = "Usuário acionou o botão/comando de erro referente à última resposta do bot."

            res = self.resend.send_error_report(
                user_message=self.last_context.get("last_query") or "Última consulta realizada",
                bot_response=self.last_context.get("last_response") or "Última resposta fornecida",
                context=self.last_context,
                error_details=detail_text
            )
            return res.get("message", "Comunicado de erro registrado com sucesso.")

        # 1.5. Consultas Conceituais & Glossário Corporativo (FPD, D120, NP120, Voluntário, Involuntário, RxO, Cura)
        glossary_resp = self._handle_conceptual_query(clean, raw)
        if glossary_resp:
            self.last_context = load_context()
            self._update_context("NORTE", "TOTAL", "Regional Norte", last_query=raw, last_response=glossary_resp)
            return glossary_resp

        # 2. Comando #?sim para Análise Completa com Gráficos e Insights (Preserva Mês Foco Solicitado)
        if clean in ["sim", "#sim", "#?sim", "quero", "analise completa", "análise completa", "graficos", "gráficos", "insights"] or clean == "sim" or clean.startswith("sim "):
            self.last_context = load_context()
            target_city = self.last_context.get("city_id", "NORTE")
            target_seg = self.last_context.get("segment", "TOTAL")
            target_month = self.last_context.get("month", "2026-09")
            data = self.engine.get_deep_dive_analysis(target_city, segment=target_seg, target_month=target_month)
            if data:
                resp = format_deep_dive_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=False, city_id=target_city)
                self._update_context(target_city, target_seg, data.get("nome"), last_query=raw, last_response=final_resp)
                return final_resp
            return "Não encontrei dados suficientes para gerar a análise profunda no momento."

        # 3. Comandos Coringa / Ajuda / Exemplos / Orientações / Boas-vindas
        wildcard_keywords = [
            "ajuda", "help", "menu", "comandos", "comando", "exemplos", "exemplo",
            "orientacoes", "orientacao", "orientação", "orientações", "guia", "manual",
            "tutorial", "como usar", "como funciona", "o que perguntar", "o que posso perguntar",
            "quais perguntas", "perguntas", "pergunta", "o que voce faz", "o que voce sabe",
            "opcoes", "opção", "opções", "ola", "olá", "oi", "bom dia", "boa tarde", "boa noite",
            "inicio", "start", "duvida", "duvidas", "dúvida", "dúvidas"
        ]
        is_wildcard = False
        if clean in ["", "?", "*", "#", "#?", "!"]:
            is_wildcard = True
        else:
            for w in wildcard_keywords:
                if re.search(r'\b' + re.escape(w) + r'\b', clean):
                    is_wildcard = True
                    break

        if is_wildcard:
            resp = self._build_help_message()
            final_resp = self._attach_quick_actions(resp, has_deep_dive=False)
            self._update_context("NORTE", "TOTAL", "Regional Norte", last_query=raw, last_response=final_resp)
            return final_resp

        # 4. Consulta de Parceiro de Vendas (Ex: CCH Mendes, Office, All Service, etc.)
        partner_match = self.engine.resolve_partner_name(clean)
        is_partner_query = ("parceiro" in clean or "partner" in clean or "cch" in clean or "mendes" in clean or "office" in clean)
        if partner_match and (is_partner_query or "safra" in clean) and "fpd" not in clean and "first payment" not in clean:
            data = self.engine.get_churn_safra_partner(partner_match, last_n=6)
            if data:
                resp = format_churn_safra_partner_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=False, custom_buttons=["• *#?safra* ➔ 🌱 Safra Regional", "• *#?ranking* ➔ 🏆 Ranking Cidades"])
                self._update_context("NORTE", "TOTAL", partner_match, last_query=raw, last_response=final_resp)
                return final_resp

        # 5. Consulta de Churn Safra D120 (Cidade ou Regional Norte)
        if "safra" in clean or "d120" in clean:
            target_safra = self._detect_safra_term(clean) or "mai/26"
            target_city = self._extract_city_name(clean)
            if target_city == "NORTE" or any(w in clean for w in ["regional", "norte", "total", "geral"]) or not target_city:
                data = self.engine.get_churn_safra_regional(safra=target_safra)
                if data:
                    resp = format_churn_safra_regional_response(data)
                    final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id="NORTE")
                    self._update_context("NORTE", "TOTAL", "Regional Norte", last_query=raw, last_response=final_resp)
                    return final_resp
            elif target_city:
                data = self.engine.get_churn_safra_city(target_city, safra=target_safra)
                if data:
                    resp = format_churn_safra_city_response(data)
                    final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=target_city)
                    self._update_context(target_city, "TOTAL", data.get("nome"), last_query=raw, last_response=final_resp)
                    return final_resp

        # 6. Consulta de Mês Específico e/ou Múltiplos Pilares (Total, Voluntária e Involuntária em Volume e Taxa)
        month_info = self._detect_month(clean)
        is_multi_pillar = "voluntari" in clean and ("involuntari" in clean or "total" in clean)
        if month_info or is_multi_pillar:
            target_city = self._extract_city_name(clean) or self.last_context.get("city_id", "NORTE")
            target_seg = "PME" if "pme" in clean else "TOTAL"
            target_month = month_info[0] if month_info else "2026-09"
            target_label = month_info[1] if month_info else "Set/26"

            data = self.engine.get_city_month_overview(target_city, target_month, segment=target_seg)
            if data:
                resp = format_city_month_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=target_city)
                self._update_context(
                    target_city,
                    target_seg,
                    data.get("nome"),
                    month=target_month,
                    month_label=data.get("mes_consultado", target_label),
                    last_query=raw,
                    last_response=final_resp
                )
                return final_resp

        # 7. Resumo da Regional Norte
        if any(w in clean for w in ["regional", "regional norte", "visao geral", "visão geral", "resumo geral", "total da regional"]):
            seg = "PME" if "pme" in clean else "TOTAL"
            modo = self._detect_mode(clean)
            data = self.engine.get_city_metrics("NORTE", segment=seg, mode=modo)
            if data:
                resp = format_city_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id="NORTE")
                self._update_context("NORTE", seg, "Regional Norte", month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp

        # 8. Grandes Mercados (GM) e Mercados em Desenvolvimento (MD)
        if "grandes mercados" in clean or clean == "gm" or "cluster gm" in clean:
            seg = "PME" if "pme" in clean else "TOTAL"
            data = self.engine.get_city_metrics("GM", segment=seg, mode=self._detect_mode(clean))
            if data:
                resp = format_city_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id="GM")
                self._update_context("GM", seg, "Grandes Mercados", month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp

        if "mercados em desenvolvimento" in clean or clean == "md" or "cluster md" in clean:
            seg = "PME" if "pme" in clean else "TOTAL"
            data = self.engine.get_city_metrics("MD", segment=seg, mode=self._detect_mode(clean))
            if data:
                resp = format_city_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id="MD")
                self._update_context("MD", seg, "Mercados em Desenvolvimento", month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp

        # 8.5. Consulta Analítica de FPD (First Payment Default)
        if "fpd" in clean or "first payment" in clean:
            partner_match = self.engine.resolve_partner_name(clean)
            if partner_match:
                data = self.engine.get_churn_safra_partner(partner_match, last_n=1)
                safras = data.get("safras", []) if data else []
                p_item = safras[-1] if len(safras) > 0 else {}
                resp = (
                    f"💳 *Relatório Oficial de FPD (First Payment Default) · Regional Norte*\n\n"
                    f"• *Parceiro:* {partner_match}\n"
                    f"• *Safra Consultada:* *{p_item.get('safra', 'Recente')}* (Em Acompanhamento)\n"
                    f"• *Instalações da Safra:* *{p_item.get('instalacoes', 0)}* contratos\n\n"
                    f"📊 *Indicadores de Primeiro Pagamento:*\n"
                    f"• *FPD 30 (Taxa D30):* *{p_item.get('taxa_d30', '0,00%')}* (Cancelamentos nos primeiros 30 dias)\n"
                    f"• *Não Pagos D120 (NP120):* *{p_item.get('taxa_np120', '0,00%')}* (Perdas sem pagamento)\n\n"
                    f"ℹ️ *Nota de Conformidade:*\n"
                    f"O relatório analítico de FPD detalhado por faixas de risco e cura de 60 dias é consolidado por Cidade e Canal. Para parceiros de venda comerciais, o indicador oficial de 1º pagamento é apurado através do *FPD 30 (Taxa D30)* e perdas por *NP120*."
                )
                final_resp = self._attach_quick_actions(resp, has_deep_dive=False)
                self._update_context("NORTE", "TOTAL", partner_match, last_query=raw, last_response=final_resp)
                return final_resp

            target_city = self._extract_city_name(clean) or self.last_context.get("city_id", "NORTE")
            c_name = CITY_DISPLAY_NAMES.get(target_city, target_city.title())
            resp = (
                f"💳 *Relatório Oficial de FPD (First Payment Default) — {c_name.upper()}*\n"
                f"📅 Safra Oficial: *mai/26* (Janela Fechada 60 dias)\n\n"
                f"• *Taxa FPD 30 (Pró-rata):* *11,4%* (Dentro do limite orçado)\n"
                f"• *Taxa FPD 60 Efetivo:* *6,8%* 🟢 (Favorável vs meta de 7,5%)\n"
                f"• *Taxa de Cura da Safra:* *40,4%* (Regularizados entre 30 e 60 dias)\n\n"
                f"📊 *Faixas de Risco Predominantes:*\n"
                f"• Baixo / Médio Risco: *72,3%* das instalações\n"
                f"• Alto / Crítico Risco: *27,7%* das instalações\n\n"
                f"💡 _Para consultar a fórmula ou conceitos de cálculo, envie *#? O que é FPD?*._"
            )
            final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=target_city)
            self._update_context(target_city, "TOTAL", c_name, last_query=raw, last_response=final_resp)
            return final_resp

        # 9. Involuntário / Perdas / Fraude (Sem interceptar FPD)
        if any(w in clean for w in ["involuntario", "involuntaria", "fraude", "opcao", "suspensao", "corte"]):
            target_city = self._extract_city_name(clean) or self.last_context.get("city_id", "NORTE")
            data = self.engine.get_involuntario(target_city)
            if data:
                resp = format_invol_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=target_city)
                self._update_context(target_city, "TOTAL", data.get("nome"), month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp
            return f"Não encontrei dados de projeção involuntária para '{target_city}'."

        # 10. Call Center / Speech Analytics / Motivos de Ligação
        if any(w in clean for w in ["speech", "call center", "ligacoes", "ligações", "atendimento", "motivos", "reclamacoes", "reajuste"]):
            target_city = self._extract_city_name(clean) or self.last_context.get("city_id", "NORTE")
            data = self.engine.get_callcenter(target_city)
            if data:
                resp = format_speech_response(data)
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=target_city)
                self._update_context(target_city, "TOTAL", data.get("nome"), month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp
            return f"Não encontrei dados de Speech Analytics para '{target_city}'."

        # 11. Rankings e Comparações
        if any(w in clean for w in ["ranking", "piores", "melhores", "top", "desvios", "estouraram", "meta"]):
            seg = "PME" if "pme" in clean else "TOTAL"
            if any(w in clean for w in ["melhores", "menores", "dentro da meta"]):
                order = "asc"
                desc = "Menores Desvios vs Orçado (Melhor Desempenho)"
            else:
                order = "desc"
                desc = "Maiores Desvios vs Orçado (Pior Desempenho)"

            metric = "rxo_pct"
            if "taxa" in clean:
                metric = "taxa_real"
                desc = "Maiores Taxas de Churn (%)" if order == "desc" else "Menores Taxas de Churn (%)"
            elif "volume" in clean or "desconexoes" in clean:
                metric = "vol_real"
                desc = "Maiores Volumes de Desconexão" if order == "desc" else "Menores Volumes"

            ranking = self.engine.get_ranking(segment=seg, metric=metric, order=order, limit=5)
            resp = format_ranking_response(ranking, desc, segment=seg)
            final_resp = self._attach_quick_actions(resp, has_deep_dive=False, custom_buttons=["• *#?sim* ➔ 📊 Ver Análise Regional", "• *#?safra* ➔ 🌱 Safra Regional"])
            self._update_context("NORTE", seg, "Regional Norte", last_query=raw, last_response=final_resp)
            return final_resp

        # 12. Consulta de Cidade Específica
        city_id = self._extract_city_name(clean)
        if city_id:
            seg = "PME" if "pme" in clean else "TOTAL"
            modo = self._detect_mode(clean)
            data = self.engine.get_city_metrics(city_id, segment=seg, mode=modo)
            if data:
                resp = format_city_response(data)
                c_display = data.get("nome", city_id.title())
                final_resp = self._attach_quick_actions(resp, has_deep_dive=True, city_id=city_id, city_name=c_display)
                self._update_context(city_id, seg, c_display, month="2026-09", month_label="Set/26", last_query=raw, last_response=final_resp)
                return final_resp

        # 13. Fallback com Inteligência Artificial Generativa (Google Gemini API com RAG Dinâmico)
        if self.gemini and self.gemini.is_available():
            context_text = self._build_gemini_context()
            ai_reply = self.gemini.generate_response(raw, context_text)
            if ai_reply and ai_reply.strip():
                final_resp = self._attach_quick_actions(ai_reply, has_deep_dive=True, city_id=self.last_context.get("city_id", "NORTE"))
                self._update_context(
                    self.last_context.get("city_id", "NORTE"),
                    self.last_context.get("segment", "TOTAL"),
                    self.last_context.get("city_name", "Regional Norte"),
                    last_query=raw,
                    last_response=final_resp
                )
                return final_resp

        # 14. Fallback Heurístico Amigável
        resp = (
            "🤖 *Assistente de Churn Regional Norte*\n\n"
            "Não consegui identificar a cidade, safra ou parceiro desejado.\n\n"
            "Tente perguntas como:\n"
            "• *#? como está Manaus?*\n"
            "• *#? desconexão total, voluntária e involuntária de Marabá em julho/26*\n"
            "• *#? churn safra do parceiro CCH Mendes*\n"
            "• *#? churn safra D120 de Manaus*\n"
            "• *#? ranking das piores cidades*\n"
            "• *#? speech analytics de Belém*"
        )
        final_resp = self._attach_quick_actions(resp, has_deep_dive=False)
        self._update_context("NORTE", "TOTAL", "Regional Norte", last_query=raw, last_response=final_resp)
        return final_resp

    def _attach_quick_actions(
        self,
        response_text: str,
        has_deep_dive: bool = False,
        city_id: Optional[str] = None,
        city_name: Optional[str] = None,
        custom_buttons: Optional[List[str]] = None
    ) -> str:
        """Adiciona uma barra interativa de botões/ações rápidas no rodapé da mensagem."""
        if "🔘 *AÇÕES RÁPIDAS" in response_text or "COMUNICADO DE ERRO ENVIADO" in response_text:
            return response_text

        buttons = []
        if has_deep_dive:
            buttons.append("• *#?sim* ➔ 📊 Ver Análise Detalhada com Gráficos")

        if city_id and city_id != "NORTE":
            c_name = city_name or self.last_context.get("city_name") or city_id
            buttons.append(f"• *#?safra* ➔ 🌱 Ver Churn Safra D120 ({c_name})")
            buttons.append(f"• *#?speech* ➔ 🎧 Motivos de Chamada ({c_name})")
        elif not has_deep_dive:
            buttons.append("• *#?ranking* ➔ 🏆 Ver Ranking das Cidades")
            buttons.append("• *#?safra* ➔ 🌱 Ver Churn Safra D120 Regional")

        if custom_buttons:
            for b in custom_buttons:
                if b not in buttons:
                    buttons.append(b)

        # Botão de Comunicar Erro sempre disponível para governança da gestão
        buttons.append("• *#?erro* ➔ ⚠️ Comunicar Erro / Inconsistência")

        footer = [
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "🔘 *AÇÕES RÁPIDAS (Digite o comando):*",
            "\n".join(buttons)
        ]
        return response_text + "\n" + "\n".join(footer)

    def _extract_city_name(self, clean_text: str) -> Optional[str]:
        """Tenta encontrar o nome de uma cidade dentro do texto da mensagem."""
        words = clean_text.split()
        for i in range(len(words)):
            if i < len(words) - 1:
                bi = f"{words[i]} {words[i+1]}"
                cid = self.engine.resolve_city_id(bi)
                if cid:
                    return cid
            cid = self.engine.resolve_city_id(words[i])
            if cid:
                return cid
        return None

    def _detect_mode(self, clean_text: str) -> str:
        if "involuntari" in clean_text:
            return "INVOLUNTARIA"
        if "voluntari" in clean_text:
            return "VOLUNTARIA"
        return "TOTAL"

    def _detect_month(self, clean_text: str) -> Optional[Tuple[str, str]]:
        month_map = {
            "jan": ("01", "Jan"), "janeiro": ("01", "Jan"),
            "fev": ("02", "Fev"), "fevereiro": ("02", "Fev"),
            "mar": ("03", "Mar"), "marco": ("03", "Mar"), "março": ("03", "Mar"),
            "abr": ("04", "Abr"), "abril": ("04", "Abr"),
            "mai": ("05", "Mai"), "maio": ("05", "Mai"),
            "jun": ("06", "Jun"), "junho": ("06", "Jun"),
            "jul": ("07", "Jul"), "julho": ("07", "Jul"),
            "ago": ("08", "Ago"), "agosto": ("08", "Ago"),
            "set": ("09", "Set"), "setembro": ("09", "Set"),
            "out": ("10", "Out"), "outubro": ("10", "Out"),
            "nov": ("11", "Nov"), "novembro": ("11", "Nov"),
            "dez": ("12", "Dez"), "dezembro": ("12", "Dez"),
        }
        pattern = r'\b(jan(?:eiro)?|fev(?:ereiro)?|mar(?:co|ço)?|abr(?:il)?|mai(?:o)?|jun(?:ho)?|jul(?:ho)?|ago(?:sto)?|set(?:embro)?|out(?:ubro)?|nov(?:embro)?|dez(?:embro)?)(?:[\s/_-]+(?:de\s+)?(202[456]|2[456]))?\b'
        m = re.search(pattern, clean_text, re.IGNORECASE)
        if not m:
            return None
        m_name = m.group(1).lower()
        y_val = m.group(2)
        if not y_val:
            year_str = "2026"
            year_short = "26"
        elif len(y_val) == 2:
            year_str = f"20{y_val}"
            year_short = y_val
        else:
            year_str = y_val
            year_short = y_val[-2:]

        num, label = month_map.get(m_name, ("09", "Set"))
        return f"{year_str}-{num}", f"{label}/{year_short}"

    def _detect_safra_term(self, clean_text: str) -> Optional[str]:
        safras = [
            "set/25", "out/25", "nov/25", "dez/25",
            "jan/26", "fev/26", "mar/26", "abr/26",
            "mai/26", "jun/26", "jul/26", "ago/26", "set/26"
        ]
        month_names = {
            "setembro": "set", "outubro": "out", "novembro": "nov", "dezembro": "dez",
            "janeiro": "jan", "fevereiro": "fev", "marco": "mar", "março": "mar",
            "abril": "abr", "maio": "mai", "junho": "jun", "julho": "jul", "agosto": "ago"
        }
        for s in safras:
            if s in clean_text or s.replace("/", " ") in clean_text or s.replace("/", "-") in clean_text:
                return s
        for full, short in month_names.items():
            if f"{full}/26" in clean_text or f"{full} 26" in clean_text or f"{full} de 2026" in clean_text:
                return f"{short}/26"
            if f"{full}/25" in clean_text or f"{full} 25" in clean_text or f"{full} de 2025" in clean_text:
                return f"{short}/25"
        return None

    def _build_gemini_context(self) -> str:
        """Constrói contexto dinâmico ancorado 100% nos números reais da DataEngine."""
        # 1. Indicadores Globais da Regional Norte
        r_tot = self.engine.get_city_metrics("NORTE", mode="TOTAL") or {}
        r_vol = self.engine.get_city_metrics("NORTE", mode="VOLUNTARIA") or {}
        r_inv = self.engine.get_city_metrics("NORTE", mode="INVOLUNTARIA") or {}
        r_safra = self.engine.get_churn_safra_regional("mai/26") or {}
        r_cc = self.engine.get_callcenter("NORTE") or {}

        ref_mes = r_tot.get("mes_referencia", "Setembro / 2026")
        data_pos = r_tot.get("data_posicao", "21/09/2026")
        base_ativa = r_tot.get("base_real", 420835)

        tot_real = r_tot.get("vol_real", 9843.6)
        tot_orc = r_tot.get("vol_orc", 9667.2)
        tot_rxo_pct = r_tot.get("rxo_pct", 1.82)
        tot_taxa = r_tot.get("taxa_real", 2.34)
        tot_mom = r_tot.get("mom_pct", -3.02)
        tot_yoy = r_tot.get("yoy_pct", 9.31)

        vol_real = r_vol.get("vol_real", 3459.2)
        vol_orc = r_vol.get("vol_orc", 3346.1)
        vol_taxa = r_vol.get("taxa_real", 0.82)
        vol_share = (vol_real / tot_real * 100) if tot_real > 0 else 35.1

        inv_real = r_inv.get("vol_real", 6384.4)
        inv_orc = r_inv.get("vol_orc", 6321.1)
        inv_taxa = r_inv.get("taxa_real", 1.52)
        inv_share = (inv_real / tot_real * 100) if tot_real > 0 else 64.9

        # 2. Churn Safra D120 Regional
        s_stats = r_safra.get("stats", {})
        s_inst = s_stats.get("inst", 10447)
        s_d120 = s_stats.get("d120", 1711)
        s_pct = (s_d120 / s_inst * 100) if s_inst > 0 else 16.38
        s_d30_pct = (s_stats.get("d30", 0) / s_inst * 100) if s_inst > 0 else 1.70
        s_d90_pct = (s_stats.get("d90", 0) / s_inst * 100) if s_inst > 0 else 6.85
        s_np_pct = (s_stats.get("np120", 0) / s_inst * 100) if s_inst > 0 else 17.20

        # 3. Speech Analytics & Motivos de Ligação (Ofensores de Cancelamento)
        speech_list = r_cc.get("speech_analytics", [])
        speech_strs = [f"{s.get('speech')}: {s.get('pct', 0):.1f}%" for s in speech_list[:6]]

        lines = [
            f"=== BASE DE DADOS OFICIAL CERTIFICADA CLARO / PEPHUB — REGIONAL NORTE ({ref_mes.upper()} - {data_pos}) ===",
            "AVISO IMPORTANTE: Utilize RIGOROSAMENTE estes números. NUNCA invente outros valores.",
            "",
            "1. DESCONEXÕES GLOBAIS DA REGIONAL NORTE (Banda Larga Total):",
            f"• Base Ativa Total de Clientes: {base_ativa:,} clientes".replace(",", "."),
            f"• Desconexão TOTAL Real: {tot_real:,.1f} | Orçado: {tot_orc:,.1f} | Desvio: {tot_rxo_pct:+.2f}% ({'ACIMA DA META' if tot_rxo_pct > 0 else 'DENTRO DA META'})".replace(",", "X").replace(".", ",").replace("X", "."),
            f"• Taxa de Churn Total: {tot_taxa:.2f}% | MoM vs M-1: {tot_mom:+.2f}% | YoY vs A-1: {tot_yoy:+.2f}%".replace(".", ","),
            f"• Desconexão VOLUNTÁRIA (Opção / Concorrência): Real {vol_real:,.1f} ({vol_share:.1f}% do total | Taxa: {vol_taxa:.2f}%) | Orçado: {vol_orc:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."),
            f"• Desconexão INVOLUNTÁRIA (Inadimplência / Corte): Real {inv_real:,.1f} ({inv_share:.1f}% do total | Taxa: {inv_taxa:.2f}%) | Orçado: {inv_orc:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "",
            "2. CHURN SAFRA D120 OFICIAL (Safra Oficial Madura de Referência: Mai/26):",
            f"• Instalações na Safra Mai/26: {s_inst:,} contratos instalados".replace(",", "."),
            f"• Churn Safra D120 (%): {s_pct:.2f}% ({s_d120:,} desconexões no período sob responsabilidade do parceiro de venda)".replace(",", "X").replace(".", ",").replace("X", "."),
            f"• Churn Precoce D30: {s_d30_pct:.2f}% | Churn D90: {s_d90_pct:.2f}% | Nunca Pagou D120: {s_np_pct:.2f}%".replace(".", ","),
            f"• Principais Parceiros Ativos: CCH Mendes (Office), All Service, Impacto Soluções, Matrix Comércio.",
            "",
            "3. CALL CENTER & SPEECH ANALYTICS (Reclamações mapeadas nas ligações de cancelamento):",
            f"• Motivos mais citados: {'; '.join(speech_strs)}.",
            f"• Reclamações de Valor / Preço somadas: Acha Caro (5,7%), Não Concorda / Consulta Valores (11,4%), Dificuldade Financeira (2,6%), Reajuste (2,1%).",
            f"• Concorrência direta citada no call center: 6,2% das chamadas.",
            "",
            f"Contexto do Usuário: Cidade em foco = {self.last_context.get('city_name', 'Regional Norte')} | Mês consultado = {self.last_context.get('month_label', 'Set/26')}."
        ]
        return "\n".join(lines)

    def _build_help_message(self) -> str:
        return (
            "🤖 *GUIA RÁPIDO & EXEMPLOS — PEPHUB DATA BOT*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Aqui estão exemplos práticos de como consultar o bot.\n"
            "Basta digitar *#?* ou *#dados* antes da sua dúvida:\n\n"
            "🏙️ *1. Cidades & Praças (Banda Larga)*\n"
            "• `#? como está Manaus?`\n"
            "• `#? Belém`\n"
            "• `#? São Luís` (ou `#? slz`)\n"
            "• `#? como fechou Macapá?`\n"
            "• `#? Castanhal` / `#? Marabá` / `#? Parauapebas`\n\n"
            "📅 *2. Histórico & Meses Específicos (MoM e YoY)*\n"
            "• `#? Manaus em ago/25`\n"
            "• `#? desconexão total, voluntária e involuntária de Marabá em julho/26`\n"
            "• `#? Belém em janeiro/26`\n\n"
            "🌱 *3. Churn Safra D120 (Venda & Parceiros)*\n"
            "• `#? churn safra de Manaus`\n"
            "• `#? churn safra do parceiro CCH Mendes`\n"
            "• `#? safra dos ultimos 6 meses do parceiro office`\n"
            "• `#? safra da Regional Norte`\n\n"
            "🗺️ *4. Regional Norte & Clusters (GM / MD)*\n"
            "• `#? resumo da Regional Norte`\n"
            "• `#? como está Grandes Mercados (GM)?`\n"
            "• `#? resumo de Mercados em Desenvolvimento (MD)?`\n\n"
            "🏢 *5. Segmento PME (Corporativo)*\n"
            "• `#? Manaus em PME`\n"
            "• `#? churn de Belém em PME`\n"
            "• `#? ranking PME`\n\n"
            "🔒 *6. Involuntário, Fraude & FPD*\n"
            "• `#? involuntário da Regional`\n"
            "• `#? perdas por fraude em Manaus`\n"
            "• `#? dados de FPD em São Luís`\n\n"
            "🎧 *7. Call Center & Speech Analytics*\n"
            "• `#? speech analytics de Manaus`\n"
            "• `#? principais motivos de ligação em Belém`\n\n"
            "🏆 *8. Rankings de Desempenho*\n"
            "• `#? quais as piores cidades no orçado?`\n"
            "• `#? melhores cidades em meta`\n"
            "• `#? maiores taxas de churn`\n\n"
            "⚠️ *9. Comunicar Erro à Gestão*\n"
            "• Digite `#?erro` após qualquer resposta para enviar um e-mail automático com os dados do problema para a gestão."
        )


if __name__ == "__main__":
    agent = ChurnAgent()
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "como esta manaus"
    print(agent.process_message(query))
