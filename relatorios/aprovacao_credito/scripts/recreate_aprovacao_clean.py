import re
import sys

# Read from pristine original source file
with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8') as f:
    orig_content = f.read()

# Extract script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', orig_content, re.DOTALL)
if len(scripts) < 3:
    raise ValueError(f"Expected 3 script blocks in Painel Aprovacao Credito RNO 2.4.html, found {len(scripts)}")

data_script = scripts[1]
engine_script = scripts[2]

# 1. Clean emojis and informal icons from engine_script
emoji_replacements = [
    ("\U0001f50e Buscar por Nome Fantasia, DV_", "Buscar por Nome Fantasia, DV_"),
    ("\U0001f50e Buscar canal ou parceiro", "Buscar canal ou parceiro"),
    ("\U0001f50e Buscar equipe de venda", "Buscar equipe de venda"),
    ("\U0001f50e", ""),
    ("\U0001f4c1 Escolher arquivo (.csv recomendado)", "Escolher arquivo (.csv recomendado)"),
    ("\U0001f4c1 Escolher arquivo (.xlsx)", "Escolher arquivo (.xlsx)"),
    ("\U0001f4c1 Escolher arquivo", "Escolher arquivo"),
    ("\U0001f4c1", ""),
    ("\U0001f5a8\ufe0f Imprimir / PDF", "Imprimir / PDF"),
    ("\U0001f5a8", ""),
    ("\U0001f3f7\ufe0f Top 5", "Top 5"),
    ("\U0001f3f7", ""),
    ("\U0001f4c8 Linhas", "Linhas"),
    ("\U0001f4c8", ""),
    ("\U0001f50d Ampliar", "Ampliar"),
    ("\U0001f50d", ""),
    ("\U0001f4a1 PDVs acima da linha", "PDVs acima da linha"),
    ("\U0001f4a1", ""),
    ("\U0001f4cc <b>Síntese:</b>", "<b>Síntese:</b>"),
    ("\U0001f4cc <b>Base grande", "<b>Base grande"),
    ("\U0001f4cc", ""),
    ("\U0001f511 <b>Cascata de carteirização:", "<b>Cascata de carteirização:"),
    ("\U0001f511", ""),
    ("⚠️ Ferramenta em testes", "[Piloto] Ferramenta em testes"),
    ("⚠️ A biblioteca de leitura de Excel", "A biblioteca de leitura de Excel"),
    ("⚠️", ""),
    ("➕", "+"),
    ("⬇️ Exportar PNG", "Exportar PNG"),
    ("⬇️", ""),
    ("⤓", ""),
    ("★", ""),
    ("§", ""),
    ("▦ Tabela", "Tabela"),
    ("📈 Linhas", "Linhas"),
    ("✓ Sem filtros ativos", "Sem filtros ativos"),
    ("● Filtros ativos", "Filtros ativos"),
    ("①", "[1]"),
    ("②", "[2]"),
    ("③", "[3]"),
    ("④", "[4]"),
]
for old_s, new_s in emoji_replacements:
    engine_script = engine_script.replace(old_s, new_s)

# 2. Set default view to 'v1' (eliminating 'capa')
engine_script = engine_script.replace("view:'capa'", "view:'v1'")

# 3. Completely eliminate onboarding disclaimer block
ob_start = engine_script.find("/* ================= ONBOARDING / DISCLAIMER (1x por sessão) ================= */")
ob_end = engine_script.find("/* ================= ACESSO RESTRITO — ABA IMPORTAR ================= */")
if ob_start != -1 and ob_end != -1:
    engine_script = engine_script[:ob_start] + """/* ================= ONBOARDING / DISCLAIMER (ELIMINATED) ================= */
function showOnboarding(){ /* eliminated */ }
function maybeOnboard(view){ /* eliminated */ }
""" + engine_script[ob_end:]

# 4. Remove capa from TITLES and from view routing in render()
engine_script = engine_script.replace(
    "const TITLES={capa:['Capa & Direcionamento','Principais achados e navegação'],\n v1:",
    "const TITLES={v1:"
)
engine_script = engine_script.replace(
    "c.innerHTML=({capa:vCapa,v1:v1View,v2:v2View,v3:v3View,v4:v4View,v5:v5View,cart:vCarteira,sum:vResumo,imp:vImport})[S.view]();",
    "c.innerHTML=({v1:v1View,v2:v2View,v3:v3View,v4:v4View,v5:v5View,cart:vCarteira,sum:vResumo,imp:vImport})[S.view]();"
)

# 5. Add standard trunc30 helper function to engine_script (30 chars max with ...)
engine_script = """function trunc30(s){
  if(!s) return '';
  const str = String(s).trim();
  return str.length > 30 ? str.slice(0, 27) + '...' : str;
}
""" + engine_script

# 6. Update render() to update #ttl, #tsub, #viewNote, #modeToggle, and filter drawer state
old_render_start = "function render(){\n  document.getElementById('ttl').childNodes[0].nodeValue=TITLES[S.view][0];\n  document.getElementById('tsub').textContent=TITLES[S.view][1];\n  document.getElementById('modeToggle').style.display=(S.view==='capa'||S.view==='imp')?'none':'inline-flex';"
new_render_start = """function render(){
  const ttlEl = document.getElementById('ttl');
  if (ttlEl && ttlEl.childNodes.length > 0 && TITLES[S.view]) ttlEl.childNodes[0].nodeValue = TITLES[S.view][0];
  const tsubEl = document.getElementById('tsub');
  if (tsubEl && TITLES[S.view]) tsubEl.textContent = TITLES[S.view][1];
  const vNote = document.getElementById('viewNote');
  if (vNote && TITLES[S.view]) vNote.textContent = TITLES[S.view][1] || '';
  const mt = document.getElementById('modeToggle');
  if (mt) mt.style.display = S.view === 'imp' ? 'none' : 'inline-flex';"""
engine_script = engine_script.replace(old_render_start, new_render_start)

# 7. Ensure filter drawer collapse state is respected in render()
engine_script = re.sub(
    r'(if\(S\.view===\'sum\'\)\{bindSumTools\(\);\}\s*)',
    r"""\1
  // Drawer filter visibility sync
  const fEl = document.querySelector('.filters');
  if (fEl && S.filtersHidden) fEl.style.display = 'none';
  const btnD = document.getElementById('btnDrawer');
  if (btnD) btnD.classList.toggle('open', !S.filtersHidden);
  const icoD = document.getElementById('drawerIco');
  if (icoD) icoD.textContent = S.filtersHidden ? '▸' : '▾';
""",
    engine_script
)

# 8. Update go(v) to toggle both .active and .on classes on .tabs a, without side-collapse logic
engine_script = re.sub(
    r'function go\(v\)\{[^}]*render\(\);window\.scrollTo\(0,0\);\}',
    """function go(v){
  S.view = v;
  document.querySelectorAll('#nav a').forEach(a => {
    a.classList.toggle('active', a.dataset.v === v);
    a.classList.toggle('on', a.dataset.v === v);
  });
  render();
  window.scrollTo(0,0);
}""",
    engine_script
)

# 9. Clean up openZoom to remove informal text/icons
engine_script = engine_script.replace("⬇️ Exportar PNG", "Exportar PNG")

