#!/usr/bin/env python3
"""
Script utilitário para aplicar a nova identidade visual PEP HUB PRIME
Insere a referência a /css/pephub-prime.css logo antes do fechamento </head>
de forma limpa e idempotente.
"""

import os
import re
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRS = [
    os.path.join(ROOT_DIR, "public"),
    os.path.join(ROOT_DIR, "relatorios")
]

PRIME_LINK = '<link rel="stylesheet" href="/css/pephub-prime.css">'

def process_html_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "</head>" not in content.lower():
            return False, "Sem tag </head>"

        # Remover links anteriores para reposicionar antes de </head>
        clean_content = re.sub(
            r'\s*<link[^>]+pephub-prime\.css[^>]*>',
            '',
            content,
            flags=re.IGNORECASE
        )

        # Inserir antes do fechamento </head>
        # Procura </head> mantendo a capitalização exata
        pattern = re.compile(r'(</head>)', re.IGNORECASE)
        replacement = f'{PRIME_LINK}\n\\1'
        
        new_content = pattern.sub(replacement, clean_content, count=1)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True, "Aplicado antes de </head>"
        else:
            return False, "Já atualizado ou inalterado"

    except Exception as e:
        return False, str(e)

def main():
    print("=" * 65)
    print("🎨 APLICANDO NOVA IDENTIDADE VISUAL (PEP HUB PRIME) NOS HTMLs")
    print("=" * 65)

    total_files = 0
    updated_files = 0

    for base_dir in TARGET_DIRS:
        if not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            # Ignorar templates vazios ou pastas ocultas
            if "_template" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith(".html"):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, ROOT_DIR)
                    total_files += 1
                    ok, msg = process_html_file(filepath)
                    if ok:
                        updated_files += 1
                        print(f"  ✅ [ATUALIZADO] {rel_path} -> {msg}")
                    else:
                        print(f"  • [MANTIDO]    {rel_path} -> {msg}")

    print("=" * 65)
    print(f"Concluído: {updated_files} de {total_files} arquivos HTML integrados com PEP HUB PRIME.")
    print("=" * 65)

if __name__ == "__main__":
    main()
