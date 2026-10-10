with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

idx = t.find('function drawCells')
if idx == -1:
    idx = t.find('function drawMap(')
print("drawMap:", t[idx:idx+2000])
