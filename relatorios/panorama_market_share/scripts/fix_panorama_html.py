import re

with open('public_staging/panorama-market-share/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. CSS to add
css_addition = """
/* Filter Bar & Dropdown Multi-Selects (Churn Safra Standard) */
.filterbar { background: transparent; padding: 0; }
.fl-lbl { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); margin-right: 2px; }
.ms { position: relative; display: inline-block; }
.ms > button {
  border: 1px solid var(--line); background: #fff; border-radius: 2px;
  padding: 5px 10px; font-size: 11.5px; font-weight: 600; color: var(--ink);
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;
}
.ms > button:hover { background: #f0f2f5; border-color: var(--nav); }
.ms > button .cnt { background: var(--red); color: #fff; border-radius: 999px; font-size: 9.5px; padding: 1px 5px; font-weight: 700; }
.ms > button .cx { color: var(--ink3); font-size: 10px; }
.ms .panel {
  position: absolute; top: calc(100% + 4px); left: 0; background: #fff;
  border: 1px solid var(--line); border-radius: 3px; box-shadow: 0 4px 14px rgba(0,0,0,.12);
  padding: 8px; min-width: 220px; max-height: 320px; overflow-y: auto; display: none; z-index: 100;
}
.ms.open .panel { display: block; }
.ms .panel input.srch {
  width: 100%; border: 1px solid var(--line); border-radius: 2px; padding: 4px 8px;
  font: 11.5px "Segoe UI", Arial; margin-bottom: 6px; outline: none; box-sizing: border-box;
}
.ms .panel input.srch:focus { border-color: var(--blue); }
.ms .opts { max-height: 240px; overflow-y: auto; }
.ms .opt { display: flex; align-items: center; gap: 6px; padding: 4px 6px; border-radius: 2px; font-size: 11.5px; cursor: pointer; color: var(--ink); }
.ms .opt:hover { background: #f0f2f5; }
.ms .opt input { accent-color: var(--red); }
.seg-pills { display: inline-flex; border: 1px solid var(--line); border-radius: 2px; overflow: hidden; background: #fff; }
.seg-pills button { border: 0; background: #fff; color: var(--ink2); padding: 5px 11px; font-size: 11.5px; font-weight: 600; cursor: pointer; transition: background .15s; }
.seg-pills button:hover { background: #f0f2f5; }
.seg-pills button.on { background: var(--nav) !important; color: #fff !important; font-weight: 700; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.tag2 .x { cursor: pointer; color: var(--ink3); font-weight: 700; font-size: 11px; }
.tag2 .x:hover { color: var(--red); }
.clearall { font-size: 11.5px; color: var(--red); cursor: pointer; font-weight: 600; border: 1px solid transparent; background: none; padding: 3px 6px; border-radius: 2px; }
.clearall:hover { text-decoration: underline; }

/* Top KPI Bar CoverMeta (Churn Safra Pattern) */
#coverMeta.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  border: 1px solid var(--line2); background: #fff; border-radius: 3px; margin-bottom: 14px;
}
#coverMeta > div { padding: 10px 14px; border-right: 1px solid var(--line2); }
#coverMeta > div:last-child { border-right: none; }
#coverMeta span { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; display: block; }
#coverMeta b { font-size: 22px; font-weight: 600; color: var(--ink); display: block; margin-top: 3px; line-height: 1.1; letter-spacing: -.3px; }
"""

html = html.replace('</style>', css_addition + '\n</style>', 1)

# 2. Replace filter panel and add coverMeta
target_filter_panel = """  <!-- Painel de Filtros Globais (Churn Safra Pattern) -->
  <div class="panel">
    <h2>FILTROS GLOBAIS <span class="note">Filtre por Estado, DDD, Município, Escopo e Tipo de Pessoa</span> <button class="drawer-btn" style="margin-left:auto;" onclick="document.getElementById('fbody').classList.toggle('collapsed')">Filtros</button> <button class="hlp" data-h="filtros">?</button></h2>
    <div class="pbody" id="fbody">
      <div class="filterbar" style="border:none; box-shadow:none; padding:0; position:static;">
        <div class="wrap" style="padding:0; gap:8px;">
          <!-- Filtros preservados para manter reatividade total dos scripts -->
          <div class="ms" id="msUf"><button type="button">UF <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar UF..."><div class="opts"></div></div></div>
          <div class="ms" id="msDdd"><button type="button">DDD <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar DDD..."><div class="opts"></div></div></div>
          <div class="ms" id="msMun"><button type="button">Município <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar município..."><div class="opts"></div></div></div>
          
          <div class="seg-pills" id="segZona">
            <button class="on" data-z="ALL">Todas as Cidades</button>
            <button data-z="RNO">Apenas RNO Oficial</button>
            <button data-z="CAB">Cidades Cabeadas Claro</button>
          </div>

          <div class="seg-pills" id="segPess">
            <button class="on" data-p="ALL">PF + PJ</button>
            <button data-p="PF">Pessoa Física</button>
            <button data-p="PJ">Pessoa Jurídica</button>
          </div>

          <div class="tags" id="activeTags"></div>
          <button class="clearall" id="btnClearAll" style="margin-left:auto; display:none;">Limpar filtros</button>
        </div>
      </div>
    </div>
  </div>"""

replacement_filter_panel = """  <!-- Resumo de Indicadores Chave no Topo (CoverMeta) -->
  <div class="kpis" id="coverMeta"></div>

  <!-- Painel de Filtros Globais (Churn Safra Pattern) -->
  <div class="panel">
    <h2>FILTROS GLOBAIS <span class="note">Filtre por Estado, DDD, Município, Capital/Interior, Produto, Escopo e Pessoa</span> <button class="hlp" data-h="filtros">?</button></h2>
    <div class="pbody" id="fbody">
      <div class="filterbar" style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
        <span class="fl-lbl">Filtros:</span>
        <div class="ms" id="msUF"></div>
        <div class="ms" id="msDDD"></div>
        <div class="ms" id="msMun"></div>
        <div class="ms" id="msZona"></div>
        <div class="ms" id="msProd"></div>
        <div class="seg-pills" id="scopePills">
          <button data-v="ambos" class="on">Ambos</button><button data-v="movel">Móvel</button><button data-v="fixa">Fixa</button>
        </div>
        <div class="seg-pills" id="pessPills">
          <button data-v="todos" class="on">PF+PJ</button><button data-v="PF">PF</button><button data-v="PJ">PJ</button>
        </div>
        <div class="tags" id="filterTags" style="margin-left:auto;"></div>
      </div>
    </div>
  </div>"""

if target_filter_panel in html:
    html = html.replace(target_filter_panel, replacement_filter_panel)
    print("Filter panel replaced successfully.")
else:
    print("Warning: target_filter_panel not found exactly as string. Searching with regex...")
    # fallback regex
    pattern = r'<!-- Painel de Filtros Globais.*?</div>\s*</div>\s*</div>\s*</div>'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        html = html[:match.start()] + replacement_filter_panel + html[match.end():]
        print("Filter panel replaced via regex!")
    else:
        print("ERROR: Could not find filter panel block!")

# 3. Clean duplicate closing tags at bottom
# Remove the extra </body></html> before <script>const HELP
html = re.sub(r'</script>\s*</body>\s*</html>\s*<script>\s*const HELP', '</script>\n\n<script>\nconst HELP', html)

with open('public_staging/panorama-market-share/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated public_staging/panorama-market-share/index.html")
