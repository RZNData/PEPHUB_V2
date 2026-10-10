import csv
from collections import Counter

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = [col.strip().replace('"', '').upper() for col in next(r)]
    h_idx = {name: i for i, name in enumerate(h)}
    
    print('Total de colunas:', len(h))
    
    # 1. Procurar colunas de Node, Visao, Domicilio, etc.
    for term in ['NODE', 'VISAO', 'DOMICILIO', 'PRODUTO', 'AGING', 'INAD', 'PAG', 'OVER', 'BASE', 'RECUSA']:
        matching = [col_name for col_name in h if term in col_name]
        print(f'Contem {term}:', matching)
        
    # Amostrar primeiros 10 registros
    rows = []
    for _ in range(1000):
        try:
            row = next(r)
            if row: rows.append(row)
        except StopIteration:
            break

print(f'\nAmostrados {len(rows)} registros.')

# Verificar valores das colunas chave
cols_to_check = [
    'NM_VISAO_ANALISE', 'NM_TIPO_ASS_DOMICILIO', 'PRODUTO_ATUAL', 'PRODUTO', 
    'PRODUTO_DADOS', 'AGING30', 'AGING60', 'AGING90', 'AGING120', 'OVER90',
    'FLAG_INAD_INT', 'INAD_INT', 'AGING_INAD_INT', 'BASE'
]

for col in cols_to_check:
    if col in h_idx:
        vals = Counter(r[h_idx[col]].strip() for r in rows)
        print(f'\nValores de {col}:', vals.most_common(10))
    else:
        print(f'\nColuna {col} NÃO encontrada.')