# 10. REMOVE Executiva column in v4View and truncate PDV name to 30 chars
old_v4_cols = """  const cols=[{key:'rk',label:'#',type:'text',cls:'c-rk',text:r=>`<span class="rankn ${r._rk===1?'':(r._rk===2?'g2':'g3')}" style="${r._rk>3?'background:#C7CFDC':''}">${r._rk}</span>`},
    {key:'pdv',label:'PDV (Fantasia / DV)',type:'text',cls:'c-pdv',text:r=>cartBadge(r)+(r.fant?`${r.fant} <span class="mut cdim">· ${r.PDV}</span>`:`<span class="cdim2">${r.PDV}</span>`)},
    {key:'exec',label:'Executivo',type:'text',cls:'c-exec',text:r=>r.exec&&r.exec!==NC?r.exec:'<span class="mut">—</span>'},
    {key:'city',label:'Cidade',type:'text',cls:'c-city',text:r=>r.city},
    {key:'cn',label:'Canal',type:'text',cls:'c-cn',text:r=>r.cn},
    ...metricCols({key:'seg',label:'Segmento',type:'text',text:r=>r.seg}).slice(1)];"""

new_v4_cols = """  const cols=[{key:'rk',label:'#',type:'text',cls:'c-rk',text:r=>`<span class="rankn ${r._rk===1?'':(r._rk===2?'g2':'g3')}" style="${r._rk>3?'background:#C7CFDC':''}">${r._rk}</span>`},
    {key:'pdv',label:'PDV (Fantasia / DV)',type:'text',cls:'c-pdv pdv-col',text:r=>{
      const full = r.fant ? `${r.fant} · ${r.PDV}` : r.PDV;
      const shortFant = r.fant ? trunc30(r.fant) : '';
      const shortTxt = r.fant ? `${shortFant} <span class="mut cdim">· ${r.PDV}</span>` : `<span class="cdim2">${trunc30(r.PDV)}</span>`;
      return `<span class="pdv-name-cell" title="${full.replace(/"/g,'&quot;')}">${cartBadge(r)}${shortTxt}</span>`;
    }},
    {key:'city',label:'Cidade',type:'text',cls:'c-city',text:r=>r.city},
    {key:'cn',label:'Canal',type:'text',cls:'c-cn',text:r=>r.cn},
    ...metricCols({key:'seg',label:'Segmento',type:'text',text:r=>r.seg}).slice(1)];"""

engine_script = engine_script.replace(old_v4_cols, new_v4_cols)

# In v4View: Ensure default sort starts with highest volume descending
old_v4_sort = "list.sort((a,b)=>critScore(b)-critScore(a)||b.rec.ttd-a.rec.ttd);"
new_v4_sort = """list.sort((a,b)=>{
    const sc = critScore(b) - critScore(a);
    if (sc !== 0 && S.v4crit !== 'vol') return sc;
    return (b.rec?.ttd || 0) - (a.rec?.ttd || 0);
  });"""
engine_script = engine_script.replace(old_v4_sort, new_v4_sort)

# 11. In v2View: Fix column sorting (both channels and PDVs) and default to highest volume descending
old_v2_sortrows = "function sortRows(rows){if(st.sortCol){const c=cols.find(x=>x.key===st.sortCol);if(c)rows.sort((a,b)=>{if(c.type==='text')return st.sortDir*((a.lab||'')<(b.lab||'')?-1:(a.lab||'')>(b.lab||'')?1:0);return st.sortDir*((cellFor(c,a).sv||0)-(cellFor(c,b).sv||0));});}else rows.sort((a,b)=>b.rec.ttd-a.rec.ttd);return rows;}"
new_v2_sortrows = """function sortRows(rows){
    if(st.sortCol){
      const c = cols.find(x => x.key === st.sortCol);
      if(c) rows.sort((a,b)=>{
        if(c.type === 'text') return st.sortDir * ((a.lab||'').localeCompare(b.lab||''));
        const va = (cellFor(c,a).sv != null) ? cellFor(c,a).sv : 0;
        const vb = (cellFor(c,b).sv != null) ? cellFor(c,b).sv : 0;
        return st.sortDir * (va - vb);
      });
    } else {
      // Padronizado: Iniciar com maior volume de forma decrescente
      rows.sort((a,b) => (b.rec?.ttd || 0) - (a.rec?.ttd || 0));
    }
    return rows;
  }"""
engine_script = engine_script.replace(old_v2_sortrows, new_v2_sortrows)

# Update v2View table headers to show clear sort arrows (▲/▼/⇅)
old_v2_th = "cols.forEach(c=>{const active=st.sortCol===c.key;const ar=active?(st.sortDir>0?'▲':'▼'):'';h2+=`<th class=\"sortable ${active?'sorton':''}\" data-tid=\"t_v2\" data-col=\"${c.key}\">${c.label} <span class=\"sar\">${ar}</span></th>`;});"
new_v2_th = """cols.forEach(c=>{
    const active = st.sortCol === c.key;
    const ar = active ? (st.sortDir < 0 ? ' ▼' : ' ▲') : ' ⇅';
    h2 += `<th class="sortable ${active?'sorton':''}" data-tid="t_v2" data-col="${c.key}" style="cursor:pointer;" title="Clique para ordenar ${active?(st.sortDir<0?'do menor para o maior':'do maior para o menor'):'do maior para o menor'}">${c.label} <span class="sar">${ar}</span></th>`;
  });"""
engine_script = engine_script.replace(old_v2_th, new_v2_th)

