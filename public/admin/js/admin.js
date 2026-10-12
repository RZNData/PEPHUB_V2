// Módulos e Ferramentas oficiais organizados por seção canônica (Regional Norte)
// Inicializado com os módulos canônicos e atualizado dinamicamente via D1
let SYSTEM_SECTIONS = [
  {
    "name": "Painéis & Relatórios Oficiais",
    "key": "paineis_e_relatorios_oficiais",
    "modules": [
      {
        "id": "churn",
        "name": "Painel de Churn Safra",
        "short": "Safra",
        "desc": "Acompanhamento de Churn Safra da Regional Norte"
      },
      {
        "id": "churn-bl-total",
        "name": "Painel de Churn Banda Larga Total",
        "short": "BL Total",
        "desc": "Acompanhamento de Churn Horizontal BL Total (Residencial + PME)"
      },
      {
        "id": "churn-bl-pme",
        "name": "Painel de Churn Banda Larga PME",
        "short": "BL PME",
        "desc": "Acompanhamento de Churn Horizontal BL PME"
      },
      {
        "id": "fpd",
        "name": "Painel de FPD 60/30 (First Payment Default)",
        "short": "FPD Regional",
        "desc": "Inadimplência de primeira fatura (FPD 30 e FPD 60)"
      },
      {
        "id": "fpd-residencial",
        "name": "FPD Residencial (Executivo Fixa)",
        "short": "FPD Residencial",
        "desc": "Relatório Executivo Oficial de FPD 60 da Fixa por Canal, Cidade e Parceiro"
      },
      {
        "id": "market-share-movel",
        "name": "Market Share Móvel",
        "short": "MS Móvel",
        "desc": "Relatório Executivo Oficial de Market Share Móvel (Anatel · Telefonia Móvel & 5G)"
      },
      {
        "id": "market-share-residencial",
        "name": "Market Share Residencial",
        "short": "MS Residencial",
        "desc": "Relatório Executivo Oficial de Market Share Residencial (Anatel · Banda Larga)"
      },
      {
        "id": "panorama-market-share",
        "name": "Panorama & Market Share",
        "short": "Panorama",
        "desc": "Market share móvel e residencial Anatel e dinâmica concorrencial"
      },
      {
        "id": "aprovacao-credito",
        "name": "Painel de Taxa de Aprovação de Crédito",
        "short": "Taxa Crédito",
        "desc": "Taxa de aprovação por canal, parceiro e cidade"
      },
      {
        "id": "evolucao-carteira",
        "name": "Evolução de Carteira Móvel & B2B",
        "short": "Evolução Carteira",
        "desc": "Evolução temporal, net adds, desdobramento por segmento e migrações da Regional Norte"
      }
    ]
  },
  {
    "name": "PeP Tools & Operações",
    "key": "pep_tools___opera__es",
    "modules": [
      {
        "id": "divulgacao",
        "name": "Divulgação Corporativa (TVs)",
        "short": "TV Divulgação",
        "desc": "Propostas de mídia, curadoria e exibição nas TVs da Regional"
      },
      {
        "id": "tv",
        "name": "Player TV (16:9 Fullscreen)",
        "short": "Player TV",
        "desc": "Acesso direto ao reprodutor widescreen para recepções e salas"
      }
    ]
  }
];

let ALL_SYSTEM_MODULES = SYSTEM_SECTIONS.flatMap(s => s.modules);
let ALL_MODULE_IDS = ALL_SYSTEM_MODULES.map(m => m.id);
let REPORT_MODULES = ALL_SYSTEM_MODULES;

function isPepToolsModule(m) {
  if (!m) return false;
  const sec = (m.section || '').toLowerCase();
  const id = (m.id || '').toLowerCase();
  return sec.includes('pep') || sec.includes('ferramenta') || id === 'divulgacao' || id === 'tv';
}

function updateSystemCatalog(modules) {
  if (!Array.isArray(modules) || modules.length === 0) return;
  const sectionsMap = new Map();
  
  // Garante as duas seções canônicas iniciais
  sectionsMap.set('Painéis & Relatórios Oficiais', {
    name: 'Painéis & Relatórios Oficiais',
    key: 'paineis_e_relatorios_oficiais',
    modules: []
  });
  sectionsMap.set('PeP Tools & Operações', {
    name: 'PeP Tools & Operações',
    key: 'pep_tools___opera__es',
    modules: []
  });

  modules.forEach(m => {
    let secName = m.section || 'Painéis & Relatórios Oficiais';
    const cleanId = normalizeModuleId(m.id);
    if (cleanId === 'divulgacao' || cleanId === 'tv' || secName.toLowerCase().includes('pep') || secName.toLowerCase().includes('ferramenta')) {
      secName = 'PeP Tools & Operações';
    } else if (secName.toLowerCase().includes('painel') || secName.toLowerCase().includes('relat') || secName.toLowerCase().includes('indicador') || secName.toLowerCase().includes('estrat')) {
      secName = 'Painéis & Relatórios Oficiais';
    }

    if (!sectionsMap.has(secName)) {
      sectionsMap.set(secName, {
        name: secName,
        key: secName.toLowerCase().replace(/[^a-z0-9]/g, '_'),
        modules: []
      });
    }

    sectionsMap.get(secName).modules.push({
      id: cleanId,
      name: m.name,
      short: m.short_name || m.name,
      desc: m.description || '',
      section: secName,
      route: m.route,
      status: m.status || 'ativo',
      sort_order: m.sort_order || 0
    });
  });

  // Filtra seções que tenham pelo menos 1 módulo
  SYSTEM_SECTIONS = Array.from(sectionsMap.values()).filter(s => s.modules.length > 0);
  ALL_SYSTEM_MODULES = SYSTEM_SECTIONS.flatMap(s => s.modules);
  ALL_MODULE_IDS = ALL_SYSTEM_MODULES.map(m => m.id);
  REPORT_MODULES = ALL_SYSTEM_MODULES;
  
  populateBroadcastReports();
  populateDelegationScopeSelect();
}

function populateBroadcastReports() {
  const sel = document.getElementById('bcReport');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = '<option value="Todos os Relatórios & Plataforma Pephub">Todos os Relatórios &amp; Plataforma Pephub</option>' +
    ALL_SYSTEM_MODULES.map(m => `<option value="${escapeHtml(m.name)}">${escapeHtml(m.name)} (${escapeHtml(m.short)})</option>`).join('');
  if (currentVal) sel.value = currentVal;
}

function populateDelegationScopeSelect() {
  const sel = document.getElementById('delegationScopeSelect');
  if (!sel) return;
  const currentVal = sel.value;
  let html = '<option value="ALL">Todos os Relatórios &amp; Insumos (Geral)</option>';
  ALL_SYSTEM_MODULES.forEach(m => {
    html += `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`;
  });
  html += '<option value="bot-knowledge">Base de Regras do Bot RAG</option>';
  sel.innerHTML = html;
  if (currentVal) sel.value = currentVal;
}

let allUsers = [];
let allControls = [];
let allModules = [];
let allProfileFields = [];
let activeUserFilter = 'all';
let activeLogActionFilter = 'all';

// Filtro de data do Dashboard
let statsDateFilter = {
  preset: '30d',
  startDate: '',
  endDate: ''
};

// Navegação de Abas
const tabUsersBtn = document.getElementById('tabUsersBtn');
const tabNotificationsBtn = document.getElementById('tabNotificationsBtn');
const tabStatsBtn = document.getElementById('tabStatsBtn');
const tabLogsBtn = document.getElementById('tabLogsBtn');
const tabControlsBtn = document.getElementById('tabControlsBtn');
const tabModulesBtn = document.getElementById('tabModulesBtn');
const tabUploadsBtn = document.getElementById('tabUploadsBtn');
const tabRequestsBtn = document.getElementById('tabRequestsBtn');

const sectionUsers = document.getElementById('sectionUsers');
const sectionNotifications = document.getElementById('sectionNotifications');
const sectionStats = document.getElementById('sectionStats');
const sectionLogs = document.getElementById('sectionLogs');
const sectionControls = document.getElementById('sectionControls');
const sectionModules = document.getElementById('sectionModules');
const sectionUploads = document.getElementById('sectionUploads');
const sectionRequests = document.getElementById('sectionRequests');

function showTab(tab) {
  closeActionMenu();
  [tabUsersBtn, tabRequestsBtn, tabNotificationsBtn, tabStatsBtn, tabLogsBtn, tabControlsBtn, tabModulesBtn, tabUploadsBtn].filter(Boolean).forEach(b => b.classList.remove('active'));
  [sectionUsers, sectionRequests, sectionNotifications, sectionStats, sectionLogs, sectionControls, sectionModules, sectionUploads].filter(Boolean).forEach(s => s.style.display = 'none');

  if (tab === 'users') {
    tabUsersBtn.classList.add('active');
    sectionUsers.style.display = 'block';
    loadUsers();
  } else if (tab === 'requests') {
    tabRequestsBtn.classList.add('active');
    sectionRequests.style.display = 'block';
    loadAccessRequests();
  } else if (tab === 'notifications') {
    if (tabNotificationsBtn) tabNotificationsBtn.classList.add('active');
    if (sectionNotifications) sectionNotifications.style.display = 'block';
    loadAdminNotifications();
  } else if (tab === 'stats') {
    tabStatsBtn.classList.add('active');
    sectionStats.style.display = 'block';
    loadAccessStats();
  } else if (tab === 'logs') {
    tabLogsBtn.classList.add('active');
    sectionLogs.style.display = 'block';
    loadAccessLogs();
  } else if (tab === 'controls') {
    tabControlsBtn.classList.add('active');
    sectionControls.style.display = 'block';
    loadSystemControls();
    loadProfileFields();
  } else if (tab === 'modules') {
    tabModulesBtn.classList.add('active');
    sectionModules.style.display = 'block';
    loadModules();
  } else if (tab === 'uploads') {
    tabUploadsBtn.classList.add('active');
    sectionUploads.style.display = 'block';
    loadUploadsConfig();
  }
}

tabUsersBtn.addEventListener('click', () => showTab('users'));
if (tabNotificationsBtn) tabNotificationsBtn.addEventListener('click', () => showTab('notifications'));
tabRequestsBtn.addEventListener('click', () => showTab('requests'));
tabStatsBtn.addEventListener('click', () => showTab('stats'));
tabLogsBtn.addEventListener('click', () => showTab('logs'));
tabControlsBtn.addEventListener('click', () => showTab('controls'));
tabModulesBtn.addEventListener('click', () => showTab('modules'));
tabUploadsBtn.addEventListener('click', () => showTab('uploads'));

// Logout Seguro e Direto
document.getElementById('btnLogout').addEventListener('click', async () => {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
  } catch (_) {}
  window.location.href = '/login/';
});

// Fechar modais
document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const modalId = e.currentTarget.dataset.close;
    if (modalId) document.getElementById(modalId).classList.remove('on');
  });
});

function normalizeModuleId(id) {
  if (!id) return '';
  const clean = String(id).trim().toLowerCase();
  if (clean === 'churn' || clean === 'churn_safra' || clean === 'churn-safra') return 'churn';
  if (clean === 'churn-bl-total' || clean === 'churn_bl_total' || clean === 'bl-total') return 'churn-bl-total';
  if (clean === 'churn-bl-pme' || clean === 'churn_bl_pme' || clean === 'bl-pme') return 'churn-bl-pme';
  if (clean === 'fpd' || clean === 'fpd_regional_norte' || clean === 'fpd-regional-norte') return 'fpd';
  if (clean === 'fpd-residencial' || clean === 'fpd_residencial' || clean === 'fpd-executivo') return 'fpd-residencial';
  if (clean === 'divulgacao' || clean === 'pep_tools_divulgacao' || clean === 'peptools_divulgacao') return 'divulgacao';
  if (clean === 'tv' || clean === 'player_tv' || clean === 'tv_player') return 'tv';
  if (clean === 'panorama-market-share' || clean === 'panorama_market_share' || clean === 'market-share-panorama') return 'panorama-market-share';
  if (clean === 'market-share-residencial' || clean === 'market_share_residencial' || clean === 'mkt-share-residencial') return 'market-share-residencial';
  if (clean === 'market-share-movel' || clean === 'market_share_movel' || clean === 'mkt-share-movel') return 'market-share-movel';
  if (clean === 'aprovacao-credito' || clean === 'aprovacao_credito' || clean === 'credito') return 'aprovacao-credito';
  return clean;
}

// Helper: Extrair lista de módulos de um usuário (interpretação estrita de permissões)
function getUserModules(u) {
  if (u.is_admin || u.modules_allowed === 'all') {
    return [...ALL_MODULE_IDS];
  }
  if (!u.modules_allowed || u.modules_allowed === 'none' || String(u.modules_allowed).trim() === '') {
    return [];
  }
  return u.modules_allowed.split(',').map(normalizeModuleId).filter(Boolean);
}

// Helper: Iniciais do nome
function getInitials(name) {
  if (!name) return 'CL';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

// Helper: Converter timestamps UTC do SQLite/Worker para objeto Date correto no navegador
function parseUtcDate(dateStr) {
  if (!dateStr) return null;
  if (dateStr instanceof Date) return dateStr;
  const s = String(dateStr).trim();
  if (s.endsWith('Z') || s.includes('+')) return new Date(s);
  return new Date(s.replace(' ', 'T') + 'Z');
}

// Helper: Formatar data relativa com fuso oficial de Brasília (UTC-3)
function formatRelativeTime(dateStr) {
  if (!dateStr) return 'Nunca';
  try {
    const d = parseUtcDate(dateStr);
    if (!d || isNaN(d.getTime())) return dateStr;
    const now = new Date();
    const diffMin = Math.round((now - d) / 60000);
    if (diffMin < 2 && diffMin >= -2) return 'Agora mesmo';
    if (diffMin > 0 && diffMin < 60) return `Há ${diffMin} min`;
    const diffHours = Math.round(diffMin / 60);
    const timeStr = d.toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit' });
    if (diffHours < 24 && diffHours >= 0) return `Hoje às ${timeStr}`;
    if (diffHours < 48 && diffHours >= 24) return `Ontem às ${timeStr}`;
    const dateStrFormatted = d.toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit' });
    return `${dateStrFormatted} às ${timeStr}`;
  } catch (_) {
    return dateStr;
  }
}

// Helper: Formatar data curta com fuso oficial de Brasília (UTC-3)
function formatDateShort(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = parseUtcDate(dateStr);
    if (!d || isNaN(d.getTime())) return '—';
    return d.toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  } catch (_) {
    return '—';
  }
}

