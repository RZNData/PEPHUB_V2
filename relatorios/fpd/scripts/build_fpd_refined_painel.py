import csv
import json
import zlib
import base64
import os
import re
import math

print("=== GERANDO PAINEL REFINADO DE FPD - VERSÃO COMPLETA (6 ITENS ATENDIDOS) ===")

# Centroides urbanos das 13 cidades da Regional Norte
centroides_cidade = {
    'MANAUS': (-3.1190, -60.0217, 0.045),
    'BELEM': (-1.4558, -48.4902, 0.035),
    'BELÉM': (-1.4558, -48.4902, 0.035),
    'SAO LUIS': (-2.5387, -44.2825, 0.035),
    'SÃO LUÍS': (-2.5387, -44.2825, 0.035),
    'IMPERATRIZ': (-5.5266, -47.4797, 0.025),
    'MACAPA': (0.0389, -51.0694, 0.025),
    'MACAPÁ': (0.0389, -51.0694, 0.025),
    'PARAUAPEBAS': (-6.0684, -49.9048, 0.030),
    'CASTANHAL': (-1.2970, -47.9250, 0.020),
    'ANANINDEUA': (-1.3656, -48.3725, 0.025),
    'SANTANA': (-0.0583, -51.1817, 0.015),
    'MARABA': (-5.3686, -49.1178, 0.025),
    'MARABÁ': (-5.3686, -49.1178, 0.025),
    'PARAGOMINAS': (-2.9972, -47.3533, 0.020),
    'CAXIAS': (-4.8589, -43.3561, 0.020),
    'TIMON': (-5.0939, -42.8361, 0.020)
}

def pseudo_jitter(key, scale):
    h = (hash(str(key)) ^ 0x5bf03635) & 0xffffffff
    h1 = (h & 0xffff) / 65535.0
    h2 = ((h >> 16) & 0xffff) / 65535.0
    angle = h1 * 2 * math.pi
    radius = (h2 ** 0.5) * scale
    return radius * math.cos(angle), radius * math.sin(angle)

# 1. Carregar Geocod
print("1. Indexando Georreferenciamento...")
geocod = {}
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name.strip().upper(): i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO', 14)
    b_idx = h_idx.get('BAIRRO', 34)
    n_idx = h_idx.get('CD_NODE', 13)
    lat_idx = h_idx.get('LAT_FINAL(FALLBACK_2)', 68)
    lon_idx = h_idx.get('LONG_FINAL(FALLBACK_2)', 69)
    porte_idx = h_idx.get('IBGE.TIPO', 7)
    cabo_idx = h_idx.get('IBGE.TIPO_CIDADE', 6)
    ddd_idx = h_idx.get('IBGE.NR_DDD', 5)

    for row in r:
        ctr = row[c_idx].strip() if c_idx < len(row) else ''
        if ctr and ctr not in geocod:
            geocod[ctr] = {
                'b': row[b_idx].strip() if b_idx < len(row) else 'Não Informado',
                'n': row[n_idx].strip() if n_idx < len(row) else 'Não Informado',
                'lat': row[lat_idx].strip() if lat_idx < len(row) else '',
                'lon': row[lon_idx].strip() if lon_idx < len(row) else '',
                'porte': row[porte_idx].strip() if porte_idx < len(row) else 'Demais Mercados',
                'cabo': row[cabo_idx].strip() if cabo_idx < len(row) else 'Com Cabo',
                'ddd': row[ddd_idx].strip() if ddd_idx < len(row) else ''
            }

print(f"Lookup Geocod carregado: {len(geocod):,} contratos.")

# 2. Estrutura de Dicionários e Colunas
print("\n2. Processando FPD_JAN_MAI_26.csv...")
dicts = {
    'safra': [], 'uf': [], 'tipo_cidade': [], 'porte': [], 'ddd': [],
    'canal_grupo': [], 'canal_sub': [], 'produto': [], 'marca': [],
    'perfil': [], 'risco_nv': [], 'score': [], 'portfolio_tv': [],
    'pagto': [], 'visao': [], 'motivo': [],
    'ger_negocio': [], 'ger_canal': [], 'tipo_canal': [], 'key_account': [],
    'coordenador': [], 'ger_filial': [], 'executivo': [],
    'cidade': [], 'bairro': [], 'node': [], 'parceiro': [],
    'empresa': [], 'vendedor': []
}

dict_indices = {k: {} for k in dicts}

def get_code(dim, val):
    v = str(val).strip() if val else "Não Informado"
    if not v: v = "Não Informado"
    if v not in dict_indices[dim]:
        idx = len(dicts[dim])
        dicts[dim].append(v)
        dict_indices[dim][v] = idx
        return idx
    return dict_indices[dim][v]

cols_data = {
    'safra': [], 'uf': [], 'tipo_cidade': [], 'porte': [], 'ddd': [],
    'canal_grupo': [], 'canal_sub': [], 'produto': [], 'marca': [],
    'perfil': [], 'risco_nv': [], 'score': [], 'portfolio_tv': [],
    'pagto': [], 'visao': [], 'motivo': [],
    'ger_negocio': [], 'ger_canal': [], 'tipo_canal': [], 'key_account': [],
    'coordenador': [], 'ger_filial': [], 'executivo': [],
    'cidade': [], 'bairro': [], 'node': [], 'parceiro': [],
    'empresa': [], 'vendedor': [],
    'abk': [], 'pbk': [], 'tpk': [], 'dinst': [], 'aging': [], 'ctr': [],
    'ag30': [], 'ag60': []
}

lats, lons = [], []

safra_nome = {
    '202601': 'jan/26', '202602': 'fev/26', '202603': 'mar/26',
    '202604': 'abr/26', '202605': 'mai/26'
}

ddd_por_cidade = {
    'MANAUS': '92', 'BELEM': '91', 'BELÉM': '91', 'SAO LUIS': '98', 'SÃO LUÍS': '98',
    'MACAPA': '96', 'MACAPÁ': '96', 'IMPERATRIZ': '99', 'CASTANHAL': '91',
    'PARAUAPEBAS': '94', 'MARABA': '94', 'MARABÁ': '94', 'ANANINDEUA': '91',
    'SANTANA': '96', 'BOA VISTA': '95', 'ABAETETUBA': '91', 'BARCARENA': '91',
    'TIMON': '99', 'SANTA INES': '99', 'CAXIAS': '99', 'ITAITUBA': '93', 'PARAGOMINAS': '91'
}

porte_por_cidade = {
    'MANAUS': 'Grandes', 'BELEM': 'Grandes', 'BELÉM': 'Grandes', 'SAO LUIS': 'Grandes', 'SÃO LUÍS': 'Grandes',
    'IMPERATRIZ': 'Desenvolvimento', 'MACAPA': 'Desenvolvimento', 'MACAPÁ': 'Desenvolvimento',
    'ANANINDEUA': 'Desenvolvimento', 'MARABA': 'Desenvolvimento', 'MARABÁ': 'Desenvolvimento',
    'PARAUAPEBAS': 'Desenvolvimento', 'CASTANHAL': 'Desenvolvimento', 'SANTANA': 'Demais Mercados',
    'PARAGOMINAS': 'Demais Mercados', 'CAXIAS': 'Demais Mercados', 'TIMON': 'Demais Mercados'
}

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h)}

    idx_safra = h_idx.get('SAFRA')
    idx_ctr = h_idx.get('NR_CONTRATO')
    idx_dt_inst = h_idx.get('DT_INI_CONTRATO')
    idx_cid = h_idx.get('NM_CIDADE')
    idx_uf = h_idx.get('UF')
    idx_canal_g = h_idx.get('NM_CANAL_VENDA_GRUPO')
    idx_canal_s = h_idx.get('NM_CANAL_VENDA_SUBGRUPO')
    idx_parc = h_idx.get('NM_PARCEIRO')
    idx_vend = h_idx.get('NM_VENDEDOR')
    idx_prod = h_idx.get('NM_TIPO_ASS_DOMICILIO')
    if idx_prod is None: idx_prod = h_idx.get('PRODUTO_ATUAL')
    idx_marca = h_idx.get('NM_MARCA')
    idx_risco = h_idx.get('FXRISCO')
    idx_risco_nv = h_idx.get('FX_RISCO_NV')
    idx_score = h_idx.get('FXULTSCORE')
    idx_tv = h_idx.get('PORTFOLIO_TV')
    idx_pag = h_idx.get('NM_FORMA_PAGAMENTO')
    idx_ag30 = h_idx.get('AGING30')
    idx_ag60 = h_idx.get('AGING60')

    count = 0
    nodes_found = 0
    for row in r:
        if not row or not any(row): continue
        count += 1

        sf_raw = row[idx_safra].strip() if idx_safra < len(row) else ''
        safra_str = safra_nome.get(sf_raw, sf_raw)
        ctr_str = row[idx_ctr].strip() if idx_ctr < len(row) else ''
        try: ctr_num = int(ctr_str)
        except: ctr_num = count

        cid_str = row[idx_cid].strip() if idx_cid < len(row) else ''
        cid_upper = cid_str.upper()
        uf_str = row[idx_uf].strip().upper() if idx_uf < len(row) else 'PA'

        geo_info = geocod.get(ctr_str, {})
        bairro_str = geo_info.get('b', 'Não Informado')
        node_str = geo_info.get('n', 'Não Informado')
        if node_str and node_str != 'Não Informado':
            nodes_found += 1
        cabo_str = geo_info.get('cabo', 'Com Cabo')
        porte_str = geo_info.get('porte') or porte_por_cidade.get(cid_upper, 'Demais Mercados')
        ddd_str = geo_info.get('ddd') or ddd_por_cidade.get(cid_upper, '91')

        canal_g_str = row[idx_canal_g].strip() if idx_canal_g < len(row) else 'Não Informado'
        canal_s_str = row[idx_canal_s].strip() if idx_canal_s < len(row) else 'Não Informado'
        parc_str = row[idx_parc].strip() if idx_parc < len(row) else 'Não Informado'
        vend_str = row[idx_vend].strip() if idx_vend < len(row) else 'Não Informado'
        prod_str = row[idx_prod].strip() if idx_prod < len(row) else 'Dados'
        marca_str = row[idx_marca].strip() if idx_marca < len(row) else 'Claro'
        pag_str = row[idx_pag].strip() if idx_pag < len(row) else 'Boleto'
        risco_str = row[idx_risco].strip() if idx_risco < len(row) else 'Médio'
        if not risco_str or risco_str == '.': risco_str = 'Médio'

        risco_nv_str = row[idx_risco_nv].strip() if (idx_risco_nv is not None and idx_risco_nv < len(row)) else risco_str
        if not risco_nv_str: risco_nv_str = 'Não Informado'
        
        score_str = row[idx_score].strip() if (idx_score is not None and idx_score < len(row)) else 'Não Informado'
        if not score_str: score_str = 'Não Informado'
        
        tv_str = row[idx_tv].strip() if (idx_tv is not None and idx_tv < len(row)) else 'SEM TV'
        if not tv_str: tv_str = 'SEM TV'

        a30 = 1 if (idx_ag30 < len(row) and row[idx_ag30] == '1') else 0
        a60 = 1 if (idx_ag60 < len(row) and row[idx_ag60] == '1') else 0

        if a60: abk = 2
        elif a30: abk = 1
        else: abk = 0

        if a30 and a60: pbk = 0
        else: pbk = 1

        if 'Alt' in risco_nv_str or 'Alto' in risco_nv_str or '0 e 1' in risco_nv_str: tpk = 1
        elif 'Medio' in risco_nv_str or 'Médio' in risco_nv_str: tpk = 2
        else: tpk = 3

        dt_str = row[idx_dt_inst].strip() if idx_dt_inst < len(row) else ''
        dia_inst = 1
        if dt_str and '/' in dt_str:
            try:
                dia_inst = int(dt_str.split('/')[0])
                if dia_inst < 1 or dia_inst > 31: dia_inst = 1
            except: dia_inst = 1

        aging_val = 60 if a60 else (30 if a30 else 0)

        # Qualificação de Coordenadas Inteligente
        lat_s = geo_info.get('lat')
        lon_s = geo_info.get('lon')
        if lat_s and lon_s:
            try:
                base_lat = float(lat_s.replace(',', '.'))
                base_lon = float(lon_s.replace(',', '.'))
                dlat, dlon = pseudo_jitter(ctr_num, 0.00035)
                lat_f = base_lat + dlat
                lon_f = base_lon + dlon
            except:
                c_lat, c_lon, c_rad = centroides_cidade.get(cid_upper, (-3.1190, -60.0217, 0.03))
                dlat, dlon = pseudo_jitter(ctr_num, c_rad)
                lat_f, lon_f = c_lat + dlat, c_lon + dlon
        else:
            c_lat, c_lon, c_rad = centroides_cidade.get(cid_upper, (-3.1190, -60.0217, 0.03))
            dlat, dlon = pseudo_jitter(ctr_num, c_rad)
            lat_f, lon_f = c_lat + dlat, c_lon + dlon

        lats.append(lat_f)
        lons.append(lon_f)

        cols_data['safra'].append(get_code('safra', safra_str))
        cols_data['uf'].append(get_code('uf', uf_str))
        cols_data['tipo_cidade'].append(get_code('tipo_cidade', cabo_str))
        cols_data['porte'].append(get_code('porte', porte_str))
        cols_data['ddd'].append(get_code('ddd', ddd_str))
        cols_data['canal_grupo'].append(get_code('canal_grupo', canal_g_str))
        cols_data['canal_sub'].append(get_code('canal_sub', canal_s_str))
        cols_data['produto'].append(get_code('produto', prod_str))
        cols_data['marca'].append(get_code('marca', marca_str))
        cols_data['perfil'].append(get_code('perfil', risco_str))
        cols_data['risco_nv'].append(get_code('risco_nv', risco_nv_str))
        cols_data['score'].append(get_code('score', score_str))
        cols_data['portfolio_tv'].append(get_code('portfolio_tv', tv_str))
        cols_data['pagto'].append(get_code('pagto', pag_str))
        cols_data['visao'].append(get_code('visao', 'Domicílio'))
        cols_data['motivo'].append(get_code('motivo', 'Inadimplência FPD 60' if a60 else ('Atraso Pró-rata 30d' if a30 else 'Adimplente')))

        cols_data['ger_negocio'].append(get_code('ger_negocio', 'Sem Carteira'))
        cols_data['ger_canal'].append(get_code('ger_canal', canal_g_str))
        cols_data['tipo_canal'].append(get_code('tipo_canal', 'INDIRETO' if 'Indireto' in canal_s_str else 'DIRETO'))
        cols_data['key_account'].append(get_code('key_account', 'Sem Carteira'))
        cols_data['coordenador'].append(get_code('coordenador', 'Sem Carteira'))
        cols_data['ger_filial'].append(get_code('ger_filial', 'Sem Carteira'))
        cols_data['executivo'].append(get_code('executivo', 'Sem Carteira'))

        cols_data['cidade'].append(get_code('cidade', cid_upper.title()))
        cols_data['bairro'].append(get_code('bairro', bairro_str))
        cols_data['node'].append(get_code('node', node_str))
        cols_data['parceiro'].append(get_code('parceiro', parc_str))
        cols_data['empresa'].append(get_code('empresa', parc_str))
        cols_data['vendedor'].append(get_code('vendedor', vend_str))

        cols_data['abk'].append(abk)
        cols_data['pbk'].append(pbk)
        cols_data['tpk'].append(tpk)
        cols_data['dinst'].append(dia_inst)
        cols_data['aging'].append(aging_val)
        cols_data['ctr'].append(ctr_num)
        cols_data['ag30'].append(a30)
        cols_data['ag60'].append(a60)

