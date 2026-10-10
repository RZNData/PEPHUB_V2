with open('fpd_dashboard_standalone.html', 'r', encoding='utf-8', errors='ignore') as f:
    chunk = f.read(3 * 1024 * 1024)

keywords = ['FPD (Inadimplente)', 'FPD 30', 'Aging 30', 'DENOMINADOR']
for kw in keywords:
    pos = 0
    print(f"\n=== Ocorrências de '{kw}' ===")
    while True:
        idx = chunk.find(kw, pos)
        if idx == -1:
            break
        snippet = chunk[max(0, idx - 150): min(len(chunk), idx + 250)]
        print("--- SNIPPET ---")
        print(snippet)
        pos = idx + len(kw)
        if pos >= len(chunk) or pos > 1000000:
            break
