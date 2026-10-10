import csv
import json
import zlib
import base64
import re
import os

print("=== 1. Carregando Centróides e Coordenadas de Cidades e Contratos ===")
contrato_coords = {}
city_coords_accum = {}

with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    idx_c = h_idx.get('NR_CONTRATO', 14)
    idx_cid = h_idx.get('CIDADE', 3)
    idx_lat = h_idx.get('LAT_FINAL(FALLBACK_2)', 68)
    idx_lon = h_idx.get('LONG_FINAL(FALLBACK_2)', 69)
    
    line_cnt = 0
    for row in reader:
        line_cnt += 1
        lat = row[idx_lat] if idx_lat < len(row) else ""
        lon = row[idx_lon] if idx_lon < len(row) else ""
        cid = row[idx_cid].upper().strip() if idx_cid < len(row) else ""
        c = row[idx_c].strip() if idx_c < len(row) else ""
        
        if lat and lon:
            try:
                lat_f = float(lat.replace(',', '.'))
                lon_f = float(lon.replace(',', '.'))
                if -15 < lat_f < 6 and -75 < lon_f < -35: # Bounding box Brasil Norte
                    if c and c not in contrato_coords:
                        contrato_coords[c] = (lat_f, lon_f)
                    if cid:
                        if cid not in city_coords_accum:
                            city_coords_accum[cid] = []
                        if len(city_coords_accum[cid]) < 200:
                            city_coords_accum[cid].append((lat_f, lon_f))
            except:
                pass

