import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

pos_s = text.find('<style>')
pos_e = text.find('</style>')
css = text[pos_s+7:pos_e]

target_classes = [
    'lvlstrip', 'lvlcount', 'lc-top', 'lc-num', 'lc-lbl', 'lc-sub', 'lc-dot',
    'xkpis', 'xkpi', 'sumsec-h', 'bdg', 'hint', 'resnarr', 'sumnote',
    'qcard', 'qtitle', 'qsub', 'subtabs', 'subtab',
    'cart-row', 'cart-car', 'cart-pdv', 'cart-grp',
    'stbl', 'cellwrap', 'cbadge', 'sem', 'rankn',
    'dualscroll', 'ds-top', 'ds-body', 'ds-spacer',
    'rowgrp', 'rowchild', 'rowpdv', 'rowsub',
    'fltxt', 'flval', 'flop', 'searchbox'
]

pattern = r'([^{}]*\.(?:' + '|'.join(target_classes) + r')\b[^{]*\{[^}]*\})'
matches = re.findall(pattern, css)
for m in matches[50:]:
    print(m.strip())
    print('-'*30)
