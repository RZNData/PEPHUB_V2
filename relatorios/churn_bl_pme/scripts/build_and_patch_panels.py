#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Atualiza dados Out/26 (T1) nos painéis Churn Banda Larga Total e PME,
corrige o bug do HELP (TDZ) e dinamiza cabeçalhos de Mês/Tendência.
"""

import os
import re
import json
import zlib
import base64

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Carrega os JSONs extraídos
total_json_path = os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "data.json")
pme_json_path = os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "data.json")

with open(total_json_path, "r", encoding="utf-8") as f:
    total_data_str = f.read()
    total_b64 = base64.b64encode(zlib.compress(total_data_str.encode("utf-8"), level=9)).decode("ascii")

with open(pme_json_path, "r", encoding="utf-8") as f:
    pme_data_str = f.read()
    pme_b64 = base64.b64encode(zlib.compress(pme_data_str.encode("utf-8"), level=9)).decode("ascii")

print(f"[+] Total B64 comprimido: {len(total_b64)} chars")
print(f"[+] PME B64 comprimido: {len(pme_b64)} chars")

total_files = [
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_Total.html"),
    os.path.join(WORKSPACE_DIR, "public_staging", "churn-bl-total", "index.html"),
]

pme_files = [
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_PME.html"),
    os.path.join(WORKSPACE_DIR, "public_staging", "churn-bl-pme", "index.html"),
]

def patch_file(file_path, new_b64, is_pme=False):
    if not os.path.exists(file_path):
        print(f"[-] Arquivo não existe: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Corrige o TDZ do HELP
    # Substitui a declaração problemática antes de RAW_PAYLOAD_B64
    content = re.sub(
        r"const\s+HLP_CONTENT\s*=\s*typeof\s+HELP\s*!==\s*['\"]undefined['\"]\s*\?\s*HELP\s*:\s*\{\};",
        "var HLP_CONTENT = {};",
        content
    )

    # 2. Garante que após 'const HELP = { ... };' HLP_CONTENT é atribuído
    # Procura 'const HELP = {' e insere após o fechamento do bloco 'HLP_CONTENT = HELP;'
    if "HLP_CONTENT = HELP;" not in content:
        # Encontra o fim do bloco HELP
        help_idx = content.find("const HELP = {")
        if help_idx != -1:
            end_help_idx = content.find("};\n", help_idx)
            if end_help_idx != -1:
                content = content[:end_help_idx+2] + "\nHLP_CONTENT = HELP;" + content[end_help_idx+2:]

    # 3. Substitui RAW_PAYLOAD_B64
    content = re.sub(
        r'const\s+RAW_PAYLOAD_B64\s*=\s*"[^"]+";',
        f'const RAW_PAYLOAD_B64 = "{new_b64}";',
        content
    )

    # 4. Atualiza textos de cabeçalho padrão no HTML
    content = content.replace("Setembro / 2026", "Outubro / 2026")
    content = content.replace("SETEMBRO / 2026", "OUTUBRO / 2026")
    content = content.replace("21/09/2026", "05/10/2026")
    content = content.replace("4ª Tendência (T4)", "1ª Tendência (T1)")
    content = content.replace("Realizado Mês (T4)", "Realizado Mês (T1)")
    content = content.replace("REAL (T4)", "REAL (T1)")

    # 5. No renderAll() ou boot(), garantir atualização dos IDs de cabeçalho
    dyn_header_code = """
    // Atualização dinâmica dos elementos de cabeçalho
    if (RAW_DATA) {
      const elMes = document.getElementById('subMesRef');
      if (elMes && RAW_DATA.mes_referencia) elMes.textContent = RAW_DATA.mes_referencia;
      const elPos = document.getElementById('subDataPos');
      if (elPos && RAW_DATA.data_posicao) elPos.textContent = RAW_DATA.data_posicao;
      const elTend = document.getElementById('subTendencia');
      if (elTend && RAW_DATA.tendencia_atual) elTend.textContent = RAW_DATA.tendencia_atual;
    }
"""
    if "elMes && RAW_DATA.mes_referencia" not in content:
        content = content.replace("renderKPIs();", dyn_header_code + "\n    renderKPIs();")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Sucesso: {os.path.basename(file_path)} atualizado.")

for p in total_files:
    patch_file(p, total_b64, is_pme=False)

for p in pme_files:
    patch_file(p, pme_b64, is_pme=True)

print("[+] Concluída atualização dos painéis Churn Banda Larga!")
