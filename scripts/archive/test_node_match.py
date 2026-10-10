import csv
from collections import Counter

# Carregar lookup de contratos para CD_NODE
node_lookup = {}
bairro_lookup = {}
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = f.readline().split(';')
    h_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO')
    node_idx = h_idx.get('CD_NODE')
    bairro_idx = h_idx.get('BAIRRO')
    
    for row in f:
        parts = row.split(';')
        if len(parts) > c_idx:
            ctr = parts[c_idx].strip()
            if ctr and ctr not in node_lookup:
                nd = parts[node_idx].strip() if node_idx is not None and len(parts) > node_idx else ''
                br = parts[bairro_idx].strip() if bairro_idx is not None and len(parts) > bairro_idx else ''
                node_lookup[ctr] = nd
                bairro_lookup[ctr] = br

print(f'Total contratos no lookup: {len(node_lookup):,}')

# Checar quantos dos 53.972 contratos de FPD possuem match de CD_NODE
matched = 0
unmatched = 0
node_counts = Counter()
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = f.readline().split(';')
    h_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h)}
    c_idx = h_idx.get('NR_CONTRATO')
    
    for row in f:
        parts = row.split(';')
        if len(parts) > c_idx:
            ctr = parts[c_idx].strip().replace('"', '')
            if ctr in node_lookup:
                matched += 1
                nd = node_lookup[ctr]
                if nd: node_counts[nd] += 1
            else:
                unmatched += 1

print(f'FPD x Geocod Match: {matched:,} ({matched/(matched+unmatched)*100:.1f}%) | Sem match: {unmatched:,}')
print(f'Distintos nodes encontrados nos contratos de FPD: {len(node_counts):,}')
print('Top 15 nodes dos contratos de FPD:', node_counts.most_common(15))
