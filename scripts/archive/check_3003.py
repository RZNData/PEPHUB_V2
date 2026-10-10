#!/usr/bin/env python3
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()
lines = html.split('\n')

# Show lines 3000-3010
for i in range(2999, min(len(lines), 3010)):
    print(f"L{i+1}: {lines[i][:200]}")
