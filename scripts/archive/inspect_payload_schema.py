import json

with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8') as f:
    text = f.read()

p_start = text.find('const PAYLOAD = ') + len('const PAYLOAD = ')
p_dec = text.find('/* ============ decodificação')
raw_json = text[p_start:p_dec].strip()
if raw_json.endswith(';'):
    raw_json = raw_json[:-1].strip()

orig_p = json.loads(raw_json)
print('Chaves do PAYLOAD original:', list(orig_p.keys()))
print('n:', orig_p.get('n'))
print('bbox:', orig_p.get('bbox'))
print('Exemplo col safra:', {k: (v if k!='b' else v[:30]+'...') for k, v in orig_p['cols']['safra'].items()})
print('Exemplo col ctr:', {k: (v if k!='b' else v[:30]+'...') for k, v in orig_p['cols']['ctr'].items()})
print('\nTodas as cols e seus tipos:')
for k, v in orig_p['cols'].items():
    print(f"  '{k}': '{v['t']}',")

