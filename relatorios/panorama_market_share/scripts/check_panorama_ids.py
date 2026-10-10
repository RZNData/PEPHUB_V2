import re, sys

with open('public_staging/panorama-market-share/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# find script tag
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
all_needed_ids = set()
for script_code in scripts:
    get_ids = set(re.findall(r"document\.getElementById\(['\"](.*?)['\"]", script_code))
    build_ms = set(re.findall(r"buildMS\(['\"](.*?)['\"]", script_code))
    build_radio = set(re.findall(r"buildRadio\(['\"](.*?)['\"]", script_code))
    build_prod = set(re.findall(r"buildProd\(['\"](.*?)['\"]", script_code))
    all_needed_ids |= get_ids | build_ms | build_radio | build_prod

print("All IDs referenced in JS:")
missing = []
for x in sorted(all_needed_ids):
    exists = (f'id="{x}"' in content) or (f"id='{x}'" in content)
    status = "EXISTS" if exists else "MISSING!!!"
    if not exists:
        missing.append(x)
    print(f"  {x}: {status}")

print(f"\nTotal missing IDs: {len(missing)}")
print("Missing:", missing)
