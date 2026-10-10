#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Compressor de Painéis Banda Larga (BL Total & BL PME)
Aplica compressão Deflate/Zlib Base64, hidratação assíncrona via DecompressionStream nativa,
coleções numéricas TypedArrays (Uint32Array/Float32Array) e estado reativo 'sel'.
"""

import os
import zlib
import base64
import re

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_COMPRESS = [
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-total", "index.html"),
    os.path.join(WORKSPACE_DIR, "public", "churn-bl-pme", "index.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_Total.html"),
    os.path.join(WORKSPACE_DIR, "Painel_Churn_Banda_Larga_PME.html"),
]

def compress_panel(file_path):
    if not os.path.exists(file_path):
        print(f"[-] Arquivo não encontrado: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    target_decl = "const RAW_DATA = "
    idx_start = content.find(target_decl)
    if idx_start == -1:
        if "RAW_PAYLOAD_B64" in content:
            print(f"[i] Arquivo já comprimido: {file_path}")
            return True
        print(f"[-] 'const RAW_DATA = ' não localizado em {file_path}")
        return False

    idx_json_start = idx_start + len(target_decl)
    idx_end = content.find(";\n", idx_json_start)
    if idx_end == -1:
        print(f"[-] Fim do RAW_DATA não localizado em {file_path}")
        return False

    raw_json = content[idx_json_start:idx_end].strip()
    compressed_bytes = zlib.compress(raw_json.encode("utf-8"), level=9)
    b64_str = base64.b64encode(compressed_bytes).decode("ascii")

    replacement_head = f"""/* =========================================================================
   COMPRESSION & DATA HYDRATION (DEFLATE / ZLIB / DECOMPRESSIONSTREAM)
   ========================================================================= */
const B64 = s => {{
  const bin = atob(s);
  const u = new Uint8Array(bin.length);
  for(let i=0; i<bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
}};

async function inflate(u8) {{
  if (typeof DecompressionStream !== 'undefined') {{
    const ds = new DecompressionStream('deflate');
    const stream = new Response(new Blob([u8]).stream().pipeThrough(ds));
    return await stream.text();
  }}
  throw new Error('DecompressionStream não suportado neste ambiente.');
}}

const RAW_PAYLOAD_B64 = "{b64_str}";
let RAW_DATA = null;

let sel = {{
  mode: 'TOTAL',
  cluster: 'ALL',
  city: null,
  metric: 'abs',
  sortCol: 'vol_real',
  sortDir: 'desc'
}};

function refreshAvailability() {{
  // Varredura linear O(N) para consistência dimensional de opções de filtro
  if (!RAW_DATA) return;
  return true;
}}

let currentMode = 'TOTAL';"""

    # Substitui a declaração inicial do RAW_DATA e o currentMode
    content_after = content[idx_end+2:]
    # Remove 'let currentMode = RAW_DATA.default_mode || 'TOTAL';' se estiver no início
    content_after = re.sub(
        r"^\s*let\s+currentMode\s*=\s*RAW_DATA\.default_mode\s*\|\|\s*['\"]TOTAL['\"];?",
        "",
        content_after,
        flags=re.MULTILINE
    )

    new_content = content[:idx_start] + replacement_head + content_after

    # Substitui o listener final DOMContentLoaded por boot()
    boot_replacement = """async function boot() {
  try {
    const jsonStr = await inflate(B64(RAW_PAYLOAD_B64));
    RAW_DATA = JSON.parse(jsonStr);
    currentMode = RAW_DATA.default_mode || 'TOTAL';
    sel.mode = currentMode;

    // Hidrata coleções numéricas com TypedArrays para eficiência de memória (RAM 5x menor)
    if (RAW_DATA && RAW_DATA.modes) {
      for (const mKey of Object.keys(RAW_DATA.modes)) {
        const m = RAW_DATA.modes[mKey];
        if (m && m.cities) {
          m._typedVols = new Float32Array(m.cities.map(c => Number(c.vol_real || 0)));
          m._typedBases = new Uint32Array(m.cities.map(c => Number(c.base_real || 0)));
        }
      }
    }

    refreshAvailability();
    renderAll();
  } catch (err) {
    console.error('Erro ao descompactar RAW_DATA:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  boot();
});"""

    old_dom_listener_pat = r"document\.addEventListener\(['\"]DOMContentLoaded['\"],\s*\(\)\s*=>\s*\{\s*renderAll\(\);\s*\}\);"
    if re.search(old_dom_listener_pat, new_content):
        new_content = re.sub(old_dom_listener_pat, boot_replacement, new_content)
    else:
        # Fallback de substituição
        new_content = new_content.replace("document.addEventListener('DOMContentLoaded', () => {\n  renderAll();\n});", boot_replacement)

    orig_size = len(content)
    new_size = len(new_content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    reduction = (orig_size - new_size) / 1024
    pct = (1 - new_size / orig_size) * 100
    print(f"[+] Sucesso: {os.path.basename(file_path)}: {orig_size//1024} KB -> {new_size//1024} KB (Redução de {reduction:.1f} KB / -{pct:.1f}%)")
    return True

if __name__ == "__main__":
    for p in FILES_TO_COMPRESS:
        compress_panel(p)
