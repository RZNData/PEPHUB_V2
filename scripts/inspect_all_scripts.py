import re

with open('public_staging/panorama-market-share/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', text, re.DOTALL)
print(f"Total script blocks: {len(scripts)}")
for i, s in enumerate(scripts):
    print(f"Script {i+1} length: {len(s)} chars")
    fns = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{', s)
    if fns:
        print(f"  Functions ({len(fns)}): {fns[:10]}...")
    classes = set()
    for m in re.findall(r'class=[\'\"]([^\'\"]+)[\'\"]', s):
        for c in m.split():
            classes.add(c)
    if classes:
        print(f"  Classes ({len(classes)}): {sorted(classes)}")
