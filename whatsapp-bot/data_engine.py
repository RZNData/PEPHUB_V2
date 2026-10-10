"""
Data Engine para o Bot de WhatsApp do Pephub / Churn Regional Norte.
Carrega os dados consolidados de 'public/churn-bl-total/data.json' e 'public/churn-bl-pme/data.json'
e fornece consultas analíticas rápidas e formatação profissional para o WhatsApp.
"""

import json
import os
import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_TOTAL = os.path.join(ROOT_DIR, "public", "churn-bl-total", "data.json")
PATH_PME = os.path.join(ROOT_DIR, "public", "churn-bl-pme", "data.json")
PATH_SAFRA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safra_data.json")


def _normalize(text: str) -> str:
    """Remove acentos, espaços extras e coloca em minúsculas para comparação flexível."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join([c for c in text if not unicodedata.combining(c)])
    return text.strip().lower()


CITY_DISPLAY_NAMES = {
    "NORTE": "Regional Norte",
    "GM": "Grandes Mercados",
    "MD": "Mercados em Desenvolvimento",
    "MANAUS": "Manaus",
    "BELEM": "Belém",
    "SAO_LUIS": "São Luís",
    "ANANINDEUA": "Ananindeua",
    "MACAPA": "Macapá",
    "SANTANA": "Santana",
    "CASTANHAL": "Castanhal",
    "CAXIAS": "Caxias",
    "IMPERATRIZ": "Imperatriz",
    "MARABA": "Marabá",
    "PARAGOMINAS": "Paragominas",
    "PARAUAPEBAS": "Parauapebas",
    "TIMON": "Timon",
}


class DataEngine:
    def __init__(self):
        self.data_total = self._load_json(PATH_TOTAL)
        self.data_pme = self._load_json(PATH_PME)
        self.safra_data = self._load_json(PATH_SAFRA) if os.path.exists(PATH_SAFRA) else None
        self.city_alias_map = self._build_alias_map()

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_alias_map(self) -> Dict[str, str]:
        """Mapeia variações de nomes para o ID canônico da cidade."""
        alias = {
            "regional": "NORTE",
            "regional norte": "NORTE",
            "norte": "NORTE",
            "rno": "NORTE",
            "gm": "GM",
            "grandes mercados": "GM",
            "md": "MD",
            "mercados em desenvolvimento": "MD",
            "desenvolvimento": "MD",
            "manaus": "MANAUS",
            "mao": "MANAUS",
            "belem": "BELEM",
            "belém": "BELEM",
            "bel": "BELEM",
            "ananindeua": "ANANINDEUA",
            "macapa": "MACAPA",
            "macapá": "MACAPA",
            "santana": "SANTANA",
            "sao luis": "SAO_LUIS",
            "são luís": "SAO_LUIS",
            "slz": "SAO_LUIS",
            "castanhal": "CASTANHAL",
            "caxias": "CAXIAS",
            "imperatriz": "IMPERATRIZ",
            "itz": "IMPERATRIZ",
            "maraba": "MARABA",
            "marabá": "MARABA",
            "paragominas": "PARAGOMINAS",
            "parauapebas": "PARAUAPEBAS",
            "pebas": "PARAUAPEBAS",
            "timon": "TIMON",
        }
        # Adicionar os próprios IDs como alias
        for cid in list(set(alias.values())):
            alias[cid.lower()] = cid
            alias[cid.lower().replace("_", " ")] = cid
        return alias

    def resolve_city_id(self, query: str) -> Optional[str]:
        if not query:
            return None
        # Se já for um ID canônico
        q_upper = query.strip().upper()
        if q_upper in self.city_alias_map.values():
            return q_upper

        norm = _normalize(query)
        # Substituir underline por espaço e limpar pontuação
        norm = norm.replace("_", " ")
        norm = re.sub(r"[^\w\s]", "", norm).strip()
        if not norm:
            return None

        # 1. Correspondência exata no mapa de aliases
        if norm in self.city_alias_map:
            return self.city_alias_map[norm]

        # 2. Se a query contiver o alias como palavra inteira
        if len(norm) >= 3:
            for alias, cid in self.city_alias_map.items():
                if len(alias) >= 3 and alias in norm:
                    return cid

        return None

    def get_dataset(self, segment: str = "TOTAL") -> Dict[str, Any]:
        seg_upper = segment.upper()
        if "PME" in seg_upper:
            return self.data_pme
        return self.data_total

    def get_city_metrics(
        self, city_id_or_name: str, segment: str = "TOTAL", mode: str = "TOTAL"
    ) -> Optional[Dict[str, Any]]:
        dataset = self.get_dataset(segment)
        mode_upper = mode.upper()
        if mode_upper not in dataset.get("modes", {}):
            mode_upper = "TOTAL"

        cid = self.resolve_city_id(city_id_or_name)
        if not cid:
            return None

        cities = dataset["modes"][mode_upper].get("cities", [])
        for c in cities:
            if c.get("id") == cid:
                res = dict(c)
                res["segmento_label"] = dataset.get("segmento", "Banda Larga - Total")
                res["mes_referencia"] = dataset.get("mes_referencia", "Setembro / 2026")
                res["data_posicao"] = dataset.get("data_posicao", "S4")
                res["mode_label"] = mode_upper
                return res
        return None

    def get_ranking(
        self,
        segment: str = "TOTAL",
        mode: str = "TOTAL",
        metric: str = "rxo_pct",
        order: str = "desc",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        dataset = self.get_dataset(segment)
        mode_upper = mode.upper() if mode.upper() in dataset.get("modes", {}) else "TOTAL"

        cities = dataset["modes"][mode_upper].get("cities", [])
        # Filtrar apenas cidades reais (excluir Regional Norte, GM e MD do ranking de cidades)
        city_rows = [
            c for c in cities
            if c.get("id") not in ["NORTE", "GM", "MD"] and c.get("tipo") != "REGIONAL"
        ]

        reverse = order.lower() == "desc"
        sorted_cities = sorted(
            city_rows, key=lambda x: x.get(metric, 0) if x.get(metric) is not None else -999999, reverse=reverse
        )
        return sorted_cities[:limit]

    def get_involuntario(self, city_or_cluster: str = "NORTE") -> Optional[Dict[str, Any]]:
        cid = self.resolve_city_id(city_or_cluster) or "NORTE"
        invol = self.data_total.get("involuntaria_proj", {})
        if not invol:
            return None

        if cid == "NORTE":
            item = invol.get("regional")
        elif cid == "GM":
            item = invol.get("gm")
        elif cid == "MD":
            item = invol.get("md")
        else:
            item = invol.get("cities", {}).get(cid)

        if item:
            res = dict(item)
            res["nome"] = CITY_DISPLAY_NAMES.get(cid, cid.title())
            res["id"] = cid
            res["mes_referencia"] = self.data_total.get("mes_referencia", "Setembro / 2026")
            return res
        return None

    def get_callcenter(self, city_or_cluster: str = "NORTE") -> Optional[Dict[str, Any]]:
        cid = self.resolve_city_id(city_or_cluster) or "NORTE"
        cc = self.data_total.get("callcenter", {})
        if not cc:
            return None

        if cid == "NORTE":
            item = cc.get("regional")
        elif cid == "GM":
            item = cc.get("gm")
        elif cid == "MD":
            item = cc.get("md")
        else:
            item = cc.get("cities", {}).get(cid)

        if item:
            res = dict(item)
            res["nome"] = CITY_DISPLAY_NAMES.get(cid, cid.title())
            res["id"] = cid
            res["mes_referencia"] = self.data_total.get("mes_referencia", "Setembro / 2026")
            return res
        return None

    def get_city_month_overview(
        self, city_or_cluster: str = "NORTE", iso_or_label: str = "2026-07", segment: str = "TOTAL"
    ) -> Optional[Dict[str, Any]]:
        cid = self.resolve_city_id(city_or_cluster) or "NORTE"
        dataset = self.get_dataset(segment)
        modes = dataset.get("modes", {})

        def extract_from_timeline(mode_name: str):
            timeline = modes.get(mode_name, {}).get("timeline", [])
            for idx, item in enumerate(timeline):
                iso_match = item.get("iso") == iso_or_label
                label_match = _normalize(item.get("label", "")) == _normalize(iso_or_label)
                prefix_match = _normalize(item.get("label", "")).startswith(_normalize(iso_or_label))
                if iso_match or label_match or prefix_match:
                    def get_val_at(timeline_idx):
                        if timeline_idx < 0 or timeline_idx >= len(timeline):
                            return None
                        t_item = timeline[timeline_idx]
                        if cid == "NORTE":
                            return t_item.get("realizado", 0)
                        elif cid == "GM":
                            return t_item.get("gm_real", 0)
                        elif cid == "MD":
                            return t_item.get("md_real", 0)
                        else:
                            return t_item.get("cities", {}).get(cid, {}).get("realizado", 0)

                    def get_orc_at(timeline_idx):
                        if timeline_idx < 0 or timeline_idx >= len(timeline):
                            return None
                        t_item = timeline[timeline_idx]
                        if cid == "NORTE":
                            return t_item.get("orcamento")
                        elif cid == "GM":
                            return t_item.get("gm_orc")
                        elif cid == "MD":
                            return t_item.get("md_orc")
                        else:
                            return t_item.get("cities", {}).get(cid, {}).get("orcamento")

                    real_val = get_val_at(idx)
                    orc_val = get_orc_at(idx)
                    prev_val = get_val_at(idx - 1) if idx > 0 else None
                    yoy_val = get_val_at(idx - 12) if idx >= 12 else None

                    mom_pct = ((real_val - prev_val) / prev_val * 100) if prev_val and prev_val > 0 else None
                    yoy_pct = ((real_val - yoy_val) / yoy_val * 100) if yoy_val and yoy_val > 0 else None
                    prev_label = timeline[idx - 1].get("label") if idx > 0 else None
                    yoy_label = timeline[idx - 12].get("label") if idx >= 12 else None

                    return {
                        "real": real_val,
                        "orc": orc_val,
                        "label": item.get("label"),
                        "iso": item.get("iso"),
                        "index": idx,
                        "mom_pct": mom_pct,
                        "yoy_pct": yoy_pct,
                        "prev_label": prev_label,
                        "yoy_label": yoy_label,
                    }
            return None

        tot_data = extract_from_timeline("TOTAL")
        vol_data = extract_from_timeline("VOLUNTARIA")
        inv_data = extract_from_timeline("INVOLUNTARIA")

        if not tot_data:
            return None

        # Base de clientes da praça
        cities_tot = modes.get("TOTAL", {}).get("cities", [])
        city_meta = next((c for c in cities_tot if c.get("id") == cid), {})
        base_real = city_meta.get("base_real")
        vol_atual = city_meta.get("vol_real")
        taxa_atual = city_meta.get("taxa_real")

        label_month = tot_data.get("label", iso_or_label)

        tot_real = tot_data.get("real", 0)
        tot_orc = tot_data.get("orc")
        tot_delta = (tot_real - tot_orc) if tot_orc is not None else None
        tot_pct = ((tot_real - tot_orc) / tot_orc * 100) if tot_orc and tot_orc > 0 else None
        tot_taxa = (tot_real / base_real * 100) if base_real and base_real > 0 else None

        vol_real = vol_data.get("real", 0) if vol_data else 0
        vol_orc = vol_data.get("orc") if vol_data else None
        vol_delta = (vol_real - vol_orc) if vol_orc is not None else None
        vol_pct = ((vol_real - vol_orc) / vol_orc * 100) if vol_orc and vol_orc > 0 else None
        vol_taxa = (vol_real / base_real * 100) if base_real and base_real > 0 else None
        vol_share = (vol_real / tot_real * 100) if tot_real and tot_real > 0 else None

        inv_real = inv_data.get("real", 0) if inv_data else 0
        inv_orc = inv_data.get("orc") if inv_data else None
        inv_delta = (inv_real - inv_orc) if inv_orc is not None else None
        inv_pct = ((inv_real - inv_orc) / inv_orc * 100) if inv_orc and inv_orc > 0 else None
        inv_taxa = (inv_real / base_real * 100) if base_real and base_real > 0 else None
        inv_share = (inv_real / tot_real * 100) if tot_real and tot_real > 0 else None

        return {
            "id": cid,
            "nome": CITY_DISPLAY_NAMES.get(cid, cid.title()),
            "segmento_label": dataset.get("segmento", "Banda Larga - Total"),
            "mes_consultado": label_month,
            "iso_consultado": tot_data.get("iso"),
            "base_real": base_real,
            "vol_atual": vol_atual,
            "taxa_atual": taxa_atual,
            "total": {
                "real": tot_real, "orc": tot_orc, "delta": tot_delta, "pct": tot_pct, "taxa": tot_taxa,
                "mom_pct": tot_data.get("mom_pct"), "yoy_pct": tot_data.get("yoy_pct"),
                "prev_label": tot_data.get("prev_label"), "yoy_label": tot_data.get("yoy_label")
            },
            "voluntaria": {
                "real": vol_real, "orc": vol_orc, "delta": vol_delta, "pct": vol_pct, "taxa": vol_taxa, "share": vol_share,
                "mom_pct": vol_data.get("mom_pct") if vol_data else None,
                "yoy_pct": vol_data.get("yoy_pct") if vol_data else None
            },
            "involuntaria": {
                "real": inv_real, "orc": inv_orc, "delta": inv_delta, "pct": inv_pct, "taxa": inv_taxa, "share": inv_share,
                "mom_pct": inv_data.get("mom_pct") if inv_data else None,
                "yoy_pct": inv_data.get("yoy_pct") if inv_data else None
            }
        }

    def resolve_partner_name(self, query: str) -> Optional[str]:
        """Localiza o parceiro correspondente com base no nome ou termo de busca."""
        if not self.safra_data or "parceiros" not in self.safra_data:
            return None
        parceiros = list(self.safra_data["parceiros"].keys())
        clean = _normalize(query)
        clean = re.sub(r'[^a-z0-9\s]', ' ', clean)
        stopwords = {
            "parceiro", "parceiros", "churn", "safra", "dados", "grafico", "meses",
            "ultimos", "como", "esta", "qual", "dos", "das", "para", "sobre", "ver",
            "mostrar", "quanto", "foi", "empresa", "canal"
        }
        words = [w for w in clean.split() if len(w) >= 3 and w not in stopwords]
        if not words:
            return None

        # Busca por sobreposição de palavras
        scores = []
        for p in parceiros:
            p_clean = _normalize(p)
            p_clean = re.sub(r'[^a-z0-9\s]', ' ', p_clean)
            p_words = set(p_clean.split())
            matched_words = [w for w in words if w in p_words or (len(w) >= 4 and w in p_clean)]
            if matched_words:
                inst_cnt = self.safra_data["parceiros"][p].get("total", {}).get("inst", 0)
                scores.append((p, len(matched_words), inst_cnt))
        if scores:
            scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
            return scores[0][0]
        return None

    def get_churn_safra_partner(self, partner_query: str, last_n: int = 6) -> Optional[Dict[str, Any]]:
        """Extrai evolução de safras, D120, motivos e cidades do parceiro de venda."""
        if not self.safra_data:
            return None
        p_name = self.resolve_partner_name(partner_query)
        if not p_name:
            return None

        p_info = self.safra_data.get("parceiros", {}).get(p_name)
        if not p_info:
            return None

        safras_dict = p_info.get("safras", {})
        safra_order = self.safra_data.get("safra_order", [])

        safras_list = []
        for s in safra_order[-last_n:]:
            st = safras_dict.get(s, {})
            inst = st.get("inst", 0)
            d120 = st.get("d120", 0)
            pct = (d120 / inst * 100) if inst > 0 else 0.0
            safras_list.append({
                "safra": s,
                "inst": inst,
                "d120": d120,
                "pct": round(pct, 2),
                "inad": st.get("inad", 0),
                "opc": st.get("opc", 0),
                "frd": st.get("frd", 0),
                "is_madura": s in ["set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26"],
                "is_referencia": (s == "mai/26")
            })

        return {
            "parceiro": p_name,
            "safras": safras_list,
            "total": p_info.get("total", {}),
            "top_cidades": p_info.get("top_cidades", [])
        }

    def get_churn_safra_city(self, city_or_cluster: str, safra: str = "mai/26") -> Optional[Dict[str, Any]]:
        """Extrai indicadores de safra D120 de uma cidade específica."""
        if not self.safra_data:
            return None
        cid = self.resolve_city_id(city_or_cluster) or "MANAUS"
        c_display = CITY_DISPLAY_NAMES.get(cid, cid.title())

        city_data = None
        city_name_found = c_display
        for c_key, c_val in self.safra_data.get("cidades", {}).items():
            if _normalize(c_key) == _normalize(c_display) or _normalize(c_key) == _normalize(cid):
                city_data = c_val
                city_name_found = c_key
                break

        if not city_data:
            return None

        safra_order = self.safra_data.get("safra_order", [])
        target_s = "mai/26"
        for s in safra_order:
            if _normalize(s) == _normalize(safra) or _normalize(s).startswith(_normalize(safra)):
                target_s = s
                break

        safras_dict = city_data.get("safras", {})
        st = safras_dict.get(target_s, {})

        history = []
        for s in safra_order:
            s_st = safras_dict.get(s, {})
            inst = s_st.get("inst", 0)
            d120 = s_st.get("d120", 0)
            pct = (d120 / inst * 100) if inst > 0 else 0.0
            history.append({
                "safra": s,
                "inst": inst,
                "d120": d120,
                "pct": round(pct, 2)
            })

        return {
            "id": cid,
            "nome": city_name_found,
            "safra": target_s,
            "stats": st,
            "total": city_data.get("total", {}),
            "top_parceiros": city_data.get("top_parceiros", []),
            "top_vendedores": city_data.get("top_vendedores", []),
            "history_safras": history
        }

    def get_churn_safra_regional(self, safra: str = "mai/26") -> Optional[Dict[str, Any]]:
        """Extrai indicadores de safra D120 da Regional Norte."""
        if not self.safra_data:
            return None
        safra_order = self.safra_data.get("safra_order", [])
        target_s = "mai/26"
        for s in safra_order:
            if _normalize(s) == _normalize(safra) or _normalize(s).startswith(_normalize(safra)):
                target_s = s
                break

        regional_dict = self.safra_data.get("regional", {})
        st = regional_dict.get(target_s, {})

        history = []
        for s in safra_order:
            s_st = regional_dict.get(s, {})
            inst = s_st.get("inst", 0)
            d120 = s_st.get("d120", 0)
            pct = (d120 / inst * 100) if inst > 0 else 0.0
            history.append({
                "safra": s,
                "inst": inst,
                "d120": d120,
                "pct": round(pct, 2)
            })

        return {
            "nome": "Regional Norte",
            "safra": target_s,
            "stats": st,
            "history_safras": history
        }

    def get_deep_dive_analysis(
        self, city_or_cluster: str = "NORTE", segment: str = "TOTAL", target_month: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        cid = self.resolve_city_id(city_or_cluster) or "NORTE"
        dataset = self.get_dataset(segment)
        modes = dataset.get("modes", {})

        cities_tot = modes.get("TOTAL", {}).get("cities", [])
        city_meta = next((c for c in cities_tot if c.get("id") == cid), {})
        if not city_meta:
            return None

        full_tot = modes.get("TOTAL", {}).get("timeline", [])
        full_vol = modes.get("VOLUNTARIA", {}).get("timeline", [])
        full_inv = modes.get("INVOLUNTARIA", {}).get("timeline", [])

        # Localizar o mês foco (se fornecido, e.g. "2025-08" ou "Ago/25")
        focus_idx = len(full_tot) - 1
        if target_month:
            for idx, item in enumerate(full_tot):
                iso_match = item.get("iso") == target_month
                lbl_match = _normalize(item.get("label", "")) == _normalize(target_month)
                prefix_match = _normalize(item.get("label", "")).startswith(_normalize(target_month))
                if iso_match or lbl_match or prefix_match:
                    focus_idx = idx
                    break

        # Janela de 5 meses até o mês foco
        start_idx = max(0, focus_idx - 4)
        timeline_tot = full_tot[start_idx : focus_idx + 1]
        timeline_vol = full_vol[start_idx : focus_idx + 1]
        timeline_inv = full_inv[start_idx : focus_idx + 1]

        focus_item_tot = full_tot[focus_idx] if focus_idx < len(full_tot) else {}
        focus_item_vol = full_vol[focus_idx] if focus_idx < len(full_vol) else {}
        focus_item_inv = full_inv[focus_idx] if focus_idx < len(full_inv) else {}

        def get_val_for_cid(item, default=0):
            if not item:
                return default
            if cid == "NORTE":
                return item.get("realizado", default)
            elif cid == "GM":
                return item.get("gm_real", default)
            elif cid == "MD":
                return item.get("md_real", default)
            return item.get("cities", {}).get(cid, {}).get("realizado", default)

        def get_orc_for_cid(item):
            if not item:
                return None
            if cid == "NORTE":
                return item.get("orcamento")
            elif cid == "GM":
                return item.get("gm_orc")
            elif cid == "MD":
                return item.get("md_orc")
            return item.get("cities", {}).get(cid, {}).get("orcamento")

        f_real = get_val_for_cid(focus_item_tot)
        f_orc = get_orc_for_cid(focus_item_tot)
        f_vol = get_val_for_cid(focus_item_vol)
        f_inv = get_val_for_cid(focus_item_inv)

        # MoM e YoY para o mês foco
        prev_item = full_tot[focus_idx - 1] if focus_idx > 0 else None
        yoy_item = full_tot[focus_idx - 12] if focus_idx >= 12 else None
        prev_real = get_val_for_cid(prev_item) if prev_item else None
        yoy_real = get_val_for_cid(yoy_item) if yoy_item else None

        mom_pct = ((f_real - prev_real) / prev_real * 100) if prev_real and prev_real > 0 else None
        yoy_pct = ((f_real - yoy_real) / yoy_real * 100) if yoy_real and yoy_real > 0 else None

        # Call Center & URA
        cc_raw = dataset.get("callcenter", {}).get("cities", {}).get(cid)
        if not cc_raw:
            if cid == "NORTE":
                cc_raw = dataset.get("callcenter", {}).get("regional", {})
            elif cid == "GM":
                cc_raw = dataset.get("callcenter", {}).get("gm", {})
            elif cid == "MD":
                cc_raw = dataset.get("callcenter", {}).get("md", {})
            else:
                cc_raw = dataset.get("callcenter", {}).get("regional", {})

        # Churn Safra Snapshot da Praça
        safra_city = self.get_churn_safra_city(cid, safra="mai/26")

        return {
            "id": cid,
            "nome": CITY_DISPLAY_NAMES.get(cid, cid.title()),
            "segmento_label": dataset.get("segmento", "Banda Larga - Total"),
            "mes_foco": focus_item_tot.get("label", "Set/26"),
            "iso_foco": focus_item_tot.get("iso", "2026-09"),
            "city_meta": city_meta,
            "foco_tot_real": f_real,
            "foco_tot_orc": f_orc,
            "foco_vol_real": f_vol,
            "foco_inv_real": f_inv,
            "mom_pct": mom_pct,
            "yoy_pct": yoy_pct,
            "prev_label": prev_item.get("label") if prev_item else None,
            "yoy_label": yoy_item.get("label") if yoy_item else None,
            "timeline_tot": timeline_tot,
            "timeline_vol": timeline_vol,
            "timeline_inv": timeline_inv,
            "callcenter": cc_raw or {},
            "motivos_matriz": (cc_raw or {}).get("motivos_matriz", [])[:5],
            "safra_city": safra_city,
        }


# ==============================================================================
# FORMATADORES WHATSAPP (Markdown com Emojis e Layout Executivo)
# ==============================================================================

def format_number(val: Optional[float], decimals: int = 1) -> str:
    if val is None:
        return "N/D"
    if decimals == 0:
        return f"{int(round(val)):,}".replace(",", ".")
    # Formatação com ponto para milhar e vírgula para decimal
    parts = f"{val:.{decimals}f}".split(".")
    int_part = f"{int(parts[0]):,}".replace(",", ".")
    dec_part = parts[1]
    return f"{int_part},{dec_part}"


def format_delta_badge(val: Optional[float], is_good_when_lower: bool = True) -> str:
    """Gera badge visual: para Churn, menor é melhor (queda = verde, alta = vermelho)."""
    if val is None:
        return ""
    sign = "+" if val > 0 else ""
    val_str = f"{sign}{val:.1f}%".replace(".", ",")
    if val > 0:
        badge = "🔴" if is_good_when_lower else "🟢"
        return f"{val_str} {badge}"
    elif val < 0:
        badge = "🟢" if is_good_when_lower else "🔴"
        return f"{val_str} {badge}"
    return "0,0% ⚪"


def format_pp_badge(val: Optional[float]) -> str:
    if val is None:
        return ""
    sign = "+" if val > 0 else ""
    val_str = f"{sign}{val:.2f}".replace(".", ",")
    badge = "🔴" if val > 0 else ("🟢" if val < 0 else "⚪")
    return f"{val_str} p.p. {badge}"


def format_city_response(c: Dict[str, Any]) -> str:
    nome = c.get("nome", "Desconhecido")
    seg = c.get("segmento_label", "Banda Larga")
    modo = c.get("mode_label", "TOTAL")
    ref = c.get("mes_referencia", "Setembro/2026")
    pos = c.get("data_posicao", "Fechamento")

    vol_real = c.get("vol_real", 0)
    vol_orc = c.get("vol_orc")
    rxo_pct = c.get("rxo_pct")
    rxo_delta = c.get("rxo_delta")

    mom_pct = c.get("mom_pct")
    yoy_pct = c.get("yoy_pct")

    taxa_real = c.get("taxa_real")
    taxa_orc = c.get("taxa_orc")
    taxa_pp = c.get("taxa_delta_pp")

    base = c.get("base_real", 0)

    # Tendências semanais
    t1, t2, t3, t4 = c.get("t1"), c.get("t2"), c.get("t3"), c.get("t4")

    # Ícone e status
    if rxo_pct is not None:
        status_icon = "🟢" if rxo_pct <= 0 else "🔴"
        status_text = "DENTRO DA META" if rxo_pct <= 0 else "ACIMA DA META"
    else:
        status_icon = "ℹ️"
        status_text = "EM ACOMPANHAMENTO"

    msg = [
        f"📊 *{nome.upper()} — {seg.upper()} ({modo})*",
        f"📅 Ref: *{ref}* ({pos})",
        "",
        f"• *Status:* {status_icon} *{status_text}*",
        f"• *Realizado:* *{format_number(vol_real, 1)}* desconexões",
    ]

    if vol_orc is not None and rxo_delta is not None and rxo_pct is not None:
        rxo_delta_str = f"{rxo_delta:+.1f}".replace(".", ",")
        msg.append(f"• *Orçado:* {format_number(vol_orc, 1)} (Desvio: {rxo_delta_str} / {format_delta_badge(rxo_pct)})")
    else:
        msg.append("• *Orçado:* Não cadastrado")

    if mom_pct is not None:
        msg.append(f"• *Vs Mês Anterior (MoM):* {format_delta_badge(mom_pct)}")
    if yoy_pct is not None:
        msg.append(f"• *Vs Ano Anterior (YoY):* {format_delta_badge(yoy_pct)}")

    if taxa_real is not None:
        tr_str = f"{taxa_real:.2f}%".replace(".", ",")
        taxa_str = f"• *Taxa de Churn:* *{tr_str}*"
        if taxa_orc is not None:
            to_str = f"{taxa_orc:.2f}%".replace(".", ",")
            taxa_str += f" (Orç: {to_str} | Δ {format_pp_badge(taxa_pp)})"
        msg.append(taxa_str)

    if base:
        msg.append(f"• *Base Ativa:* {format_number(base, 0)} clientes")

    if t1 is not None and t4 is not None:
        msg.append("")
        msg.append(f"📈 *Evolução Semanal:*")
        msg.append(f"  S1: {t1:.0f} | S2: {t2:.0f} | S3: {t3:.0f} | S4: {t4:.0f}")

    msg.append("")
    msg.append(f"💡 _Deseja uma análise completa com gráficos e insights de {nome}? Digite *#?sim*_")

    return "\n".join(msg)


def format_ranking_response(
    cities: List[Dict[str, Any]], metric_desc: str, segment: str = "TOTAL"
) -> str:
    seg_title = "PME" if "PME" in segment.upper() else "TOTAL"
    msg = [
        f"🏆 *RANKING DE CIDADES — CHURN {seg_title}*",
        f"📌 *Critério:* {metric_desc}",
        "",
    ]
    for i, c in enumerate(cities, 1):
        nome = c.get("nome")
        val = c.get("rxo_pct", 0)
        vol = c.get("vol_real", 0)
        badge = "🔴" if val > 0 else "🟢"
        val_str = f"{val:+.1f}%".replace(".", ",")
        msg.append(f"*{i}. {nome}*")
        msg.append(f"   • Real: *{format_number(vol, 1)}* | Desvio Orçado: *{val_str}* {badge}")

    return "\n".join(msg)


def format_invol_response(data: Dict[str, Any]) -> str:
    nome = data.get("nome", "Regional Norte")
    ref = data.get("mes_referencia", "Setembro / 2026")
    total = data.get("total", 0)
    taxa_tot = data.get("taxa_total", 0)
    taxa_tot_str = f"{taxa_tot:.2f}%".replace(".", ",")
    base = data.get("invol_base", 0)
    fpd = data.get("fpd", 0)
    fraude = data.get("fraude", 0)
    opcao = data.get("opcao", 0)

    mom_tot = data.get("mom_total_pct", 0)
    yoy_tot = data.get("yoy_total_pct", 0)

    pct_base_str = f"{data.get('pct_base', 0):.1f}%".replace(".", ",")
    pct_fpd_str = f"{data.get('pct_fpd', 0):.1f}%".replace(".", ",")
    pct_opcao_str = f"{data.get('pct_opcao', 0):.1f}%".replace(".", ",")
    pct_fraude_str = f"{data.get('pct_fraude', 0):.1f}%".replace(".", ",")

    msg = [
        f"🔒 *CHURN INVOLUNTÁRIO (PROJEÇÃO) — {nome.upper()}*",
        f"📅 Ref: *{ref}*",
        "",
        f"• *Total Involuntário:* *{format_number(total, 1)}* (Taxa: *{taxa_tot_str}*)",
        f"• *MoM:* {format_delta_badge(mom_tot)} | *YoY:* {format_delta_badge(yoy_tot)}",
        "",
        "🔍 *Composição das Perdas:*",
        f"• *Inadimplência Base:* {format_number(base, 1)} ({pct_base_str})",
        f"• *FPD (1º Pagamento):* {format_number(fpd, 1)} ({pct_fpd_str})",
        f"• *Opção / Suspensão:* {format_number(opcao, 1)} ({pct_opcao_str})",
        f"• *Fraude:* {format_number(fraude, 1)} ({pct_fraude_str})",
        "",
        f"💡 _Deseja uma análise completa com gráficos e insights de {nome}? Digite *#?sim*_"
    ]
    return "\n".join(msg)


def format_speech_response(data: Dict[str, Any]) -> str:
    cid = data.get("nome") or data.get("id", "NORTE")
    ref = data.get("mes_referencia", "Setembro / 2026")
    speech_list = data.get("speech_analytics", [])

    # Ordenar por percentual desc
    sorted_speech = sorted(speech_list, key=lambda x: x.get("pct", 0), reverse=True)[:6]

    msg = [
        f"🎧 *CALL CENTER / SPEECH ANALYTICS — {cid.upper()}*",
        f"📅 Ref: *{ref}*",
        "📌 *Principais Ofensores Mapeados nas Ligações:*",
        "",
    ]
    for s in sorted_speech:
        motivo = s.get("speech")
        pct = s.get("pct", 0)
        pct_str = f"{pct:.1f}%".replace(".", ",")
        mom = s.get("mom_pp", 0)
        mom_str = f"{mom:+.1f}".replace(".", ",")
        tend = s.get("tendencia", "Estável")
        icon = "🔺" if "Alta" in tend else ("🔻" if "Queda" in tend else "➡️")
        msg.append(f"• *{motivo}:* {pct_str} ({icon} {mom_str} p.p. vs M-1)")

    msg.append("")
    msg.append(f"💡 _Deseja uma análise completa com gráficos e insights de {cid}? Digite *#?sim*_")
    return "\n".join(msg)


def format_city_month_response(data: Dict[str, Any]) -> str:
    nome = data.get("nome", "Regional Norte")
    seg = data.get("segmento_label", "Banda Larga")
    mes = data.get("mes_consultado", "Histórico")

    tot = data["total"]
    vol = data["voluntaria"]
    inv = data["involuntaria"]

    tot_taxa_str = f"{tot['taxa']:.2f}%".replace(".", ",") if tot['taxa'] is not None else "N/D"
    vol_taxa_str = f"{vol['taxa']:.2f}%".replace(".", ",") if vol['taxa'] is not None else "N/D"
    inv_taxa_str = f"{inv['taxa']:.2f}%".replace(".", ",") if inv['taxa'] is not None else "N/D"

    vol_share_str = f"{vol['share']:.1f}%".replace(".", ",") if vol['share'] is not None else ""
    inv_share_str = f"{inv['share']:.1f}%".replace(".", ",") if inv['share'] is not None else ""

    status_icon = "🟢" if (tot["pct"] or 0) <= 0 else "🔴"
    status_text = "DENTRO DA META" if (tot["pct"] or 0) <= 0 else "ACIMA DA META"

    msg = [
        f"📊 *{nome.upper()} — DESCONEXÕES DE {mes.upper()}*",
        f"📍 Segmento: *{seg}*",
        f"• *Status:* {status_icon} *{status_text}*",
    ]

    # Comparativos MoM e YoY em destaque
    if tot.get("mom_pct") is not None or tot.get("yoy_pct") is not None:
        comp_parts = []
        if tot.get("mom_pct") is not None:
            comp_parts.append(f"*MoM:* {format_delta_badge(tot['mom_pct'])} (vs {tot.get('prev_label')})")
        if tot.get("yoy_pct") is not None:
            comp_parts.append(f"*YoY:* {format_delta_badge(tot['yoy_pct'])} (vs {tot.get('yoy_label')})")
        msg.append(f"• {' | '.join(comp_parts)}")

    msg.extend([
        "",
        f"🔵 *Desconexão TOTAL:*",
        f"  • *Volume Real:* *{format_number(tot['real'], 1)}* desconexões",
    ])
    if tot["orc"] is not None:
        delta_str = f"{tot['delta']:+.1f}".replace(".", ",")
        msg.append(f"  • *Orçado:* {format_number(tot['orc'], 1)} (Desvio: {delta_str} / {format_delta_badge(tot['pct'])})")
    msg.append(f"  • *Taxa de Churn Total:* *{tot_taxa_str}*")
    if tot.get("mom_pct") is not None:
        msg.append(f"  • *Comparativo:* MoM {format_delta_badge(tot['mom_pct'])} | YoY {format_delta_badge(tot.get('yoy_pct'))}")
    msg.append("")

    msg.append(f"🟢 *Desconexão VOLUNTÁRIA (Opção / Concorrência):*")
    msg.append(f"  • *Volume Real:* *{format_number(vol['real'], 1)}* ({vol_share_str} das perdas)")
    if vol["orc"] is not None:
        v_delta_str = f"{vol['delta']:+.1f}".replace(".", ",")
        msg.append(f"  • *Orçado:* {format_number(vol['orc'], 1)} (Desvio: {v_delta_str} / {format_delta_badge(vol['pct'])})")
    msg.append(f"  • *Taxa Voluntária:* *{vol_taxa_str}*")
    if vol.get("mom_pct") is not None:
        msg.append(f"  • *Comparativo:* MoM {format_delta_badge(vol['mom_pct'])} | YoY {format_delta_badge(vol.get('yoy_pct'))}")
    msg.append("")

    msg.append(f"🔴 *Desconexão INVOLUNTÁRIA (Inadimplência / Corte):*")
    msg.append(f"  • *Volume Real:* *{format_number(inv['real'], 1)}* ({inv_share_str} das perdas)")
    if inv["orc"] is not None:
        i_delta_str = f"{inv['delta']:+.1f}".replace(".", ",")
        msg.append(f"  • *Orçado:* {format_number(inv['orc'], 1)} (Desvio: {i_delta_str} / {format_delta_badge(inv['pct'])})")
    msg.append(f"  • *Taxa Involuntária:* *{inv_taxa_str}*")
    if inv.get("mom_pct") is not None:
        msg.append(f"  • *Comparativo:* MoM {format_delta_badge(inv['mom_pct'])} | YoY {format_delta_badge(inv.get('yoy_pct'))}")

    # Comparativo com mês atual de posição (se for diferente)
    if data.get("vol_atual") is not None and data.get("iso_consultado") != "2026-09":
        msg.append("")
        msg.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        diff = data["vol_atual"] - tot["real"]
        diff_str = f"{diff:+.1f}".replace(".", ",")
        icon = "🟢 Redução" if diff < 0 else "🔴 Aumento"
        msg.append(f"📌 *Comparativo com Set/26 (Posição Atual):*")
        msg.append(f"  • Volume Atual: *{format_number(data['vol_atual'], 1)}* ({diff_str} vs {mes} | {icon})")
        if data.get("taxa_atual") is not None:
            msg.append(f"  • Taxa Atual: *{data['taxa_atual']:.2f}%*".replace(".", ","))

    msg.append("")
    msg.append(f"💡 _Deseja uma análise completa com gráficos e insights de {nome}? Digite *#?sim*_")
    return "\n".join(msg)


def make_bar(val: float, max_val: float, length: int = 10) -> str:
    if max_val <= 0:
        return "░" * length
    bl = int(round((val / max_val) * length))
    bl = min(length, max(0, bl))
    return "█" * bl + "░" * (length - bl)


def format_deep_dive_response(data: Dict[str, Any]) -> str:
    nome = data.get("nome", "Regional Norte")
    cid = data.get("id", "NORTE")
    seg = data.get("segmento_label", "Banda Larga")
    meta = data["city_meta"]
    base = meta.get("base_real") or 1
    mes_foco = data.get("mes_foco", "Set/26")

    f_real = data.get("foco_tot_real", meta.get("vol_real", 0))
    f_orc = data.get("foco_tot_orc", meta.get("vol_orc"))
    f_vol = data.get("foco_vol_real", 0)
    f_inv = data.get("foco_inv_real", 0)
    mom_pct = data.get("mom_pct")
    yoy_pct = data.get("yoy_pct")

    # Status vs orçado
    if f_orc is not None and f_orc > 0:
        rxo_pct = (f_real - f_orc) / f_orc * 100
        rxo_str = f"{rxo_pct:+.1f}%".replace(".", ",")
        if rxo_pct <= 0:
            diag = f"🟢 *Desempenho Saudável:* A praça operou com folga de *{abs(rxo_pct):.1f}%* dentro da meta orçada."
        else:
            diag = f"🔴 *Alerta de Estouro:* A praça operou *{rxo_str}* acima da meta orçada."
    else:
        rxo_pct = meta.get("rxo_pct", 0)
        diag = "ℹ️ *Acompanhamento Histórico Oficial.*"

    # 1. Gráfico Histórico dos 5 Meses até o Mês Consultado
    timeline = data.get("timeline_tot", [])
    month_vals = []
    for item in timeline:
        lbl = item.get("label", "")
        if cid == "NORTE":
            v = item.get("realizado", 0)
        elif cid == "GM":
            v = item.get("gm_real", 0)
        elif cid == "MD":
            v = item.get("md_real", 0)
        else:
            v = item.get("cities", {}).get(cid, {}).get("realizado", 0)
        month_vals.append((lbl, v))

    max_v = max([v for _, v in month_vals] + [1])
    chart_lines = []
    for lbl, v in month_vals:
        bar = make_bar(v, max_v, 10)
        t_est = (v / base * 100) if base > 1 else 0
        t_est_str = f"{t_est:.2f}%".replace(".", ",")
        tag = ""
        if lbl.lower() == mes_foco.lower():
            tag = " 📍 *(Mês Consultado)*"
        elif v == max_v and len(month_vals) > 1:
            tag = " 🔴 (Pico)"
        chart_lines.append(f"• *{lbl}:* {format_number(v, 1)} `[{bar}]` {t_est_str}{tag}")

    # 2. Distribuição Voluntário vs Involuntário no Mês Consultado
    sum_tot = max(1, f_vol + f_inv) if (f_vol + f_inv) > 0 else f_real
    pct_vol = (f_vol / sum_tot) * 100 if sum_tot > 0 else 0
    pct_inv = (f_inv / sum_tot) * 100 if sum_tot > 0 else 0
    pct_vol_str = f"{pct_vol:.1f}%".replace(".", ",")
    pct_inv_str = f"{pct_inv:.1f}%".replace(".", ",")
    bar_vol = make_bar(f_vol, sum_tot, 12)
    bar_inv = make_bar(f_inv, sum_tot, 12)

    # 3. Ligações & Retenção URA (Call Center)
    cc = data.get("callcenter", {})
    atendidas = cc.get("atendidas", 0)
    unicas = cc.get("unicas", 0)
    ura = cc.get("ura", 0)
    mix_ura = cc.get("mix_ura", 0.0)
    taxa_os = cc.get("taxa_os", 0.0)
    os_geradas = cc.get("os_geradas", 0)

    # 4. Taxa por Motivo de Chamada
    motivos_matriz = data.get("motivos_matriz", [])
    cc_lines = []
    for m in motivos_matriz:
        mot = m.get("motivo") or m.get("id")
        mix = m.get("mix_pct", 0)
        ret = m.get("taxa_retencao_pct")
        os_cnt = m.get("os_geradas", 0)
        line = f"• *{mot}:* *{mix:.1f}%* das chamadas ({os_cnt} OS geradas"
        if ret is not None:
            line += f" | Retenção: *{ret:.1f}%*)"
        else:
            line += ")"
        cc_lines.append(line.replace(".", ","))

    # 5. Churn Safra D120 Snapshot da Praça
    safra_lines = []
    safra_city = data.get("safra_city")
    if safra_city:
        s_data = safra_city.get("data", {})
        s_target = "mai/26"
        st = s_data.get("safras", {}).get(s_target, {})
        s_inst = st.get("inst", 0)
        s_d120 = st.get("d120", 0)
        s_pct = (s_d120 / s_inst * 100) if s_inst > 0 else 0
        safra_lines.append(f"• *Safra Referência ({s_target.upper()}):* *{format_number(s_inst, 0)}* contratos instalados")
        safra_lines.append(f"• *Churn Safra D120:* *{s_pct:.2f}%* ({format_number(s_d120, 0)} desconexões)".replace(".", ","))
        top_p = s_data.get("top_parceiros", [])
        if top_p:
            p_strs = [f"_{p.get('nome')}_ ({p.get('inst')} inst)" for p in top_p[:3]]
            safra_lines.append(f"• *Principais Parceiros na Praça:* {', '.join(p_strs)}")

    msg = [
        f"📊 *ANÁLISE PROFUNDA & INSIGHTS — {nome.upper()} ({mes_foco.upper()})*",
        f"📍 *{seg}* · Base Ativa: *{format_number(base, 0)} clientes*",
        f"• *Volume Real:* *{format_number(f_real, 1)}* desconexões (Taxa: *{(f_real / base * 100):.2f}%*)".replace(".", ","),
    ]

    if mom_pct is not None or yoy_pct is not None:
        c_parts = []
        if mom_pct is not None:
            c_parts.append(f"*MoM:* {format_delta_badge(mom_pct)}")
        if yoy_pct is not None:
            c_parts.append(f"*YoY:* {format_delta_badge(yoy_pct)}")
        msg.append(f"• {' | '.join(c_parts)}")

    msg.extend([
        "",
        diag,
        "",
        f"📈 *1. Gráfico Histórico das Desconexões (Últimos Meses até {mes_foco}):*",
        "\n".join(chart_lines),
        "",
        f"⚖️ *2. Composição das Desconexões ({mes_foco}):*",
        f"• *Voluntário:*   {format_number(f_vol, 1)} ({pct_vol_str}) `[{bar_vol}]`",
        f"• *Involuntário:* {format_number(f_inv, 1)} ({pct_inv_str}) `[{bar_inv}]`",
        "",
        f"📞 *3. Ligações & Retenção URA (Call Center):*",
        f"• *Chamadas Atendidas:* {format_number(atendidas, 0)} | *Chamadas Únicas:* {format_number(unicas, 0)}",
        f"• *Retenção na URA:* {format_number(ura, 0)} chamadas (*Taxa URA: {mix_ura:.1f}%*)".replace(".", ","),
        f"• *Emissão de OS:* {format_number(os_geradas, 0)} ordens geradas (*Taxa Global de OS: {taxa_os:.1f}%*)".replace(".", ","),
    ])

    if cc_lines:
        msg.extend([
            "",
            f"📋 *4. Taxa por Motivo de Chamada (Mix & Retenção):*",
            "\n".join(cc_lines),
        ])

    if safra_lines:
        msg.extend([
            "",
            f"🌱 *5. Churn Safra D120 (Acompanhamento da Venda & Parceiros):*",
            "\n".join(safra_lines),
        ])

    msg.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "💬 _Deseja consultar outra cidade, safra ou parceiro? Digite ex: *#? Belém* ou *#? parceiro CCH Mendes*._"
    ])

    return "\n".join(msg)


def format_churn_safra_city_response(data: Dict[str, Any]) -> str:
    nome = data.get("nome", "Cidade")
    safra = data.get("safra", "mai/26")
    st = data.get("stats", {})
    inst = st.get("inst", 0)
    d120 = st.get("d120", 0)
    pct_d120 = (d120 / inst * 100) if inst > 0 else 0
    d30 = st.get("d30", 0)
    pct_d30 = (d30 / inst * 100) if inst > 0 else 0
    d90 = st.get("d90", 0)
    pct_d90 = (d90 / inst * 100) if inst > 0 else 0
    np120 = st.get("np120", 0)
    pct_np = (np120 / inst * 100) if inst > 0 else 0

    inad = st.get("inad", 0)
    opc = st.get("opc", 0)
    frd = st.get("frd", 0)
    tot_mot = max(1, inad + opc + frd)

    is_mad = safra in ["set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26"]
    status_label = "75% dos contratos maduros (Safra Oficial)" if safra == "mai/26" else ("Safra 100% madura" if is_mad else "Safra aberta / parcial")

    msg = [
        f"🌱 *CHURN SAFRA D120 — {nome.upper()} (SAFRA {safra.upper()})*",
        f"📍 Visão: *Assinatura* · Produto: *Dados (Banda Larga)*",
        f"• *Status:* {status_label}",
        "",
        "📊 *Indicadores Oficiais de Safra:*",
        f"  • *Instalações:* *{format_number(inst, 0)}* contratos",
        f"  • *Churn Safra D120:* *{pct_d120:.2f}%* ({format_number(d120, 0)} desconexões)".replace(".", ","),
        f"  • *Churn Precoce D30:* *{pct_d30:.2f}%* ({format_number(d30, 0)} desconexões)".replace(".", ","),
        f"  • *Churn D90:* *{pct_d90:.2f}%* ({format_number(d90, 0)} desconexões)".replace(".", ","),
        f"  • *Nunca Pagou D120:* *{pct_np:.2f}%* ({format_number(np120, 0)} contratos)".replace(".", ","),
        "",
        "⚖️ *Motivos no Churn D120:*",
        f"  • *Inadimplência:* {inad} ({inad/tot_mot*100:.1f}%)".replace(".", ","),
        f"  • *Opção / Concorrência:* {opc} ({opc/tot_mot*100:.1f}%)".replace(".", ","),
        f"  • *Fraude:* {frd} ({frd/tot_mot*100:.1f}%)".replace(".", ","),
    ]

    top_p = data.get("top_parceiros", [])
    if top_p:
        msg.append("")
        msg.append("🏢 *Principais Parceiros na Praça:*")
        for p in top_p[:4]:
            msg.append(f"  • *{p.get('nome')}:* {p.get('inst')} contratos instalados")

    history = data.get("history_safras", [])
    if history:
        msg.append("")
        msg.append(f"📈 *Evolução do Churn Safra D120 ({nome}):*")
        for h in history[-5:]:
            h_s = h["safra"]
            h_inst = h["inst"]
            h_pct = h["pct"]
            bar = make_bar(h_pct, 25.0, 8)
            msg.append(f"  • *{h_s}:* {h_inst} inst | *{h_pct:.2f}%* `[{bar}]`".replace(".", ","))

    msg.append("")
    msg.append(f"💡 _Deseja uma análise completa com gráficos e insights de {nome}? Digite *#?sim*_")
    return "\n".join(msg)


def format_churn_safra_partner_response(data: Dict[str, Any]) -> str:
    p_name = data.get("parceiro", "Parceiro")
    safras = data.get("safras", [])
    tot = data.get("total", {})

    msg = [
        f"🌱 *CHURN SAFRA D120 — PARCEIRO {p_name.upper()}*",
        f"📍 Canal de Venda Parceiro · Visão: Assinatura · Dados",
        f"• *Instalações Acumuladas:* *{format_number(tot.get('inst', 0), 0)}*",
        f"• *Churn D120 Médio:* *{tot.get('pct', 0):.2f}%* ({format_number(tot.get('d120', 0), 0)} desconexões)".replace(".", ","),
        "",
        "📈 *Evolução dos Últimos 6 Meses (Safras):*",
    ]

    max_pct = max([s.get("pct", 0) for s in safras] + [20.0])
    for s in safras:
        lbl = s.get("safra")
        inst = s.get("inst", 0)
        d120 = s.get("d120", 0)
        pct = s.get("pct", 0)
        bar = make_bar(pct, max_pct, 10)
        tag = ""
        if s.get("is_referencia"):
            tag = " 📍 *(Referência)*"
        elif not s.get("is_madura"):
            tag = " _(Parcial)_"
        msg.append(f"• *{lbl}:* {inst} inst | *{pct:.2f}%* `[{bar}]` ({d120} desc){tag}".replace(".", ","))

    top_c = data.get("top_cidades", [])
    if top_c:
        msg.append("")
        msg.append("🏙️ *Principais Praças de Venda do Parceiro:*")
        for c in top_c[:4]:
            msg.append(f"• *{c.get('cidade')}:* {c.get('inst')} contratos instalados")

    msg.append("")
    msg.append("💬 _Deseja consultar outro parceiro ou praça? Digite ex: *#? safra de Manaus* ou *#? Belém em mai/26*._")
    return "\n".join(msg)


def format_churn_safra_regional_response(data: Dict[str, Any]) -> str:
    safra = data.get("safra", "mai/26")
    st = data.get("stats", {})
    inst = st.get("inst", 0)
    d120 = st.get("d120", 0)
    pct_d120 = (d120 / inst * 100) if inst > 0 else 0
    d30 = st.get("d30", 0)
    pct_d30 = (d30 / inst * 100) if inst > 0 else 0
    d90 = st.get("d90", 0)
    pct_d90 = (d90 / inst * 100) if inst > 0 else 0
    np120 = st.get("np120", 0)
    pct_np = (np120 / inst * 100) if inst > 0 else 0

    msg = [
        f"🌱 *CHURN SAFRA D120 — REGIONAL NORTE (SAFRA {safra.upper()})*",
        f"📍 Visão: Assinatura · Dados (Banda Larga)",
        "",
        "📊 *Indicadores Oficiais:*",
        f"• *Instalações:* *{format_number(inst, 0)}* contratos",
        f"• *Churn Safra D120:* *{pct_d120:.2f}%* ({format_number(d120, 0)} desconexões)".replace(".", ","),
        f"• *Churn Precoce D30:* *{pct_d30:.2f}%* ({format_number(d30, 0)} desconexões)".replace(".", ","),
        f"• *Churn D90:* *{pct_d90:.2f}%* ({format_number(d90, 0)} desconexões)".replace(".", ","),
        f"• *Nunca Pagou D120:* *{pct_np:.2f}%* ({format_number(np120, 0)} contratos)".replace(".", ","),
    ]

    history = data.get("history_safras", [])
    if history:
        msg.append("")
        msg.append("📈 *Evolução Histórica Regional:*")
        for h in history[-6:]:
            h_s = h["safra"]
            h_inst = h["inst"]
            h_pct = h["pct"]
            bar = make_bar(h_pct, 20.0, 8)
            msg.append(f"• *{h_s}:* {format_number(h_inst, 0)} inst | *{h_pct:.2f}%* `[{bar}]`".replace(".", ","))

    return "\n".join(msg)