// ==========================================
// 1. CARREGAR E RENDERIZAR USUÁRIOS
// ==========================================
async function loadUsers() {
  try {
    const [resUsers, resModules] = await Promise.all([
      fetch('/api/admin/users'),
      fetch('/api/admin/modules')
    ]);

    if (resUsers.status === 401 || resUsers.status === 403) {
      window.location.href = '/login/?redirect=/admin/';
      return;
    }
    const dataUsers = await resUsers.json();
    if (!resUsers.ok || !Array.isArray(dataUsers)) {
      throw new Error((dataUsers && dataUsers.error) ? dataUsers.error : 'Resposta inválida do servidor.');
    }
    allUsers = dataUsers;

    if (resModules.ok) {
      const dataModules = await resModules.json();
      if (Array.isArray(dataModules) && dataModules.length > 0) {
        allModules = dataModules;
        updateSystemCatalog(dataModules);
      }
    }

    renderUsers();
    populateDelegationUserSelect();
  } catch (err) {
    document.getElementById('usersTbody').innerHTML = `
      <tr><td colspan="6" style="text-align:center;color:var(--red);padding:20px">Erro ao carregar lista de usuários: ${escapeHtml(err.message)}</td></tr>
    `;
  }
}

function renderUsers() {
  const tbody = document.getElementById('usersTbody');
  const search = document.getElementById('searchUsers').value.trim().toLowerCase();

  const countPending = allUsers.filter(u => u.status === 'pendente').length;
  const countApproved = allUsers.filter(u => u.status === 'aprovado').length;
  const countBlocked = allUsers.filter(u => u.status === 'bloqueado' || u.status === 'rejeitado').length;
  const countActive = allUsers.filter(u => (u.total_accesses || 0) > 0).length;
  const countExport = allUsers.filter(u => (u.total_exports || 0) > 0).length;

  document.getElementById('totalUsersCount').textContent = allUsers.length;
  document.getElementById('countPending').textContent = countPending;
  document.getElementById('countApproved').textContent = countApproved;
  document.getElementById('countBlocked').textContent = countBlocked;

  document.getElementById('kpiTotalUsers').textContent = allUsers.length;
  document.getElementById('kpiApprovedUsers').textContent = countApproved;
  document.getElementById('kpiPendingUsers').textContent = countPending;
  document.getElementById('kpiActiveUsers').textContent = countActive;
  document.getElementById('kpiExportUsers').textContent = countExport;

  let filtered = allUsers;
  if (activeUserFilter === 'pendente') filtered = filtered.filter(u => u.status === 'pendente');
  else if (activeUserFilter === 'aprovado') filtered = filtered.filter(u => u.status === 'aprovado');
  else if (activeUserFilter === 'bloqueado') filtered = filtered.filter(u => u.status === 'bloqueado' || u.status === 'rejeitado');

  if (search) {
    filtered = filtered.filter(u => 
      (u.nome_completo || '').toLowerCase().includes(search) ||
      (u.login_claro || '').toLowerCase().includes(search) ||
      (u.email_claro || '').toLowerCase().includes(search) ||
      (u.area || '').toLowerCase().includes(search) ||
      (u.funcao || '').toLowerCase().includes(search)
    );
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--ink3);padding:24px">Nenhum colaborador encontrado com os filtros aplicados.</td></tr>`;
    return;
  }

  const totalCatalogMods = ALL_SYSTEM_MODULES.length;

  tbody.innerHTML = filtered.map(u => {
    const isPending = u.status === 'pendente';
    const isApproved = u.status === 'aprovado';
    const isBlocked = u.status === 'bloqueado' || u.status === 'rejeitado';
    const hasTempPwd = Boolean(u.must_change_password);
    const initials = getInitials(u.nome_completo);
    const userMods = getUserModules(u);
    const totalAcc = u.total_accesses || 0;
    const totalExp = u.total_exports || 0;

    return `
      <tr>
        <td>
          <div class="u-cell">
            <div class="u-avatar" title="${escapeHtml(u.nome_completo)}">${initials}</div>
            <div>
              <div style="font-weight:700;color:var(--ink)">${escapeHtml(u.nome_completo)}</div>
              <div style="font-size:11px;color:var(--ink3);display:flex;align-items:center;gap:6px;margin-top:1px">
                <span>Login: <code>${escapeHtml(u.login_claro)}</code></span>
                ${u.telefone ? `<a href="https://wa.me/${u.telefone}" target="_blank" style="color:#2f7d5d;text-decoration:none;font-weight:600" title="WhatsApp Corporativo">Tel: ${escapeHtml(u.telefone)}</a>` : ''}
              </div>
              <div style="font-family:Consolas,monospace;font-size:10.5px;color:var(--ink3);margin-top:1px">${escapeHtml(u.email_claro)}</div>
            </div>
          </div>
        </td>
        <td>
          <div style="font-weight:600;color:var(--ink)">${escapeHtml(u.area || 'OUTROS')}</div>
          <div style="color:var(--ink3);font-size:11px">${escapeHtml(u.funcao || 'COLABORADOR')}</div>
          <div style="color:var(--ink3);font-size:10px;margin-top:2px">Desde ${formatDateShort(u.created_at)}</div>
        </td>
        <td>
          ${u.is_admin ? `
            <span class="badge admin" style="display:inline-flex;align-items:center;gap:4px;padding:4px 8px;font-size:10.5px">
              Acesso Irrestrito (Admin)
            </span>
          ` : `
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
              ${userMods.length === totalCatalogMods && totalCatalogMods > 0 ? `
                <span class="badge aprovado" style="font-size:10.5px;font-weight:700">Acesso Total (${userMods.length})</span>
              ` : userMods.length === 0 ? `
                <span class="badge bloqueado" style="font-size:10.5px">Nenhum autorizado</span>
              ` : `
                <span class="badge aprovado" style="font-size:10.5px">${userMods.length} de ${totalCatalogMods} autorizados</span>
              `}
            </div>
          `}
        </td>
        <td>
          <div style="display:flex;align-items:center;gap:5px;flex-wrap:wrap">
            <span class="badge ${totalAcc > 0 ? 'aprovado' : 'colab'}" style="font-size:10px">
              ${totalAcc} ${totalAcc === 1 ? 'acesso' : 'acessos'}
            </span>
            ${totalExp > 0 ? `<span class="badge-export-yes" title="${totalExp} exportações registradas">${totalExp} exp.</span>` : '<span class="badge-export-no">0 exp.</span>'}
          </div>
          <div style="color:var(--ink2);font-size:10.5px;margin-top:3px">
            ${u.last_access ? `Último: ${formatRelativeTime(u.last_access)}` : '<span style="color:var(--ink3)">Sem acessos</span>'}
          </div>
        </td>
        <td>
          <div style="display:flex;flex-direction:column;gap:3px;align-items:flex-start">
            <div style="display:flex;align-items:center;gap:4px">
              <span class="badge ${u.status}">${u.status}</span>
              ${Boolean(u.is_online) ? '<span class="badge online" style="background:#dcfce7;color:#15803d;border:1px solid #86efac;font-size:10px;font-weight:700">🟢 Online</span>' : '<span class="badge offline" style="background:#f1f5f9;color:#64748b;font-size:10px">⚪ Offline</span>'}
            </div>
            <span class="badge ${u.is_admin ? 'admin' : 'colab'}">${u.is_admin ? 'Admin' : 'Colaborador'}</span>
            ${hasTempPwd ? '<span class="badge temp-pwd" title="Senha provisória pendente de troca no primeiro login">Trocar Senha</span>' : ''}
          </div>
        </td>
        <td>
          <div class="actions-cell">
            <button type="button" class="act-trigger" data-user-id="${u.id}" onclick="toggleActionMenu(event, '${u.id}')" aria-haspopup="true" title="Ações disponíveis para este colaborador">
              Ações
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// ==========================================
// MENU DROPDOWN DE AÇÕES DO COLABORADOR
// ==========================================
let _actionMenuEl = null;
let _actionMenuTrigger = null;

function closeActionMenu() {
  if (_actionMenuEl) { _actionMenuEl.remove(); _actionMenuEl = null; }
  if (_actionMenuTrigger) { _actionMenuTrigger.classList.remove('open'); _actionMenuTrigger = null; }
}

function actionMenuItems(u) {
  const ico = (d) => `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const isPending = u.status === 'pendente';
  const isApproved = u.status === 'aprovado';
  const isBlocked = u.status === 'bloqueado' || u.status === 'rejeitado';
  const items = [
    { label: 'Privilégios', cls: 'strong', icon: ico('<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'), run: () => openPrivilegesModal(u.id) },
  ];
  if (isPending) items.push({ label: 'Aprovar cadastro', cls: 'ok', icon: ico('<polyline points="20 6 9 17 4 12"/>'), run: () => quickStatus(u.id, 'aprovado') });
  if (isApproved) items.push({ label: 'Bloquear acesso', cls: 'danger', icon: ico('<circle cx="12" cy="12" r="10"/><line x1="4.9" y1="4.9" x2="19.1" y2="19.1"/>'), run: () => quickStatus(u.id, 'bloqueado') });
  if (isBlocked) items.push({ label: 'Reativar acesso', cls: 'ok', icon: ico('<polyline points="20 6 9 17 4 12"/>'), run: () => quickStatus(u.id, 'aprovado') });
  items.push({ label: 'Editar dados', icon: ico('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>'), run: () => openEditUserModal(u.id) });
  items.push({ label: 'Resetar senha', icon: ico('<path d="M21 2l-2 2m-7.6 7.6a5.5 5.5 0 1 1-7.8 7.8 5.5 5.5 0 0 1 7.8-7.8zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>'), run: () => resetUserPassword(u.id) });
  if (!u.is_admin) {
    items.push({ divider: true });
    items.push({ label: 'Excluir colaborador', cls: 'danger', icon: ico('<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/>'), run: () => deleteUser(u.id, u.nome_completo) });
  }
  return items;
}

function toggleActionMenu(ev, userId) {
  ev.stopPropagation();
  const trigger = ev.currentTarget;
  const alreadyOpen = _actionMenuTrigger === trigger;
  closeActionMenu();
  if (alreadyOpen) return;

  const u = allUsers.find(x => String(x.id) === String(userId));
  if (!u) return;

  const menu = document.createElement('div');
  menu.className = 'act-menu';
  menu.setAttribute('role', 'menu');
  actionMenuItems(u).forEach(it => {
    if (it.divider) { menu.appendChild(document.createElement('hr')); return; }
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'menuitem');
    if (it.cls) b.className = it.cls;
    b.innerHTML = it.icon + '<span>' + it.label + '</span>';
    b.onclick = (e) => { e.stopPropagation(); closeActionMenu(); it.run(); };
    menu.appendChild(b);
  });
  document.body.appendChild(menu);

  // Posiciona abaixo do botão (alinhado à direita); inverte para cima se faltar espaço
  const r = trigger.getBoundingClientRect();
  const mh = menu.offsetHeight;
  const mw = menu.offsetWidth;
  let top = r.bottom + 4;
  if (top + mh > window.innerHeight - 8) top = Math.max(8, r.top - mh - 4);
  let left = Math.min(Math.max(8, r.right - mw), window.innerWidth - mw - 8);
  menu.style.top = top + 'px';
  menu.style.left = left + 'px';

  trigger.classList.add('open');
  _actionMenuEl = menu;
  _actionMenuTrigger = trigger;
}

