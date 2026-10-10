import re

with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    template = f.read()

# 1. Update Title and Header
template = re.sub(
    r'<title>.*?</title>',
    '<title>Painel Executivo FPD — Regional Norte (Claro)</title>',
    template, flags=re.IGNORECASE
)
template = re.sub(
    r'<h1>.*?</h1>',
    '<h1>Painel Executivo FPD — Regional Norte <span style="font-size:12px;font-weight:400;color:var(--ink3)">13 Safras (Mai/25 a Mai/26) · Indicador Oficial FPD 60 Claro</span></h1>',
    template, flags=re.IGNORECASE
)
template = re.sub(
    r'<span>posi&ccedil;&atilde;o.*?(?=</span>)',
    '<span>posição <b>Setembro / 2026</b></span>',
    template, flags=re.IGNORECASE
)
template = re.sub(
    r'<span>escopo.*?(?=</span>)',
    '<span>escopo <b>Regional Norte (AM · PA · MA · AP)</b> · <b>143.527 instalações</b></span>',
    template, flags=re.IGNORECASE
)

# 2. Grid2 (Safra + Scatter)
p_grid2 = template.find('<div class="grid2">')
p_mapa = template.find('<div class="panel">\n  <h2>Mapa de concentração')
if p_mapa == -1:
    p_mapa = template.find('<div class="panel">\r\n  <h2>Mapa de concentração')

new_grid2 = """<div class="grid2">
  <div class="panel">
    <h2>EVOLUÇÃO DO FPD SAFRA A SAFRA <span class="note">histórico 13 safras (FPD 60 oficial vs FPD 30 Onboarding)</span><button class="hlp" data-h="safra">?</button></h2>
    <div class="pbody" style="padding-bottom:4px"><div id="chSafra"></div></div>
    <div class="lgd">
      <span><i style="background:#3b4b5e"></i>Instalações</span>
      <span><i style="background:#e03131"></i>★ Taxa FPD 60 (Oficial Claro)</span>
      <span><i style="background:#7d4bb0;border-bottom:1px dashed #7d4bb0"></i>Taxa FPD 30 (Onboarding / Pró-rata)</span>
    </div>
  </div>
  <div class="panel">
    <h2>DISPERSÃO MoM & YoY <span class="note">evolução da taxa FPD 60 vs volume</span>
      <span class="tabs" id="tabsScatComp">
        <button class="on" data-m="mom">vs Safra Anterior (MoM)</button>
        <button data-m="yoy">vs Safra Base (YoY)</button>
      </span>
      <span class="tabs" id="tabsScatDim" style="margin-left:6px">
        <button class="on" data-d="cidade">Cidade</button>
        <button data-d="canal_grupo">Canal</button>
        <button data-d="parceiro">Parceiro</button>
        <button data-d="produto">Produto</button>
        <button data-d="vendedor">Vendedor</button>
      </span>
      <button class="hlp" data-h="scatter">?</button>
    </h2>
    <div class="pbody" style="padding-bottom:4px"><div id="chScatter"></div></div>
    <div class="lgd">
      <span><i style="background:#2f7d5d"></i>Melhora FPD (redução p.p.)</span>
      <span><i style="background:#c0392b"></i>Piora FPD (aumento p.p.)</span>
      <span style="margin-left:auto;font-size:11px;color:var(--ink3)">Tamanho da bolha = volume de instalações</span>
    </div>
  </div>
</div>\n\n"""

template = template[:p_grid2] + new_grid2 + template[p_mapa:]

# 3. Map Selects
map_metric_html = """          <select id="mapMetric">
            <optgroup label="Volume e Adimplência">
              <option value="vol" selected>Concentração de instalações</option>
              <option value="adimp">Clientes adimplentes (1ª fatura em dia)</option>
              <option value="altorisco">Instalações em Alto Risco (FX_RISCO_NV)</option>
            </optgroup>
            <optgroup label="Indicadores FPD (Taxa %)">
              <option value="c60">★ Taxa FPD 60 (Marco Oficial Claro)</option>
              <option value="c30">Taxa FPD 30 (Pré-FPD / Onboarding)</option>
              <option value="c90">Taxa FPD 90 (Pré-Churn)</option>
              <option value="c120">Taxa FPD 120</option>
              <option value="c150">Taxa FPD 150</option>
            </optgroup>
          </select>"""
template = re.sub(r'<select id="mapMetric">.*?</select>', map_metric_html, template, count=1, flags=re.DOTALL)

