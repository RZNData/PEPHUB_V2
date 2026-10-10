import csv
import json
from collections import Counter, defaultdict

print("Analisando FPD_JAN_MAI_26.csv completo...")

total = 0
safras = Counter()
cidades = Counter()
ufs = Counter()
parceiros = Counter()
vendedores = Counter()
canais = Counter()
produtos = Counter()
formas_pag = Counter()
faixas_risco = Counter()

# Contadores de inadimplência
fpd_stats_safra = defaultdict(lambda: {'total': 0, 'ag30': 0, 'ag60': 0, 'ag90': 0, 'ag120': 0, 'ag150': 0, 'ag180': 0, 'over90': 0})
fpd_stats_cidade = defaultdict(lambda: {'total': 0, 'ag30': 0, 'ag60': 0, 'ag90': 0})
fpd_stats_parceiro = defaultdict(lambda: {'total': 0, 'ag30': 0, 'ag60': 0, 'ag90': 0})

has_cep = False
has_lat = False
cep_col_name = None

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    
    # Checar colunas geográficas
    for h in headers:
        if 'CEP' in h.upper():
            has_cep = True
            cep_col_name = h
        if 'LAT' in h.upper() or 'COORD' in h.upper():
            has_lat = True

    idx_safra = h_idx.get('SAFRA', 33)
    idx_cid = h_idx.get('NM_CIDADE', 28)
    idx_uf = h_idx.get('UF', 122)
    idx_parceiro = h_idx.get('NM_PARCEIRO', 26)
    idx_vendedor = h_idx.get('NM_VENDEDOR', 24)
    idx_canal = h_idx.get('NM_CANAL_VENDA_GRUPO', 22)
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

    for row in reader:
        total += 1
        safra = row[idx_safra] if idx_safra < len(row) else ""
        cid = row[idx_cid] if idx_cid < len(row) else ""
        parceiro = row[idx_parceiro] if idx_parceiro < len(row) else ""
        vendedor = row[idx_vendedor] if idx_vendedor < len(row) else ""
        canal = row[idx_canal] if idx_canal < len(row) else ""
        prod = row[idx_prod] if idx_prod < len(row) else ""
        pag = row[idx_pag] if idx_pag < len(row) else ""
        risco = row[idx_risco] if idx_risco < len(row) else ""
        
        safras[safra] += 1
        cidades[cid] += 1
        parceiros[parceiro] += 1
        vendedores[vendedor] += 1
        canais[canal] += 1
        produtos[prod] += 1
        formas_pag[pag] += 1
        faixas_risco[risco] += 1

        is_ag30 = 1 if (idx_ag30 < len(row) and row[idx_ag30] == '1') else 0
        is_ag60 = 1 if (idx_ag60 < len(row) and row[idx_ag60] == '1') else 0
        is_ag90 = 1 if (idx_ag90 < len(row) and row[idx_ag90] == '1') else 0
        is_ag120 = 1 if (idx_ag120 < len(row) and row[idx_ag120] == '1') else 0
        is_ag150 = 1 if (idx_ag150 < len(row) and row[idx_ag150] == '1') else 0
        is_ag180 = 1 if (idx_ag180 < len(row) and row[idx_ag180] == '1') else 0
        is_over90 = 1 if (idx_over90 < len(row) and row[idx_over90] == '1') else 0

        # Stats por safra
        st = fpd_stats_safra[safra]
        st['total'] += 1
        st['ag30'] += is_ag30
        st['ag60'] += is_ag60
        st['ag90'] += is_ag90
        st['ag120'] += is_ag120
        st['ag150'] += is_ag150
        st['ag180'] += is_ag180
        st['over90'] += is_over90

        # Stats por cidade
        sc = fpd_stats_cidade[cid]
        sc['total'] += 1
        sc['ag30'] += is_ag30
        sc['ag60'] += is_ag60
        sc['ag90'] += is_ag90

        # Stats por parceiro
        sp = fpd_stats_parceiro[parceiro]
        sp['total'] += 1
        sp['ag30'] += is_ag30
        sp['ag60'] += is_ag60
        sp['ag90'] += is_ag90

print(f"\nTOTAL DE REGISTROS NA BASE FPD: {total:,}")
print(f"Possui coluna de CEP? {has_cep} ({cep_col_name})")
print(f"Possui coluna de Coordenadas Lat/Lon? {has_lat}")

print("\n--- SAFRAS & TAXAS FPD (AGING 30 vs AGING 60) ---")
for s in sorted(fpd_stats_safra.keys()):
    st = fpd_stats_safra[s]
    t = st['total']
    pct_30 = (st['ag30'] / t * 100) if t > 0 else 0
    pct_60 = (st['ag60'] / t * 100) if t > 0 else 0
    pct_90 = (st['ag90'] / t * 100) if t > 0 else 0
    print(f"Safra {s}: {t:,} contratos | FPD 30: {st['ag30']:,} ({pct_30:.2f}%) | FPD 60 (Oficial): {st['ag60']:,} ({pct_60:.2f}%) | Over90: {st['over90']:,} ({pct_90:.2f}%)")

print("\n--- TOP 10 CIDADES ---")
for c, cnt in cidades.most_common(10):
    sc = fpd_stats_cidade[c]
    pct_60 = (sc['ag60'] / cnt * 100) if cnt > 0 else 0
    print(f"• {c}: {cnt:,} inst | FPD 60: {sc['ag60']:,} ({pct_60:.2f}%)")

print("\n--- TOP 10 PARCEIROS ---")
for p, cnt in parceiros.most_common(10):
    sp = fpd_stats_parceiro[p]
    pct_60 = (sp['ag60'] / cnt * 100) if cnt > 0 else 0
    print(f"• {p}: {cnt:,} inst | FPD 60: {sp['ag60']:,} ({pct_60:.2f}%)")

print("\n--- CANAIS DE VENDA ---")
for c, cnt in canais.most_common():
    print(f"• {c}: {cnt:,}")

print("\n--- FORMAS DE PAGAMENTO ---")
for f, cnt in formas_pag.most_common():
    print(f"• {f}: {cnt:,}")

print("\n--- FAIXAS DE RISCO ---")
for r, cnt in faixas_risco.most_common():
    print(f"• {r}: {cnt:,}")