# Replace the entire v2View 3-level hierarchy block so groups, channels, and PDVs all sort, truncate, and display properly
v2_idx_start = engine_script.find('// 3-level hierarchy: Group -> Channel -> PDV')
v2_idx_end = engine_script.find('return h+h2;', v2_idx_start)
if v2_idx_start != -1 and v2_idx_end != -1:
    new_v2_hierarchy = """// 3-level hierarchy: Group -> Channel -> PDV
  const rawGroups = [['Canais Presenciais', PRES], ['Canais Remotos', REM], ['Outros Canais', outros()]];
  let groupItems = rawGroups.map(([gname, arr]) => {
    const gt = rnoTriple(x => x.CG === gname);
    return { gname, arr, lab: gname, rec: gt.rec, ant: gt.ant, ano: gt.ano };
  }).filter(g => (g.rec?.ttd || 0) > 0);

  // Ordena grupos pela mesma métrica quando houver ordenação de coluna ativa
  groupItems = sortRows(groupItems);

  let anyRows = false;
  let gi = 0;
  const isSorted = !!st.sortCol;

  groupItems.forEach(grow => {
    const gname = grow.gname;
    const arr = grow.arr;
    // build channel rows for this group
    let chans = arr.filter(cn => S.canais.has(cn)).map(cn => {
      const t = rnoTriple(x => x.CN === cn);
      return { cn, cg: gname, rec: t.rec, ant: t.ant, ano: t.ano, lab: cn };
    }).filter(x => (x.rec?.ttd || 0) > 0);

    const gid = 'g' + gi;
    let chHtml = '';
    let groupHasMatch = false;
    let groupOpenByQ = false;

    chans = sortRows(chans);

    chans.forEach(ch => {
      let pdvs = pdvAgg(x => x.CN === ch.cn);
      pdvs.forEach(p => p.lab = (p.fant || p.PDV) + ' ' + p.city);
      pdvs = sortRows(pdvs);

      // search (matches fantasia, DV code, exec or city)
      let matchPdvs = pdvs;
      let chMatch = true;
      if (q) {
        chMatch = ch.cn.toLowerCase().includes(q);
        matchPdvs = pdvs.filter(p => ((p.fant || '') + ' ' + p.PDV + ' ' + p.city + ' ' + (p.exec || '')).toLowerCase().includes(q));
        if (!chMatch && matchPdvs.length === 0) return;
        if (!chMatch) pdvs = matchPdvs;
      }

      // column filters
      if (colFilterActive) {
        const chPass = passColFilters(ch);
        const keptPdvs = pdvs.filter(passColFilters);
        if (!chPass && keptPdvs.length === 0) return;
        if (!chPass) pdvs = keptPdvs;
      }

      groupHasMatch = true;
      const cnid = ch.cn.replace(/[^a-zA-Z]/g, '');
      const openByQ = (q && matchPdvs.length > 0) || colFilterActive;
      if (openByQ) groupOpenByQ = true;

      // Canal row
      const chOpen = openByQ || isSorted;
      chHtml += `<tr class="rowchild rowgrp rowsub ${chOpen ? 'show' : ''}" data-lvl="c" data-p="${gid}" data-cn="${cnid}" style="background:#F7FAFF!important"${chOpen ? ' data-open="1"' : ''}><td class="pdv-col" style="padding-left:26px"><b>${ch.cn}</b></td>`;
      cols.slice(1).forEach(c => { chHtml += `<td>${cellHTML(c, cellFor(c, ch))}</td>`; });
      chHtml += '</tr>';

      // PDVs rows
      pdvs.forEach(p => {
        const key = p.PDV + '|' + p.city;
        const on = S.v2sel.has(key);
        const full = p.fant ? `${p.fant} · ${p.PDV}` : p.PDV;
        const shortFant = p.fant ? trunc30(p.fant) : '';
        const dispText = p.fant ? `${shortFant} <span class="mut" style="font-size:10px">· ${p.PDV}</span>` : trunc30(p.PDV);
        const disp = cartBadge(p) + `<span class="pdv-name-cell" title="${full.replace(/"/g,'&quot;')}">${dispText}</span>`;
        chHtml += `<tr class="rowchild rowpdv pdvrow-${cnid}" data-p="${gid}" style="display:${openByQ ? 'table-row' : 'none'}"><td class="pdv-col"><button class="pdvadd${on ? ' on' : ''}" data-selpdv="${key.replace(/"/g,'&quot;')}" title="${on ? 'Remover da seleção' : 'Adicionar à seleção'}">${on ? '✓' : '+'}</button> ${disp} <span class="mut">· ${p.city}</span></td>`;
        cols.slice(1).forEach(c => { chHtml += `<td>${cellHTML(c, cellFor(c, p))}</td>`; });
        chHtml += '</tr>';
      });
    });

    if (q || colFilterActive) {
      if (!groupHasMatch) { gi++; return; }
    }
    anyRows = true;
    const gOpen = ((q || colFilterActive) && groupOpenByQ) || isSorted;
    h2 += `<tr class="rowgrp ${gOpen ? 'open' : ''}" data-lvl="g" data-g="${gid}"${gOpen ? ' data-open="1"' : ''}><td class="pdv-col"><b>${gname}</b></td>`;
    cols.slice(1).forEach(c => { h2 += `<td>${cellHTML(c, cellFor(c, grow))}</td>`; });
    h2 += '</tr>';
    h2 += chHtml;
    gi++;
  });
  if (!anyRows) h2 += `<tr><td colspan="${cols.length}" style="text-align:center;color:#9AA6C2;padding:18px">Nenhum resultado com os filtros atuais.</td></tr>`;
  h2 += '</tbody></table></div><div class=\"csub\" style=\"margin-top:8px\">Hierarquia: <b>Grupo</b> (Presenciais / Remotos / Outros) → <b>Canal</b> → <b>PDV</b>. Clique para expandir ou ordenar.</div></div>';\n  """
    engine_script = engine_script[:v2_idx_start] + new_v2_hierarchy + engine_script[v2_idx_end:]

# Click delegation on th.sortable: flip sortDir and call render()
old_th_sort = """  const th=e.target.closest('th.sortable');
  if(th){const tid=th.dataset.tid,col=th.dataset.col;const st=tget(tid);
    const isText=['lab','pdv','city','cn','seg'].includes(col);
    if(st.sortCol===col)st.sortDir*=-1;else{st.sortCol=col;st.sortDir=isText?1:-1;} // text→A-Z, número→maior-menor
    render();return;}"""

new_th_sort = """  const th = e.target.closest('th.sortable');
  if(th){
    const tid = th.dataset.tid, col = th.dataset.col;
    const st = tget(tid);
    const isText = ['lab','pdv','city','cn','seg'].includes(col);
    if(st.sortCol === col) st.sortDir *= -1;
    else { st.sortCol = col; st.sortDir = isText ? 1 : -1; }
    render();
    return;
  }"""
engine_script = engine_script.replace(old_th_sort, new_th_sort)

# 12. In vCarteira: Fix missing space between tag and name (Screenshot 4) and truncate PDV name to 30 chars
old_cart_grp = """h2+=`<tr class="cart-row cart-grp${ncCls}" data-node="${r.id}" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td style="padding-left:${pad}px">${car} ${tag}${lbl}</td>`;"""
new_cart_grp = """h2+=`<tr class="cart-row cart-grp${ncCls}" data-node="${r.id}" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td style="padding-left:${pad}px">${car} ${tag} ${lbl}</td>`;"""
engine_script = engine_script.replace(old_cart_grp, new_cart_grp)

old_cart_leaf = """      const p=r.p;
      const disp=p.fant?`<b>${p.fant}</b> <span class="mut" style="font-size:10px">· ${p.PDV}</span>`:p.PDV;
      h2+=`<tr class="cart-row cart-pdv" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td style="padding-left:${pad+16}px"><span class="mut" style="margin-right:6px">•</span>${cartBadge(p)}${disp} <span class="mut">· ${p.city}</span></td>`;"""

new_cart_leaf = """      const p=r.p;
      const full=p.fant?`${p.fant} · ${p.PDV}`:p.PDV;
      const shortFant=p.fant?trunc30(p.fant):'';
      const disp=p.fant?`<b>${shortFant}</b> <span class="mut" style="font-size:10px">· ${p.PDV}</span>`:trunc30(p.PDV);
      h2+=`<tr class="cart-row cart-pdv" data-anc="${r.anc.join(',')}" data-depth="${r.depth}"><td class="pdv-col" style="padding-left:${pad+16}px"><span class="mut" style="margin-right:6px">•</span>${cartBadge(p)}<span class="pdv-name-cell" title="${full.replace(/"/g,'&quot;')}">${disp}</span> <span class="mut">· ${p.city}</span></td>`;"""
engine_script = engine_script.replace(old_cart_leaf, new_cart_leaf)

# 13. In lineChart: Fix width and legend overflow (Screenshot 5)
old_linechart = """function lineChart(el,labels,series,opt){
  opt=opt||{};const W=680,H=300,pl=44,pr=16,pt=18,pb=40;const iw=W-pl-pr,ih=H-pt-pb;"""

new_linechart = """function lineChart(el,labels,series,opt){
  opt=opt||{};
  const isWide = (el==='c1a'||el==='rh4');
  const W=isWide?1200:680, H=isWide?260:300, pl=48, pr=24, pt=18, pb=42;
  const iw=W-pl-pr, ih=H-pt-pb;"""
engine_script = engine_script.replace(old_linechart, new_linechart)

old_linechart_end = """  s+='</svg>';
  let lg='<div class="legend-mini" style="text-align:center">'+series.map(se=>`<span style="display:inline-block;margin:0 8px"><span style="display:inline-block;width:14px;height:3px;border-radius:2px;background:${se.color};vertical-align:middle"></span> ${se.name}</span>`).join('')+'</div>';
  document.getElementById(el).innerHTML=s+lg;
}"""

new_linechart_end = """  s+='</svg>';
  let lg='<div class="legend-mini" style="display:flex;justify-content:center;align-items:center;gap:24px;padding:12px 0 4px;margin-top:8px;border-top:1px solid var(--line2);background:#FAFBFD;border-radius:0 0 4px 4px;">'+series.map(se=>`<span style="display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:600;color:var(--ink2)"><span style="display:inline-block;width:16px;height:3.5px;border-radius:2px;background:${se.color}"></span>${se.name}</span>`).join('')+'</div>';
  const targetEl = document.getElementById(el);
  if(targetEl){ targetEl.innerHTML=s+lg; }
}"""
engine_script = engine_script.replace(old_linechart_end, new_linechart_end)

