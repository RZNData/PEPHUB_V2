/**
 * Sub-roteador de Notificações Corporativas & Presets Administrativos
 * Regional Norte — Pephub Plataforma
 *
 * Rotas de Usuário:
 *   GET  /api/notifications               (retorna notificações elegíveis para o usuário atual)
 *   POST /api/notifications/:id/read      (marca como lida)
 *   POST /api/notifications/:id/dismiss   (dispensa a notificação)
 *   POST /api/notifications/read-all      (marca todas como lidas)
 *
 * Rotas Administrativas:
 *   GET    /api/admin/notifications       (lista todas com métricas de leitura/dispensa)
 *   POST   /api/admin/notifications       (cria nova notificação / preset)
 *   PUT    /api/admin/notifications/:id   (atualiza notificação existente)
 *   DELETE /api/admin/notifications/:id   (exclui notificação)
 *   POST   /api/admin/notifications/:id/toggle (alterna ativo/inativo)
 */

import {
  json,
  getSessionUser,
  randomHex,
  SECURITY_HEADERS,
} from '../utils/security.js';

// Assegura criação das tabelas e índices
export async function ensureNotificationsTables(env) {
  if (!env || !env.DB) return;
  try {
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'info',
        preset TEXT NOT NULL DEFAULT 'custom',
        target_audience TEXT NOT NULL DEFAULT 'ALL',
        action_url TEXT,
        action_label TEXT,
        starts_at TEXT,
        expires_at TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_by TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS user_notifications_read (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        notification_id TEXT NOT NULL,
        read_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        dismissed INTEGER NOT NULL DEFAULT 0,
        UNIQUE(user_id, notification_id)
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS user_daily_popups_seen (
        user_id TEXT NOT NULL,
        notification_id TEXT NOT NULL,
        seen_date TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(user_id, notification_id, seen_date)
      )
    `).run().catch(() => {});

    // Adiciona colunas para popup de 1º logon e prioridade
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN is_popup INTEGER NOT NULL DEFAULT 0").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN priority TEXT NOT NULL DEFAULT 'normal'").run().catch(() => {});
    // Adiciona colunas para segmentação granular de público
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN target_type TEXT NOT NULL DEFAULT 'all'").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN target_users TEXT").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN target_roles TEXT").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE notifications ADD COLUMN target_areas TEXT").run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_notifications_active ON notifications(is_active, starts_at, expires_at)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_user_notif_read_user ON user_notifications_read(user_id, notification_id)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_popup_seen_user ON user_daily_popups_seen(user_id, seen_date)
    `).run().catch(() => {});

    // Semeia presets institucionais se não houver notificações
    const countRow = await env.DB.prepare('SELECT COUNT(*) as c FROM notifications').first().catch(() => null);
    if (countRow && countRow.c === 0) {
      await seedInitialPresets(env);
    }
  } catch (err) {
    console.error('Erro em ensureNotificationsTables:', err);
  }
}