document.addEventListener('click', (e) => { if (_actionMenuEl && !_actionMenuEl.contains(e.target)) closeActionMenu(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeActionMenu(); });
window.addEventListener('resize', closeActionMenu);
window.addEventListener('scroll', closeActionMenu, true);

// ==========================================
// SOLICITAÇÕES DE ACESSO A RELATÓRIOS
// ==========================================
let accessRequestsFilter = 'pendente';

async function loadAccessRequests() {
  const tbody = document.getElementById('requestsTbody');
  try {
    const res = await fetch('/api/admin/access-requests?status=' + encodeURIComponent(accessRequestsFilter));
    if (res.status === 401 || res.status === 403) { window.location.href = '/login/?redirect=/admin/'; return; }
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Resposta inválida do servidor.');
    updatePendingRequestsBadge(data.pending || 0);
    const rows = data.requests || [];
    if (rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--ink3);padding:24px">${accessRequestsFilter === 'pendente' ? 'Nenhuma solicitação pendente.' : 'Nenhuma solicitação registrada.'}</td></tr>`;
      return;
    }
    tbody.innerHTML = rows.map(r => {
      const pending = r.status === 'pendente';
      return `
        <tr>
          <td>${formatDateShort(r.created_at)}<div style="color:var(--ink3);font-size:10.5px">${formatRelativeTime(r.created_at)}</div></td>
          <td>
            <div style="font-weight:700;color:var(--ink)">${escapeHtml(r.user_name)}</div>
            <div style="font-family:Consolas,monospace;font-size:10.5px;color:var(--ink3)">${escapeHtml(r.user_email)}</div>
            <div style="font-size:10.5px;color:var(--ink3)">${escapeHtml(r.user_area || '')}${r.user_funcao ? ' · ' + escapeHtml(r.user_funcao) : ''}</div>
          </td>
          <td><strong>${escapeHtml(r.module_name)}</strong></td>
          <td><div class="req-just">${escapeHtml(r.justification)}</div>${r.decision_note ? `<div style="font-size:11px;color:var(--ink3);margin-top:4px">Resposta: ${escapeHtml(r.decision_note)}</div>` : ''}</td>
          <td><span class="badge ${r.status === 'aprovado' ? 'aprovado' : r.status === 'negado' ? 'negado' : 'pendente'}">${escapeHtml(r.status)}</span>${r.decided_at ? `<div style="font-size:10px;color:var(--ink3);margin-top:3px">${formatRelativeTime(r.decided_at)}</div>` : ''}</td>
          <td>
            <div class="actions-cell">
              ${pending ? `
                <button class="btn-act approve" onclick="decideAccessRequest('${r.id}', 'aprovar')">Aprovar</button>
                <button class="btn-act danger" onclick="decideAccessRequest('${r.id}', 'negar')">Negar</button>` : '<span style="color:var(--ink3);font-size:11px">—</span>'}
            </div>
          </td>
        </tr>`;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--red);padding:20px">Erro ao carregar solicitações: ${escapeHtml(err.message)}</td></tr>`;
  }
}

function updatePendingRequestsBadge(n) {
  const a = document.getElementById('pendingRequestsCount');
  const b = document.getElementById('reqCountPending');
  if (a) a.textContent = n;
  if (b) b.textContent = n;
  if (tabRequestsBtn) tabRequestsBtn.style.color = n > 0 ? 'var(--red)' : '';
}

async function refreshPendingRequestsCount() {
  try {
    const res = await fetch('/api/admin/access-requests?status=pendente');
    if (res.ok) updatePendingRequestsBadge((await res.json()).pending || 0);
  } catch (_) {}
}

async function decideAccessRequest(id, action) {
  let note = '';
  if (action === 'aprovar') {
    if (!confirm('Aprovar a solicitação? O relatório será liberado em Privilégios do colaborador e ele será avisado por e-mail.')) return;
  } else {
    const typed = prompt('Negar solicitação. Informe uma observação para o colaborador (opcional):');
    if (typed === null) return;
    note = typed;
  }
  try {
    const res = await fetch(`/api/admin/access-requests/${id}/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, note })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      showToast(action === 'aprovar' ? 'Acesso aprovado e privilégios atualizados.' : 'Solicitação negada. Colaborador avisado.', 'success');
      loadAccessRequests();
      loadUsers();
    } else {
      showToast(data.error || 'Não foi possível registrar a decisão.', 'error');
      loadAccessRequests();
    }
  } catch (_) {
    showToast('Erro de conexão ao registrar decisão.', 'error');
  }
}

document.querySelectorAll('[data-req-filter]').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('[data-req-filter]').forEach(b => b.classList.remove('active'));
    e.currentTarget.classList.add('active');
    accessRequestsFilter = e.currentTarget.dataset.reqFilter;
    loadAccessRequests();
  });
});

// Filtros de Usuários
document.querySelectorAll('.sub-filter-btn[data-filter]').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.sub-filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
    e.currentTarget.classList.add('active');
    activeUserFilter = e.currentTarget.dataset.filter;
    renderUsers();
  });
});

document.getElementById('searchUsers').addEventListener('input', renderUsers);

// Alteração rápida de status
async function quickStatus(userId, newStatus) {
  if (!confirm(`Confirmar alteração de status para ${newStatus.toUpperCase()}?`)) return;
  try {
    const res = await fetch(`/api/admin/users/${userId}/privileges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(`Status alterado para ${newStatus.toUpperCase()} com sucesso.`, 'success');
      loadUsers();
    } else {
      showToast('Erro ao atualizar status.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão ao alterar status.', 'error');
  }
}

// Exclusão permanente de colaborador
async function deleteUser(userId, userName) {
  if (!confirm(`Deseja realmente EXCLUIR permanentemente o cadastro de "${userName}"?\n\nEsta operação removerá o colaborador da base corporativa e não poderá ser desfeita.`)) {
    return;
  }
  try {
    const res = await fetch(`/api/admin/users/${userId}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Colaborador "${userName}" excluído com sucesso.`, 'success');
      loadUsers();
    } else {
      showToast(data.error || 'Erro ao excluir usuário.', 'error');
    }
  } catch (err) {
    showToast('Erro de comunicação ao tentar excluir usuário.', 'error');
  }
}

// Modal de Privilégios Remodelado & Ações Rápidas
let currentModalUserMods = [];

function openPrivilegesModal(userId) {
  const user = allUsers.find(u => u.id === userId);
  if (!user) return;

  document.getElementById('privUserId').value = user.id;
  document.getElementById('privUserName').textContent = user.nome_completo;
  document.getElementById('privUserEmail').textContent = `${user.email_claro} • Login: ${user.login_claro}`;
  document.getElementById('privUserMeta').textContent = `Área: ${user.area || '—'} • Função: ${user.funcao || '—'}`;
  document.getElementById('privAvatar').textContent = getInitials(user.nome_completo);
  document.getElementById('privStatus').value = user.status;
  document.getElementById('privRole').value = user.is_admin ? '1' : '0';
  document.getElementById('privNotify').checked = Boolean(user.notify_updates);

  currentModalUserMods = getUserModules(user);
  renderModalModuleToggles();

  document.getElementById('modalPrivileges').classList.add('on');
}

function renderModalModuleToggles() {
  const container = document.getElementById('modalModulesList');
  if (!container) return;

  container.innerHTML = SYSTEM_SECTIONS.map(sec => {
    const totalInSec = sec.modules.length;
    const activeInSec = sec.modules.filter(m => currentModalUserMods.includes(m.id)).length;
    return `
      <div class="priv-section">
        <div class="priv-section-hd">
          <div class="priv-section-title">
            <span>${escapeHtml(sec.name)}</span>
            <span class="priv-section-count">${activeInSec} de ${totalInSec} autorizados</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <button type="button" class="btn-link" onclick="setSectionToggles('${sec.key}', true)">Marcar Seção</button>
            <span style="color:var(--line)">•</span>
            <button type="button" class="btn-link" onclick="setSectionToggles('${sec.key}', false)">Desmarcar</button>
          </div>
        </div>
        <div class="priv-cards-grid">
          ${sec.modules.map(m => {
            const isChecked = currentModalUserMods.includes(m.id);
            return `
              <div class="priv-card ${isChecked ? 'active' : ''}" onclick="toggleModalModule('${m.id}')" title="Clique para ${isChecked ? 'revogar' : 'conceder'} acesso ao ${escapeHtml(m.name)}">
                <div class="priv-card-info">
                  <div class="priv-card-name">${escapeHtml(m.name)}</div>
                  <div class="priv-card-desc">${escapeHtml(m.desc || m.short || '')}</div>
                </div>
                <span class="switch-btn ${isChecked ? 'active' : ''}"></span>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function setSectionToggles(sectionKey, enable) {
  const sec = SYSTEM_SECTIONS.find(s => s.key === sectionKey);
  if (!sec) return;
  const modIds = sec.modules.map(m => m.id);
  if (enable) {
    currentModalUserMods = Array.from(new Set([...currentModalUserMods, ...modIds]));
  } else {
    currentModalUserMods = currentModalUserMods.filter(id => !modIds.includes(id));
  }
  renderModalModuleToggles();
}

function toggleModalModule(moduleId) {
  if (currentModalUserMods.includes(moduleId)) {
    currentModalUserMods = currentModalUserMods.filter(m => m !== moduleId);
  } else {
    currentModalUserMods.push(moduleId);
  }
  renderModalModuleToggles();
}

function grantAllReports() {
  const reportModIds = ALL_SYSTEM_MODULES
    .filter(m => !isPepToolsModule(m))
    .map(m => m.id);
  currentModalUserMods = Array.from(new Set([...currentModalUserMods, ...reportModIds]));
  renderModalModuleToggles();
}

function revokeAllReports() {
  const reportModIds = ALL_SYSTEM_MODULES
    .filter(m => !isPepToolsModule(m))
    .map(m => m.id);
  currentModalUserMods = currentModalUserMods.filter(id => !reportModIds.includes(id));
  renderModalModuleToggles();
}

function grantAllPepTools() {
  const pepModIds = ALL_SYSTEM_MODULES
    .filter(m => isPepToolsModule(m))
    .map(m => m.id);
  currentModalUserMods = Array.from(new Set([...currentModalUserMods, ...pepModIds]));
  renderModalModuleToggles();
}

function revokeAllPepTools() {
  const pepModIds = ALL_SYSTEM_MODULES
    .filter(m => isPepToolsModule(m))
    .map(m => m.id);
  currentModalUserMods = currentModalUserMods.filter(id => !pepModIds.includes(id));
  renderModalModuleToggles();
}

function setAllPrivToggles(enableAll) {
  if (enableAll) {
    currentModalUserMods = [...ALL_MODULE_IDS];
  } else {
    currentModalUserMods = [];
  }
  renderModalModuleToggles();
}

function showToast(message, type = 'success') {
  let toast = document.getElementById('adminToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'adminToast';
    toast.style.cssText = 'position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:6px;font-size:13px;font-weight:700;color:#fff;z-index:999999;box-shadow:0 4px 14px rgba(0,0,0,0.25);transition:all .3s ease;transform:translateY(20px);opacity:0;display:flex;align-items:center;gap:8px';
    document.body.appendChild(toast);
  }
  toast.style.background = type === 'success' ? '#137333' : '#c0191f';
  toast.innerHTML = (type === 'success' ? '✓ ' : '✕ ') + escapeHtml(message);
  toast.style.transform = 'translateY(0)';
  toast.style.opacity = '1';
  clearTimeout(window._toastTimeout);
  window._toastTimeout = setTimeout(() => {
    toast.style.transform = 'translateY(20px)';
    toast.style.opacity = '0';
  }, 4000);
}

document.getElementById('btnSavePrivileges').addEventListener('click', async () => {
  const userId = document.getElementById('privUserId').value;
  const status = document.getElementById('privStatus').value;
  const is_admin = document.getElementById('privRole').value === '1';
  const modules_allowed = currentModalUserMods.length > 0 ? currentModalUserMods.join(',') : 'none';
  const notify_updates = document.getElementById('privNotify').checked ? 1 : 0;
  const btn = document.getElementById('btnSavePrivileges');
  btn.disabled = true;
  btn.textContent = 'Salvando…';

  try {
    const res = await fetch(`/api/admin/users/${userId}/privileges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, is_admin, modules_allowed, notify_updates })
    });

    if (res.ok) {
      document.getElementById('modalPrivileges').classList.remove('on');
      const uObj = allUsers.find(x => x.id === userId);
      const uName = uObj ? uObj.nome_completo : 'Colaborador';
      showToast(`Privilégios de "${uName}" salvos com sucesso!`, 'success');
      loadUsers();
    } else {
      const errData = await res.json().catch(() => ({}));
      showToast(errData.error || 'Erro ao salvar privilégios.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão ao salvar privilégios.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Salvar Privilégios';
  }
});

// Resetar Senha (Senha de uso único)
async function resetUserPassword(userId) {
  const user = allUsers.find(u => u.id === userId);
  if (!user) return;

  if (!confirm(`Deseja gerar uma senha provisória de uso único para ${user.nome_completo}? Um e-mail formal será despachado para ${user.email_claro}.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/admin/users/${userId}/reset-password`, { method: 'POST' });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Erro ao redefinir senha.', 'error');
      return;
    }

    showToast(`Senha provisória gerada para ${data.nome || user.nome_completo}.`, 'success');
    document.getElementById('tempTargetName').textContent = data.nome || user.nome_completo;
    document.getElementById('tempTargetEmail').textContent = data.email || user.email_claro;
    document.getElementById('tempCodeDisplay').textContent = data.temp_password;
    document.getElementById('modalTempPassword').classList.add('on');
    loadUsers();
  } catch (err) {
    showToast('Erro de conexão com o servidor.', 'error');
  }
}

document.getElementById('btnCopyTemp').addEventListener('click', () => {
  const code = document.getElementById('tempCodeDisplay').textContent;
  navigator.clipboard.writeText(code);
  showToast('Senha provisória copiada para a área de transferência.', 'success');
});

// ==========================================
// 2. DASHBOARD DE ACESSOS COM FILTRO DE DATA
// ==========================================
function setDatePreset(preset) {
  statsDateFilter.preset = preset;
  document.querySelectorAll('.date-preset-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.date-preset-btn[data-preset="${preset}"]`);
  if (btn) btn.classList.add('active');

  const now = new Date();
  const formatYmd = d => d.toISOString().split('T')[0];

  if (preset === 'today') {
    statsDateFilter.startDate = formatYmd(now);
    statsDateFilter.endDate = formatYmd(now);
  } else if (preset === '7d') {
    const s = new Date(now.getTime() - 7 * 86400000);
    statsDateFilter.startDate = formatYmd(s);
    statsDateFilter.endDate = formatYmd(now);
  } else if (preset === '15d') {
    const s = new Date(now.getTime() - 15 * 86400000);
    statsDateFilter.startDate = formatYmd(s);
    statsDateFilter.endDate = formatYmd(now);
  } else if (preset === '30d') {
    const s = new Date(now.getTime() - 30 * 86400000);
    statsDateFilter.startDate = formatYmd(s);
    statsDateFilter.endDate = formatYmd(now);
  } else if (preset === 'all') {
    statsDateFilter.startDate = '';
    statsDateFilter.endDate = '';
  }

  document.getElementById('statsDateStart').value = statsDateFilter.startDate;
  document.getElementById('statsDateEnd').value = statsDateFilter.endDate;
  loadAccessStats();
}

function applyCustomDateFilter() {
  const start = document.getElementById('statsDateStart').value;
  const end = document.getElementById('statsDateEnd').value;
  if (!start) {
    showToast('Selecione a data inicial.', 'error');
    return;
  }
  statsDateFilter.preset = 'custom';
  statsDateFilter.startDate = start;
  statsDateFilter.endDate = end || start;
  document.querySelectorAll('.date-preset-btn').forEach(b => b.classList.remove('active'));
  showToast('Filtro de período personalizado aplicado.', 'success');
  loadAccessStats();
}

function clearDateFilter() {
  setDatePreset('30d');
}

async function loadAccessStats() {
  let url = '/api/admin/access-stats';
  const params = [];
  if (statsDateFilter.startDate) params.push(`start_date=${encodeURIComponent(statsDateFilter.startDate)}`);
  if (statsDateFilter.endDate) params.push(`end_date=${encodeURIComponent(statsDateFilter.endDate)}`);
  if (params.length) url += `?${params.join('&')}`;

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Falha ao obter estatísticas');
    const data = await res.json();
    renderStatsDashboard(data);
  } catch (err) {
    console.error('Erro loadAccessStats:', err);
  }
}

function renderStatsDashboard(data) {
  const s = data.summary;

  // Atualiza rótulo do período
  document.getElementById('statsPeriodLabel').textContent = s.period_label || 'Período Selecionado';

  // 1. KPIs
  document.getElementById('kpiMonthAccesses').textContent = Number(s.period_accesses).toLocaleString('pt-BR');
  document.getElementById('kpiMomGrowth').innerHTML = s.growth_pct >= 0 
    ? `<span class="tag-pos">▲ +${s.growth_pct}%</span> vs período anterior`
    : `<span class="tag-neg">▼ ${s.growth_pct}%</span> vs período anterior`;

  document.getElementById('kpiPeriodExports').textContent = Number(s.total_exports).toLocaleString('pt-BR');
  const expRate = s.period_accesses > 0 ? Math.round((s.total_exports / s.period_accesses) * 100) : 0;
  document.getElementById('kpiExportRate').textContent = `${expRate}% de taxa de exportação (${s.total_exports} de ${s.period_accesses} acessos)`;

  document.getElementById('kpiUniqueUsers').textContent = s.unique_users;
  document.getElementById('kpiTopChannel').textContent = s.top_channel;
  document.getElementById('kpiTopResource').textContent = formatResourceName(s.top_resource);
  document.getElementById('kpiTopLocation').textContent = s.top_location;

  // 2. Gráfico Diário de Evolução (Consultas vs Exportações)
  const dailyEl = document.getElementById('dailyChart');
  if (!data.daily || data.daily.length === 0) {
    dailyEl.innerHTML = `<div style="margin:auto;color:var(--ink3);font-size:12px">Sem registros no intervalo filtrado.</div>`;
  } else {
    const maxDay = Math.max(...data.daily.map(d => d.count), 1);
    dailyEl.innerHTML = data.daily.map(d => {
      const hTotal = Math.round((d.count / maxDay) * 125);
      const hExp = Math.round(((d.exports || 0) / maxDay) * 125);
      const dateParts = d.day.split('-');
      const label = `${dateParts[2]}/${dateParts[1]}`;
      return `
        <div class="daily-col" title="${label}: ${d.count} acessos (${d.exports || 0} exportações)">
          <div class="daily-bars">
            <div class="daily-b views" style="height:${Math.max(3, hTotal - hExp)}px"></div>
            ${hExp > 0 ? `<div class="daily-b exports" style="height:${Math.max(3, hExp)}px"></div>` : ''}
          </div>
          <div class="daily-lbl">${label}</div>
        </div>
      `;
    }).join('');
  }

  // 3. Gráfico Horário
  const hourlyEl = document.getElementById('hourlyChart');
  const maxHour = Math.max(...data.hourly.map(h => h.count), 1);
  hourlyEl.innerHTML = data.hourly.map(h => {
    const height = Math.round((h.count / maxHour) * 130);
    return `
      <div style="flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end" title="${h.hour}:00 — ${h.count} acessos">
        <div style="width:100%;background:#2a5d8f;height:${Math.max(3, height)}px;border-radius:2px 2px 0 0"></div>
      </div>
    `;
  }).join('');

  // 4. Recursos / Visões Mais Demandadas
  const resourcesEl = document.getElementById('resourcesBars');
  const maxRes = Math.max(...data.resources.map(r => r.count), 1);
  const totalRes = data.resources.reduce((acc, r) => acc + r.count, 0) || 1;

  if (!data.resources || data.resources.length === 0) {
    resourcesEl.innerHTML = `<div style="color:var(--ink3);text-align:center;padding:20px">Sem dados de recursos no período.</div>`;
  } else {
    resourcesEl.innerHTML = data.resources.map(r => {
      const pct = Math.round((r.count / totalRes) * 100);
      const widthPct = Math.round((r.count / maxRes) * 100);
      const isExport = r.recurso.includes('DOWNLOAD') || r.recurso.includes('EXPORT');
      return `
        <div class="bar-row">
          <div class="bar-meta">
            <strong>${isExport ? '[Exportação] ' : ''}${formatResourceName(r.recurso)}</strong>
            <span>${r.count} interações (${pct}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill ${isExport ? 'green' : (r.recurso.includes('CHURN') ? 'red' : '')}" style="width:${widthPct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // 5. Canais Mais Engajados
  const channelsEl = document.getElementById('channelsBars');
  const maxChan = Math.max(...data.channels.map(c => c.count), 1);
  const totalChan = data.channels.reduce((acc, c) => acc + c.count, 0) || 1;

  if (!data.channels || data.channels.length === 0) {
    channelsEl.innerHTML = `<div style="color:var(--ink3);text-align:center;padding:20px">Sem dados de canais no período.</div>`;
  } else {
    channelsEl.innerHTML = data.channels.map(c => {
      const pct = Math.round((c.count / totalChan) * 100);
      const widthPct = Math.round((c.count / maxChan) * 100);
      return `
        <div class="bar-row">
          <div class="bar-meta">
            <strong>${escapeHtml(c.area)}</strong>
            <span>${c.count} sessões (${pct}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${widthPct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // 6. Ranking de Usuários e Visões no Período
  const topUsersTbody = document.getElementById('topUsersTbody');
  if (!data.top_users || data.top_users.length === 0) {
    topUsersTbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:var(--ink3);padding:20px">Nenhum dado individual registrado neste período.</td></tr>`;
  } else {
    topUsersTbody.innerHTML = data.top_users.map(u => {
      const dt = u.last_access ? parseUtcDate(u.last_access).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }) : '—';
      const exportsCount = u.total_exports || 0;
      return `
        <tr>
          <td>
            <strong>${escapeHtml(u.nome_completo || 'Desconhecido')}</strong>
            ${Boolean(u.is_online) ? '<span class="badge online" style="background:#dcfce7;color:#15803d;border:1px solid #86efac;font-size:9.5px;font-weight:700;margin-left:5px">🟢 Online</span>' : '<span class="badge offline" style="background:#f1f5f9;color:#64748b;font-size:9.5px;margin-left:5px">⚪ Offline</span>'}
          </td>
          <td><code>${escapeHtml(u.login_claro || '—')}</code></td>
          <td>${escapeHtml(u.email_claro)}</td>
          <td>${escapeHtml(u.area || '—')} / <span style="color:var(--ink3)">${escapeHtml(u.funcao || '—')}</span></td>
          <td><strong style="color:var(--blue);font-size:13px">${u.total_views}</strong></td>
          <td>
            ${exportsCount > 0 ? `<span class="badge-export-yes">${exportsCount} exp.</span>` : '<span class="badge-export-no">0</span>'}
          </td>
          <td><span class="badge ${u.last_resource?.includes('DOWNLOAD') || u.last_resource?.includes('EXPORT') ? 'aprovado' : 'admin'}">${formatResourceName(u.last_resource)}</span></td>
          <td>${escapeHtml(u.last_location || '—')}</td>
          <td><span style="color:var(--ink2);font-family:Consolas,monospace;font-size:11px">${dt}</span></td>
        </tr>
      `;
    }).join('');
  }
}

// ==========================================
// 3. AUDITORIA DETALHADA (ACESSOS, HORÁRIOS & SE EXPORTOU)
// ==========================================
function parseActionMeta(recurso) {
  if (!recurso) return { type: 'view', label: 'Visualização', page: 'Geral', isExport: false, exportType: '' };

  const rec = recurso.toUpperCase();
  if (rec.startsWith('EXPORT_CSV')) {
    const pageKey = rec.split(':')[1] || '';
    return { type: 'export-csv', label: 'Exportou CSV', page: formatResourceName(pageKey || rec), isExport: true, exportType: 'CSV' };
  }
  if (rec.startsWith('EXPORT_HTML') || rec.includes('DOWNLOAD')) {
    const pageKey = rec.split(':')[1] || rec.replace('_DOWNLOAD', '');
    return { type: 'export-html', label: 'Exportou HTML', page: formatResourceName(pageKey), isExport: true, exportType: 'HTML Offline' };
  }
  if (rec === 'LOGIN') {
    return { type: 'login', label: 'Autenticação / Login', page: 'Portal Corporativo', isExport: false, exportType: '' };
  }
  if (rec === 'PASSWORD_CHANGE') {
    return { type: 'password', label: 'Redefinição de Senha', page: 'Segurança', isExport: false, exportType: '' };
  }
  if (rec.startsWith('ADMIN_')) {
    return { type: 'admin', label: 'Ação Administrativa', page: rec.replace('ADMIN_', ''), isExport: false, exportType: '' };
  }
  if (rec === 'PORTAL_HOME') {
    return { type: 'view', label: 'Visualizou Tela', page: 'Portal / Pool de Ferramentas', isExport: false, exportType: '' };
  }
  return { type: 'view', label: 'Visualizou Tela', page: formatResourceName(rec), isExport: false, exportType: '' };
}

function formatResourceName(rec) {
  if (!rec) return 'Geral';
  const clean = rec.replace(/^EXPORT_HTML:/, '').replace(/^EXPORT_CSV:/, '').replace(/_DOWNLOAD$/, '');
  if (clean === 'CHURN_SAFRA' || clean === 'CHURN') return 'Painel Churn Safra';
  if (clean === 'CHURN_BL_TOTAL') return 'Painel Churn Banda Larga Total';
  if (clean === 'CHURN_BL_PME') return 'Painel Churn Banda Larga PME';
  if (clean === 'FPD_REGIONAL_NORTE' || clean === 'FPD') return 'Painel FPD Regional Norte';
  if (clean === 'PORTAL_HOME') return 'Portal Pephub Home';
  if (clean === 'ADMIN_PANEL') return 'Painel Administrativo';
  if (clean === 'LOGIN') return 'Portal / Autenticação';
  if (clean === 'PASSWORD_CHANGE') return 'Redefinição de Senha';
  return clean;
}

async function loadAccessLogs() {
  const tbody = document.getElementById('logsTbody');
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--ink3);padding:24px">Atualizando registros de auditoria…</td></tr>`;

  const query = document.getElementById('searchLogs').value.trim();
  const params = [];
  if (query) params.push(`q=${encodeURIComponent(query)}`);
  if (activeLogActionFilter !== 'all') params.push(`action=${encodeURIComponent(activeLogActionFilter)}`);

  try {
    const res = await fetch(`/api/admin/access-logs?${params.join('&')}`);
    const logs = await res.json();

    if (!logs || logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--ink3);padding:24px">Nenhum registro de auditoria localizado com estes filtros.</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => {
      const dtObj = parseUtcDate(l.created_at);
      const dateFormatted = dtObj ? dtObj.toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo' }) : '—';
      const timeFormatted = dtObj ? dtObj.toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '—';
      const act = parseActionMeta(l.recurso);

      return `
        <tr>
          <td>
            <div style="font-weight:700;color:var(--ink)">${dateFormatted}</div>
            <span class="time-tag">${timeFormatted}</span>
          </td>
          <td>
            <div style="font-weight:700;color:var(--ink)">${escapeHtml(l.nome_completo || 'Desconhecido')}</div>
            <div style="font-size:11px;color:var(--ink3)"><code>${escapeHtml(l.login_claro || '—')}</code> • ${escapeHtml(l.email_claro || '—')}</div>
          </td>
          <td>
            <div style="font-weight:600;color:var(--ink)">${escapeHtml(l.area || '—')}</div>
            <div style="color:var(--ink3);font-size:11px">${escapeHtml(l.funcao || '—')}</div>
          </td>
          <td>
            <span class="badge-act ${act.type}">
              ${act.label}
            </span>
          </td>
          <td>
            <strong style="color:var(--ink);font-size:12px">${escapeHtml(act.page)}</strong>
          </td>
          <td>
            ${act.isExport 
              ? `<span class="badge-export-yes">SIM • ${act.exportType}</span>` 
              : `<span class="badge-export-no">NÃO</span>`}
          </td>
          <td>
            <div><code style="font-size:11px">${escapeHtml(l.ip || '127.0.0.1')}</code></div>
            <div style="font-size:11px;color:var(--ink3)">${escapeHtml(l.localizacao || 'Localidade não identificada')}</div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--red);padding:24px">Erro ao consultar registros de auditoria.</td></tr>`;
  }
}

// Filtro de ações de auditoria
document.querySelectorAll('.sub-filter-btn[data-act-filter]').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.sub-filter-btn[data-act-filter]').forEach(b => b.classList.remove('active'));
    e.currentTarget.classList.add('active');
    activeLogActionFilter = e.currentTarget.dataset.actFilter;
    loadAccessLogs();
  });
});

document.getElementById('btnRefreshLogs').addEventListener('click', loadAccessLogs);
document.getElementById('searchLogs').addEventListener('input', () => {
  clearTimeout(window._logSearchTimeout);
  window._logSearchTimeout = setTimeout(loadAccessLogs, 300);
});

// Modal Broadcast
document.getElementById('btnOpenBroadcast').addEventListener('click', () => {
  document.getElementById('modalBroadcast').classList.add('on');
});

document.getElementById('btnSendBroadcast').addEventListener('click', async () => {
  const relatorio = document.getElementById('bcReport').value.trim();
  const assunto = document.getElementById('bcSubject').value.trim();
  const mensagem = document.getElementById('bcMessage').value.trim();

  if (!relatorio || !assunto) {
    showToast('Preencha o nome do relatório e o assunto.', 'error');
    return;
  }

  const btn = document.getElementById('btnSendBroadcast');
  btn.disabled = true;
  btn.textContent = 'Enviando…';

  try {
    const res = await fetch('/api/admin/broadcast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ relatorio, assunto, mensagem })
    });

    const data = await res.json();
    if (res.ok) {
      showToast(`Comunicado formal transmitido com sucesso para ${data.sent} colaboradores aprovados.`, 'success');
      document.getElementById('modalBroadcast').classList.remove('on');
    } else {
      showToast(data.error || 'Erro ao enviar comunicado.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão ao disparar comunicado.', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Enviar Comunicado';
  }
});

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ==========================================
// 4. TRAVAS E CONTROLES GLOBAIS DO SISTEMA
// ==========================================
async function loadSystemControls() {
  try {
    const res = await fetch('/api/admin/system-controls');
    if (!res.ok) throw new Error('Falha ao obter travas de sistema');
    allControls = await res.json();
    renderSystemControls();
    updateGlobalLockBanner();
  } catch (err) {
    console.error('Erro loadSystemControls:', err);
  }
}

function renderSystemControls() {
  const container = document.getElementById('controlsGrid');
  if (!container) return;

  const countActive = allControls.filter(c => c.value === '1').length;
  const countBadge = document.getElementById('activeControlsCount');
  if (countBadge) countBadge.textContent = countActive;

  container.innerHTML = allControls.map(c => {
    const isActive = c.value === '1';
    return `
      <div class="ctrl-card ${isActive ? 'locked' : ''}">
        <div class="ctrl-hd">
          <div>
            <div class="ctrl-title">${escapeHtml(c.label)}</div>
            <div class="ctrl-desc">${escapeHtml(c.description)}</div>
          </div>
          <div class="ctrl-switch-wrap">
            <div class="switch-item ${isActive ? 'on' : ''}" 
                 onclick="toggleSystemControl('${c.key}', '${isActive ? '0' : '1'}')"
                 title="Clique para ${isActive ? 'desativar trava (normalizar)' : 'ativar trava (suspender)'}">
              <span style="font-size:11px;font-weight:700">${isActive ? 'TRAVA ATIVA' : 'LIBERADO'}</span>
              <span class="switch-btn ${isActive ? 'active' : ''}"></span>
            </div>
          </div>
        </div>
        <div class="ctrl-ft">
          <span class="badge ${isActive ? 'bloqueado' : 'aprovado'}">
            ${isActive ? 'Operação Suspensa / Travada' : 'Operação Normal / Liberada'}
          </span>
          <span class="ctrl-meta">
            ${c.updated_at ? `Última alteração: ${formatRelativeTime(c.updated_at)} ${c.updated_by ? `por ${escapeHtml(c.updated_by)}` : ''}` : 'Status padrão do sistema'}
          </span>
        </div>
      </div>
    `;
  }).join('');
}

async function toggleSystemControl(key, newValue) {
  const ctrl = allControls.find(c => c.key === key);
  const isActivating = newValue === '1';
  const actionText = isActivating ? 'ATIVAR A TRAVA (SUSPENDER OPERAÇÃO)' : 'DESATIVAR A TRAVA (LIBERAR OPERAÇÃO)';
  
  if (!confirm(`Confirmar ${actionText} para:\n"${ctrl ? ctrl.label : key}"?\n\nEsta alteração entra em vigor imediatamente para todos os colaboradores.`)) {
    return;
  }

  // Atualização otimista
  if (ctrl) ctrl.value = newValue;
  renderSystemControls();
  updateGlobalLockBanner();

  try {
    const res = await fetch('/api/admin/system-controls', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value: newValue })
    });
    if (!res.ok) {
      showToast('Erro ao atualizar trava de sistema.', 'error');
      loadSystemControls();
    } else {
      showToast(`Trava de sistema atualizada (${key}: ${newValue === '1' ? 'ATIVADA' : 'DESATIVADA'}).`, 'success');
      loadSystemControls();
    }
  } catch (err) {
    showToast('Erro de comunicação com o servidor.', 'error');
    loadSystemControls();
  }
}

function updateGlobalLockBanner() {
  const banner = document.getElementById('globalLockBanner');
  const lockText = document.getElementById('globalLockText');
  if (!banner || !lockText) return;
  const activeList = allControls.filter(c => c.value === '1');
  if (activeList.length > 0) {
    banner.style.display = 'flex';
    lockText.innerHTML = `<strong>Atenção:</strong> Existem <strong>${activeList.length}</strong> trava(s) operacional(is) ativa(s) na plataforma: ${activeList.map(c => `<code>${escapeHtml(c.label)}</code>`).join(' • ')}.`;
  } else {
    banner.style.display = 'none';
  }
}

// ==========================================
// 5. GESTÃO DE FERRAMENTAS & CONTROLE EM MASSA
// ==========================================
async function loadModules() {
  try {
    const res = await fetch('/api/admin/modules');
    if (!res.ok) throw new Error('Falha ao carregar catálogo de ferramentas');
    allModules = await res.json();
    if (typeof updateSystemCatalog === 'function') {
      updateSystemCatalog(allModules);
    }
    if (typeof allUsers !== 'undefined' && allUsers.length > 0) {
      renderUsers();
    }

    const countActive = allModules.filter(m => m.status === 'ativo').length;
    const countSuspended = allModules.filter(m => m.status === 'suspenso').length;
    const countHidden = allModules.filter(m => m.status === 'oculto').length;
    const countRoadmap = allModules.filter(m => m.status === 'em_andamento').length;

    const countBadge = document.getElementById('totalModulesCount');
    if (countBadge) countBadge.textContent = allModules.length;

    const kpiTotal = document.getElementById('kpiTotalModules');
    const kpiActive = document.getElementById('kpiActiveModules');
    const kpiSusp = document.getElementById('kpiSuspendedModules');
    const kpiHidden = document.getElementById('kpiHiddenModules');
    const kpiRoadmap = document.getElementById('kpiRoadmapModules');

    if (kpiTotal) kpiTotal.textContent = allModules.length;
    if (kpiActive) kpiActive.textContent = countActive;
    if (kpiSusp) kpiSusp.textContent = countSuspended;
    if (kpiHidden) kpiHidden.textContent = countHidden;
    if (kpiRoadmap) kpiRoadmap.textContent = countRoadmap;

    renderModules();
  } catch (err) {
    console.error('Erro loadModules:', err);
  }
}

function renderModules() {
  const tbody = document.getElementById('modulesTbody');
  if (!tbody) return;

  const searchInput = document.getElementById('searchModules');
  const search = searchInput ? searchInput.value.trim().toLowerCase() : '';

  let filtered = allModules;
  if (search) {
    filtered = filtered.filter(m =>
      (m.name || '').toLowerCase().includes(search) ||
      (m.short_name || '').toLowerCase().includes(search) ||
      (m.id || '').toLowerCase().includes(search) ||
      (m.section || '').toLowerCase().includes(search) ||
      (m.route || '').toLowerCase().includes(search)
    );
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--ink3);padding:24px">Nenhuma ferramenta encontrada com os filtros aplicados.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(m => {
    const isCore = ['churn', 'fpd', 'churn-bl-total', 'churn-bl-pme', 'divulgacao', 'tv'].includes(m.id);
    const withAccess = m.users_with_access || 0;
    const totalUsers = m.total_regular_users || 0;
    const pct = totalUsers > 0 ? Math.round((withAccess / totalUsers) * 100) : 0;

    return `
      <tr>
        <td>
          <div style="font-weight:700;color:var(--ink);font-size:13px">${escapeHtml(m.name)}</div>
          <div style="font-size:11px;color:var(--ink3);display:flex;align-items:center;gap:6px;margin-top:2px">
            <span>Sigla: <strong>${escapeHtml(m.short_name)}</strong></span>
            <span>•</span>
            <span>ID: <code>${escapeHtml(m.id)}</code></span>
            <span>•</span>
            <span>Rota: <code style="color:var(--blue)">${escapeHtml(m.route)}</code></span>
          </div>
          ${m.description ? `<div style="font-size:11px;color:var(--ink2);margin-top:3px;line-height:1.4">${escapeHtml(m.description)}</div>` : ''}
        </td>
        <td>
          <span style="display:inline-block;padding:3px 8px;border-radius:3px;font-size:10.5px;font-weight:700;background:#f0f2f5;color:var(--ink2)">
            ${escapeHtml(m.section)}
          </span>
        </td>
        <td>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="badge-mod ${m.status}">${m.status}</span>
            <select class="form-select" style="font-size:11px;padding:3px 6px;width:auto;font-weight:600" onchange="changeModuleStatus('${m.id}', this.value)">
              <option value="ativo" ${m.status === 'ativo' ? 'selected' : ''}>Ativo</option>
              <option value="em_andamento" ${m.status === 'em_andamento' ? 'selected' : ''}>Em Andamento</option>
              <option value="suspenso" ${m.status === 'suspenso' ? 'selected' : ''}>Suspenso</option>
              <option value="oculto" ${m.status === 'oculto' ? 'selected' : ''}>Oculto</option>
            </select>
          </div>
        </td>
        <td>
          <div style="font-weight:700;color:var(--ink);font-size:12px">${withAccess} de ${totalUsers}</div>
          <div style="font-size:10.5px;color:var(--ink3);margin-top:1px">${pct}% dos não-admins</div>
        </td>
        <td>
          <div class="actions-cell">
            <button class="btn-act approve" onclick="bulkModuleAccess('${m.id}', 'grant_all')" title="Concede acesso deste relatório para todos os colaboradores não-admins">
              Autorizar Todos
            </button>
            <button class="btn-act danger" onclick="bulkModuleAccess('${m.id}', 'revoke_all')" title="Desmarca o acesso deste relatório de todos os colaboradores não-admins">
              Desmarcar Todos
            </button>
            <button class="btn-act" onclick="openEditModuleModal('${m.id}')" title="Editar dados da ferramenta">
              Editar
            </button>
            ${!isCore ? `
              <button class="btn-act danger" onclick="deleteModule('${m.id}', '${escapeHtml(m.name)}')" title="Excluir ferramenta do catálogo">
                Excluir
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// Alteração de status operacional de módulo via dropdown
async function changeModuleStatus(modId, newStatus) {
  try {
    const mod = allModules.find(m => m.id === modId);
    if (!mod) return;

    const res = await fetch('/api/admin/modules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: mod.id,
        name: mod.name,
        short_name: mod.short_name,
        section: mod.section,
        description: mod.description,
        route: mod.route,
        status: newStatus,
        sort_order: mod.sort_order
      })
    });
    if (res.ok) {
      showToast(`Status do relatório alterado para "${newStatus}".`, 'success');
      loadModules();
    } else {
      showToast('Erro ao atualizar status do módulo.', 'error');
      loadModules();
    }
  } catch (err) {
    showToast('Erro de conexão ao alterar status do módulo.', 'error');
    loadModules();
  }
}

