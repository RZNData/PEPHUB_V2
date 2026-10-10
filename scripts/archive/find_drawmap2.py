with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

idx = t.find('function drawMap()')
print(t[idx+1800:idx+3800])
