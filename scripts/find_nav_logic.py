import re

with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = 0
while True:
    idx = text.find('id="nav"', pos)
    if idx == -1:
        idx = text.find("id='nav'", pos)
    if idx == -1:
        break
    print("Found id=nav at:", idx)
    pos = idx + 10

# Search for nav event listener in JS
for m in re.finditer(r'nav\.(?:addEventListener|onclick)|document\.querySelectorAll\(["\']#nav\s+a["\']\)', text):
    print("Nav listener:", text[m.start():m.start()+200])

# Search for S.view or active view logic
for m in re.finditer(r'(?:setView|switchView|goView|showView|curView|activeView)', text):
    print("View logic:", text[m.start():m.start()+150])