// Ação em massa em um módulo específico (conceder ou desmarcar para todos os não-admins)
async function bulkModuleAccess(modId, action) {
  const mod = allModules.find(m => m.id === modId);
  const modTitle = mod ? mod.name : modId;
  const isGrant = action === 'grant_all';

  const confirmMsg = isGrant
    ? `Deseja realmente AUTORIZAR o acesso a "${modTitle}" para TODOS os colaboradores não-administradores?`
    : `Deseja realmente DESMARCAR/REVOGAR o acesso a "${modTitle}" de TODOS os colaboradores não-administradores?`;

  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch(`/api/admin/modules/${modId}/bulk-access`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Permissões atualizadas com sucesso para ${data.affected || 0} colaboradores.`, 'success');
      loadModules();
      loadUsers();
    } else {
      showToast(data.error || 'Erro ao processar permissões em massa.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão com o servidor.', 'error');
  }
}

// Ação em massa mestra: Conceder ou Desmarcar TODOS os módulos para todos os não-admins
async function bulkAllModulesAccess(action) {
  const isGrant = action === 'grant_all';
  const confirmMsg = isGrant
    ? 'ATENÇÃO: Deseja realmente CONCEDER acesso a TODOS os relatórios e ferramentas ativos para TODOS os colaboradores não-administradores?'
    : 'ATENÇÃO: Deseja realmente DESMARCAR / REVOGAR o acesso a TODOS os relatórios e ferramentas de TODOS os colaboradores não-administradores?';

  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch('/api/admin/modules/bulk-access-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(isGrant ? 'Todos os relatórios foram autorizados com sucesso para todos os colaboradores.' : 'Todos os relatórios foram desmarcados de todos os colaboradores com sucesso.', 'success');
      loadModules();
      loadUsers();
    } else {
      showToast(data.error || 'Erro ao atualizar permissões em massa.', 'error');
    }
  } catch (err) {
    showToast('Erro de comunicação ao processar ação em massa.', 'error');
  }
}

// Modal de Cadastrar / Editar Ferramenta
function openEditModuleModal(modId) {
  const isEdit = Boolean(modId);
  document.getElementById('modalEditModuleTitle').textContent = isEdit ? 'Editar Ferramenta Corporativa' : 'Cadastrar Nova Ferramenta / Módulo';

  const idIn = document.getElementById('modId');
  const shortIn = document.getElementById('modShortName');
  const nameIn = document.getElementById('modName');
  const secIn = document.getElementById('modSection');
  const statusIn = document.getElementById('modStatus');
  const routeIn = document.getElementById('modRoute');
  const sortIn = document.getElementById('modSortOrder');
  const descIn = document.getElementById('modDesc');

  if (isEdit) {
    const mod = allModules.find(m => m.id === modId);
    if (!mod) return;
    idIn.value = mod.id;
    idIn.disabled = true;
    shortIn.value = mod.short_name || '';
    nameIn.value = mod.name || '';
    secIn.value = mod.section || 'Painéis Analíticos';
    statusIn.value = mod.status || 'ativo';
    routeIn.value = mod.route || '';
    sortIn.value = mod.sort_order || 10;
    descIn.value = mod.description || '';
  } else {
    idIn.value = '';
    idIn.disabled = false;
    shortIn.value = '';
    nameIn.value = '';
    secIn.value = 'Painéis Analíticos';
    statusIn.value = 'ativo';
    routeIn.value = '';
    sortIn.value = 10;
    descIn.value = '';
  }

  document.getElementById('modalEditModule').classList.add('on');
}

async function saveModule() {
  const id = document.getElementById('modId').value.trim().toLowerCase();
  const name = document.getElementById('modName').value.trim();
  const short_name = document.getElementById('modShortName').value.trim();
  const section = document.getElementById('modSection').value.trim();
  const status = document.getElementById('modStatus').value;
  const route = document.getElementById('modRoute').value.trim();
  const sort_order = parseInt(document.getElementById('modSortOrder').value || '0', 10);
  const description = document.getElementById('modDesc').value.trim();

  if (!id || !name || !short_name || !section || !route) {
    showToast('Por favor, preencha todos os campos obrigatórios (ID, Nome, Sigla, Seção e Rota).', 'error');
    return;
  }

  try {
    const res = await fetch('/api/admin/modules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, name, short_name, section, status, route, sort_order, description })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Ferramenta "${name}" salva com sucesso!`, 'success');
      document.getElementById('modalEditModule').classList.remove('on');
      await loadModules();
      loadUsers();
    } else {
      showToast(data.error || 'Erro ao salvar ferramenta.', 'error');
    }
  } catch (err) {
    showToast('Erro de comunicação com o servidor.', 'error');
  }
}

