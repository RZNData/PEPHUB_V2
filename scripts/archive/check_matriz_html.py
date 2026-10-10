with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8') as f:
    text = f.read()

p = text.find('tblMtx')
start = text.rfind('<div class="panel">', 0, p)
end = text.find('</div>\n</div>', p) + len('</div>\n</div>')
print('Painel da Matriz (tamanho):', end - start)
print(text[start:start+500])
