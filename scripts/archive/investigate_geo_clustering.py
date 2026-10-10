import csv
from collections import Counter

# 1. Analisar como as coordenadas foram atribuídas
ctr_geo = {}
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name.strip().upper(): i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO', 14)
    lat_idx = h_idx.get('LAT_FINAL(FALLBACK_2)', 68)
    lon_idx = h_idx.get('LONG_FINAL(FALLBACK_2)', 69)
    status_idx = h_idx.get('STATUS_CONTRATO', 61)
    
    for row in r:
        ctr = row[c_idx].strip() if c_idx < len(row) else ''
        if ctr and ctr not in ctr_geo:
            ctr_geo[ctr] = {
                'lat': row[lat_idx].strip() if lat_idx < len(row) else '',
                'lon': row[lon_idx].strip() if lon_idx < len(row) else '',
            }

coords_count = Counter()
missing_geo = 0
total = 0
cities_missing = Counter()

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name.strip().upper(): i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO')
    cid_idx = h_idx.get('NM_CIDADE')
    
    for row in r:
        if not row or not any(row): continue
        total += 1
        ctr = row[c_idx].strip()
        cid = row[cid_idx].strip()
        
        g = ctr_geo.get(ctr)
        if g and g['lat'] and g['lon']:
            lat = g['lat']
            lon = g['lon']
            coords_count[(lat, lon, cid)] += 1
        else:
            missing_geo += 1
            cities_missing[cid] += 1

print(f"Total contratos FPD: {total:,}")
print(f"Sem geocod (caíram no fallback fixo): {missing_geo:,} ({missing_geo/total*100:.1f}%)")
print(f"Cidades com contratos sem geocod:")
for cid, cnt in cities_missing.most_common(10):
    print(f"  {cid}: {cnt:,}")

print(f"\nTotal de pares de coordenadas únicas: {len(coords_count):,}")
print("\nTop 15 coordenadas mais repetidas (agrupamentos massivos):")
for (lat, lon, cid), cnt in coords_count.most_common(15):
    print(f"  Coord: ({lat}, {lon}) em {cid} -> {cnt:,} contratos empilhados exatamente no mesmo ponto ({cnt/total*100:.2f}%)")
