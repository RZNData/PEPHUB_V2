import re

print("Lendo primeiros 3MB do fpd_dashboard_standalone.html...")
with open('fpd_dashboard_standalone.html', 'r', encoding='utf-8', errors='ignore') as f:
    header_chunk = f.read(3 * 1024 * 1024) # 3MB

print(f"Lidos {len(header_chunk):,} caracteres.")

# Procurar títulos de abas, componentes e textos em português
# Normalmente React/Vite minificado tem strings literais como "Taxa FPD", "Instalações", "Parceiros", etc.
pt_strings = re.findall(r'["\']([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõçA-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\s/%–\-_()]{3,40})["\']', header_chunk)
unique_strings = sorted(list(set(pt_strings)))

fpd_related = [s for s in unique_strings if any(k in s.lower() for k in ['fpd', 'safra', 'parceir', 'vendedor', 'canal', 'aging', 'inadimpl', 'cidade', 'taxa', 'volume', 'mapa', 'ranking', 'ponto'])]
print(f"\nStrings relevantes de UI ({len(fpd_related)}):")
for s in fpd_related[:60]:
    print(" -", s)
