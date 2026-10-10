import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', text, re.DOTALL)
engine = scripts[2]

m = re.search(r'Top \$\{tops\.length\}', engine)
if m:
    start = m.start()
    lines = engine[start-100:start+1500].split('\n')
    print("=== Top N ofensores side list in scatterSVG ===")
    print('\n'.join(lines[:45]))