// Avalia se uma notificação é elegível para o usuário com base em pessoa, cargo, setor ou regra global
export function isNotificationEligible(item, user) {
  if (!user) return false;
  const isAdmin = Boolean(user.is_admin);
  const targetType = String(item.target_type || '').trim().toLowerCase();

  // 1. Verificação por tipo estruturado
  if (targetType === 'admin') {
    return isAdmin;
  }
  if (targetType === 'regular') {
    return !isAdmin;
  }
  if (targetType === 'users') {
    let allowedUsers = [];
    try {
      if (typeof item.target_users === 'string') {
        const trimmed = item.target_users.trim();
        if (trimmed.startsWith('[')) {
          allowedUsers = JSON.parse(trimmed);
        } else {
          allowedUsers = trimmed.split(',').map(s => s.trim());
        }
      } else if (Array.isArray(item.target_users)) {
        allowedUsers = item.target_users;
      }
    } catch (_) {
      allowedUsers = [];
    }
    const cleanAllowed = allowedUsers.map(u => String(u).trim().toLowerCase());
    const uid = String(user.id || '').trim().toLowerCase();
    const ulogin = String(user.login_claro || '').trim().toLowerCase();
    const uemail = String(user.email_claro || '').trim().toLowerCase();
    return cleanAllowed.includes(uid) || cleanAllowed.includes(ulogin) || cleanAllowed.includes(uemail);
  }
  if (targetType === 'roles') {
    let allowedRoles = [];
    try {
      if (typeof item.target_roles === 'string') {
        const trimmed = item.target_roles.trim();
        if (trimmed.startsWith('[')) {
          allowedRoles = JSON.parse(trimmed);
        } else {
          allowedRoles = trimmed.split(',').map(s => s.trim());
        }
      } else if (Array.isArray(item.target_roles)) {
        allowedRoles = item.target_roles;
      }
    } catch (_) {
      allowedRoles = [];
    }
    const cleanAllowedRoles = allowedRoles.map(r => String(r).trim().toUpperCase());
    const userRole = String(user.funcao || '').trim().toUpperCase();
    return cleanAllowedRoles.includes(userRole);
  }
  if (targetType === 'areas') {
    let allowedAreas = [];
    try {
      if (typeof item.target_areas === 'string') {
        const trimmed = item.target_areas.trim();
        if (trimmed.startsWith('[')) {
          allowedAreas = JSON.parse(trimmed);
        } else {
          allowedAreas = trimmed.split(',').map(s => s.trim());
        }
      } else if (Array.isArray(item.target_areas)) {
        allowedAreas = item.target_areas;
      }
    } catch (_) {
      allowedAreas = [];
    }
    const cleanAllowedAreas = allowedAreas.map(a => String(a).trim().toUpperCase());
    const userArea = String(user.area || '').trim().toUpperCase();
    return cleanAllowedAreas.includes(userArea);
  }
  if (targetType === 'all') {
    return true;
  }

  // 2. Fallback para target_audience textual legado
  const aud = String(item.target_audience || 'ALL').trim();
  const audUpper = aud.toUpperCase();
  if (audUpper === 'ALL' || audUpper === '') return true;
  if (audUpper === 'ADMIN') return isAdmin;
  if (audUpper === 'REGULAR') return !isAdmin;

  if (audUpper.startsWith('USERS:')) {
    const raw = aud.substring(6).trim();
    let ids = [];
    try {
      ids = raw.startsWith('[') ? JSON.parse(raw) : raw.split(',').map(s => s.trim());
    } catch (_) {
      ids = raw.split(',').map(s => s.trim());
    }
    const cleanIds = ids.map(s => String(s).trim().toLowerCase());
    const uid = String(user.id || '').trim().toLowerCase();
    const ulogin = String(user.login_claro || '').trim().toLowerCase();
    const uemail = String(user.email_claro || '').trim().toLowerCase();
    return cleanIds.includes(uid) || cleanIds.includes(ulogin) || cleanIds.includes(uemail);
  }

  if (audUpper.startsWith('ROLES:')) {
    const raw = aud.substring(6).trim();
    let roles = [];
    try {
      roles = raw.startsWith('[') ? JSON.parse(raw) : raw.split(',').map(s => s.trim());
    } catch (_) {
      roles = raw.split(',').map(s => s.trim());
    }
    const cleanRoles = roles.map(s => String(s).trim().toUpperCase());
    const userRole = String(user.funcao || '').trim().toUpperCase();
    return cleanRoles.includes(userRole);
  }

  if (audUpper.startsWith('AREAS:')) {
    const raw = aud.substring(6).trim();
    let areas = [];
    try {
      areas = raw.startsWith('[') ? JSON.parse(raw) : raw.split(',').map(s => s.trim());
    } catch (_) {
      areas = raw.split(',').map(s => s.trim());
    }
    const cleanAreas = areas.map(s => String(s).trim().toUpperCase());
    const userArea = String(user.area || '').trim().toUpperCase();
    return cleanAreas.includes(userArea);
  }

  if (user.area && user.area.toUpperCase() === audUpper) {
    return true;
  }

  return false;
}

