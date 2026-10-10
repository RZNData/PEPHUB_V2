#!/usr/bin/env python3
# Find the exact context around the broken tabsCid comment
html = open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore').read()
lines = html.split('\n')

# Show more lines around the issue
for i in range(3133, min(len(lines), 3145)):
    print(f"L{i+1}: {repr(lines[i][:250])}")
