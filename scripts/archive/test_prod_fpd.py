import csv

prod_agg = {}
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = [c.strip().replace('"', '').upper() for c in next(r)]
    p_idx = h.index('NM_TIPO_ASS_DOMICILIO')
    ag30_idx = h.index('AGING30')
    ag60_idx = h.index('AGING60')
    
    for row in r:
        if len(row) > p_idx:
            prod = row[p_idx].strip().replace('"', '')
            if not prod: prod = 'Não Informado'
            if prod not in prod_agg:
                prod_agg[prod] = {'inst': 0, 'c30': 0, 'c60': 0}
            prod_agg[prod]['inst'] += 1
            if len(row) > ag30_idx and row[ag30_idx].strip().replace('"', '') == '1':
                prod_agg[prod]['c30'] += 1
            if len(row) > ag60_idx and row[ag60_idx].strip().replace('"', '') == '1':
                prod_agg[prod]['c60'] += 1

print(f"{'Produto':<25} | {'Instalações':<12} | {'FPD 60':<8} | {'% FPD 60':<10} | {'FPD 30':<8} | {'% FPD 30':<10}")
print("-" * 85)
for prod, d in sorted(prod_agg.items(), key=lambda x: x[1]['inst'], reverse=True):
    p60 = d['c60'] / d['inst'] * 100
    p30 = d['c30'] / d['inst'] * 100
    print(f"{prod:<25} | {d['inst']:<12,d} | {d['c60']:<8,d} | {p60:<9.2f}% | {d['c30']:<8,d} | {p30:<9.2f}%")
