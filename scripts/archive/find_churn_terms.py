with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Split into HTML body and script
s_script = html.find('<script>')
body = html[:s_script]

terms = [
    'desconex', 'desconect', 'nunca pagou', 'esteira', 'motivo da desc',
    'curva de matur', 'sk_fc_gerou', 'd120', 'd150'
]

for t in terms:
    idx = 0
    while True:
        pos = body.lower().find(t, idx)
        if pos == -1: break
        print(f"Term '{t}' in HTML body at {pos}:")
        print(body[max(0, pos-40):min(len(body), pos+80)].replace('\n', ' '))
        print('---')
        idx = pos + len(t)
