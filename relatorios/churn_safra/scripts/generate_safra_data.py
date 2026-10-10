"""
Gera o arquivo consolidado 'safra_data.json' a partir do payload contido em 'Painel_Churn_Safra 28.html'.
Permite que o bot consulte instantaneamente qualquer informação de Churn Safra D120,
por cidade, safra, parceiro ou vendedor, sem precisar carregar 5MB de HTML em cada mensagem.
"""

import json
import zlib
import base64
import struct
import os
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(ROOT_DIR, "Painel_Churn_Safra 28.html")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safra_data.json")


def generate():
    t0 = time.time()
    print("Iniciando extração do Painel_Churn_Safra 28.html...")

    if not os.path.exists(HTML_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {HTML_PATH}")

    with open(HTML_PATH, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    idx = text.find("const PAYLOAD =")
    if idx == -1:
        raise ValueError("const PAYLOAD não encontrado no HTML!")

    content = text[idx + len("const PAYLOAD ="):].lstrip()
    dec = json.JSONDecoder()
    payload, _ = dec.raw_decode(content)
    cols = payload["cols"]

    def decode_col(k):
        info = cols[k]
        raw = zlib.decompress(base64.b64decode(info["b"]))
        t = info["t"]
        if t == "u8":
            return list(raw)
        elif t == "u16":
            return list(struct.unpack(f"{len(raw)//2}H", raw))
        elif t == "u32":
            return list(struct.unpack(f"{len(raw)//4}I", raw))

    safra_col = decode_col("safra")
    cidade_col = decode_col("cidade")
    parceiro_col = decode_col("parceiro")
    vendedor_col = decode_col("vendedor")
    abk_col = decode_col("abk")
    pbk_col = decode_col("pbk")
    tpk_col = decode_col("tpk")
    visao_col = decode_col("visao")
    produto_col = decode_col("produto")

    dicts = payload["dicts"]
    safras = dicts["safra"]
    cidades = dicts["cidade"]
    parceiros = dicts["parceiro"]
    vendedores = dicts["vendedor"]

    safra_order = [
        "set/25", "out/25", "nov/25", "dez/25",
        "jan/26", "fev/26", "mar/26", "abr/26",
        "mai/26", "jun/26", "jul/26", "ago/26", "set/26"
    ]

    def empty_stats():
        return {"inst": 0, "d120": 0, "d30": 0, "d90": 0, "np120": 0, "npc": 0, "inad": 0, "opc": 0, "frd": 0}

    regional = {s: empty_stats() for s in safra_order}
    cidades_map = {c: {s: empty_stats() for s in safra_order} for c in cidades}
    parceiros_map = {p: {s: empty_stats() for s in safra_order} for p in parceiros}

    # Tracking de relacionamento para Top Parceiros/Vendedores
    cidade_parceiros = {c: {} for c in cidades}
    cidade_vendedores = {c: {} for c in cidades}
    parceiro_cidades = {p: {} for p in parceiros}

    total_rows = len(safra_col)
    for r in range(total_rows):
        # Filtro padrão corporativo: Visão = Assinatura (0), Produto = Dados / Banda Larga (0)
        if visao_col[r] != 0:
            continue
        if produto_col[r] != 0:
            continue

        s_label = safras[safra_col[r]]
        c_name = cidades[cidade_col[r]]
        p_name = parceiros[parceiro_col[r]]
        v_name = vendedores[vendedor_col[r]]

        a = abk_col[r]
        p = pbk_col[r]
        t = tpk_col[r]

        is_d120 = (a > 0 and a <= 4)
        is_np = (p == 0 or p > 4)
        is_npc = (is_d120 and is_np)

        for bucket in [regional[s_label], cidades_map[c_name][s_label], parceiros_map[p_name][s_label]]:
            bucket["inst"] += 1
            if is_d120:
                bucket["d120"] += 1
                if t == 1:
                    bucket["inad"] += 1
                elif t == 2:
                    bucket["opc"] += 1
                elif t == 3:
                    bucket["frd"] += 1
            if a == 1:
                bucket["d30"] += 1
            if a > 0 and a <= 3:
                bucket["d90"] += 1
            if is_np:
                bucket["np120"] += 1
            if is_npc:
                bucket["npc"] += 1

        # Relações
        cidade_parceiros[c_name][p_name] = cidade_parceiros[c_name].get(p_name, 0) + 1
        cidade_vendedores[c_name][v_name] = cidade_vendedores[c_name].get(v_name, 0) + 1
        parceiro_cidades[p_name][c_name] = parceiro_cidades[p_name].get(c_name, 0) + 1

    # Formatar Top 5 para cidades e parceiros
    cidades_final = {}
    for c, s_data in cidades_map.items():
        tot_inst = sum(s["inst"] for s in s_data.values())
        if tot_inst == 0:
            continue
        tot_d120 = sum(s["d120"] for s in s_data.values())
        # Top parceiros na cidade
        top_p = sorted(cidade_parceiros[c].items(), key=lambda x: x[1], reverse=True)[:5]
        # Top vendedores na cidade
        top_v = sorted(cidade_vendedores[c].items(), key=lambda x: x[1], reverse=True)[:5]

        cidades_final[c] = {
            "safras": s_data,
            "total": {"inst": tot_inst, "d120": tot_d120, "pct": round(tot_d120 / tot_inst * 100, 2)},
            "top_parceiros": [{"nome": p, "inst": cnt} for p, cnt in top_p],
            "top_vendedores": [{"nome": v, "inst": cnt} for v, cnt in top_v if v != "NÃO INFORMADO"]
        }

    parceiros_final = {}
    for p, s_data in parceiros_map.items():
        tot_inst = sum(s["inst"] for s in s_data.values())
        if tot_inst < 5:
            continue
        tot_d120 = sum(s["d120"] for s in s_data.values())
        top_c = sorted(parceiro_cidades[p].items(), key=lambda x: x[1], reverse=True)[:5]

        parceiros_final[p] = {
            "safras": s_data,
            "total": {"inst": tot_inst, "d120": tot_d120, "pct": round(tot_d120 / tot_inst * 100, 2)},
            "top_cidades": [{"cidade": c, "inst": cnt} for c, cnt in top_c]
        }

    out = {
        "metadata": {
            "data_posicao": "20/09/2026",
            "visao": "Assinatura",
            "produto": "Dados (Banda Larga)",
            "safra_referencia_madura": "mai/26",
            "total_linhas": total_rows
        },
        "safra_order": safra_order,
        "regional": regional,
        "cidades": cidades_final,
        "parceiros": parceiros_final
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"safra_data.json gerado com sucesso em {time.time() - t0:.2f}s!")
    print(f"Cidades com dados: {len(cidades_final)}")
    print(f"Parceiros ativos: {len(parceiros_final)}")
    print(f"Tamanho do arquivo: {round(os.path.getsize(OUTPUT_PATH) / 1024, 1)} KB")


if __name__ == "__main__":
    generate()