async function deleteModule(modId, modName) {
  if (!confirm(`Deseja realmente EXCLUIR a ferramenta "${modName}" do catálogo?`)) return;
  try {
    const res = await fetch(`/api/admin/modules/${modId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast(`Ferramenta "${modName}" excluída com sucesso.`, 'success');
      await loadModules();
      loadUsers();
    } else {
      showToast('Erro ao excluir ferramenta.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão ao excluir ferramenta.', 'error');
  }
}

// Filtro em tempo real no catálogo de módulos
const searchModulesInput = document.getElementById('searchModules');
if (searchModulesInput) searchModulesInput.addEventListener('input', renderModules);

// ==========================================
// 6. EDIÇÃO DE CADASTRO DO COLABORADOR (ADMIN)
// ==========================================
let currentEditingUserId = null;

function openEditUserModal(userId) {
  const user = allUsers.find(u => u.id === userId);
  if (!user) return;
  currentEditingUserId = userId;

  document.getElementById('editUserId').value = user.id;
  document.getElementById('editUserNome').value = user.nome_completo || '';
  document.getElementById('editUserLogin').value = user.login_claro || '';
  document.getElementById('editUserEmail').value = user.email_claro || '';
  document.getElementById('editUserTelefone').value = user.telefone || '';
  document.getElementById('editUserArea').value = user.area || '';
  document.getElementById('editUserFuncao').value = user.funcao || '';

  // Renderiza campos dinâmicos adicionais
  const dynamicContainer = document.getElementById('editUserDynamicFields');
  let meta = {};
  if (user.profile_metadata) {
    try { meta = typeof user.profile_metadata === 'object' ? user.profile_metadata : JSON.parse(user.profile_metadata); } catch(e) { meta = {}; }
  }

  // Identifica campos obrigatórios que não são os padrões de coluna
  const extraFields = allProfileFields.filter(f => f.key !== 'telefone');
  if (extraFields.length === 0 && Object.keys(meta).length === 0) {
    dynamicContainer.innerHTML = `<div style="font-size:11.5px;color:var(--ink3)">Nenhum parâmetro dinâmico adicional configurado.</div>`;
  } else {
    const keys = Array.from(new Set([...extraFields.map(f => f.key), ...Object.keys(meta)]));
    dynamicContainer.innerHTML = keys.map(k => {
      const fieldDef = allProfileFields.find(f => f.key === k);
      const label = fieldDef ? fieldDef.label : k;
      const type = fieldDef ? fieldDef.field_type : 'text';
      const val = meta[k] || '';
      return `
        <div class="form-group" style="margin-bottom:8px">
          <label class="form-label" style="font-size:10.5px">${escapeHtml(label)} (<code>${escapeHtml(k)}</code>)</label>
          <input type="${type}" data-meta-key="${escapeHtml(k)}" class="form-input edit-dynamic-input" value="${escapeHtml(val)}">
        </div>
      `;
    }).join('');
  }

  document.getElementById('modalEditUser').classList.add('on');
}

async function saveUserProfile() {
  if (!currentEditingUserId) return;

  const nome_completo = document.getElementById('editUserNome').value.trim();
  const login_claro = document.getElementById('editUserLogin').value.trim();
  const email_claro = document.getElementById('editUserEmail').value.trim();
  const telefone = document.getElementById('editUserTelefone').value.trim();
  const area = document.getElementById('editUserArea').value.trim();
  const funcao = document.getElementById('editUserFuncao').value.trim();

  if (!nome_completo || !login_claro || !email_claro) {
    showToast('Nome completo, login e e-mail corporativo são obrigatórios.', 'error');
    return;
  }

  // Coleta campos dinâmicos adicionais
  const metadata = {};
  document.querySelectorAll('.edit-dynamic-input').forEach(inp => {
    const k = inp.dataset.metaKey;
    if (k) metadata[k] = inp.value.trim();
  });

  try {
    const res = await fetch(`/api/admin/users/${currentEditingUserId}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome_completo,
        login_claro,
        email_claro,
        telefone,
        area,
        funcao,
        profile_metadata: metadata
      })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Cadastro de "${nome_completo}" atualizado com sucesso!`, 'success');
      document.getElementById('modalEditUser').classList.remove('on');
      loadUsers();
    } else {
      showToast(data.error || 'Erro ao salvar dados cadastrais do colaborador.', 'error');
    }
  } catch (err) {
    showToast('Erro de comunicação com o servidor.', 'error');
  }
}

// ==========================================
// 7. GESTÃO DE PARÂMETROS OBRIGATÓRIOS DE PERFIL
// ==========================================
async function loadProfileFields() {
  try {
    const res = await fetch('/api/admin/profile-fields');
    if (!res.ok) return;
    allProfileFields = await res.json();
    renderProfileFields();
  } catch (err) {
    console.error('Erro loadProfileFields:', err);
  }
}

function renderProfileFields() {
  const tbody = document.getElementById('requiredFieldsTbody');
  if (!tbody) return;

  if (allProfileFields.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--ink3);padding:18px">Nenhum campo obrigatório configurado além do padrão inicial.</td></tr>`;
    return;
  }

  tbody.innerHTML = allProfileFields.map(f => {
    const isCore = f.key === 'telefone';
    const isReq = Boolean(f.is_required);
    return `
      <tr>
        <td>
          <div style="font-weight:700;color:var(--ink)">${escapeHtml(f.label)}</div>
          ${f.placeholder ? `<div style="font-size:10.5px;color:var(--ink3)">Ex: ${escapeHtml(f.placeholder)}</div>` : ''}
        </td>
        <td><code>${escapeHtml(f.key)}</code></td>
        <td><span style="font-size:11px;color:var(--ink2)">${escapeHtml(f.field_type || 'text')}</span></td>
        <td>
          <span class="badge ${isReq ? 'aprovado' : 'colab'}">
            ${isReq ? 'Obrigatório no Login' : 'Opcional'}
          </span>
        </td>
        <td>
          <div class="actions-cell">
            ${!isCore ? `
              <button class="btn-act danger" onclick="deleteProfileField('${f.key}', '${escapeHtml(f.label)}')">
                Excluir
              </button>
            ` : '<span style="font-size:10.5px;color:var(--ink3);padding:4px">Campo Base Padrão</span>'}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function openAddProfileFieldModal() {
  document.getElementById('fieldKey').value = '';
  document.getElementById('fieldLabel').value = '';
  document.getElementById('fieldType').value = 'text';
  document.getElementById('fieldPlaceholder').value = '';
  document.getElementById('fieldRequired').value = '1';
  document.getElementById('fieldRegex').value = '';
  document.getElementById('modalAddProfileField').classList.add('on');
}

async function saveProfileField() {
  const key = document.getElementById('fieldKey').value.trim().toLowerCase().replace(/[^a-z0-9_]/g, '');
  const label = document.getElementById('fieldLabel').value.trim();
  const field_type = document.getElementById('fieldType').value;
  const placeholder = document.getElementById('fieldPlaceholder').value.trim();
  const is_required = parseInt(document.getElementById('fieldRequired').value || '1', 10);
  const validation_regex = document.getElementById('fieldRegex').value.trim();

  if (!key || !label) {
    showToast('Chave e rótulo do campo são obrigatórios.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/admin/profile-fields', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, label, field_type, placeholder, is_required, validation_regex })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Requisito cadastral "${label}" salvo com sucesso!`, 'success');
      document.getElementById('modalAddProfileField').classList.remove('on');
      loadProfileFields();
    } else {
      showToast(data.error || 'Erro ao cadastrar parâmetro obrigatório.', 'error');
    }
  } catch (err) {
    showToast('Erro de comunicação com o servidor.', 'error');
  }
}

