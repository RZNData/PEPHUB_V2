import re

with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    text = f.read()

s_idx = text.find('<script>')
e_idx = text.rfind('</script>')
html_part = text[:s_idx]
js_part = text[s_idx+8:e_idx]

# Encontrar todos os getElementById no JS
calls = re.findall(r"document\.getElementById\(['\"]([a-zA-Z0-9_\-]+)['\"]\)", js_part)
print(f"Total de chamadas document.getElementById no JS: {len(calls)}")
unique_ids = sorted(list(set(calls)))
print(f"IDs únicos buscados: {len(unique_ids)}")

missing = []
for el_id in unique_ids:
    # Checar se existe no HTML como id="el_id" ou id='el_id'
    pattern = rf'id=["\']?{re.escape(el_id)}["\'\s>]'
    if not re.search(pattern, html_part):
        missing.append(el_id)

print(f"\nIDs NAO ENCONTRADOS no HTML ({len(missing)}):")
for m in missing:
    # Ver onde esse ID é chamado no JS
    locs = [line.strip() for line in js_part.splitlines() if f"'{m}'" in line or f'"{m}"' in line]
    print(f"  [MISSING] '{m}':")
    for l in locs[:3]:
        print(f"     -> {l[:100]}")

