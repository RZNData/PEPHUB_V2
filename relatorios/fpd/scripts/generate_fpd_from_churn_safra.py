import csv
import json
import zlib
import base64
import os
import re

print("=== 1. Indexando Georreferenciamento e Dimensões Territoriais ===")
geocod = {}
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name: i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO', 14)
    b_idx = h_idx.get('BAIRRO', 8)
    n_idx = h_idx.get('NODE', 9)
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

print(f"Lookup de contratos geocodificados carregado: {len(geocod):,} registros.")

print("\n=== 2. Lendo Base FPD e Montando Estrutura Churn Safra ===")

dicts = {
    'safra': [],
    'uf': [],
    'tipo_cidade': [],
    'porte': [],
    'ddd': [],
    'canal_grupo': [],
    'canal_sub': [],
    'produto': [],
    'marca': [],
    'perfil': [],
    'pagto': [],
    'visao': [],
    'motivo': [],
    'ger_negocio': [],
    'ger_canal': [],
    'tipo_canal': [],
    'key_account': [],
    'coordenador': [],
    'ger_filial': [],
    'executivo': [],
    'cidade': [],
    'bairro': [],
    'node': [],
    'parceiro': [],
    'empresa': [],
    'vendedor': []
}

dict_indices = {k: {} for k in dicts}

def get_code(dim, val):
    v = str(val).strip() if val else "Não Informado"
    if not v:
        v = "Não Informado"
    if v not in dict_indices[dim]:
        idx = len(dicts[dim])
        dicts[dim].append(v)
        dict_indices[dim][v] = idx
        return idx
    return dict_indices[dim][v]

# Listas de colunas
cols_data = {
    'safra': [], 'uf': [], 'tipo_cidade': [], 'porte': [], 'ddd': [],
    'canal_grupo': [], 'canal_sub': [], 'produto': [], 'marca': [],
    'perfil': [], 'pagto': [], 'visao': [], 'motivo': [],
    'ger_negocio': [], 'ger_canal': [], 'tipo_canal': [], 'key_account': [],
    'coordenador': [], 'ger_filial': [], 'executivo': [],
    'cidade': [], 'bairro': [], 'node': [], 'parceiro': [],
    'empresa': [], 'vendedor': [],
    'abk': [], 'pbk': [], 'tpk': [], 'dinst': [], 'aging': [], 'ctr': []
}

lats = []
lons = []

safra_nome = {
    '202601': 'jan/26',
    '202602': 'fev/26',
    '202603': 'mar/26',
    '202604': 'abr/26',
    '202605': 'mai/26'
}

ddd_por_cidade = {
    'MANAUS': '92', 'BELEM': '91', 'BELÉM': '91', 'SAO LUIS': '98', 'SÃO LUÍS': '98',
    'MACAPA': '96', 'MACAPÁ': '96', 'IMPERATRIZ': '99', 'CASTANHAL': '91',
    'PARAUAPEBAS': '94', 'MARABA': '94', 'MARABÁ': '94', 'ANANINDEUA': '91',
    'SANTANA': '96', 'BOA VISTA': '95', 'ABAETETUBA': '91', 'BARCARENA': '91',
    'TIMON': '99', 'SANTA INES': '99', 'CAXIAS': '99', 'ITAITUBA': '93',
    'ALTAMIRA': '93', 'PARINTINS': '92', 'ITACOATIARA': '92'
}

