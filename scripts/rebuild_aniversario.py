#!/usr/bin/env python3
"""
Reconstrói o Gerador de Card de Aniversário (TV 16:9) em public_staging/pep-tools/aniversario/index.html,
alinhando-o 100% ao Design System oficial do PEP HUB (PADRAO_DESIGN_PAINEIS.md):
- Header oficial com gradiente corporativo da Claro
- Variáveis CSS semânticas padronizadas (:root)
- Zero dependências externas (html2canvas local, template local, fonte local)
- Layout executivo com painéis, botões e tipografia corporativa
- Enquadramento perfeito da foto na moldura da imagem (1920x1080) e textos legíveis sem colisão
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def rebuild_aniversario():
    target_file = os.path.join("public_staging", "pep-tools", "aniversario", "index.html")
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gerador de Card de Aniversário (TV 16:9) — PeP Tools | Pephub</title>
<style>
@font-face {
  font-family: 'ShineValentine';
  src: url('Shine in Valentine.ttf') format('truetype');
  font-display: swap;
}

:root {
  --bg: #f4f5f7;
  --panel: #ffffff;
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
  --claro-red: #e02424;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Staging Banner Sóbrio */
.staging-banner {
  background: var(--nav);
  color: #c9d2df;
  padding: 6px 26px;
  font-size: 11px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 100;
}
.staging-pill {
  background: rgba(255,255,255,0.15);
  color: #fff;
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 10px;
  text-transform: uppercase;
  font-weight: 600;
}

/* Header Corporativo Oficial PEP HUB */
header { background: #fff; border-bottom: 1px solid var(--line); }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 26px;
}
.hd-ico {
  width: 46px;
  height: 46px;
  min-width: 46px;
  border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,.95);
  display: flex;
  align-items: center;
  justify-content: center;
}
.hd-bar h1 {
  margin: 0;
  color: #fff;
  font-size: 30px;
  font-weight: 400;
  letter-spacing: -.4px;
  line-height: 1.05;
  display: flex;
  align-items: baseline;
  gap: 11px;
  flex-wrap: wrap;
}
.hd-bar h1 b { font-weight: 800; letter-spacing: -1px; }
.hd-bar h1 span { font-weight: 300; font-size: 24px; color: rgba(255,255,255,.93); }
.hd-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.hd-btn {
  background: rgba(255,255,255,.18);
  color: #fff;
  border: 1px solid rgba(255,255,255,.35);
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  text-decoration: none;
  transition: background .15s;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.hd-btn:hover { background: rgba(255,255,255,.32); color: #fff; }
.hd-btn.primary { background: #fff; color: var(--red); font-weight: 700; border-color: #fff; }
.hd-btn.primary:hover { background: #fdf2f2; color: #991b1b; }

.hd-sub {
  background: var(--nav);
  color: #aab4c0;
  font-size: 11.5px;
  padding: 8px 26px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.hd-sub b { color: #e8edf3; font-weight: 600; }
.hd-sub .dot { width: 3px; height: 3px; border-radius: 50%; background: #5b6675; display: inline-block; }
.hd-sub a { color: #f9b233; text-decoration: none; font-weight: 600; }
.hd-sub a:hover { color: #fff; text-decoration: underline; }
.hd-sub .hd-right { margin-left: auto; display: flex; align-items: center; gap: 8px; }

/* Layout Grid */
.wrap {
  padding: 18px 26px 40px;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  flex: 1;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 18px;
  align-items: start;
}
@media (max-width: 1100px) {
  .workspace-grid { grid-template-columns: 1fr; }
}

/* Painel Padrão Oficial PEP HUB */
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  overflow: hidden;
}
.panel > h2 {
  margin: 0;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: var(--ink2);
  border-bottom: 1px solid var(--line2);
  background: #fafbfc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.pbody { padding: 16px; }

/* KPI Metrics */
.kpis { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }
.kpi { background: var(--bg); border: 1px solid var(--line); border-radius: 3px; padding: 6px 10px; }
.kpi .k { font-size: 10.5px; color: var(--ink3); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi .v { font-size: 22px; font-weight: 600; color: var(--ink); letter-spacing: -0.3px; }
.kpi .d { font-size: 10px; color: var(--ink2); }

/* Botão Help Modal */
.hlp {
  width: 19px;
  height: 19px;
  min-width: 19px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink3);
  font: 600 11px "Segoe UI", Arial;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

/* Form Elements */
.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .4px;
  color: var(--ink2);
}
.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  font-size: 13px;
  font-family: inherit;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: #fff;
  color: var(--ink);
  outline: none;
  transition: border-color .15s, box-shadow .15s;
}
.form-group input[type="text"]:focus,
.form-group textarea:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.12);
}

.file-dropzone {
  border: 2px dashed var(--line);
  border-radius: 6px;
  padding: 18px;
  text-align: center;
  background: #fcfcfd;
  cursor: pointer;
  transition: all .15s;
}
.file-dropzone:hover {
  border-color: var(--red);
  background: #fdf5f4;
}
.file-dropzone input { display: none; }
.file-dropzone .drop-title { font-weight: 700; color: var(--ink); margin-bottom: 2px; }
.file-dropzone .drop-sub { font-size: 11px; color: var(--ink3); }

.slider-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.slider-row input[type="range"] {
  flex: 1;
  accent-color: var(--red);
  cursor: ew-resize;
  height: 5px;
}
.slider-val {
  font-size: 11px;
  font-weight: 700;
  color: var(--ink2);
  width: 32px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* Preset Pills */
.pills { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.pill {
  background: #f1f3f5;
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 11px;
  color: var(--ink2);
  cursor: pointer;
  font-weight: 600;
}
.pill:hover { background: #e2e8f0; color: var(--ink); }

/* Ações */
.btn-action {
  width: 100%;
  padding: 12px;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .5px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all .15s;
}
.btn-action.primary {
  background: var(--red);
  color: #fff;
  box-shadow: 0 2px 6px rgba(192, 57, 43, 0.25);
}
.btn-action.primary:hover { background: #a93226; transform: translateY(-1px); }

.btn-action.secondary {
  background: #fff;
  border: 1px solid var(--line);
  color: var(--ink2);
  margin-top: 8px;
  text-decoration: none;
  font-size: 11.5px;
}
.btn-action.secondary:hover { background: #f8fafc; color: var(--ink); border-color: #cbd5e1; }

/* Canvas Stage */
.stage-panel {
  position: relative;
  background: #0f172a;
  border-radius: 6px;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
  overflow: hidden;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
}

.canvas-scale-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 1920x1080 Container Nativo */
#card-container {
  position: relative;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
  transform-origin: center center;
  background-color: #7a0c08;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  user-select: none;
}

/* Foto do Aniversariante encaixada perfeitamente na moldura */
#foto-preview {
  position: absolute;
  top: 210px;
  left: 1266px;
  width: 426px;
  height: 624px;
  border-radius: 6px;
  background-color: #1e293b;
  z-index: 2;
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.4);
}

/* Template 16:9 Full HD transparente sobre a foto */
#template-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 1920px;
  height: 1080px;
  z-index: 5;
  pointer-events: none;
}

/* Elementos de Texto */
.draggable {
  position: absolute;
  cursor: move;
  z-index: 10;
  transition: opacity .15s;
}
.draggable:hover {
  outline: 2px dashed rgba(255, 255, 255, 0.7);
  outline-offset: 4px;
}

#data {
  top: 72px;
  left: 96px;
  font-size: 68px;
  font-weight: 800;
  color: #fff;
  text-shadow: 2px 2px 6px rgba(0,0,0,0.35);
  text-transform: uppercase;
  letter-spacing: 1px;
}

#mens_padrao {
  top: 210px;
  left: 80px;
  width: 980px;
  font-weight: 900;
  font-size: 115px;
  color: #fff;
  line-height: 0.85;
  text-shadow: 3px 4px 10px rgba(0,0,0,0.4);
  text-align: center;
}

#nome {
  top: 390px;
  left: 80px;
  width: 980px;
  font-size: 124px;
  font-family: 'ShineValentine', cursive;
  color: #ffe597;
  text-shadow: -2px 6px 14px rgba(0,0,0,0.5);
  text-align: center;
  white-space: nowrap;
}

#mensagem {
  top: 570px;
  left: 100px;
  width: 940px;
  font-size: 34px;
  color: #ffffff;
  font-style: italic;
  text-shadow: 2px 3px 8px rgba(0,0,0,0.4);
  text-align: center;
  line-height: 1.35;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Controles de Zoom do Palco */
.stage-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  background: #1e293b;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  color: #cbd5e1;
  font-size: 11px;
}
.zoom-controls { display: flex; align-items: center; gap: 8px; }
.zoom-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
}
.zoom-btn:hover { background: rgba(255,255,255,0.2); }
</style>
</head>
<body>

  <!-- Staging Banner -->
  <div class="staging-banner">
    <span>[STAGING] <b>AMBIENTE SECUNDÁRIO DE TESTE</b> — Gerador de Card de Aniversário Oficial 16:9 (PeP Tools)</span>
    <span class="staging-pill">Staging Preview</span>
  </div>

  <!-- Header Oficial Claro PEP HUB -->
  <header>
    <div class="hd-bar">
      <div class="hd-ico">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2"/><polygon points="10 11 15 14 10 17"/><line x1="8" y1="3" x2="16" y2="3"/>
        </svg>
      </div>
      <h1>
        <b>Gerador de Card de Aniversário</b>
        <span>· Regional Norte</span>
      </h1>
      <div class="hd-actions">
        <a href="/pep-tools/divulgacao/" class="hd-btn">‹ Divulgação TV</a>
        <a href="/" class="hd-btn">‹ Portal Pephub</a>
        <button id="btnTopDownload" class="hd-btn primary">Baixar JPG (1080p)</button>
      </div>
    </div>
    <div class="hd-sub">
      <a href="/">‹ Portal Pephub</a>
      <span class="dot"></span>
      <a href="/#pep-tools">‹ PeP Tools</a>
      <span class="dot"></span>
      <span>Proporção Obrigatória: <b>16:9 Widescreen (1920x1080 Full HD)</b></span>
      <span class="dot"></span>
      <span>Destino Oficial: <b>Telas de TV dos Prédios Administrativos & Operacionais</b></span>
      <div class="hd-right">
        <span>100% Autocontido & Seguro</span>
      </div>
    </div>
  </header>

  <!-- Workspace Executivo -->
  <div class="wrap">
    <div class="workspace-grid">

      <!-- Coluna da Esquerda: Controles e Parâmetros -->
      <div class="panel">
        <h2>
          <span>Parâmetros do Aniversariante</span>
          <button class="hlp" data-h="aniv_params" title="Ajuda">?</button>
        </h2>
        <div class="pbody">

          <!-- Métricas de Status do Card (Design System) -->
          <div class="kpis" style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:14px;">
            <div class="kpi" style="background:var(--bg); border:1px solid var(--line); border-radius:3px; padding:6px 10px;">
              <div class="k" style="font-size:10.5px; color:var(--ink3); font-weight:600; text-transform:uppercase;">Resolução</div>
              <div class="v" style="font-size:22px; font-weight:600; color:var(--ink);">1080p</div>
              <div class="d" style="font-size:10px; color:var(--ink2);">Full HD 16:9</div>
            </div>
            <div class="kpi" style="background:var(--bg); border:1px solid var(--line); border-radius:3px; padding:6px 10px;">
              <div class="k" style="font-size:10.5px; color:var(--ink3); font-weight:600; text-transform:uppercase;">Status</div>
              <div class="v" style="font-size:22px; font-weight:600; color:var(--green);">Pronto</div>
              <div class="d" style="font-size:10px; color:var(--ink2);">Exportação Direta</div>
            </div>
          </div>

          <!-- 1. Foto -->
          <div class="form-group">
            <label>1. Foto do Colaborador</label>
            <div class="file-dropzone" onclick="document.getElementById('fotoInput').click()">
              <input type="file" id="fotoInput" accept="image/jpeg, image/png, image/webp">
              <div class="drop-title">Clique para selecionar ou arraste a foto</div>
              <div class="drop-sub">Formatos suportados: JPG, PNG ou WEBP</div>
            </div>

            <div class="slider-row">
              <span style="font-size:11px; color:var(--ink3);">Vertical (Y):</span>
              <input type="range" id="inputFotoY" min="0" max="100" value="50">
              <span class="slider-val" id="valFotoY">50%</span>
            </div>
            <div class="slider-row">
              <span style="font-size:11px; color:var(--ink3);">Horizontal (X):</span>
              <input type="range" id="inputFotoX" min="0" max="100" value="50">
              <span class="slider-val" id="valFotoX">50%</span>
            </div>
          </div>

          <!-- 2. Data -->
          <div class="form-group">
            <label for="inputData">2. Data de Aniversário</label>
            <input type="text" id="inputData" value="16/Out" placeholder="ex: 16/Out">
            <div class="pills">
              <button class="pill" onclick="setPresetDate('Hoje')">Hoje</button>
              <button class="pill" onclick="setPresetDate('Amanhã')">Amanhã</button>
              <button class="pill" onclick="setPresetDate('Esta Semana')">Esta Semana</button>
            </div>
          </div>

          <!-- 3. Nome -->
          <div class="form-group">
            <label for="inputNome">3. Nome do Aniversariante</label>
            <input type="text" id="inputNome" value="Nome Sobrenome" placeholder="ex: Arthur Rezende">
          </div>

          <!-- 4. Mensagem -->
          <div class="form-group">
            <label for="inputMsg">4. Mensagem de Felicitação</label>
            <textarea id="inputMsg" rows="3" placeholder="Mensagem personalizada">"Que a sua vida seja sempre repleta de sorrisos, risadas e muita alegria."</textarea>
            <div class="pills">
              <button class="pill" onclick="setPresetMsg(1)">Frase Clássica</button>
              <button class="pill" onclick="setPresetMsg(2)">Foco em Sucesso</button>
              <button class="pill" onclick="setPresetMsg(3)">Equipe Claro</button>
            </div>
          </div>

          <!-- Ações -->
          <div style="margin-top:20px;">
            <button id="btnDownload" class="btn-action primary">
              Baixar Imagem (JPG 1080p)
            </button>
            <a href="/pep-tools/divulgacao/" class="btn-action secondary">
              Ir para Curadoria de TV & Enviar Card →
            </a>
          </div>

        </div>
      </div>

      <!-- Coluna da Direita: Palco de Pré-visualização 16:9 -->
      <div class="panel">
        <div class="stage-toolbar">
          <span><b>Pré-visualização 16:9 (1920x1080 Full HD)</b> — Clique e arraste qualquer texto para ajustar a posição</span>
          <div class="zoom-controls">
            <span>Ajuste de Tela:</span>
            <button class="zoom-btn" onclick="fitToScreen()">Enquadrar</button>
          </div>
        </div>

        <div class="stage-panel" id="stagePanel">
          <div class="canvas-scale-wrapper" id="canvasWrapper">
            <div id="card-container">
              <!-- Foto posicionada exatamente dentro do recorte transparente -->
              <div id="foto-preview"></div>

              <!-- Template 1080p transparente por cima da foto -->
              <img id="template-overlay" src="template.png" alt="Template Frame 16:9">

              <!-- Textos Interativos -->
              <div id="data" class="draggable">16/Out</div>
              <div id="mens_padrao" class="draggable">Feliz Aniversário,</div>
              <div id="nome" class="draggable">Nome Sobrenome</div>
              <div id="mensagem" class="draggable">"Que a sua vida seja sempre repleta de sorrisos, risadas e muita alegria."</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- Local Script de Renderização Canvas (Zero Dependências Externas) -->
  <script src="html2canvas.min.js"></script>

  <script>
    const HELP = {
      aniv_params: 'Preencha os dados do colaborador, faça o upload da foto e ajuste o enquadramento. A imagem é gerada na proporção 16:9 oficial para as TVs da Claro.'
    };

    document.querySelectorAll('.hlp').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const key = e.currentTarget.getAttribute('data-h');
        if (HELP[key]) alert(HELP[key]);
      });
    });

    const cardContainer = document.getElementById('card-container');
    const stagePanel = document.getElementById('stagePanel');
    const fotoInput = document.getElementById('fotoInput');
    const fotoPreview = document.getElementById('foto-preview');

    const dataText = document.getElementById('data');
    const nomeText = document.getElementById('nome');
    const msgText = document.getElementById('mensagem');

    const inputData = document.getElementById('inputData');
    const inputNome = document.getElementById('inputNome');
    const inputMsg = document.getElementById('inputMsg');

    const inputFotoX = document.getElementById('inputFotoX');
    const inputFotoY = document.getElementById('inputFotoY');
    const valFotoX = document.getElementById('valFotoX');
    const valFotoY = document.getElementById('valFotoY');

    const btnDownload = document.getElementById('btnDownload');
    const btnTopDownload = document.getElementById('btnTopDownload');

    // Auto-fit 1920x1080 to container
    function fitToScreen() {
      if (!stagePanel || !cardContainer) return;
      const w = stagePanel.clientWidth - 48;
      const h = stagePanel.clientHeight - 48;
      const scaleW = w / 1920;
      const scaleH = h / 1080;
      const scale = Math.min(scaleW, scaleH, 0.98);
      cardContainer.style.transform = `scale(${scale})`;
    }

    window.addEventListener('resize', fitToScreen);
    setTimeout(fitToScreen, 150);

    // Live text updates
    inputData.addEventListener('input', e => { dataText.textContent = e.target.value; });
    inputNome.addEventListener('input', e => { nomeText.textContent = e.target.value; });
    inputMsg.addEventListener('input', e => { msgText.textContent = e.target.value; });

    // Presets
    function setPresetDate(type) {
      const now = new Date();
      const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
      if (type === 'Hoje') {
        inputData.value = `${now.getDate()}/${meses[now.getMonth()]}`;
      } else if (type === 'Amanhã') {
        const tomorrow = new Date(now.getTime() + 86400000);
        inputData.value = `${tomorrow.getDate()}/${meses[tomorrow.getMonth()]}`;
      } else {
        inputData.value = 'Esta Semana';
      }
      dataText.textContent = inputData.value;
    }

    function setPresetMsg(idx) {
      if (idx === 1) {
        inputMsg.value = '"Que a sua vida seja sempre repleta de sorrisos, risadas e muita alegria."';
      } else if (idx === 2) {
        inputMsg.value = '"Desejamos muito sucesso, saúde e realizações nesta nova fase da sua trajetória!"';
      } else {
        inputMsg.value = '"Parabéns pelo seu dia! É um privilégio ter você no time da Regional Norte!"';
      }
      msgText.textContent = inputMsg.value;
    }

    // Photo Upload
    fotoInput.addEventListener('change', e => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = evt => {
          fotoPreview.style.backgroundImage = `url('${evt.target.result}')`;
        };
        reader.readAsDataURL(file);
      }
    });

    // Photo Alignment (X & Y)
    function updatePhotoPos() {
      const x = inputFotoX.value;
      const y = inputFotoY.value;
      valFotoX.textContent = `${x}%`;
      valFotoY.textContent = `${y}%`;
      fotoPreview.style.backgroundPosition = `${x}% ${y}%`;
    }
    inputFotoX.addEventListener('input', updatePhotoPos);
    inputFotoY.addEventListener('input', updatePhotoPos);

    // Drag & Drop on Canvas
    document.querySelectorAll('.draggable').forEach(elem => {
      let isDragging = false;
      let startX, startY, origX, origY;

      elem.addEventListener('mousedown', e => {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        const rect = elem.getBoundingClientRect();
        const parentRect = cardContainer.getBoundingClientRect();
        const scaleMatch = cardContainer.style.transform.match(/scale\(([^)]+)\)/);
        const scale = scaleMatch ? parseFloat(scaleMatch[1]) : 1;

        origX = (rect.left - parentRect.left) / scale;
        origY = (rect.top - parentRect.top) / scale;
        e.preventDefault();
      });

      window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        const scaleMatch = cardContainer.style.transform.match(/scale\(([^)]+)\)/);
        const scale = scaleMatch ? parseFloat(scaleMatch[1]) : 1;

        const deltaX = (e.clientX - startX) / scale;
        const deltaY = (e.clientY - startY) / scale;

        elem.style.left = `${origX + deltaX}px`;
        elem.style.top = `${origY + deltaY}px`;
        elem.style.right = 'auto';
        elem.style.bottom = 'auto';
      });

      window.addEventListener('mouseup', () => {
        isDragging = false;
      });
    });

    // Render & Download JPG 1080p
    function downloadCard() {
      const oldTransform = cardContainer.style.transform;
      cardContainer.style.transform = 'none';

      btnDownload.textContent = 'Gerando Card 1080p...';

      html2canvas(cardContainer, {
        scale: 1,
        width: 1920,
        height: 1080,
        useCORS: true,
        allowTaint: true
      }).then(canvas => {
        cardContainer.style.transform = oldTransform;
        btnDownload.textContent = 'Baixar Imagem (JPG 1080p)';

        const link = document.createElement('a');
        const nomeClean = (inputNome.value || 'colaborador').trim().replace(/[^a-zA-Z0-9]/g, '_');
        link.download = `Aniversario_TV_${nomeClean}.jpg`;
        link.href = canvas.toDataURL('image/jpeg', 0.95);
        link.click();
      }).catch(err => {
        cardContainer.style.transform = oldTransform;
        btnDownload.textContent = 'Baixar Imagem (JPG 1080p)';
        alert('Erro ao exportar card: ' + err);
      });
    }

    btnDownload.addEventListener('click', downloadCard);
    btnTopDownload.addEventListener('click', downloadCard);
  </script>
</body>
</html>
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {target_file} reconstruído com sucesso de acordo com PADRAO_DESIGN_PAINEIS.md!")

if __name__ == "__main__":
    rebuild_aniversario()
