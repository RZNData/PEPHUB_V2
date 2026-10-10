#!/usr/bin/env python3
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Find ALL occurrences of btnApply
import re
for m in re.finditer(r'btnApply', html):
    pos = m.start()
    ctx = html[max(0,pos-40):pos+60]
    print(f"pos {pos}: ...{ctx}...")
    print()

# Find the JS btnApply.onclick=render
js_btnApply = html.find("'btnApply').onclick=render")
print(f"\nJS btnApply.onclick=render at pos: {js_btnApply}")
if js_btnApply != -1:
    ctx = html[max(0,js_btnApply-100):js_btnApply+60]
    print(ctx)