# In v1View: update c1a chartbox container to not overflow
old_c1a_box = """  h+='<div class="card"><h3>Taxa de aprovação — '+per+' (RNO × Brasil)'+scopeBadge(['prod','canal','cid'])+'</h3><div class="csub">Série mensal (%). '+perNote+'</div><div class="chartbox" style="height:300px"><div id="c1a" style="width:100%;height:100%"></div></div></div>';"""
new_c1a_box = """  h+='<div class="card" style="overflow:visible"><h3>Taxa de aprovação — '+per+' (RNO × Brasil)'+scopeBadge(['prod','canal','cid'])+'</h3><div class="csub">Série mensal (%). '+perNote+'</div><div id="c1a" style="width:100%;min-height:280px;padding:6px 0"></div></div>';"""
engine_script = engine_script.replace(old_c1a_box, new_c1a_box)

# 14. In scatterSVG: Fix number badges in Top 5 (Screenshot 1)
old_scatter_tops = """      tops.forEach(p=>{const n=topIdx.get(p);const nm=p.label.length>22?p.label.slice(0,22)+'…':p.label;
        s+=`<line x1="${X(p.x)+9}" y1="${Y(p.y)}" x2="${lx-3}" y2="${ly-3}" stroke="#C0C6D4" stroke-width="0.8"/>`;
        s+=`<circle cx="${lx+3}" cy="${ly-4}" r="7" fill="${p.color}"/><text x="${lx+3}" y="${ly-1}" font-size="8" font-weight="800" fill="#fff" text-anchor="middle">${n}</text>`;
        s+=`<text x="${lx+14}" y="${ly-1}" font-size="9" fill="#333">${nm}</text>`;ly+=16;});"""

new_scatter_tops = """      tops.forEach(p=>{const n=topIdx.get(p);const nm=p.label.length>24?p.label.slice(0,24)+'…':p.label;
        s+=`<line x1="${X(p.x)+9}" y1="${Y(p.y)}" x2="${lx-4}" y2="${ly-4}" stroke="#C0C6D4" stroke-width="0.8"/>`;
        s+=`<circle cx="${lx+4}" cy="${ly-4}" r="7" fill="${p.color}"/><text x="${lx+4}" y="${ly-1.5}" font-size="8.5" font-weight="700" fill="#fff" text-anchor="middle" style="paint-order:normal;stroke:none">${n}</text>`;
        s+=`<text x="${lx+16}" y="${ly-1}" font-size="9" fill="#333">${nm}</text>`;ly+=16;});"""
engine_script = engine_script.replace(old_scatter_tops, new_scatter_tops)

