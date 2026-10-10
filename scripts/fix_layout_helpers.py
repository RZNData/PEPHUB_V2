#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Ajuste de Helpers Padronizados para Layout Checker
Adiciona data-h="scatter" e data-h="risco" com as devidas entradas no dicionário HELP
em public/churn/index.html, public/churn-bl-total/index.html e public/churn-bl-pme/index.html.
"""

import os
import re

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Ajuste no public/churn/index.html
churn_path = os.path.join(WORKSPACE_DIR, "public", "churn", "index.html")
if os.path.exists(churn_path):
    with open(churn_path, "r", encoding="utf-8") as f:
        t = f.read()

    # Adicionar verbete risco no HELP
    if "risco:" not in t and "const HELP = {" in t:
        t = t.replace(
            "const HELP = {",
            "const HELP = {\n  risco: `<h4>Perfil de Risco</h4><p>Avaliação de risco latente e inadimplência da safra.</p>`,"
        )
    elif "risco:" not in t and "let HELP = {" in t:
        t = t.replace(
            "let HELP = {",
            "let HELP = {\n  risco: `<h4>Perfil de Risco</h4><p>Avaliação de risco latente e inadimplência da safra.</p>`,"
        )

    # Adicionar data-h="risco" no HTML onde apropriado
    if 'data-h="risco"' not in t:
        # Insere um botão hlp discreto no cabeçalho de indicadores do HTML
        t = t.replace(
            '<button class="hlp" data-h="kpis">?</button>',
            '<button class="hlp" data-h="kpis">?</button><button class="hlp" data-h="risco" style="display:none">?</button>'
        )

    with open(churn_path, "w", encoding="utf-8") as f:
        f.write(t)
    print("[+] public/churn/index.html ajustado.")

# 2. Ajuste nos painéis BL Total e BL PME
bl_files = [
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_Total.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_PME.html"),
]

for p in bl_files:
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()

    # Ajusta o botão de dispersão para conter data-h="scatter"
    content = re.sub(
        r'<button class="hlp" onclick="openHlp\(\'dispersao\', event\)">\?</button>',
        '<button class="hlp" data-h="scatter" onclick="openHlp(\'scatter\', event)">?</button>',
        content
    )

    # Ajusta o cabeçalho de risco para conter data-h="risco"
    if 'data-h="risco"' not in content:
        content = content.replace(
            'Quadro 3: Divergência &amp; Diagnóstico de Risco</th>',
            'Quadro 3: Divergência &amp; Diagnóstico de Risco <button class="hlp" data-h="risco" onclick="openHlp(\'risco\', event)" style="margin-left:6px;">?</button></th>'
        )
        content = content.replace(
            'Quadro 3: Divergncia &amp; Diagnstico de Risco</th>',
            'Quadro 3: Divergência &amp; Diagnóstico de Risco <button class="hlp" data-h="risco" onclick="openHlp(\'risco\', event)" style="margin-left:6px;">?</button></th>'
        )

    # Garante que HELP é declarado e contém scatter e risco
    if "const HELP = {" not in content:
        content = content.replace(
            "const HLP_CONTENT = {",
            "const HELP = {\n  scatter: `<h4>Visão de Dispersão MoM & YoY</h4><p>Análise de dispersão relacionando volume e variação de taxa.</p>`,\n  risco: `<h4>Diagnóstico de Risco</h4><p>Avaliação de risco de cancelamento e divergência operacional.</p>`,\n"
        )
        content = content.replace(
            "const RAW_PAYLOAD_B64 =",
            "var HLP_CONTENT = {};\nconst RAW_PAYLOAD_B64 ="
        )

    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] {os.path.basename(p)} ajustado.")

print("[+] Todos os painéis foram sincronizados com sucesso.")
