#!/usr/bin/env python3
"""
Adiciona os cards de Gerador de Cards de Aniversário e Market Share Studio
à seção PeP Tools do portal em public_staging/index.html.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def add_cards():
    path = "public_staging/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = '  <!-- SEÇÃO PEP TOOLS -->\n  <div class="section-title" id="pep-tools" style="margin-top:36px">PeP Tools · Soluções de Suporte & Produtividade Operacional</div>\n\n  <div class="cards">\n\n    <!-- Card: Divulgação Corporativa -->'

    cards_to_insert = """  <!-- SEÇÃO PEP TOOLS -->
  <div class="section-title" id="pep-tools" style="margin-top:36px">PeP Tools · Soluções de Suporte & Produtividade Operacional</div>

  <div class="cards">

    <!-- Card: Gerador de Cards de Aniversário -->
    <div class="card" style="border-top: 3px solid #e02424;">
      <div class="card-header">
        <div>
          <h3 class="card-title">Gerador de Card de Aniversário — TV 16:9</h3>
          <span style="font-size:11px;color:var(--ink3)">Auxiliar de Produção Visual para Telas da Regional</span>
        </div>
        <span class="card-tag active" style="background:#fef2f2;color:#b91c1c;border-color:#fecaca;">Novo! PeP Tool</span>
      </div>
      <div class="card-body">
        <p class="card-desc">Ferramenta dedicada para criação instantânea de homenagens e cards de aniversário para os colaboradores da Regional Norte. Permite upload de foto com enquadramento fino, data, nome estilizado e mensagem personalizada com arraste livre, gerando a imagem em resolução oficial Full HD (1920x1080p 16:9) pronta para transmissão.</p>
        <div class="card-meta">
          <div><span>Formato de Saída</span><strong>JPG 1080p (1920x1080)</strong></div>
          <div><span>Proporção Oficial</span><strong>16:9 Widescreen TV</strong></div>
          <div><span>Interatividade</span><strong>Arraste Livre & Recorte</strong></div>
          <div><span>Destino</span><strong>Curadoria de TVs PeP</strong></div>
        </div>
        <div class="quick-kpis">
          <span class="kpi-tag red">TV 16:9 Full HD</span>
          <span class="kpi-tag blue">Upload & Enquadramento</span>
          <span class="kpi-tag amber">Arraste Interativo</span>
          <span class="kpi-tag green">100% Autocontido</span>
        </div>
      </div>
      <div class="card-footer">
        <a href="/pep-tools/aniversario/" class="btn-primary">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          Criar Card de Aniversário →
        </a>
        <a href="/pep-tools/divulgacao/" class="btn-secondary" title="Acessar painel de envio de mídias para as TVs">
          📺 Enviar para TV
        </a>
      </div>
    </div>

    <!-- Card: Market Share Studio Telecom -->
    <div class="card" style="border-top: 3px solid #0071e3;">
      <div class="card-header">
        <div>
          <h3 class="card-title">Market Share Studio — Telecom & Infográficos</h3>
          <span style="font-size:11px;color:var(--ink3)">Estúdio de Criação de Gráficos, Tabelas e Matrizes</span>
        </div>
        <span class="card-tag active" style="background:#eff6ff;color:#1d4ed8;border-color:#bfdbfe;">Novo! PeP Tool</span>
      </div>
      <div class="card-body">
        <p class="card-desc">Assistente completo para concepção de gráficos de Market Share, infográficos telecom, matrizes de concorrência e organogramas operacionais. Suporta importação direta de arquivos Excel (XLSX), visualização em tempo real e exportação em SVG vetorial de alta definição para relatórios executivos e apresentações.</p>
        <div class="card-meta">
          <div><span>Formatos Gráficos</span><strong>Pizza, Donut, Barras, Org</strong></div>
          <div><span>Importação</span><strong>Planilhas Excel (.xlsx)</strong></div>
          <div><span>Exportação</span><strong>SVG Puro, PNG & Clipboard</strong></div>
          <div><span>Operação</span><strong>100% Offline & Local</strong></div>
        </div>
        <div class="quick-kpis">
          <span class="kpi-tag blue">Market Share Telecom</span>
          <span class="kpi-tag green">Excel XLSX Import</span>
          <span class="kpi-tag purple">SVG Vetorial Puro</span>
          <span class="kpi-tag amber">Organogramas & Tabelas</span>
        </div>
      </div>
      <div class="card-footer">
        <a href="/pep-tools/market-share/" class="btn-primary" style="background:#0071e3;">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          Abrir Market Share Studio →
        </a>
        <a href="/pep-tools/divulgacao/" class="btn-secondary" title="Usar imagem em slide nas TVs">
          📺 Usar em Slide de TV
        </a>
      </div>
    </div>

    <!-- Card: Divulgação Corporativa -->"""

    if target in content:
        content = content.replace(target, cards_to_insert)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Cards adicionados com sucesso ao public_staging/index.html!")
    else:
        print("⚠️ Target não encontrado no arquivo.")

if __name__ == "__main__":
    add_cards()
