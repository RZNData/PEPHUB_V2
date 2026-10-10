with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re

# Find each panel in the body
panels_to_find = [
    'chSafra',
    'chCurva',
    'mapCv',
    'chCid',
    'chNp',
    'chMot',
    'tblMtx',
    'chEsteira',
    'tblRank',
    'tblContratos',
    'upFile'
]

for p in panels_to_find:
    idx = text.find(f'id="{p}"')
    if idx != -1:
        # find closest preceding <div class="panel"
        p_div = text.rfind('<div class="panel"', 0, idx)
        # find <h2>
        h2_start = text.find('<h2>', p_div)
        h2_end = text.find('</h2>', h2_start)
        h2_text = text[h2_start+4:h2_end].strip().replace('\n', ' ')
        h2_clean = re.sub(r'<.*?>', '', h2_text)
        print(f"ID '{p}': panel at {p_div}, h2: {h2_clean.encode('ascii', 'replace').decode('ascii')[:60]}")
