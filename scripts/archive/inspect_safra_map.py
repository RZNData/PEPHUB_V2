with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    f.seek(5349600)
    chunk = f.read(3500)
    print(chunk)