async function deleteProfileField(key, label) {
  if (!confirm(`Deseja realmente remover o requisito cadastral "${label}"?`)) return;
  try {
    const res = await fetch(`/api/admin/profile-fields/${key}`, { method: 'DELETE' });
    if (res.ok) {
      showToast(`Requisito "${label}" excluído com sucesso.`, 'success');
      loadProfileFields();
    } else {
      showToast('Erro ao excluir requisito.', 'error');
    }
  } catch (err) {
    showToast('Erro de conexão com o servidor.', 'error');
  }
}

// ==========================================
// CENTRAL DE CARGA DE INSUMOS & UPLOADS
// ==========================================
let uploadsConfigData = null;
let uploadDelegationsList = [];

async function loadUploadsConfig() {
  const grid = document.getElementById('uploadsGrid');
  try {
    const res = await fetch('/api/uploads/config');
    if (res.status === 401 || res.status === 403) {
      window.location.href = '/login/?redirect=/admin/';
      return;
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Erro ao consultar configuração de uploads.');
    
    uploadsConfigData = data;
    
    // Controle de visibilidade administrativa
    const btnDelegations = document.getElementById('btnOpenDelegations');
    if (btnDelegations) {
      btnDelegations.style.display = data.is_admin ? 'inline-flex' : 'none';
    }

    if (!data.is_admin) {
      // Usuário delegado: ajusta cabeçalho e esconde abas de admin puro
      document.getElementById('userTag').textContent = `Conectado como Colaborador Delegado (${escapeHtml(data.user.nome)})`;
      [tabUsersBtn, tabRequestsBtn, tabStatsBtn, tabLogsBtn, tabControlsBtn, tabModulesBtn].forEach(b => b.style.display = 'none');
      const bcast = document.getElementById('btnOpenBroadcast');
      if (bcast) bcast.style.display = 'none';
    } else {
      document.getElementById('userTag').textContent = `Conectado como Responsável pela Ferramenta (${escapeHtml(data.user.nome)})`;
    }

    renderUploadsGrid(data.inputs || []);
  } catch (err) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:24px;color:var(--red)">
        Falha ao carregar insumos: ${escapeHtml(err.message)}
      </div>
    `;
  }
}

function renderUploadsGrid(inputs) {
  const grid = document.getElementById('uploadsGrid');
  if (!inputs.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:var(--ink3);padding:24px">Nenhum insumo configurado no sistema.</div>';
    return;
  }

  document.getElementById('totalUploadsCount').textContent = inputs.length;

  grid.innerHTML = inputs.map(inp => {
    const canUpload = Boolean(inp.can_upload);
    const last = inp.last_upload;
    const hasLast = Boolean(last && last.id);
    const formatsList = Array.isArray(inp.accepted_formats)
      ? inp.accepted_formats
      : (Array.isArray(inp.formats) ? inp.formats : ['.xlsx', '.csv']);
    const formatsStr = formatsList.join(', ');
    const formatsAccept = formatsList.join(',');
    const maxSize = inp.max_size_mb || 50;

    return `
      <div class="upload-card ${!canUpload ? 'disabled' : ''}" id="card_${inp.key}">
        <div class="upload-card-hd">
          <div>
            <div class="upload-card-title">
              <span>${escapeHtml(inp.name)}</span>
            </div>
            <div class="upload-card-desc">${escapeHtml(inp.description)}</div>
          </div>
          <div>
            <span class="badge ${canUpload ? 'aprovado' : 'bloqueado'}" title="${canUpload ? 'Você possui permissão de carga' : 'Sem permissão delegada'}">
              ${canUpload ? 'Autorizado' : 'Apenas Leitura'}
            </span>
          </div>
        </div>

        <div class="upload-card-bd">
          <div class="upload-info-box">
            <div class="upload-info-row">
              <span class="upload-info-label">Painel Alimentado:</span>
              <span class="upload-info-val"><code style="font-size:11px">${escapeHtml(inp.destination_module)}</code></span>
            </div>
            <div class="upload-info-row">
              <span class="upload-info-label">Tabela D1:</span>
              <span class="upload-info-val"><code style="font-size:11px">${escapeHtml(inp.target_table)}</code></span>
            </div>
            <div class="upload-info-row">
              <span class="upload-info-label">Formatos Aceitos:</span>
              <span class="upload-info-val">${escapeHtml(formatsStr)} (Máx ${maxSize}MB)</span>
            </div>
            <div class="upload-info-row" style="margin-top:6px;border-top:1px dashed var(--line2);padding-top:6px">
              <span class="upload-info-label">Último Envio:</span>
              <span class="upload-info-val" style="color:${hasLast ? 'var(--ink)' : 'var(--ink3)'}">
                ${hasLast ? `${escapeHtml(last.filename)} (${formatBytes(last.filesize)})` : 'Nenhum envio registrado'}
              </span>
            </div>
            ${hasLast ? `
              <div class="upload-info-row">
                <span class="upload-info-label">Responsável:</span>
                <span class="upload-info-val" style="font-size:11px">${escapeHtml(last.uploader_name)} (${formatRelativeTime(last.created_at)})</span>
              </div>
            ` : ''}
          </div>

          ${canUpload ? `
            <div class="upload-dropzone" id="dropzone_${inp.key}" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleFileDrop(event, '${inp.key}', ${maxSize})">
              <input type="file" accept="${formatsAccept}" onchange="handleFileSelect(event, '${inp.key}', ${maxSize})">
              <div class="upload-drop-text">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:4px;color:var(--blue)"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                Clique para selecionar ou arraste o arquivo aqui
              </div>
              <div class="upload-drop-sub">Extensões permitidas: ${formatsStr} · Limite ${maxSize}MB</div>
            </div>

            <div class="upload-progress" id="progress_wrap_${inp.key}">
              <div class="upload-progress-bar">
                <div class="upload-progress-fill" id="progress_fill_${inp.key}"></div>
              </div>
              <div class="upload-progress-text">
                <span id="progress_status_${inp.key}">Enviando…</span>
                <span id="progress_pct_${inp.key}">0%</span>
              </div>
            </div>
          ` : `
            <div style="padding:12px;background:#f7f8fa;border:1px dashed var(--line);border-radius:4px;text-align:center;font-size:11.5px;color:var(--ink3)">
              Você não possui permissão delegada para carregar este insumo. Solicite autorização formal ao administrador.
            </div>
          `}
        </div>

        <div class="upload-card-ft" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
          <div>
            ${hasLast ? `
              <a href="/api/uploads/download/${last.id}" class="btn-act" title="Baixar último arquivo enviado">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                Baixar Atual
              </a>
            ` : '<span style="font-size:11px;color:var(--ink3)">Sem arquivo ativo</span>'}
          </div>
          <button class="btn-act" onclick="downloadBaseStructure('${inp.key}')" title="Baixar tabela/modelo com a estrutura de colunas oficial desta base" style="color:var(--blue);font-weight:600">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Baixar Estrutura
          </button>
          <button class="btn-act" onclick="openUploadHistory('${inp.key}', '${escapeHtml(inp.name)}')">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 14"/></svg>
            Histórico
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function downloadBaseStructure(reportKey) {
  if (!reportKey) return;
  const link = document.createElement('a');
  link.href = `/api/uploads/template/${encodeURIComponent(reportKey)}`;
  link.download = `estrutura_base_${reportKey}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e, reportKey, maxMb) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files && files.length > 0) {
    processUploadFile(reportKey, files[0], maxMb);
  }
}

function handleFileSelect(e, reportKey, maxMb) {
  const files = e.target.files;
  if (files && files.length > 0) {
    processUploadFile(reportKey, files[0], maxMb);
  }
  e.target.value = '';
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const dm = 1;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function readSliceAsBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result || '';
      const commaIdx = dataUrl.indexOf(',');
      resolve(commaIdx !== -1 ? dataUrl.slice(commaIdx + 1) : dataUrl);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

async function processUploadFile(reportKey, file, maxMb = 300) {
  if (!file) return;

  const fileSizeMb = file.size / (1024 * 1024);
  if (fileSizeMb > maxMb) {
    showToast(`O arquivo selecionado (${fileSizeMb.toFixed(1)}MB) ultrapassa o limite máximo permitido de ${maxMb}MB.`, 'error');
    return;
  }

  const pWrap = document.getElementById(`progress_wrap_${reportKey}`);
  const pFill = document.getElementById(`progress_fill_${reportKey}`);
  const pStatus = document.getElementById(`progress_status_${reportKey}`);
  const pPct = document.getElementById(`progress_pct_${reportKey}`);

  if (pWrap) pWrap.style.display = 'block';
  if (pFill) {
    pFill.style.background = 'linear-gradient(90deg,#2f7d5d,#3b9b73)';
    pFill.style.width = '3%';
  }
  if (pStatus) pStatus.textContent = 'Iniciando transmissão otimizada…';
  if (pPct) pPct.textContent = '3%';

  try {
    // Slicing nativo em blocos de 512KB para consumo mínimo de memória (<5MB)
    const SLICE_SIZE = 512 * 1024;
    const totalChunks = Math.max(1, Math.ceil(file.size / SLICE_SIZE));
    const uploadId = crypto.randomUUID();

    for (let chunkIdx = 0; chunkIdx < totalChunks; chunkIdx++) {
      const start = chunkIdx * SLICE_SIZE;
      const end = Math.min(start + SLICE_SIZE, file.size);
      const sliceBlob = file.slice(start, end);
      const chunkBase64 = await readSliceAsBase64(sliceBlob);

      const pct = Math.round(((chunkIdx + 1) / totalChunks) * 100);
      if (pFill) pFill.style.width = `${pct}%`;
      if (pStatus) pStatus.textContent = `Enviando bloco ${chunkIdx + 1} de ${totalChunks} (${(end / (1024*1024)).toFixed(1)}MB / ${fileSizeMb.toFixed(1)}MB)…`;
      if (pPct) pPct.textContent = `${pct}%`;

      const payload = {
        upload_id: uploadId,
        report_key: reportKey,
        filename: file.name,
        filesize: file.size,
        filetype: file.type || 'application/octet-stream',
        chunk_index: chunkIdx,
        total_chunks: totalChunks,
        chunk_data: chunkBase64,
        records_count: 0,
        metadata: {
          original_name: file.name,
          client_uploaded_at: new Date().toISOString()
        }
      };

      const res = await fetch('/api/uploads/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const resData = await res.json();
      if (!res.ok) {
        throw new Error(resData.error || 'Erro durante envio de dados ao servidor.');
      }
    }

    if (pStatus) pStatus.textContent = 'Carga concluída com sucesso!';
    showToast(`Insumo "${file.name}" carregado com sucesso!`, 'success');
    setTimeout(() => {
      if (pWrap) pWrap.style.display = 'none';
      loadUploadsConfig();
    }, 1200);

  } catch (err) {
    if (pStatus) pStatus.textContent = `Erro: ${err.message}`;
    if (pFill) pFill.style.background = 'var(--red)';
    showToast(`Erro ao enviar insumo: ${err.message}`, 'error');
  }
}

// Histórico de Envios
async function openUploadHistory(reportKey, reportName) {
  const modal = document.getElementById('modalUploadHistory');
  const title = document.getElementById('modalUploadHistoryTitle');
  const tbody = document.getElementById('uploadHistoryTbody');

  title.textContent = `Histórico de Cargas: ${reportName}`;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--ink3);padding:20px">Consultando histórico…</td></tr>';
  modal.classList.add('on');

  try {
    const res = await fetch(`/api/uploads/history?report=${encodeURIComponent(reportKey)}`);
    const list = await res.json();
    if (!res.ok) throw new Error(list.error || 'Erro ao consultar histórico.');

    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--ink3);padding:20px">Nenhum envio realizado para este relatório até o momento.</td></tr>';
      return;
    }

    tbody.innerHTML = list.map(item => `
      <tr>
        <td style="white-space:nowrap;font-size:11.5px">${formatRelativeTime(item.created_at)}</td>
        <td><strong>${escapeHtml(item.filename)}</strong></td>
        <td style="white-space:nowrap">${formatBytes(item.filesize)}</td>
        <td style="font-size:11.5px">${escapeHtml(item.uploader_name)}</td>
        <td><span class="badge ${item.status === 'completed' ? 'aprovado' : 'bloqueado'}">${escapeHtml(item.status)}</span></td>
        <td style="text-align:right">
          <a href="/api/uploads/download/${item.id}" class="btn-act" style="font-size:11px" download="${escapeHtml(item.filename)}">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download
          </a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--red);padding:20px">Falha: ${escapeHtml(err.message)}</td></tr>`;
  }
}

