import re

with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('=== ORDEM DOS PAINÉIS NO HTML ===')
matches = re.finditer(r'<div class="panel[^"]*">.*?<h2>(.*?)(?:<button|<span|</h2>)', text, re.DOTALL)
for m in matches:
    pos = m.start()
    clean = re.sub(r'<.*?>', '', m.group(1)).strip().replace('\n', ' ')
    print(f'Pos {pos:7d}: {clean}')
