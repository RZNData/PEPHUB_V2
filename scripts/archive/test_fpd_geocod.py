import csv

print("Testando cruzamento de contratos FPD com Base_Churn_Geocod...")
fpd_contratos = set()
with open('FPD_JAN_MAI_26.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    idx_contrato = h_idx.get('NR_CONTRATO', 4)
    for row in reader:
        c = row[idx_contrato]
        if c:
            fpd_contratos.add(c)

print(f"Total de contratos no FPD: {len(fpd_contratos):,}")

# Cruzar com Base_Churn_Geocod
matches = 0
coords_found = 0
city_coords = {}

with open('Base_Churn_Geocod_v3_FALLBACK_CEP.csv', 'r', encoding='latin1', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    h_idx = {h: idx for idx, h in enumerate(headers)}
    idx_c = h_idx.get('NR_CONTRATO', 14)
    idx_cid = h_idx.get('CIDADE', 3)
    idx_lat = h_idx.get('LAT_FINAL(FALLBACK_2)', 68)
    idx_lon = h_idx.get('LONG_FINAL(FALLBACK_2)', 69)
    
    count = 0
    for row in reader:
        count += 1
        c = row[idx_c] if idx_c < len(row) else ""
        cid = row[idx_cid] if idx_cid < len(row) else ""
        lat = row[idx_lat] if idx_lat < len(row) else ""
        lon = row[idx_lon] if idx_lon < len(row) else ""
        
        if lat and lon and cid:
            try:
                lat_f = float(lat.replace(',', '.'))
                lon_f = float(lon.replace(',', '.'))
                if cid not in city_coords:
                    city_coords[cid] = []
                if len(city_coords[cid]) < 50:
                    city_coords[cid].append((lat_f, lon_f))
            except:
                pass

        if c in fpd_contratos:
            matches += 1
            if lat and lon:
                coords_found += 1
        if count % 100000 == 0:
            print(f"Lidos {count:,} linhas... Matches: {matches:,} | Coordenadas: {coords_found:,}")

print(f"\nFinal: Matches de Contrato: {matches:,} / {len(fpd_contratos):,} ({matches/len(fpd_contratos)*100:.1f}%)")
print(f"Com Coordenadas exatas: {coords_found:,}")
print(f"Cidades com centróides mapeados: {len(city_coords)}")
for cid, pts in list(city_coords.items())[:10]:
    avg_lat = sum(p[0] for p in pts)/len(pts)
    avg_lon = sum(p[1] for p in pts)/len(pts)
    print(f"  {cid}: ({avg_lat:.4f}, {avg_lon:.4f}) [{len(pts)} pts]")