// Gestão de Delegações
async function openUploadDelegations() {
  const modal = document.getElementById('modalUploadDelegations');
  modal.classList.add('on');
  populateDelegationUserSelect();
  loadUploadDelegations();
}

function populateDelegationUserSelect() {
  const select = document.getElementById('delegationUserSelect');
  if (!select) return;
  if (!allUsers || !allUsers.length) {
    select.innerHTML = '<option value="">Nenhum usuário carregado</option>';
    return;
  }
  const approvedUsers = allUsers.filter(u => u.status === 'aprovado' && !u.is_admin);
  select.innerHTML = '<option value="">Selecione um colaborador…</option>' + approvedUsers.map(u => `
    <option value="${u.id}">${escapeHtml(u.nome_completo)} — ${escapeHtml(u.email_claro)} (${escapeHtml(u.funcao || u.area || 'Colaborador')})</option>
  `).join('');
}

async function loadUploadDelegations() {
  const tbody = document.getElementById('delegationsTbody');
  try {
    const res = await fetch('/api/uploads/delegations');
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Erro ao listar delegações.');

    uploadDelegationsList = data;
    document.getElementById('delegationsCount').textContent = data.length;

    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--ink3);padding:16px">Nenhum colaborador delegado no momento. Apenas administradores podem enviar insumos.</td></tr>';
      return;
    }

    tbody.innerHTML = data.map(del => {
      const scopeLabel = del.scope_type === 'ALL' ? 'Todos os Relatórios & Insumos' : del.scope_type;
      return `
        <tr>
          <td>
            <strong>${escapeHtml(del.delegated_user_name)}</strong>
            <div style="font-size:11px;color:var(--ink2)">${escapeHtml(del.delegated_user_email)}</div>
          </td>
          <td><span class="badge ${del.scope_type === 'ALL' ? 'admin' : 'aprovado'}">${escapeHtml(scopeLabel)}</span></td>
          <td style="font-size:11.5px;white-space:nowrap">${formatRelativeTime(del.created_at)}</td>
          <td style="text-align:right">
            <button class="btn-act danger" onclick="revokeDelegation('${del.id}', '${escapeHtml(del.delegated_user_name)}')">
              Revogar
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--red);padding:16px">Erro: ${escapeHtml(err.message)}</td></tr>`;
  }
}

async function createDelegation() {
  const userSelect = document.getElementById('delegationUserSelect');
  const scopeSelect = document.getElementById('delegationScopeSelect');

  const userId = userSelect.value;
  const scope = scopeSelect.value;

  if (!userId) {
    showToast('Por favor, selecione um colaborador.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/uploads/delegations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delegated_user_id: userId, scope_type: scope })
    });
    const data = await res.json();
    if (res.ok) {
      userSelect.value = '';
      showToast('Delegação de upload concedida com sucesso!', 'success');
      loadUploadDelegations();
      loadUploadsConfig();
    } else {
      showToast(data.error || 'Erro ao conceder delegação.', 'error');
    }
  } catch (err) {
    showToast('Falha na comunicação com o servidor.', 'error');
  }
}

async function revokeDelegation(delId, userName) {
  if (!confirm(`Deseja realmente revogar a delegação de upload de "${userName}"?`)) return;

  try {
    const res = await fetch(`/api/uploads/delegations/${delId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast(`Delegação de "${userName}" revogada com sucesso.`, 'success');
      loadUploadDelegations();
      loadUploadsConfig();
    } else {
      showToast('Erro ao revogar delegação.', 'error');
    }
  } catch (err) {
    showToast('Falha de conexão com o servidor.', 'error');
  }
}

// ==========================================
// 9. CENTRAL DE NOTIFICAÇÕES CORPORATIVAS
// ==========================================
let allAdminNotifications = [];

const NOTIF_TYPE_CONFIG = {
  info: { label: 'Informativo', color: '#0f5499', bg: '#e8f0fe', border: '#b8d5fa' },
  update: { label: 'Lançamento', color: '#634199', bg: '#f3e8fd', border: '#dec6f8' },
  security: { label: 'Segurança', color: '#be185d', bg: '#fce7f3', border: '#f9a8d4' },
  warning: { label: 'Alerta', color: '#c05621', bg: '#fef3c7', border: '#fde68a' },
  success: { label: 'Sucesso', color: '#237804', bg: '#eaf2ec', border: '#b8dcbf' }
};

const NOTIF_PRESETS = {
  first_login: {
    type: 'info',
    audience: 'ALL',
    title: 'Bem-vindo ao PEP HUB Regional Norte',
    message: 'Explore os módulos analíticos de Churn Safra, FPD, Churn BL e a nova Evolução da Carteira. Mantenha seu perfil corporativo sempre atualizado e com número funcional.',
    action_url: '/perfil/',
    action_label: 'Acessar Meu Perfil'
  },
  password_change: {
    type: 'security',
    audience: 'ALL',
    title: 'Segurança Corporativa: Lembrete de Alteração de Senha',
    message: 'Por diretriz de conformidade da Regional Norte, recomendamos atualizar sua senha de acesso a cada 90 dias para salvaguardar suas credenciais.',
    action_url: '/redefinir-senha/',
    action_label: 'Atualizar Senha Agora'
  },
  new_report: {
    type: 'update',
    audience: 'ALL',
    title: 'Novo Painel Disponível: Evolução da Carteira Safra',
    message: 'Já está em produção o novo painel de Evolução da Carteira com acompanhamento de saldos ativos, migração, churn involuntário e ticket médio por segmento.',
    action_url: '/evolucao-carteira/',
    action_label: 'Explorar Novo Painel'
  },
  maintenance: {
    type: 'warning',
    audience: 'ALL',
    title: 'Janela Programada de Consolidação de Safra',
    message: 'Informamos que realizaremos a consolidação e carga de novos dados no próximo fim de semana. O ambiente permanecerá disponível para consultas operacionais.',
    action_url: '',
    action_label: ''
  }
};

async function loadAdminNotifications() {
  const tbody = document.getElementById('notificationsTbody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--ink3);padding:24px">Carregando notificações…</td></tr>`;
  }

  try {
    const res = await fetch('/api/admin/notifications');
    if (!res.ok) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--red);padding:24px">Falha ao carregar notificações.</td></tr>`;
      return;
    }
    const data = await res.json();
    allAdminNotifications = Array.isArray(data) ? data : (data.notifications || []);
    renderAdminNotifications();
  } catch (err) {
    console.error('Erro loadAdminNotifications:', err);
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--red);padding:24px">Erro de comunicação com o servidor.</td></tr>`;
  }
}