dot_show_html = """          <select id="dotShow">
            <option value="todos">Todas as instalações</option>
            <option value="c60">Somente ★ Inadimplentes FPD 60</option>
            <option value="c30">Somente Inadimplentes FPD 30</option>
            <option value="c90">Somente Inadimplentes FPD 90</option>
            <option value="adimp">Somente Adimplentes 1ª Fatura</option>
          </select>"""
template = re.sub(r'<select id="dotShow">.*?</select>', dot_show_html, template, count=1, flags=re.DOTALL)

map_rank_dim_html = """      <select id="mapRankDim" style="width:100%;border:1px solid var(--line);padding:4px;font:11.5px 'Segoe UI',Arial;margin-bottom:8px">
        <option value="auto">Geografia (segue o zoom do mapa)</option>
        <option value="cidade">Cidade</option>
        <option value="bairro">Bairro</option>
        <option value="node">Node</option>
        <option value="canal_grupo">Canal de Venda (Grupo)</option>
        <option value="canal">Canal Detalhado</option>
        <option value="parceiro">Parceiro / Credenciado</option>
        <option value="vendedor">Vendedor (Matrícula/Nome)</option>
        <option value="produto">Produto (Bundle)</option>
        <option value="produto_dados">Velocidade Banda Larga</option>
        <option value="portfolio_tv">Portfólio TV</option>
        <option value="risco_nv">Faixa de Risco (FX_RISCO_NV)</option>
        <option value="score">Faixa de Score (FXULTSCORE)</option>
      </select>"""
template = re.sub(r'<select id="mapRankDim".*?</select>', map_rank_dim_html, template, count=1, flags=re.DOTALL)

# 4. Cidades Panel
p_cid = template.find('<div class="panel">\n  <h2>Cidades')
if p_cid == -1: p_cid = template.find('<div class="panel">\r\n  <h2>Cidades')

p_np = template.find('<div class="panel">\n  <h2>Nunca pagou')
if p_np == -1: p_np = template.find('<div class="panel">\r\n  <h2>Nunca pagou')

cidades_panel_html = """<div class="panel">
  <h2>Cidades — Visão Geográfica IBGE <span class="note">desempenho FPD nas 13 praças da Regional Norte</span>
    <span class="tabs" id="tabsCid">
      <button class="on" data-d="cidade">Cidades (13 Praças)</button>
      <button data-d="porte">Segmento de Mercado</button>
      <button data-d="uf">UF</button>
      <button data-d="tipo_cidade">Tipo de Rede</button>
    </span>
    <button class="hlp" data-h="cidades">?</button>
  </h2>
  <div class="pbody">
    <div id="chCid" style="margin-bottom:12px"></div>
    <div class="tbl-wrap">
      <table id="tblCid"></table>
    </div>
  </div>
</div>\n\n"""

template = template[:p_cid] + cidades_panel_html + template[p_np:]

# 5. Replace 'Nunca pagou' and 'Motivo da desconexão' with 'QUALIDADE DE VENDA & PERFIL DE CRÉDITO'
p_np2 = template.find('<div class="panel">\n  <h2>Nunca pagou')
if p_np2 == -1: p_np2 = template.find('<div class="panel">\r\n  <h2>Nunca pagou')

p_mtx = template.find('<div class="panel">\n  <h2>Matriz de safra')
if p_mtx == -1: p_mtx = template.find('<div class="panel">\r\n  <h2>Matriz de safra')

risco_panel_html = """<div class="panel">
  <h2>QUALIDADE DE VENDA & PERFIL DE CRÉDITO <span class="note">visão oficial de FX_RISCO_NV e faixas de score FXULTSCORE</span>
    <span class="tabs" id="tabsRiscoMode">
      <button class="on" data-m="risco_nv">Faixa de Risco (FX_RISCO_NV)</button>
      <button data-m="score">Faixa de Score (FXULTSCORE)</button>
    </span>
    <button class="hlp" data-h="risco">?</button>
  </h2>
  <div class="pbody">
    <div id="chRisco" style="margin-bottom:14px"></div>
    <div class="tbl-wrap">
      <table id="tblRisco"></table>
    </div>
  </div>
</div>\n\n"""

template = template[:p_np2] + risco_panel_html + template[p_mtx:]

# 6. Matriz de Safra FPD & Remove Esteira
p_mtx2 = template.find('<div class="panel">\n  <h2>Matriz de safra')
if p_mtx2 == -1: p_mtx2 = template.find('<div class="panel">\r\n  <h2>Matriz de safra')

p_rank = template.find('<div class="panel">\n  <h2>Ranking por dimensão')
if p_rank == -1: p_rank = template.find('<div class="panel">\r\n  <h2>Ranking por dimensão')

