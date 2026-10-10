import csv

for filename in ['BASE_FPD_JUN25_JUN26.csv', 'FPD_JAN_MAI_26.csv']:
    print(f'=== Verificando {filename} ===')
    try:
        with open(filename, 'r', encoding='latin1', errors='ignore') as f:
            r = csv.reader(f, delimiter=';')
            header = next(r)
            h_idx = {h.strip().upper(): i for i, h in enumerate(header)}
            print('Colunas encontradas:', [c for c in ['SAFRA', 'AGING30', 'AGING60', 'AGING90', 'AGING120', 'AGING150', 'FX_RISCO_NV', 'FXULTSCORE', 'PORTFOLIO_TV', 'REGIONAL'] if c in h_idx])
            
            safras = {}
            tot = 0
            for row in r:
                tot += 1
                sf = row[h_idx['SAFRA']].strip() if 'SAFRA' in h_idx and h_idx['SAFRA'] < len(row) else 'N/A'
                reg = row[h_idx['REGIONAL']].strip() if 'REGIONAL' in h_idx and h_idx['REGIONAL'] < len(row) else 'N/A'
                if 'REGIONAL' in h_idx and reg != 'NORTE':
                    continue
                if sf not in safras:
                    safras[sf] = {'count': 0, 'ag30': 0, 'ag60': 0, 'ag90': 0, 'ag120': 0, 'ag150': 0}
                safras[sf]['count'] += 1
                for k in [30, 60, 90, 120, 150]:
                    col = f'AGING{k}'
                    if col in h_idx and h_idx[col] < len(row) and row[h_idx[col]].strip() in ('1', '1.0', 1):
                        safras[sf][f'ag{k}'] += 1
            norte_tot = sum(s['count'] for s in safras.values())
            print(f'Total linhas NORTE: {norte_tot} de {tot} totais')
            for sf in sorted(safras.keys()):
                s = safras[sf]
                c = s['count']
                print(f'  Safra {sf}: {c} inst | ag30={s["ag30"]} ({s["ag30"]/c*100:.1f}%) | ag60={s["ag60"]} ({s["ag60"]/c*100:.1f}%) | ag90={s["ag90"]} | ag120={s["ag120"]} | ag150={s["ag150"]}')
    except Exception as e:
        print('Erro:', e)
