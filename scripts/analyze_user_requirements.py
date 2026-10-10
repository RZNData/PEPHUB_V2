import csv
from collections import Counter

c_risco = Counter()
c_score = Counter()
c_tv = Counter()
c_safra = Counter()

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_clean = [col.strip().replace('"', '').upper() for col in h]
    
    idx_risco = h_clean.index('FX_RISCO_NV')
    idx_score = h_clean.index('FXULTSCORE')
    idx_tv = h_clean.index('PORTFOLIO_TV')
    idx_safra = h_clean.index('SAFRA')
    idx_a60 = h_clean.index('AGING60')
    idx_a30 = h_clean.index('AGING30')
    idx_ctr = h_clean.index('NR_CONTRATO')
    
    tot = 0
    # Guardar cruzamento de risco e score com FPD
    risco_fpd = {}
    score_fpd = {}
    tv_fpd = {}

    for row in r:
        if not row or not any(row): continue
        tot += 1
        r_val = row[idx_risco].strip() if idx_risco < len(row) else ''
        s_val = row[idx_score].strip() if idx_score < len(row) else ''
        t_val = row[idx_tv].strip() if idx_tv < len(row) else ''
        sf_val = row[idx_safra].strip() if idx_safra < len(row) else ''
        
        a60 = 1 if (idx_a60 < len(row) and row[idx_a60] == '1') else 0
        a30 = 1 if (idx_a30 < len(row) and row[idx_a30] == '1') else 0
        
        c_risco[r_val] += 1
        c_score[s_val] += 1
        c_tv[t_val] += 1
        c_safra[sf_val] += 1
        
        for d, v in [(risco_fpd, r_val), (score_fpd, s_val), (tv_fpd, t_val)]:
            if v not in d: d[v] = {'inst': 0, 'c60': 0, 'c30': 0}
            d[v]['inst'] += 1
            if a60: d[v]['c60'] += 1
            if a30: d[v]['c30'] += 1

print(f"Total de registros: {tot:,}")
print("\n--- DISTRIBUIÇÃO FX_RISCO_NV ---")
for k, v in c_risco.most_common():
    d = risco_fpd[k]
    tx60 = d['c60'] / d['inst'] * 100
    tx30 = d['c30'] / d['inst'] * 100
    print(f"  {repr(k)}: {v:,} ({v/tot*100:.1f}%) | FPD 60: {tx60:.2f}% | FPD 30: {tx30:.2f}%")

print("\n--- DISTRIBUIÇÃO FXULTSCORE ---")
for k, v in c_score.most_common():
    d = score_fpd[k]
    tx60 = d['c60'] / d['inst'] * 100
    tx30 = d['c30'] / d['inst'] * 100
    print(f"  {repr(k)}: {v:,} ({v/tot*100:.1f}%) | FPD 60: {tx60:.2f}% | FPD 30: {tx30:.2f}%")

print("\n--- DISTRIBUIÇÃO PORTFOLIO_TV ---")
for k, v in c_tv.most_common():
    d = tv_fpd[k]
    tx60 = d['c60'] / d['inst'] * 100
    tx30 = d['c30'] / d['inst'] * 100
    print(f"  {repr(k)}: {v:,} ({v/tot*100:.1f}%) | FPD 60: {tx60:.2f}% | FPD 30: {tx30:.2f}%")

print("\n--- SAFRAS PRESENTES ---")
for k, v in c_safra.most_common():
    print(f"  {k}: {v:,}")
