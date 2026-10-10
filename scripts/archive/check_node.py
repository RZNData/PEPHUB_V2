import csv
from collections import Counter

# 1. Checar NODE em Base_Churn_Geocod_v3_FALLBACK_CEP.csv
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = f.readline().split(';')
    h_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h)}
    print('Colunas em Base_Churn_Geocod:', [k for k in h_idx if 'NODE' in k])
    node_idx = h_idx.get('NODE')
    
    nodes_geocod = Counter()
    for _ in range(5000):
        row = f.readline().split(';')
        if len(row) > node_idx:
            nodes_geocod[row[node_idx].strip()] += 1

print('Top nodes em Base_Churn_Geocod:', nodes_geocod.most_common(10))

# 2. Checar FPD_JAN_MAI_26.csv se existe algum outro campo
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    h2 = f.readline().split(';')
    h2_idx = {name.strip().replace('"', '').upper(): i for i, name in enumerate(h2)}
    
    # Amostrar 1000 contratos de FPD e ver o match de contrato com geocod
    ctrs_fpd = []
    for _ in range(1000):
        row = f.readline().split(';')
        if len(row) > 4:
            ctrs_fpd.append(row[4].strip().replace('"', ''))

print('\nExemplos de contratos em FPD:', ctrs_fpd[:10])

# Checar formatos em Base_Churn_Geocod
with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    h = f.readline().split(';')
    c_idx = 14 # NR_CONTRATO
    ctrs_geo = [f.readline().split(';')[c_idx].strip() for _ in range(10)]
    print('Exemplos de contratos em Geocod:', ctrs_geo)