city_centroids = {}
for cid, pts in city_coords_accum.items():
    city_centroids[cid] = (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

# Centróides padrões para cidades chave da Regional Norte caso não estejam no dicionário
default_cities = {
    'MANAUS': (-3.1190, -60.0217),
    'BELEM': (-1.4558, -48.4902),
    'BELÉM': (-1.4558, -48.4902),
    'SAO LUIS': (-2.5391, -44.2828),
    'SÃO LUÍS': (-2.5391, -44.2828),
    'MACAPA': (0.0389, -51.0664),
    'MACAPÁ': (0.0389, -51.0664),
    'IMPERATRIZ': (-5.5266, -47.4777),
    'CASTANHAL': (-1.2981, -47.9248),
    'PARAUAPEBAS': (-6.0678, -49.9075),
    'MARABA': (-5.3686, -49.1174),
    'MARABÁ': (-5.3686, -49.1174),
    'ANANINDEUA': (-1.3656, -48.3744),
    'SANTANA': (-0.0583, -51.1764),
    'BOA VISTA': (2.8235, -60.6758),
    'ABAETETUBA': (-1.7218, -48.8833),
    'BARCARENA': (-1.5058, -48.6186),
    'TIMON': (-5.0939, -42.8369),
    'SANTA INES': (-3.6667, -45.3800),
    'CAXIAS': (-4.8589, -43.3561)
}
for c, pt in default_cities.items():
    if c not in city_centroids:
        city_centroids[c] = pt

print(f"Coordenadas de contratos carregadas: {len(contrato_coords):,}")
print(f"Cidades com centróides: {len(city_centroids)}")

print("\n=== 2. Lendo e Estruturando Base FPD ===")
dicts = {
    'safra': [],
    'uf': [],
    'cidade': [],
    'canal_grupo': [],
    'canal_sub': [],
    'parceiro': [],
    'vendedor': [],
    'pagto': [],
    'risco': [],
    'produto': []
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

col_safra = []
col_uf = []
col_cidade = []
col_canal_grupo = []
col_canal_sub = []
col_parceiro = []
col_vendedor = []
col_vendedor_cpf = [] # texto ou indice
col_pagto = []
col_risco = []
col_produto = []

col_ag30 = []
col_ag60 = []
col_ag90 = []
col_ag120 = []
col_ag150 = []
col_ag180 = []
col_over90 = []

col_lat = []
col_lon = []

# Mapeamento de UFs das cidades
cid_to_uf = {
    'MANAUS': 'AM', 'BELEM': 'PA', 'BELÉM': 'PA', 'SAO LUIS': 'MA', 'SÃO LUÍS': 'MA',
    'MACAPA': 'AP', 'MACAPÁ': 'AP', 'IMPERATRIZ': 'MA', 'CASTANHAL': 'PA',
    'PARAUAPEBAS': 'PA', 'MARABA': 'PA', 'MARABÁ': 'PA', 'ANANINDEUA': 'PA',
    'SANTANA': 'AP', 'BOA VISTA': 'RR', 'ABAETETUBA': 'PA', 'BARCARENA': 'PA',
    'TIMON': 'MA', 'SANTA INES': 'MA', 'CAXIAS': 'MA', 'ITAITUBA': 'PA',
    'ALTAMIRA': 'PA', 'PARINTINS': 'AM', 'ITACOATIARA': 'AM', 'TUCURUI': 'PA'
}

safra_map = {
    '202601': 'Jan/26',
    '202602': 'Fev/26',
    '202603': 'Mar/26',
    '202604': 'Abr/26',
    '202605': 'Mai/26'
}

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    
    idx_contrato = h_idx.get('NR_CONTRATO', 4)
    idx_safra = h_idx.get('SAFRA', 33)
    idx_cid = h_idx.get('NM_CIDADE', 28)
    idx_uf = h_idx.get('UF', 122)
    idx_parceiro = h_idx.get('NM_PARCEIRO', 26)
    idx_vendedor = h_idx.get('NM_VENDEDOR', 24)
    idx_cpf = h_idx.get('NR_CPF_CNPJ_VENDEDOR', 23)
    idx_canal = h_idx.get('NM_CANAL_VENDA_GRUPO', 22)
    idx_sub = h_idx.get('NM_CANAL_VENDA_SUBGRUPO', 21)
    idx_prod = h_idx.get('NM_TIPO_ASS_DOMICILIO', 16)
    idx_pag = h_idx.get('NM_FORMA_PAGAMENTO', 17)
    idx_risco = h_idx.get('FXRISCO', 104)
    
    idx_ag30 = h_idx.get('AGING30', 129)
    idx_ag60 = h_idx.get('AGING60', 130)
    idx_ag90 = h_idx.get('AGING90', 131)
    idx_ag120 = h_idx.get('AGING120', 132)
    idx_ag150 = h_idx.get('AGING150', 133)
    idx_ag180 = h_idx.get('AGING180', 134)
    idx_over90 = h_idx.get('OVER90', 128)

    row_count = 0
    for row in reader:
        row_count += 1
        contrato = row[idx_contrato].strip() if idx_contrato < len(row) else ""
        s_raw = row[idx_safra].strip() if idx_safra < len(row) else ""
        s_label = safra_map.get(s_raw, s_raw or "Outros")
        
        cid_raw = row[idx_cid].strip() if idx_cid < len(row) else ""
        cid_clean = cid_raw.upper().replace("BELEM", "BELÉM").replace("SAO LUIS", "SÃO LUÍS").replace("MARABA", "MARABÁ").replace("MACAPA", "MACAPÁ")
        
        uf_raw = row[idx_uf].strip() if idx_uf < len(row) else ""
        if not uf_raw:
            uf_raw = cid_to_uf.get(cid_clean.replace("BELÉM", "BELEM").replace("SÃO LUÍS", "SAO LUIS").replace("MARABÁ", "MARABA").replace("MACAPÁ", "MACAPA"), "PA")

        parc = row[idx_parceiro].strip() if idx_parceiro < len(row) else "Não Informado"
        vend = row[idx_vendedor].strip() if idx_vendedor < len(row) else "Não Informado"
        cpf_vend = row[idx_cpf].strip() if idx_cpf < len(row) else ""
        canal = row[idx_canal].strip() if idx_canal < len(row) else "Não Informado"
        sub = row[idx_sub].strip() if idx_sub < len(row) else "Não Informado"
        prod = row[idx_prod].strip() if idx_prod < len(row) else "Dados"
        pag = row[idx_pag].strip() if idx_pag < len(row) else "Boleto"
        risco = row[idx_risco].strip() if idx_risco < len(row) else "Médio"
        if not risco or risco == '.':
            risco = "Não Informado"

        # Coordenadas
        pt = contrato_coords.get(contrato)
        if not pt:
            pt = city_centroids.get(cid_clean.replace("BELÉM", "BELEM").replace("SÃO LUÍS", "SAO LUIS").replace("MARABÁ", "MARABA").replace("MACAPÁ", "MACAPA"), (-2.5, -50.0))
        
        # Inadimplencia
        a30 = 1 if (idx_ag30 < len(row) and row[idx_ag30] == '1') else 0
        a60 = 1 if (idx_ag60 < len(row) and row[idx_ag60] == '1') else 0
        a90 = 1 if (idx_ag90 < len(row) and row[idx_ag90] == '1') else 0
        a120 = 1 if (idx_ag120 < len(row) and row[idx_ag120] == '1') else 0
        a150 = 1 if (idx_ag150 < len(row) and row[idx_ag150] == '1') else 0
        a180 = 1 if (idx_ag180 < len(row) and row[idx_ag180] == '1') else 0
        ov90 = 1 if (idx_over90 < len(row) and row[idx_over90] == '1') else 0

        col_safra.append(get_code('safra', s_label))
        col_uf.append(get_code('uf', uf_raw))
        col_cidade.append(get_code('cidade', cid_clean.title()))
        col_canal_grupo.append(get_code('canal_grupo', canal))
        col_canal_sub.append(get_code('canal_sub', sub))
        col_parceiro.append(get_code('parceiro', parc))
        col_vendedor.append(get_code('vendedor', vend))
        col_vendedor_cpf.append(cpf_vend)
        col_pagto.append(get_code('pagto', pag))
        col_risco.append(get_code('risco', risco))
        col_produto.append(get_code('produto', prod))

        col_ag30.append(a30)
        col_ag60.append(a60)
        col_ag90.append(a90)
        col_ag120.append(a120)
        col_ag150.append(a150)
        col_ag180.append(a180)
        col_over90.append(ov90)

        col_lat.append(pt[0])
        col_lon.append(pt[1])

print(f"Total processado: {row_count:,} registros")
print("Tamanho dos dicionários:")
for k, v in dicts.items():
    print(f"  {k}: {len(v)} itens")

# Calcular Bounding Box
min_lat = min(col_lat)
max_lat = max(col_lat)
min_lon = min(col_lon)
max_lon = max(col_lon)
bbox = [min_lat, max_lat, min_lon, max_lon]
print(f"BBOX: {bbox}")

# Mapear coordenadas para Uint16 (0 a 65534)
lat_d = max_lat - min_lat if max_lat > min_lat else 1.0
lon_d = max_lon - min_lon if max_lon > min_lon else 1.0
gx = [int(round((lon - min_lon) / lon_d * 65534)) for lon in col_lon]
gy = [int(round((lat - min_lat) / lat_d * 65534)) for lat in col_lat]

print("Compactando colunas...")
def compress_u8(arr):
    b = bytes(arr)
    comp = zlib.compress(b, level=9)
    return {'t': 'u8', 'b': base64.b64encode(comp).decode('ascii')}

def compress_u16(arr):
    import struct
    b = struct.pack(f'<{len(arr)}H', *arr)
    comp = zlib.compress(b, level=9)
    return {'t': 'u16', 'b': base64.b64encode(comp).decode('ascii')}

payload_cols = {
    'safra': compress_u8(col_safra),
    'uf': compress_u8(col_uf),
    'cidade': compress_u16(col_cidade),
    'canal': compress_u8(col_canal_grupo),
    'canal_sub': compress_u16(col_canal_sub),
    'parceiro': compress_u16(col_parceiro),
    'vendedor': compress_u16(col_vendedor),
    'pagto': compress_u8(col_pagto),
    'risco': compress_u8(col_risco),
    'produto': compress_u8(col_produto),
    'ag30': compress_u8(col_ag30),
    'ag60': compress_u8(col_ag60),
    'ag90': compress_u8(col_ag90),
    'ag120': compress_u8(col_ag120),
    'ag150': compress_u8(col_ag150),
    'ag180': compress_u8(col_ag180),
    'over90': compress_u8(col_over90),
    'gx': compress_u16(gx),
    'gy': compress_u16(gy)
}

payload = {
    'n': row_count,
    'dicts': dicts,
    'bbox': bbox,
    'cols': payload_cols
}

out_json = json.dumps(payload)
print(f"Tamanho do payload JSON gerado: {len(out_json):,} bytes ({len(out_json)/(1024*1024):.2f} MB)")

with open('public/fpd_payload.json', 'w', encoding='utf-8') as f:
    f.write(out_json)
print("Salvo em public/fpd_payload.json com sucesso!")
