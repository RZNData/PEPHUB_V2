import re

with open('public_staging/panorama-market-share/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# find script tag
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_match:
    js = script_match.group(1)
    
    # check functions that generate HTML
    fns = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{', js)
    print("Found functions in JS:", len(fns))
    
    # Check mentions of classes in JS string templates
    classes_in_js = set(re.findall(r'class=[\'\"]([^\'\"]+)[\'\"]', js))
    all_classes = set()
    for c in classes_in_js:
        for single in c.split():
            all_classes.add(single)
    
    print("\nClasses generated/used by JS:")
    for c in sorted(all_classes):
        print(f"  {c}")