porte_por_cidade = {
    'MANAUS': 'Grandes', 'BELEM': 'Grandes', 'BELÉM': 'Grandes', 'SAO LUIS': 'Grandes', 'SÃO LUÍS': 'Grandes',
    'IMPERATRIZ': 'Desenvolvimento', 'MACAPA': 'Desenvolvimento', 'MACAPÁ': 'Desenvolvimento',
    'ANANINDEUA': 'Desenvolvimento', 'MARABA': 'Desenvolvimento', 'MARABÁ': 'Desenvolvimento',
    'PARAUAPEBAS': 'Desenvolvimento', 'CASTANHAL': 'Desenvolvimento'
}

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name: i for i, name in enumerate(h)}

    idx_ctr = h_idx.get('NR_CONTRATO', 4)
    idx_dt_inst = h_idx.get('DT_INI_CONTRATO', 5)
    idx_safra = h_idx.get('SAFRA', 33)
    idx_cid = h_idx.get('NM_CIDADE', 28)
    idx_uf = h_idx.get('UF', 122)
    idx_canal_g = h_idx.get('NM_CANAL_VENDA_GRUPO', 22)
    idx_canal_s = h_idx.get('NM_CANAL_VENDA_SUBGRUPO', 21)
    idx_parceiro = h_idx.get('NM_PARCEIRO', 26)
    idx_vendedor = h_idx.get('NM_VENDEDOR', 24)
    idx_pag = h_idx.get('NM_FORMA_PAGAMENTO', 17)
    idx_prod = h_idx.get('NM_TIPO_ASS_DOMICILIO', 16)
    idx_marca = h_idx.get('NM_MARCA', 13)
    idx_perfil = h_idx.get('NM_PERFIL_CLIENTE', 14)
    idx_risco = h_idx.get('FXRISCO', 104)

    idx_ag30 = h_idx.get('AGING30', 129)
    idx_ag60 = h_idx.get('AGING60', 130)
    idx_ag90 = h_idx.get('AGING90', 131)
    idx_ag120 = h_idx.get('AGING120', 132)
    idx_ag150 = h_idx.get('AGING150', 133)
    idx_ag180 = h_idx.get('AGING180', 134)
    idx_over90 = h_idx.get('OVER90', 128)

    count = 0
    for row in r:
        count += 1
        ctr_str = row[idx_ctr].strip() if idx_ctr < len(row) else ''
        try:
            ctr_num = int(ctr_str)
        except:
            ctr_num = count

        s_raw = row[idx_safra].strip() if idx_safra < len(row) else ''
        safra_str = safra_nome.get(s_raw, 'jan/26')

        cid_raw = row[idx_cid].strip() if idx_cid < len(row) else 'Não Informado'
        cid_upper = cid_raw.upper().replace('BELEM', 'BELÉM').replace('SAO LUIS', 'SÃO LUÍS').replace('MARABA', 'MARABÁ').replace('MACAPA', 'MACAPÁ')

        uf_str = row[idx_uf].strip() if idx_uf < len(row) else ''
        if not uf_str:
            if 'AM' in cid_upper or 'MANAUS' in cid_upper: uf_str = 'AM'
            elif 'MA' in cid_upper or 'LUÍS' in cid_upper or 'IMPERATRIZ' in cid_upper: uf_str = 'MA'
            elif 'AP' in cid_upper or 'MACAPÁ' in cid_upper: uf_str = 'AP'
            else: uf_str = 'PA'

        geo_info = geocod.get(ctr_str, {})
        bairro_str = geo_info.get('b') or cid_upper.title()
        node_str = geo_info.get('n') or 'Não Informado'
        porte_str = geo_info.get('porte') or porte_por_cidade.get(cid_upper, 'Demais Mercados')
        if porte_str not in ['Grandes', 'Desenvolvimento', 'Demais Mercados', 'Outros']:
            porte_str = porte_por_cidade.get(cid_upper, 'Demais Mercados')
        if porte_str == 'Demais Mercados':
            porte_str = 'Outros'

        cabo_str = geo_info.get('cabo') or 'Com Cabo'
        ddd_str = geo_info.get('ddd') or ddd_por_cidade.get(cid_upper, '91')

        canal_g_str = row[idx_canal_g].strip() if idx_canal_g < len(row) else 'Não Informado'
        canal_s_str = row[idx_canal_s].strip() if idx_canal_s < len(row) else 'Não Informado'
        parc_str = row[idx_parceiro].strip() if idx_parceiro < len(row) else 'Não Informado'
        vend_str = row[idx_vendedor].strip() if idx_vendedor < len(row) else 'Não Informado'
        pag_str = row[idx_pag].strip() if idx_pag < len(row) else 'Boleto'
        prod_str = row[idx_prod].strip() if idx_prod < len(row) else 'Dados'
        marca_str = row[idx_marca].strip() if idx_marca < len(row) else 'NET'
        perfil_str = row[idx_perfil].strip() if idx_perfil < len(row) else 'Prospect'
        risco_str = row[idx_risco].strip() if idx_risco < len(row) else 'Médio'
        if not risco_str or risco_str == '.': risco_str = 'Médio'

        # Aging e Buckets
        a30 = 1 if (idx_ag30 < len(row) and row[idx_ag30] == '1') else 0
        a60 = 1 if (idx_ag60 < len(row) and row[idx_ag60] == '1') else 0
        a90 = 1 if (idx_ag90 < len(row) and row[idx_ag90] == '1') else 0
        a120 = 1 if (idx_ag120 < len(row) and row[idx_ag120] == '1') else 0
        a150 = 1 if (idx_ag150 < len(row) and row[idx_ag150] == '1') else 0
        a180 = 1 if (idx_ag180 < len(row) and row[idx_ag180] == '1') else 0
        ov90 = 1 if (idx_over90 < len(row) and row[idx_over90] == '1') else 0

        # abk: 1=D30, 2=D60, 3=D90, 4=D120, 5=D150, 0=ativo/adimplente
        if a30: abk = 1
        elif a60: abk = 2
        elif a90: abk = 3
        elif a120: abk = 4
        elif a150 or a180: abk = 5
        else: abk = 0

        # pbk: 0 se nunca pagou (a30 e a60), 1 se pagou
        if a30 and a60: pbk = 0
        else: pbk = 1

        # tpk: Motivo / Classificação de Risco (1=Inadimplência, 2=Opção, 3=Fraude)
        if 'Alt' in risco_str or 'Alto' in risco_str: tpk = 1
        elif 'Fraude' in risco_str: tpk = 3
        else: tpk = 2

        # Data e dia de instalação
        dt_str = row[idx_dt_inst].strip() if idx_dt_inst < len(row) else ''
        dia_inst = 1
        if dt_str and '/' in dt_str:
            try:
                dia_inst = int(dt_str.split('/')[0])
                if dia_inst < 1 or dia_inst > 31: dia_inst = 1
            except:
                dia_inst = 1

        aging_val = 60 if a60 else (30 if a30 else (90 if a90 else 0))

        # Coordenadas
        lat_s = geo_info.get('lat')
        lon_s = geo_info.get('lon')
        if lat_s and lon_s:
            try:
                lat_f = float(lat_s.replace(',', '.'))
                lon_f = float(lon_s.replace(',', '.'))
            except:
                lat_f, lon_f = -3.1190, -60.0217
        else:
            lat_f, lon_f = -3.1190, -60.0217

        lats.append(lat_f)
        lons.append(lon_f)

        # Adicionar códigos aos vetores
        cols_data['safra'].append(get_code('safra', safra_str))
        cols_data['uf'].append(get_code('uf', uf_str))
        cols_data['tipo_cidade'].append(get_code('tipo_cidade', cabo_str))
        cols_data['porte'].append(get_code('porte', porte_str))
        cols_data['ddd'].append(get_code('ddd', ddd_str))
        cols_data['canal_grupo'].append(get_code('canal_grupo', canal_g_str))
        cols_data['canal_sub'].append(get_code('canal_sub', canal_s_str))
        cols_data['produto'].append(get_code('produto', prod_str))
        cols_data['marca'].append(get_code('marca', marca_str))
        cols_data['perfil'].append(get_code('perfil', perfil_str))
        cols_data['pagto'].append(get_code('pagto', pag_str))
        cols_data['visao'].append(get_code('visao', 'Assinatura'))
        cols_data['motivo'].append(get_code('motivo', 'Inadimplência' if a60 else 'Sem Desconexão'))

        # Estrutura comercial (padrão Claro / RNO)
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