print(f"Total: {count:,} contratos processados. Nodes identificados: {nodes_found:,} ({nodes_found/count*100:.1f}%).")

# BBOX
min_lat, max_lat = min(lats), max(lats)
min_lon, max_lon = min(lons), max(lons)
bbox = [min_lat, max_lat, min_lon, max_lon]
lat_d = max_lat - min_lat if max_lat > min_lat else 1.0
lon_d = max_lon - min_lon if max_lon > min_lon else 1.0

gx = [int(round((lon - min_lon) / lon_d * 65534)) for lon in lons]
gy = [int(round((lat - min_lat) / lat_d * 65534)) for lat in lats]

# Centroides Bairros
bairro_pts = {}
for i in range(count):
    b_idx_val = cols_data['bairro'][i]
    if b_idx_val not in bairro_pts: bairro_pts[b_idx_val] = []
    if len(bairro_pts[b_idx_val]) < 100: bairro_pts[b_idx_val].append((gx[i], gy[i]))

nb_bairros = len(dicts['bairro'])
bmx, bmy, bmn = [0] * nb_bairros, [0] * nb_bairros, [0] * nb_bairros
for b_idx_val, pts in bairro_pts.items():
    if b_idx_val < nb_bairros:
        bmx[b_idx_val] = int(round(sum(p[0] for p in pts) / len(pts)))
        bmy[b_idx_val] = int(round(sum(p[1] for p in pts) / len(pts)))
        bmn[b_idx_val] = min(len(pts), 255)

# Compressão
def pack_and_compress(arr, dtype):
    if dtype == 'u8': raw_bytes = bytearray(arr)
    elif dtype == 'u16':
        raw_bytes = bytearray()
        for v in arr: raw_bytes.extend(int(v).to_bytes(2, byteorder='little', signed=False))
    elif dtype == 'u32':
        raw_bytes = bytearray()
        for v in arr: raw_bytes.extend(int(v).to_bytes(4, byteorder='little', signed=False))
    comp = zlib.compress(raw_bytes, level=9)
    return {'t': dtype, 'b': base64.b64encode(comp).decode('ascii')}

compressed_cols = {}
for k, arr in cols_data.items():
    if k in ['cidade', 'bairro', 'node', 'parceiro', 'empresa', 'vendedor', 'canal_sub', 'produto', 'score']:
        dtype = 'u16'
    elif k == 'ctr':
        dtype = 'u32'
    else:
        dtype = 'u8'
    compressed_cols[k] = pack_and_compress(arr, dtype)

compressed_cols['gx'] = pack_and_compress(gx, 'u16')
compressed_cols['gy'] = pack_and_compress(gy, 'u16')
compressed_cols['bmx'] = pack_and_compress(bmx, 'u16')
compressed_cols['bmy'] = pack_and_compress(bmy, 'u16')
compressed_cols['bmn'] = pack_and_compress(bmn, 'u8')

payload = {
    'n': count,
    'nb': nb_bairros,
    'dicts': dicts,
    'bbox': bbox,
    'cols': compressed_cols
}
payload_json_str = json.dumps(payload, ensure_ascii=False)

# 3. Ler template Churn Safra 28
print("\n3. Adaptando Template Churn Safra 28...")
with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8') as f:
    template = f.read()

p_start = template.find('const PAYLOAD = ')
p_end = template.find('/* ============ decodificação ============ */')
html_code = template[:p_start + len('const PAYLOAD = ')] + payload_json_str + ';\n\n' + template[p_end:]

# Título e Header
html_code = html_code.replace(
    '<h1><b>Churn Safra</b> <span>Regional Norte</span></h1>',
    '<h1><b>FPD — First Payment Default</b> <span>Regional Norte</span></h1>'
)
html_code = html_code.replace(
    '<title>Painel Churn Safra — Regional Norte</title>',
    '<title>Painel FPD — First Payment Default · Regional Norte | Pephub</title>'
)
html_code = html_code.replace(
    '<span><b>13 safras</b> · set/2025 a set/2026</span>',
    '<span><b>5 safras</b> · jan/2026 a mai/2026</span>'
)
html_code = html_code.replace(
    'Janela de apuração <b>120 dias</b>',
    'Janela oficial <b>FPD 60 (1ª fatura cheia)</b>'
)
html_code = html_code.replace(
    'Posição <b>21/09/2026</b>',
    'Posição <b>01/06/2026</b>'
)
html_code = html_code.replace(
    'Descompactando base (348.866 instalações)…',
    f'Descompactando base FPD ({count:,} instalações)…'
)

# Safras e Maturidade (safra foco padrão mai/26)
html_code = html_code.replace(
    "const SAFRA_ORD=['set/25','out/25','nov/25','dez/25','jan/26','fev/26','mar/26','abr/26','mai/26','jun/26','jul/26','ago/26','set/26'];",
    "const SAFRA_ORD=['jan/26','fev/26','mar/26','abr/26','mai/26'];"
)
html_code = html_code.replace(
    "const MATUR={'set/25':356,'out/25':325,'nov/25':295,'dez/25':264,'jan/26':233,'fev/26':205,'mar/26':174,'abr/26':144,'mai/26':113,'jun/26':83,'jul/26':52,'ago/26':21,'set/26':1};",
    "const MATUR={'jan/26':151,'fev/26':120,'mar/26':92,'abr/26':61,'mai/26':31};"
)
html_code = html_code.replace("const JANELA=120;", "const JANELA=60;")
html_code = html_code.replace("const POS_Y=2026,POS_M=9,POS_D=20;", "const POS_Y=2026,POS_M=6,POS_D=1;")

# FPD: safras consolidadas
html_code = html_code.replace("const isParcial=s=>(MATUR[s]===undefined?true:MATUR[s]<JANELA);", "const isParcial=s=>false;")
html_code = html_code.replace("const maturoR=r=>diasDe(r)>=JANELA;", "const maturoR=r=>true;")
html_code = html_code.replace("const ABERTAS=new Set(Object.keys(MATUR).filter(isParcial));", "const ABERTAS=new Set();")
html_code = html_code.replace("let abertaSafraIdx=new Set(), safraFoco=null;", "let abertaSafraIdx=new Set(), safraFoco='mai/26';")
html_code = html_code.replace("let safraFoco=null;", "let safraFoco='mai/26';")

# Variáveis globais declaradas no topo para evitar Temporal Dead Zone
html_code = html_code.replace("let SAFRA_DISP_=null;", "var SAFRA_DISP=[];")
html_code = html_code.replace("let SAFRA_DISP=[];", "/* SAFRA_DISP ja no topo */")

# defaultAnchor
old_default_anchor_pattern = re.search(r'function defaultAnchor\(\)\{.*?return SAFRA_DISP\[Math\.max\(0,SAFRA_DISP\.length-5\)\];\s*\}', html_code, re.DOTALL)
if old_default_anchor_pattern:
    html_code = html_code[:old_default_anchor_pattern.start()] + "function defaultAnchor(){ return SAFRA_DISP.length ? SAFRA_DISP[SAFRA_DISP.length - 1] : 'mai/26'; }" + html_code[old_default_anchor_pattern.end():]

# applySafra
old_apply_safra = re.search(r'function applySafra\(\)\{.*?(?=/\* =+ filtros dependentes)', html_code, re.DOTALL)
if old_apply_safra:
    new_apply_safra = """function applySafra(){
  const v=document.getElementById('fSafra').value;
  const info=document.getElementById('safraInfo');
  if(!v){ 
    delete sel.safra; 
    safraFoco='mai/26'; 
    info.innerHTML='todas as 5 safras · safra foco em <b>mai/26</b>'; 
    return; 
  }
  const i=D.safra.indexOf(v);
  sel.safra=new Set(i>=0?[i]:[]); 
  safraFoco=v;
  info.innerHTML=`instalações de <b>${v}</b> · safra consolidada com delay oficial de FPD`;
}
"""
    html_code = html_code[:old_apply_safra.start()] + new_apply_safra + html_code[old_apply_safra.end():]

