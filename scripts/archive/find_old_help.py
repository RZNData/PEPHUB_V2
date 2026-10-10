with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

s = text.find('const HELP={')
depth = 0
in_s = False
e = s
for i in range(s, len(text)):
    c = text[i]
    if c == "'" and text[i-1] != '\\':
        in_s = not in_s
    if not in_s:
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                e = i + 1
                if text[e:e+1] == ';': e += 1
                break

print(f"Old HELP range: {s} to {e} ({e-s} bytes)")
print("Starts:", repr(text[s:s+60]))
print("Ends:", repr(text[e-60:e]))
