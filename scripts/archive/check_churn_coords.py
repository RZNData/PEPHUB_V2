import json, zlib, base64, struct

with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

p_start = text.find('const PAYLOAD = ') + len('const PAYLOAD = ')
idx = p_start
depth = 0
in_str = False
escape = False
p_end = p_start
for i in range(p_start, len(text)):
    c = text[i]
    if escape:
        escape = False
        continue
    if c == '\\':
        escape = True
        continue
    if c == '"':
        in_str = not in_str
    elif not in_str:
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                p_end = i + 1
                break

payload = json.loads(text[p_start:p_end])
n = payload['n']
gx_b64 = payload['cols']['gx']['b']
gx_bytes = zlib.decompress(base64.b64decode(gx_b64))
gx_vals = struct.unpack(f'<{n}H', gx_bytes)
valid_geo = sum(1 for x in gx_vals if x > 0)
print(f"Churn 28: Total n = {n}, with gx > 0: {valid_geo} ({valid_geo/n*100:.1f} pct)")