print(f"Total de registros processados: {count:,}")

# Bounding Box e Normalização Web Mercator
min_lat = min(lats)
max_lat = max(lats)
min_lon = min(lons)
max_lon = max(lons)
bbox = [min_lat, max_lat, min_lon, max_lon]
print(f"BBOX: {bbox}")

lat_d = max_lat - min_lat if max_lat > min_lat else 1.0
lon_d = max_lon - min_lon if max_lon > min_lon else 1.0

gx = [int(round((lon - min_lon) / lon_d * 65534)) for lon in lons]
gy = [int(round((lat - min_lat) / lat_d * 65534)) for lat in lats]

# Centroides de Bairros (bmx, bmy, bmn)
bairro_pts = {}
for i in range(count):
    b_idx = cols_data['bairro'][i]
    if b_idx not in bairro_pts:
        bairro_pts[b_idx] = []
    if len(bairro_pts[b_idx]) < 100:
        bairro_pts[b_idx].append((gx[i], gy[i]))

nb_bairros = len(dicts['bairro'])
bmx = [0] * nb_bairros
bmy = [0] * nb_bairros
bmn = [0] * nb_bairros

for b_idx, pts in bairro_pts.items():
    if b_idx < nb_bairros:
        bmx[b_idx] = int(round(sum(p[0] for p in pts) / len(pts)))
        bmy[b_idx] = int(round(sum(p[1] for p in pts) / len(pts)))
        bmn[b_idx] = min(len(pts), 255)

