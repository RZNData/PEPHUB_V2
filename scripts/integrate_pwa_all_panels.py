#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — PWA & Mobile Best Practices Integrator
Integra manifest, meta tags móveis, viewport-fit=cover, CSS mobile e controller JS
em todos os painéis e ferramentas da Regional Norte.
"""

import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PWA_HEAD_TAGS = """<!-- PWA & Mobile Web App Meta Tags -->
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#8a0f18">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="PEP HUB">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon.png">
<link rel="stylesheet" href="/css/app-mobile.css">"""

PWA_BODY_SCRIPT = """<script src="/js/app-mobile.js"></script>"""

PANELS = [
    'public/index.html',
    'public/login/index.html',
    'public/churn/index.html',
    'public/fpd/index.html',
    'public/panorama-market-share/index.html',
    'public/aprovacao-credito/index.html',
    'public/churn-bl-pme/index.html',
    'public/churn-bl-total/index.html',
    'public/pep-tools/market-share/index.html',
    'public/pep-tools/aniversario/index.html',
    'public/podcast/index.html',
    'public/admin/index.html',
    'public/register/index.html',
    'public/forgot-password/index.html',
    'public/reset-password/index.html',
    'public/offline.html'
]

def process_file(filepath):
    if not os.path.exists(filepath):
        print(f"[SKIP] Arquivo não encontrado: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    changed = False

    # 1. Atualizar viewport para viewport-fit=cover
    if 'viewport-fit=cover' not in content:
        if '<meta name="viewport" content="width=device-width, initial-scale=1">' in content:
            content = content.replace(
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            )
            changed = True
        elif '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in content:
            content = content.replace(
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">'
            )
            changed = True

    # 2. Injetar PWA_HEAD_TAGS se não houver manifest.webmanifest
    if 'manifest.webmanifest' not in content:
        # Procurar </title> ou <head>
        if '</title>' in content:
            content = content.replace('</title>', f'</title>\n\n{PWA_HEAD_TAGS}')
            changed = True
        elif '<head>' in content:
            content = content.replace('<head>', f'<head>\n{PWA_HEAD_TAGS}')
            changed = True

    # 3. Garantir link para app-mobile.css se não existir
    if 'app-mobile.css' not in content:
        if '</head>' in content:
            content = content.replace('</head>', '<link rel="stylesheet" href="/css/app-mobile.css">\n</head>')
            changed = True

    # 4. Injetar script app-mobile.js antes de </body> se não existir (exceto offline.html)
    if 'app-mobile.js' not in content and not filepath.endswith('offline.html'):
        if '</body>' in content:
            content = content.replace('</body>', f'{PWA_BODY_SCRIPT}\n</body>')
            changed = True
        else:
            content += f'\n{PWA_BODY_SCRIPT}\n'
            changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Integrado com sucesso: {filepath}")
    else:
        print(f"[UNCHANGED] Já estava atualizado: {filepath}")

def main():
    print("Iniciando integração de PWA & Mobile Best Practices em todos os painéis...")
    for p in PANELS:
        process_file(p)
    print("\nIntegração concluída em todos os painéis!")

if __name__ == '__main__':
    main()
