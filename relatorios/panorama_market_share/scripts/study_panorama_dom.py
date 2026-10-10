import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open('Panorama_MktShare_Movel_Residencial_RNO_jul26 10.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('<script')
html_before = text[:idx]

sections = re.findall(r'<section[^>]*id=["\']([^"\']+)["\']', html_before)
print('Section IDs:', sections)

headings = re.findall(r'<h2[^>]*>(.*?)</h2>', html_before)
for h in headings:
    clean = re.sub(r'<[^>]+>', '', h).strip()
    print('  H2:', clean)