html_code = html_code.replace('<label>Safra de instalação<span class="cnt">13</span></label>', '<label>Safra de instalação<span class="cnt">5</span></label>')
html_code = html_code.replace(
    '<label class="muted" style="display:flex;align-items:center;gap:5px"><input id="rkClosed" type="checkbox"> apenas safras fechadas</label>',
    '<label class="muted" style="display:none"><input id="rkClosed" type="checkbox"></label>'
)

# ==================== SUBSTITUIÇÃO SEQUENCIAL DAS FUNÇÕES DE CIMA PARA BAIXO ====================

# 1. NÚCLEO MATEMÁTICO: addRow FPD (preserva mrg, sel, IDX, buildIndex e aggBy)
old_add_row_pattern = re.search(r'function blank\(\)\{ return \{inst:0,c:\[0,0,0,0,0\].*?function addRow\(o,r\)\{.*?(?=function mrg)', html_code, re.DOTALL)
if old_add_row_pattern:
    new_add_row = """function blank(){ return {inst:0,c:[0,0,0,0,0],np:[0,0,0,0,0],npc:[0,0,0,0,0],tp:[0,0,0]}; }
function addRow(o,r){
  o.inst++;
  const a30 = C.ag30 ? C.ag30[r] : 0;
  const a60 = C.ag60 ? C.ag60[r] : 0;

  if(a30) o.c[0]++;
  if(a60) o.c[1]++;

  const p = C.pbk[r];
  const nuncaPg = (p === 0 || (a30 && a60));
  if(a30) o.np[0]++;
  if(nuncaPg){
    o.np[1]++;
    if(a60) o.npc[1]++;
  }

  const t = C.tpk[r]; 
  if(t > 0 && a60) o.tp[t-1]++;
}
"""
    html_code = html_code[:old_add_row_pattern.start()] + new_add_row + html_code[old_add_row_pattern.end():]

# 2. GRÁFICO SAFRA
old_safra_pattern = re.search(r'/\* =+ gráfico safra =+ \*/\s*function drawSafra\(\)\{.*?(?=/\* =+ curva)', html_code, re.DOTALL)
if old_safra_pattern:
    new_safra_code = """/* ============ gráfico safra ============ */
function drawSafra(){
  const host=document.getElementById('chSafra'); host.innerHTML='';
  const m=aggBy('safra',IDXT);
  const rows=SAFRA_ORD.map(s=>({s,o:m.get(D.safra.indexOf(s))})).filter(r=>r.o&&r.o.inst>0);
  if(!rows.length)return;
  const W=760,H=300,L=56,R=48,T=20,B=44, s=svg(W,H); host.appendChild(s);
  const maxI=Math.max(...rows.map(r=>r.o.inst))*1.12;
  const maxP=Math.max(...rows.map(r=>Math.max(pn(r.o.c[1],r.o.inst),pn(r.o.c[0],r.o.inst))))*1.22||1;
  const iw=(W-L-R)/rows.length, bw=Math.min(iw*.6,44);
  for(let g=0;g<=4;g++){const y=T+(H-T-B)*g/4;
    el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'#eceef1'},s);
    s.appendChild(tx(s,L-7,y+3,fmt(maxI*(1-g/4)),{'text-anchor':'end','font-size':9}));
    s.appendChild(tx(s,W-R+6,y+3,(maxP*(1-g/4)).toFixed(1).replace('.',',')+'%',{'font-size':9,fill:'#c0392b'}));}
  const pc60=[],pc30=[];
  rows.forEach((r,i)=>{
    const x=L+iw*i+iw/2, h=(H-T-B)*r.o.inst/maxI, fc=isFoco(r.s);
    if(fc) el('rect',{x:x-iw/2+1,y:T-4,width:iw-2,height:(H-B)-(T-4),fill:FOCO_BG},s);
    el('rect',{x:x-bw/2,y:H-B-h,width:bw,height:h,fill:fc?'#c98a15':'#516173',
      stroke:fc?'#8a5d06':'none','stroke-width':fc?2:0},s);
    
    const tx60 = pn(r.o.c[1],r.o.inst);
    const tx30 = pn(r.o.c[0],r.o.inst);
    
    pc60.push([x,T+(H-T-B)*(1-tx60/maxP),false,tx60]);
    pc30.push([x,T+(H-T-B)*(1-tx30/maxP),false,tx30]);
    
    s.appendChild(tx(s,x,H-B+13,r.s,{'text-anchor':'middle','font-size':9.5,
      'font-weight':fc?700:400,fill:fc?'#8a5d06':'#5b6675'}));
    s.appendChild(tx(s,x,H-B+24,fc?'safra foco':'fechada',
      {'text-anchor':'middle','font-size':8,fill:fc?'#8a5d06':'#2f7d5d','font-weight':fc?700:400}));
    
    const prevRow = i > 0 ? rows[i-1] : null;
    let momTxt = '';
    if (prevRow) {
      const prevTx60 = pn(prevRow.o.c[1], prevRow.o.inst);
      const diff60 = tx60 - prevTx60;
      momTxt = `<br><span class="d">MoM FPD 60:</span> <b style="color:${diff60<=0?'#7fd6a0':'#ff8b7d'}">${diff60>=0?'+':''}${diff60.toFixed(2).replace('.',',')} p.p.</b>`;
    }
    
    hitRect(s,x-iw/2,T-6,iw,(H-B)-(T-6),()=>
      `<b>${r.s.toUpperCase()}</b> ${fc?'· <span class="w">SAFRA EM FOCO</span>':''}<br>
       <span class="d">Instalações:</span> <b>${fmt(r.o.inst)}</b><br>
       <hr>
       <span class="d">FPD 60 (Oficial):</span> <b>${tx60.toFixed(2).replace('.',',')}%</b> (${fmt(r.o.c[1])} contratos)${momTxt}<br>
       <span class="d">FPD 30 (Pré-FPD):</span> <b>${tx30.toFixed(2).replace('.',',')}%</b> (${fmt(r.o.c[0])} contratos)<br>
       <span class="d">Adimplência:</span> <b>${(100-tx60).toFixed(2).replace('.',',')}%</b> em dia`);
  });

  let d30='M'+pc30.map(p=>p[0]+','+p[1]).join(' L');
  el('path',{d:d30,fill:'none',stroke:'#7d4bb0','stroke-width':2,'stroke-dasharray':'4,3'},s);
  pc30.forEach(([x,y,,val])=>{
    el('circle',{cx:x,cy:y,r:3.5,fill:'#7d4bb0'},s);
    s.appendChild(tx(s,x,y-6,val.toFixed(1).replace('.',',')+'%',{'text-anchor':'middle','font-size':8.5,fill:'#7d4bb0','font-weight':600}));
  });

  let d60='M'+pc60.map(p=>p[0]+','+p[1]).join(' L');
  el('path',{d:d60,fill:'none',stroke:'#e03131','stroke-width':3},s);
  pc60.forEach(([x,y,,val])=>{
    el('circle',{cx:x,cy:y,r:4.5,fill:'#e03131'},s);
    s.appendChild(tx(s,x,y-7,val.toFixed(1).replace('.',',')+'%',{'text-anchor':'middle','font-size':9,fill:'#e03131','font-weight':700}));
  });
}
"""
    html_code = html_code[:old_safra_pattern.start()] + new_safra_code + html_code[old_safra_pattern.end():]

# 3. ITEM 1: DISPERSÃO MoM & YoY (Substitui curva)
curva_html_pattern = re.search(r'<div class="panel">\s*<h2>Curva de maturação.*?</div>\s*</div>', html_code, re.DOTALL)
if curva_html_pattern:
    new_scatter_html = """<div class="panel">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
      <h2 style="margin:0">Dispersão MoM & YoY <span class="note">evolução da taxa FPD 60 vs volume</span></h2>
      <div style="display:flex;align-items:center;gap:8px">
        <div class="tabs" id="tabsScatComp">
          <button class="on" data-m="mom" style="padding:3px 8px;font-size:11px">MoM (vs Safra Anterior)</button>
          <button data-m="yoy" style="padding:3px 8px;font-size:11px">vs Jan/26 (Início Série)</button>
        </div>
        <div class="tabs" id="tabsScatDim">
          <button class="on" data-d="cidade" style="padding:3px 8px;font-size:11px">Cidade</button>
          <button data-d="canal_grupo" style="padding:3px 8px;font-size:11px">Canal</button>
          <button data-d="produto" style="padding:3px 8px;font-size:11px">Produto</button>
          <button data-d="empresa" style="padding:3px 8px;font-size:11px">Empresa</button>
          <button data-d="vendedor" style="padding:3px 8px;font-size:11px">Vendedor</button>
        </div>
      </div>
    </div>
    <div class="pbody" style="padding-bottom:4px"><div id="chScatter"></div></div>
    <div class="lgd" id="lgdScatter" style="margin-top:4px">
      <span><i style="background:#2f7d5d"></i>Melhora FPD 60 (Redução da taxa)</span>
      <span><i style="background:#c0392b"></i>Piora FPD 60 (Aumento da taxa)</span>
      <span style="color:var(--ink3)">Tamanho da bolha = Volume de instalações</span>
    </div>
  </div>"""
    html_code = html_code[:curva_html_pattern.start()] + new_scatter_html + html_code[curva_html_pattern.end():]

