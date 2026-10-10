import re

with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    c = f.read()

scripts = re.findall(r'<script>(.*?)</script>', c, re.DOTALL)
print(f'Total de blocos script: {len(scripts)}')

js_code = scripts[0]
print(f'Tamanho do script JS: {len(js_code):,} caracteres')

checks = [
    'boot', 'drawKpis', 'drawSafra', 'drawCurva', 'drawCid',
    'drawNp', 'drawMot', 'drawMtx', 'drawEsteira', 'drawRank',
    'drawMap', 'buildIndex', 'openContratos', 'csvContratos'
]
for fn in checks:
    print(f'Funcao {fn}:', f'function {fn}' in js_code or f'{fn}(' in js_code)

card_checks = [
    'Taxa FPD 60 (Oficial)',
    'Taxa FPD 30 (Pré-FPD)',
    'Taxa FPD 90 (Pré-Churn)',
    'Adimplência 1ª Fatura',
    'Variação MoM (FPD 60)',
    'Benchmark YTD (Acumulado)',
    'Nunca Pagou (FPD 30 & 60)',
    'Regularização Pré-FPD'
]
for cd in card_checks:
    print(f'Card "{cd}":', cd in js_code)

print("\nVerificando consistência dos arquivos exportados:")
for path in ['Painel_FPD_Regional_Norte.html', 'public/fpd/index.html', 'public/fpd/Painel_FPD_Regional_Norte.html']:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f' - {path}: {len(content):,} bytes | FPD 60 Oficial presente: {"FPD 60 (Oficial)" in content}')
