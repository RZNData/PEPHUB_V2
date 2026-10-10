#!/usr/bin/env python3
import re
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Find all references to HELP in JS code
help_refs = [(m.start(), html[max(0,m.start()-30):m.start()+60]) for m in re.finditer(r'HELP', html)]
print(f"Total HELP references: {len(help_refs)}")
for pos, ctx in help_refs[:10]:
    print(f"  pos {pos}: ...{ctx}...")

# Check if there's a hlp button handler
hlp_pos = html.find('.hlp')
if hlp_pos != -1:
    print(f"\n.hlp handler at pos {hlp_pos}: ...{html[max(0,hlp_pos-50):hlp_pos+100]}...")

# Check for data-h attributes (help buttons)
data_h = re.findall(r'data-h="(\w+)"', html)
print(f"\nHelp button data-h attributes: {data_h}")

# Check if the new HELP is being defined anywhere in the replaced JS block
print(f"\nNew JS block has 'const HELP': {'const HELP' in html}")
has_help_eq = 'HELP={' in html
print(f"New JS block has HELP=opening brace: {has_help_eq}")

