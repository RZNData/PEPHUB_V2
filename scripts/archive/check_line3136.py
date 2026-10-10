#!/usr/bin/env python3
# Check around line 3136 for JS syntax errors
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()
lines = html.split('\n')

print(f"Total lines: {len(lines)}")

# Show lines around 3136
start = max(0, 3130)
end = min(len(lines), 3145)
for i in range(start, end):
    print(f"L{i+1}: {lines[i][:200]}")
