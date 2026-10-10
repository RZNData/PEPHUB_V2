with open('Painel_Churn_Safra 28.html', 'r', encoding='utf-8', errors='ignore') as f:
    t = f.read()

anchors = [
    '<div class="grid2">',
    '<div class="panel">\n  <h2>Mapa de concentração',
    '<select id="mapMetric">',
    '</select>',
    '<select id="dotShow">',
    '</select>',
    '<select id="mapRankDim"',
    '<!-- Painel Cidades -->',
    '<div class="panel">\n  <h2>Nunca pagou',
    '<div class="panel">\n  <h2>Motivo da desconexão',
    '<div class="panel">\n  <h2>Matriz de safra',
    '<div class="panel">\n  <h2>Esteira de instalações',
    '<div class="panel">\n  <h2>Ranking por dimensão',
    '<table id="tblContratos"',
    '<div class="panel">\n  <h2>Notas metodológicas',
    'const DIMDEF=',
    'const RANKDIMS=',
    'function drawSafra()',
    '/* ============ MAPA ============ */',
    'function newCell(x,y){',
    'function metricVal(o,m){',
    'function tipCell(o){',
    'function drawGeoFoot(){',
    'const RATE=new Set(',
    'function dotColor(',
    'function dotIsHot(',
    'function drawMapRank(){',
    'function openContratos(rows,titulo){',
    'cv.addEventListener(\'mousemove\',e=>{ if(drag)return;',
    'const TAGLAB={',
    'function defaultAnchor(){',
    'function applySafra(){',
    'function render_(){',
    '/* ============ init ============ */',
    'const sv=fEl.querySelector(\'select[data-dim="visao"]\')',
    'const HELP={'
]

for a in anchors:
    pos = t.find(a)
    print(f"Anchor '{a[:30]}': {'FOUND at ' + str(pos) if pos != -1 else 'NOT FOUND'}")
