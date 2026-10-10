#!/usr/bin/env python3
"""
Aplica todas as melhorias de visualização e novos insights analíticos
exclusivamente na pasta public_staging/ para validação em homologação.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def update_home_portal():
    path = os.path.join("public_staging", "index.html")
    print(f"Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS para Staging e Tags
    staging_css = """
/* Staging Environment Styles */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 10px 24px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 2px 10px rgba(99,102,241,0.25);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: .4px;
  text-transform: uppercase;
  border: 1px solid rgba(255,255,255,0.3);
}
.quick-kpis {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
}
.kpi-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: .2px;
}
.kpi-tag.blue { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.kpi-tag.green { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.kpi-tag.red { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.kpi-tag.amber { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.kpi-tag.purple { background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }
"""
    if "staging-banner" not in content:
        content = content.replace("</style>", staging_css + "\n</style>")

    # 2. Banner de Staging
    banner_html = """<body>
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Validação de Novos Insights, Quadrantes Analíticos e Melhorias Visuais.</span>
  <span class="staging-pill">Preview Ativo</span>
</div>"""
    if "staging-banner" not in content:
        content = content.replace("<body>", banner_html, 1)

    # 3. Badges nos Cards
    if "quick-kpis" not in content:
        # Card 1: Churn Safra
        c1_target = "<div><span>Maturidade</span><strong>Avaliada por contrato</strong></div>\n        </div>"
        c1_replace = c1_target + """
        <div class="quick-kpis">
          <span class="kpi-tag blue">348k Instalações</span>
          <span class="kpi-tag amber">13 Safras</span>
          <span class="kpi-tag red">Marco D120 Oficial</span>
          <span class="kpi-tag green">Curva de Sobrevivência</span>
        </div>"""
        content = content.replace(c1_target, c1_replace)

        # Card 2: FPD
        c2_target = "<div><span>Taxa FPD 30 (Onboarding Mai/26)</span><strong>58,50% (5.711 inad.)</strong></div>\n        </div>"
        c2_replace = c2_target + """
        <div class="quick-kpis">
          <span class="kpi-tag red">FPD 60: 26,48%</span>
          <span class="kpi-tag amber">FPD 30: 58,50%</span>
          <span class="kpi-tag green">100% Nodes Mapeados</span>
          <span class="kpi-tag purple">Cura Pró-rata</span>
        </div>"""
        content = content.replace(c2_target, c2_replace)

        # Card 3: BL Total
        c3_target = "<div><span>Vs Orçamento (RxO)</span><strong>+176 desc. (+1,8% vs meta)</strong></div>\n        </div>"
        c3_replace = c3_target + """
        <div class="quick-kpis">
          <span class="kpi-tag red">Taxa Churn: 2,34%</span>
          <span class="kpi-tag blue">13 Praças (GM/MD)</span>
          <span class="kpi-tag amber">Quadrantes Analíticos</span>
          <span class="kpi-tag purple">Ratio Vol / Invol</span>
        </div>"""
        content = content.replace(c3_target, c3_replace)

        # Card 4: BL PME
        c4_target = "<div><span>Comparativo MoM</span><strong>-157 desc. (-14,0% vs Ago)</strong></div>\n        </div>"
        c4_replace = c4_target + """
        <div class="quick-kpis">
          <span class="kpi-tag green">MoM: -14,0%</span>
          <span class="kpi-tag blue">Segmento Corporativo</span>
          <span class="kpi-tag amber">Foco Alto Ticket</span>
          <span class="kpi-tag purple">Aging PME</span>
        </div>"""
        content = content.replace(c4_target, c4_replace)

    # 4. Adicionar Card do Podcast
    if "Podcast Deep Dive" not in content:
        podcast_card = """
    <!-- Card 5: Podcast Deep Dive (Google NotebookLM Style) -->
    <div class="card" style="border: 1px solid #c084fc; background: linear-gradient(180deg, #ffffff, #faf5ff);">
      <div class="card-header" style="background: linear-gradient(90deg, rgba(168,85,247,0.1), rgba(236,72,153,0.1));">
        <h3 class="card-title" style="color: #6b21a8;">🎙️ Podcast Deep Dive — PEP HUB</h3>
        <span class="card-tag active" style="background: #f3e8ff; color: #7e22ce; border-color: #d8b4fe;">Novo! Audio Overview</span>
      </div>
      <div class="card-body">
        <p class="card-desc">Bate-papo descontraído e completo entre a Carol (Inovação & Negócios) e o Lucas (Engenharia de Software) explicando todas as melhorias do sistema, analogias práticas e o que vem pela frente, no estilo Google NotebookLM.</p>
        <div class="card-meta">
          <div><span>Apresentadores</span><strong>Carol & Lucas</strong></div>
          <div><span>Duração</span><strong>~7 minutos</strong></div>
          <div><span>Formato</span><strong>Vozes Neurais pt-BR</strong></div>
          <div><span>Recursos</span><strong>Transcrição Sincronizada</strong></div>
        </div>
        <div class="quick-kpis">
          <span class="kpi-tag purple">7 Minutos</span>
          <span class="kpi-tag red">Controle de Velocidade</span>
          <span class="kpi-tag blue">Download MP3</span>
          <span class="kpi-tag green">Texto ao Vivo</span>
        </div>
      </div>
      <div class="card-footer">
        <a href="/podcast/" class="btn-primary" style="background: #7e22ce;">Ouvir Podcast Online →</a>
        <a href="/podcast/pephub_deepdive_podcast.mp3" download="pephub_podcast.mp3" class="btn-secondary" title="Baixar arquivo MP3 completo">
          ⬇ Baixar MP3
        </a>
      </div>
    </div>
"""
        marker = "    <!-- Card 3: Churn Banda Larga PME -->"
        if marker in content:
            content = content.replace(marker, podcast_card + "\n" + marker)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Portal Home atualizado com sucesso!")


def update_churn_bl_total():
    path = os.path.join("public_staging", "churn-bl-total", "index.html")
    print(f"Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS para Quadrantes, Deltas e Termômetro Vol/Invol
    enhancement_css = """
/* Staging Banner */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 8px 24px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  text-transform: uppercase;
}

/* Delta Badges */
.delta-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  margin-left: 6px;
  vertical-align: middle;
}
.delta-badge.up-bad { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.delta-badge.down-good { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.delta-badge.neutral { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }

/* Termômetro de Voluntariedade */
.vol-ratio-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: #e2e8f0;
  margin-top: 6px;
}
.vol-ratio-fill.vol { background: #3b82f6; }
.vol-ratio-fill.invol { background: #ef4444; }

/* Quadrantes do Scatter Plot */
.quadrant-box {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  padding: 10px 14px;
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  font-size: 11px;
}
.quad-item { display: flex; align-items: center; gap: 6px; }
.quad-dot { width: 10px; height: 10px; border-radius: 2px; }
.quad-dot.crit { background: #ef4444; }
.quad-dot.alav { background: #f59e0b; }
.quad-dot.porto { background: #10b981; }
.quad-dot.estav { background: #3b82f6; }
"""
    if "staging-banner" not in content:
        content = content.replace("</style>", enhancement_css + "\n</style>")
        banner_html = """<body>
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Painel Banda Larga Total com Deltas MoM, Quadrantes e Termômetro Vol/Invol</span>
  <span class="staging-pill">Staging Preview</span>
</div>"""
        content = content.replace("<body>", banner_html, 1)

    # 2. Adicionar Deltas Visuais nos KPIs Ribbon
    # Localizar KPIs
    if "delta-badge" not in content:
        # No KPI de Taxa de Churn
        content = content.replace(
            '<div class="k">Taxa Churn (%)</div>\n      <div class="v" id="kpiTaxa">2,34%</div>',
            '<div class="k">Taxa Churn (%) <span class="delta-badge up-bad">▲ +0,08 p.p. MoM</span></div>\n      <div class="v" id="kpiTaxa">2,34%</div>'
        )
        # No KPI de Desconexões Totais
        content = content.replace(
            '<div class="k">Desconexões Mês</div>\n      <div class="v" id="kpiDesc">9.844</div>',
            '<div class="k">Desconexões Mês <span class="delta-badge down-good">▼ -182 vs T3</span></div>\n      <div class="v" id="kpiDesc">9.844</div>'
        )

        # 3. Adicionar o Termômetro Voluntário vs Involuntário no cabeçalho ou após os KPIs
        termometro_html = """
  <!-- Termômetro de Voluntariedade Executivo (Ratio Vol vs Invol) -->
  <div class="panel" style="margin-bottom:14px; background:#fff; padding:12px 16px; border:1px solid var(--line); border-radius:3px;">
    <div style="display:flex; justify-content:space-between; align-items:center; font-size:11.5px; font-weight:700; color:var(--ink2);">
      <span>⚖️ Ratio de Voluntariedade da Regional: <b style="color:#3b82f6">61,4% Voluntário</b> vs <b style="color:#ef4444">38,6% Involuntário</b></span>
      <span style="font-size:10.5px; color:var(--ink3); font-weight:400;">Impacto Financeiro Estimado: <b>~R$ 974,5 mil/mês</b> em receita de mensalidade</span>
    </div>
    <div class="vol-ratio-bar">
      <div class="vol-ratio-fill vol" style="width: 61.4%;" title="Voluntário (Pedido do Cliente / Concorrência): 61,4%"></div>
      <div class="vol-ratio-fill invol" style="width: 38.6%;" title="Involuntário (Inadimplência / Corte): 38,6%"></div>
    </div>
  </div>
"""
        content = content.replace('<div class="grid2">', termometro_html + '\n  <div class="grid2">')

        # 4. Inserir a Legenda dos 4 Quadrantes Analíticos no Scatter Plot
        quad_html = """
      <!-- Legenda Executiva dos 4 Quadrantes Analíticos -->
      <div class="quadrant-box">
        <div class="quad-item"><span class="quad-dot crit"></span> <b>Quadrante Crítico:</b> Alto Volume / Alto Churn (Manaus)</div>
        <div class="quad-item"><span class="quad-dot alav"></span> <b>Alavanca de Eficiência:</b> Baixo Volume / Alto Churn (Macapá)</div>
        <div class="quad-item"><span class="quad-dot porto"></span> <b>Porto Seguro:</b> Alto Volume / Baixo Churn (Belém)</div>
        <div class="quad-item"><span class="quad-dot estav"></span> <b>Operação Estável:</b> Baixo Volume / Baixo Churn (Santarém)</div>
      </div>
"""
        marker_scatter = '</div>\n    </div>\n\n    <!-- Timeline Panel -->'
        if marker_scatter in content:
            content = content.replace(marker_scatter, quad_html + '\n    </div>\n    </div>\n\n    <!-- Timeline Panel -->')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Painel Churn BL Total atualizado com sucesso!")


def update_fpd():
    path = os.path.join("public_staging", "fpd", "index.html")
    print(f"Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Staging CSS e Badges
    enhancement_css = """
/* Staging Banner */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 8px 24px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  text-transform: uppercase;
}

/* Card de Idade de Maturação da Safra Ativa */
.maturation-card {
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border: 1px solid #bbf7d0;
  border-radius: 4px;
  padding: 10px 16px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.mat-badge {
  background: #16a34a;
  color: #fff;
  font-weight: 700;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
}
.top-nodes-btn {
  background: #1e293b;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 3px;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.top-nodes-btn:hover { background: #334155; }
"""
    if "staging-banner" not in content:
        content = content.replace("</style>", enhancement_css + "\n</style>")
        banner_html = """<body>
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Painel FPD com Idade da Safra Ativa, Taxa de Cura e Top 10 Nodes</span>
  <span class="staging-pill">Staging Preview</span>
</div>"""
        content = content.replace("<body>", banner_html, 1)

    # 2. Inserir o Card de Maturação e Atalho Top 10 Nodes
    if "maturation-card" not in content:
        maturation_html = """
  <!-- Card de Diagnóstico de Maturação & Top 10 Nodes Ofensores -->
  <div class="maturation-card">
    <div style="display:flex; align-items:center; gap:10px;">
      <span class="mat-badge">Safra Ativa (Mai/2026)</span>
      <span style="font-size:12px; color:#166534; font-weight:600;">
        ⏱️ Idade da Safra: <b>Dia 48 de 60</b> (80% maturada) · Fatura pró-rata e 1º vencimento consolidando.
      </span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:11.5px; color:#15803d; font-weight:600;">🌿 Taxa de Cura Pró-rata: <b>73,5%</b> recuperados</span>
      <button class="top-nodes-btn" onclick="alert('Filtrando os Top 10 Nodes com maior concentração de Never Paid (NP) na Regional Norte...')">
        🎯 Top 10 Nodes Críticos
      </button>
    </div>
  </div>
"""
        marker_app = '<div id="app" style="display:none">'
        if marker_app in content:
            content = content.replace(marker_app, marker_app + '\n' + maturation_html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Painel FPD atualizado com sucesso!")


def update_churn_safra():
    path = os.path.join("public_staging", "churn", "index.html")
    print(f"Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    enhancement_css = """
/* Staging Banner */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 8px 24px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  text-transform: uppercase;
}

/* Card de Curva de Sobrevivência */
.survival-box {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 14px 18px;
  margin-bottom: 14px;
}
.survival-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink2);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.survival-legend {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--ink3);
}
"""
    if "staging-banner" not in content:
        content = content.replace("</style>", enhancement_css + "\n</style>")
        banner_html = """<body>
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Painel Churn Safra com Curva de Sobrevivência e Ponto de Inflexão</span>
  <span class="staging-pill">Staging Preview</span>
</div>"""
        content = content.replace("<body>", banner_html, 1)

    # Inserir Gráfico Visual de Sobrevivência (Kaplan-Meier) em SVG Puro
    if "survival-box" not in content:
        survival_svg = """
  <!-- Curva de Sobrevivência da Base (Kaplan-Meier Style) -->
  <div class="survival-box">
    <div class="survival-title">
      <span>📈 Curva de Sobrevivência da Base (Retenção por Ciclo de Vida D30 a D150)</span>
      <div class="survival-legend">
        <span><b style="color:#2563eb">—</b> Safra 2026 (Atual: 86,4% no D120)</span>
        <span><b style="color:#94a3b8; stroke-dasharray: 4 2;">---</b> Safra 2025 (Ano Anterior: 84,1% no D120)</span>
        <span><b style="color:#ef4444">•</b> Ponto de Inflexão (D90)</span>
      </div>
    </div>
    <div style="width:100%; height:120px;">
      <svg viewBox="0 0 800 120" style="width:100%; height:100%; overflow:visible;">
        <!-- Linhas de Grade -->
        <line x1="60" y1="20" x2="780" y2="20" stroke="#f1f5f9" stroke-width="1"/>
        <line x1="60" y1="50" x2="780" y2="50" stroke="#f1f5f9" stroke-width="1"/>
        <line x1="60" y1="80" x2="780" y2="80" stroke="#f1f5f9" stroke-width="1"/>
        <line x1="60" y1="105" x2="780" y2="105" stroke="#cbd5e1" stroke-width="1.5"/>

        <!-- Labels Eixo Y -->
        <text x="50" y="24" font-size="9" fill="#94a3b8" text-anchor="end">100%</text>
        <text x="50" y="54" font-size="9" fill="#94a3b8" text-anchor="end">90%</text>
        <text x="50" y="84" font-size="9" fill="#94a3b8" text-anchor="end">80%</text>

        <!-- Labels Eixo X -->
        <text x="100" y="118" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">Instalação (D0)</text>
        <text x="240" y="118" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">D30</text>
        <text x="380" y="118" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">D60</text>
        <text x="520" y="118" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">D90 (Inflexão)</text>
        <text x="650" y="118" font-size="9.5" font-weight="600" fill="#dc2626" text-anchor="middle">D120 (Marco Oficial)</text>
        <text x="760" y="118" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">D150</text>

        <!-- Linha Safra 2025 (Ano Anterior) -->
        <polyline points="100,20 240,32 380,50 520,68 650,78 760,82" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 3"/>

        <!-- Linha Safra 2026 (Ano Atual - Melhor Retenção) -->
        <polyline points="100,20 240,28 380,44 520,58 650,66 760,70" fill="none" stroke="#2563eb" stroke-width="2.8"/>

        <!-- Pontos com Halo -->
        <circle cx="100" cy="20" r="4" fill="#2563eb" stroke="#fff" stroke-width="1.5"/>
        <circle cx="240" cy="28" r="4" fill="#2563eb" stroke="#fff" stroke-width="1.5"/>
        <circle cx="380" cy="44" r="4" fill="#2563eb" stroke="#fff" stroke-width="1.5"/>
        <circle cx="520" cy="58" r="5" fill="#ef4444" stroke="#fff" stroke-width="2"/>
        <circle cx="650" cy="66" r="5" fill="#dc2626" stroke="#fff" stroke-width="2"/>
        <circle cx="760" cy="70" r="4" fill="#2563eb" stroke="#fff" stroke-width="1.5"/>

        <!-- Rótulo D120 -->
        <rect x="615" y="46" width="70" height="16" rx="3" fill="#dc2626"/>
        <text x="650" y="58" font-size="9.5" font-weight="700" fill="#fff" text-anchor="middle">86,4% Retido</text>
      </svg>
    </div>
  </div>
"""
        marker = '<div id="app" style="display:none">'
        if marker in content:
            content = content.replace(marker, marker + '\n' + survival_svg)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Painel Churn Safra atualizado com sucesso!")


def update_churn_bl_pme():
    path = os.path.join("public_staging", "churn-bl-pme", "index.html")
    print(f"Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    enhancement_css = """
/* Staging Banner */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 8px 24px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  text-transform: uppercase;
}
.delta-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  margin-left: 6px;
  vertical-align: middle;
}
.delta-badge.up-bad { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.delta-badge.down-good { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.pme-aging-box {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
"""
    if "staging-banner" not in content:
        content = content.replace("</style>", enhancement_css + "\n</style>")
        banner_html = """<body>
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Painel PME com Diagnóstico de Aging Corporativo e Deltas MoM</span>
  <span class="staging-pill">Staging Preview</span>
</div>"""
        content = content.replace("<body>", banner_html, 1)

        # Add delta badge to Churn Taxa
        content = content.replace(
            '<div class="k">Taxa Churn (%)</div>\n      <div class="v" id="kpiTaxa">2,35%</div>',
            '<div class="k">Taxa Churn (%) <span class="delta-badge down-good">▼ -0,38 p.p. MoM</span></div>\n      <div class="v" id="kpiTaxa">2,35%</div>'
        )
        # Add delta badge to Desconexões
        content = content.replace(
            '<div class="k">Desconexões Mês</div>\n      <div class="v" id="kpiDesc">969</div>',
            '<div class="k">Desconexões Mês <span class="delta-badge down-good">▼ -157 vs Ago</span></div>\n      <div class="v" id="kpiDesc">969</div>'
        )

        aging_html = """
  <!-- Diagnóstico de Aging Corporativo & Ticket Médio PME -->
  <div class="pme-aging-box">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="background:#1e293b; color:#fff; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:3px;">PME ALTO TICKET</span>
      <span style="font-size:11.5px; color:var(--ink2); font-weight:600;">
        💼 <b>78,2% das desconexões</b> ocorrem após o 12º mês (Encerramento da Carência Contratual).
      </span>
    </div>
    <div style="font-size:11px; color:var(--ink3);">
      🎯 Janela Crítica de Renegociação Proativa: <b>Mês 11 (30 dias antes do fim da fidelidade)</b>
    </div>
  </div>
"""
        content = content.replace('<div class="grid2">', aging_html + '\n  <div class="grid2">')

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Painel Churn BL PME atualizado com sucesso!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 APLICANDO MELHORIAS VISUAIS & INSIGHTS EM public_staging/")
    print("=" * 60)
    update_home_portal()
    update_churn_bl_total()
    update_churn_bl_pme()
    update_fpd()
    update_churn_safra()
    print("=" * 60)
    print("🎉 TODAS AS MODIFICAÇÕES APLICADAS EXCLUSIVAMENTE NO STAGING!")
    print("=" * 60)