print("\n=== 3. Compactando Colunas em ZLIB + Base64 ===")

def pack_and_compress(arr, dtype):
    if dtype == 'u8':
        raw_bytes = bytearray(arr)
    elif dtype == 'u16':
        raw_bytes = bytearray()
        for v in arr:
            raw_bytes.extend(int(v).to_bytes(2, byteorder='little', signed=False))
    elif dtype == 'u32':
        raw_bytes = bytearray()
        for v in arr:
            raw_bytes.extend(int(v).to_bytes(4, byteorder='little', signed=False))
    
    comp = zlib.compress(raw_bytes, level=9)
    b64 = base64.b64encode(comp).decode('ascii')
    return {'t': dtype, 'b': b64}

compressed_cols = {}
for k, arr in cols_data.items():
    if k in ['cidade', 'bairro', 'node', 'parceiro', 'empresa', 'vendedor', 'canal_sub']:
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
print(f"Payload JSON completo gerado: {len(payload_json_str):,} caracteres.")

print("\n=== 4. Lendo Molde Original Painel_Churn_Safra 28.html ===")
with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Substituir PAYLOAD
p_start = template.find('const PAYLOAD = ')
p_end = template.find('/* ============ decodificação ============ */')
if p_start == -1 or p_end == -1:
    raise Exception("Não foi possível encontrar a declaração do PAYLOAD no molde!")

print("Substituindo PAYLOAD...")
new_html = template[:p_start + len('const PAYLOAD = ')] + payload_json_str + ';\n\n' + template[p_end:]

# Substituir Cabeçalho e Títulos
new_html = new_html.replace(
    '<h1><b>Churn Safra</b> <span>Regional Norte</span></h1>',
    '<h1><b>FPD — First Payment Default</b> <span>Regional Norte</span></h1>'
)
new_html = new_html.replace(
    '<title>Painel Churn Safra — Regional Norte</title>',
    '<title>Painel FPD — First Payment Default · Regional Norte | Pephub</title>'
)
new_html = new_html.replace(
    '<span><b>13 safras</b> · set/2025 a set/2026</span>',
    '<span><b>5 safras</b> · jan/2026 a mai/2026</span>'
)
new_html = new_html.replace(
    'Janela de apuração <b>120 dias</b>',
    'Janela oficial <b>FPD 60 (1ª fatura cheia)</b>'
)
new_html = new_html.replace(
    'Posição <b>21/09/2026</b>',
    'Posição <b>01/06/2026</b>'
)
new_html = new_html.replace(
    'Descompactando base (348.866 instalações)…',
    f'Descompactando base FPD ({count:,} instalações)…'
)

# Ajustar safras ordenadas no JS
old_safra_ord = "const SAFRA_ORD=['set/25','out/25','nov/25','dez/25','jan/26','fev/26','mar/26','abr/26','mai/26','jun/26','jul/26','ago/26','set/26'];"
new_safra_ord = "const SAFRA_ORD=['jan/26','fev/26','mar/26','abr/26','mai/26'];"
new_html = new_html.replace(old_safra_ord, new_safra_ord)

