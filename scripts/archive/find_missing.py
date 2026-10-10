with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

import re

# 1. Cidades panel start
idx_cid = t.find('id="chCid"')
p_cid = t.rfind('<div class="panel"', 0, idx_cid)
print("Cidades panel:", t[p_cid:p_cid+100].replace('\n', ' '))

# 2. Tables in HTML body
s_script = t.find('<script>')
body = t[:s_script]
tables = re.findall(r'<table[^>]*>', body)
print("Tables in body:", tables)

# 3. metricVal search
m_val = [m.start() for m in re.finditer(r'metricVal', t)]
print("metricVal positions:", m_val)
for pos in m_val:
    print(t[pos-30:pos+100].replace('\n', ' '))

# 4. tipCell search
m_tip = [m.start() for m in re.finditer(r'tipCell', t)]
print("tipCell positions:", m_tip)
for pos in m_tip:
    print(t[pos-30:pos+100].replace('\n', ' '))
