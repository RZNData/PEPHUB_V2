import re

def clean_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    orig_len = len(content)

    # Remove staging banner HTML block
    content = re.sub(
        r'(?:<!--\s*Staging Banner[^\n]*-->\s*)?<div class="staging-banner">[\s\S]*?</div>(?:\s*</head>\s*<body>)?\s*',
        '',
        content,
        flags=re.IGNORECASE
    )

    # Remove staging banner CSS block if present
    content = re.sub(
        r'/\*\s*Staging(?: Banner| Environment)?[^\*]*\*/\s*\.staging-banner\s*\{[\s\S]*?\.staging-pill\s*\{[\s\S]*?\}\s*',
        '',
        content,
        flags=re.IGNORECASE
    )

    if len(content) != orig_len:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned {path} (diff {orig_len - len(content)} chars)")
    else:
        print(f"No changes in {path}")

for p in [
    "public/index.html",
    "public/aprovacao-credito/index.html",
    "public/churn/index.html",
    "public/churn-bl-pme/index.html",
    "public/churn-bl-total/index.html",
    "public/fpd/index.html",
    "public/pep-tools/aniversario/index.html"
]:
    clean_file(p)
