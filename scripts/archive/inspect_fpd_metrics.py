import csv
from collections import Counter

print("=== DISTRIBUIÇÃO DAS MÉTRICAS NO CSV ===")
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    
    safras = Counter()
    ufs = Counter()
    cidades = Counter()
    indicadores = Counter()
    formas_pag = Counter()
    denominador_vals = Counter()
    base_vals = Counter()
    over90_vals = Counter()
    aging30_vals = Counter()
    flag_inad_vals = Counter()
    
    total_linhas = 0
    for row in reader:
        total_linhas += 1
        if total_linhas > 50000:
            break
        safras[row[h_idx.get('SAFRA', 33)]] += 1
        ufs[row[h_idx.get('UF', 122)]] += 1
        cidades[row[h_idx.get('NM_CIDADE', 28)]] += 1
        indicadores[row[h_idx.get('NM_INDICADOR_NEGOCIO', 12)]] += 1
        formas_pag[row[h_idx.get('NM_FORMA_PAGAMENTO', 17)]] += 1
        denominador_vals[row[h_idx.get('DENOMINADOR', 154)]] += 1
        base_vals[row[h_idx.get('BASE', 137)]] += 1
        aging30_vals[row[h_idx.get('AGING30', 129)]] += 1
        flag_inad_vals[row[h_idx.get('FLAG_INAD_INT', 116)]] += 1

print(f"Total amostrado: {total_linhas}")
print("\nSafras:", dict(safras.most_common(10)))
print("\nUFs:", dict(ufs.most_common(10)))
print("\nCidades:", dict(cidades.most_common(10)))
print("\nNM_INDICADOR_NEGOCIO:", dict(indicadores.most_common(10)))
print("\nNM_FORMA_PAGAMENTO:", dict(formas_pag.most_common(10)))
print("\nDENOMINADOR:", dict(denominador_vals.most_common(10)))
print("\nBASE:", dict(base_vals.most_common(10)))
print("\nAGING30:", dict(aging30_vals.most_common(10)))
print("\nFLAG_INAD_INT:", dict(flag_inad_vals.most_common(10)))
