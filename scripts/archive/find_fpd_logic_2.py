with open('fpd_dashboard_standalone.html', 'r', encoding='utf-8', errors='ignore') as f:
    chunk = f.read(3 * 1024 * 1024)

idx = chunk.find('Aging 30')
if idx != -1:
    snippet = chunk[idx: idx + 4000]
    print(snippet)
