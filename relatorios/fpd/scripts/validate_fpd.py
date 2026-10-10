#!/usr/bin/env python3
# Quick validation of the generated FPD panel HTML
import re, sys

html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()
print(f"Size: {len(html):,} chars")
print(f"Has PAYLOAD: {'const PAYLOAD' in html}")
print(f"Has closing html: {'</html>' in html}")

fns = ['render_', 'drawKpis', 'drawSafra', 'drawScatter', 'drawCid', 'drawRisco', 'drawMtx', 'drawRank', 'openContratos', 'pagouOf']
for fn in fns:
    found = ('function ' + fn + '(') in html
    status = 'OK' if found else 'MISSING'
    print(f"  {fn}: {status}")

t = re.search(r'<title>(.*?)</title>', html, re.I)
if t:
    print(f"Title: {t.group(1)}")

# Check key DOM IDs
dom_ids = ['chSafra', 'chScatter', 'chCidades', 'chRisco', 'chMtx', 'tblRank', 'tblMapRank', 'tabsScatComp', 'tabsScatDim', 'tabsRiscoMode', 'tabsMtx']
for did in dom_ids:
    found = ('id="' + did + '"') in html
    status = 'OK' if found else 'MISSING'
    print(f"  DOM #{did}: {status}")

# Check HELP object
print(f"Has HELP object: {'const HELP' in html}")

# Check for legacy churn artifacts
legacy = ['Nunca pagou', 'Motivo da desconex', 'drawCurva', 'drawNp', 'drawMot', 'drawEsteira']
for l in legacy:
    found = l in html
    status = 'REMOVED' if not found else 'STILL PRESENT (BAD)'
    print(f"  Legacy '{l}': {status}")
