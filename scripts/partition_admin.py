# -*- coding: utf-8 -*-
import os

ADMIN_HTML = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "admin", "index.html")
ADMIN_JS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "admin", "js")
ADMIN_JS = os.path.join(ADMIN_JS_DIR, "admin.js")

with open(ADMIN_HTML, "r", encoding="utf-8") as f:
    text = f.read()

s_tag = "<script>\n"
e_tag = "\n</script>"

s_idx = text.find(s_tag)
e_idx = text.find(e_tag, s_idx)

if s_idx != -1 and e_idx != -1:
    js_code = text[s_idx + len(s_tag):e_idx]
    os.makedirs(ADMIN_JS_DIR, exist_ok=True)
    with open(ADMIN_JS, "w", encoding="utf-8") as f_js:
        f_js.write(js_code)
    
    new_html = text[:s_idx] + '<script src="/admin/js/admin.js"></script>' + text[e_idx + len(e_tag):]
    with open(ADMIN_HTML, "w", encoding="utf-8") as f_html:
        f_html.write(new_html)
    
    print("Sucesso! Admin particionado:")
    print(f"  • public/admin/index.html: {new_html.count(chr(10)) + 1} linhas")
    print(f"  • public/admin/js/admin.js: {js_code.count(chr(10)) + 1} linhas")
else:
    print(f"Tags de script não localizadas. s_idx={s_idx}, e_idx={e_idx}")