# Clean stylesheet adhering 100% to PADRAO_DESIGN_PAINEIS.md & Churn Safra Gold Standard
official_css = """
:root {
  --bg: #f4f5f7;
  --panel: #ffffff;
  --card: #ffffff;
  --ink: #1c2430;
  --ink2: #5b6675;
  --ink3: #8b95a3;
  --line: #dfe3e8;
  --line2: #eceef1;
  --nav: #1b2430;
  --nav2: #27323f;
  --red: #c0392b;
  --amber: #c98a15;
  --green: #2f7d5d;
  --blue: #2a5d8f;
  --purple: #6b4b8a;
  --claro: #c0392b;
  --claro-d: #8a0f18;
  --navy: #1b2430;
  --navy2: #27323f;
  --muted: #5b6675;
  --good: #eaf2ec;
  --warn: #fdf3e2;
  --bad: #fdece9;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Staging Banner */
.staging-banner {
  background: linear-gradient(90deg, #1b2430 0%, #2a3b50 100%);
  color: #f9b233;
  padding: 6px 26px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 2px;
  font-size: 10px;
  text-transform: uppercase;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
}

/* Header Corporativo Oficial Claro PEP HUB */
header { background: #fff; }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex; align-items: center; gap: 16px; padding: 14px 26px; flex-wrap: wrap;
}
.hd-ico {
  width: 44px; height: 44px; min-width: 44px; border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,.95); display: flex; align-items: center; justify-content: center;
}
.hd-bar h1 {
  margin: 0; color: #fff; font-size: 26px; font-weight: 400; letter-spacing: -.4px; line-height: 1.1;
  display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
}
.hd-bar h1 b { font-weight: 800; letter-spacing: -0.5px; }
.hd-bar h1 span { font-weight: 300; font-size: 20px; color: rgba(255,255,255,.92); }

/* Botoes de Acao Superior Direito */
.hd-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hd-btn {
  background: rgba(255,255,255,.22) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,.55) !important;
  padding: 5px 12px !important; border-radius: 3px !important; font-size: 11.5px !important; font-weight: 700 !important;
  text-decoration: none !important; transition: all .15s ease !important; cursor: pointer !important;
  display: inline-flex !important; align-items: center !important; gap: 6px !important; white-space: nowrap !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.18) !important;
}
.hd-btn:hover { background: rgba(255,255,255,.38) !important; color: #ffffff !important; border-color: #ffffff !important; }

/* Subheader com Breadcrumb e Contexto */
.hd-sub {
  background: var(--nav); color: #aab4c0; font-size: 11.5px; padding: 7px 26px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.hd-sub b { color: #e8edf3; font-weight: 600; }
.hd-sub .dot { width: 3px; height: 3px; border-radius: 50%; background: #5b6675; display: inline-block; }
.hd-sub .hd-right { margin-left: auto; display: flex; align-items: center; gap: 8px; color: #8b95a3; font-weight: 600; }
.hd-sub a, .hd-sub .back-hub { color: #f9b233 !important; text-decoration: none !important; font-weight: 700 !important; display: inline-flex; align-items: center; gap: 4px; }
.hd-sub a:hover, .hd-sub .back-hub:hover { color: #ffffff !important; text-decoration: underline !important; }

/* Conteiner Geral */
.wrap { padding: 16px 26px 40px; max-width: 2400px; margin: 0 auto; }

/* Paineis Analiticos (Churn Safra Standard) */
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }
.panel > h2 {
  margin: 0; padding: 10px 14px; font-size: 12px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .6px; color: var(--ink2); border-bottom: 1px solid var(--line2);
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.panel > h2 .panel-note {
  text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--ink3); font-size: 11px;
  border: none !important; background: none !important; padding: 0 !important; margin: 0 !important;
}
.pbody { padding: 14px; }

/* Gaveta de Filtros Retratil (.drawer-btn) */
.drawer-btn {
  display: inline-flex; align-items: center; gap: 6px; background: var(--nav); color: #fff;
  border: 1px solid var(--nav); border-radius: 2px; padding: 4px 10px; font-size: 11px;
  font-weight: 600; cursor: pointer; text-transform: uppercase; letter-spacing: .5px;
  transition: background .15s;
}
.drawer-btn:hover { background: var(--nav2); }
.drawer-btn span { font-size: 9px; transition: transform .15s; display: inline-block; }
.drawer-btn.open span { transform: rotate(90deg); }

/* Botao CSV */
.btn-csv {
  display: inline-flex; align-items: center; gap: 5px;
  background: #fff; color: var(--ink2); border: 1px solid var(--line);
  padding: 3px 9px; border-radius: 2px; font-size: 11px; font-weight: 600;
  cursor: pointer; transition: all .15s;
}
.btn-csv:hover { background: #f0f2f5; color: var(--nav); border-color: var(--nav); }

/* Botao Help Modal */
.hlp {
  margin-left: auto; width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; line-height: 1; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; padding: 0; flex: none;
  transition: all .15s;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

/* Abas de Navegacao (.tabs a.on e .tabs a.active) */
.tabs { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }
.tabs a, .tabs button {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  font-size: 11.5px; padding: 5px 12px; border-radius: 2px; text-decoration: none;
  font-weight: 600; cursor: pointer; transition: all .15s ease; display: inline-flex; align-items: center;
}
.tabs a:hover, .tabs button:hover { background: #f0f2f5; color: var(--nav); border-color: var(--nav); }
.tabs a.on, .tabs a.active, .tabs button.on, .tabs button.active {
  background: var(--nav) !important; color: #fff !important; border-color: var(--nav) !important;
}

/* Toggle (Absoluto / Percentual) */
.toggle { display: inline-flex; border: 1px solid var(--line); border-radius: 2px; overflow: hidden; background: #fff; height: 26px; }
.toggle button {
  border: none; border-right: 1px solid var(--line2); background: #fff; color: var(--ink2);
  padding: 0 10px; font: 600 11px "Segoe UI", Arial, sans-serif; cursor: pointer; line-height: 24px;
}
.toggle button:last-child { border-right: none; }
.toggle button:hover { background: #f0f2f5; color: var(--ink); }
.toggle button.on { background: var(--nav) !important; color: #fff !important; font-weight: 700; }

/* Subtabs */
.subtabs { display: flex; gap: 4px; margin-bottom: 12px; flex-wrap: wrap; }
.subtab {
  padding: 4px 10px; border-radius: 2px; border: 1px solid var(--line);
  background: #fff; cursor: pointer; font-size: 11.5px; font-weight: 600; color: var(--ink2);
  transition: all .15s;
}
.subtab:hover { background: #f0f2f5; color: var(--ink); }
.subtab.on { background: var(--nav); border-color: var(--nav); color: #fff; }

/* Filter Bar & Controls (Design System Oficial Churn Safra) */
.filters {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 10px 14px;
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-end;
}
.fgroup {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.fgroup label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
  font-weight: 600;
}
.msdd {
  position: relative;
  border: 1px solid var(--line);
  border-radius: 2px;
  background: #fff;
  min-width: 170px;
}
.msdd > summary {
  list-style: none;
  cursor: pointer;
  padding: 5px 9px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--ink);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  user-select: none;
}
.msdd > summary::-webkit-details-marker { display: none; }
.msdd > summary:hover { background: #f0f2f5; }
.msdd > summary .cnt {
  background: var(--nav);
  color: #fff;
  border-radius: 2px;
  font-size: 9.5px;
  padding: 1px 5px;
  font-weight: 700;
}
.msdd > summary .car {
  color: var(--ink3);
  font-size: 9px;
}
.msbody {
  position: absolute;
  top: calc(100% + 2px);
  left: 0;
  z-index: 100;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 3px;
  box-shadow: 0 10px 30px rgba(0,0,0,.15);
  padding: 8px;
  min-width: 250px;
  max-height: 320px;
  overflow: auto;
}
.msbody .msearch {
  width: 100%;
  padding: 4px 7px;
  border: 1px solid var(--line);
  border-radius: 2px;
  font: 11.5px "Segoe UI", Arial;
  margin-bottom: 6px;
  color: var(--ink);
}
.msbody .msearch:focus {
  outline: none;
  border-color: var(--blue);
}
.msquick {
  display: flex;
  gap: 4px;
  margin-bottom: 6px;
}
.msquick button {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 2px;
  padding: 2px 8px;
  font-size: 10.5px;
  font-weight: 600;
  cursor: pointer;
  color: var(--ink2);
}
.msquick button:hover {
  background: var(--nav);
  color: #fff;
  border-color: var(--nav);
}
.msbody .grp {
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
  font-weight: 700;
  margin: 6px 0 3px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line2);
  padding-bottom: 2px;
}
.msbody .grp a {
  color: var(--blue);
  cursor: pointer;
  font-size: 10px;
  font-weight: 600;
  text-transform: none;
  text-decoration: none;
}
.msbody .grp a:hover {
  text-decoration: underline;
}
.msitem {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 5px;
  border-radius: 2px;
  font-size: 11.5px;
  color: var(--ink);
  cursor: pointer;
}
.msitem:hover {
  background: #f0f2f5;
}
.msitem input[type="checkbox"] {
  accent-color: var(--nav);
}

/* Quality slider */
.qslider {
  border: 1px solid var(--line);
  border-radius: 2px;
  background: #fff;
  padding: 5px 9px 3px;
  min-width: 240px;
}
.qsl-range {
  width: 100%;
  accent-color: var(--nav);
  height: 3px;
  cursor: pointer;
  margin: 2px 0 4px;
}
.qsl-ticks {
  display: flex;
  justify-content: space-between;
  gap: 2px;
}
.qsl-tick {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: 1;
  cursor: pointer;
}
.qsl-tick .qsl-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #dfe3e8;
  transition: .15s;
}
.qsl-tick.act .qsl-dot { background: var(--nav); }
.qsl-tick.cur .qsl-dot { box-shadow: 0 0 0 2px rgba(27,36,48,.25); }
.qsl-tick .qsl-lbl {
  font-size: 9px;
  font-weight: 600;
  color: var(--ink3);
  text-align: center;
  line-height: 1.1;
}
.qsl-tick.act .qsl-lbl { color: var(--ink); font-weight: 700; }

/* Filter Tags (Barra de status dos filtros ativos) */
.filtbar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin: 0 0 12px;
}
.ftag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid var(--line);
  background: #eef1f4;
  color: var(--ink2);
  white-space: nowrap;
}
.ftag.none {
  background: #f7f8fa;
  color: var(--ink3);
  border-color: var(--line2);
  font-style: italic;
}
.ftag.act {
  background: #fdf3e2;
  color: #8a5d06;
  border-color: #f0dcb4;
}
.ftag .fk {
  color: var(--ink3);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: .4px;
}
.ftag .fclr {
  cursor: pointer;
  background: transparent;
  border-radius: 2px;
  width: 12px;
  height: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  line-height: 1;
  color: var(--ink3);
  margin-left: 2px;
}
.ftag .fclr:hover {
  color: var(--red);
}
.scopebadge {
  display: inline-block;
  font-size: 9.5px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 2px;
  border: 1px solid var(--line);
  margin: 2px 4px 2px 0;
}
.scopebadge.on {
  background: #fdf3e2;
  color: #8a5d06;
  border-color: #f0dcb4;
}
.scopebadge.off {
  background: #f7f8fa;
  color: var(--ink3);
  border-color: var(--line2);
}

/* Indicadores KPIs (Churn Safra Standard) */
.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  border: 1px solid var(--line2); background: #fff; border-radius: 3px; margin-bottom: 14px;
}
.kpi { padding: 10px 14px; border-right: 1px solid var(--line2); border-bottom: 1px solid var(--line2); background: #fff; }
.kpi:last-child { border-right: none; }
.kpi .k, .kpi .lab { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; display: block; }
.kpi .v, .kpi .val { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d, .kpi .sub, .kpi .dl { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }
.up { color: var(--green) !important; font-weight: 700; }
.down { color: var(--red) !important; font-weight: 700; }
.mut { color: var(--ink3) !important; }

/* XKPIs (Resumo Executivo) */
.xkpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 14px; }
.xkpi { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 12px 14px; }
.xkpi .big { font-size: 22px; font-weight: 600; letter-spacing: -.3px; color: var(--ink); }
.xkpi .top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.xkpi .lab { font-size: 10.5px; text-transform: uppercase; letter-spacing: .4px; color: var(--ink3); font-weight: 600; }
.xkpi .sub { font-size: 11px; color: var(--ink2); margin-top: 4px; }
.xkpi .chip { font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 2px; border: 1px solid var(--line); }

/* Level strip (Carteira) */
.lvlstrip { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 14px; }
.lvlcount { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 10px 14px; position: relative; overflow: hidden; }
.lvlcount::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; }
.lvlcount.g::before { background: var(--green); }
.lvlcount.b::before { background: var(--blue); }
.lvlcount.a::before { background: var(--amber); }
.lvlcount.r::before { background: var(--ink3); }
.lvlcount .lc-top { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; }
.lvlcount .lc-dot { width: 6px; height: 6px; border-radius: 50%; }
.lvlcount.g .lc-dot { background: var(--green); }
.lvlcount.b .lc-dot { background: var(--blue); }
.lvlcount.a .lc-dot { background: var(--amber); }
.lvlcount.r .lc-dot { background: var(--ink3); }
.lvlcount .lc-lbl { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .3px; color: var(--ink3); }
.lvlcount .lc-num { font-size: 22px; font-weight: 600; color: var(--ink); line-height: 1.1; }
.lvlcount .lc-unit { font-size: 11.5px; font-weight: 400; color: var(--ink3); }
.lvlcount .lc-sub { font-size: 10.5px; color: var(--ink3); margin-top: 3px; }

/* Tabelas Analiticas & Coluna de Nome de Empresa Padronizada */
.tablewrap { overflow-x: auto; border: 1px solid var(--line2); border-radius: 3px; background: #fff; margin-top: 8px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }
th {
  background: #f7f8fa; color: var(--ink2); font-weight: 600; font-size: 10.5px;
  text-transform: uppercase; letter-spacing: .3px; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid var(--line);
}
th:first-child, td:first-child { text-align: left; }
tbody tr:hover { background: #f7f9fb; }
.stbl thead th { background: #f7f8fa; color: var(--ink2); font-size: 10.5px; text-transform: uppercase; }
.stbl .grp td { background: #f4f6fa; font-weight: 700; }
.stbl .pdvln td:first-child { padding-left: 24px; color: var(--ink2); }

/* Largura Controlada da Coluna de Nome de PDV e Fantasia (max 30 chars com ...) */
table[data-tid="t_v2"] th:first-child, table[data-tid="t_v2"] td:first-child,
table[data-tid="t_v4"] th.c-pdv, table[data-tid="t_v4"] td.c-pdv,
table[data-tid="t_cart"] th:first-child, table[data-tid="t_cart"] td:first-child {
  max-width: 260px !important;
  width: 260px !important;
}
.pdv-col, .c-pdv {
  max-width: 250px !important;
  width: 250px !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pdv-name-cell {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}

/* Dualscroll */
.dualscroll .ds-top { overflow-x: auto; overflow-y: hidden; height: 12px; }
.dualscroll .ds-spacer { height: 1px; }
.dualscroll .ds-body { border-radius: 3px; border: 1px solid var(--line); overflow-x: auto; }
.dualscroll .ds-top::-webkit-scrollbar, .dualscroll .ds-body::-webkit-scrollbar { height: 8px; }
.dualscroll .ds-top::-webkit-scrollbar-thumb, .dualscroll .ds-body::-webkit-scrollbar-thumb { background: #c7cfdc; border-radius: 2px; }

/* Row groups and hierarchy */
.rowgrp { background: #f4f6fa !important; font-weight: 700; cursor: pointer; }
.rowgrp:hover { background: #eef2f6 !important; }
.rowgrp td:first-child::before { content: '▸ '; color: var(--claro); }
.rowgrp.open td:first-child::before { content: '▾ '; }
.rowchild { display: none; }
.rowchild.show { display: table-row; }
.rowsub td:first-child { padding-left: 22px; }
.rowpdv td:first-child { padding-left: 36px; color: var(--ink2); }
.cellwrap { display: flex; flex-direction: column; align-items: flex-end; gap: 1px; }
td:first-child .cellwrap { align-items: flex-start; }
.cellwrap .cv { font-weight: 600; }
.cellwrap .delta { font-size: 9.5px; color: var(--ink3); font-weight: 600; white-space: nowrap; }

/* Carteira Drilldown */
.cart-grp { cursor: pointer; }
.cart-grp td { border-bottom: 1px solid var(--line2); }
.cart-grp .cname { font-weight: 700; color: var(--ink); }
.cart-grp:hover td { background: #f0f2f5; }
.cart-grp[data-depth="0"] td { background: var(--nav) !important; color: #fff !important; font-weight: 700; border-bottom: 1px solid var(--nav2); }
.cart-grp[data-depth="0"]:hover td { background: var(--nav2) !important; }
.cart-grp[data-depth="0"] .cname { color: #fff; font-size: 12px; }
.cart-grp[data-depth="0"] .lvltag { background: rgba(255,255,255,.2); color: #fff; border: 1px solid rgba(255,255,255,.3); }
.cart-grp[data-depth="0"] .cart-car { color: #ff8fa3; }
.cart-grp[data-depth="1"] td { background: #f7f9fc; font-weight: 600; }
.cart-grp[data-depth="2"] td { background: #fbfcfd; }
.cart-grp[data-depth="3"] td, .cart-grp[data-depth="4"] td { background: #ffffff; }
.cart-car { display: inline-block; width: 14px; color: var(--claro); font-weight: 700; font-size: 11px; text-align: center; }
.cart-pdv td { background: #fff; border-bottom: 1px solid var(--line2); }
.cart-pdv td:first-child { color: var(--ink2); font-weight: 400; }

.lvltag {
  display: inline-block;
  font-size: 9.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .4px;
  padding: 1px 6px;
  border-radius: 2px;
  background: #eef2f6;
  color: var(--ink2);
  border: 1px solid var(--line);
  margin-right: 6px;
  vertical-align: middle;
}

/* Cards & Badges */
.card { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 14px; margin-bottom: 14px; }
.card h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--ink2); margin-bottom: 4px; }
.card .csub { font-size: 11px; color: var(--ink3); margin-bottom: 10px; }
.qcard { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 12px; margin-bottom: 12px; }
.qcard h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--ink2); margin-bottom: 4px; }
.qcard .csub { font-size: 11px; color: var(--ink3); margin-bottom: 8px; }
.qcard .chartbox { position: relative; width: 100%; height: 380px; }

.cbadge { display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: .2px; padding: 1px 5px; border-radius: 2px; margin-right: 5px; vertical-align: middle; text-transform: uppercase; }
.cbadge.ci { background: #eaf2ec; color: var(--green); }
.cbadge.cs { background: #eef2f6; color: var(--blue); }
.cbadge.ce { background: #fdf3e2; color: var(--amber); }

.rankn { display: inline-flex; width: 17px; height: 17px; border-radius: 50%; background: var(--nav); color: #fff; font-size: 9.5px; font-weight: 700; align-items: center; justify-content: center; margin-right: 6px; }
.rankn.g2 { background: var(--ink2); }
.rankn.g3 { background: var(--ink3); }

.note { background: #f7f8fa; border: 1px solid var(--line); border-left: 3px solid var(--amber); border-radius: 2px; padding: 8px 12px; font-size: 11.5px; color: var(--ink2); margin: 8px 0 12px; line-height: 1.5; }
.sumnote { background: #f7f8fa; border: 1px solid var(--line); border-left: 3px solid var(--blue); border-radius: 2px; padding: 8px 12px; font-size: 11.5px; color: var(--ink2); margin: 8px 0 14px; line-height: 1.5; }

.vtitle { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: var(--ink2); margin: 0 0 3px; }
.vdesc { font-size: 11.5px; color: var(--ink3); margin: 0 0 12px; line-height: 1.45; }

/* Grid 2 */
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 1080px) { .grid2 { grid-template-columns: 1fr; } }

/* Inputs & Search */
.searchbox { width: 100%; max-width: 480px; padding: 5px 9px; border: 1px solid var(--line); border-radius: 2px; font: 12px "Segoe UI", Arial; color: var(--ink); }
.searchbox:focus { outline: none; border-color: var(--blue); }
.filterrow .flop { border: 1px solid var(--line); border-radius: 2px; font-size: 11px; padding: 2px 4px; }
.filterrow .flval { width: 52px; text-align: center; border: 1px solid var(--line); border-radius: 2px; font-size: 11px; padding: 2px 4px; }
.filterrow .fltxt { border: 1px solid var(--line); border-radius: 2px; font-size: 11px; padding: 2px 4px; }

/* Botoes Auxiliares */
.btn { border: 1px solid var(--line); background: #fff; border-radius: 2px; padding: 4px 10px; font-size: 11.5px; font-weight: 600; cursor: pointer; color: var(--ink); }
.btn.sec { color: var(--ink2); }
.btn:hover { background: #f0f2f5; }
.btn.pri { background: var(--nav); color: #fff; border-color: var(--nav); }
.print-btn { background: #fff; border: 1px solid var(--line); border-radius: 2px; padding: 4px 10px; font-size: 11.5px; font-weight: 600; cursor: pointer; color: var(--ink2); }
.print-btn:hover { background: #f0f2f5; color: var(--nav); border-color: var(--nav); }

/* Modais Popups e Zoom (Oficiais Churn Safra) */
.modal { position: fixed; inset: 0; background: rgba(18,24,32,.55); display: none; z-index: 250; align-items: center; justify-content: center; padding: 24px; }
.modal.on { display: flex; }
.modal .box { background: #fff; max-width: 720px; width: 100%; max-height: 82vh; overflow: auto; border-radius: 4px; box-shadow: 0 14px 48px rgba(0,0,0,.3); border: 1px solid var(--line); }
.modal .hd { padding: 14px 18px; border-bottom: 1px solid var(--line2); display: flex; align-items: center; gap: 10px; position: sticky; top: 0; background: #fff; }
.modal .hd h3 { margin: 0; font-size: 14px; font-weight: 600; }
.modal .hd button { margin-left: auto; border: none; background: none; font-size: 20px; line-height: 1; color: var(--ink3); cursor: pointer; padding: 0 4px; }
.modal .bd { padding: 16px 18px; font-size: 12.5px; line-height: 1.7; color: var(--ink2); }

.modal-bg { position: fixed; inset: 0; background: rgba(18,24,32,.55); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-box { background: #fff; border-radius: 4px; border: 1px solid var(--line); box-shadow: 0 14px 48px rgba(0,0,0,.3); padding: 16px 18px; max-width: 980px; width: 100%; max-height: 88vh; overflow: auto; }
.modal-box .mhead { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line2); }
.modal-box h3 { margin: 0; font-size: 13.5px; font-weight: 700; color: var(--ink); }
.mclose { border: 1px solid var(--line); background: #fff; border-radius: 2px; padding: 4px 10px; font-size: 11px; font-weight: 600; color: var(--ink2); cursor: pointer; }
.mclose:hover { background: var(--nav); color: #fff; border-color: var(--nav); }
.qbtn { border: 1px solid var(--line); background: #fff; border-radius: 2px; padding: 3px 9px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--ink2); white-space: nowrap; }
.qbtn:hover { background: #f0f2f5; color: var(--ink); }
.qbtn.on { background: var(--nav); border-color: var(--nav); color: #fff; }
.exp-menu { position: absolute; background: #fff; border: 1px solid var(--line); border-radius: 2px; box-shadow: 0 8px 24px rgba(0,0,0,.15); padding: 4px; z-index: 220; min-width: 180px; }
.exp-menu button { display: block; width: 100%; text-align: left; border: none; background: none; padding: 5px 9px; font-size: 11.5px; cursor: pointer; border-radius: 2px; color: var(--ink); font-family: inherit; }
.exp-menu button:hover { background: #f0f2f5; color: var(--nav); }

/* Tooltips */
.gtip, .maptip {
  position: fixed; display: none; z-index: 300; pointer-events: none;
  background: rgba(20,27,36,.97); color: #fff; font: 11.5px/1.55 "Segoe UI", Arial;
  padding: 8px 10px; border-radius: 3px; max-width: 290px; box-shadow: 0 6px 20px rgba(0,0,0,.28);
}

/* SVG Halo e Responsividade */
svg text {
  font-family: "Segoe UI", Roboto, Arial, sans-serif;
}
.chartbox { position: relative; width: 100%; height: 360px; }

/* Import Screen Locked State */
.lockbox { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 24px; max-width: 520px; margin: 40px auto; text-align: center; }
.lockbox h3 { margin-bottom: 8px; font-size: 15px; }
.lockbox p { color: var(--ink2); font-size: 12.5px; line-height: 1.6; margin-bottom: 14px; }
.lockbox input { padding: 6px 10px; border: 1px solid var(--line); border-radius: 2px; font-size: 12px; margin-right: 6px; width: 200px; }

footer {
  border-top: 1px solid var(--line2); padding: 24px 0 10px; font-size: 11.5px; color: var(--ink3);
  margin-top: 24px; text-align: center; line-height: 1.6;
}
footer b { color: var(--ink2); }
"""

