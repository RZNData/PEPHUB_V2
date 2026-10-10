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
  // Cabeçalho dos relatórios
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
          <span data-pephub-online></span>
          <a href="/admin/" class="hd-btn" title="Ir para Central Administrativa">Admin</a>
          <button id="btnHeaderLogout" class="hd-btn" title="Encerrar sessão corporativa">Sair</button>
        `;
        window.pephubMountOnlineWidget(container.querySelector('[data-pephub-online]'));
      } else {
        // Colaborador comum: somente o botão Sair (Voltar ao Catálogo já está no HTML)
        container.innerHTML = `
          <button id="btnHeaderLogout" class="hd-btn" title="Encerrar sessão corporativa">Sair</button>
        `;
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
    const hosts = document.querySelectorAll('[data-pephub-online]');
    if (hosts.length) {
      getMe().then(me => {
        if (me && me.authenticated && me.is_admin) {
          hosts.forEach(h => window.pephubMountOnlineWidget(h));
        }
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoInit);
  else autoInit();
})();