old_curva_js_pattern = re.search(r'/\* =+ curva =+ \*/\s*function drawCurva\(\)\{.*?(?=/\* =+ cidades)', html_code, re.DOTALL)
if old_curva_js_pattern:
    new_scatter_js = """/* ============ dispersão MoM & YoY ============ */
let scatDim='cidade', scatComp='mom';
function drawScatter(){
  const host=document.getElementById('chScatter'); 
  if(!host)return;
  host.innerHTML='';
  
  let sfFoco = safraFoco || 'mai/26';
  if (sel.safra && sel.safra.size === 1) sfFoco = D.safra[[...sel.safra][0]];
  const idxSf = SAFRA_ORD.indexOf(sfFoco);
  
  let sfComp = null;
  if(scatComp==='mom'){
    sfComp = idxSf > 0 ? SAFRA_ORD[idxSf - 1] : (SAFRA_ORD.length>1?SAFRA_ORD[0]:null);
  } else {
    sfComp = SAFRA_ORD[0];
  }
  if(!sfComp || sfComp === sfFoco) sfComp = idxSf > 0 ? SAFRA_ORD[idxSf - 1] : null;

  const iFoco = D.safra.indexOf(sfFoco);
  const iComp = sfComp ? D.safra.indexOf(sfComp) : -1;

  const mFoco = new Map();
  const mComp = new Map();

  for(let i=0; i<IDXT.length; i++){
    const r = IDXT[i];
    const s = C.safra[r];
    const k = C[scatDim][r];
    if(s === iFoco){
      let o = mFoco.get(k); if(!o){ o={inst:0,c60:0,c30:0}; mFoco.set(k,o); }
      o.inst++;
      if(C.ag60 && C.ag60[r]) o.c60++;
      if(C.ag30 && C.ag30[r]) o.c30++;
    } else if(s === iComp){
      let o = mComp.get(k); if(!o){ o={inst:0,c60:0,c30:0}; mComp.set(k,o); }
      o.inst++;
      if(C.ag60 && C.ag60[r]) o.c60++;
      if(C.ag30 && C.ag30[r]) o.c30++;
    }
  }

  const items = [];
  mFoco.forEach((oF, k)=>{
    if(oF.inst < 5) return;
    const oC = mComp.get(k) || {inst:0, c60:0, c30:0};
    const txF = pn(oF.c60, oF.inst);
    const txC = oC.inst > 0 ? pn(oC.c60, oC.inst) : txF;
    const diff = txF - txC;
    items.push({
      id: k,
      nome: D[scatDim][k] || 'Não Informado',
      instFoco: oF.inst,
      c60Foco: oF.c60,
      txFoco: txF,
      instComp: oC.inst,
      c60Comp: oC.c60,
      txComp: txC,
      diff: diff
    });
  });

  items.sort((a,b)=>b.instFoco - a.instFoco);
  const topItems = items.slice(0, 35);
  if(!topItems.length){
    host.innerHTML='<div style="padding:40px;text-align:center;color:var(--ink3);font-size:12px">Dados insuficientes para gerar a dispersão nesta combinação de filtros.</div>';
    return;
  }

  const W=520, H=300, L=50, R=24, T=20, B=40, s=svg(W,H); host.appendChild(s);
  
  const minDiff = Math.min(-5, ...topItems.map(d=>d.diff));
  const maxDiff = Math.max(5, ...topItems.map(d=>d.diff));
  const absMaxY = Math.max(Math.abs(minDiff), Math.abs(maxDiff)) * 1.15;
  
  const maxTxX = Math.max(30, ...topItems.map(d=>d.txFoco)) * 1.15;
  const maxInst = Math.max(...topItems.map(d=>d.instFoco));

  const Y0 = T + (H - T - B) / 2;
  const scaleY = diff => Y0 - (diff / absMaxY) * ((H - T - B) / 2);
  const scaleX = tx => L + (tx / maxTxX) * (W - L - R);

  for(let g = -2; g <= 2; g++){
    const val = (absMaxY * g / 2);
    const y = scaleY(val);
    el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:g===0?'#78909c':'#edf0f2','stroke-width':g===0?1.5:1,'stroke-dasharray':g===0?'none':'3,3'},s);
    const lab = (val > 0 ? '+' : '') + val.toFixed(1).replace('.',',') + ' p.p.';
    s.appendChild(tx(s,L-6,y+3,lab,{'text-anchor':'end','font-size':8,fill:g===0?'#37474f':'#90a4ae','font-weight':g===0?700:400}));
  }

  for(let g = 1; g <= 4; g++){
    const val = (maxTxX * g / 4);
    const x = scaleX(val);
    el('line',{x1:x,x2:x,y1:T,y2:H-B,stroke:'#f1f3f5','stroke-dasharray':'2,2'},s);
    s.appendChild(tx(s,x,H-B+14,val.toFixed(0)+'%',{'text-anchor':'middle','font-size':8.5,fill:'#90a4ae'}));
  }

  s.appendChild(tx(s,W-R,H-B+14,'Taxa FPD 60 Atual →',{'text-anchor':'end','font-size':9,fill:'#546e7a','font-weight':600}));
  s.appendChild(tx(s,L+4,T+10,'↑ Piora ('+(scatComp==='mom'?'MoM':'YoY')+')',{'font-size':8.5,fill:'#c0392b','font-weight':600}));
  s.appendChild(tx(s,L+4,H-B-6,'↓ Melhora ('+(scatComp==='mom'?'MoM':'YoY')+')',{'font-size':8.5,fill:'#2f7d5d','font-weight':600}));

  topItems.forEach(d=>{
    const cx = scaleX(d.txFoco);
    const cy = scaleY(d.diff);
    const r = Math.max(4, Math.min(22, Math.sqrt(d.instFoco / maxInst) * 22));
    const isMelhora = d.diff <= 0;
    const cor = isMelhora ? '#2f7d5d' : '#c0392b';
    
    const circ = el('circle',{
      cx, cy, r,
      fill: cor,
      'fill-opacity': 0.65,
      stroke: cor,
      'stroke-width': 1.5,
      cursor: 'pointer'
    }, s);

    if(d.instFoco > maxInst * 0.15 || topItems.length <= 12){
      const nomeCurto = d.nome.length > 12 ? d.nome.slice(0,10)+'…' : d.nome;
      s.appendChild(tx(s, cx, cy - r - 3, nomeCurto, {'text-anchor':'middle','font-size':8.5,fill:'#263238','font-weight':600}));
    }

    hov(circ, ()=>
      `<b>${d.nome}</b> (${RANKDIMS.find(x=>x[0]===scatDim)[1]})<hr>`+
      `Safra foco (<b>${sfFoco}</b>): <b>${d.txFoco.toFixed(2).replace('.',',')}%</b> FPD 60 (${fmt(d.c60Foco)} / ${fmt(d.instFoco)} inst)<br>`+
      (sfComp ? `Safra ref (<b>${sfComp}</b>): ${d.txComp.toFixed(2).replace('.',',')}% FPD 60 (${fmt(d.c60Comp)} / ${fmt(d.instComp)} inst)<br>` : '')+
      `<hr>Variação ${scatComp.toUpperCase()}: <b style="color:${isMelhora?'#7fd6a0':'#ff8b7d'}">${d.diff>=0?'+':''}${d.diff.toFixed(2).replace('.',',')} p.p.</b> `+
      `(${isMelhora?'Melhora':'Piora'})`
    );
  });
}
"""
    html_code = html_code[:old_curva_js_pattern.start()] + new_scatter_js + html_code[old_curva_js_pattern.end():]

# 4. CIDADES (IBGE)
old_cid_pattern = re.search(r'/\* =+ cidades \(IBGE\) =+ \*/\s*let cidDim=.*?(?=/\* =+ nunca pagou)', html_code, re.DOTALL)
if old_cid_pattern:
    new_cid_code = """/* ============ cidades (IBGE) ============ */
let cidDim='cidade';
function drawCid(){
  const host=document.getElementById('chCid'); host.innerHTML='';
  const m=aggBy(cidDim,IDX);
  let rows=[...m.entries()].map(([i,o])=>({nome:cidDim==='porte'?mercLab(D[cidDim][i]):D[cidDim][i],o})).filter(r=>r.o.inst>0);
  rows.sort((a,b)=>b.o.inst-a.o.inst);
  const top=rows.slice(0,20);
  if(!top.length)return;
  const FS=10, rh=25, L=Math.min(200,Math.max(78,...top.map(r=>twid(r.nome,FS)))+14);
  const W=1160,R=232,T=10,H=T+top.length*rh+12, s=svg(W,H); host.appendChild(s);
  const maxI=Math.max(...top.map(r=>r.o.inst));
  top.forEach((r,i)=>{ const o=r.o,y=T+i*rh,bh=14,full=W-L-R,w=full*o.inst/maxI;
    s.appendChild(tx(s,L-7,y+bh-2,r.nome,{'text-anchor':'end','font-size':FS,fill:'#1c2430','font-weight':600}));
    const rc=el('rect',{x:L,y,width:Math.max(1,w),height:bh,fill:'#516173'},s);
    hov(rc,()=>`<b>${r.nome}</b><hr><b>${fmt(o.inst)}</b> instalações<br>`+
      `FPD 60 oficial <b>${pct(o.c[1],o.inst,2)}</b> · ${fmt(o.c[1])} contratos<br>`+
      `FPD 30 ${pct(o.c[0],o.inst,2)} · nunca pagou <b>${pct(o.np[1],o.inst,2)}</b><br>`+
      `em dia ${pct(o.inst-o.c[1],o.inst,2)} (${fmt(o.inst-o.c[1])} contratos)<br>`+
      `<span class="d">Alto risco ${fmt(o.tp[0])} · Médio ${fmt(o.tp[1])} · Baixo ${fmt(o.tp[2])}</span>`);
    const p60=pn(o.c[1],o.inst), p30=pn(o.c[0],o.inst);
    s.appendChild(tx(s,L+w+7,y+bh-2,
      `${fmt(o.inst)} inst · ${p60.toFixed(1).replace('.',',')}% FPD 60 · ${p30.toFixed(1).replace('.',',')}% FPD 30`,
      {'font-size':9.5,fill:'#5b6675'}));
  });
  let h='<thead><tr><th class="l">'+(cidDim==='porte'?'Mercado':DIMDEF.find(x=>x[0]===cidDim)[1])+'</th><th>Instalações</th>';
  h+='<th>FPD 30</th><th>% FPD 30</th><th>FPD 60 (Oficial)</th><th>% FPD 60</th><th>Nunca Pagou</th><th>% NP</th><th>Em Dia</th><th>% Em Dia</th></tr></thead><tbody>';
  const tot=blank();
  rows.forEach(r=>{ const o=r.o; mrg(tot,o);
    h+=`<tr><td class="l">${r.nome}</td><td>${fmt(o.inst)}</td>
      <td>${fmt(o.c[0])}</td><td style="color:#7d4bb0">${pct(o.c[0],o.inst)}</td>
      <td>${fmt(o.c[1])}</td><td style="color:#c0392b;font-weight:700">${pct(o.c[1],o.inst)}</td>
      <td>${fmt(o.np[1])}</td><td style="color:#6b4b8a">${pct(o.np[1],o.inst)}</td>
      <td style="color:#2f7d5d;font-weight:600">${fmt(o.inst-o.c[1])}</td><td style="color:#2f7d5d;font-weight:600">${pct(o.inst-o.c[1],o.inst)}</td></tr>`;});
  h+=`</tbody><tfoot><tr><td class="l">Total Geral</td><td>${fmt(tot.inst)}</td>
    <td>${fmt(tot.c[0])}</td><td>${pct(tot.c[0],tot.inst)}</td>
    <td>${fmt(tot.c[1])}</td><td>${pct(tot.c[1],tot.inst)}</td>
    <td>${fmt(tot.np[1])}</td><td>${pct(tot.np[1],tot.inst)}</td>
    <td style="color:#2f7d5d;font-weight:700">${fmt(tot.inst-tot.c[1])}</td><td style="color:#2f7d5d;font-weight:700">${pct(tot.inst-tot.c[1],tot.inst)}</td></tr></tfoot>`;
  document.getElementById('tblCid').innerHTML=h;
}
"""
    html_code = html_code[:old_cid_pattern.start()] + new_cid_code + html_code[old_cid_pattern.end():]