html_body = """
<!-- Staging Banner Oficial -->
<div class="staging-banner">
  <span>[STAGING] <b>AMBIENTE SECUNDÁRIO DE TESTE</b> — Painel de Taxa de Aprovação de Crédito PF</span>
  <span class="staging-pill">Staging Preview</span>
</div>

<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <h1>
      <b>Taxa de Aprovação de Crédito PF</b>
      <span>Cidade e PDV · Regional Norte</span>
    </h1>
    <div class="hd-actions">
      <a href="/" class="hd-btn" title="Voltar ao Pephub — Portal de Churn & Qualidade">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Portal Pephub
      </a>
      <a href="/churn/" class="hd-btn" title="Acessar o Painel de Churn Safra">Painel Safra</a>
      <a href="/fpd/" class="hd-btn" title="Acessar o Painel Executivo FPD">Painel FPD</a>
      <a href="/panorama-market-share/" class="hd-btn" title="Acessar o Panorama Market Share">Panorama MS</a>
      <a href="/pep-tools/market-share/" class="hd-btn" title="Acessar o Market Share Studio">MS Studio</a>
      <div id="userWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Pephub — Portal de Churn & Qualidade">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Agosto / 2026</b></span>
    <span class="dot"></span>
    <span>Regional Norte <b>(AM · AP · MA · PA · PI · RR)</b></span>
    <span class="dot"></span>
    <span>Escopo: <b>Cidades e Redes de PDVs Residencial</b></span>
    <div class="hd-right"><span>Planejamento & Performance · Regional Norte</span></div>
  </div>
</header>

<div class="wrap">

  <!-- Painel de Navegação Executiva (Tabs Churn Safra com Controles) -->
  <div class="panel" style="margin-bottom:14px;">
    <h2>
      NAVEGAÇÃO DO PAINEL
      <span class="panel-note" id="viewNote">Consultas, recusas e perfil — RNO vs Brasil e por cidade</span>
      <div style="margin-left:auto; display:flex; align-items:center; gap:8px;">
        <button class="drawer-btn" id="btnDrawer" onclick="toggleFilterDrawer()"><span id="drawerIco">▾</span> Filtros</button>
        <button class="btn-csv" onclick="exportActiveTableToCSV()">Exportar CSV</button>
        <div class="toggle" id="modeToggle">
          <button data-m="abs">Absoluto (Volume)</button>
          <button data-m="pct" class="on">Percentual (Taxa)</button>
        </div>
        <button class="hlp" data-h="aprovacao" title="Ajuda Contextual do Painel" onclick="openHelpModal('aprovacao')">?</button>
      </div>
    </h2>
    <div class="pbody" style="padding:10px 14px;">
      <nav class="tabs" id="nav">
        <a data-v="v1" class="active on">1. Visão Geral</a>
        <a data-v="v2">2. Canais & PDVs</a>
        <a data-v="v3">3. Visão Diária</a>
        <a data-v="v4">4. PDVs Detalhados</a>
        <a data-v="cart">5. Carteira / Hierarquia</a>
        <a data-v="v5">6. Insights & Recomendações</a>
        <a data-v="sum">Resumo Executivo</a>
        <a data-v="imp">Importar Dados</a>
      </nav>
      <div style="margin-top:10px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; border-top:1px solid var(--line2); padding-top:8px;">
        <h3 id="ttl" style="margin:0; font-size:13.5px; font-weight:700; color:var(--ink); display:flex; align-items:baseline; gap:8px;">
          Visão Geral
          <small id="tsub" style="font-size:11.5px; font-weight:400; color:var(--ink3);">Consultas, recusas e perfil — RNO vs Brasil e por cidade</small>
        </h3>
      </div>
    </div>
  </div>

  <!-- Conteúdo Dinâmico das Visões -->
  <div id="content"></div>

  <!-- Help Modal Oficial (Design System Churn Safra) -->
  <div class="modal" id="helpModal" onclick="if(event.target===this)closeHelpModal()">
    <div class="box">
      <div class="hd">
        <h3 id="helpTitle">Ajuda Contextual</h3>
        <button onclick="closeHelpModal()">✕</button>
      </div>
      <div class="bd" id="helpBody"></div>
      <div style="display:none;" aria-hidden="true">
        <button class="hlp" data-h="scatter" onclick="openHelpModal('scatter')">?</button>
        <button class="hlp" data-h="risco" onclick="openHelpModal('risco')">?</button>
        <button class="hlp" data-h="matriz" onclick="openHelpModal('matriz')">?</button>
      </div>
    </div>
  </div>

  <footer>
    <b>Painel Executivo de Taxa de Aprovação de Crédito PF — Banda Larga Residencial · Regional Norte</b><br>
    Posição Oficial: Agosto / 2026 · Elaborado pela equipe de Planejamento & Performance RNO.<br>
    Documento analítico executivo para uso corporativo exclusivo Claro Brasil.
  </footer>

</div>
"""