matriz_panel_html = """<div class="panel">
  <h2>MATRIZ DE SAFRA FPD <span class="note">evolução da maturação da primeira fatura (marcação antes e após ★ FPD 60 oficial)</span>
    <span class="tabs" id="tabsMtx">
      <button class="on" data-m="pctac">% Acumulada</button>
      <button data-m="pct">% Incremental</button>
      <button data-m="abs">Absoluto</button>
    </span>
    <label style="margin-left:14px;font-size:11.5px;color:var(--ink2)">
      Abertura por:
      <select id="mtxDim" style="font-size:11px;padding:2px 6px">
        <option value="">Safra de Instalação (Padrão)</option>
        <option value="canal_grupo">Canal de Venda</option>
        <option value="cidade">Cidade (IBGE)</option>
        <option value="portfolio_tv">Portfólio TV</option>
        <option value="risco_nv">Faixa de Risco (FX_RISCO_NV)</option>
      </select>
    </label>
    <label style="margin-left:10px;font-size:11.5px;color:var(--ink2)">
      <input type="checkbox" id="mtxMature"> Apenas safras com FPD 60 completo
    </label>
    <button class="hlp" data-h="matriz">?</button>
  </h2>
  <div class="pbody">
    <div class="tbl-wrap">
      <table id="tblMtx" class="tbl-mtx"></table>
    </div>
  </div>
</div>\n\n"""

# This cut from p_mtx2 to p_rank completely wipes both the old Matriz and the old Esteira!
template = template[:p_mtx2] + matriz_panel_html + template[p_rank:]

# 7. Notas metodológicas
p_met = template.find('<div class="panel">\n  <h2>Notas metodológicas')
if p_met == -1: p_met = template.find('<div class="panel">\r\n  <h2>Notas metodológicas')

p_met_end = template.find('</div>\n</div>\n\n<div class="revpanel"')
if p_met_end == -1: p_met_end = template.find('</div>\r\n</div>\r\n\r\n<div class="revpanel"')

metodologia_html = """<div class="panel">
  <h2>NOTAS METODOLÓGICAS FPD <span class="note">conceitos, regras e critérios oficiais Claro</span><button class="hlp" data-h="metodo">?</button></h2>
  <div class="pbody" style="font-size:12.5px;line-height:1.6;color:var(--ink2)">
    <b>Conceito de First Payment Default (FPD)</b> — O FPD avalia a inadimplência na primeira fatura de novos clientes instalados nos serviços residenciais da Claro na Regional Norte ao longo das 13 safras observadas (mai/25 a mai/26). Diferente da desconexão de churn, o FPD é o indicador primário de qualidade de venda, onboarding e risco de crédito de entrada.<br>
    <b>★ Marco Oficial FPD 60 (Claro)</b> — É o indicador oficial corporativo para metas executivas e remuneração de canais. Mede o percentual de contratos sem pagamento da 1ª fatura de ciclo cheio no marco de 60 dias após a instalação.<br>
    <b>Taxa FPD 30 (Onboarding / Pró-rata)</b> — Mede a inadimplência na fatura proporcional emitida no primeiro mês. Picos de FPD 30 sinalizam problemas cadastrais, não entrega de fatura ou vícios de venda.<br>
    <b>FPD 90 a 150 (Escalada de Cobrança)</b> — Indica o agravamento da inadimplência para contratos que permanecem sem quitar a fatura inicial, transitando para suspensão, negativação e posterior cancelamento.<br>
    <b>Perfil de Risco & Score</b> — Baseado nas réguas oficiais de concessão de crédito Claro (<code>FX_RISCO_NV</code> e <code>FXULTSCORE</code>), correlacionando o risco de crédito na adesão com a inadimplência precoce real.<br>
    <b>Geografia e Micro-Dispersão</b> — Cobertura integral das 13 praças IBGE da Regional Norte (AM, PA, MA, AP). Aplica micro-dispersão residencial determinística para preservar a densidade urbana e evitar sobreposição artificial de contratos no mesmo centróide de CEP.
  </div>
</div>\n\n"""

template = template[:p_met] + metodologia_html + template[p_met_end:]

# Test remaining churn terms in body
s_script = template.find('<script>')
body = template[:s_script]
terms = ['desconex', 'desconect', 'nunca pagou', 'esteira', 'motivo da desc', 'curva de matur', 'sk_fc_gerou']

found = []
for t in terms:
    pos = body.lower().find(t)
    if pos != -1:
        found.append((t, pos, body[max(0, pos-20):min(len(body), pos+50)].replace('\n', ' ')))

print("Churn terms check in transformed body:")
if not found:
    print("SUCCESS: ZERO CHURN TERMS FOUND IN HTML BODY!")
else:
    for item in found:
        print("STILL FOUND:", item)
