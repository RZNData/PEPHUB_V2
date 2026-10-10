#!/usr/bin/env python3
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()
pos = html.find('Nunca pagou')
if pos != -1:
    start = max(0, pos - 200)
    end = min(len(html), pos + 200)
    print(f"Context around 'Nunca pagou' at pos {pos}:")
    print(html[start:end])
    print("---")

# Also check where drawEsteira comment is
pos2 = html.find('drawEsteira')
if pos2 != -1:
    start2 = max(0, pos2 - 80)
    end2 = min(len(html), pos2 + 80)
    print(f"\nContext around 'drawEsteira' at pos {pos2}:")
    print(html[start2:end2])