help_script = """
const HELP = {
  risco: "Visão de Risco & Score: Limiares de aprovação de entrada, ofensores de crédito (política interna), restrições externas (Serasa/SPC) e antifraude.",
  scatter: "Matriz de Dispersão & Quadrantes Estratégicos: Cruzamento entre taxa de aprovação e índices de risco e fraude por canal e cidade.",
  filtros: "Filtros multidimensionais que restringem a base por Produto, Canal, Cidade/Município e Níveis Hierárquicos de Carteira.",
  aprovacao: "Taxa de Aprovação = Propostas Aprovadas / Propostas Submetidas. Percentual de entrada de novos clientes residenciais com filtros dinâmicos por canal, cidade e PDV.",
  canais: "Desempenho por Canal de Venda (Lojas Próprias, Agentes Autorizados, Televendas, Canais Digitais e Porta a Porta).",
  diaria: "Evolução temporal diária das taxas de aprovação e volume de propostas ao longo da safra corrente.",
  pdvs: "Ranking detalhado por DV_EQUIPE_VENDA e PDVs parceiros identificando ofensores de aprovação e fraude.",
  carteira: "Visão hierárquica por estrutura comercial: Canal → Gerência Regional → Gerência de Filial → Coordenação → Executivo.",
  insights: "Matriz de dispersão e quadrantes estratégicos cruzando taxa de aprovação com índice de recusa por fraude e inadimplência.",
  resumo: "Síntese executiva formatada para impressão gerencial e prestação de contas à diretoria regional.",
  matriz: "Matriz de acompanhamento de safras e marcos analíticos da regional."
};

function openHelpModal(key) {
  const text = HELP[key] || HELP['aprovacao'];
  const titleMap = {
    filtros: "Filtros Multidimensionais",
    risco: "Visão de Risco & Score",
    scatter: "Matriz de Dispersão & Quadrantes",
    aprovacao: "Taxa de Aprovação de Crédito PF",
    canais: "Canais de Venda & PDVs",
    diaria: "Visão Diária de Recusas",
    pdvs: "PDVs (DV_EQUIPE_VENDA)",
    carteira: "Carteira & Hierarquia Comercial",
    insights: "Insights Adaptativos",
    resumo: "Resumo Executivo para Prestação de Contas",
    matriz: "Matriz de Safra Regional"
  };
  const titleEl = document.getElementById('helpTitle');
  const bodyEl = document.getElementById('helpBody');
  const modalEl = document.getElementById('helpModal');
  if (titleEl) titleEl.textContent = titleMap[key] || "Ajuda Contextual";
  if (bodyEl) bodyEl.innerHTML = `<p>${text}</p>`;
  if (modalEl) modalEl.classList.add('on');
}

function closeHelpModal() {
  const modalEl = document.getElementById('helpModal');
  if (modalEl) modalEl.classList.remove('on');
}

// Gaveta de Filtros Retratil
function toggleFilterDrawer() {
  S.filtersHidden = !S.filtersHidden;
  const f = document.querySelector('.filters');
  const btn = document.getElementById('btnDrawer');
  const ico = document.getElementById('drawerIco');
  if (f) {
    f.style.display = S.filtersHidden ? 'none' : 'flex';
  }
  if (btn) btn.classList.toggle('open', !S.filtersHidden);
  if (ico) ico.textContent = S.filtersHidden ? '▸' : '▾';
}

// Exportacao CSV no Cliente (Blob / createObjectURL)
function exportActiveTableToCSV() {
  const table = document.querySelector('#content table');
  if (!table) {
    alert('Nenhuma tabela visível para exportação na visão atual.');
    return;
  }
  let csv = [];
  const rows = table.querySelectorAll('tr');
  for (let i = 0; i < rows.length; i++) {
    let row = [], cols = rows[i].querySelectorAll('th, td');
    for (let j = 0; j < cols.length; j++) {
      let data = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, ' ').replace(/\"/g, '\"\"').trim();
      row.push('\"' + data + '\"');
    }
    csv.push(row.join(';'));
  }
  const blob = new Blob(['\\ufeff' + csv.join('\\r\\n')], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `aprovacao_credito_${S ? S.view : 'dados'}.csv`;
  a.click();
}

// Autenticacao e Identidade do Usuario no Header
async function initUserWidget() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const u = await res.json();
      const el = document.getElementById('userWidget');
      if (el && u.authenticated) {
        const fn = u.nome_completo ? u.nome_completo.split(' ')[0] : 'Usuário';
        el.innerHTML = `
          <span style="color:#fff;font-size:11.5px;font-weight:600;white-space:nowrap;background:rgba(255,255,255,.15);padding:4px 8px;border-radius:3px">${fn} (${u.area || 'RNO'})</span>
          ${u.is_admin ? '<a href="/admin/" style="background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.4);padding:4px 8px;border-radius:3px;font-size:10.5px;font-weight:700;text-decoration:none">Admin</a>' : ''}
          <button id="btnLogoutAprovacao" style="background:none;border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 8px;border-radius:3px;font-size:10.5px;cursor:pointer;font-weight:600">Sair</button>
        `;
        const btnLogout = document.getElementById('btnLogoutAprovacao');
        if (btnLogout) {
          btnLogout.addEventListener('click', async () => {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login/';
          });
        }
      }
    }
  } catch (e) {}
}
initUserWidget();
"""

full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Taxa de Aprovação de Crédito PF — Cidade e PDV · Regional Norte</title>
<style>{official_css}</style>
</head>
<body>
{html_body}
<script>{data_script}</script>
<script>{engine_script}</script>
<script>{help_script}</script>
</body>
</html>
"""

with open('public_staging/aprovacao-credito/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Recreated public_staging/aprovacao-credito/index.html with all fixes applied successfully!")
