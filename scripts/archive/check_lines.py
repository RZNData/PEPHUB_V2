with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines in Painel_FPD_Regional_Norte.html: {len(lines)}")
for target in [1425, 1426, 1427, 2136, 2137, 2138, 3001, 3002, 3003, 3134, 3135, 3136]:
    if target <= len(lines):
        print(f"Line {target}: {lines[target-1][:100].strip()}")
