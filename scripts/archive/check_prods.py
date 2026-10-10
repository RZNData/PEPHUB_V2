import csv
from collections import Counter

prods = Counter()
visoes = Counter()
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = [c.strip().replace('"', '').upper() for c in next(r)]
    p_idx = h.index('NM_TIPO_ASS_DOMICILIO')
    v_idx = h.index('NM_VISAO_ANALISE')
    
    for row in r:
        if len(row) > p_idx:
            prods[row[p_idx].strip().replace('"', '')] += 1
        if len(row) > v_idx:
            visoes[row[v_idx].strip().replace('"', '')] += 1

print('Produtos (NM_TIPO_ASS_DOMICILIO):', prods)
print('Visoes (NM_VISAO_ANALISE):', visoes)
