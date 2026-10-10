import csv
from collections import Counter

# 1. Checar CD_NODE em Base_Churn_Geocod_v3_FALLBACK_CEP.csv
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = f.readline().split(';')
    h_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h)}
    node_idx = h_idx.get('CD_NODE')
    print('CD_NODE index:', node_idx)
    
    nodes_geocod = Counter()
    for _ in range(5000):
        row = f.readline().split(';')
        if node_idx is not None and len(row) > node_idx:
            nodes_geocod[row[node_idx].strip()] += 1

print('Top nodes em Base_Churn_Geocod (CD_NODE):', nodes_geocod.most_common(10))

# 2. Em FPD_JAN_MAI_26.csv, verificar se há alguma coluna com códigos de node, log, rede, ponto etc.
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = [col.strip().replace('"', '').upper() for col in f.readline().split(';')]
    row = f.readline().split(';')
    for i, col in enumerate(h):
        val = row[i].strip().replace('"', '') if i < len(row) else ''
        if any(w in col for w in ['COD', 'REDE', 'PONTO', 'LOG', 'GPON', 'CIDADE', 'MUNIC']):
            print(f'{col}: {val}')