// Semeador de Presets Oficiais de Lançamento
async function seedInitialPresets(env) {
  const presets = [
    {
      id: 'notif_welcome_default',
      title: 'Boas-vindas ao PEP HUB — Regional Norte',
      message: 'Plataforma oficial integrada de acompanhamento de Churn Safra, FPD, Market Share e Qualidade da Regional Norte. Consulte os painéis analíticos oficiais e mantenha suas decisões orientadas a dados.',
      type: 'info',
      preset: 'first_login',
      target_audience: 'ALL',
      action_url: '/',
      action_label: 'Conhecer Catálogo de Painéis',
      is_active: 1,
      created_by: 'SISTEMA'
    },
    {
      id: 'notif_evolucao_carteira',
      title: 'Novo Painel Oficial: Evolução da Carteira Móvel & B2B',
      message: 'Está disponível o novo diagnóstico analítico de Gross Bruto, Descontos, Churn Involuntário, Churn Voluntário, Matriz de Migrações e Net Adds (com liderança da Regional Norte em Consumo no Brasil).',
      type: 'update',
      preset: 'new_report',
      target_audience: 'ALL',
      action_url: '/evolucao-carteira/',
      action_label: 'Acessar Relatório Oficial',
      is_active: 1,
      created_by: 'SISTEMA'
    },
    {
      id: 'notif_security_reminder',
      title: 'Segurança Corporativa: Proteja sua Credencial',
      message: 'Recomendamos manter sua senha corporativa atualizada e não compartilhá-la. A plataforma conta com auditoria estrita de acessos em conformidade com as políticas de segurança da Claro.',
      type: 'security',
      preset: 'password_change',
      target_audience: 'ALL',
      action_url: '/forgot-password/',
      action_label: 'Redefinir Minha Senha',
      is_active: 1,
      created_by: 'SISTEMA'
    }
  ];

  for (const p of presets) {
    await env.DB.prepare(`
      INSERT OR IGNORE INTO notifications (id, title, message, type, preset, target_audience, action_url, action_label, is_active, created_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(p.id, p.title, p.message, p.type, p.preset, p.target_audience, p.action_url, p.action_label, p.is_active, p.created_by)
      .run().catch(() => {});
  }
}

export async function handleNotificationRoutes(request, env, url, pathname) {
  // Ignora se não for rota deste roteador
  if (!pathname.startsWith('/api/notifications') && !pathname.startsWith('/api/admin/notifications')) {
    return null;
  }

  // 1. Verificação de Sessão do Usuário
  const user = await getSessionUser(request, env);
  if (!user || user.status !== 'aprovado') {
    return json({ error: 'Não autorizado. Sessão inválida ou expirada.' }, 401);
  }

  const method = request.method.toUpperCase();

  // =========================================================================
  // ROTAS ADMINISTRATIVAS (/api/admin/notifications/*)
  // =========================================================================
  if (pathname.startsWith('/api/admin/notifications')) {
    if (!Boolean(user.is_admin)) {
      return json({ error: 'Acesso restrito a administradores corporativos.' }, 403);
    }

    await ensureNotificationsTables(env);

    // GET /api/admin/notifications — Lista todas as notificações com engajamento
    if (pathname === '/api/admin/notifications' && method === 'GET') {
      try {
        const query = `
          SELECT 
            n.*,
            (SELECT COUNT(*) FROM user_notifications_read r WHERE r.notification_id = n.id) as read_count,
            (SELECT COUNT(*) FROM user_notifications_read r WHERE r.notification_id = n.id AND r.dismissed = 1) as dismiss_count,
            (SELECT COUNT(*) FROM user_notifications_read r WHERE r.notification_id = n.id AND r.dismissed = 1) as dismissed_count
          FROM notifications n
          ORDER BY n.created_at DESC
        `;
        const { results } = await env.DB.prepare(query).all();
        return json({
          success: true,
          notifications: results || []
        });
      } catch (err) {
        console.error('Erro ao listar notificações admin:', err);
        return json({ error: 'Falha ao consultar notificações no banco de dados.' }, 500);
      }
    }

    // POST /api/admin/notifications — Cria nova notificação ou preset
    if (pathname === '/api/admin/notifications' && method === 'POST') {
      try {
        const body = await request.json().catch(() => ({}));
        const {
          title,
          message,
          type = 'info',
          preset = 'custom',
          target_audience = 'ALL',
          audience,
          target_type = 'all',
          target_users = null,
          target_roles = null,
          target_areas = null,
          action_url = '',
          action_label = '',
          starts_at = null,
          expires_at = null,
          is_active = 1,
          is_popup = 0,
          priority = 'normal'
        } = body;

        if (!title || !title.trim() || !message || !message.trim()) {
          return json({ error: 'Título e mensagem são campos obrigatórios.' }, 400);
        }

        const notifId = `notif_${randomHex(8)}`;
        const validTypes = ['info', 'warning', 'success', 'update', 'security'];
        const cleanType = validTypes.includes(type) ? type : 'info';
        const validPriorities = ['normal', 'alta', 'urgente'];
        const cleanPriority = validPriorities.includes(priority) ? priority : 'normal';

        // Normalização de segmentação
        let cleanTargetType = String(target_type || '').toLowerCase();
        if (!cleanTargetType || cleanTargetType === 'undefined') {
          const rawAud = String(target_audience || audience || 'ALL').toUpperCase();
          if (rawAud === 'ADMIN') cleanTargetType = 'admin';
          else if (rawAud === 'REGULAR') cleanTargetType = 'regular';
          else if (rawAud.startsWith('USERS:')) cleanTargetType = 'users';
          else if (rawAud.startsWith('ROLES:')) cleanTargetType = 'roles';
          else if (rawAud.startsWith('AREAS:')) cleanTargetType = 'areas';
          else cleanTargetType = 'all';
        }

        const cleanTargetUsers = target_users ? (typeof target_users === 'string' ? target_users : JSON.stringify(target_users)) : null;
        const cleanTargetRoles = target_roles ? (typeof target_roles === 'string' ? target_roles : JSON.stringify(target_roles)) : null;
        const cleanTargetAreas = target_areas ? (typeof target_areas === 'string' ? target_areas : JSON.stringify(target_areas)) : null;

        let cleanAudience = target_audience || audience || 'ALL';
        if (cleanTargetType === 'users' && cleanTargetUsers) {
          cleanAudience = `USERS:${cleanTargetUsers}`;
        } else if (cleanTargetType === 'roles' && cleanTargetRoles) {
          cleanAudience = `ROLES:${cleanTargetRoles}`;
        } else if (cleanTargetType === 'areas' && cleanTargetAreas) {
          cleanAudience = `AREAS:${cleanTargetAreas}`;
        } else if (cleanTargetType === 'admin') {
          cleanAudience = 'admin';
        } else if (cleanTargetType === 'regular') {
          cleanAudience = 'regular';
        } else if (cleanTargetType === 'all') {
          cleanAudience = 'ALL';
        }

        await env.DB.prepare(`
          INSERT INTO notifications (
            id, title, message, type, preset, target_audience,
            target_type, target_users, target_roles, target_areas,
            action_url, action_label, starts_at, expires_at, is_active,
            is_popup, priority, created_by
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          notifId,
          title.trim(),
          message.trim(),
          cleanType,
          preset || 'custom',
          cleanAudience,
          cleanTargetType,
          cleanTargetUsers,
          cleanTargetRoles,
          cleanTargetAreas,
          action_url ? action_url.trim() : null,
          action_label ? action_label.trim() : null,
          starts_at || null,
          expires_at || null,
          is_active ? 1 : 0,
          is_popup ? 1 : 0,
          cleanPriority,
          user.login_claro || user.nome_completo || 'ADMIN'
        ).run();

        return json({
          success: true,
          message: 'Notificação corporativa criada com sucesso.',
          id: notifId
        }, 201);
      } catch (err) {
        console.error('Erro ao criar notificação:', err);
        return json({ error: 'Falha interna ao criar notificação.' }, 500);
      }
    }

    // POST /api/admin/notifications/:id/toggle — Alterna status ativo/inativo
    const toggleMatch = pathname.match(/^\/api\/admin\/notifications\/([^\/]+)\/toggle$/);
    if (toggleMatch && method === 'POST') {
      const notifId = toggleMatch[1];
      try {
        const row = await env.DB.prepare('SELECT is_active FROM notifications WHERE id = ?').bind(notifId).first();
        if (!row) {
          return json({ error: 'Notificação não localizada.' }, 404);
        }
        const nextStatus = row.is_active ? 0 : 1;
        await env.DB.prepare('UPDATE notifications SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
          .bind(nextStatus, notifId).run();

        return json({
          success: true,
          is_active: nextStatus,
          message: nextStatus ? 'Notificação ativada.' : 'Notificação pausada.'
        });
      } catch (err) {
        console.error('Erro ao alternar status da notificação:', err);
        return json({ error: 'Falha ao alterar status da notificação.' }, 500);
      }
    }

    // PUT /api/admin/notifications/:id — Atualiza notificação existente
    const updateMatch = pathname.match(/^\/api\/admin\/notifications\/([^\/]+)$/);
    if (updateMatch && method === 'PUT') {
      const notifId = updateMatch[1];
      try {
        const body = await request.json().catch(() => ({}));
        const {
          title,
          message,
          type = 'info',
          preset = 'custom',
          target_audience = 'ALL',
          audience,
          target_type = 'all',
          target_users = null,
          target_roles = null,
          target_areas = null,
          action_url = '',
          action_label = '',
          starts_at = null,
          expires_at = null,
          is_active = 1,
          is_popup = 0,
          priority = 'normal'
        } = body;

        if (!title || !title.trim() || !message || !message.trim()) {
          return json({ error: 'Título e mensagem são campos obrigatórios.' }, 400);
        }

        const validTypes = ['info', 'warning', 'success', 'update', 'security'];
        const cleanType = validTypes.includes(type) ? type : 'info';
        const validPriorities = ['normal', 'alta', 'urgente'];
        const cleanPriority = validPriorities.includes(priority) ? priority : 'normal';

        let cleanTargetType = String(target_type || '').toLowerCase();
        if (!cleanTargetType || cleanTargetType === 'undefined') {
          const rawAud = String(target_audience || audience || 'ALL').toUpperCase();
          if (rawAud === 'ADMIN') cleanTargetType = 'admin';
          else if (rawAud === 'REGULAR') cleanTargetType = 'regular';
          else if (rawAud.startsWith('USERS:')) cleanTargetType = 'users';
          else if (rawAud.startsWith('ROLES:')) cleanTargetType = 'roles';
          else if (rawAud.startsWith('AREAS:')) cleanTargetType = 'areas';
          else cleanTargetType = 'all';
        }

        const cleanTargetUsers = target_users ? (typeof target_users === 'string' ? target_users : JSON.stringify(target_users)) : null;
        const cleanTargetRoles = target_roles ? (typeof target_roles === 'string' ? target_roles : JSON.stringify(target_roles)) : null;
        const cleanTargetAreas = target_areas ? (typeof target_areas === 'string' ? target_areas : JSON.stringify(target_areas)) : null;

        let cleanAudience = target_audience || audience || 'ALL';
        if (cleanTargetType === 'users' && cleanTargetUsers) {
          cleanAudience = `USERS:${cleanTargetUsers}`;
        } else if (cleanTargetType === 'roles' && cleanTargetRoles) {
          cleanAudience = `ROLES:${cleanTargetRoles}`;
        } else if (cleanTargetType === 'areas' && cleanTargetAreas) {
          cleanAudience = `AREAS:${cleanTargetAreas}`;
        } else if (cleanTargetType === 'admin') {
          cleanAudience = 'admin';
        } else if (cleanTargetType === 'regular') {
          cleanAudience = 'regular';
        } else if (cleanTargetType === 'all') {
          cleanAudience = 'ALL';
        }

        await env.DB.prepare(`
          UPDATE notifications SET
            title = ?,
            message = ?,
            type = ?,
            preset = ?,
            target_audience = ?,
            target_type = ?,
            target_users = ?,
            target_roles = ?,
            target_areas = ?,
            action_url = ?,
            action_label = ?,
            starts_at = ?,
            expires_at = ?,
            is_active = ?,
            is_popup = ?,
            priority = ?,
            updated_at = CURRENT_TIMESTAMP
          WHERE id = ?
        `).bind(
          title.trim(),
          message.trim(),
          cleanType,
          preset || 'custom',
          cleanAudience,
          cleanTargetType,
          cleanTargetUsers,
          cleanTargetRoles,
          cleanTargetAreas,
          action_url ? action_url.trim() : null,
          action_label ? action_label.trim() : null,
          starts_at || null,
          expires_at || null,
          is_active ? 1 : 0,
          is_popup ? 1 : 0,
          cleanPriority,
          notifId
        ).run();

        return json({ success: true, message: 'Notificação atualizada com sucesso.' });
      } catch (err) {
        console.error('Erro ao atualizar notificação:', err);
        return json({ error: 'Falha ao atualizar notificação.' }, 500);
      }
    }

    // DELETE /api/admin/notifications/:id — Remove notificação
    const deleteMatch = pathname.match(/^\/api\/admin\/notifications\/([^\/]+)$/);
    if (deleteMatch && method === 'DELETE') {
      const notifId = deleteMatch[1];
      try {
        await env.DB.prepare('DELETE FROM notifications WHERE id = ?').bind(notifId).run();
        await env.DB.prepare('DELETE FROM user_notifications_read WHERE notification_id = ?').bind(notifId).run();
        return json({ success: true, message: 'Notificação excluída com sucesso.' });
      } catch (err) {
        console.error('Erro ao excluir notificação:', err);
        return json({ error: 'Falha ao excluir notificação.' }, 500);
      }
    }
  }

  // =========================================================================
  // ROTAS DO USUÁRIO GERAL (/api/notifications/*)
  // =========================================================================
  await ensureNotificationsTables(env);

  // GET /api/notifications — Retorna notificações ativas e elegíveis para o usuário
  if (pathname === '/api/notifications' && method === 'GET') {
    try {
      const nowIso = new Date().toISOString();

      // Consulta todas as ativas que se enquadram na vigência
      const query = `
        SELECT 
          n.id,
          n.title,
          n.message,
          n.type,
          n.preset,
          n.target_audience,
          n.target_type,
          n.target_users,
          n.target_roles,
          n.target_areas,
          n.action_url,
          n.action_label,
          n.created_at,
          r.read_at,
          r.dismissed
        FROM notifications n
        LEFT JOIN user_notifications_read r 
          ON r.notification_id = n.id AND r.user_id = ?
        WHERE n.is_active = 1
          AND (n.starts_at IS NULL OR n.starts_at <= ?)
          AND (n.expires_at IS NULL OR n.expires_at >= ?)
        ORDER BY n.created_at DESC
        LIMIT 50
      `;

      const { results } = await env.DB.prepare(query).bind(user.id, nowIso, nowIso).all();
      const items = (results || []).filter(item => {
        // Filtra por público-alvo (pessoa, cargo, setor, admin, etc.)
        if (!isNotificationEligible(item, user)) return false;

        // Filtra dispensadas pelo usuário
        if (Boolean(item.dismissed)) return false;

        return true;
      });

      const formatted = items.map(it => ({
        id: it.id,
        title: it.title,
        message: it.message,
        type: it.type || 'info',
        preset: it.preset || 'custom',
        action_url: it.action_url || null,
        action_label: it.action_label || null,
        created_at: it.created_at,
        is_read: Boolean(it.read_at)
      }));

      const unreadCount = formatted.filter(f => !f.is_read).length;

      // 2. Detecção de Popup Prioritário no 1º logon do dia
      let dailyPopup = null;
      const todayDate = new Date().toISOString().slice(0, 10);

      try {
        const popupQuery = `
          SELECT 
            n.id, n.title, n.message, n.type, n.preset, n.priority,
            n.action_url, n.action_label, n.created_at,
            n.target_audience, n.target_type, n.target_users, n.target_roles, n.target_areas
          FROM notifications n
          LEFT JOIN user_daily_popups_seen p 
            ON p.notification_id = n.id AND p.user_id = ? AND p.seen_date = ?
          LEFT JOIN user_notifications_read r 
            ON r.notification_id = n.id AND r.user_id = ?
          WHERE n.is_active = 1
            AND n.is_popup = 1
            AND (n.starts_at IS NULL OR n.starts_at <= ?)
            AND (n.expires_at IS NULL OR n.expires_at >= ?)
            AND p.seen_date IS NULL
            AND (r.dismissed IS NULL OR r.dismissed = 0)
          ORDER BY CASE WHEN n.priority = 'urgente' THEN 1 WHEN n.priority = 'alta' THEN 2 ELSE 3 END, n.created_at DESC
        `;

        const { results: popupResults } = await env.DB.prepare(popupQuery).bind(user.id, todayDate, user.id, nowIso, nowIso).all();
        for (const cand of (popupResults || [])) {
          if (!isNotificationEligible(cand, user)) continue;

          dailyPopup = {
            id: cand.id,
            title: cand.title,
            message: cand.message,
            type: cand.type || 'info',
            preset: cand.preset || 'custom',
            priority: cand.priority || 'alta',
            action_url: cand.action_url || null,
            action_label: cand.action_label || null,
            created_at: cand.created_at
          };
          break; // Retorna o popup de maior prioridade elegível para o usuário
        }
      } catch (pErr) {
        console.error('Erro ao verificar daily_popup:', pErr);
      }

      return json({
        success: true,
        notifications: formatted,
        unread_count: unreadCount,
        daily_popup: dailyPopup,
        server_time: nowIso
      });
    } catch (err) {
      console.error('Erro ao consultar notificações do usuário:', err);
      return json({ error: 'Falha ao buscar notificações.' }, 500);
    }
  }

  // POST /api/notifications/:id/popup-seen — Registra visualização de popup diário
  const popupSeenMatch = pathname.match(/^\/api\/notifications\/([^\/]+)\/popup-seen$/);
  if (popupSeenMatch && method === 'POST') {
    const notifId = popupSeenMatch[1];
    const todayDate = new Date().toISOString().slice(0, 10);
    try {
      await env.DB.prepare(`
        INSERT INTO user_daily_popups_seen (user_id, notification_id, seen_date)
        VALUES (?, ?, ?)
      `).bind(user.id, notifId, todayDate).run().catch(() => {});

      return json({ success: true, message: 'Popup diário visualizado.' });
    } catch (err) {
      console.error('Erro ao marcar popup como visto:', err);
      return json({ error: 'Falha ao registrar visualização.' }, 500);
    }
  }

  // POST /api/notifications/:id/read — Marca notificação como lida
  const readMatch = pathname.match(/^\/api\/notifications\/([^\/]+)\/read$/);
  if (readMatch && method === 'POST') {
    const notifId = readMatch[1];
    try {
      await env.DB.prepare(`
        INSERT INTO user_notifications_read (user_id, notification_id, read_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, notification_id) DO UPDATE SET read_at = CURRENT_TIMESTAMP
      `).bind(user.id, notifId).run();

      return json({ success: true, message: 'Notificação marcada como lida.' });
    } catch (err) {
      console.error('Erro ao marcar notificação como lida:', err);
      return json({ error: 'Falha ao atualizar leitura.' }, 500);
    }
  }

  // POST /api/notifications/:id/dismiss — Dispensa notificação
  const dismissMatch = pathname.match(/^\/api\/notifications\/([^\/]+)\/dismiss$/);
  if (dismissMatch && method === 'POST') {
    const notifId = dismissMatch[1];
    try {
      await env.DB.prepare(`
        INSERT INTO user_notifications_read (user_id, notification_id, read_at, dismissed)
        VALUES (?, ?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(user_id, notification_id) DO UPDATE SET dismissed = 1, read_at = CURRENT_TIMESTAMP
      `).bind(user.id, notifId).run();

      return json({ success: true, message: 'Notificação dispensada.' });
    } catch (err) {
      console.error('Erro ao dispensar notificação:', err);
      return json({ error: 'Falha ao dispensar notificação.' }, 500);
    }
  }

  // POST /api/notifications/read-all — Marca todas como lidas para o usuário
  if (pathname === '/api/notifications/read-all' && method === 'POST') {
    try {
      const nowIso = new Date().toISOString();
      const activeNotifs = await env.DB.prepare(`
        SELECT id FROM notifications 
        WHERE is_active = 1 
          AND (starts_at IS NULL OR starts_at <= ?)
          AND (expires_at IS NULL OR expires_at >= ?)
      `).bind(nowIso, nowIso).all();

      const notifIds = (activeNotifs.results || []).map(n => n.id);
      for (const nid of notifIds) {
        await env.DB.prepare(`
          INSERT INTO user_notifications_read (user_id, notification_id, read_at)
          VALUES (?, ?, CURRENT_TIMESTAMP)
          ON CONFLICT(user_id, notification_id) DO UPDATE SET read_at = CURRENT_TIMESTAMP
        `).bind(user.id, nid).run().catch(() => {});
      }

      return json({ success: true, message: 'Todas as notificações foram marcadas como lidas.' });
    } catch (err) {
      console.error('Erro ao marcar todas notificações como lidas:', err);
      return json({ error: 'Falha ao processar solicitação.' }, 500);
    }
  }

  return null;
}
