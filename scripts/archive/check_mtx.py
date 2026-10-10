with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("document.getElementById('tabsMtx')")
if pos != -1:
    print(text[pos:pos+350])
