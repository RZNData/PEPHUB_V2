with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

idx = t.find('const maxN=Math.max(1,...pool.map(o=>o')
print(t[idx:idx+2000])
