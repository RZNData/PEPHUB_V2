/**
 * Header Widget & Online Users Component — Pephub Plataforma Regional
 * Padronização de cabeçalhos, presença em tempo real (heartbeat) e widget "Online" para administradores.
 *
 * API pública:
 *   window.initPephubHeader(containerId)   -> cabeçalho dos relatórios (Sair / Admin / Online)
 *   window.pephubMountOnlineWidget(host)   -> monta o botão "Online" (hover + modal) em qualquer elemento
 *   window.pephubOpenActiveUsersModal()    -> abre o modal completo
 * Qualquer elemento com o atributo [data-pephub-online] recebe o widget automaticamente (somente admin).
 */

(function() {
  if (window.__pephubHeaderWidgetLoaded) return;
  window.__pephubHeaderWidgetLoaded = true;

  // ------------------------------------------------------------------
  // Estilos (identidade institucional: gradiente Claro, tinta #1c2430, Segoe UI, sem emojis)
  // ------------------------------------------------------------------
  const style = document.createElement('style');
  style.id = 'pephub-header-styles';
  style.textContent = `
    .hd-actions {
      margin-left: auto;
      display: flex !important;
      align-items: center !important;
      gap: 8px !important;
      flex-wrap: wrap !important;
    }
    .hd-btn, a.hd-btn, button.hd-btn, .btn-nav-catalog, a.btn-nav-catalog {
      display: inline-flex !important;
      align-items: center !important;
      gap: 6px !important;
      background: rgba(255, 255, 255, 0.22) !important;
      color: #ffffff !important;
      border: 1px solid rgba(255, 255, 255, 0.5) !important;
      padding: 6px 14px !important;
      border-radius: 4px !important;
      font-size: 11.5px !important;
      font-weight: 700 !important;
      text-decoration: none !important;
      transition: all 0.15s ease !important;
      cursor: pointer !important;
      white-space: nowrap !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18) !important;
      font-family: inherit !important;
      line-height: normal !important;
    }
    .hd-btn:hover, a.hd-btn:hover, button.hd-btn:hover, .btn-nav-catalog:hover, a.btn-nav-catalog:hover {
      background: rgba(255, 255, 255, 0.38) !important;
      color: #ffffff !important;
      border-color: #ffffff !important;
      text-decoration: none !important;
    }

    /* Botão informativo de usuários ativos (ícone + contagem) */
    .hd-btn.btn-active-users {
      padding: 5px 9px !important;
      gap: 6px !important;
      background: rgba(255, 255, 255, 0.22) !important;
      border-color: rgba(255, 255, 255, 0.55) !important;
    }
    .hd-btn.btn-active-users .ou-count {
      background: #ffffff;
      color: #8a0f18;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      font-size: 11px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
    }
    .ou-dot {
      position: relative;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #3ddc84;
      box-shadow: 0 0 0 1.5px rgba(255,255,255,.85);
      flex: none;
      display: inline-block;
    }
    .ou-dot::after {
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      border: 2px solid rgba(61, 220, 132, .65);
      animation: ouPulse 1.9s ease-out infinite;
    }
    .ou-dot.idle { background: #9aa5b1; box-shadow: none; }
    .ou-dot.idle::after { display: none; }
    @keyframes ouPulse {
      0%   { transform: scale(.55); opacity: 1; }
      100% { transform: scale(1.5); opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) { .ou-dot::after { animation: none; } }

    /* Wrapper + Hover Card (a "ponte" de 8px evita fechar ao mover o mouse até o card) */
    .active-users-wrapper { position: relative; display: inline-flex; }
    .active-users-hover-card {
      display: none;
      position: absolute;
      top: 100%;
      right: 0;
      width: 392px;
      padding-top: 8px;
      z-index: 99999;
      font-family: "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
      cursor: default;
    }
    .active-users-hover-card.show { display: block; animation: ouFade .14s ease-out; }
    @keyframes ouFade { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
    .ou-card {
      background: #ffffff;
      border: 1px solid #dfe3e8;
      border-radius: 4px;
      box-shadow: 0 14px 34px rgba(28, 36, 48, .28);
      overflow: hidden;
    }
    .ou-card::before, .ou-modal-box::before {
      content: '';
      display: block;
      height: 4px;
      background: linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);
    }
    .ou-hd {
      background: #1c2430;
      color: #ffffff;
      padding: 11px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .ou-hd-title { font-size: 12.5px; font-weight: 700; display: flex; align-items: center; gap: 8px; letter-spacing: .1px; }
    .ou-hd-title small { font-weight: 600; color: #aab4c0; font-size: 11px; }
    .ou-badge-live {
      font-size: 9.5px; font-weight: 800; letter-spacing: .6px; text-transform: uppercase;
      color: #f9b233; border: 1px solid rgba(249,178,51,.55); padding: 2px 7px; border-radius: 3px;
    }
    .ou-body { padding: 8px; max-height: 330px; overflow-y: auto; background: #f4f6f8; }
    .ou-empty { text-align: center; padding: 22px 12px; color: #5b6675; font-size: 12px; }
    .ou-row {
      display: flex; align-items: center; gap: 10px;
      padding: 8px 10px; background: #ffffff;
      border: 1px solid #e6e9ed; border-left: 3px solid #2f7d5d;
      border-radius: 3px; margin-bottom: 6px;
      transition: border-color .12s ease, box-shadow .12s ease;
    }
    .ou-row:last-child { margin-bottom: 0; }
    .ou-row:hover { border-color: #c4ccd5; border-left-color: #2f7d5d; box-shadow: 0 2px 6px rgba(28,36,48,.08); }
    .ou-row.idle { border-left-color: #b9c2cc; }
    .ou-avatar {
      width: 32px; height: 32px; min-width: 32px; border-radius: 50%;
      background: linear-gradient(135deg,#c0191f,#f47a1f);
      color: #fff; display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 11px; letter-spacing: .3px;
    }
    .ou-info { flex: 1; min-width: 0; }
    .ou-name {
      font-size: 12.5px; font-weight: 700; color: #1c2430;
      display: flex; align-items: center; gap: 6px; min-width: 0;
    }
    .ou-name > span:first-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ou-sub { font-size: 10.5px; color: #5b6675; margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .ou-tag-admin {
      font-size: 9px; font-weight: 800; letter-spacing: .4px; text-transform: uppercase;
      background: #fdf3e2; color: #8a5d06; border: 1px solid #f0dcb4; padding: 1px 5px; border-radius: 2px; flex: none;
    }
    .ou-time { text-align: right; flex: none; }
    .ou-pill {
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 10.5px; font-weight: 700; white-space: nowrap;
      color: #1e5837; background: #eaf2ec; border: 1px solid #c3e2cb;
      padding: 2px 8px; border-radius: 10px;
    }
    .ou-pill.idle { color: #5b6675; background: #eef0f3; border-color: #d6dbe1; }
    .ou-pill .ou-dot { width: 6px; height: 6px; box-shadow: none; }
    .ou-pill .ou-dot::after { inset: -3px; border-width: 1.5px; }
    .ou-since { font-size: 10px; color: #7b8794; margin-top: 3px; white-space: nowrap; }
    .ou-ft {
      padding: 8px 14px; background: #ffffff; border-top: 1px solid #e6e9ed;
      display: flex; justify-content: space-between; align-items: center; gap: 10px;
    }
    .ou-ft span { font-size: 10.5px; color: #7b8794; }
    .ou-link {
      font-size: 11.5px; color: #c0191f; font-weight: 700; background: none; border: none;
      cursor: pointer; padding: 0; font-family: inherit;
    }
    .ou-link:hover { text-decoration: underline; color: #8a0f18; }

    /* Modal executivo completo */
    #pephubActiveUsersModal {
      display: none; position: fixed; inset: 0;
      background: rgba(28, 36, 48, 0.62); backdrop-filter: blur(3px);
      z-index: 99999; align-items: center; justify-content: center;
      font-family: "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #pephubActiveUsersModal.on { display: flex; animation: ouFade .16s ease-out; }
    .ou-modal-box {
      background: #ffffff; border-radius: 4px; width: 92%; max-width: 720px; max-height: 86vh;
      display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 24px 50px rgba(0,0,0,.35); border: 1px solid #dfe3e8;
    }
    .ou-modal-hd {
      background: #1c2430; color: #fff; padding: 15px 20px;
      display: flex; align-items: center; justify-content: space-between;
    }
    .ou-modal-hd h3 { margin: 0; font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    .ou-modal-hd small { display: block; font-size: 11px; font-weight: 500; color: #aab4c0; margin-top: 1px; }
    .ou-modal-x { background: none; border: none; color: #aab4c0; font-size: 22px; cursor: pointer; line-height: 1; padding: 0 2px; }
    .ou-modal-x:hover { color: #fff; }
    .ou-kpis { display: flex; gap: 10px; padding: 12px 20px; background: #fff; border-bottom: 1px solid #e6e9ed; flex-wrap: wrap; }
    .ou-kpi { flex: 1; min-width: 120px; border: 1px solid #e6e9ed; border-radius: 3px; padding: 8px 12px; background: #f7f8fa; }
    .ou-kpi b { display: block; font-size: 22px; line-height: 1.1; color: #1c2430; }
    .ou-kpi span { font-size: 10px; text-transform: uppercase; letter-spacing: .5px; color: #5b6675; font-weight: 600; }
    .ou-modal-bd { padding: 14px 20px; overflow-y: auto; flex: 1; background: #f4f6f8; }
    .ou-modal-ft {
      padding: 10px 20px; background: #fff; border-top: 1px solid #e6e9ed;
      display: flex; justify-content: space-between; align-items: center; gap: 10px;
    }
    .ou-modal-ft span { font-size: 11px; color: #7b8794; }
    .ou-btn {
      border: 1px solid #cfd6de; background: #fff; color: #1c2430; padding: 6px 14px; border-radius: 3px;
      font: 700 11.5px "Segoe UI", Roboto, sans-serif; cursor: pointer; transition: all .15s;
    }
    .ou-btn:hover { background: #f0f2f5; }
    .ou-btn.primary { background: #1c2430; border-color: #1c2430; color: #fff; }
    .ou-btn.primary:hover { background: #2b3647; }
    .ou-res { font-size: 10px; color: #7b8794; margin-top: 3px; }

    /* ================================================================
       SINO & FLYOUT CORPORATIVO DE NOTIFICAÇÕES (UNIVERSAL)
       ================================================================ */
    .notif-wrapper { position: relative; display: inline-flex; }
    .hd-btn.btn-notifications {
      position: relative !important;
      padding: 6px 10px !important;
      background: rgba(255, 255, 255, 0.22) !important;
      border-color: rgba(255, 255, 255, 0.55) !important;
      gap: 5px !important;
    }
    .hd-btn.btn-notifications:hover {
      background: rgba(255, 255, 255, 0.38) !important;
    }
    .notif-bell-icon {
      width: 15px; height: 15px; display: inline-block; flex: none;
    }
    .notif-badge {
      background: #c0191f;
      color: #ffffff;
      min-width: 17px;
      height: 17px;
      padding: 0 4px;
      border-radius: 9px;
      font-size: 10px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
      box-shadow: 0 0 0 1.5px rgba(255,255,255,.9);
      line-height: 1;
    }
    .notif-badge.pulse {
      animation: notifPulse 2s infinite ease-in-out;
    }
    @keyframes notifPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.15); box-shadow: 0 0 0 3px rgba(192, 25, 31, .35); }
    }
    .notif-badge.empty { display: none !important; }

    /* Popover / Drawer Flutuante */
    .notif-popover {
      display: none;
      position: absolute;
      top: 100%;
      right: 0;
      width: 410px;
      max-width: 92vw;
      margin-top: 8px;
      z-index: 99999;
      font-family: "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
      cursor: default;
    }
    .notif-popover.show { display: block; animation: ouFade .16s ease-out; }
    .notif-card-box {
      background: #ffffff;
      border: 1px solid #dfe3e8;
      border-radius: 4px;
      box-shadow: 0 16px 42px rgba(28, 36, 48, .28);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .notif-card-box::before {
      content: '';
      display: block;
      height: 4px;
      background: linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);
    }
    .notif-hd {
      background: #1c2430;
      color: #ffffff;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .notif-hd-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .notif-hd-title {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: .1px;
      margin: 0;
    }
    .notif-hd-sub {
      font-size: 11px;
      color: #aab4c0;
      font-weight: 500;
    }
    .notif-btn-all-read {
      background: rgba(255,255,255,.16);
      border: 1px solid rgba(255,255,255,.3);
      color: #ffffff;
      font-size: 10.5px;
      font-weight: 600;
      padding: 4px 9px;
      border-radius: 3px;
      cursor: pointer;
      transition: background .15s;
    }
    .notif-btn-all-read:hover {
      background: rgba(255,255,255,.28);
    }
    .notif-tabs-bar {
      display: flex;
      background: #f4f6f8;
      border-bottom: 1px solid #e6e9ed;
      padding: 0 12px;
      gap: 4px;
    }
    .notif-tab {
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      padding: 8px 10px;
      font-size: 11.5px;
      font-weight: 600;
      color: #5b6675;
      cursor: pointer;
      transition: all .15s;
    }
    .notif-tab:hover { color: #1c2430; }
    .notif-tab.active {
      color: #c0191f;
      border-bottom-color: #c0191f;
      background: #ffffff;
    }
    .notif-body {
      max-height: 360px;
      overflow-y: auto;
      padding: 10px 12px;
      background: #f7f9fb;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .notif-item {
      background: #ffffff;
      border: 1px solid #e5e8ec;
      border-left: 3px solid #2a5d8f;
      border-radius: 3px;
      padding: 10px 12px;
      transition: transform .15s, box-shadow .15s;
      position: relative;
    }
    .notif-item:hover {
      box-shadow: 0 3px 10px rgba(0,0,0,.04);
      border-color: #cbd5e1;
    }
    .notif-item.unread {
      background: #ffffff;
      border-left-width: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,.03);
    }
    .notif-item.type-info { border-left-color: #2a5d8f; }
    .notif-item.type-warning { border-left-color: #c98a15; }
    .notif-item.type-update { border-left-color: #6b4b8a; }
    .notif-item.type-security { border-left-color: #c0191f; }
    .notif-item.type-success { border-left-color: #2f7d5d; }

    .notif-item-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 5px;
    }
    .notif-tag {
      font-size: 9.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .4px;
      padding: 2px 6px;
      border-radius: 3px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .notif-tag.type-info { background: #edf4fa; color: #2a5d8f; }
    .notif-tag.type-warning { background: #fef9ee; color: #a16207; }
    .notif-tag.type-update { background: #f6f0fa; color: #6b4b8a; }
    .notif-tag.type-security { background: #fdf2f2; color: #991b1b; }
    .notif-tag.type-success { background: #eaf5f0; color: #2f7d5d; }

    .notif-item-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .notif-btn-dismiss {
      background: none;
      border: none;
      color: #9aa5b1;
      font-size: 16px;
      line-height: 1;
      cursor: pointer;
      padding: 0 2px;
      border-radius: 2px;
    }
    .notif-btn-dismiss:hover { color: #c0191f; background: #fdece9; }

    .notif-item-title {
      font-size: 12.5px;
      font-weight: 700;
      color: #1c2430;
      margin: 0 0 4px;
      line-height: 1.35;
    }
    .notif-item-msg {
      font-size: 11.5px;
      color: #5b6675;
      line-height: 1.5;
      margin: 0 0 8px;
    }
    .notif-item-ft {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding-top: 6px;
      border-top: 1px dashed #eceef1;
    }
    .notif-time {
      font-size: 10px;
      color: #8b95a3;
      font-weight: 500;
    }
    .notif-cta {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 700;
      color: #2a5d8f;
      text-decoration: none;
      background: #f0f6fc;
      border: 1px solid #d0e2f5;
      padding: 3px 8px;
      border-radius: 3px;
      transition: all .15s;
    }
    .notif-cta:hover {
      background: #2a5d8f;
      color: #ffffff;
      border-color: #2a5d8f;
    }
    .notif-empty {
      padding: 32px 16px;
      text-align: center;
      color: #5b6675;
      font-size: 12px;
    }
    .notif-empty-ico {
      width: 32px;
      height: 32px;
      margin: 0 auto 8px;
      color: #94a3b8;
    }
  `;
  if (!document.getElementById('pephub-header-styles')) {
    document.head.appendChild(style);
  }

  // ------------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------------
  function parseUtcDate(dateStr) {
    if (!dateStr) return null;
    if (dateStr instanceof Date) return dateStr;
    const s = String(dateStr).trim();
    if (s.endsWith('Z') || s.includes('+')) return new Date(s);
    return new Date(s.replace(' ', 'T') + 'Z');
  }

  function formatTimeBr(dateStr) {
    const d = parseUtcDate(dateStr);
    if (!d || isNaN(d.getTime())) return '—';
    return d.toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit' });
  }

  function formatDuration(totalSec) {
    const sec = Math.max(0, Math.floor(totalSec || 0));
    if (sec < 60) return 'menos de 1 min';
    const min = Math.floor(sec / 60);
    if (min < 60) return min + ' min';
    const h = Math.floor(min / 60);
    const m = min % 60;
    return m ? `${h}h ${String(m).padStart(2, '0')}min` : `${h}h`;
  }

  function getInitials(name) {
    if (!name) return 'CL';
    const p = name.trim().split(/\s+/);
    if (p.length === 1) return p[0].substring(0, 2).toUpperCase();
    return (p[0][0] + p[p.length - 1][0]).toUpperCase();
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function humanizeResource(r) {
    if (!r) return '';
    const map = { PORTAL_HOME: 'Catálogo de relatórios' };
    if (map[r]) return map[r];
    return String(r).replace(/[_:]+/g, ' ').toLowerCase().replace(/^./, c => c.toUpperCase());
  }

  // /api/auth/me memoizado (evita chamadas repetidas entre widgets)
  let _mePromise = null;
  function getMe() {
    if (!_mePromise) {
      _mePromise = fetch('/api/auth/me')
        .then(r => (r.ok ? r.json() : null))
        .catch(() => null);
    }
    return _mePromise;
  }

  // ------------------------------------------------------------------
  // Presença em tempo real (heartbeat) — roda em TODAS as páginas autenticadas,
  // inclusive no catálogo. Usuário só é "online" se enviar sinal nos últimos 3 min.
  // ------------------------------------------------------------------
  const HEARTBEAT_MS = 60000;
  let _hbTimer = null;
  async function sendHeartbeat() {
    try {
      const res = await fetch('/api/auth/heartbeat', { method: 'POST', keepalive: true });
      if (res.status === 401 && _hbTimer) {
        clearInterval(_hbTimer);
        _hbTimer = null;
      }
    } catch (_) {}
  }
  function startHeartbeat() {
    if (_hbTimer || /^\/login\b/.test(location.pathname)) return;
    sendHeartbeat();
    _hbTimer = setInterval(sendHeartbeat, HEARTBEAT_MS);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') sendHeartbeat();
    });
  }

  // ------------------------------------------------------------------
  // Estado e renderização da lista de online
  // ------------------------------------------------------------------
  let _users = [];
  let _fetchedAt = 0;
  let _refreshTimer = null;

  function liveSeconds(u) {
    return (u.online_seconds || 0) + (Date.now() - _fetchedAt) / 1000;
  }

  function rowHtml(u, detailed) {
    const idleSec = (u.idle_seconds || 0) + (Date.now() - _fetchedAt) / 1000;
    const idle = idleSec > 90;
    const since = u.online_since ? formatTimeBr(u.online_since) : '';
    return `
      <div class="ou-row${idle ? ' idle' : ''}">
        <div class="ou-avatar">${escapeHtml(getInitials(u.nome_completo))}</div>
        <div class="ou-info">
          <div class="ou-name">
            <span>${escapeHtml(u.nome_completo || 'Colaborador')}</span>
            ${u.is_admin ? '<span class="ou-tag-admin">Admin</span>' : ''}
          </div>
          <div class="ou-sub">${escapeHtml(u.email_claro || '')} · ${escapeHtml(u.area || 'Regional')}</div>
          ${detailed && u.last_resource ? `<div class="ou-res">Último recurso: ${escapeHtml(humanizeResource(u.last_resource))}</div>` : ''}
        </div>
        <div class="ou-time">
          <span class="ou-pill${idle ? ' idle' : ''}"><span class="ou-dot${idle ? ' idle' : ''}"></span>Online há ${formatDuration(liveSeconds(u))}</span>
          ${since ? `<div class="ou-since">desde ${since}</div>` : ''}
        </div>
      </div>`;
  }

  function renderLists() {
    const total = _users.length;
    document.querySelectorAll('.ou-count-live').forEach(el => { el.textContent = total; });

    const hoverBody = document.getElementById('hoverCardBody');
    if (hoverBody) {
      hoverBody.innerHTML = total === 0
        ? '<div class="ou-empty">Nenhum colaborador online no momento.</div>'
        : _users.map(u => rowHtml(u, false)).join('');
    }

    const listBody = document.getElementById('activeUsersListBody');
    if (listBody) {
      listBody.innerHTML = total === 0
        ? '<div class="ou-empty">Nenhuma sessão ativa detectada no momento.</div>'
        : _users.map(u => rowHtml(u, true)).join('');
    }

    const kTotal = document.getElementById('ouKpiTotal');
    if (kTotal) {
      kTotal.textContent = total;
      document.getElementById('ouKpiAdmins').textContent = _users.filter(u => u.is_admin).length;
      document.getElementById('ouKpiColab').textContent = _users.filter(u => !u.is_admin).length;
    }
    const meta = document.getElementById('activeModalMeta');
    if (meta) meta.textContent = 'Horário de Brasília · atualizado às ' + formatTimeBr(new Date().toISOString());
  }

  async function fetchActiveUsersList() {
    try {
      const res = await fetch('/api/admin/active-users');
      if (!res.ok) throw new Error('http ' + res.status);
      const data = await res.json();
      _users = data.users || [];
      _fetchedAt = Date.now();
      renderLists();
    } catch (_) {
      const msg = '<div class="ou-empty" style="color:#c0191f">Não foi possível carregar os usuários online.</div>';
      const hb = document.getElementById('hoverCardBody');
      const lb = document.getElementById('activeUsersListBody');
      if (hb) hb.innerHTML = msg;
      if (lb) lb.innerHTML = msg;
    }
  }

  // Atualiza contagem em segundo plano (60s) e, com painel aberto, a cada 15s
  function ensureRefreshLoop() {
    if (_refreshTimer) return;
    _refreshTimer = setInterval(() => {
      const open = document.getElementById('pephubActiveUsersHoverCard')?.classList.contains('show')
        || document.getElementById('pephubActiveUsersModal')?.classList.contains('on');
      if (open || (Date.now() - _fetchedAt) > 60000) fetchActiveUsersList();
      else renderLists();
    }, 15000);
  }

  // ------------------------------------------------------------------
  // Modal completo
  // ------------------------------------------------------------------
  function ensureActiveUsersModal() {
    if (document.getElementById('pephubActiveUsersModal')) return;
    const modal = document.createElement('div');
    modal.id = 'pephubActiveUsersModal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'Colaboradores online');
    modal.innerHTML = `
      <div class="ou-modal-box">
        <div class="ou-modal-hd">
          <h3>
            <span class="ou-dot"></span>
            <span>Colaboradores Online<small>Sessões com atividade nos últimos 3 minutos</small></span>
          </h3>
          <button class="ou-modal-x" id="btnCloseActiveModal" title="Fechar" aria-label="Fechar">&times;</button>
        </div>
        <div class="ou-kpis">
          <div class="ou-kpi"><b id="ouKpiTotal">–</b><span>Online agora</span></div>
          <div class="ou-kpi"><b id="ouKpiColab">–</b><span>Colaboradores</span></div>
          <div class="ou-kpi"><b id="ouKpiAdmins">–</b><span>Administradores</span></div>
        </div>
        <div class="ou-modal-bd" id="activeUsersListBody">
          <div class="ou-empty">Carregando sessões ativas…</div>
        </div>
        <div class="ou-modal-ft">
          <span id="activeModalMeta">Horário de Brasília</span>
          <div style="display:flex;gap:8px">
            <button id="btnRefreshActiveList" class="ou-btn primary">Atualizar</button>
            <button id="btnCloseActiveModal2" class="ou-btn">Fechar</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const close = () => modal.classList.remove('on');
    document.getElementById('btnCloseActiveModal').onclick = close;
    document.getElementById('btnCloseActiveModal2').onclick = close;
    modal.onclick = (e) => { if (e.target === modal) close(); };
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    document.getElementById('btnRefreshActiveList').onclick = fetchActiveUsersList;
  }

  window.pephubOpenActiveUsersModal = function() {
    ensureActiveUsersModal();
    document.getElementById('pephubActiveUsersHoverCard')?.classList.remove('show');
    document.getElementById('pephubActiveUsersModal').classList.add('on');
    fetchActiveUsersList();
  };

  // ------------------------------------------------------------------
  // Widget "Online" reutilizável (relatórios, catálogo e Central Administrativa)
  // ------------------------------------------------------------------
  window.pephubMountOnlineWidget = function(host) {
    if (!host || host.dataset.pephubMounted === '1') return;
    host.dataset.pephubMounted = '1';
    ensureActiveUsersModal();

    host.innerHTML = `
      <div class="active-users-wrapper">
        <button type="button" id="btnHeaderActiveUsers" class="hd-btn btn-active-users" aria-haspopup="true" title="Usuários ativos agora">
          <span class="ou-dot"></span>
          <span class="ou-count ou-count-live">…</span>
        </button>
        <div id="pephubActiveUsersHoverCard" class="active-users-hover-card" role="tooltip">
          <div class="ou-card">
            <div class="ou-hd">
              <div class="ou-hd-title">
                <span class="ou-dot"></span>
                <span>Online agora <small>(<span class="ou-count-live">…</span>)</small></span>
              </div>
              <span class="ou-badge-live">Tempo real</span>
            </div>
            <div class="ou-body" id="hoverCardBody"><div class="ou-empty">Carregando…</div></div>
            <div class="ou-ft">
              <span>Horário de Brasília</span>
              <button type="button" class="ou-link" id="btnHoverCardFullModal">Ver detalhes &rarr;</button>
            </div>
          </div>
        </div>
      </div>
    `;

    const wrapper = host.querySelector('.active-users-wrapper');
    const hoverCard = host.querySelector('#pephubActiveUsersHoverCard');
    let hoverTimer = null;

    const openHover = () => {
      if (hoverTimer) clearTimeout(hoverTimer);
      if (!hoverCard.classList.contains('show')) {
        hoverCard.classList.add('show');
        fetchActiveUsersList();
      }
    };
    const closeHover = () => {
      hoverTimer = setTimeout(() => hoverCard.classList.remove('show'), 220);
    };

    // O wrapper contém botão + card: mover o mouse entre eles não fecha o painel
    wrapper.addEventListener('mouseenter', openHover);
    wrapper.addEventListener('mouseleave', closeHover);
    wrapper.addEventListener('focusin', openHover);
    wrapper.addEventListener('focusout', closeHover);

    host.querySelector('#btnHeaderActiveUsers').addEventListener('click', window.pephubOpenActiveUsersModal);
    host.querySelector('#btnHoverCardFullModal').addEventListener('click', window.pephubOpenActiveUsersModal);

    fetchActiveUsersList();
    ensureRefreshLoop();
  };

  // ------------------------------------------------------------------
  // Logout
  // ------------------------------------------------------------------
  async function handleLogout() {
    try {
      if (navigator.serviceWorker && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'LOGOUT' });
      }
      if ('caches' in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map(k => caches.delete(k)));
      }
      sessionStorage.clear();
      localStorage.clear();
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (_) {}
    window.location.replace('/login/?logout=1');
  }

  // ------------------------------------------------------------------
  // SISTEMA CORPORATIVO DE NOTIFICAÇÕES (UNIVERSAL: TODOS OS USUÁRIOS)
  // ------------------------------------------------------------------
  let _userNotifications = [];
  let _activeNotifFilter = 'all';
  let _notifPollingTimer = null;

  async function fetchUserNotifications() {
    try {
      const res = await fetch('/api/notifications');
      if (!res.ok) return [];
      const data = await res.json();
      _userNotifications = data.notifications || [];
      updateNotificationsUI(data.unread_count || 0);
      return _userNotifications;
    } catch (_) {
      return [];
    }
  }

  function formatRelativeDate(isoStr) {
    if (!isoStr) return 'Recente';
    try {
      const d = new Date(isoStr.replace(' ', 'T') + (isoStr.endsWith('Z') ? '' : 'Z'));
      const diffMs = Date.now() - d.getTime();
      const diffMin = Math.floor(diffMs / 60000);
      if (diffMin < 2) return 'Agora mesmo';
      if (diffMin < 60) return `Há ${diffMin} min`;
      const diffH = Math.floor(diffMin / 60);
      if (diffH < 24) return `Há ${diffH} hora${diffH > 1 ? 's' : ''}`;
      const diffDays = Math.floor(diffH / 24);
      if (diffDays === 1) return 'Ontem';
      if (diffDays < 7) return `Há ${diffDays} dias`;
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    } catch (_) {
      return 'Recente';
    }
  }

  function getNotifTypeMeta(type) {
    const map = {
      info: { label: 'Informativo', icon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>' },
      warning: { label: 'Atenção', icon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' },
      update: { label: 'Novo Painel', icon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' },
      security: { label: 'Segurança', icon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
      success: { label: 'Sucesso', icon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>' }
    };
    return map[type] || map.info;
  }

  function updateNotificationsUI(unreadCount) {
    document.querySelectorAll('.notif-badge').forEach(badge => {
      badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
      if (unreadCount > 0) {
        badge.classList.remove('empty');
        badge.classList.add('pulse');
      } else {
        badge.classList.add('empty');
        badge.classList.remove('pulse');
      }
    });

    const subEl = document.getElementById('notifHeaderSub');
    if (subEl) {
      subEl.textContent = unreadCount > 0 ? `${unreadCount} não lida${unreadCount > 1 ? 's' : ''}` : 'Todas lidas';
    }

    const tabUnreadEl = document.getElementById('notifTabUnreadCount');
    if (tabUnreadEl) {
      tabUnreadEl.textContent = unreadCount;
    }
  }

  function renderNotificationList() {
    const body = document.getElementById('notifListBody');
    if (!body) return;

    let filtered = _userNotifications;
    if (_activeNotifFilter === 'unread') {
      filtered = _userNotifications.filter(n => !n.is_read);
    }

    if (!filtered || filtered.length === 0) {
      body.innerHTML = `
        <div class="notif-empty">
          <svg class="notif-empty-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            <polyline points="9 11 11 13 15 9"/>
          </svg>
          <div style="font-weight:700;color:var(--ink);margin-bottom:3px">Você está em dia!</div>
          <div>Nenhum comunicado pendente para você no momento.</div>
        </div>
      `;
      return;
    }

    body.innerHTML = filtered.map(item => {
      const meta = getNotifTypeMeta(item.type);
      return `
        <div class="notif-item type-${escapeHtml(item.type)} ${item.is_read ? '' : 'unread'}" id="notif-item-${escapeHtml(item.id)}" data-id="${escapeHtml(item.id)}">
          <div class="notif-item-top">
            <span class="notif-tag type-${escapeHtml(item.type)}">
              ${meta.icon}
              ${escapeHtml(meta.label)}
            </span>
            <div class="notif-item-actions">
              ${!item.is_read ? `<button type="button" class="notif-btn-dismiss" title="Marcar como lida" onclick="window.__pephubMarkRead('${escapeHtml(item.id)}')"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></button>` : ''}
              <button type="button" class="notif-btn-dismiss" title="Dispensar aviso" onclick="window.__pephubDismissNotif('${escapeHtml(item.id)}')">&times;</button>
            </div>
          </div>
          <div class="notif-item-title">${escapeHtml(item.title)}</div>
          <div class="notif-item-msg">${escapeHtml(item.message)}</div>
          <div class="notif-item-ft">
            <span class="notif-time">${formatRelativeDate(item.created_at)}</span>
            ${item.action_url ? `
              <a href="${escapeHtml(item.action_url)}" class="notif-cta" onclick="window.__pephubMarkRead('${escapeHtml(item.id)}')">
                ${escapeHtml(item.action_label || 'Acessar')} &rarr;
              </a>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  window.__pephubMarkRead = async function(notifId) {
    try {
      const item = _userNotifications.find(n => n.id === notifId);
      if (item) item.is_read = true;
      const unreadCount = _userNotifications.filter(n => !n.is_read).length;
      updateNotificationsUI(unreadCount);
      renderNotificationList();
      await fetch(`/api/notifications/${notifId}/read`, { method: 'POST' });
    } catch (_) {}
  };

  window.__pephubDismissNotif = async function(notifId) {
    try {
      const el = document.getElementById(`notif-item-${notifId}`);
      if (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateX(10px)';
      }
      setTimeout(() => {
        _userNotifications = _userNotifications.filter(n => n.id !== notifId);
        const unreadCount = _userNotifications.filter(n => !n.is_read).length;
        updateNotificationsUI(unreadCount);
        renderNotificationList();
      }, 150);
      await fetch(`/api/notifications/${notifId}/dismiss`, { method: 'POST' });
    } catch (_) {}
  };

  window.__pephubMarkAllRead = async function() {
    try {
      _userNotifications.forEach(n => { n.is_read = true; });
      updateNotificationsUI(0);
      renderNotificationList();
      await fetch('/api/notifications/read-all', { method: 'POST' });
    } catch (_) {}
  };

  window.pephubMountNotificationsWidget = function(host) {
    if (!host || host.dataset.pephubNotifMounted === '1') return;
    host.dataset.pephubNotifMounted = '1';

    host.innerHTML = `
      <div class="notif-wrapper">
        <button type="button" class="hd-btn btn-notifications" id="btnHeaderNotifications" aria-haspopup="true" title="Notificações & Comunicados">
          <svg class="notif-bell-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span class="notif-badge empty">0</span>
        </button>
        <div id="pephubNotificationsPopover" class="notif-popover" role="dialog" aria-label="Notificações corporativas">
          <div class="notif-card-box">
            <div class="notif-hd">
              <div class="notif-hd-left">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
                <div>
                  <h4 class="notif-hd-title">Notificações</h4>
                  <div class="notif-hd-sub" id="notifHeaderSub">Carregando…</div>
                </div>
              </div>
              <button type="button" class="notif-btn-all-read" onclick="window.__pephubMarkAllRead()" title="Marcar todas como lidas">
                Limpar não lidas
              </button>
            </div>
            <div class="notif-tabs-bar">
              <button type="button" class="notif-tab active" id="btnNotifTabAll">Todas</button>
              <button type="button" class="notif-tab" id="btnNotifTabUnread">Não lidas (<span id="notifTabUnreadCount">0</span>)</button>
            </div>
            <div class="notif-body" id="notifListBody">
              <div class="notif-empty">Carregando avisos…</div>
            </div>
          </div>
        </div>
      </div>
    `;

    const btn = host.querySelector('#btnHeaderNotifications');
    const popover = host.querySelector('#pephubNotificationsPopover');
    const tabAll = host.querySelector('#btnNotifTabAll');
    const tabUnread = host.querySelector('#btnNotifTabUnread');

    const togglePopover = () => {
      const isOpen = popover.classList.contains('show');
      if (isOpen) {
        popover.classList.remove('show');
      } else {
        popover.classList.add('show');
        renderNotificationList();
      }
    };

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePopover();
    });

    tabAll.addEventListener('click', () => {
      _activeNotifFilter = 'all';
      tabAll.classList.add('active');
      tabUnread.classList.remove('active');
      renderNotificationList();
    });

    tabUnread.addEventListener('click', () => {
      _activeNotifFilter = 'unread';
      tabUnread.classList.add('active');
      tabAll.classList.remove('active');
      renderNotificationList();
    });

    document.addEventListener('click', (e) => {
      if (popover.classList.contains('show') && !host.contains(e.target)) {
        popover.classList.remove('show');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && popover.classList.contains('show')) {
        popover.classList.remove('show');
      }
    });

    // Carga inicial
    fetchUserNotifications().then(() => renderNotificationList());
    if (!_notifPollingTimer) {
      _notifPollingTimer = setInterval(fetchUserNotifications, 45000);
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') fetchUserNotifications();
      });
    }
  };

  // ------------------------------------------------------------------
  // Cabeçalho dos relatórios (Universal)
  // ------------------------------------------------------------------
  window.initPephubHeader = async function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
      const user = await getMe();
      if (!user || !user.authenticated || (user.status && user.status !== 'aprovado')) {
        window.location.replace('/login/');
        return;
      }

      if (user.is_admin) {
        container.innerHTML = `
          <span data-pephub-notifications></span>
          <span data-pephub-online></span>
          <a href="/admin/" class="hd-btn" title="Ir para Central Administrativa">Admin</a>
          <button id="btnHeaderLogout" class="hd-btn" title="Encerrar sessão corporativa">Sair</button>
        `;
        window.pephubMountNotificationsWidget(container.querySelector('[data-pephub-notifications]'));
        window.pephubMountOnlineWidget(container.querySelector('[data-pephub-online]'));
      } else {
        // Colaborador comum: botão de Notificações e botão Sair
        container.innerHTML = `
          <span data-pephub-notifications></span>
          <button id="btnHeaderLogout" class="hd-btn" title="Encerrar sessão corporativa">Sair</button>
        `;
        window.pephubMountNotificationsWidget(container.querySelector('[data-pephub-notifications]'));
      }

      const btnLogout = document.getElementById('btnHeaderLogout');
      if (btnLogout) {
        btnLogout.onclick = (e) => {
          e.preventDefault();
          btnLogout.disabled = true;
          btnLogout.textContent = 'Saindo...';
          handleLogout();
        };
      }
    } catch (_) {
      window.location.replace('/login/');
    }
  };

  // ------------------------------------------------------------------
  // Inicialização automática
  // ------------------------------------------------------------------
  function autoInit() {
    startHeartbeat();

    // Monta notificações para qualquer elemento anotado (para todos os usuários autenticados)
    const notifHosts = document.querySelectorAll('[data-pephub-notifications]');
    if (notifHosts.length) {
      getMe().then(me => {
        if (me && me.authenticated) {
          notifHosts.forEach(h => window.pephubMountNotificationsWidget(h));
        }
      });
    }

    // Monta widget "Online" apenas para administradores
    const onlineHosts = document.querySelectorAll('[data-pephub-online]');
    if (onlineHosts.length) {
      getMe().then(me => {
        if (me && me.authenticated && me.is_admin) {
          onlineHosts.forEach(h => window.pephubMountOnlineWidget(h));
        }
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoInit);
  else autoInit();
})();