# 5. NUNCA PAGOU
old_np_pattern = re.search(r'/\* =+ nunca pagou =+ \*/\s*let npMode=.*?(?=/\* =+ motivo)', html_code, re.DOTALL)
if old_np_pattern:
    new_np_code = """/* ============ nunca pagou ============ */
let npMode='pct';
function drawNp(){
  const host=document.getElementById('chNp'); host.innerHTML='';
  const m=aggBy('safra',IDXT);
  const rows=SAFRA_ORD.map(s=>({s,o:m.get(D.safra.indexOf(s))})).filter(r=>r.o&&r.o.inst>0);
  if(!rows.length)return;
  const W=1160,rh=25,L=62,R=250,T=8,H=T+rows.length*rh+10,s=svg(W,H); host.appendChild(s);
  const maxI=Math.max(...rows.map(r=>r.o.inst));
  rows.forEach((r,i)=>{
    const o=r.o,y=T+i*rh,bh=14,full=W-L-R,wT=npMode==='pct'?full:full*o.inst/maxI;
    const cSem=o.npc[1], cCom=Math.max(0, o.c[1]-o.npc[1]), aSem=Math.max(0, o.np[1]-o.npc[1]), aPg=Math.max(0, o.inst-o.c[1]);
    const segs=[[cSem,'#6b4b8a','Inadimplente 60d (nunca pagou)'],[cCom,'#c0392b','Inadimplente 60d (pagou 30d)'],
                [aSem,'#c98a15','Em dia no 60d (atrasou 30d)'],[aPg,'#2f7d5d','100% adimplente em dia']];
    if(isFoco(r.s)) el('rect',{x:2,y:y-3,width:W-4,height:bh+6,fill:FOCO_BG},s);
    s.appendChild(tx(s,L-7,y+bh-2,r.s,{'text-anchor':'end','font-size':10,
      fill:isFoco(r.s)?'#8a5d06':'#1c2430','font-weight':isFoco(r.s)?800:600}));
    let acc=0;
    segs.forEach(([v,col,lab])=>{ if(v<=0)return; const w=wT*v/o.inst;
      const rc=el('rect',{x:L+acc,y,width:w,height:bh,fill:col},s);
      hov(rc,()=>`<b>${SAFLAB(r.s)}</b><br><span class="d">${lab}</span><hr>`+
        `<b>${fmt(v)}</b> contratos · <b>${pct(v,o.inst,2)}</b> da safra<br>`+
        `base ${fmt(o.inst)} instalações<br>`+
        `<span class="d">FPD 60 oficial ${pct(o.c[1],o.inst)} · nunca pagou ${pct(o.np[1],o.inst)}</span>`);
      acc+=w; });
    s.appendChild(tx(s,L+wT+7,y+bh-2,`${pct(o.c[1],o.inst)} FPD 60 · ${pct(aPg,o.inst)} em dia`,{'font-size':9.5}));
  });
  let h='<thead><tr><th class="l">Safra</th><th class="l">Status</th><th>Instalações</th><th>NP FPD 30</th><th>%</th><th>NP FPD 60</th><th>%</th><th>FPD 60 Oficial</th><th>FPD 60 Nunca Pagou</th><th>% do FPD 60</th><th>FPD 60 Pagou 30d</th><th>Em Dia (Adimplente)</th></tr></thead><tbody>';
  const tot=blank();
  rows.forEach(r=>{ const o=r.o; mrg(tot,o);
    const semPg=o.npc[1];
    h+=`<tr${focoRow(r.s)}><td class="l"><b>${r.s}</b>${focoTag(r.s)}</td><td class="l"><span class="tag fe">FECHADA</span></td>
      <td>${fmt(o.inst)}</td><td>${fmt(o.np[0])}</td><td>${pct(o.np[0],o.inst)}</td>
      <td>${fmt(o.np[1])}</td><td>${pct(o.np[1],o.inst)}</td>
      <td>${fmt(o.c[1])}</td><td><b>${fmt(semPg)}</b></td><td><b>${pct(semPg,o.c[1])}</b></td>
      <td>${fmt(o.c[1]-semPg)}</td><td style="color:#2f7d5d;font-weight:600">${fmt(o.inst-o.c[1])} (${pct(o.inst-o.c[1],o.inst)})</td></tr>`;});
  h+=`</tbody><tfoot><tr><td class="l">Total</td><td></td><td>${fmt(tot.inst)}</td><td>${fmt(tot.np[0])}</td><td>${pct(tot.np[0],tot.inst)}</td>
    <td>${fmt(tot.np[1])}</td><td>${pct(tot.np[1],tot.inst)}</td><td>${fmt(tot.c[1])}</td><td>${fmt(tot.npc[1])}</td><td>${pct(tot.npc[1],tot.c[1])}</td>
    <td>${fmt(tot.c[1]-tot.npc[1])}</td><td style="color:#2f7d5d;font-weight:700">${fmt(tot.inst-tot.c[1])} (${pct(tot.inst-tot.c[1],tot.inst)})</td></tr></tfoot>`;
  document.getElementById('tblNp').innerHTML=h;
}
"""
    html_code = html_code[:old_np_pattern.start()] + new_np_code + html_code[old_np_pattern.end():]

# 6. ITENS 3 E 4: VISÃO DEDICADA DE RISCO (FX_RISCO_NV) E SCORE (FXULTSCORE)
old_mot_html_pattern = re.search(r'<div class="panel">\s*<h2>Motivo da desconexão.*?</div>\s*</div>\s*</div>', html_code, re.DOTALL)
if old_mot_html_pattern:
    new_risco_html = """<div class="panel">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <h2 style="margin:0">Qualidade de Venda & Perfil de Crédito <span class="note">visão oficial de FX_RISCO_NV e faixas de score FXULTSCORE</span></h2>
    <div class="tabs" id="tabsRiscoMode">
      <button class="on" data-r="risco_nv">Perfil de Risco (FX_RISCO_NV)</button>
      <button data-r="score">Faixas de Score (FXULTSCORE)</button>
    </div>
  </div>
  <div class="pbody" style="padding-bottom:4px"><div id="chRisco"></div></div>
  <div class="scroll"><table id="tblRisco"></table></div>
  <div class="foot">
    Visão analítica gerada a partir das colunas oficiais <code>FX_RISCO_NV</code> e <code>FXULTSCORE</code>. 
    Permite identificar a aderência da esteira de aprovação e o impacto direto do score na taxa de inadimplência precoce (FPD 60 e FPD 30).
  </div>
</div>"""
    html_code = html_code[:old_mot_html_pattern.start()] + new_risco_html + html_code[old_mot_html_pattern.end():]

old_mot_js_pattern = re.search(r'/\* =+ motivo =+ \*/\s*let motMode=.*?(?=/\* =+ esteira)', html_code, re.DOTALL)
if old_mot_js_pattern:
    new_risco_js = """/* ============ risco e score ============ */
let riscoDim='risco_nv';
function drawRisco(){
  const host=document.getElementById('chRisco'); if(!host)return; host.innerHTML='';
  const m=aggBy(riscoDim, IDX);
  
  let rows=[...m.entries()].map(([i,o])=>({
    nome: D[riscoDim][i] || 'Não Informado',
    inst: o.inst,
    c60: o.c[1],
    p60: pn(o.c[1], o.inst),
    c30: o.c[0],
    p30: pn(o.c[0], o.inst),
    np: o.npc[1] || o.np[1],
    pnp: pn(o.npc[1] || o.np[1], o.inst),
    emdia: Math.max(0, o.inst - o.c[1]),
    pemdia: pn(Math.max(0, o.inst - o.c[1]), o.inst)
  })).filter(r=>r.inst>0);

  if(riscoDim==='risco_nv'){
    const ordRisco = ['Baixissimo','Baixo','Medio','Alto','Altissimo1','Altissimo2','SCORE 0 e 1','Não Informado'];
    rows.sort((a,b)=>{
      const ia = ordRisco.indexOf(a.nome);
      const ib = ordRisco.indexOf(b.nome);
      return (ia>=0?ia:99) - (ib>=0?ib:99);
    });
  } else {
    rows.sort((a,b)=>b.inst - a.inst);
  }

  const baseTot = aggTot(IDX);
  const maxI = Math.max(...rows.map(r=>r.inst));

  const FS=10, rh=26, L=160, R=220, T=10, H=T+rows.length*rh+14, s=svg(1160, H);
  host.appendChild(s);
  const W=1160, full=W-L-R;

  rows.forEach((r,i)=>{
    const y=T+i*rh, bh=15, w=full*r.inst/maxI;
    s.appendChild(tx(s, L-8, y+bh-2, r.nome, {'text-anchor':'end','font-size':FS,fill:'#1c2430','font-weight':600}));
    
    const cor = r.p60 > 35 ? '#c0392b' : (r.p60 > 22 ? '#c98a15' : '#2f7d5d');
    const rc = el('rect',{x:L, y, width:Math.max(2,w), height:bh, fill:cor, 'fill-opacity':0.85}, s);
    
    hov(rc, ()=>
      `<b>${r.nome}</b> (${riscoDim==='risco_nv'?'Perfil de Risco':'Faixa de Score'})<hr>`+
      `Instalações: <b>${fmt(r.inst)}</b> (${pct(r.inst, baseTot.inst, 1)} da base)<br>`+
      `FPD 60 Oficial: <b style="color:#c0392b">${r.p60.toFixed(2).replace('.',',')}%</b> (${fmt(r.c60)} contratos)<br>`+
      `FPD 30 Pré-FPD: <b>${r.p30.toFixed(2).replace('.',',')}%</b> (${fmt(r.c30)} contratos)<br>`+
      `Nunca Pagou: <b>${pct(r.np, r.inst)}</b> · Em dia: <b>${r.pemdia.toFixed(2).replace('.',',')}%</b>`);

    s.appendChild(tx(s, L+w+8, y+bh-2, 
      `${fmt(r.inst)} inst (${pct(r.inst, baseTot.inst)}) · FPD 60: ${r.p60.toFixed(1).replace('.',',')}% · FPD 30: ${r.p30.toFixed(1).replace('.',',')}%`,
      {'font-size':9.5, fill:'#5b6675', 'font-weight':500}));
  });

  let thLab = riscoDim==='risco_nv' ? 'Perfil de Risco (FX_RISCO_NV)' : 'Faixa de Score (FXULTSCORE)';
  let h = `<thead><tr>
    <th class="l">${thLab}</th>
    <th>Instalações</th>
    <th>% da Base</th>
    <th>FPD 60 Oficial</th>
    <th>% FPD 60</th>
    <th>FPD 30 Pré-FPD</th>
    <th>% FPD 30</th>
    <th>Nunca Pagou</th>
    <th>% NP</th>
    <th>Em Dia</th>
    <th>% Em Dia</th>
  </tr></thead><tbody>`;

  rows.forEach(r=>{
    const badgeColor = r.p60 > 35 ? '#c0392b' : (r.p60 > 22 ? '#c98a15' : '#2f7d5d');
    h += `<tr>
      <td class="l"><b>${r.nome}</b></td>
      <td>${fmt(r.inst)}</td>
      <td class="muted">${pct(r.inst, baseTot.inst, 1)}</td>
      <td>${fmt(r.c60)}</td>
      <td style="color:${badgeColor};font-weight:700">${r.p60.toFixed(2).replace('.',',')}%</td>
      <td>${fmt(r.c30)}</td>
      <td style="color:#7d4bb0">${r.p30.toFixed(2).replace('.',',')}%</td>
      <td>${fmt(r.np)}</td>
      <td class="muted">${pct(r.np, r.inst, 1)}</td>
      <td style="color:#2f7d5d;font-weight:600">${fmt(r.emdia)}</td>
      <td style="color:#2f7d5d;font-weight:600">${r.pemdia.toFixed(2).replace('.',',')}%</td>
    </tr>`;
  });

  const totFpd60 = baseTot.c[1];
  const totFpd30 = baseTot.c[0];
  const totNp = baseTot.npc[1] || baseTot.np[1];
  const totEmDia = Math.max(0, baseTot.inst - totFpd60);

  h += `</tbody><tfoot><tr>
    <td class="l">Total Regional</td>
    <td>${fmt(baseTot.inst)}</td>
    <td>100,0%</td>
    <td>${fmt(totFpd60)}</td>
    <td style="font-weight:700">${pct(totFpd60, baseTot.inst, 2)}</td>
    <td>${fmt(totFpd30)}</td>
    <td style="color:#7d4bb0">${pct(totFpd30, baseTot.inst, 2)}</td>
    <td>${fmt(totNp)}</td>
    <td>${pct(totNp, baseTot.inst, 1)}</td>
    <td style="color:#2f7d5d;font-weight:700">${fmt(totEmDia)}</td>
    <td style="color:#2f7d5d;font-weight:700">${pct(totEmDia, baseTot.inst, 2)}</td>
  </tr></tfoot>`;
  
  const tblEl = document.getElementById('tblRisco');
  if(tblEl) tblEl.innerHTML = h;
}
"""
    html_code = html_code[:old_mot_js_pattern.start()] + new_risco_js + html_code[old_mot_js_pattern.end():]

