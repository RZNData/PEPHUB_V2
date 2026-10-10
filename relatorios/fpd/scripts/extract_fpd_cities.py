import csv
from collections import Counter

cities = Counter()
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_clean = [col.strip().replace('"', '').upper() for col in h]
    cid_idx = h_clean.index('NM_CIDADE')
    uf_idx = h_clean.index('UF')
    for row in r:
        if not row: continue
        cities[(row[cid_idx].strip(), row[uf_idx].strip())] += 1

print(f"Total de cidades no FPD: {len(cities)}")
for (cid, uf), cnt in cities.most_common(40):
    print(f"  ('{cid}', '{uf}'): {cnt:,}")
