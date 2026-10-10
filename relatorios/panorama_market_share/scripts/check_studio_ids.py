import re

with open('public_staging/pep-tools/market-share/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
all_needed_ids = set()
for script_code in scripts:
    get_ids = set(re.findall(r"document\.getElementById\(['\"](.*?)['\"]", script_code))
    all_needed_ids |= get_ids

print(f"Total IDs referenced in JS: {len(all_needed_ids)}")
missing = []
for x in sorted(all_needed_ids):
    exists = (f'id="{x}"' in content) or (f"id='{x}'" in content)
    if not exists:
        missing.append(x)

print(f"Total missing IDs: {len(missing)}")
if missing:
    print("Missing IDs:", missing)
else:
    print("No missing IDs!")
