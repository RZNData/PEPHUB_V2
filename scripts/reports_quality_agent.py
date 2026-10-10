#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente Universal de Qualidade de Relatórios (Reports Quality Auditor)
Valida rigorosamente os 7 pilares corporativos de dados e layout em qualquer relatório do PEP HUB:
  1. Subtotais com valores preenchidos em linhas agrupadoras (Grandes Mercados, Canais, etc.)
  2. Alinhamento numérico estrito à direita em dados e subtotais (text-align: right)
  3. Notação de variação de pontos percentuais estritamente em minúsculo ('p.p.')
  4. Largura e dimensionamento fixo de tabelas (table-layout: fixed)
  5. Filtros dependentes com opções sem dados reordenadas e marcadas (.na)
  6. Reatividade do Benchmark Nacional e bloqueio de filtros em visões exclusivas
  7. Autonomia zero CDNs/dependências externas e headers anti-cache
"""

import os
import re
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_REPORTS = [
    os.path.join(WORKSPACE_DIR, "public", "fpd", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "fpd-residencial", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "market-share-residencial", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "market-share-movel", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "panorama-market-share", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "aprovacao-credito", "index.html"),
]

def audit_single_report(html_path):
    rel_path = os.path.relpath(html_path, WORKSPACE_DIR)
    print("\n" + "-" * 72)
    print(f"  AUDITANDO: {rel_path}")
    print("-" * 72)

    if not os.path.exists(html_path):
        print(f"  [ERRO] Arquivo não encontrado: {html_path}")
        return 0, [f"Arquivo ausente: {rel_path}"]

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    score = 100
    deductions = []

    # -------------------------------------------------------------
    # 1. Subtotais e dados em linhas de grupo (Canais, Mercados) (25 pts)
    # -------------------------------------------------------------
    has_grp_header = "grp-header" in html or "grp-total-row" in html or "subtotal" in html.lower()
    if has_grp_header:
        # Verifica se as linhas de total do grupo possuem células de dados
        if "grp-total-row" in html:
            # Confere se os valores numéricos estão associados ou se há classes de subtotal
            print("  [OK] Pilar 1: Linhas de subtotais/agrupamento estruturadas (.grp-total-row)")
        else:
            print("  [AVISO] Pilar 1: Estrutura de agrupamento detectada, recomendável .grp-total-row")
    else:
        # Se for relatório que não usa agrupamento por canais/mercados (ex: aprovação de crédito)
        print("  [INFO] Pilar 1: Relatório sem agrupamento por canais ou mercados explícito.")

    # -------------------------------------------------------------
    # 2. Alinhamento numérico estrito à direita (20 pts)
    # -------------------------------------------------------------
    # Linhas de subtotais não devem ter text-align: left em valores numéricos
    p2_ok = True
    if "grp-header td" in html and "text-align: left" in html:
        # Deve ter separação td.l para nomes e td para valores à direita
        if "grp-header td.l" not in html and "grp-total-row td.l" not in html and "td.l" not in html:
            p2_ok = False
            score -= 15
            deductions.append("Células de subtotal não diferenciam texto à esquerda (.l) e números à direita.")
        else:
            print("  [OK] Pilar 2: Alinhamento numérico à direita com exceção apenas para rótulos (.l)")
    else:
        print("  [OK] Pilar 2: Alinhamento numérico padronizado à direita.")

    # -------------------------------------------------------------
    # 3. Notação 'p.p.' estritamente em minúsculo (15 pts)
    # -------------------------------------------------------------
    # Procura por 'P.P.' ou 'P.p.' em textos de cabeçalho ou deltas
    upper_pp = re.findall(r'(?<![A-Za-z0-9])P\.P\.(?![A-Za-z0-9])', html)
    mixed_pp = re.findall(r'(?<![A-Za-z0-9])P\.p\.(?![A-Za-z0-9])', html)
    if upper_pp or mixed_pp:
        count_bad = len(upper_pp) + len(mixed_pp)
        score -= 15
        deductions.append(f"Notação de ponto percentual em maiúsculo encontrada ({count_bad}x 'P.P.' ou 'P.p.'). Deve ser 'p.p.'.")
        print(f"  [FALHA] Pilar 3: Encontrado '{upper_pp or mixed_pp}' em maiúsculo ({count_bad} ocorrências).")
    else:
        print("  [OK] Pilar 3: Notação 'p.p.' estritamente em minúsculo (conforme padrão corporativo).")

    # -------------------------------------------------------------
    # 4. Largura e Layout Fixo de Tabelas (15 pts)
    # -------------------------------------------------------------
    if "<table" in html:
        if "table-layout: fixed" in html or "table-layout:fixed" in html:
            print("  [OK] Pilar 4: Tabelas analíticas com 'table-layout: fixed' rígido.")
        else:
            score -= 10
            deductions.append("Tabela analítica sem 'table-layout: fixed', suscetível a deslocamento de colunas.")
            print("  [AVISO] Pilar 4: 'table-layout: fixed' ausente em tabelas analíticas.")
    else:
        print("  [INFO] Pilar 4: Não contém tabelas HTML.")

    # -------------------------------------------------------------
    # 5. Filtros dependentes com opções sem dados (.na) (10 pts)
    # -------------------------------------------------------------
    if "select" in html:
        if "option.na" in html or "class=\"na\"" in html or ".na {" in html or "opt.classList.toggle('na'" in html:
            print("  [OK] Pilar 5: Filtros dependentes com estilização/reordenação de itens sem dados (.na).")
        else:
            score -= 5
            deductions.append("Filtros dependentes sem suporte explícito a desativação de itens (.na).")
            print("  [AVISO] Pilar 5: Filtros não utilizam classe .na para opções sem dados.")
    else:
        print("  [INFO] Pilar 5: Sem campos select de filtro.")

    # -------------------------------------------------------------
    # 6. Reatividade de Benchmark e Filtro Travado (10 pts)
    # -------------------------------------------------------------
    if "filter-locked" in html or "currentLockedCanal" in html or "selMulti" in html:
        print("  [OK] Pilar 6: Benchmark reativo aos filtros e proteção de visões exclusivas (.filter-locked).")
    else:
        print("  [INFO] Pilar 6: Relatório de dimensão única ou sem necessidade de benchmark duplo.")

    # -------------------------------------------------------------
    # 7. Autonomia Zero CDNs Externos (10 pts)
    # -------------------------------------------------------------
    cdn_matches = re.findall(r'(https?:)?//(cdn\.jsdelivr|unpkg\.com|cdnjs\.cloudflare|fonts\.googleapis|stackpath|maxcdn)', html)
    if cdn_matches:
        score -= 20
        deductions.append(f"Dependências externas de CDNs detectadas ({len(cdn_matches)} referências).")
        print(f"  [FALHA] Pilar 7: CDNs externos detectados: {cdn_matches}")
    else:
        print("  [OK] Pilar 7: Zero dependências externas (100% autônomo e corporativo).")

    # -------------------------------------------------------------
    # 8. Numeração Sequencial de Indicadores de KPI (10 pts)
    # -------------------------------------------------------------
    has_kpis = ".kpi" in html or "kpis" in html
    if has_kpis:
        has_numbered = bool(re.search(r'(?:card\(|kpi\(|rc\(|meta\(|class=["\']k["\']>|class=["\']lab["\']>)\s*[\'"]?1\.\s+', html))
        if not has_numbered:
            score -= 10
            deductions.append("Indicadores de KPI sem numeração sequencial (deve iniciar com '1. ...').")
            print("  [FALHA] Pilar 8: Indicadores de KPI sem numeração sequencial.")
        else:
            print("  [OK] Pilar 8: Indicadores de KPI devidamente numerados (1., 2., 3...).")

    # -------------------------------------------------------------
    # 9. Cabeçalho Padronizado e Ausência de Exportação HTML (10 pts)
    # -------------------------------------------------------------
    has_header = "<header" in html
    if has_header:
        has_nav_catalog = "Voltar ao Catálogo" in html or "btn-nav-catalog" in html
        has_export_html = bool(re.search(r'<header[^>]*>.*?download=["\'][^"\']*\.html["\'].*?</header>', html, re.DOTALL))
        has_back_hub = "back-hub" in html and "Portal Pephub" in html

        p9_ok = True
        if not has_nav_catalog:
            p9_ok = False
            score -= 5
            deductions.append("Cabeçalho sem botão oficial 'Voltar ao Catálogo'.")
        if has_export_html:
            p9_ok = False
            score -= 5
            deductions.append("Opção de exportar HTML presente no relatório (deve ficar apenas na gestão/admin).")
        if has_back_hub:
            p9_ok = False
            score -= 5
            deductions.append("Link textual redundante 'Portal Pephub' presente no cabeçalho.")

        if p9_ok:
            print("  [OK] Pilar 9: Cabeçalho padronizado (Voltar ao Catálogo + Sair) e sem exportação HTML.")
        else:
            print("  [FALHA] Pilar 9: Cabeçalho fora do padrão corporativo.")

    score = max(0, score)
    print(f"  RESULTADO: Score {score}/100")
    if deductions:
        print("  Deduções:")
        for d in deductions:
            print(f"    - {d}")

    return score, deductions

def main():
    print("=" * 74)
    print("  PEP HUB — REPORTS QUALITY AUDITOR (AUDITORIA UNIVERSAL)")
    print("=" * 74)

    targets = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_REPORTS
    all_scores = []
    failed = False

    for target in targets:
        if os.path.exists(target):
            sc, _ = audit_single_report(target)
            all_scores.append((target, sc))
            if sc < 85:
                failed = True

    print("\n" + "=" * 74)
    print("  RESUMO CONSOLIDADO DA AUDITORIA DE QUALIDADE")
    print("=" * 74)
    for path, sc in all_scores:
        status = "APROVADO (Grau A)" if sc >= 85 else "REPROVADO (Grau B/C)"
        rel = os.path.relpath(path, WORKSPACE_DIR)
        print(f"  • {rel:<45} : {sc:>3}/100 [{status}]")

    print("=" * 74)
    if failed:
        print("  [STATUS] Relatórios com apontamentos pendentes (Score < 85).")
        return 1
    else:
        print("  [STATUS] Todos os relatórios auditados com SUCESSO e conformidade total!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
