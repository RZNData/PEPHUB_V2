import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect(filename):
    print("=" * 60)
    print("INSPECTING:", filename)
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    title = re.search(r'<title>(.*?)</title>', text, re.I)
    print("Title:", title.group(1) if title else "None")
    
    root_match = re.search(r':root\s*\{([^}]+)\}', text)
    if root_match:
        print("Root CSS snippet:\n", root_match.group(1).strip()[:300])
    else:
        print("No :root CSS found")
        
    body_idx = text.find('<body')
    if body_idx != -1:
        print("\nBody start:\n", text[body_idx:body_idx+600])

inspect('Panorama_MktShare_Movel_Residencial_RNO_jul26 10.html')
inspect('Painel Aprovacao Credito RNO 2.4.html')
