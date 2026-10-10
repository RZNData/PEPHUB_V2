#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Agente de Qualidade e Integridade do Painel FPD Executivo
Audita rigorosamente os 5 pilares do painel FPD:
  1. Classificacao correta de cidades por mercado (Grandes Mercados com Boa Vista, etc.)
  2. Classificacao correta de canais por tipo (Presenciais, Remotos e Outros)
  3. Logica de filtros dependentes e combinacao de produtos
  4. Divergencia de nomenclatura e alinhamento de colunas entre tabelas
  5. Reatividade instantanea dos filtros (onchange + fallback do botao)

Retorna Score: XX/100 e exit code 0 (Aprovado >= 90) ou 1 (Reprovado).
"""

import os
import re
import sys
import json

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_HTML = os.path.join(WORKSPACE_DIR, "relatorios", "fpd_residencial", "index.html")
PUBLIC_HTML = os.path.join(WORKSPACE_DIR, "public", "fpd-residencial", "index.html")
BUILD_SCRIPT = os.path.join(WORKSPACE_DIR, "relatorios", "fpd_residencial", "scripts", "build.py")

EXPECTED_GM = {"ANANINDEUA", "BELEM", "BOA VISTA", "MACAPA", "MANAUS", "SANTANA", "SAO LUIS"}
EXPECTED_MD = {"CASTANHAL", "CAXIAS", "IMPERATRIZ", "MARABA", "PARAGOMINAS", "PARAUAPEBAS", "TIMON"}

EXPECTED_CANAIS_PRESENCIAIS = [
    'Agente Autorizado', 'Porta Porta', 'Lojas Proprias', 'Varejo',
    'Distribuidor', 'Canais Exclusivo Empresas'
]
EXPECTED_CANAIS_REMOTOS = ['Ativo', 'Receptivo', 'Canais Eletronicos']
EXPECTED_CANAIS_OUTROS = ['Outros']

EXPECTED_METRIC_BUTTONS = [
    '% FPD 60 DIAS',
    '% FPD 30 DIAS (Prevenção)',
    'QTD FPD',
    'Instalação',
    'Todas as Métricas'
]

def audit_fpd():
    print()
    print("=" * 74)
    print("  PEP HUB — AGENTE DE QUALIDADE E CONFORMIDADE DO FPD EXECUTIVO")
    print("=" * 74)

    if not os.path.exists(REPORT_HTML):
        print(f"  [ERRO CRITICO] Arquivo nao encontrado: {REPORT_HTML}")
        print("  Score: 0/100")
        return 1

    with open(REPORT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    with open(BUILD_SCRIPT, "r", encoding="utf-8") as f:
        build_code = f.read()

    score = 100
    deductions = []
    checks = []

    # -------------------------------------------------------------
    # PILAR 1: Classificacao correta de cidades por mercado (20 pts)
    # -------------------------------------------------------------
    p1_ok = True
    # 1.1 Boa Vista em Grandes Mercados no build.py
    if '"BOA VISTA"' not in build_code or 'CIDADES_GRANDES' not in build_code:
        p1_ok = False
        deductions.append((-10, "CIDADES_GRANDES no build.py nao contem 'BOA VISTA'"))
    else:
        # Verificar se Boa Vista está em CIDADES_GRANDES
        m_gm = re.search(r'CIDADES_GRANDES\s*=\s*\[(.*?)\]', build_code)
        if not m_gm or 'BOA VISTA' not in m_gm.group(1):
            p1_ok = False
            deductions.append((-10, "BOA VISTA ausente de CIDADES_GRANDES"))
    
    # 1.2 Sem Cabo nao deve conter Boa Vista
    m_sc = re.search(r'CIDADES_SEM_CABO\s*=\s*\[(.*?)\]', build_code)
    if m_sc and 'BOA VISTA' in m_sc.group(1):
        p1_ok = False
        deductions.append((-10, "BOA VISTA ainda consta indevidamente em CIDADES_SEM_CABO"))

    # 1.3 Todas as 7 cidades GM estao presentes
    for c in EXPECTED_GM:
        if c not in html:
            p1_ok = False
            deductions.append((-5, f"Cidade GM '{c}' nao encontrada no HTML"))

    checks.append(("Pilar 1: Cidades por Mercado (Boa Vista em GM)", p1_ok, 20))

    # -------------------------------------------------------------
    # PILAR 2: Classificacao de canal por tipo (20 pts)
    # -------------------------------------------------------------
    p2_ok = True
    for cp in EXPECTED_CANAIS_PRESENCIAIS:
        if cp not in build_code:
            p2_ok = False
            deductions.append((-4, f"Canal presencial '{cp}' ausente das definicoes oficiais"))

    for cr in EXPECTED_CANAIS_REMOTOS:
        if cr not in build_code:
            p2_ok = False
            deductions.append((-4, f"Canal remoto '{cr}' ausente das definicoes oficiais"))

    # Verificar presenca dos grupos nas tabelas de canal
    if 'Canais Presenciais' not in html or 'Canais Remotos' not in html or 'Outros Canais' not in html:
        p2_ok = False
        deductions.append((-10, "Tabelas de canais nao apresentam os cabecalhos de separacao (Presenciais, Remotos, Outros)"))

    if 'grp-presencial' not in html or 'grp-remoto' not in html or 'grp-outros' not in html:
        p2_ok = False
        deductions.append((-5, "Classes CSS de separacao de canal (grp-presencial, grp-remoto, grp-outros) ausentes"))

    checks.append(("Pilar 2: Classificacao de Canais (Presenciais/Remotos/Outros)", p2_ok, 20))

    # -------------------------------------------------------------
    # PILAR 3: Logica de filtros & Combinacao de Produtos (20 pts)
    # -------------------------------------------------------------
    p3_ok = True
    # 3.1 Filtro de Combinacao de Produtos presente no drawer
    if 'selCombinacao' not in html or 'Combinação de Produtos' not in html:
        p3_ok = False
        deductions.append((-8, "Filtro de Combinacao de Produtos nao encontrado no HTML"))

    # 3.2 Combinacao presente no activeFilters e no cubo
    if 'combinacoes' not in html or 'activeFilters.combinacoes' not in html:
        p3_ok = False
        deductions.append((-6, "Estado activeFilters.combinacoes ou D.combinacoes ausente"))

    # 3.3 Filtros dependentes com opcoes invalidas no fim (.na)
    if 'refreshAvailabilityUI' not in html and 'refreshAvailability' not in html:
        p3_ok = False
        deductions.append((-6, "Funcao de atualizacao de disponibilidade dependente nao identificada"))

    if 'option.na' not in html and '.na' not in html:
        p3_ok = False
        deductions.append((-4, "Estilizacao para opcoes indisponiveis (.na) ausente"))

    checks.append(("Pilar 3: Filtros Dependentes & Combinacao de Produtos", p3_ok, 20))

    # -------------------------------------------------------------
    # PILAR 4: Nomenclatura e Alinhamento de Colunas (20 pts)
    # -------------------------------------------------------------
    p4_ok = True
    # 4.1 Botoes de visao com nomenclaturas padronizadas
    # Procurar por botoes antigos ou divergentes
    divergencias = []
    if 'FPD 60 Dias</button>' in html or 'FPD60</button>' in html:
        divergencias.append("Rotulo divergente de FPD 60 em botao")
    if 'FPD 30 Dias</button>' in html or 'FPD30</button>' in html:
        divergencias.append("Rotulo divergente de FPD 30 em botao")
    if 'Inadimplentes</button>' in html or 'Volume</button>' in html:
        divergencias.append("Rotulo divergente de QTD em botao")

    if divergencias:
        p4_ok = False
        for d in divergencias:
            deductions.append((-5, d))

    # 4.2 Alinhamento estrito entre tblCanal e tblCanalBrasil
    if '#tblCanal, #tblCanalBrasil' not in html and ('#tblCanal' not in html or '#tblCanalBrasil' not in html):
        p4_ok = False
        deductions.append((-10, "CSS nao contem seletores de alinhamento rigido para #tblCanal e #tblCanalBrasil"))

    if 'table-layout: fixed' not in html:
        p4_ok = False
        deductions.append((-6, "table-layout: fixed ausente para garantia de correspondencia de colunas"))

    checks.append(("Pilar 4: Padronizacao de Nomenclatura & Alinhamento de Colunas", p4_ok, 20))

    # -------------------------------------------------------------
    # PILAR 5: Reatividade e Funcionamento dos Filtros (20 pts)
    # -------------------------------------------------------------
    p5_ok = True
    # 5.1 selects com onchange ativando instantaneamente
    if 'onchange="handleFilterChange(' not in html and 'onchange="applyFilters' not in html:
        p5_ok = False
        deductions.append((-10, "Selects de filtro nao disparam ativacao instantanea no onchange"))

    # 5.2 Botao Aplicar Filtros como fallback
    if 'onclick="applyFilters()"' not in html:
        p5_ok = False
        deductions.append((-5, "Botao de fallback 'Aplicar Filtros' ausente"))

    # 5.3 Chips de filtros ativos
    if 'activeFilterChips' not in html or 'renderChips' not in html:
        p5_ok = False
        deductions.append((-5, "Sistema de chips de filtros ativos ausente"))

    checks.append(("Pilar 5: Reatividade Instantanea dos Filtros & Fallback", p5_ok, 20))

    # -------------------------------------------------------------
    # PILAR 6: Ajustes Executivos dos 3 Novos Requisitos
    # -------------------------------------------------------------
    p6_ok = True
    # 6.1 Linhas de grupo com dados consolidados
    if 'grp-total-row' not in html or 'calcSeriesFromAcc(gAcc)' not in html or 'calcSeriesFromAcc(brGAcc)' not in html:
        p6_ok = False
        deductions.append((-10, "Linhas de grupos de canal nao estao calculando/exibindo subtotais consolidados"))

    # 6.2 Benchmark Brasil reativo em todas as visões
    if 'br_cube_rows' not in html or 'currentBrTotal' not in html or 'currentBrCanais' not in html:
        p6_ok = False
        deductions.append((-10, "Benchmark Brasil nao esta configurado para reatividade universal via cubo multidimensional"))

    # 6.3 Trava de canal nas visões exclusivas
    if 'tabCanalLockMap' not in html or 'currentLockedCanal' not in html or 'filter-locked' not in html:
        p6_ok = False
        deductions.append((-10, "Mecanismo de bloqueio estrito de canal nas visoes exclusivas ausente"))

    checks.append(("Pilar 6: Totais de Grupo, Benchmark BR Reativo e Trava de Canal", p6_ok, 20))

    # -------------------------------------------------------------
    # PILAR 7: Subtotais de Mercados (Visoes 2 a 6), Alinhamento e p.p. Minusculo
    # -------------------------------------------------------------
    p7_ok = True
    # 7.1 Linhas de grupos de cidades (Grandes Mercados, etc.) com valores em todas as visões
    if 'groupItems.forEach' not in html or 'acc: cidAccs[idx]' not in html:
        p7_ok = False
        deductions.append((-10, "Linhas de agrupamentos de cidades (Grandes Mercados / MD) nas visoes 2 a 6 nao possuem acumuladores consolidados"))

    # 7.2 Alinhamento a direita nas celulas numericas das linhas de grupo
    if 'tbody tr.grp-total-row td {\n  background: #edf1f5 !important;\n  font-weight: 700;\n  text-align: right;' not in html and 'text-align: right' not in html:
        p7_ok = False
        deductions.append((-5, "Celulas numericas das linhas de grupo nao estao alinhadas a direita"))

    # 7.3 Comparativo p.p. estritamente em minusculo
    if 'text-transform: lowercase' not in html or 'text-transform: uppercase' in html.split('.d-val')[0] and 'tbody tr.grp-header td {\n  background: #edf1f5;\n  color: var(--nav);\n  font-weight: 700;\n  text-transform: uppercase;' in html:
        p7_ok = False
        deductions.append((-5, "Comparativo p.p. pode ser exibido indevidamente em maiusculo (P.P.)"))

    checks.append(("Pilar 7: Mercados com Totais (Visoes 2-6), Alinhamento Direita & p.p. Minusculo", p7_ok, 20))

    # Calcular score final
    for pts, reason in deductions:
        score += pts

    score = max(0, min(100, score))

    print(f"\n  [AUDITORIA EXECUTIVA DE CONFORMIDADE]")
    for label, ok, max_p in checks:
        icon = "[OK]" if ok else "[X ]"
        print(f"  {icon} {label}")

    if deductions:
        print("\n  [APONTAMENTOS DETECTADOS]:")
        for pts, reason in deductions:
            print(f"    - ({pts} pts) {reason}")
    else:
        print("\n  Nenhum apontamento detectado! Todos os 5 pilares atendidos com excelencia.")

    print("\n" + "-" * 74)
    print(f"  Pontuacao FPD Quality Agent: {score}/100")
    print("-" * 74)

    status = "APROVADO" if score >= 90 else "REPROVADO"
    print(f"  Status Final: {status} (Minimo requerido: 90/100)\n")
    print("=" * 74)

    return 0 if score >= 90 else 1

if __name__ == "__main__":
    sys.exit(audit_fpd())