function renderAdminNotifications() {
  const tbody = document.getElementById('notificationsTbody');
  if (!tbody) return;

  const total = allAdminNotifications.length;
  const activeCount = allAdminNotifications.filter(n => n.is_active === 1 || n.is_active === true).length;
  const totalReads = allAdminNotifications.reduce((acc, n) => acc + (Number(n.read_count) || 0), 0);
  const totalDismisses = allAdminNotifications.reduce((acc, n) => acc + (Number(n.dismissed_count) || 0), 0);

  const kpiAct = document.getElementById('kpiNotifActive');
  const kpiAud = document.getElementById('kpiNotifAudience');
  const kpiReads = document.getElementById('kpiNotifReads');
  const kpiDism = document.getElementById('kpiNotifDismisses');

  if (kpiAct) kpiAct.textContent = activeCount;
  if (kpiAud) kpiAud.textContent = total;
  if (kpiReads) kpiReads.textContent = totalReads.toLocaleString('pt-BR');
  if (kpiDism) kpiDism.textContent = totalDismisses.toLocaleString('pt-BR');

  if (total === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--ink3);padding:32px">Nenhuma notificação corporativa cadastrada no momento.<br><span style="font-size:11px">Utilize os botões acima para criar uma nova notificação ou carregar um preset em 1 clique.</span></td></tr>`;
    return;
  }

  tbody.innerHTML = allAdminNotifications.map(n => {
    const typeCfg = NOTIF_TYPE_CONFIG[n.type] || NOTIF_TYPE_CONFIG.info;
    const isActive = n.is_active === 1 || n.is_active === true;
    const isScheduled = n.starts_at && new Date(n.starts_at) > new Date();
    const isExpired = n.expires_at && new Date(n.expires_at) < new Date();

    let statusBadge = '';
    if (!isActive) {
      statusBadge = `<span class="badge-mod suspenso" style="font-size:10.5px">Inativa</span>`;
    } else if (isExpired) {
      statusBadge = `<span class="badge-mod oculto" style="font-size:10.5px">Expirada</span>`;
    } else if (isScheduled) {
      statusBadge = `<span class="badge-mod em_andamento" style="font-size:10.5px">Agendada</span>`;
    } else {
      statusBadge = `<span class="badge-mod ativo" style="font-size:10.5px">Ativa</span>`;
    }

    const audLabel = n.audience === 'admin' ? 'Apenas Admins' : (n.audience === 'regular' ? 'Não-Admins' : 'Todos');

    const vigencia = [];
    if (n.starts_at) {
      vigencia.push(`Início: ${new Date(n.starts_at).toLocaleDateString('pt-BR', {day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}`);
    }
    if (n.expires_at) {
      vigencia.push(`Fim: ${new Date(n.expires_at).toLocaleDateString('pt-BR', {day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}`);
    }
    const vigenciaStr = vigencia.length > 0 ? vigencia.join('<br>') : '<span style="color:var(--ink3)">Sem expiração</span>';

    const safeTitle = (n.title || '').replace(/"/g, '&quot;');

    return `
      <tr>
        <td>
          <span style="display:inline-block;padding:3px 8px;border-radius:3px;font-size:10.5px;font-weight:700;background:${typeCfg.bg};color:${typeCfg.color};border:1px solid ${typeCfg.border}">
            ${typeCfg.label}
          </span>
        </td>
        <td>
          <div style="font-weight:700;color:var(--ink);font-size:12px;margin-bottom:2px">${escapeHtml(n.title)}</div>
          <div style="font-size:11px;color:var(--ink2);line-height:1.35;max-width:340px;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">
            ${escapeHtml(n.message)}
          </div>
          ${n.action_url ? `<div style="font-size:10.5px;color:var(--blue);margin-top:3px">↳ Destino: <a href="${escapeHtml(n.action_url)}" target="_blank" style="color:var(--blue);text-decoration:underline">${escapeHtml(n.action_label || n.action_url)}</a></div>` : ''}
        </td>
        <td>
          <span style="font-size:11px;font-weight:600;color:var(--ink)">${audLabel}</span>
        </td>
        <td style="font-size:10.5px;color:var(--ink2);line-height:1.3">
          ${vigenciaStr}
        </td>
        <td>
          <div style="font-size:11px;font-weight:600;color:var(--ink)">
            <span style="color:#2f7d5d">👁️ ${n.read_count || 0}</span> lidas
          </div>
          <div style="font-size:10.5px;color:var(--ink3);margin-top:1px">
            ✖ ${n.dismissed_count || 0} dispensadas
          </div>
        </td>
        <td>
          ${statusBadge}
        </td>
        <td style="text-align:right">
          <div class="actions-cell">
            <button class="btn-act ${isActive ? 'danger' : 'approve'}" onclick="toggleNotificationStatus('${n.id}')" title="${isActive ? 'Desativar notificação' : 'Ativar notificação'}">
              ${isActive ? 'Pausar' : 'Ativar'}
            </button>
            <button class="btn-act primary" onclick="openNotificationModal(null, '${n.id}')" title="Editar notificação">
              Editar
            </button>
            <button class="btn-act danger" onclick="deleteNotification('${n.id}', '${safeTitle}')" title="Excluir notificação">
              Excluir
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function openNotificationModal(presetKey = null, notifId = null) {
  const modal = document.getElementById('modalNotification');
  if (!modal) return;

  const titleEl = document.getElementById('modalNotificationTitle');
  const notifIdInput = document.getElementById('notifId');
  const presetSelect = document.getElementById('notifPreset');

  if (notifId) {
    const notif = allAdminNotifications.find(n => n.id === notifId);
    if (!notif) return;

    if (titleEl) titleEl.textContent = 'Editar Notificação Corporativa';
    if (notifIdInput) notifIdInput.value = notif.id;
    if (presetSelect) presetSelect.value = 'custom';

    document.getElementById('notifType').value = notif.type || 'info';
    document.getElementById('notifAudience').value = notif.audience || 'ALL';
    document.getElementById('notifTitle').value = notif.title || '';
    document.getElementById('notifMessage').value = notif.message || '';
    document.getElementById('notifActionUrl').value = notif.action_url || '';
    document.getElementById('notifActionLabel').value = notif.action_label || '';

    const formatDt = (iso) => iso ? new Date(iso).toISOString().slice(0, 16) : '';
    document.getElementById('notifStartsAt').value = formatDt(notif.starts_at);
    document.getElementById('notifExpiresAt').value = formatDt(notif.expires_at);
    document.getElementById('notifActive').checked = notif.is_active === 1 || notif.is_active === true;
  } else {
    if (titleEl) titleEl.textContent = 'Criar Notificação Corporativa';
    if (notifIdInput) notifIdInput.value = '';
    
    // Resetar campos
    document.getElementById('notifType').value = 'info';
    document.getElementById('notifAudience').value = 'ALL';
    document.getElementById('notifTitle').value = '';
    document.getElementById('notifMessage').value = '';
    document.getElementById('notifActionUrl').value = '';
    document.getElementById('notifActionLabel').value = '';
    document.getElementById('notifStartsAt').value = '';
    document.getElementById('notifExpiresAt').value = '';
    document.getElementById('notifActive').checked = true;

    if (presetKey && NOTIF_PRESETS[presetKey]) {
      if (presetSelect) presetSelect.value = presetKey;
      applyNotificationPreset(presetKey);
    } else {
      if (presetSelect) presetSelect.value = 'custom';
    }
  }

  updateNotifModalPreview();
  modal.classList.add('on');
}

function applyNotificationPreset(presetKey) {
  if (!presetKey || presetKey === 'custom') return;
  const p = NOTIF_PRESETS[presetKey];
  if (!p) return;

  if (p.type) document.getElementById('notifType').value = p.type;
  if (p.audience) document.getElementById('notifAudience').value = p.audience;
  if (p.title) document.getElementById('notifTitle').value = p.title;
  if (p.message) document.getElementById('notifMessage').value = p.message;
  if (p.action_url !== undefined) document.getElementById('notifActionUrl').value = p.action_url;
  if (p.action_label !== undefined) document.getElementById('notifActionLabel').value = p.action_label;

  updateNotifModalPreview();
}

function updateNotifModalPreview() {
  const box = document.getElementById('notifModalPreviewBox');
  if (!box) return;

  const type = document.getElementById('notifType').value || 'info';
  const title = document.getElementById('notifTitle').value.trim() || 'Título da Notificação';
  const msg = document.getElementById('notifMessage').value.trim() || 'Texto explicativo ou comunicado direcionado ao colaborador…';
  const actionUrl = document.getElementById('notifActionUrl').value.trim();
  const actionLabel = document.getElementById('notifActionLabel').value.trim() || 'Acessar Link';

  const typeCfg = NOTIF_TYPE_CONFIG[type] || NOTIF_TYPE_CONFIG.info;

  box.innerHTML = `
    <div style="background:#fff;border:1px solid #dfe3e8;border-left:4px solid ${typeCfg.color};border-radius:4px;padding:12px;position:relative">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px">
        <span style="font-size:10px;font-weight:700;text-transform:uppercase;padding:2px 6px;border-radius:2px;background:${typeCfg.bg};color:${typeCfg.color};border:1px solid ${typeCfg.border}">
          ${typeCfg.label}
        </span>
        <span style="font-size:10px;color:var(--ink3)">Agora mesmo</span>
      </div>
      <div style="font-size:12.5px;font-weight:700;color:var(--ink);margin-bottom:4px">
        ${escapeHtml(title)}
      </div>
      <div style="font-size:11.5px;color:var(--ink2);line-height:1.4">
        ${escapeHtml(msg)}
      </div>
      ${actionUrl ? `
        <div style="margin-top:10px">
          <span style="display:inline-block;padding:5px 12px;background:#1b2430;color:#fff;font-size:11px;font-weight:700;border-radius:3px">
            ${escapeHtml(actionLabel)} →
          </span>
        </div>
      ` : ''}
    </div>
  `;
}

async function saveNotification() {
  const id = document.getElementById('notifId').value.trim();
  const type = document.getElementById('notifType').value;
  const audience = document.getElementById('notifAudience').value;
  const title = document.getElementById('notifTitle').value.trim();
  const message = document.getElementById('notifMessage').value.trim();
  const action_url = document.getElementById('notifActionUrl').value.trim() || null;
  const action_label = document.getElementById('notifActionLabel').value.trim() || null;
  const starts_at = document.getElementById('notifStartsAt').value || null;
  const expires_at = document.getElementById('notifExpiresAt').value || null;
  const is_active = document.getElementById('notifActive').checked ? 1 : 0;

  if (!title) {
    showToast('Informe o título do comunicado.', 'error');
    document.getElementById('notifTitle').focus();
    return;
  }
  if (!message) {
    showToast('Informe a mensagem da notificação.', 'error');
    document.getElementById('notifMessage').focus();
    return;
  }

  const payload = {
    type,
    audience,
    title,
    message,
    action_url,
    action_label,
    starts_at: starts_at ? new Date(starts_at).toISOString() : null,
    expires_at: expires_at ? new Date(expires_at).toISOString() : null,
    is_active
  };

  const btn = document.getElementById('btnSaveNotification');
  if (btn) btn.disabled = true;

  try {
    const url = id ? `/api/admin/notifications/${id}` : '/api/admin/notifications';
    const method = id ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      showToast(id ? 'Notificação atualizada com sucesso!' : 'Notificação corporativa criada com sucesso!', 'success');
      document.getElementById('modalNotification').classList.remove('on');
      loadAdminNotifications();
    } else {
      showToast(data.error || 'Erro ao salvar notificação.', 'error');
    }
  } catch (err) {
    console.error('Erro saveNotification:', err);
    showToast('Falha na comunicação com o servidor.', 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function toggleNotificationStatus(id) {
  try {
    const res = await fetch(`/api/admin/notifications/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast(`Status da notificação alterado para: ${data.is_active ? 'Ativa' : 'Inativa'}.`, 'success');
      loadAdminNotifications();
    } else {
      showToast(data.error || 'Erro ao alterar status.', 'error');
    }
  } catch (err) {
    showToast('Falha de conexão com o servidor.', 'error');
  }
}

async function deleteNotification(id, title) {
  if (!confirm(`Deseja realmente excluir a notificação "${title}"?\nEsta ação não poderá ser desfeita.`)) return;

  try {
    const res = await fetch(`/api/admin/notifications/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok) {
      showToast('Notificação excluída com sucesso.', 'success');
      loadAdminNotifications();
    } else {
      showToast(data.error || 'Erro ao excluir notificação.', 'error');
    }
  } catch (err) {
    showToast('Falha de conexão com o servidor.', 'error');
  }
}

// Expor métodos globais para uso inline no HTML
window.loadAdminNotifications = loadAdminNotifications;
window.openNotificationModal = openNotificationModal;
window.applyNotificationPreset = applyNotificationPreset;
window.updateNotifModalPreview = updateNotifModalPreview;
window.saveNotification = saveNotification;
window.toggleNotificationStatus = toggleNotificationStatus;
window.deleteNotification = deleteNotification;

async function initAdminPanel() {
  setDatePreset('30d');
  try {
    const res = await fetch('/api/uploads/config');
    if (res.ok) {
      const cfg = await res.json();
      uploadsConfigData = cfg;
      if (!cfg.is_admin) {
        showTab('uploads');
        return;
      }
    }
  } catch (_) {}

  // Fluxo normal para administradores plenos:
  // Carrega catálogo de módulos canônicos primeiro, sincronizando todas as visões
  await loadModules();
  loadUsers();
  loadSystemControls();
  loadProfileFields();
  loadUploadsConfig();
  loadAdminNotifications();

  // O botão "Online" do cabeçalho é montado pelo header-widget.js ([data-pephub-online])
  refreshPendingRequestsCount();
}

initAdminPanel();