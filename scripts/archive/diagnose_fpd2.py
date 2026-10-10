#!/usr/bin/env python3
import re
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Find the init function area with legacy code
for legacy in ['drawNp()', 'drawMot()', 'drawEsteira()', 'drawCurva()']:
    pos = html.find(legacy)
    if pos != -1:
        # Find surrounding context
        start = max(0, pos - 100)
        end = min(len(html), pos + 100)
        snippet = html[start:end].replace('\n', '\\n')
        print(f"'{legacy}' at pos {pos}:")
        print(f"  ...{snippet}...")
        print()

# Check how init() function is structured near end
init_pos = html.rfind('function init(')
if init_pos != -1:
    print(f"Last init() at pos {init_pos}")
    print(html[init_pos:init_pos+200])
else:
    # Check for other init patterns
    for p in ['init()', 'addEventListener', 'DOMContentLoaded']:
        pos = html.rfind(p)
        if pos != -1:
            print(f"'{p}' last at pos {pos}: ...{html[max(0,pos-50):pos+80]}...")

# Check for 'Nunca pagou' more carefully - is it in HELP or in legacy?
pos = html.find('Nunca pagou')
if pos != -1:
    start = max(0, pos - 200)
    end = min(len(html), pos + 200)
    print(f"\n'Nunca pagou' context:")
    print(html[start:end])

# Find HELP pattern 
for p in ['const HELP', 'HELP={', 'HELP ={', 'HELP= {', 'HELP = {']:
    pos = html.find(p)
    if pos != -1:
        print(f"\nHELP pattern '{p}' at pos {pos}")
        print(html[pos:pos+80])
