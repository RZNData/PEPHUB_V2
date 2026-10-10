import re

with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('=== PAINÉIS HTML NO CHURN SAFRA 28 ===')
matches = re.findall(r'<div class="panel[^"]*">.*?<h2>(.*?)(?:<button|<span|</h2>)', text, re.DOTALL)
for m in matches:
    clean = re.sub(r'<.*?>', '', m).strip()
    print('-', clean)

print('\n=== SEÇÕES JS NO CHURN SAFRA 28 ===')
js_sections = re.findall(r'/\* =+ (.*?) =+ \*/', text)
for s in js_sections:
    print('-', s)
