import csv

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_clean = [col.strip().replace('"', '').upper() for col in h]
    
    print(f"Total de colunas no CSV: {len(h)}")
    
    targets = ['FX_RISCO_NV', 'FXULTSCORE', 'PORTFOLIO_TV', 'SAFRA', 'CEP', 'CIDADE']
    for t in targets:
        matches = [(i, h[i]) for i, name in enumerate(h_clean) if t in name]
        print(f"Alvo '{t}': {matches}")
