import re

with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    text = f.read()

s_idx = text.find('function init(){')
e_idx = text.find('</script>', s_idx)
init_code = text[s_idx:e_idx]

# Achar todos os document.getElementById('xyz').on... =
bindings = re.findall(r"document\.getElementById\(['\"]([a-zA-Z0-9_\-]+)['\"]\)\.(on[a-zA-Z]+)\s*=", init_code)
html_part = text[:text.find('<script>')]

print(f"Total de event bindings diretos no init(): {len(bindings)}")
for el_id, event in bindings:
    in_html = f'id="{el_id}"' in html_part or f"id='{el_id}'" in html_part
    status = "OK" if in_html else "PERIGO (NULL!)"
    print(f"  {el_id:20s}.{event:10s} -> {status}")
