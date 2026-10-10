import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

aside_match = re.search(r'<aside id="side"[^>]*>(.*?)</aside>', text, re.DOTALL)
if aside_match:
    print('Side nav items:')
    links = re.findall(r'<a[^>]*data-v=["\']([^"\']+)["\'][^>]*>(.*?)</a>', aside_match.group(1), re.DOTALL)
    for v, l in links:
        clean = re.sub(r'<[^>]+>', ' ', l).strip()
        print(f'  data-v="{v}": {clean}')

views = re.findall(r'<div[^>]*class=["\'][^"\']*view[^"\']*["\'][^>]*id=["\']([^"\']+)["\']', text)
print('\nView IDs found:', views)
