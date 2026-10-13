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

    /* Botão informativo de usuários ativos (ícone corporativo + badge numérico fixo) */
    .hd-btn.btn-active-users {
      position: relative !important;
      padding: 5px 8px !important;
      min-width: 34px !important;
      height: 28px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      background: rgba(255, 255, 255, 0.22) !important;
      border: 1px solid rgba(255, 255, 255, 0.55) !important;
      border-radius: 4px !important;
      cursor: pointer !important;
      overflow: visible !important;
    }
    .hd-btn.btn-active-users:hover {
      background: rgba(255, 255, 255, 0.38) !important;
      border-color: #ffffff !important;
    }
    .ou-icon {
      width: 16px;
      height: 16px;
      display: block;
      color: #ffffff;
      stroke: #ffffff;
      flex: none;
    }
    .ou-badge {
      position: absolute !important;
      top: -5px !important;
      right: -6px !important;
      background: #16a34a !important; /* Verde corporativo vivo de status online */
      color: #ffffff !important;
      min-width: 18px !important;
      height: 18px !important;
      padding: 0 4px !important;
      border-radius: 9px !important;
      border: 2px solid #ffffff !important;
      font-size: 10px !important;
      font-weight: 800 !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      box-sizing: border-box !important;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.28) !important;
      line-height: 1 !important;
      z-index: 3 !important;
      pointer-events: none !important;
    }
    .ou-badge.empty { display: none !important; }
    .ou-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #3ddc84;
      flex: none;
      display: inline-block;
    }
    .ou-dot.idle { background: #9aa5b1; }

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
      padding: 5px 8px !important;
      min-width: 34px !important;
      height: 28px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      background: rgba(255, 255, 255, 0.22) !important;
      border: 1px solid rgba(255, 255, 255, 0.55) !important;
      border-radius: 4px !important;
      cursor: pointer !important;
      overflow: visible !important;
    }
    .hd-btn.btn-notifications:hover {
      background: rgba(255, 255, 255, 0.38) !important;
      border-color: #ffffff !important;
    }
    .notif-bell-icon {
      width: 17px;
      height: 17px;
      display: block;
      flex: none;
    }
    .notif-badge {
      position: absolute !important;
      top: -5px !important;
      right: -6px !important;
      background: #e53935 !important; /* Vermelho vivo fiel ao modelo executivo */
      color: #ffffff !important;
      min-width: 18px !important;
      height: 18px !important;
      padding: 0 4px !important;
      border-radius: 9px !important;
      border: 2px solid #ffffff !important;
      font-size: 10px !important;
      font-weight: 800 !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      box-sizing: border-box !important;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.28) !important;
      line-height: 1 !important;
      z-index: 3 !important;
      pointer-events: none !important;
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

    /* ==================================================================
       PROFILE BUTTON, DROPDOWN & MODAIS (PERFIL & CONFIGURAÇÕES)
       ================================================================== */
    .ph-profile-wrapper {
      position: relative !important;
      display: inline-flex !important;
      align-items: center !important;
    }
    .ph-profile-btn {
      display: inline-flex !important;
      align-items: center !important;
      gap: 7px !important;
      background: rgba(255, 255, 255, 0.22) !important;
      color: #ffffff !important;
      border: 1px solid rgba(255, 255, 255, 0.5) !important;
      padding: 3px 10px 3px 4px !important;
      border-radius: 18px !important;
      cursor: pointer !important;
      transition: all 0.15s ease !important;
      font-family: inherit !important;
      user-select: none !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18) !important;
      text-decoration: none !important;
      line-height: normal !important;
    }
    .ph-profile-btn:hover {
      background: rgba(255, 255, 255, 0.38) !important;
      border-color: #ffffff !important;
    }
    .ph-profile-avatar {
      width: 24px !important;
      height: 24px !important;
      border-radius: 50% !important;
      background: linear-gradient(135deg, #8a0f18 0%, #c0191f 100%) !important;
      color: #ffffff !important;
      font-weight: 800 !important;
      font-size: 10px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      border: 1.5px solid #ffffff !important;
      overflow: hidden !important;
      flex: none !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    .ph-profile-avatar img {
      width: 100% !important;
      height: 100% !important;
      object-fit: cover !important;
      display: block !important;
    }
    .ph-profile-name {
      font-size: 11.5px !important;
      font-weight: 700 !important;
      max-width: 110px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      color: #ffffff !important;
    }
    .ph-profile-chevron {
      width: 10px !important;
      height: 10px !important;
      stroke: #ffffff !important;
      stroke-width: 2.2 !important;
      fill: none !important;
      flex: none !important;
      transition: transform 0.15s ease !important;
    }
    .ph-profile-wrapper.open .ph-profile-chevron {
      transform: rotate(180deg) !important;
    }

    /* Dropdown Suspenso */
    .ph-profile-dropdown {
      display: none;
      position: absolute !important;
      top: calc(100% + 6px) !important;
      right: 0 !important;
      width: 280px !important;
      background: #ffffff !important;
      border: 1px solid #dfe3e8 !important;
      border-radius: 5px !important;
      box-shadow: 0 14px 34px rgba(28, 36, 48, 0.24) !important;
      z-index: 99999 !important;
      overflow: hidden !important;
      font-family: "Segoe UI", Roboto, Arial, sans-serif !important;
      cursor: default !important;
      animation: phFade .14s ease-out !important;
    }
    .ph-profile-dropdown.show {
      display: block !important;
    }
    .ph-dropdown-header {
      padding: 14px 16px !important;
      background: #f8fafc !important;
      border-bottom: 1px solid #eef2f6 !important;
      display: flex !important;
      align-items: center !important;
      gap: 12px !important;
      position: relative !important;
    }
    .ph-dropdown-header::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);
    }
    .ph-dropdown-big-avatar {
      width: 44px !important;
      height: 44px !important;
      border-radius: 50% !important;
      background: linear-gradient(135deg, #8a0f18 0%, #c0191f 100%) !important;
      color: #fff !important;
      font-weight: 800 !important;
      font-size: 15px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      border: 2px solid #ffffff !important;
      box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
      overflow: hidden !important;
      flex: none !important;
    }
    .ph-dropdown-big-avatar img {
      width: 100% !important;
      height: 100% !important;
      object-fit: cover !important;
      display: block !important;
    }
    .ph-dropdown-user-info {
      flex: 1 !important;
      min-width: 0 !important;
    }
    .ph-dropdown-user-name {
      font-size: 13px !important;
      font-weight: 700 !important;
      color: #1c2430 !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }
    .ph-dropdown-user-email {
      font-size: 11px !important;
      color: #5b6675 !important;
      margin-top: 2px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }
    .ph-dropdown-user-badge {
      display: inline-block !important;
      font-size: 9.5px !important;
      font-weight: 700 !important;
      padding: 1px 6px !important;
      border-radius: 3px !important;
      margin-top: 4px !important;
      background: #eceef1 !important;
      color: #5b6675 !important;
      text-transform: uppercase !important;
      letter-spacing: .3px !important;
    }
    .ph-dropdown-user-badge.admin {
      background: #fdece9 !important;
      color: #c0191f !important;
    }
    .ph-dropdown-menu-list {
      padding: 6px 0 !important;
      display: flex !important;
      flex-direction: column !important;
    }
    .ph-dropdown-item {
      display: flex !important;
      align-items: center !important;
      gap: 11px !important;
      padding: 9px 16px !important;
      color: #1c2430 !important;
      text-decoration: none !important;
      cursor: pointer !important;
      border: none !important;
      background: none !important;
      width: 100% !important;
      box-sizing: border-box !important;
      text-align: left !important;
      transition: background .12s ease !important;
    }
    .ph-dropdown-item:hover {
      background: #f1f4f8 !important;
    }
    .ph-dropdown-item-icon {
      width: 16px !important;
      height: 16px !important;
      stroke: #5b6675 !important;
      fill: none !important;
      stroke-width: 2 !important;
      flex: none !important;
    }
    .ph-dropdown-item:hover .ph-dropdown-item-icon {
      stroke: #c0191f !important;
    }
    .ph-dropdown-item-texts {
      flex: 1 !important;
      min-width: 0 !important;
    }
    .ph-dropdown-item-title {
      font-size: 12.5px !important;
      font-weight: 600 !important;
      color: #1c2430 !important;
      line-height: 1.2 !important;
    }
    .ph-dropdown-item-subtitle {
      font-size: 10.5px !important;
      color: #728095 !important;
      margin-top: 2px !important;
      line-height: 1.2 !important;
    }
    .ph-dropdown-divider {
      height: 1px !important;
      background: #eef2f6 !important;
      margin: 4px 0 !important;
    }
    .ph-dropdown-item.logout {
      color: #c0191f !important;
    }
    .ph-dropdown-item.logout .ph-dropdown-item-title {
      color: #c0191f !important;
      font-weight: 700 !important;
    }
    .ph-dropdown-item.logout .ph-dropdown-item-icon {
      stroke: #c0191f !important;
    }
    .ph-dropdown-item.logout:hover {
      background: #fdece9 !important;
    }

    /* Modais Corporativos */
    .ph-modal-backdrop {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      background: rgba(18, 24, 32, 0.65) !important;
      backdrop-filter: blur(2px) !important;
      z-index: 100000 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      padding: 16px !important;
      box-sizing: border-box !important;
    }
    .ph-modal-dialog {
      background: #ffffff !important;
      border-radius: 4px !important;
      width: 100% !important;
      max-width: 580px !important;
      max-height: 90vh !important;
      display: flex !important;
      flex-direction: column !important;
      box-shadow: 0 20px 50px rgba(0,0,0,0.3) !important;
      overflow: hidden !important;
      border: 1px solid #dfe3e8 !important;
      animation: phPop .15s ease-out !important;
      font-family: "Segoe UI", Roboto, Arial, sans-serif !important;
    }
    @keyframes phPop {
      from { opacity: 0; transform: scale(0.96) translateY(-8px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }
    .ph-modal-header {
      background: linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%) !important;
      padding: 14px 20px !important;
      color: #ffffff !important;
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      flex: none !important;
    }
    .ph-modal-header-text small {
      display: block !important;
      font-size: 10.5px !important;
      text-transform: uppercase !important;
      letter-spacing: 1px !important;
      opacity: 0.9 !important;
      font-weight: 600 !important;
    }
    .ph-modal-header-text b {
      font-size: 16px !important;
      font-weight: 700 !important;
      letter-spacing: -0.2px !important;
    }
    .ph-modal-close-btn {
      background: none !important;
      border: none !important;
      color: #ffffff !important;
      font-size: 20px !important;
      cursor: pointer !important;
      opacity: 0.85 !important;
      line-height: 1 !important;
      padding: 0 4px !important;
      transition: opacity .15s !important;
    }
    .ph-modal-close-btn:hover {
      opacity: 1 !important;
    }
    .ph-modal-content {
      padding: 20px 24px !important;
      overflow-y: auto !important;
      flex: 1 !important;
      font-size: 12.5px !important;
      color: #1c2430 !important;
      box-sizing: border-box !important;
    }
    .ph-modal-actions {
      padding: 12px 20px !important;
      background: #f8fafc !important;
      border-top: 1px solid #eef2f6 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      gap: 10px !important;
      flex: none !important;
    }
    .ph-btn-primary {
      background: #8a0f18 !important;
      color: #ffffff !important;
      border: none !important;
      padding: 9px 18px !important;
      border-radius: 3px !important;
      font-size: 12.5px !important;
      font-weight: 700 !important;
      cursor: pointer !important;
      transition: background .15s !important;
      display: inline-flex !important;
      align-items: center !important;
      gap: 6px !important;
    }
    .ph-btn-primary:hover {
      background: #c0191f !important;
    }
    .ph-btn-secondary {
      background: #ffffff !important;
      color: #1c2430 !important;
      border: 1px solid #dfe3e8 !important;
      padding: 8px 16px !important;
      border-radius: 3px !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      cursor: pointer !important;
      transition: all .15s !important;
    }
    .ph-btn-secondary:hover {
      background: #f1f4f8 !important;
      border-color: #cbd5e1 !important;
    }
    .ph-btn-danger-outline {
      background: #ffffff !important;
      color: #c0191f !important;
      border: 1px solid #fecaca !important;
      padding: 8px 14px !important;
      border-radius: 3px !important;
      font-size: 11.5px !important;
      font-weight: 600 !important;
      cursor: pointer !important;
      transition: all .15s !important;
    }
    .ph-btn-danger-outline:hover {
      background: #fef2f2 !important;
      border-color: #c0191f !important;
    }
    .ph-form-grid {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 12px 14px !important;
      margin-top: 14px !important;
    }
    .ph-form-group-full {
      grid-column: 1 / -1 !important;
    }
    .ph-label {
      display: block !important;
      font-size: 11px !important;
      font-weight: 700 !important;
      color: #5b6675 !important;
      text-transform: uppercase !important;
      letter-spacing: .4px !important;
      margin-bottom: 5px !important;
    }
    .ph-input, .ph-select, .ph-textarea {
      width: 100% !important;
      box-sizing: border-box !important;
      border: 1px solid #dfe3e8 !important;
      border-radius: 3px !important;
      padding: 8px 11px !important;
      font-size: 12.5px !important;
      font-family: inherit !important;
      color: #1c2430 !important;
      background: #ffffff !important;
      transition: border-color .15s !important;
    }
    .ph-input:focus, .ph-select:focus, .ph-textarea:focus {
      outline: none !important;
      border-color: #c0191f !important;
      box-shadow: 0 0 0 2px rgba(192, 25, 31, 0.12) !important;
    }
    .ph-input[readonly], .ph-input:disabled {
      background: #f8fafc !important;
      color: #64748b !important;
      border-color: #e2e8f0 !important;
      cursor: not-allowed !important;
    }
    .ph-notice-box {
      background: #f0f7ff !important;
      border: 1px solid #cfe2ff !important;
      border-radius: 4px !important;
      padding: 11px 14px !important;
      margin-bottom: 14px !important;
      font-size: 12px !important;
      line-height: 1.5 !important;
      color: #1e429f !important;
    }
    .ph-notice-box.warning {
      background: #fefce8 !important;
      border-color: #fef08a !important;
      color: #854d0e !important;
    }
    .ph-notice-box.success {
      background: #f0fdf4 !important;
      border-color: #bbf7d0 !important;
      color: #166534 !important;
    }
    .ph-avatar-edit-box {
      display: flex !important;
      align-items: center !important;
      gap: 16px !important;
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 4px !important;
      padding: 12px 16px !important;
    }
    .ph-avatar-preview-circle {
      width: 60px !important;
      height: 60px !important;
      border-radius: 50% !important;
      background: linear-gradient(135deg, #8a0f18 0%, #c0191f 100%) !important;
      color: #ffffff !important;
      font-size: 20px !important;
      font-weight: 800 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      border: 2px solid #ffffff !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
      overflow: hidden !important;
      flex: none !important;
    }
    .ph-avatar-preview-circle img {
      width: 100% !important;
      height: 100% !important;
      object-fit: cover !important;
      display: block !important;
    }
    .ph-settings-section {
      background: #ffffff !important;
      border: 1px solid #dfe3e8 !important;
      border-radius: 4px !important;
      padding: 14px 16px !important;
      margin-bottom: 16px !important;
    }
    .ph-settings-title {
      font-size: 13px !important;
      font-weight: 700 !important;
      color: #1c2430 !important;
      margin-bottom: 12px !important;
      display: flex !important;
      align-items: center !important;
      gap: 8px !important;
    }
    .ph-radio-label {
      display: flex !important;
      align-items: flex-start !important;
      gap: 8px !important;
      font-size: 12.5px !important;
      color: #1c2430 !important;
      cursor: pointer !important;
      margin-bottom: 8px !important;
    }
    .ph-radio-label input {
      margin-top: 2px !important;
      cursor: pointer !important;
    }
    .ph-checkbox-grid {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 6px 12px !important;
      margin: 10px 0 10px 24px !important;
      padding: 10px 14px !important;
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 4px !important;
    }
    .ph-check-label {
      display: flex !important;
      align-items: center !important;
      gap: 7px !important;
      font-size: 12px !important;
      color: #334155 !important;
      cursor: pointer !important;
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
  let _lastHbSent = 0;
  async function sendHeartbeat() {
    const now = Date.now();
    if (now - _lastHbSent < 25000) return; // Debounce de 25s: previne flood de abas/visibilidade
    _lastHbSent = now;
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
        <button type="button" id="btnHeaderActiveUsers" class="hd-btn btn-active-users" aria-haspopup="true" title="Colaboradores online agora">
          <svg class="ou-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <span class="ou-badge ou-count-live">0</span>
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
      } else {
        badge.classList.add('empty');
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
          <svg class="notif-bell-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C8.68629 2 6 4.68629 6 8V11.2C6 12.3 5.4 13.5 4.5 14.3L3.6 15.1C2.8 15.8 3.3 17.2 4.4 17.2H19.6C20.7 17.2 21.2 15.8 20.4 15.1L19.5 14.3C18.6 13.5 18 12.3 18 11.2V8C18 4.68629 15.3137 2 12 2Z" fill="#ffb800" stroke="#d97706" stroke-width="1.2"/>
            <ellipse cx="12" cy="19.5" rx="3.2" ry="2.2" fill="#d97706"/>
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
  // WIDGET CORPORATIVO DE PROFILE (CANTO SUPERIOR DIREITO)
  // Dropdown: 1 - Perfil, 2 - Configurações, 3 - Sair
  // ------------------------------------------------------------------

  function closeAllProfileDropdowns() {
    document.querySelectorAll('.ph-profile-dropdown.show').forEach(el => el.classList.remove('show'));
    document.querySelectorAll('.ph-profile-wrapper.open').forEach(el => el.classList.remove('open'));
  }

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.ph-profile-wrapper')) {
      closeAllProfileDropdowns();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllProfileDropdowns();
    }
  });

  // Helper para compressão de avatar em canvas (< 35KB)
  function compressAvatarFile(file) {
    return new Promise((resolve, reject) => {
      if (!file || !file.type.startsWith('image/')) {
        reject(new Error('Selecione uma imagem válida (PNG, JPG, WEBP).'));
        return;
      }
      if (file.size > 8 * 1024 * 1024) {
        reject(new Error('A imagem deve ter no máximo 8MB.'));
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const size = 160;
          const minSide = Math.min(img.width, img.height);
          const sx = (img.width - minSide) / 2;
          const sy = (img.height - minSide) / 2;
          const canvas = document.createElement('canvas');
          canvas.width = size;
          canvas.height = size;
          const ctx = canvas.getContext('2d');
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, size, size);
          ctx.drawImage(img, sx, sy, minSide, minSide, 0, 0, size, size);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
          resolve(dataUrl);
        };
        img.onerror = () => reject(new Error('Não foi possível ler os dados da imagem.'));
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('Erro na leitura do arquivo local.'));
      reader.readAsDataURL(file);
    });
  }

  function renderAvatarHtml(foto, name, className = 'ph-profile-avatar') {
    if (foto && typeof foto === 'string' && foto.startsWith('data:image/')) {
      return `<div class="${className}"><img src="${escapeHtml(foto)}" alt="${escapeHtml(name || 'Avatar')}"></div>`;
    }
    return `<div class="${className}">${escapeHtml(getInitials(name))}</div>`;
  }

  // ------------------------------------------------------------------
  // Modal 1: Perfil Cadastral & Foto
  // ------------------------------------------------------------------
  async function openProfileModal() {
    closeAllProfileDropdowns();
    let modalEl = document.getElementById('pephubProfileModal');
    if (!modalEl) {
      modalEl = document.createElement('div');
      modalEl.id = 'pephubProfileModal';
      modalEl.className = 'ph-modal-backdrop';
      document.body.appendChild(modalEl);
    }
    modalEl.style.display = 'flex';
    modalEl.innerHTML = `
      <div class="ph-modal-dialog">
        <div class="ph-modal-header">
          <div class="ph-modal-header-text">
            <small>Identidade Corporativa · Regional Norte</small>
            <b>Meu Perfil</b>
          </div>
          <button type="button" class="ph-modal-close-btn" id="btnCloseProfileModal" aria-label="Fechar">&times;</button>
        </div>
        <div class="ph-modal-content" id="profileModalContent">
          <div style="text-align:center;padding:36px 0;color:#64748b">Carregando dados cadastrais…</div>
        </div>
        <div class="ph-modal-actions" id="profileModalActions">
          <button type="button" class="ph-btn-secondary" id="btnProfileModalCancel">Fechar</button>
        </div>
      </div>
    `;

    const close = () => { modalEl.style.display = 'none'; };
    modalEl.querySelector('#btnCloseProfileModal').onclick = close;
    modalEl.querySelector('#btnProfileModalCancel').onclick = close;
    modalEl.onclick = (e) => { if (e.target === modalEl) close(); };

    try {
      const res = await fetch('/api/user/profile');
      if (!res.ok) throw new Error('Falha ao carregar perfil');
      const data = await res.json();
      renderProfileForm(modalEl, data);
    } catch (_) {
      const cnt = modalEl.querySelector('#profileModalContent');
      if (cnt) {
        cnt.innerHTML = `
          <div class="ph-notice-box" style="background:#fef2f2;border-color:#fecaca;color:#991b1b">
            Erro ao carregar dados do usuário. Por favor, tente novamente.
          </div>
        `;
      }
    }
  }

  function renderProfileForm(modalEl, data) {
    const user = data.user || {};
    const pending = data.pending_request;
    const isAdmin = !!user.is_admin;
    let isEditing = false;
    let currentFotoBase64 = user.foto || '';

    const contentEl = modalEl.querySelector('#profileModalContent');
    const actionsEl = modalEl.querySelector('#profileModalActions');

    function refreshView() {
      const initials = getInitials(user.nome_completo);
      const avatarPreview = currentFotoBase64
        ? `<img id="profileAvatarImgPreview" src="${escapeHtml(currentFotoBase64)}" alt="Foto de perfil">`
        : `<span id="profileAvatarInitialsPreview">${escapeHtml(initials)}</span>`;

      let pendingHtml = '';
      if (pending && !isAdmin) {
        const reqDate = pending.requested_at ? formatTimeBr(pending.requested_at) : 'recentemente';
        pendingHtml = `
          <div class="ph-notice-box warning">
            <b>Solicitação em Análise:</b> Você possui uma solicitação de alteração cadastral enviada em ${escapeHtml(pending.requested_at || '')} que está aguardando validação do Administrador. Enquanto não for validada, seus dados oficiais permanecem inalterados.
          </div>
        `;
      }

      let editNoticeHtml = '';
      if (isEditing && !isAdmin) {
        editNoticeHtml = `
          <div class="ph-notice-box">
            <b>Atenção:</b> Por governança corporativa, qualquer alteração em seus dados cadastrais (nome, telefone, setor, função e foto) será encaminhada por e-mail para aprovação do Administrador. A alteração só terá efeito após validação formal.
          </div>
        `;
      }

      contentEl.innerHTML = `
        ${pendingHtml}
        ${editNoticeHtml}
        <div id="profileFormFeedback"></div>

        <div class="ph-avatar-edit-box">
          <div class="ph-avatar-preview-circle" id="profileAvatarCircle">
            ${avatarPreview}
          </div>
          <div>
            <b style="font-size:13px;display:block;margin-bottom:2px">Foto do Perfil</b>
            <span style="font-size:11.5px;color:#64748b;display:block;margin-bottom:8px">
              ${user.foto ? 'Foto corporativa definida.' : 'Nenhuma foto definida. O sistema exibe suas iniciais.'}
            </span>
            ${isEditing ? `
              <div style="display:flex;gap:8px;align-items:center">
                <label class="ph-btn-secondary" style="font-size:11px;padding:5px 10px;cursor:pointer">
                  <input type="file" id="profileFileInput" accept="image/png,image/jpeg,image/webp" style="display:none">
                  Escolher foto
                </label>
                ${currentFotoBase64 ? `<button type="button" id="btnRemoveAvatar" class="ph-btn-danger-outline" style="font-size:11px;padding:4px 8px">Remover</button>` : ''}
              </div>
            ` : ''}
          </div>
        </div>

        <div class="ph-form-grid">
          <div class="ph-form-group-full">
            <label class="ph-label" for="pfNome">Nome Completo</label>
            <input class="ph-input" type="text" id="pfNome" value="${escapeHtml(user.nome_completo || '')}" ${isEditing ? '' : 'readonly'}>
          </div>

          <div>
            <label class="ph-label" for="pfLogin">Login de Rede</label>
            <input class="ph-input" type="text" id="pfLogin" value="${escapeHtml(user.login_claro || '')}" readonly title="Identificador corporativo único (não editável)">
          </div>

          <div>
            <label class="ph-label" for="pfEmail">E-mail Institucional</label>
            <input class="ph-input" type="email" id="pfEmail" value="${escapeHtml(user.email_claro || '')}" readonly title="E-mail de autenticação (não editável)">
          </div>

          <div>
            <label class="ph-label" for="pfArea">Setor / Área</label>
            <input class="ph-input" type="text" id="pfArea" value="${escapeHtml(user.area || '')}" ${isEditing ? '' : 'readonly'}>
          </div>

          <div>
            <label class="ph-label" for="pfFuncao">Função / Cargo</label>
            <input class="ph-input" type="text" id="pfFuncao" value="${escapeHtml(user.funcao || '')}" ${isEditing ? '' : 'readonly'}>
          </div>

          <div class="ph-form-group-full">
            <label class="ph-label" for="pfTelefone">Telefone / Ramal</label>
            <input class="ph-input" type="text" id="pfTelefone" value="${escapeHtml(user.telefone || '')}" ${isEditing ? '' : 'readonly'}>
          </div>
        </div>

        <div style="margin-top:20px;padding-top:16px;border-top:1px solid #eef2f6;display:flex;align-items:center;justify-content:space-between">
          <div>
            <b style="font-size:12.5px;color:#1c2430;display:block">Segurança & Senha</b>
            <span style="font-size:11.5px;color:#64748b">Deseja alterar ou redefinir sua senha de acesso?</span>
          </div>
          <button type="button" class="ph-btn-secondary" id="btnProfileResetPassword" style="font-size:11.5px">
            Redefinir Senha
          </button>
        </div>
      `;

      // Eventos de foto
      if (isEditing) {
        const fileInput = contentEl.querySelector('#profileFileInput');
        if (fileInput) {
          fileInput.onchange = async (e) => {
            const f = e.target.files && e.target.files[0];
            if (!f) return;
            try {
              const b64 = await compressAvatarFile(f);
              currentFotoBase64 = b64;
              refreshView();
            } catch (err) {
              alert(err.message || 'Erro ao carregar imagem');
            }
          };
        }
        const btnRemove = contentEl.querySelector('#btnRemoveAvatar');
        if (btnRemove) {
          btnRemove.onclick = () => {
            currentFotoBase64 = '';
            refreshView();
          };
        }
      }

      // Evento de redefinir senha
      const btnResetPwd = contentEl.querySelector('#btnProfileResetPassword');
      if (btnResetPwd) {
        btnResetPwd.onclick = async () => {
          if (!confirm('Deseja enviar um link de redefinição de senha para o seu e-mail institucional?')) return;
          btnResetPwd.disabled = true;
          btnResetPwd.textContent = 'Enviando link…';
          try {
            const res = await fetch('/api/user/profile/password-reset', { method: 'POST' });
            const d = await res.json();
            const fb = contentEl.querySelector('#profileFormFeedback');
            if (fb) {
              fb.innerHTML = `<div class="ph-notice-box success">${escapeHtml(d.message || 'Link de redefinição de senha enviado com sucesso.')}</div>`;
            }
          } catch (_) {
            alert('Não foi possível enviar a redefinição de senha no momento.');
          } finally {
            btnResetPwd.disabled = false;
            btnResetPwd.textContent = 'Redefinir Senha';
          }
        };
      }

      // Rodapé de Ações
      if (!isEditing) {
        actionsEl.innerHTML = `
          <button type="button" class="ph-btn-secondary" id="btnProfileCloseBottom">Fechar</button>
          <button type="button" class="ph-btn-primary" id="btnProfileStartEdit">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            ${isAdmin ? 'Editar Dados' : 'Solicitar Alteração'}
          </button>
        `;
        actionsEl.querySelector('#btnProfileCloseBottom').onclick = () => { modalEl.style.display = 'none'; };
        actionsEl.querySelector('#btnProfileStartEdit').onclick = () => {
          isEditing = true;
          refreshView();
        };
      } else {
        actionsEl.innerHTML = `
          <button type="button" class="ph-btn-secondary" id="btnProfileCancelEdit">Cancelar</button>
          <button type="button" class="ph-btn-primary" id="btnProfileSubmitEdit">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            ${isAdmin ? 'Salvar Alterações' : 'Enviar para Validação'}
          </button>
        `;
        actionsEl.querySelector('#btnProfileCancelEdit').onclick = () => {
          isEditing = false;
          currentFotoBase64 = user.foto || '';
          refreshView();
        };
        actionsEl.querySelector('#btnProfileSubmitEdit').onclick = async () => {
          const nome = (contentEl.querySelector('#pfNome')?.value || '').trim();
          const area = (contentEl.querySelector('#pfArea')?.value || '').trim();
          const funcao = (contentEl.querySelector('#pfFuncao')?.value || '').trim();
          const telefone = (contentEl.querySelector('#pfTelefone')?.value || '').trim();

          if (!nome) {
            alert('Por favor, informe seu nome completo.');
            return;
          }

          const btnSubmit = actionsEl.querySelector('#btnProfileSubmitEdit');
          btnSubmit.disabled = true;
          btnSubmit.textContent = isAdmin ? 'Salvando…' : 'Enviando…';

          try {
            const res = await fetch('/api/user/profile/request-change', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                nome_completo: nome,
                area,
                funcao,
                telefone,
                foto: currentFotoBase64
              })
            });
            const resData = await res.json();
            if (!res.ok) throw new Error(resData.error || 'Falha ao processar solicitação');

            // Atualiza dados locais
            user.nome_completo = nome;
            user.area = area;
            user.funcao = funcao;
            user.telefone = telefone;
            if (isAdmin) user.foto = currentFotoBase64;

            // Atualiza cache e botões
            _mePromise = null;
            updateProfileWidgetsUI(user);

            isEditing = false;
            refreshView();

            const fb = contentEl.querySelector('#profileFormFeedback');
            if (fb) {
              fb.innerHTML = `<div class="ph-notice-box success">${escapeHtml(resData.message || 'Sucesso!')}</div>`;
            }
          } catch (err) {
            alert(err.message || 'Erro ao enviar alteração.');
          } finally {
            if (btnSubmit) {
              btnSubmit.disabled = false;
              btnSubmit.textContent = isAdmin ? 'Salvar Alterações' : 'Enviar para Validação';
            }
          }
        };
      }
    }

    refreshView();
  }

  // ------------------------------------------------------------------
  // Modal 2: Configurações & Reporte de Erro
  // ------------------------------------------------------------------
  async function openSettingsModal() {
    closeAllProfileDropdowns();
    let modalEl = document.getElementById('pephubSettingsModal');
    if (!modalEl) {
      modalEl = document.createElement('div');
      modalEl.id = 'pephubSettingsModal';
      modalEl.className = 'ph-modal-backdrop';
      document.body.appendChild(modalEl);
    }
    modalEl.style.display = 'flex';
    modalEl.innerHTML = `
      <div class="ph-modal-dialog">
        <div class="ph-modal-header">
          <div class="ph-modal-header-text">
            <small>Preferências & Notificações</small>
            <b>Configurações</b>
          </div>
          <button type="button" class="ph-modal-close-btn" id="btnCloseSettingsModal" aria-label="Fechar">&times;</button>
        </div>
        <div class="ph-modal-content" id="settingsModalContent">
          <div style="text-align:center;padding:36px 0;color:#64748b">Carregando configurações…</div>
        </div>
        <div class="ph-modal-actions" id="settingsModalActions">
          <button type="button" class="ph-btn-secondary" id="btnSettingsModalCancel">Fechar</button>
        </div>
      </div>
    `;

    const close = () => { modalEl.style.display = 'none'; };
    modalEl.querySelector('#btnCloseSettingsModal').onclick = close;
    modalEl.querySelector('#btnSettingsModalCancel').onclick = close;
    modalEl.onclick = (e) => { if (e.target === modalEl) close(); };

    try {
      const res = await fetch('/api/user/profile');
      if (!res.ok) throw new Error('Falha ao carregar preferências');
      const data = await res.json();
      renderSettingsForm(modalEl, data);
    } catch (_) {
      const cnt = modalEl.querySelector('#settingsModalContent');
      if (cnt) {
        cnt.innerHTML = `
          <div class="ph-notice-box" style="background:#fef2f2;border-color:#fecaca;color:#991b1b">
            Erro ao carregar configurações. Por favor, tente novamente.
          </div>
        `;
      }
    }
  }

  function renderSettingsForm(modalEl, data) {
    const user = data.user || {};
    const prefs = user.preferences || {};
    const accessible = data.accessible_modules || [];

    const updateFreq = prefs.update_frequency === 'specific' ? 'specific' : 'all';
    const monitoredList = Array.isArray(prefs.monitored_modules) ? prefs.monitored_modules : [];
    const notifyNew = prefs.notify_new_reports !== false; // Padrão: true

    const contentEl = modalEl.querySelector('#settingsModalContent');
    const actionsEl = modalEl.querySelector('#settingsModalActions');

    // Monta checkboxes dos relatórios acessíveis
    const checkboxesHtml = accessible.length === 0
      ? '<div style="color:#64748b;font-size:11.5px;padding:4px 0">Nenhum relatório atribuído no momento.</div>'
      : accessible.map(m => {
          const checked = monitoredList.includes(m.code) ? 'checked' : '';
          return `
            <label class="ph-check-label">
              <input type="checkbox" class="ph-module-check" value="${escapeHtml(m.code)}" ${checked}>
              <span>${escapeHtml(m.name)}</span>
            </label>
          `;
        }).join('');

    // Monta options de relatórios para o formulário de feedback
    const feedbackOptionsHtml = [
      '<option value="geral">Geral / Plataforma PEPHUB</option>',
      ...accessible.map(m => `<option value="${escapeHtml(m.code)}">${escapeHtml(m.name)}</option>`)
    ].join('');

    contentEl.innerHTML = `
      <div id="settingsFeedbackAlert"></div>

      <!-- Seção 1: Alertas de Atualização de Relatórios -->
      <div class="ph-settings-section">
        <div class="ph-settings-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          Alertas de Atualização de Relatórios
        </div>
        
        <label class="ph-radio-label">
          <input type="radio" name="opt_update_freq" value="all" id="radFreqAll" ${updateFreq === 'all' ? 'checked' : ''}>
          <div>
            <b>1 — Desejo receber alertas de atualização de todos os relatórios que possuo acesso</b>
            <div style="font-size:11.5px;color:#64748b;margin-top:2px">Notificar sempre que qualquer painel com meu acesso for atualizado pela equipe.</div>
          </div>
        </label>

        <label class="ph-radio-label" style="margin-top:12px">
          <input type="radio" name="opt_update_freq" value="specific" id="radFreqSpecific" ${updateFreq === 'specific' ? 'checked' : ''}>
          <div>
            <b>2 — Desejo receber alertas de atualização somente de:</b>
            <div style="font-size:11.5px;color:#64748b;margin-top:2px">Selecione abaixo individualmente os relatórios prioritários para monitorar:</div>
          </div>
        </label>

        <div class="ph-checkbox-grid" id="settingsModulesGrid" style="display:${updateFreq === 'specific' ? 'grid' : 'none'}">
          ${checkboxesHtml}
        </div>
      </div>

      <!-- Seção 2: Alertas de Novos Relatórios -->
      <div class="ph-settings-section">
        <div class="ph-settings-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          Lançamentos & Publicações
        </div>
        <label class="ph-check-label" style="font-size:12.5px;color:#1c2430">
          <input type="checkbox" id="chkNotifyNewReports" ${notifyNew ? 'checked' : ''}>
          <b>3 — Desejo receber alertas sobre novos relatórios publicados no PEPHUB</b>
        </label>
      </div>

      <!-- Seção 3: Informar Erro ou Fazer Comentário -->
      <div class="ph-settings-section">
        <div class="ph-settings-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          4 — Desejo informar um erro ou fazer um comentário
        </div>
        <div style="font-size:11.5px;color:#64748b;margin-bottom:12px">
          Sua mensagem será enviada por e-mail diretamente aos administradores da ferramenta e registrada para melhoria contínua da Regional Norte.
        </div>

        <div class="ph-form-grid" style="margin-top:0">
          <div>
            <label class="ph-label" for="fbType">Tipo de Comunicação</label>
            <select class="ph-select" id="fbType">
              <option value="bug">Informar um erro / Bug</option>
              <option value="feedback">Fazer um comentário / Elogio</option>
              <option value="duvida">Dúvida sobre os dados</option>
            </select>
          </div>
          <div>
            <label class="ph-label" for="fbModule">Relatório Relacionado</label>
            <select class="ph-select" id="fbModule">
              ${feedbackOptionsHtml}
            </select>
          </div>
          <div class="ph-form-group-full">
            <label class="ph-label" for="fbMessage">Mensagem / Descrição do Ocorrido</label>
            <textarea class="ph-textarea" id="fbMessage" rows="3" placeholder="Descreva os detalhes, cenário observado ou sugestão..."></textarea>
          </div>
          <div class="ph-form-group-full" style="text-align:right">
            <button type="button" class="ph-btn-secondary" id="btnSendFeedback">
              Enviar Mensagem ao Administrador
            </button>
          </div>
        </div>
      </div>
    `;

    // Interatividade do radio
    const radAll = contentEl.querySelector('#radFreqAll');
    const radSpecific = contentEl.querySelector('#radFreqSpecific');
    const gridEl = contentEl.querySelector('#settingsModulesGrid');

    const updateGridVisibility = () => {
      if (gridEl) gridEl.style.display = radSpecific.checked ? 'grid' : 'none';
    };
    radAll.onchange = updateGridVisibility;
    radSpecific.onchange = updateGridVisibility;

    // Ação de Enviar Feedback
    const btnFeedback = contentEl.querySelector('#btnSendFeedback');
    if (btnFeedback) {
      btnFeedback.onclick = async () => {
        const type = contentEl.querySelector('#fbType')?.value || 'bug';
        const module = contentEl.querySelector('#fbModule')?.value || 'geral';
        const msg = (contentEl.querySelector('#fbMessage')?.value || '').trim();

        if (!msg) {
          alert('Por favor, digite sua mensagem antes de enviar.');
          return;
        }

        btnFeedback.disabled = true;
        btnFeedback.textContent = 'Enviando comunicado…';

        try {
          const res = await fetch('/api/user/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, module, message: msg })
          });
          const resData = await res.json();
          if (!res.ok) throw new Error(resData.error || 'Erro ao enviar mensagem');

          contentEl.querySelector('#fbMessage').value = '';
          const alertEl = contentEl.querySelector('#settingsFeedbackAlert');
          if (alertEl) {
            alertEl.innerHTML = `<div class="ph-notice-box success">${escapeHtml(resData.message || 'Mensagem enviada com sucesso ao administrador!')}</div>`;
          }
        } catch (err) {
          alert(err.message || 'Erro ao enviar feedback.');
        } finally {
          btnFeedback.disabled = false;
          btnFeedback.textContent = 'Enviar Mensagem ao Administrador';
        }
      };
    }

    // Botões de Ação do Rodapé (Salvar Preferências)
    actionsEl.innerHTML = `
      <button type="button" class="ph-btn-secondary" id="btnSettingsCloseBottom">Fechar</button>
      <button type="button" class="ph-btn-primary" id="btnSavePreferences">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Salvar Preferências
      </button>
    `;

    actionsEl.querySelector('#btnSettingsCloseBottom').onclick = () => { modalEl.style.display = 'none'; };
    actionsEl.querySelector('#btnSavePreferences').onclick = async () => {
      const isSpecific = radSpecific.checked;
      const checkedModules = [];
      if (isSpecific) {
        contentEl.querySelectorAll('.ph-module-check:checked').forEach(c => checkedModules.push(c.value));
      }
      const notifyNewReports = !!contentEl.querySelector('#chkNotifyNewReports')?.checked;

      const btnSave = actionsEl.querySelector('#btnSavePreferences');
      btnSave.disabled = true;
      btnSave.textContent = 'Salvando…';

      try {
        const res = await fetch('/api/user/preferences', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            update_frequency: isSpecific ? 'specific' : 'all',
            monitored_modules: checkedModules,
            notify_new_reports: notifyNewReports
          })
        });
        const resData = await res.json();
        if (!res.ok) throw new Error(resData.error || 'Falha ao salvar preferências');

        const alertEl = contentEl.querySelector('#settingsFeedbackAlert');
        if (alertEl) {
          alertEl.innerHTML = `<div class="ph-notice-box success">Preferências de notificação salvas com sucesso!</div>`;
        }
        setTimeout(() => { modalEl.style.display = 'none'; }, 900);
      } catch (err) {
        alert(err.message || 'Erro ao salvar preferências.');
      } finally {
        if (btnSave) {
          btnSave.disabled = false;
          btnSave.textContent = 'Salvar Preferências';
        }
      }
    };
  }

  // Atualiza widgets de profile ativos na tela quando o usuário salva foto ou nome
  function updateProfileWidgetsUI(user) {
    if (!user) return;
    const firstName = user.nome_completo ? user.nome_completo.split(' ')[0] : 'Perfil';
    const initials = getInitials(user.nome_completo);

    document.querySelectorAll('.ph-profile-wrapper').forEach(wrapper => {
      const btnAvatar = wrapper.querySelector('#phProfileBtnAvatar');
      const btnName = wrapper.querySelector('#phProfileBtnName');
      const dropAvatar = wrapper.querySelector('#phDropdownBigAvatar');
      const dropName = wrapper.querySelector('#phDropdownUserName');
      const dropEmail = wrapper.querySelector('#phDropdownUserEmail');

      if (btnAvatar) {
        if (user.foto) {
          btnAvatar.innerHTML = `<img src="${escapeHtml(user.foto)}" alt="${escapeHtml(user.nome_completo)}">`;
        } else {
          btnAvatar.textContent = initials;
        }
      }
      if (btnName) btnName.textContent = firstName;
      if (dropAvatar) {
        if (user.foto) {
          dropAvatar.innerHTML = `<img src="${escapeHtml(user.foto)}" alt="${escapeHtml(user.nome_completo)}">`;
        } else {
          dropAvatar.textContent = initials;
        }
      }
      if (dropName) dropName.textContent = user.nome_completo || 'Colaborador';
      if (dropEmail) dropEmail.textContent = user.email_claro || '';
    });
  }

  // ------------------------------------------------------------------
  // Montagem do Profile Widget no Header
  // ------------------------------------------------------------------
  window.pephubMountProfileWidget = async function(host) {
    if (!host || host.dataset.pephubProfileMounted === '1') return;
    host.dataset.pephubProfileMounted = '1';

    let user = await getMe();
    if (!user || !user.authenticated) return;

    const firstName = user.nome_completo ? user.nome_completo.split(' ')[0] : 'Perfil';
    const initials = getInitials(user.nome_completo);
    const avatarInner = user.foto
      ? `<img src="${escapeHtml(user.foto)}" alt="${escapeHtml(user.nome_completo)}">`
      : escapeHtml(initials);

    host.innerHTML = `
      <div class="ph-profile-wrapper">
        <button type="button" class="ph-profile-btn" id="btnHeaderProfile" aria-haspopup="true" aria-expanded="false" title="Opções de Conta & Perfil">
          <div class="ph-profile-avatar" id="phProfileBtnAvatar">${avatarInner}</div>
          <span class="ph-profile-name" id="phProfileBtnName">${escapeHtml(firstName)}</span>
          <svg class="ph-profile-chevron" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="ph-profile-dropdown" id="phProfileDropdown" role="menu">
          <div class="ph-dropdown-header">
            <div class="ph-dropdown-big-avatar" id="phDropdownBigAvatar">${avatarInner}</div>
            <div class="ph-dropdown-user-info">
              <div class="ph-dropdown-user-name" id="phDropdownUserName">${escapeHtml(user.nome_completo || 'Colaborador')}</div>
              <div class="ph-dropdown-user-email" id="phDropdownUserEmail">${escapeHtml(user.email_claro || '')}</div>
              <span class="ph-dropdown-user-badge ${user.is_admin ? 'admin' : ''}" id="phDropdownUserBadge">
                ${user.is_admin ? 'Administrador' : 'Colaborador'}
              </span>
            </div>
          </div>
          <div class="ph-dropdown-menu-list">
            <button type="button" class="ph-dropdown-item" id="phMenuItemProfile">
              <svg class="ph-dropdown-item-icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <div class="ph-dropdown-item-texts">
                <div class="ph-dropdown-item-title">1 — Perfil</div>
                <div class="ph-dropdown-item-subtitle">Dados cadastrais e foto</div>
              </div>
            </button>
            <button type="button" class="ph-dropdown-item" id="phMenuItemSettings">
              <svg class="ph-dropdown-item-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <div class="ph-dropdown-item-texts">
                <div class="ph-dropdown-item-title">2 — Configurações</div>
                <div class="ph-dropdown-item-subtitle">Alertas e reporte de erro</div>
              </div>
            </button>
            <div class="ph-dropdown-divider"></div>
            <button type="button" class="ph-dropdown-item logout" id="phMenuItemLogout">
              <svg class="ph-dropdown-item-icon" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              <div class="ph-dropdown-item-texts">
                <div class="ph-dropdown-item-title">3 — Sair</div>
                <div class="ph-dropdown-item-subtitle">Encerrar sessão de forma segura</div>
              </div>
            </button>
          </div>
        </div>
      </div>
    `;

    const wrapper = host.querySelector('.ph-profile-wrapper');
    const btn = host.querySelector('#btnHeaderProfile');
    const dropdown = host.querySelector('#phProfileDropdown');

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains('show');
      closeAllProfileDropdowns();
      if (!isOpen) {
        dropdown.classList.add('show');
        wrapper.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      } else {
        btn.setAttribute('aria-expanded', 'false');
      }
    });

    host.querySelector('#phMenuItemProfile').addEventListener('click', (e) => {
      e.stopPropagation();
      openProfileModal();
    });

    host.querySelector('#phMenuItemSettings').addEventListener('click', (e) => {
      e.stopPropagation();
      openSettingsModal();
    });

    host.querySelector('#phMenuItemLogout').addEventListener('click', (e) => {
      e.stopPropagation();
      closeAllProfileDropdowns();
      handleLogout();
    });
  };

  // ------------------------------------------------------------------
  // Cabeçalho dos relatórios (Universal)
  // Substitui botão sair solto pelo botão corporativo de profile
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
          <span data-pephub-profile></span>
        `;
        window.pephubMountNotificationsWidget(container.querySelector('[data-pephub-notifications]'));
        window.pephubMountOnlineWidget(container.querySelector('[data-pephub-online]'));
        window.pephubMountProfileWidget(container.querySelector('[data-pephub-profile]'));
      } else {
        container.innerHTML = `
          <span data-pephub-notifications></span>
          <span data-pephub-profile></span>
        `;
        window.pephubMountNotificationsWidget(container.querySelector('[data-pephub-notifications]'));
        window.pephubMountProfileWidget(container.querySelector('[data-pephub-profile]'));
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

    // 1. Notificações
    const notifHosts = document.querySelectorAll('[data-pephub-notifications]');
    if (notifHosts.length) {
      getMe().then(me => {
        if ((me && me.authenticated) || window.location.pathname.startsWith('/admin')) {
          notifHosts.forEach(h => window.pephubMountNotificationsWidget(h));
        }
      }).catch(() => {
        if (window.location.pathname.startsWith('/admin')) {
          notifHosts.forEach(h => window.pephubMountNotificationsWidget(h));
        }
      });
    }

    // 2. Online
    const onlineHosts = document.querySelectorAll('[data-pephub-online]');
    if (onlineHosts.length) {
      getMe().then(me => {
        if ((me && me.authenticated && me.is_admin) || window.location.pathname.startsWith('/admin')) {
          onlineHosts.forEach(h => window.pephubMountOnlineWidget(h));
        }
      }).catch(() => {
        if (window.location.pathname.startsWith('/admin')) {
          onlineHosts.forEach(h => window.pephubMountOnlineWidget(h));
        }
      });
    }

    // 3. Profile Widget em hosts explícitos
    const profileHosts = document.querySelectorAll('[data-pephub-profile]');
    if (profileHosts.length) {
      profileHosts.forEach(h => window.pephubMountProfileWidget(h));
    }

    // 4. Migração e auto-substituição de botões legados de Sair (#btnLogoutPortal, #btnLogout)
    getMe().then(me => {
      if (me && me.authenticated) {
        const legacyButtons = document.querySelectorAll('#btnLogoutPortal, #btnLogout');
        legacyButtons.forEach(btn => {
          const parent = btn.parentElement;
          if (!parent) return;
          if (parent.querySelector('[data-pephub-profile]') || parent.querySelector('.ph-profile-wrapper')) {
            btn.remove();
          } else {
            const host = document.createElement('span');
            host.setAttribute('data-pephub-profile', '');
            parent.replaceChild(host, btn);
            window.pephubMountProfileWidget(host);
          }
        });
      }
    }).catch(() => {});
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoInit);
  else autoInit();
})();

