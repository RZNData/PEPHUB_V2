# scripts/build_market_share_seeds.py
"""
Script analítico que extrai os dados oficiais e reais de:
1. public/market-share-movel/index.html (SMP - Pós-pago sem M2M e 5G)
2. public/market-share-residencial/index.html (SCM - Banda Larga Fixa Residencial com filtro estrito de 02.BL)
e gera o seed SQL agrupado em lotes de 30 rows por INSERT com IDs estritamente alfanuméricos.
"""

import json
import re
import uuid
import unicodedata

def clean_city_name(name: str) -> str:
    """Padroniza nome da cidade removendo prefixos como 'PA - ' e capitalizando."""
    if ' - ' in name:
        name = name.split(' - ', 1)[1]
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
    return name.strip().title()

def safe_id_str(val: str) -> str:
    """Garante string alfanumerica segura para compor IDs sem aspas ou caracteres especiais."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(val))

def main():
    print("[*] Carregando dados de Market Share Movel...")
    with open('public/market-share-movel/index.html', 'r', encoding='utf-8') as f:
        content_mov = f.read()

    m_mov = re.search(r'const DATA = (\{.*?\});', content_mov, re.DOTALL)
    if not m_mov:
        raise ValueError("Nao foi possivel encontrar DATA em market-share-movel/index.html")
    data_mov = json.loads(m_mov.group(1))

    print("[*] Carregando dados de Market Share Residencial...")
    with open('public/market-share-residencial/index.html', 'r', encoding='utf-8') as f:
        content_res = f.read()

    p_start = content_res.find('const PAYLOAD = ') + len('const PAYLOAD = ')
    brace_count = 0
    p_end = -1
    for i in range(p_start, len(content_res)):
        if content_res[i] == '{':
            brace_count += 1
        elif content_res[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                p_end = i + 1
                break

    if p_end == -1:
        raise ValueError("Nao foi possivel encontrar PAYLOAD em market-share-residencial/index.html")
    data_res = json.loads(content_res[p_start:p_end])

    mes_ref = "2026-08"
    raw_rows = []

    # =========================================================================
    # 1. MOVEL: REGIONAL NORTE CONSOLIDADA (POS-PAGO SEM M2M)
    # =========================================================================
    total_reg = next((x for x in data_mov.get('ddd_data', []) if x.get('key') == 'Total'), None)
    if total_reg:
        base = total_reg['base']
        share = total_reg['share']
        adds = total_reg['adds']
        ops = [
            ('Claro', base.get('CLARO', 0), share.get('CLARO', 0), adds.get('CLARO', 0)),
            ('Vivo', base.get('VIVO', 0), share.get('VIVO', 0), adds.get('VIVO', 0)),
            ('TIM', base.get('TIM', 0), share.get('TIM', 0), adds.get('TIM', 0)),
            ('Surf', base.get('SURF', 0), share.get('SURF', 0), adds.get('SURF', 0)),
            ('Competitivas/Outras', base.get('OUTROS', 0), share.get('OUTROS', 0), adds.get('OUTROS', 0))
        ]
        ops_sorted = sorted(ops, key=lambda x: x[1], reverse=True)
        for rank, (op, ac, sh, nt) in enumerate(ops_sorted, start=1):
            mid = f"mkt-rno-{rank}"
            raw_rows.append((mid, mes_ref, 'Regional Norte', 'RNO', 'TODOS', op, 'MOVEL', 'POS_PAGO_SEM_M2M', ac, round(sh, 2), nt, rank))

    # =========================================================================
    # 2. MOVEL: POR DDD (91 a 99) (POS-PAGO SEM M2M)
    # =========================================================================
    for item in data_mov.get('ddd_data', []):
        ddd = item.get('key')
        if ddd == 'Total':
            continue
        base = item['base']
        share = item['share']
        adds = item['adds']
        ops = [
            ('Claro', base.get('CLARO', 0), share.get('CLARO', 0), adds.get('CLARO', 0)),
            ('Vivo', base.get('VIVO', 0), share.get('VIVO', 0), adds.get('VIVO', 0)),
            ('TIM', base.get('TIM', 0), share.get('TIM', 0), adds.get('TIM', 0)),
            ('Surf', base.get('SURF', 0), share.get('SURF', 0), adds.get('SURF', 0)),
            ('Competitivas/Outras', base.get('OUTROS', 0), share.get('OUTROS', 0), adds.get('OUTROS', 0))
        ]
        ops_sorted = sorted(ops, key=lambda x: x[1], reverse=True)
        for rank, (op, ac, sh, nt) in enumerate(ops_sorted, start=1):
            mid = f"mkt-ddd{ddd}-{rank}"
            raw_rows.append((mid, mes_ref, f"DDD {ddd}", 'RNO', ddd, op, 'MOVEL', 'POS_PAGO_SEM_M2M', ac, round(sh, 2), nt, rank))

    # =========================================================================
    # 3. MOVEL: 5G (REGIONAL E POR DDD)
    # =========================================================================
    for item_5g in data_mov.get('data_5g', []):
        ddd = item_5g.get('ddd')
        pct_5g = item_5g.get('pct_5g', {})
        base_5g = item_5g.get('base_5g', {})
        tot_5g = base_5g.get('total', 1) or 1
        cid_label = 'Regional Norte' if ddd == 'Total' else f'DDD {ddd}'
        ddd_code = 'TODOS' if ddd == 'Total' else ddd
        ops = [
            ('Claro', base_5g.get('CLARO', 0), (base_5g.get('CLARO', 0) / tot_5g * 100)),
            ('Vivo', base_5g.get('VIVO', 0), (base_5g.get('VIVO', 0) / tot_5g * 100)),
            ('TIM', base_5g.get('TIM', 0), (base_5g.get('TIM', 0) / tot_5g * 100)),
        ]
        ops_sorted = sorted(ops, key=lambda x: x[1], reverse=True)
        for rank, (op, ac, sh) in enumerate(ops_sorted, start=1):
            mid = f"mkt-5g-{safe_id_str(ddd)}-{rank}"
            raw_rows.append((mid, mes_ref, cid_label, 'RNO', ddd_code, op, 'MOVEL', '5G', ac, round(sh, 2), 0, rank))

    # =========================================================================
    # 4. MOVEL: POR CIDADE (TODAS AS CIDADES) (POS-PAGO SEM M2M)
    # =========================================================================
    accents_map = {
        'Belem': 'Belém',
        'Sao Luis': 'São Luís',
        'Macapa': 'Macapá',
        'Santarem': 'Santarém',
        'Maraba': 'Marabá',
        'Acailandia': 'Açailândia',
        'Barcarena': 'Barcarena',
        'Paragominas': 'Paragominas',
        'Castanhal': 'Castanhal',
        'Ananindeua': 'Ananindeua',
        'Imperatriz': 'Imperatriz',
        'Boa Vista': 'Boa Vista'
    }

    cidades_mov = data_mov.get('cities_data', [])
    for c_obj in cidades_mov:
        raw_cid = c_obj.get('cidade', '')
        uf = raw_cid.split(' - ')[0] if ' - ' in raw_cid else 'PA'
        cid_clean = clean_city_name(raw_cid)
        cid_display = accents_map.get(cid_clean, cid_clean)

        base = c_obj.get('base', {})
        share = c_obj.get('share', {})
        adds = c_obj.get('adds', {})

        ops = [
            ('Claro', base.get('CLARO', 0), share.get('CLARO', 0), adds.get('CLARO', 0)),
            ('Vivo', base.get('VIVO', 0), share.get('VIVO', 0), adds.get('VIVO', 0)),
            ('TIM', base.get('TIM', 0), share.get('TIM', 0), adds.get('TIM', 0)),
            ('Surf', base.get('SURF', 0), share.get('SURF', 0), adds.get('SURF', 0)),
            ('Competitivas/Outras', base.get('OUTROS', 0), share.get('OUTROS', 0), adds.get('OUTROS', 0))
        ]
        ops_sorted = sorted(ops, key=lambda x: x[1], reverse=True)
        safe_prefix = safe_id_str(cid_clean)[:6]
        for rank, (op, ac, sh, nt) in enumerate(ops_sorted, start=1):
            if ac == 0 and nt == 0 and sh == 0:
                continue
            mid = f"mkt-m-{safe_id_str(uf)}-{safe_prefix}-{rank}-{uuid.uuid4().hex[:4]}"
            raw_rows.append((mid, mes_ref, cid_display, uf, 'TODOS', op, 'MOVEL', 'POS_PAGO_SEM_M2M', ac, round(sh, 2), nt, rank))

    # =========================================================================
    # 5. BANDA LARGA RESIDENCIAL (SCM): FILTRO ESTRITO 02.BL (BANDA LARGA)
    # =========================================================================
    dicts_res = data_res.get('dicts', {})
    rows_res = data_res.get('rows', [])
    cidades_res = dicts_res.get('cidade', [])
    grupos_res = dicts_res.get('grupo', [])
    empresas_res = dicts_res.get('empresa', [])
    ufs_res = dicts_res.get('uf', [])
    ddds_res = dicts_res.get('ddd', [])

    bl_idx = dicts_res.get('servico', []).index('02.BL') if '02.BL' in dicts_res.get('servico', []) else -1
    if bl_idx == -1:
        raise ValueError("Servico 02.BL nao encontrado em market-share-residencial")

    claro_grp_id = next((i for i, g in enumerate(grupos_res) if g.upper() == 'CLARO'), -1)

    cidade_agg = {}
    reg_agg = {}
    ddd_agg = {}

    # DIM_COL_IDX: cidade:0, grupo:1, empresa:2, ddd:3, uf:4, servico:5, ...
    for r in rows_res:
        # Filtro Mandatório: Somente Banda Larga Fixa (02.BL), eliminando TV e Telefonia Fixa
        if r[5] != bl_idx:
            continue

        cid_id = r[0]
        grp_id = r[1]
        emp_id = r[2]
        ddd_id = r[3]
        uf_id = r[4]
        m = r[11]
        v_ago26 = m[13]
        v_jul26 = m[12]
        net = v_ago26 - v_jul26

        grp_name = grupos_res[grp_id]
        emp_name = empresas_res[emp_id]

        if grp_id == claro_grp_id or emp_name.upper().startswith('CLARO'):
            canonical_grp = 'Claro'
        elif grp_name.upper() == 'OI':
            canonical_grp = 'Oi'
        elif grp_name.upper() == 'VIVO':
            canonical_grp = 'Vivo'
        elif grp_name.upper() == 'TIM':
            canonical_grp = 'TIM'
        elif 'SKY' in grp_name.upper() or 'WERTHEIN' in grp_name.upper():
            canonical_grp = 'Sky'
        else:
            canonical_grp = 'Competitivas/ISPs'

        if canonical_grp not in reg_agg:
            reg_agg[canonical_grp] = {'base': 0, 'net': 0}
        reg_agg[canonical_grp]['base'] += v_ago26
        reg_agg[canonical_grp]['net'] += net

        if cid_id not in cidade_agg:
            cidade_agg[cid_id] = {'uf': ufs_res[uf_id], 'ddd': ddds_res[ddd_id], 'grupos': {}}
        if canonical_grp not in cidade_agg[cid_id]['grupos']:
            cidade_agg[cid_id]['grupos'][canonical_grp] = {'base': 0, 'net': 0}
        cidade_agg[cid_id]['grupos'][canonical_grp]['base'] += v_ago26
        cidade_agg[cid_id]['grupos'][canonical_grp]['net'] += net

        ddd_val = ddds_res[ddd_id]
        if ddd_val not in ddd_agg:
            ddd_agg[ddd_val] = {}
        if canonical_grp not in ddd_agg[ddd_val]:
            ddd_agg[ddd_val][canonical_grp] = {'base': 0, 'net': 0}
        ddd_agg[ddd_val][canonical_grp]['base'] += v_ago26
        ddd_agg[ddd_val][canonical_grp]['net'] += net

    # Regional Norte Banda Larga (02.BL)
    tot_reg_bl = sum(x['base'] for x in reg_agg.values()) or 1
    ops_bl_sorted = sorted(reg_agg.items(), key=lambda x: x[1]['base'], reverse=True)
    for rank, (op, stats) in enumerate(ops_bl_sorted, start=1):
        ac = stats['base']
        nt = stats['net']
        sh = (ac / tot_reg_bl * 100)
        mid = f"mkt-bl-rno-{rank}"
        raw_rows.append((mid, mes_ref, 'Regional Norte', 'RNO', 'TODOS', op, 'BANDA_LARGA', 'RESIDENCIAL', ac, round(sh, 2), nt, rank))

    # DDD Banda Larga (02.BL)
    for ddd_val, grps in ddd_agg.items():
        tot_ddd_bl = sum(x['base'] for x in grps.values()) or 1
        grps_sorted = sorted(grps.items(), key=lambda x: x[1]['base'], reverse=True)
        for rank, (op, stats) in enumerate(grps_sorted, start=1):
            ac = stats['base']
            nt = stats['net']
            sh = (ac / tot_ddd_bl * 100)
            mid = f"mkt-bl-ddd{safe_id_str(ddd_val)}-{rank}"
            raw_rows.append((mid, mes_ref, f"DDD {ddd_val}", 'RNO', ddd_val, op, 'BANDA_LARGA', 'RESIDENCIAL', ac, round(sh, 2), nt, rank))

    # Cidades Banda Larga (02.BL)
    for cid_id, info in cidade_agg.items():
        raw_cid_name = cidades_res[cid_id]
        cid_clean = clean_city_name(raw_cid_name)
        cid_display = accents_map.get(cid_clean, cid_clean)
        uf = info['uf']
        ddd = info['ddd']
        grps = info['grupos']
        tot_cid_bl = sum(x['base'] for x in grps.values()) or 1

        grps_sorted = sorted(grps.items(), key=lambda x: x[1]['base'], reverse=True)
        safe_prefix = safe_id_str(cid_clean)[:6]
        for rank, (op, stats) in enumerate(grps_sorted, start=1):
            ac = stats['base']
            nt = stats['net']
            sh = (ac / tot_cid_bl * 100)
            mid = f"mkt-bl-{safe_id_str(uf)}-{safe_prefix}-{rank}-{uuid.uuid4().hex[:4]}"
            raw_rows.append((mid, mes_ref, cid_display, uf, ddd, op, 'BANDA_LARGA', 'RESIDENCIAL', ac, round(sh, 2), nt, rank))

    print(f"[*] Total de linhas geradas: {len(raw_rows)}")

    # Gera comandos SQL em lotes de 30 rows por INSERT
    BATCH_SIZE = 30
    sql_chunks = ["DELETE FROM fato_market_share;"]

    for i in range(0, len(raw_rows), BATCH_SIZE):
        batch = raw_rows[i:i + BATCH_SIZE]
        val_strs = []
        for r in batch:
            id_esc = str(r[0]).replace("'", "''")
            cidade_esc = str(r[2]).replace("'", "''")
            op_esc = str(r[5]).replace("'", "''")
            val_strs.append(
                f"('{id_esc}', '{r[1]}', '{cidade_esc}', '{r[3]}', '{r[4]}', '{op_esc}', '{r[6]}', '{r[7]}', {r[8]}, {r[9]}, {r[10]}, {r[11]})"
            )
        stmt = "INSERT INTO fato_market_share (id, mes_referencia, cidade, uf, ddd, operadora, produto, segmento, acessos, market_share_pct, net_adds, posicao_ranking) VALUES " + ",\n".join(val_strs) + ";"
        sql_chunks.append(stmt)

    with open('seed_market_share_batches.sql', 'w', encoding='utf-8') as f:
        f.write("\n\n".join(sql_chunks) + "\n")

    print(f"[OK] Gerado 'seed_market_share_batches.sql' com {len(sql_chunks)} statements agrupados e IDs seguros.")

if __name__ == '__main__':
    main()