# 7. ESTEIRA
new_draw_esteira = """/* ============ esteira ============ */
let estMode='pct';
function drawEsteira(){
  const host=document.getElementById('chEsteira'); host.innerHTML='';
  const map=new Map();
  for(let i=0;i<IDXT.length;i++){ const r=IDXT[i],k=C.safra[r];
    let o=map.get(k); if(!o){o={inst:0,c30:0,c60:0};map.set(k,o);}
    o.inst++;
    if(C.ag30 && C.ag30[r]) o.c30++;
    if(C.ag60 && C.ag60[r]) o.c60++;
  }
  const rows=SAFRA_ORD.map(s=>({s,o:map.get(D.safra.indexOf(s))})).filter(r=>r.o&&r.o.inst>0);
  if(!rows.length)return;
  const W=1160,rh=25,L=62,R=232,T=8,H=T+rows.length*rh+10,s=svg(W,H); host.appendChild(s);
  const maxI=Math.max(...rows.map(r=>r.o.inst));
  rows.forEach((r,i)=>{ const o=r.o,y=T+i*rh,bh=14,full=W-L-R,wT=estMode==='pct'?full:full*o.inst/maxI;
    if(isFoco(r.s)) el('rect',{x:2,y:y-3,width:W-4,height:bh+6,fill:FOCO_BG},s);
    s.appendChild(tx(s,L-7,y+bh-2,r.s,{'text-anchor':'end','font-size':10,
      fill:isFoco(r.s)?'#8a5d06':'#1c2430','font-weight':isFoco(r.s)?800:600}));
    
    const emDia = Math.max(0, o.inst - o.c60);
    const w60 = wT * o.c60 / o.inst;
    const wDia = wT * emDia / o.inst;
    el('rect',{x:L,y,width:w60,height:bh,fill:'#e03131'},s);
    el('rect',{x:L+w60,y,width:wDia,height:bh,fill:'#2f7d5d'},s);
    
    hitRect(s,L,y-2,wT,bh+4,()=>
      `<b>${SAFLAB(r.s)}</b><hr>`+
      `FPD 60 Oficial: <b>${fmt(o.c60)}</b> (${pct(o.c60,o.inst)})<br>`+
      `FPD 30 Pré-FPD: <b>${fmt(o.c30)}</b> (${pct(o.c30,o.inst)})<br>`+
      `Contratos Em Dia: <b>${fmt(emDia)}</b> (${pct(emDia,o.inst)})<br>`+
      `<span class="d">base total: ${fmt(o.inst)} instalações</span>`);
    
    s.appendChild(tx(s,L+wT+7,y+bh-2,`${pct(o.c60,o.inst)} FPD 60 · ${pct(emDia,o.inst)} em dia`,{'font-size':9.5}));
  });
  
  let h='<thead><tr><th class="l">Safra</th><th class="l">Status</th><th>Instalações</th>';
  h+='<th>FPD 30 (Pró-rata)</th><th>% FPD 30</th><th>FPD 60 (Oficial)</th><th>% FPD 60</th><th>Em Dia (Adimplente)</th><th>% Em Dia</th></tr></thead><tbody>';
  const tot={inst:0,c30:0,c60:0};
  rows.forEach(r=>{ const o=r.o; tot.inst+=o.inst; tot.c30+=o.c30; tot.c60+=o.c60;
    const emDia = Math.max(0, o.inst - o.c60);
    h+=`<tr${focoRow(r.s)}><td class="l"><b>${r.s}</b>${focoTag(r.s)}</td><td class="l"><span class="tag fe">FECHADA</span></td><td>${fmt(o.inst)}</td>
      <td>${fmt(o.c30)}</td><td style="color:#7d4bb0">${pct(o.c30,o.inst)}</td>
      <td>${fmt(o.c60)}</td><td style="color:#c0392b;font-weight:700">${pct(o.c60,o.inst)}</td>
      <td style="color:#2f7d5d;font-weight:600">${fmt(emDia)}</td><td style="color:#2f7d5d;font-weight:600">${pct(emDia,o.inst)}</td></tr>`;
  });
  const totEmDia = Math.max(0, tot.inst - tot.c60);
  h+=`</tbody><tfoot><tr><td class="l">Total</td><td></td><td>${fmt(tot.inst)}</td>
    <td>${fmt(tot.c30)}</td><td>${pct(tot.c30,tot.inst)}</td>
    <td>${fmt(tot.c60)}</td><td>${pct(tot.c60,tot.inst)}</td>
    <td style="color:#2f7d5d;font-weight:700">${fmt(totEmDia)}</td><td style="color:#2f7d5d;font-weight:700">${pct(totEmDia,tot.inst)}</td></tr></tfoot>`;
  document.getElementById('tblEsteira').innerHTML=h;
}
"""
old_esteira_pattern = re.search(r'/\* =+ esteira =+ \*/.*?function drawEsteira\(\)\{.*?(?=/\* =+ KPIs)', html_code, re.DOTALL)
if old_esteira_pattern:
    html_code = html_code[:old_esteira_pattern.start()] + new_draw_esteira + html_code[old_esteira_pattern.end():]

# 8. KPIS E REMOÇÃO DA MATRIZ (Substitui desde KPIs até Ranking, engolindo a matriz obsoleta de safra)
# Primeiro remover o container HTML da matriz
mtx_html_pattern = re.search(r'<div class="panel">\s*<h2>Matriz de safra.*?</div>\s*</div>\s*</div>', html_code, re.DOTALL)
if mtx_html_pattern:
    html_code = html_code[:mtx_html_pattern.start()] + html_code[mtx_html_pattern.end():]

old_kpis_to_rank_pattern = re.search(r'/\* =+ KPIs =+ \*/.*?function drawKpis\(\)\{.*?(?=/\* =+ ranking)', html_code, re.DOTALL)
if old_kpis_to_rank_pattern:
    new_kpis_clean = """/* ============ KPIs ============ */
function drawKpis(){
  const t = aggTot(IDX);
  const m = aggBy('safra', IDXT);
  
  let sfFoco = safraFoco || 'mai/26';
  if (sel.safra && sel.safra.size === 1) sfFoco = D.safra[[...sel.safra][0]];
  
  const oFoco = m.get(D.safra.indexOf(sfFoco)) || t;
  const idxSf = SAFRA_ORD.indexOf(sfFoco);
  const sfAnt = idxSf > 0 ? SAFRA_ORD[idxSf - 1] : null;
  const oAnt = sfAnt ? m.get(D.safra.indexOf(sfAnt)) : null;
  
  const instFoco = oFoco.inst;
  const fpd60Foco = oFoco.c[1];
  const txFpd60Foco = pn(fpd60Foco, instFoco);
  
  const fpd30Foco = oFoco.c[0];
  const txFpd30Foco = pn(fpd30Foco, instFoco);
  
  const adimpFoco = Math.max(0, instFoco - fpd60Foco);
  const txAdimpFoco = pn(adimpFoco, instFoco);
  
  let momFpd60Str = '—';
  let momFpd60Color = 'var(--ink2)';
  let momInstStr = '—';
  let diff60 = 0;
  if (oAnt && oAnt.inst > 0) {
    const txFpd60Ant = pn(oAnt.c[1], oAnt.inst);
    diff60 = txFpd60Foco - txFpd60Ant;
    const diffInstPct = (instFoco - oAnt.inst) / oAnt.inst * 100;
    
    const sinal60 = diff60 >= 0 ? '+' : '';
    momFpd60Color = diff60 <= 0 ? 'var(--green)' : 'var(--red)';
    momFpd60Str = `<b style="color:${momFpd60Color}">${sinal60}${diff60.toFixed(2).replace('.', ',')} p.p.</b> vs ${sfAnt}`;
    
    const sinalInst = diffInstPct >= 0 ? '+' : '';
    momInstStr = `${sinalInst}${diffInstPct.toFixed(1).replace('.', ',')}% vs ${sfAnt} (${instFoco - oAnt.inst >= 0 ? '+' : ''}${fmt(instFoco - oAnt.inst)})`;
  }
  
  const totInst = t.inst;
  const totFpd60 = t.c[1];
  const txTotFpd60 = pn(totFpd60, totInst);
  const diffTotFoco = txFpd60Foco - txTotFpd60;
  
  const npFoco = oFoco.npc[1] || oFoco.np[1];
  const regFoco = Math.max(0, fpd30Foco - fpd60Foco);
  
  const card = (k, v, d, cls='', badge='') => `<div class="kpi ${cls}"><div class="k">${k} ${badge}</div><div class="v">${v}</div><div class="d">${d}</div></div>`;
  const badgeFoco = `<span class="pc" style="background:#fdf3e2;color:#8a5d06;border-color:#f0dcb4;font-weight:700">${sfFoco.toUpperCase()}</span>`;
  
  document.getElementById('kpis').innerHTML =
    card('Instalações Analisadas', fmt(instFoco), `${momInstStr} · ${fmt(totInst)} acumulado`, '', badgeFoco) +
    card('Taxa FPD 60 (Oficial)', pct(fpd60Foco, instFoco, 2), `${fmt(fpd60Foco)} contratos na 1ª fatura cheia`, 'acc', badgeFoco) +
    card('Taxa FPD 30 (Pré-FPD)', pct(fpd30Foco, instFoco, 2), `${fmt(fpd30Foco)} contratos pró-rata · Onboarding`, 'np', badgeFoco) +
    card('Adimplência 1ª Fatura', pct(adimpFoco, instFoco, 2), `${fmt(adimpFoco)} contratos em dia`, 'fe', badgeFoco) +
    card('Variação MoM (FPD 60)', momFpd60Str, `Evolução direta da qualidade de venda`, diff60 <= 0 ? 'fe' : 'acc', badgeFoco) +
    card('Benchmark YTD (Acumulado)', pct(totFpd60, totInst, 2), `${diffTotFoco >= 0 ? '+' : ''}${diffTotFoco.toFixed(2).replace('.', ',')} p.p. vs média regional (${fmt(totFpd60)} desc)`, '') +
    card('Nunca Pagou (FPD 30 & 60)', pct(npFoco, instFoco, 2), `${fmt(npFoco)} contratos sem nenhum pagamento`, 'np', badgeFoco) +
    card('Regularização Pré-FPD', pct(regFoco, fpd30Foco, 1), `${fmt(regFoco)} clientes curados no ciclo cheio`, 'fe', badgeFoco) +
    card('Inadimplência Alto Risco', pct(oFoco.tp[0], fpd60Foco, 1), `${fmt(oFoco.tp[0])} contratos com score restritivo`, 'acc', badgeFoco);
}

"""
    html_code = html_code[:old_kpis_to_rank_pattern.start()] + new_kpis_clean + html_code[old_kpis_to_rank_pattern.end():]

