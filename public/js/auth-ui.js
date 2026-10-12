/**
 * PEP HUB — Auth UI v2
 * 1) Fundo animado (rede de nós "dados conectados"), leve e pausado em aba oculta
 * 2) Utilitários compartilhados: alertas, toggle de senha, medidor de força, estado de carregamento
 * Zero dependências externas.
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* 1. ANIMAÇÃO DE TELEMETRIA E FLUXO DE SAFRAS (TEMA CLARO CORPORATIVO) */
  /* ------------------------------------------------------------------ */
  var canvas = document.getElementById('authBg');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (canvas && !reduce && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, raf = 0, running = true;
    var mouse = { x: -9999, y: -9999 };
    var time = 0;
    var parent = canvas.parentElement || document.body;

    // Definição das camadas de ondas alinhadas rigorosamente à paleta Claro
    var waves = [
      {
        baseY: 0.72,
        amp: 32,
        freq: 0.0042,
        speed: 0.012,
        stroke: 'rgba(192, 25, 31, 0.55)',      // Vermelho Claro
        fillTop: 'rgba(192, 25, 31, 0.08)',
        fillBottom: 'rgba(192, 25, 31, 0.005)',
        lineWidth: 1.5
      },
      {
        baseY: 0.62,
        amp: 38,
        freq: 0.0035,
        speed: -0.009,
        stroke: 'rgba(226, 58, 30, 0.45)',     // Coral institucional
        fillTop: 'rgba(226, 58, 30, 0.06)',
        fillBottom: 'rgba(226, 58, 30, 0.002)',
        lineWidth: 1.2
      },
      {
        baseY: 0.80,
        amp: 26,
        freq: 0.0055,
        speed: 0.015,
        stroke: 'rgba(249, 178, 51, 0.60)',     // Âmbar institucional
        fillTop: 'rgba(249, 178, 51, 0.07)',
        fillBottom: 'rgba(249, 178, 51, 0.002)',
        lineWidth: 1.4
      },
      {
        baseY: 0.52,
        amp: 24,
        freq: 0.0030,
        speed: 0.007,
        stroke: 'rgba(42, 93, 143, 0.35)',      // Azul corporativo analítico
        fillTop: 'rgba(42, 93, 143, 0.04)',
        fillBottom: 'rgba(42, 93, 143, 0.00)',
        lineWidth: 1.0
      }
    ];

    // Pulsos de telemetria / pacotes de dados que viajam pelas ondas (movimento calmo e fluido)
    var pulses = [
      { waveIdx: 0, progress: 0.15, speed: 0.0004, color: '#c0191f', size: 3.0 },
      { waveIdx: 0, progress: 0.68, speed: 0.0005, color: '#c0191f', size: 2.6 },
      { waveIdx: 1, progress: 0.35, speed: 0.00035, color: '#e23a1e', size: 2.8 },
      { waveIdx: 1, progress: 0.85, speed: 0.0004, color: '#e23a1e', size: 2.4 },
      { waveIdx: 2, progress: 0.22, speed: 0.00055, color: '#f9b233', size: 3.2 },
      { waveIdx: 2, progress: 0.54, speed: 0.00045, color: '#f9b233', size: 2.4 },
      { waveIdx: 3, progress: 0.42, speed: 0.0003, color: '#2a5d8f', size: 2.6 }
    ];

    function resize() {
      W = parent.clientWidth || window.innerWidth;
      H = parent.clientHeight || window.innerHeight;
      if (W === 0 || H === 0) return;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function calcY(wave, x, t) {
      var y0 = H * wave.baseY;
      // Multiplicadores reduzidos para oscilação lenta, orgânica e fluida
      var y = y0 +
        Math.sin(x * wave.freq + t * wave.speed * 4) * wave.amp +
        Math.sin(x * (wave.freq * 1.8) - t * wave.speed * 2.5) * (wave.amp * 0.35);

      // Perturbação tátil e suave ao cursor
      var mdx = x - mouse.x;
      if (Math.abs(mdx) < 160 && mouse.y > 0) {
        var distFactor = 1 - Math.abs(mdx) / 160;
        var mdy = mouse.y - y;
        y += mdy * distFactor * 0.18;
      }
      return y;
    }

    function frame() {
      if (!running) return;
      time += 1;
      ctx.clearRect(0, 0, W, H);

      // 1. Renderiza cada camada de onda fluida
      for (var w = 0; w < waves.length; w++) {
        var wave = waves[w];
        ctx.beginPath();
        ctx.moveTo(0, H);

        for (var x = 0; x <= W; x += 6) {
          var y = calcY(wave, x, time);
          if (x === 0) ctx.lineTo(0, y);
          else ctx.lineTo(x, y);
        }

        ctx.lineTo(W, H);
        ctx.closePath();

        // Gradiente vertical do preenchimento
        var grad = ctx.createLinearGradient(0, H * (wave.baseY - 0.2), 0, H);
        grad.addColorStop(0, wave.fillTop);
        grad.addColorStop(1, wave.fillBottom);
        ctx.fillStyle = grad;
        ctx.fill();

        // Linha de crista elegante
        ctx.beginPath();
        for (var lx = 0; lx <= W; lx += 6) {
          var ly = calcY(wave, lx, time);
          if (lx === 0) ctx.moveTo(0, ly);
          else ctx.lineTo(lx, ly);
        }
        ctx.strokeStyle = wave.stroke;
        ctx.lineWidth = wave.lineWidth;
        ctx.stroke();
      }

      // 2. Renderiza os pulsos de telemetria / pacotes de dados
      for (var p = 0; p < pulses.length; p++) {
        var pulse = pulses[p];
        pulse.progress += pulse.speed;
        if (pulse.progress > 1) pulse.progress = 0;

        var px = pulse.progress * W;
        var pWave = waves[pulse.waveIdx];
        var py = calcY(pWave, px, time);

        // Halo suave
        ctx.beginPath();
        ctx.fillStyle = pulse.color;
        ctx.globalAlpha = 0.18;
        ctx.arc(px, py, pulse.size * 2.8, 0, Math.PI * 2);
        ctx.fill();

        // Ponto central
        ctx.beginPath();
        ctx.globalAlpha = 0.85;
        ctx.arc(px, py, pulse.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
      }

      raf = requestAnimationFrame(frame);
    }

    window.addEventListener('resize', resize);
    parent.addEventListener('mousemove', function (e) {
      var rect = parent.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });
    parent.addEventListener('mouseleave', function () {
      mouse.x = -9999;
      mouse.y = -9999;
    });
    document.addEventListener('visibilitychange', function () {
      running = document.visibilityState === 'visible';
      if (running) { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
    });

    resize();
    raf = requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------------ */
  /* 2. UTILITÁRIOS COMPARTILHADOS                                       */
  /* ------------------------------------------------------------------ */
  var ICONS = {
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
  };

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function showAlert(text, type) {
    type = type || 'error';
    var box = document.getElementById('alertBox');
    if (!box) return;
    box.className = 'alert ' + type;
    box.innerHTML = (ICONS[type] || ICONS.error) + '<div>' + escapeHtml(text) + '</div>';
    if (type === 'error') {
      void box.offsetWidth;
      box.classList.add('shake');
    }
  }

  function setBusy(busy, label) {
    var btn = document.getElementById('btnSubmit');
    var sp = document.getElementById('btnSpinner');
    var txt = document.getElementById('btnText');
    var arrow = btn ? btn.querySelector('.arrow') : null;
    if (!btn) return;
    btn.disabled = busy;
    if (sp) sp.style.display = busy ? 'inline-block' : 'none';
    if (arrow) arrow.style.display = busy ? 'none' : '';
    if (txt && label) txt.textContent = label;
  }

  function bindPasswordToggle(btnId, inputId) {
    var btn = document.getElementById(btnId);
    var input = document.getElementById(inputId);
    if (!btn || !input) return;
    var open = btn.querySelector('.eye-open');
    var closed = btn.querySelector('.eye-closed');
    btn.addEventListener('click', function () {
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      if (open) open.style.display = show ? 'none' : 'block';
      if (closed) closed.style.display = show ? 'block' : 'none';
    });
  }

  function bindCapsLock(inputId, warnId) {
    var input = document.getElementById(inputId);
    var warn = document.getElementById(warnId);
    if (!input || !warn) return;
    function check(e) {
      warn.style.display = (e.getModifierState && e.getModifierState('CapsLock')) ? 'flex' : 'none';
    }
    input.addEventListener('keydown', check);
    input.addEventListener('keyup', check);
    input.addEventListener('blur', function () { warn.style.display = 'none'; });
  }

  function bindStrength(inputId, meterId) {
    var input = document.getElementById(inputId);
    var meter = document.getElementById(meterId);
    if (!input || !meter) return;
    var label = meter.querySelector('.strength-label');
    var names = ['', 'Fraca', 'Razoável', 'Boa', 'Forte'];
    input.addEventListener('input', function () {
      var v = input.value;
      if (!v) { meter.classList.remove('on'); return; }
      var score = 0;
      if (v.length >= 6) score++;
      if (v.length >= 10) score++;
      if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
      if (/\d/.test(v) && /[^A-Za-z0-9]/.test(v)) score++;
      score = Math.max(1, Math.min(4, score));
      meter.classList.add('on');
      meter.setAttribute('data-level', String(score));
      if (label) label.textContent = 'Força da senha: ' + names[score];
    });
  }

  window.PepAuth = {
    escapeHtml: escapeHtml,
    showAlert: showAlert,
    setBusy: setBusy,
    bindPasswordToggle: bindPasswordToggle,
    bindCapsLock: bindCapsLock,
    bindStrength: bindStrength
  };
})();
