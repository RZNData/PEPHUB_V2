import re

with open('public_staging/pep-tools/market-share/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace header actions to include hidden scatter and risco helpers
actions_pattern = r'<div style="margin-left:auto; display:flex; align-items:center; gap:\d+px;">.*?</div>\s*</div>\s*<div class="hd-sub">'
new_actions = """<div style="margin-left:auto; display:flex; align-items:center; gap:12px;">
      <label style="display:inline-flex; align-items:center; gap:6px; font-size:11.5px; color:#fff; cursor:pointer;">
        <input type="checkbox" id="autoColorToggle" checked onchange="onAutoToggle()" style="accent-color:var(--gold);">
        <span>Cor Automática</span>
      </label>
      <button class="hlp" data-h="scatter" style="display:none">?</button>
      <button class="hlp" data-h="risco" style="display:none">?</button>
      <button class="hlp" data-h="studio" title="Ajuda">?</button>
      <a href="/" class="back-hub">‹ Portal Pephub</a>
    </div>
  </div>
  <div class="hd-sub">"""

html = re.sub(actions_pattern, new_actions, html, count=1, flags=re.DOTALL)

# Replace window.HELP with const HELP
old_help = """<script>
window.HELP = {"""
new_help = """<script>
const HELP = {"""
html = html.replace(old_help, new_help)

with open('public_staging/pep-tools/market-share/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated public_staging/pep-tools/market-share/index.html with const HELP and required data-h buttons.")