old_matur = "const MATUR={'set/25':356,'out/25':325,'nov/25':295,'dez/25':264,'jan/26':233,'fev/26':205,'mar/26':174,'abr/26':144,'mai/26':113,'jun/26':83,'jul/26':52,'ago/26':21,'set/26':1};"
new_matur = "const MATUR={'jan/26':151,'fev/26':120,'mar/26':92,'abr/26':61,'mai/26':31};"
new_html = new_html.replace(old_matur, new_matur)

# No FPD, a janela oficial é 60 dias (FPD 60 / 1ª fatura cheia)
new_html = new_html.replace("const JANELA=120;", "const JANELA=60;")
new_html = new_html.replace("const POS_Y=2026,POS_M=9,POS_D=20;", "const POS_Y=2026,POS_M=6,POS_D=1;")

# Substituir textos dos KPIs
new_html = new_html.replace("card('Churn Safra D120',pct(f.c[3],f.inst,2),`${fmt(f.c[3])} desconexões · ${base}`,'acc')",
                            "card('Taxa FPD 60 (Oficial)',pct(f.c[1],f.inst,2),`${fmt(f.c[1])} contratos na 1ª fatura cheia`,'acc')")
new_html = new_html.replace("card('Churn D30',pct(f.c[0],f.inst,2),`${fmt(f.c[0])} desconexões precoces`)",
                            "card('Taxa FPD 30 (Pró-rata)',pct(f.c[0],f.inst,2),`${fmt(f.c[0])} contratos pró-rata precoces`,'np')")
new_html = new_html.replace("card('Churn D90',pct(f.c[2],f.inst,2),`${fmt(f.c[2])} desconexões`)",
                            "card('Adimplência 1ª Fatura',pct(f.inst-f.c[1],f.inst,2),`${fmt(f.inst-f.c[1])} contratos em dia`,'fe')")
new_html = new_html.replace("card('Nunca pagou D120',pct(f.np[3],f.inst,2),`${fmt(f.np[3])} contratos sem pagamento`,'np')",
                            "card('Nunca Pagou (FPD 30 & 60)',pct(f.np[1],f.inst,2),`${fmt(f.np[1])} contratos sem nenhum pagamento`,'np')")
new_html = new_html.replace("card('Churn sem pagamento',pct(semPg,f.inst,2),`${pct(semPg,f.c[3])} de todo o churn D120`,'np')",
                            "card('Inadimplência Crônica (90d+)',pct(f.c[2],f.inst,2),`${fmt(f.c[2])} contratos com 90d+ atraso`,'acc')")

# Substituir títulos das seções
new_html = new_html.replace("<h2>Churn safra por safra", "<h2>Evolução do FPD por safra")
new_html = new_html.replace("% churn D120", "% FPD 60 (Oficial)")
new_html = new_html.replace("% nunca pagou D120", "% FPD 30 (Pró-rata)")
new_html = new_html.replace("<h2>Matriz de safra — responsabilidade do parceiro", "<h2>Matriz de safra — evolução de aging")
new_html = new_html.replace("M1 = 30d · M4 = 120d (limite do parceiro) · M5 = 150d", "M1 = 30d (pró-rata) · M2 = 60d (FPD oficial) · M3 = 90d · M4 = 120d · M5 = 150d")

print("\n=== 5. Salvando Arquivos ===")
# 1. Na raiz
with open('Painel_FPD_Regional_Norte.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print(f"Salvo Painel_FPD_Regional_Norte.html ({len(new_html):,} bytes).")

# 2. No public/fpd/index.html
os.makedirs('public/fpd', exist_ok=True)
with open('public/fpd/index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Salvo public/fpd/index.html com sucesso!")

# 3. No public/fpd/Painel_FPD_Regional_Norte.html para download
with open('public/fpd/Painel_FPD_Regional_Norte.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("Salvo public/fpd/Painel_FPD_Regional_Norte.html com sucesso!")

print("\nProcesso concluído com 100% de sucesso!")
