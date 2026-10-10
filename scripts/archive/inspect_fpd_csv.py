import csv
from collections import Counter

reg_counter = Counter()
safra_counter = Counter()
total = 0

with open('BASE_FPD_JUN25_JUN26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    header = next(r)
    h_map = {col.strip('"'): i for i, col in enumerate(header)}
    reg_idx = h_map.get('NM_REGIONAL_CMV')
    safra_idx = h_map.get('SAFRA')
    
    for row in r:
        total += 1
        reg = row[reg_idx].strip('"').strip() if reg_idx is not None and reg_idx < len(row) else ''
        sf = row[safra_idx].strip('"').strip() if safra_idx is not None and safra_idx < len(row) else ''
        reg_counter[reg] += 1
        safra_counter[sf] += 1

print(f"Total rows: {total:,}")
print("Regionais:", dict(reg_counter))
print("Safras:", sorted(safra_counter.items()))
