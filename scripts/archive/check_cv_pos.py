with open('Painel_FPD_Regional_Norte.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

cv_decl = content.find('const cv=')
print('const cv= at:', cv_decl)

import re
matches = [m.start() for m in re.finditer(r'cv\.addEventListener', content)]
print(f"Total cv.addEventListener: {len(matches)}")
for m in matches:
    print(f"cv.addEventListener at {m}: {'BEFORE cv_decl (ERROR)' if m < cv_decl else 'AFTER cv_decl (OK)'}")
