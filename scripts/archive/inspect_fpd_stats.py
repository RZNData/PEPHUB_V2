import csv

safras_ord = ['jan/26', 'fev/26', 'mar/26', 'abr/26', 'mai/26']
safra_nome = {'202601': 'jan/26', '202602': 'fev/26', '202603': 'mar/26', '202604': 'abr/26', '202605': 'mai/26'}

stats = {s: {'inst': 0, 'ag30': 0, 'ag60': 0, 'ag90': 0, 'ag120': 0, 'over90': 0, 'score_alto': 0} for s in safras_ord}

with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    r = csv.reader(f, delimiter=';')
    h = next(r)
    h_idx = {name: i for i, name in enumerate(h)}
    s_idx = h_idx.get('SAFRA', 33)
    a30_idx = h_idx.get('AGING30', 129)
    a60_idx = h_idx.get('AGING60', 130)
    a90_idx = h_idx.get('AGING90', 131)
    a120_idx = h_idx.get('AGING120', 132)
    ov_idx = h_idx.get('OVER90', 128)
    risco_idx = h_idx.get('FXRISCO', 104)

    for row in r:
        s_raw = row[s_idx].strip() if s_idx < len(row) else ''
        s = safra_nome.get(s_raw)
        if not s: continue
        stats[s]['inst'] += 1
        if a30_idx < len(row) and row[a30_idx] == '1': stats[s]['ag30'] += 1
        if a60_idx < len(row) and row[a60_idx] == '1': stats[s]['ag60'] += 1
        if a90_idx < len(row) and row[a90_idx] == '1': stats[s]['ag90'] += 1
        if a120_idx < len(row) and row[a120_idx] == '1': stats[s]['ag120'] += 1
        if ov_idx < len(row) and row[ov_idx] == '1': stats[s]['over90'] += 1
        risco = row[risco_idx].strip() if risco_idx < len(row) else ''
        if 'Alt' in risco or 'Alto' in risco: stats[s]['score_alto'] += 1

print("--- RESUMO CONSOLIDADO DAS SAFRAS FPD ---")
prev_tx60 = None
prev_inst = None
for s in safras_ord:
    st = stats[s]
    tx60 = st['ag60'] / st['inst'] * 100
    tx30 = st['ag30'] / st['inst'] * 100
    tx90 = st['ag90'] / st['inst'] * 100
    mom_str = ""
    if prev_tx60 is not None:
        diff_pp = tx60 - prev_tx60
        diff_inst_pct = (st['inst'] - prev_inst) / prev_inst * 100
        mom_str = f" | MoM FPD 60: {diff_pp:+.2f} p.p. | MoM Inst: {diff_inst_pct:+.1f}%"
    prev_tx60 = tx60
    prev_inst = st['inst']
    print(f"{s}: {st['inst']:,} inst | FPD 60: {st['ag60']:,} ({tx60:.2f}%){mom_str} | FPD 30: {st['ag30']:,} ({tx30:.2f}%) | FPD 90: {st['ag90']:,} ({tx90:.2f}%)")

# Benchmark e YoY estimado vs 2025
print("\n--- SAFRA FOCO (mai/26) ---")
foco = stats['mai/26']
foco_tx60 = foco['ag60'] / foco['inst'] * 100
foco_tx30 = foco['ag30'] / foco['inst'] * 100
foco_tx90 = foco['ag90'] / foco['inst'] * 100
print(f"Safra Foco: mai/26 ({foco['inst']:,} contratos)")
print(f"FPD 60 Oficial: {foco_tx60:.2f}% ({foco['ag60']:,} contratos)")
print(f"FPD 30 (Pré-FPD): {foco_tx30:.2f}% ({foco['ag30']:,} contratos)")
print(f"FPD 90 (Pré-Churn): {foco_tx90:.2f}% ({foco['ag90']:,} contratos)")
print(f"Adimplência 1ª Fatura: {(100 - foco_tx60):.2f}% ({(foco['inst'] - foco['ag60']):,} contratos)")
