#!/usr/bin/env python3
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()

# Check for event init code markers
markers = ['tabsScatComp', 'tabsScatDim', 'tabsRiscoMode', 'mtxDim', 'mtxMature', 'rkSearch', 'rkMin']
for m in markers:
    # Find all occurrences
    pos = html.find(m)
    if pos != -1:
        print(f"Found '{m}' at pos {pos}")
    else:
        print(f"MISSING '{m}'")

# Check for event_init_code injection (look for the distinctive pattern)
inject_marker = 'tabsScatCompEl'
pos = html.find(inject_marker)
if pos != -1:
    start = max(0, pos - 50)
    end = min(len(html), pos + 120)
    print(f"\nEvent init code injected at pos {pos}:")
    print(html[start:end])
else:
    print("\nWARNING: Event init code NOT found in HTML!")

# Check for JS errors by looking for the btnApply area
ba_pos = html.find("btnApply")
if ba_pos != -1:
    start = max(0, ba_pos - 200)
    end = min(len(html), ba_pos + 80)
    print(f"\nbtnApply area:")
    print(html[start:end])