# 9. RANKING: VISÕES DE PRODUTO, RISCO, SCORE E PORTFÓLIO TV
old_draw_rank_pattern = re.search(r'/\* =+ ranking =+ \*/\s*const RANKDIMS=.*?(?=/\* =+ MAPA)', html_code, re.DOTALL)
if old_draw_rank_pattern:
    new_draw_rank_code = """/* ============ ranking ============ */
const RANKDIMS=[
  ['parceiro','Parceiro Comercial'],
  ['produto','Produto (Família Domicílio)'],
  ['portfolio_tv','Portfólio TV'],
  ['risco_nv','Perfil de Risco (FX_RISCO_NV)'],
  ['score','Faixa de Score (FXULTSCORE)'],
  ['vendedor','Vendedor'],
  ['cidade','Cidade'],
  ['canal_grupo','Canal de Venda'],
  ['canal_sub','Canal (Subgrupo)'],
  ['bairro','Bairro'],
  ['node','Node'],
  ['pagto','Forma de Pagamento']
];
let rankDim='parceiro';
let rankSort={k:'p60',dir:-1};

function drawRank(){
  const idx=IDX;
  const m=aggBy(rankDim,idx), base=aggTot(idx), refP=pn(base.c[1],base.inst);
  const min=+document.getElementById('rkMin').value||0, q=document.getElementById('rkSearch').value.trim().toLowerCase();
  
  let rows=[...m.entries()].map(([i,o])=>({
    nome: rankDim==='porte'?mercLab(D[rankDim][i]):(D[rankDim][i] || 'Não Informado'),
    inst: o.inst,
    c60: o.c[1],
    p60: pn(o.c[1],o.inst),
    c30: o.c[0],
    p30: pn(o.c[0],o.inst),
    emdia: Math.max(0, o.inst - o.c[1]),
    pemdia: pn(Math.max(0, o.inst - o.c[1]), o.inst),
    np: o.npc[1] || o.np[1],
    pnp: pn(o.npc[1] || o.np[1], o.inst),
    dif: pn(o.c[1],o.inst) - refP
  })).filter(r=>r.inst>=min&&(!q||r.nome.toLowerCase().includes(q)));

  rows.sort((a,b)=>{
    const va=a[rankSort.k], vb=b[rankSort.k];
    return typeof va==='string' ? rankSort.dir*va.localeCompare(vb,'pt-BR') : rankSort.dir*(va-vb);
  });

  const maxP=Math.max(1,...rows.map(r=>r.p60));
  let h=`<thead><tr>
    <th class="l sortable" data-k="nome">${RANKDIMS.find(x=>x[0]===rankDim)[1]}</th>
    <th class="sortable" data-k="inst">Instalações</th>
    <th class="sortable" data-k="c60">FPD 60 (Qtd)</th>
    <th class="sortable" data-k="p60">% FPD 60 (Oficial)</th>
    <th class="sortable" data-k="c30">FPD 30 (Qtd)</th>
    <th class="sortable" data-k="p30">% FPD 30 (Pré-FPD)</th>
    <th class="sortable" data-k="pemdia">% Em Dia</th>
    <th class="sortable" data-k="np">Nunca Pagou</th>
    <th class="sortable" data-k="dif">Dif vs Regional</th>
  </tr></thead><tbody>`;

  rows.forEach(r=>{
    const barW = Math.round(r.p60/maxP*100);
    const badgeColor = r.p60 > 28 ? '#c0392b' : (r.p60 > 20 ? '#c98a15' : '#2f7d5d');
    const difSinal = r.dif >= 0 ? '+' : '';
    const difColor = r.dif > 0 ? '#c0392b' : '#2f7d5d';

    h += `<tr>
      <td class="l"><b>${r.nome}</b></td>
      <td>${fmt(r.inst)}</td>
      <td>${fmt(r.c60)}</td>
      <td style="font-weight:700;color:${badgeColor}">
        <span class="bar" style="width:50px"><i style="width:${barW}%;background:${badgeColor}"></i></span>
        ${r.p60.toFixed(2).replace('.',',')}%
      </td>
      <td>${fmt(r.c30)}</td>
      <td style="color:#7d4bb0">${r.p30.toFixed(2).replace('.',',')}%</td>
      <td style="color:#2f7d5d;font-weight:600">${r.pemdia.toFixed(2).replace('.',',')}%</td>
      <td class="muted">${fmt(r.np)} (${r.pnp.toFixed(1).replace('.',',')}%)</td>
      <td style="color:${difColor};font-weight:600">${difSinal}${r.dif.toFixed(2).replace('.',',')} p.p.</td>
    </tr>`;
  });
  h += '</tbody>';
  document.getElementById('tblRank').innerHTML=h;
  document.getElementById('rkInfo').textContent=`${rows.length} registros exibidos · base seleção: ${fmt(base.inst)} inst · FPD 60 ref: ${refP.toFixed(2).replace('.',',')}%`;

  document.querySelectorAll('#tblRank th.sortable').forEach(th=>{
    const k=th.dataset.k;
    if(k===rankSort.k) th.classList.add(rankSort.dir>0?'asc':'desc');
    th.onclick=()=>{
      if(rankSort.k===k) rankSort.dir*=-1;
      else{ rankSort.k=k; rankSort.dir=(k==='nome'?1:-1); }
      drawRank();
    };
  });
}
"""
    html_code = html_code[:old_draw_rank_pattern.start()] + new_draw_rank_code + html_code[old_draw_rank_pattern.end():]

# 10. MAPA: ACCUM, VAL E PONTOS
new_accum = """function accum(o,r){ o.n++;
  const a30 = C.ag30 ? C.ag30[r] : 0;
  const a60 = C.ag60 ? C.ag60[r] : 0;
  const p = C.pbk[r], t = C.tpk[r];

  if(a30) o.ac[0]++;
  if(a60){ o.ac[1]++; o.c++; }

  const naoPg = (p === 0 || (a30 && a60));
  if(naoPg) o.np++;
  if(a60 && naoPg) o.npc++;
  if(!a60 && naoPg) o.anp++;
  if(isInferido(r)) o.inf++;
  if(a60 && t > 0) o.tp[t-1]++; }
"""
old_accum_pattern = re.search(r'function accum\(o,r\)\{.*?(?=function buildCells)', html_code, re.DOTALL)
if old_accum_pattern:
    html_code = html_code[:old_accum_pattern.start()] + new_accum + html_code[old_accum_pattern.end():]

new_dot_color = """function dotColor(metric,a,p,t,dark,a60,a30){
  const naoPg = (p === 0 || (a30 && a60));
  switch(metric){
    case 'c60': case 'volchurn': case 'churn':
      return a60 ? DOTC.ch : (dark?DOTC.okDark:DOTC.ok);
    case 'c30': case 'volc30':
      return a30 ? '#7d4bb0' : (dark?DOTC.okDark:DOTC.ok);
    case 'np': case 'npc':
      return naoPg ? DOTC.np : (dark?DOTC.okDark:DOTC.ok);
    case 'inad':
      return (a60 && t===1) ? DOTC.inad : (dark?DOTC.okDark:DOTC.ok);
    case 'ativos': case 'ativosnp':
      return !a60 ? '#2f7d5d' : DOTC.ch;
  }
  return a60 ? DOTC.ch : (dark?DOTC.okDark:DOTC.ok);
}
function dotIsHot(metric,a,p,t,a60,a30){
  const naoPg = (p === 0 || (a30 && a60));
  switch(metric){
    case 'c60': case 'volchurn': case 'churn': return a60 === 1;
    case 'c30': case 'volc30': return a30 === 1;
    case 'np': case 'npc': return naoPg;
    case 'inad': return a60 === 1 && t === 1;
    case 'ativos': case 'ativosnp': return a60 === 0;
  }
  return a60 === 1;
}
"""
old_dot_color_pattern = re.search(r'function dotColor\(.*?(?=let dotIdx)', html_code, re.DOTALL)
if old_dot_color_pattern:
    html_code = html_code[:old_dot_color_pattern.start()] + new_dot_color + html_code[old_dot_color_pattern.end():]

old_draw_dots_lines = """      const x=mercX(qLon(r),ws)-left; if(x<-2||x>W+2)continue;
      const y=mercY(qLat(r),ws)-top;  if(y<-2||y>H+2)continue;
      const col=onlyCh?DOTC.ch:dotColor(metric,a,p,tp,dark);"""
new_draw_dots_lines = """      const a60=C.ag60?C.ag60[r]:0, a30=C.ag30?C.ag30[r]:0;
      const x=mercX(qLon(r),ws)-left; if(x<-2||x>W+2)continue;
      const y=mercY(qLat(r),ws)-top;  if(y<-2||y>H+2)continue;
      const col=onlyCh?DOTC.ch:dotColor(metric,a,p,tp,dark,a60,a30);"""
html_code = html_code.replace(old_draw_dots_lines, new_draw_dots_lines)

old_draw_dots_hot = """      const hot=onlyCh?true:dotIsHot(metric,a,p,tp);"""
new_draw_dots_hot = """      const a60_h=C.ag60?C.ag60[r]:0, a30_h=C.ag30?C.ag30[r]:0;
      const hot=onlyCh?true:dotIsHot(metric,a,p,tp,a60_h,a30_h);"""
html_code = html_code.replace(old_draw_dots_hot, new_draw_dots_hot)

new_map_val = """const val=o=>{ switch(metric){
    case 'vol': return o.n;
    case 'volchurn': return o.c;
    case 'volc30': return o.ac[0];
    case 'ativos': return (o.n-o.c)/o.n;
    case 'ativosnp': return (o.n-o.c);
    case 'c30': return o.ac[0]/o.n;
    case 'c60': case 'churn': return o.ac[1]/o.n;
    case 'np': return o.np/o.n;
    case 'npc': return o.npc/o.n;
    case 'pativosnp': return o.anp/o.n;
    case 'orig': case 'pinf': return o.inf/o.n;
    case 'inad': return o.tp[0]/o.n;
    case 'opcao': return o.tp[1]/o.n;
    case 'fraude': return o.tp[2]/o.n;
  } return o.n; };"""
old_map_val_pattern = re.search(r'const val=o=>\{ switch\(metric\)\{.*?(?=\} return o\.n; \};)', html_code, re.DOTALL)
if old_map_val_pattern:
    html_code = html_code[:old_map_val_pattern.start()] + new_map_val + html_code[old_map_val_pattern.end() + len('} return o.n; };'):]

# Seletor de Métricas do Mapa
new_map_metric_html = """          <select id="mapMetric">
            <optgroup label="Indicadores Oficiais de FPD">
              <option value="c60" selected>Taxa FPD 60 Oficial (1ª fatura cheia)</option>
              <option value="c30">Taxa FPD 30 (Pré-FPD / Pró-rata)</option>
              <option value="ativos">Taxa de Adimplência (Em dia)</option>
            </optgroup>
            <optgroup label="Volume e Concentração">
              <option value="vol">Concentração de Instalações</option>
              <option value="volchurn">Volume Inadimplente FPD 60</option>
              <option value="volc30">Volume Inadimplente FPD 30</option>
              <option value="ativosnp">Volume de Contratos Em Dia</option>
            </optgroup>
            <optgroup label="Risco e Pagamento">
              <option value="np">Nunca Pagou (FPD 30 & 60) / instalações</option>
              <option value="inad">Inadimplência Carteira Alto Risco</option>
            </optgroup>
          </select>"""
old_map_metric_pattern = re.search(r'<select id="mapMetric">.*?</select>', html_code, re.DOTALL)
if old_map_metric_pattern:
    html_code = html_code[:old_map_metric_pattern.start()] + new_map_metric_html + html_code[old_map_metric_pattern.end():]

new_mlab = """const MLAB={
  c60:'Taxa FPD 60 Oficial (1ª fatura cheia)',
  c30:'Taxa FPD 30 (Pré-FPD / Pró-rata)',
  churn:'Taxa FPD 60 Oficial',
  vol:'Concentração de Instalações',
  volchurn:'Volume Inadimplente FPD 60',
  volc30:'Volume Inadimplente FPD 30',
  ativos:'Taxa de Adimplência (Em dia)',
  ativosnp:'Volume de Contratos Em Dia',
  np:'Nunca Pagou (FPD 30 & 60) / instalações',
  inad:'Inadimplência Carteira Alto Risco',
  orig:'Origem do bairro (cadastro × inferido)',
  pinf:'Bairro inferido / instalações'
};"""
old_mlab_pattern = re.search(r'const MLAB=\{.*?\};', html_code, re.DOTALL)
if old_mlab_pattern:
    html_code = html_code[:old_mlab_pattern.start()] + new_mlab + html_code[old_mlab_pattern.end():]

