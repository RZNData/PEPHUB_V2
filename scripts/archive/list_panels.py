with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

s_script = html.find('<script>')
body = html[:s_script]

import re
panels = re.findall(r'<div class="panel">[\s\S]*?<h2>(.*?)</h2>', body, re.IGNORECASE)
print(f"Total panels found in body: {len(panels)}")
for i, p in enumerate(panels):
    # clean tags
    p_clean = re.sub(r'<.*?>', '', p).strip()
    print(f"{i+1}: {p_clean}")
