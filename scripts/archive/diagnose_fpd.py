#!/usr/bin/env python3
import re
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Find all chart container IDs
ids = re.findall(r'id="(ch[A-Za-z0-9_]+)"', html)
print('Chart IDs:', ids)

# Find all IDs with mtx
mtx_ids = re.findall(r'id="([^"]*[Mm]tx[^"]*)"', html)
print('Matrix IDs:', mtx_ids)

# Find all IDs with cid 
cid_ids = re.findall(r'id="([^"]*[Cc]id[^"]*)"', html)
print('Cid IDs:', cid_ids)

# Check HELP patterns
help_patterns = ['const HELP', 'HELP=', 'HELP =']
for p in help_patterns:
    pos = html.find(p)
    if pos != -1:
        print(f"Found '{p}' at pos {pos}: ...{html[pos:pos+60]}...")

# Check for legacy drawNp
for legacy in ['drawNp', 'drawMot', 'drawEsteira', 'Nunca pagou']:
    pos = html.find(legacy)
    if pos != -1:
        print(f"Legacy '{legacy}' at pos {pos}: ...{html[max(0,pos-30):pos+40]}...")
