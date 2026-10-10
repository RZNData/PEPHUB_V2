with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

idx = c.find('id="mapRankDim"')
print("mapRankDim at:", idx)
if idx != -1:
    print(c[idx-50:idx+350])
