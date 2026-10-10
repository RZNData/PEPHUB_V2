with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

idx = t.find('function buildCells')
print(t[idx+800:idx+2500])
