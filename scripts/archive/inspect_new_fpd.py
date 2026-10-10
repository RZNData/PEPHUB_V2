import csv
from collections import Counter

regionais = Counter()
regionais_cmv = Counter()
cidades = Counter()
dt_ini_anos = Counter()
safra_counter = Counter()

with open('BASE_FPD_JUN25_JUN26.csv', 'r', encoding='latin1') as f:
    reader = csv.reader(f, delimiter=';')
    header = [c.strip().strip('"') for c in next(reader)]
    i_reg = header.index('NM_REGIONAL')
    i_reg_cmv = header.index('NM_REGIONAL_CMV')
    i_cid = header.index('NM_CIDADE')
    i_dt = header.index('DT_INI_CONTRATO')
    i_safra = header.index('SAFRA')
    
    for row in reader:
        regionais[row[i_reg]] += 1
        regionais_cmv[row[i_reg_cmv]] += 1
        if 'NORTE' in row[i_reg].upper() or 'NORTE' in row[i_reg_cmv].upper():
            cidades[row[i_cid]] += 1
        safra_counter[row[i_safra]] += 1
        dt = row[i_dt].strip()
        if len(dt) >= 10:
            dt_ini_anos[dt[6:10] + dt[3:5]] += 1

print("Regionais:", sorted(regionais.items()))
print("Regionais CMV:", sorted(regionais_cmv.items()))
print("Safra:", sorted(safra_counter.items()))
print("DT_INI (AnoMes):", sorted(dt_ini_anos.items()))
print("Cidades Norte:", cidades.most_common(15))




