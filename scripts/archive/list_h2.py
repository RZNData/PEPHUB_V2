with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

s_script = html.find('<script>')
body = html[:s_script]

import re
h2s = re.findall(r'<h2>([\s\S]*?)</h2>', body, re.IGNORECASE)
print(f"Total h2 found in body: {len(h2s)}")
for i, h in enumerate(h2s):
    h_clean = re.sub(r'<.*?>', '', h).strip().replace('\n', ' ')
    print(f"{i+1}: {h_clean.encode('ascii', 'replace').decode('ascii')[:70]}")