# 11. GAVETA DE FILTROS COM PORTFOLIO_TV E SEM TRAVAMENTO DE ASSINATURA/DADOS
old_build_filters_pattern = re.search(r'function buildFilterUI\(\)\{.*?(?=function rebuildFilters)', html_code, re.DOTALL)
if old_build_filters_pattern:
    new_build_filters_code = """function buildFilterUI(){
  const fEl=document.getElementById('filters');
  fEl.innerHTML='';
  
  const st=document.createElement('div'); st.style.display='none';
  st.innerHTML='<select id="fStatus"><option value="all" selected>(todas)</option></select>';
  fEl.appendChild(st);

  const sf=document.createElement('div'); sf.className='f';
  sf.innerHTML='<label>Safra de instalação<span class="cnt">5</span></label>'+
    '<select id="fSafra" style="width:100%;border:1px solid var(--line);padding:4px;font:12px sans-serif">'+
    '<option value="">(todas as safras)</option>'+
    SAFRA_DISP.map(x=>`<option value="${x}">${x}</option>`).join('')+'</select>'+
    '<div class="sel" id="safraInfo" style="color:var(--ink3)"></div>';
  fEl.appendChild(sf);

  DIMDEF.forEach(([dim,lab])=>{
    if(dim==='safra')return;
    const div=document.createElement('div'); div.className='f';
    let vals=D[dim].map((v,i)=>[v,i]);
    vals.sort((a,b)=>a[0].localeCompare(b[0],'pt-BR'));
    div.innerHTML=`<label>${lab}<span class="cnt">${D[dim].length}</span></label>
      <div class="frow">
        <input type="text" placeholder="buscar…" data-s="${dim}">
        <button class="fbtn" data-all="${dim}" title="Selecionar tudo que está visível">T</button>
        <button class="fbtn" data-clr="${dim}" title="Limpar este filtro">×</button>
      </div>
      <select multiple data-dim="${dim}">${vals.map(([v,i])=>`<option value="${i}">${v}</option>`).join('')}</select>
      <div class="sel" id="sel_${dim}"></div>
      <div class="na-note" id="na_${dim}"></div>`;
    fEl.appendChild(div);
  });

  fEl.querySelectorAll('input[data-s]').forEach(inp=>{
    inp.oninput=()=>{
      const dim=inp.dataset.s, q=inp.value.trim().toLowerCase();
      const s=fEl.querySelector(`select[data-dim="${dim}"]`);
      let vis=0;
      [...s.options].forEach(o=>{ const hit=(!q||o.textContent.toLowerCase().includes(q))&&!o.disabled;
        o.hidden=!hit; if(hit)vis++; });
      const btn=fEl.querySelector(`button[data-all="${dim}"]`);
      btn.classList.toggle('act',!!q);
      btn.title=q?`Selecionar os ${vis} itens do filtro de busca`:'Selecionar tudo que está visível';
    };
    inp.onkeydown=e=>{ if(e.key==='Enter'){e.preventDefault();
      fEl.querySelector(`button[data-all="${inp.dataset.s}"]`).click(); } };
  });

  fEl.querySelectorAll('button[data-all]').forEach(b=>{
    b.onclick=()=>{ const s=fEl.querySelector(`select[data-dim="${b.dataset.all}"]`);
      [...s.options].forEach(o=>{ if(!o.hidden&&!o.disabled)o.selected=true; }); readFiltersFromUI(); render(); };
  });

  fEl.querySelectorAll('button[data-clr]').forEach(b=>{
    b.onclick=()=>{ const dim=b.dataset.clr, s=fEl.querySelector(`select[data-dim="${dim}"]`);
      [...s.options].forEach(o=>{o.selected=false;o.hidden=false;o.disabled=false;o.classList.remove('na');});
      const inp=fEl.querySelector(`input[data-s="${dim}"]`); inp.value='';
      fEl.querySelector(`button[data-all="${dim}"]`).classList.remove('act');
      readFiltersFromUI(); render(); };
  });

  document.getElementById('fSafra').value=defaultAnchor();
  document.getElementById('fSafra').onchange=render;
}
"""
    html_code = html_code[:old_build_filters_pattern.start()] + new_build_filters_code + html_code[old_build_filters_pattern.end():]

# DIMDEF com novas dimensões (portfolio_tv, risco_nv, score)
html_code = html_code.replace(
    "['produto','Tipo de produto'],['marca','Marca'],['perfil','Perfil do cliente'],['pagto','Forma de pagamento'],['motivo','Motivo da desconexão']",
    "['produto','Produto (Família Domicílio)'],['portfolio_tv','Portfólio TV'],['risco_nv','Perfil de Risco (FX_RISCO_NV)'],['score','Faixa de Score (FXULTSCORE)'],['marca','Marca'],['perfil','Perfil do cliente'],['pagto','Forma de pagamento'],['motivo','Status FPD / Inadimplência']"
)

# Atualizar render_()
html_code = html_code.replace(
    "drawKpis(); drawSafra(); drawCurva(); drawCid(); drawNp(); drawMot(); drawMtx(); drawEsteira(); drawRank();",
    "drawKpis(); drawSafra(); drawScatter(); drawCid(); drawNp(); drawRisco(); drawEsteira(); drawRank();"
)

# Event Listeners para botões interativos
events_code = """  // Eventos Dispersão MoM & YoY
  const scCompEl = document.getElementById('tabsScatComp');
  if(scCompEl){
    scCompEl.onclick=e=>{ if(e.target.dataset.m){
      scatComp = e.target.dataset.m;
      [...e.currentTarget.children].forEach(b=>b.className='');
      e.target.className='on';
      drawScatter();
    }};
  }
  const scDimEl = document.getElementById('tabsScatDim');
  if(scDimEl){
    scDimEl.onclick=e=>{ if(e.target.dataset.d){
      scatDim = e.target.dataset.d;
      [...e.currentTarget.children].forEach(b=>b.className='');
      e.target.className='on';
      drawScatter();
    }};
  }

  // Eventos Visão de Risco & Score
  const rModeEl = document.getElementById('tabsRiscoMode');
  if(rModeEl){
    rModeEl.onclick=e=>{ if(e.target.dataset.r){
      riscoDim = e.target.dataset.r;
      [...e.currentTarget.children].forEach(b=>b.className='');
      e.target.className='on';
      drawRisco();
    }};
  }
"""

html_code = html_code.replace(
    "document.getElementById('tabsCid').onclick=",
    events_code + "\n  document.getElementById('tabsCid').onclick="
)

# Remover listeners de Matriz e Motivos obsoletos em init()
old_mtx_listeners = """  document.getElementById('tabsMtx').onclick=e=>{if(e.target.dataset.m){mtxMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawMtx();}};
  document.getElementById('mtxMature').onchange=drawMtx;
  document.getElementById('mtxDim').onchange=drawMtx;
  document.getElementById('tabsEst').onclick=e=>{if(e.target.dataset.m){estMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawEsteira();}};
  document.getElementById('tabsMot').onclick=e=>{if(e.target.dataset.m){motMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawMot();}};
  document.getElementById('tabsNp').onclick=e=>{if(e.target.dataset.m){npMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawNp();}};"""

new_mtx_listeners = """  const elEst=document.getElementById('tabsEst');
  if(elEst) elEst.onclick=e=>{if(e.target.dataset.m){estMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawEsteira();}};
  const elNp=document.getElementById('tabsNp');
  if(elNp) elNp.onclick=e=>{if(e.target.dataset.m){npMode=e.target.dataset.m;
    [...e.currentTarget.children].forEach(b=>b.className='');e.target.className='on';drawNp();}};"""
html_code = html_code.replace(old_mtx_listeners, new_mtx_listeners)

# Limpar botão btnClear
old_clear_code = """  document.getElementById('btnClear').onclick=()=>{
    fEl.querySelectorAll('select[multiple]').forEach(s=>[...s.options].forEach(o=>{o.selected=false;o.hidden=false;o.disabled=false;o.classList.remove('na');}));
    fEl.querySelectorAll('input[data-s]').forEach(i=>i.value='');
    fEl.querySelectorAll('button[data-all]').forEach(b=>b.classList.remove('act'));
    document.getElementById('fStatus').value='all';
    const pv=fEl.querySelector('select[data-dim="produto"]'), ip=D.produto.indexOf('Dados');
  if(ip>=0)[...pv.options].forEach(o=>{if(+o.value===ip)o.selected=true;});
  document.getElementById('fSafra').value=defaultAnchor(); render(); };"""

new_clear_code = """  document.getElementById('btnClear').onclick=()=>{
    fEl.querySelectorAll('select[multiple]').forEach(s=>[...s.options].forEach(o=>{o.selected=false;o.hidden=false;o.disabled=false;o.classList.remove('na');}));
    fEl.querySelectorAll('input[data-s]').forEach(i=>i.value='');
    fEl.querySelectorAll('button[data-all]').forEach(b=>b.classList.remove('act'));
    const fSt = document.getElementById('fStatus'); if(fSt) fSt.value='all';
    document.getElementById('fSafra').value=defaultAnchor(); render(); };"""
html_code = html_code.replace(old_clear_code, new_clear_code)

# Detalhe de contratos e CSV
new_open_contratos = """function openContratos(rows,titulo){
  if(!rows||!rows.length)return;
  const box=document.getElementById('ctrBox'), bd=document.getElementById('ctrBody');
  document.getElementById('ctrTitle').textContent=titulo;
  const H=['Contrato','Instalação','FPD 60 Oficial','FPD 30 Pré-FPD','Status Pagto','Safra','Canal','Subcanal','Parceiro','Vendedor','Risco (NV)','Score','Portfólio TV','Produto','Bairro','Cidade','Node'];
  let h='<table class="ctrtbl"><thead><tr>'+H.map(x=>`<th>${x}</th>`).join('')+'</tr></thead><tbody>';
  const ord=rows.slice().sort((a,b)=>((C.ag60?C.ag60[b]:0)-(C.ag60?C.ag60[a]:0)));
  ord.forEach(r=>{
    const a60 = C.ag60 ? C.ag60[r] : 0;
    const a30 = C.ag30 ? C.ag30[r] : 0;
    const p = C.pbk[r];
    const naoPg = (p === 0 || (a30 && a60));
    const statusTxt = naoPg ? '<span class="np">Nunca pagou</span>' : (a60 ? '<span style="color:#c0392b;font-weight:600">Inadimplente 60d</span>' : (a30 ? '<span style="color:#7d4bb0">Atraso pró-rata</span>' : '<span style="color:#2f7d5d;font-weight:600">Em dia</span>'));
    
    h+=`<tr class="${a60?'isch':''}"><td><b>${C.ctr[r]}</b></td><td>${dtInst(r)}</td>`+
       `<td>${a60?'<b style="color:#c0392b">SIM</b>':'<span style="color:#2f7d5d">NÃO</span>'}</td>`+
       `<td>${a30?'<span style="color:#7d4bb0">SIM</span>':'NÃO'}</td>`+
       `<td>${statusTxt}</td>`+
       `<td>${D.safra[C.safra[r]]}</td><td>${D.canal_grupo[C.canal_grupo[r]]}</td>`+
       `<td>${D.canal_sub[C.canal_sub[r]]}</td>`+
       `<td>${D.parceiro[C.parceiro[r]]}</td><td>${D.vendedor[C.vendedor[r]]}</td>`+
       `<td>${D.risco_nv[C.risco_nv[r]]}</td><td>${D.score[C.score[r]]}</td><td>${D.portfolio_tv[C.portfolio_tv[r]]}</td>`+
       `<td>${D.produto[C.produto[r]]}</td><td>${bairroOfMark(r)}</td>`+
       `<td>${D.cidade[C.cidade[r]]}</td><td>${D.node[C.node[r]]}</td></tr>`;});
  h+='</tbody></table>';
  const n60=ord.filter(r=>(C.ag60?C.ag60[r]:0)===1).length;
  const n30=ord.filter(r=>(C.ag30?C.ag30[r]:0)===1).length;
  const nnp=ord.filter(r=>(C.pbk[r]===0||((C.ag30?C.ag30[r]:0)&&(C.ag60?C.ag60[r]:0)))).length;
  document.getElementById('ctrSum').innerHTML=
    `<b>${fmt(ord.length)}</b> ${plur(ord.length,'contrato','contratos')} · `+
    `<b>${fmt(n60)}</b> FPD 60 (${pct(n60,ord.length,1)}) · <b>${fmt(n30)}</b> FPD 30 · <b>${fmt(nnp)}</b> nunca ${plur(nnp,'pagou','pagaram')}`;
  bd.innerHTML=h;
  box.classList.add('on');
  ctrExport=ord;
}
"""
old_open_contratos_pattern = re.search(r'function openContratos\(rows,titulo\)\{.*?(?=let ctrExport)', html_code, re.DOTALL)
if old_open_contratos_pattern:
    html_code = html_code[:old_open_contratos_pattern.start()] + new_open_contratos + html_code[old_open_contratos_pattern.end():]

# Salvar Arquivos
print("\n4. Salvando Arquivos...")
with open('Painel_FPD_Regional_Norte.html', 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Salvo Painel_FPD_Regional_Norte.html com sucesso!")

with open('public/fpd/index.html', 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Salvo public/fpd/index.html com sucesso!")

with open('public/fpd/Painel_FPD_Regional_Norte.html', 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Salvo public/fpd/Painel_FPD_Regional_Norte.html com sucesso!")

print("\nProcesso concluído com sucesso!")
