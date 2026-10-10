with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

import re

# Search around newCell (pos 5355561)
idx = t.find('function newCell')
print("Code around newCell:")
print(t[idx:idx+1500])
