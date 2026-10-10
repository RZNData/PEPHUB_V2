/**
 * Sub-roteador Administrativo Corporativo
 * Rotas: /api/admin/*
 */

import {
  SECURITY_HEADERS,
  json,
  getSessionUser,
  logAccess,
  hashPassword,
  sendEmail,
  ALL_SYSTEM_MODULES,
  ALL_DEFAULT_MODULES_STR,
  normalizeModuleId,
  invalidateSystemControlsCache,
  invalidateModuleSuspensionCache,
  invalidateSessionUserCache,
  ensureSystemModulesSeeded,
  generateTempPassword,
  ensureSessionPresenceColumns,
  ONLINE_WINDOW_SECONDS,
} from '../utils/security.js';

export async function handleAdminRoutes(request, env, url, pathname) {
  // GET /api/portal/modules (Lista de módulos e status para o portal público/autenticado)
    if (pathname === '/api/portal/modules' && request.method === 'GET') {
      const user = await getSessionUser(request, env);
      const isAdmin = Boolean(user && user.is_admin);

      let query = "SELECT id, name, short_name, section, description, route, status, sort_order FROM system_modules ";
      if (!isAdmin) {
        query += "WHERE status != 'oculto' ";
      }
      query += "ORDER BY section ASC, sort_order ASC";

      const rows = await env.DB.prepare(query).all();
      let userModsStr = 'none';
      if (user && user.status === 'aprovado') {
        if (Boolean(user.is_admin) || user.modules_allowed === 'all') {
          userModsStr = 'all';
        } else if (user.modules_allowed === 'none' || user.modules_allowed === '') {
          userModsStr = 'none';
        } else if (user.modules_allowed) {
          userModsStr = user.modules_allowed.split(',').map(normalizeModuleId).filter(Boolean).join(',');
        } else {
          userModsStr = ALL_DEFAULT_MODULES_STR;
        }
      }

      const normalizedModules = (rows.results || []).map(r => ({
        ...r,
        id: normalizeModuleId(r.id)
      }));

      return json({
        modules: normalizedModules,
        user_modules: userModsStr,
        is_admin: isAdmin
      });
    }


  if (!pathname.startsWith('/api/admin/')) {
    return null;
  }

  const currentUser = await getSessionUser(request, env);
  if (!currentUser || !currentUser.is_admin) {
    return json({ error: 'Acesso restrito ao responsável pela ferramenta.' }, 403);
  }

  const baseUrl = env.PUBLIC_BASE_URL || `${url.protocol}//${url.host}`;
  await ensureSessionPresenceColumns(env);

  // Critério único de "online": sessão válida COM heartbeat recebido nos últimos 180s (3 min)
  // Escrito em SQL literal estrito para evitar apontamentos de CWE-89 no auditor AppSec

      // GET /api/admin/active-users (Contagem e lista de usuários online em tempo real para administradores)
      if (pathname === '/api/admin/active-users' && request.method === 'GET') {
        const activeList = await env.DB.prepare(`
          SELECT 
            u.id, 
            u.nome_completo, 
            u.login_claro, 
            u.email_claro, 
            u.area, 
            u.funcao, 
            u.is_admin,
            MAX(s.last_seen) as last_activity,
            MIN(s.online_since) as online_since,
            CAST((julianday('now') - julianday(MIN(s.online_since))) * 86400 AS INTEGER) as online_seconds,
            CAST((julianday('now') - julianday(MAX(s.last_seen))) * 86400 AS INTEGER) as idle_seconds,
            (SELECT a2.recurso FROM access_logs a2 WHERE a2.user_id = u.id AND a2.recurso NOT LIKE 'ADMIN_%' ORDER BY a2.created_at DESC LIMIT 1) as last_resource,
            COUNT(s.id) as session_count
          FROM sessions s
          JOIN users u ON s.user_id = u.id
          WHERE datetime(s.expires_at) > datetime('now')
            AND s.last_seen IS NOT NULL
            AND (julianday('now') - julianday(s.last_seen)) * 86400 <= ?
            AND u.status = 'aprovado'
          GROUP BY u.id
          ORDER BY online_seconds DESC
        `).bind(ONLINE_WINDOW_SECONDS).all();

        return json({
          total: activeList.results ? activeList.results.length : 0,
          window_seconds: ONLINE_WINDOW_SECONDS,
          users: activeList.results || []
        });
      }

      // GET /api/admin/users (Panorama detalhado de cada usuário com telemetria otimizada)
      if (pathname === '/api/admin/users' && request.method === 'GET') {
        const users = await env.DB.prepare(`
          SELECT 
            u.id, u.nome_completo, u.login_claro, u.email_claro, u.telefone, u.area, u.funcao, 
            u.status, u.is_admin, u.notify_updates, u.modules_allowed, u.must_change_password, 
            u.profile_metadata,
            u.created_at, u.approved_at,
            CASE WHEN EXISTS (
              SELECT 1 FROM sessions s 
              WHERE s.user_id = u.id 
                AND datetime(s.expires_at) > datetime('now')
                AND s.last_seen IS NOT NULL
                AND (julianday('now') - julianday(s.last_seen)) * 86400 <= ?
            ) THEN 1 ELSE 0 END as is_online,
            COUNT(CASE WHEN a.recurso NOT LIKE 'ADMIN_%' THEN a.id END) as total_accesses,
            MAX(CASE WHEN a.recurso NOT LIKE 'ADMIN_%' THEN a.created_at END) as last_access,
            COUNT(CASE WHEN a.recurso LIKE '%DOWNLOAD%' OR a.recurso LIKE '%EXPORT%' THEN 1 END) as total_exports,
            MAX(CASE WHEN a.recurso LIKE '%DOWNLOAD%' OR a.recurso LIKE '%EXPORT%' THEN a.created_at END) as last_export
          FROM users u
          LEFT JOIN access_logs a ON a.user_id = u.id
          GROUP BY u.id
          ORDER BY u.created_at DESC
        `).bind(ONLINE_WINDOW_SECONDS).all();

        return json(users.results || []);
      }

      // POST /api/admin/users/:id/profile (Admin edita dados cadastrais de um usuário)
      if (pathname.match(/^\/api\/admin\/users\/[^/]+\/profile$/) && request.method === 'POST') {
        const targetUserId = pathname.split('/')[4];
        const body = await request.json();
        const { nome_completo, email_claro, login_claro, telefone, area, funcao, profile_metadata } = body;

        const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(targetUserId).first();
        if (!user) return json({ error: 'Usuário não localizado.' }, 404);

        let finalMeta = user.profile_metadata;
        if (profile_metadata !== undefined) {
          finalMeta = typeof profile_metadata === 'object' && profile_metadata !== null
            ? JSON.stringify(profile_metadata)
            : String(profile_metadata);
        }

        const cleanPhone = telefone !== undefined ? String(telefone).replace(/\D/g, '') : user.telefone;
        const cleanLogin = login_claro ? String(login_claro).trim().toUpperCase() : user.login_claro;
        const cleanEmail = email_claro ? String(email_claro).trim().toLowerCase() : user.email_claro;
        const cleanNome = nome_completo ? String(nome_completo).trim() : user.nome_completo;
        const cleanArea = area ? String(area).trim() : user.area;
        const cleanFuncao = funcao ? String(funcao).trim() : user.funcao;

        // Se alterou login ou email, verifica se já não existe em outro usuário
        if (cleanLogin !== user.login_claro) {
          const exists = await env.DB.prepare('SELECT id FROM users WHERE login_claro = ? AND id != ?').bind(cleanLogin, targetUserId).first();
          if (exists) return json({ error: 'Este login Claro já está em uso por outro colaborador.' }, 400);
        }
        if (cleanEmail !== user.email_claro) {
          const exists = await env.DB.prepare('SELECT id FROM users WHERE email_claro = ? AND id != ?').bind(cleanEmail, targetUserId).first();
          if (exists) return json({ error: 'Este e-mail já está em uso por outro colaborador.' }, 400);
        }

        await env.DB.prepare(`
          UPDATE users SET
            nome_completo = ?,
            email_claro = ?,
            login_claro = ?,
            telefone = ?,
            area = ?,
            funcao = ?,
            profile_metadata = ?
          WHERE id = ?
        `).bind(cleanNome, cleanEmail, cleanLogin, cleanPhone, cleanArea, cleanFuncao, finalMeta, targetUserId).run();

        await logAccess(env, request, currentUser, `ADMIN_UPDATE_USER_PROFILE:${cleanLogin}`);
        return json({
          success: true,
          user_id: targetUserId,
          message: 'Dados cadastrais atualizados com sucesso.'
        });
      }

      // POST /api/admin/users/:id/privileges (Atualiza perfil, status, módulos via toggle e notificações)
      if (pathname.match(/^\/api\/admin\/users\/[^/]+\/privileges$/) && request.method === 'POST') {
        const targetUserId = pathname.split('/')[4];
        const body = await request.json();
        const { is_admin, status: newStatus, modules_allowed, notify_updates } = body;

        const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(targetUserId).first();
        if (!user) return json({ error: 'Usuário não localizado.' }, 404);

        const statusToSet = newStatus !== undefined ? newStatus : user.status;
        if (!['aprovado', 'rejeitado', 'pendente', 'bloqueado'].includes(statusToSet)) {
          return json({ error: 'Status informado é inválido.' }, 400);
        }

        const adminToSet = is_admin !== undefined ? (is_admin ? 1 : 0) : user.is_admin;
        let modulesToSet;
        if (modules_allowed !== undefined) {
          if (Array.isArray(modules_allowed)) {
            modulesToSet = modules_allowed.map(normalizeModuleId).filter(Boolean).join(',');
          } else {
            const rawStr = String(modules_allowed).trim();
            if (rawStr === 'none' || rawStr === '') {
              modulesToSet = 'none';
            } else if (rawStr === 'all') {
              modulesToSet = 'all';
            } else {
              modulesToSet = rawStr.split(',').map(normalizeModuleId).filter(Boolean).join(',');
            }
          }
          if (!modulesToSet) modulesToSet = 'none';
        } else {
          modulesToSet = user.modules_allowed !== null && user.modules_allowed !== undefined ? user.modules_allowed : ALL_DEFAULT_MODULES_STR;
        }
        const notifyToSet = notify_updates !== undefined ? (notify_updates ? 1 : 0) : user.notify_updates;

        await env.DB.prepare(`
          UPDATE users SET 
            is_admin = ?,
            status = ?,
            modules_allowed = ?,
            notify_updates = ?,
            approved_at = CASE WHEN ? = 'aprovado' THEN COALESCE(approved_at, datetime('now')) ELSE NULL END
          WHERE id = ?
        `).bind(adminToSet, statusToSet, modulesToSet, notifyToSet, statusToSet, targetUserId).run();

        // Se o usuário foi bloqueado ou rejeitado, invalida imediatamente todas as sessões ativas dele no D1
        if (statusToSet !== 'aprovado') {
          await env.DB.prepare('DELETE FROM sessions WHERE user_id = ?').bind(targetUserId).run().catch(() => {});
        }
        invalidateSessionUserCache();

        await logAccess(env, request, currentUser, `ADMIN_UPDATE_PRIVILEGES:${user.login_claro}:${modulesToSet}`);
        return json({
          success: true,
          user_id: targetUserId,
          modules_allowed: modulesToSet,
          status: statusToSet,
          is_admin: adminToSet
        });
      }

      // DELETE /api/admin/users/:id (Exclui permanentemente o usuário)
      if ((pathname.match(/^\/api\/admin\/users\/[^/]+$/) && request.method === 'DELETE') ||
          (pathname.match(/^\/api\/admin\/users\/[^/]+\/delete$/) && request.method === 'POST')) {
        const targetUserId = pathname.split('/')[4];
        const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(targetUserId).first();
        if (!user) return json({ error: 'Usuário não localizado.' }, 404);

        if (user.id === currentUser.id || user.login_claro === 'admin' || user.email_claro === 'admin@pephub.cloud') {
          return json({ error: 'Operação não permitida: não é possível excluir o próprio usuário administrador principal.' }, 403);
        }

        await env.DB.prepare('DELETE FROM users WHERE id = ?').bind(targetUserId).run();
        await logAccess(env, request, currentUser, `ADMIN_DELETE_USER:${user.login_claro}`);

        return json({ success: true, message: `Usuário ${user.nome_completo} excluído com sucesso.` });
      }

      // POST /api/admin/users/:id/reset-password (Gera senha provisória de uso único)
      if (pathname.match(/^\/api\/admin\/users\/[^/]+\/reset-password$/) && request.method === 'POST') {
        const targetUserId = pathname.split('/')[4];
        const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(targetUserId).first();
        if (!user) return json({ error: 'Usuário não localizado.' }, 404);

        const tempPassword = generateTempPassword();
        const { salt, hash } = await hashPassword(tempPassword);

        await env.DB.prepare(`
          UPDATE users 
          SET password_hash = ?, salt = ?, must_change_password = 1 
          WHERE id = ?
        `).bind(hash, salt, targetUserId).run();

        const emailHtml = `
          <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
            <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
              <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Senha Provisória de Uso Único</h2>
            </div>
            <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
              <p style="margin-top:0">Prezado(a) <strong>${user.nome_completo}</strong>,</p>
              <p>Uma senha provisória de uso único foi configurada para o seu usuário corporativo pelo responsável pela ferramenta.</p>
              
              <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:14px;margin:16px 0;font-size:13px;text-align:center">
                <span style="color:#5b6675;font-size:11.5px;display:block;text-transform:uppercase;letter-spacing:.5px">Sua Senha Provisória:</span>
                <strong style="font-size:18px;letter-spacing:1px;color:#1c2430;font-family:Consolas,monospace">${tempPassword}</strong>
              </div>

              <p style="font-size:12px;color:#5b6675">
                Por diretriz de segurança, ao realizar este acesso, o sistema exigirá que você defina obrigatoriamente a sua nova senha pessoal definitiva.
              </p>

              <div style="margin:24px 0;text-align:center">
                <a href="${baseUrl}/login/" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                  Entrar e Definir Nova Senha
                </a>
              </div>
            </div>
          </div>
        `;

        await sendEmail(env, {
          to: user.email_claro,
          subject: '[Pephub Regional] Senha Provisória de Acesso',
          html: emailHtml,
          text: `Sua senha temporária de uso único é: ${tempPassword}. Entre em ${baseUrl}/login/ para definir sua senha permanente.`,
        });

        await logAccess(env, request, currentUser, `ADMIN_RESET_PASSWORD:${user.login_claro}`);

        return json({
          success: true,
          temp_password: tempPassword,
          email: user.email_claro,
          nome: user.nome_completo
        });
      }

      // GET /api/admin/access-stats (Estatísticas e Inteligência do Dashboard de Acessos com Filtro de Data)
      if (pathname === '/api/admin/access-stats' && request.method === 'GET') {
        const startDate = url.searchParams.get('start_date');
        const endDate = url.searchParams.get('end_date');

        let whereClause = '';
        let whereParams = [];
        let prevWhereClause = '';
        let prevWhereParams = [];
        let periodLabel = 'Últimos 30 dias';

        if (startDate && endDate) {
          whereClause = "WHERE datetime(created_at) >= datetime(? || ' 00:00:00') AND datetime(created_at) <= datetime(? || ' 23:59:59')";
          whereParams = [startDate, endDate];
          periodLabel = `${startDate} a ${endDate}`;

          const s = new Date(startDate);
          const e = new Date(endDate);
          const diffMs = Math.max(86400000, e.getTime() - s.getTime() + 86400000);
          const prevE = new Date(s.getTime() - 86400000);
          const prevS = new Date(prevE.getTime() - diffMs + 86400000);
          const prevStartStr = prevS.toISOString().split('T')[0];
          const prevEndStr = prevE.toISOString().split('T')[0];
          prevWhereClause = "WHERE datetime(created_at) >= datetime(? || ' 00:00:00') AND datetime(created_at) <= datetime(? || ' 23:59:59')";
          prevWhereParams = [prevStartStr, prevEndStr];
        } else if (startDate) {
          whereClause = "WHERE datetime(created_at) >= datetime(? || ' 00:00:00')";
          whereParams = [startDate];
          periodLabel = `Desde ${startDate}`;
        } else {
          whereClause = "WHERE datetime(created_at) >= datetime('now', '-30 days')";
          whereParams = [];
          prevWhereClause = "WHERE datetime(created_at) >= datetime('now', '-60 days') AND datetime(created_at) < datetime('now', '-30 days')";
          prevWhereParams = [];
        }

        const totalAll = await env.DB.prepare("SELECT count(*) as c FROM access_logs WHERE recurso NOT LIKE 'ADMIN_%'").first();
        const baseWhere = whereClause ? `${whereClause} AND recurso NOT LIKE 'ADMIN_%'` : "WHERE recurso NOT LIKE 'ADMIN_%'";
        const prevBaseWhere = prevWhereClause ? `${prevWhereClause} AND recurso NOT LIKE 'ADMIN_%'` : "WHERE recurso NOT LIKE 'ADMIN_%'";

        const countQuery = `SELECT count(*) as c FROM access_logs ${baseWhere}`;
        const currentPeriodCount = await env.DB.prepare(countQuery).bind(...whereParams).first();
        const prevCountQuery = prevWhereClause ? `SELECT count(*) as c FROM access_logs ${prevBaseWhere}` : null;
        const prevPeriodCount = prevCountQuery
          ? await env.DB.prepare(prevCountQuery).bind(...prevWhereParams).first()
          : null;

        const countCurrent = currentPeriodCount?.c || 0;
        const countPrev = prevPeriodCount?.c || 0;
        const growth = countPrev > 0 ? Math.round(((countCurrent - countPrev) / countPrev) * 100) : 0;

        const uniqueQuery = `SELECT count(DISTINCT email_claro) as c FROM access_logs ${baseWhere}`;
        const uniqueUsers = await env.DB.prepare(uniqueQuery).bind(...whereParams).first();

        const exportQuery = `SELECT count(*) as c FROM access_logs ${baseWhere} AND (recurso LIKE '%DOWNLOAD%' OR recurso LIKE '%EXPORT%')`;
        const exportLogs = await env.DB.prepare(exportQuery).bind(...whereParams).first();

        // Recursos / Visões Mais Utilizadas no Período
        const resourcesQuery = `
          SELECT recurso, count(*) as count 
          FROM access_logs 
          ${baseWhere}
          GROUP BY recurso 
          ORDER BY count DESC
        `;
        const resourcesRaw = await env.DB.prepare(resourcesQuery).bind(...whereParams).all();

        // Canais / Áreas Mais Engajadas no Período
        const channelsQuery = `
          SELECT area, count(*) as count 
          FROM access_logs 
          ${baseWhere} AND area IS NOT NULL AND area != '' 
          GROUP BY area 
          ORDER BY count DESC
        `;
        const channelsRaw = await env.DB.prepare(channelsQuery).bind(...whereParams).all();

        // Polos Regionais / Cidades no Período
        const locationsQuery = `
          SELECT cidade, estado, localizacao, count(*) as count 
          FROM access_logs 
          ${baseWhere} AND cidade IS NOT NULL AND cidade != ''
          GROUP BY cidade, estado 
          ORDER BY count DESC 
          LIMIT 8
        `;
        const locationsRaw = await env.DB.prepare(locationsQuery).bind(...whereParams).all();

        // Ranking de Usuários e Visões por Usuário no Período
        const topUsersQuery = `
          SELECT 
            nome_completo, 
            login_claro, 
            email_claro, 
            area, 
            funcao, 
            count(*) as total_views, 
            sum(CASE WHEN recurso LIKE '%DOWNLOAD%' OR recurso LIKE '%EXPORT%' THEN 1 ELSE 0 END) as total_exports,
            max(created_at) as last_access,
            CASE WHEN EXISTS (
              SELECT 1 FROM sessions s 
              JOIN users u_s ON s.user_id = u_s.id 
              WHERE lower(u_s.email_claro) = lower(a1.email_claro) 
                AND datetime(s.expires_at) > datetime('now')
                AND s.last_seen IS NOT NULL
                AND (julianday('now') - julianday(s.last_seen)) * 86400 <= ?
            ) THEN 1 ELSE 0 END as is_online,
            (SELECT recurso FROM access_logs a2 WHERE a2.email_claro = a1.email_claro AND a2.recurso NOT LIKE 'ADMIN_%' ORDER BY created_at DESC LIMIT 1) as last_resource,
            (SELECT localizacao FROM access_logs a3 WHERE a3.email_claro = a1.email_claro ORDER BY created_at DESC LIMIT 1) as last_location
          FROM access_logs a1 
          ${baseWhere} AND email_claro IS NOT NULL AND email_claro != ''
          GROUP BY email_claro 
          ORDER BY total_views DESC 
          LIMIT 15
        `;
        const topUsersRaw = await env.DB.prepare(topUsersQuery).bind(ONLINE_WINDOW_SECONDS, ...whereParams).all();

        // Curva Horária de Pico (Fuso Oficial de Brasília: UTC-3)
        const hourlyQuery = `
          SELECT strftime('%H', created_at, '-3 hours') as hour, count(*) as count
          FROM access_logs
          ${baseWhere}
          GROUP BY hour
          ORDER BY hour ASC
        `;
        const hourlyRaw = await env.DB.prepare(hourlyQuery).bind(...whereParams).all();

        // Série Diária do Período (Fuso Oficial de Brasília: UTC-3)
        const dailyQuery = `
          SELECT strftime('%Y-%m-%d', created_at, '-3 hours') as day, count(*) as count,
                 sum(CASE WHEN recurso LIKE '%DOWNLOAD%' OR recurso LIKE '%EXPORT%' THEN 1 ELSE 0 END) as exports
          FROM access_logs
          ${baseWhere}
          GROUP BY day
          ORDER BY day ASC
        `;
        const dailyRaw = await env.DB.prepare(dailyQuery).bind(...whereParams).all();

        return json({
          summary: {
            total_accesses_all: totalAll?.c || 0,
            period_accesses: countCurrent,
            prev_period_accesses: countPrev,
            growth_pct: growth,
            unique_users: uniqueUsers?.c || 0,
            total_exports: exportLogs?.c || 0,
            period_label: periodLabel,
            top_resource: resourcesRaw.results?.[0]?.recurso || 'CHURN_SAFRA',
            top_channel: channelsRaw.results?.[0]?.area || 'LOJAS PRÓPRIAS',
            top_location: locationsRaw.results?.[0]?.cidade || 'Manaus'
          },
          resources: resourcesRaw.results || [],
          channels: channelsRaw.results || [],
          locations: locationsRaw.results || [],
          top_users: topUsersRaw.results || [],
          hourly: hourlyRaw.results || [],
          daily: dailyRaw.results || []
        });
      }

      // GET /api/admin/access-logs (Auditoria Detalhada de Acessos com Busca e Filtros)
      if (pathname === '/api/admin/access-logs' && request.method === 'GET') {
        const query = url.searchParams.get('q') || '';
        const actionFilter = url.searchParams.get('action') || 'all'; // all, export, view, login, admin
        const startDate = url.searchParams.get('start_date');
        const endDate = url.searchParams.get('end_date');

        let conditions = [];
        let params = [];

        if (query.trim()) {
          const term = `%${query.trim()}%`;
          conditions.push(`(nome_completo LIKE ? OR login_claro LIKE ? OR email_claro LIKE ? OR ip LIKE ? OR localizacao LIKE ? OR recurso LIKE ? OR area LIKE ? OR funcao LIKE ?)`);
          params.push(term, term, term, term, term, term, term, term);
        }

        if (actionFilter === 'export') {
          conditions.push(`(recurso LIKE '%DOWNLOAD%' OR recurso LIKE '%EXPORT%')`);
        } else if (actionFilter === 'view') {
          conditions.push(`(recurso IN ('CHURN_SAFRA', 'FPD_REGIONAL_NORTE', 'CHURN_BL_TOTAL', 'CHURN_BL_PME', 'PORTAL_HOME'))`);
        } else if (actionFilter === 'login') {
          conditions.push(`(recurso = 'LOGIN' OR recurso = 'PASSWORD_CHANGE')`);
        } else if (actionFilter === 'admin') {
          conditions.push(`(recurso LIKE 'ADMIN%')`);
        }

        if (startDate && endDate) {
          conditions.push(`datetime(created_at) >= datetime(? || ' 00:00:00') AND datetime(created_at) <= datetime(? || ' 23:59:59')`);
          params.push(startDate, endDate);
        } else if (startDate) {
          conditions.push(`datetime(created_at) >= datetime(? || ' 00:00:00')`);
          params.push(startDate);
        }

        const whereSql = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
        const logsQuery = `
          SELECT id, user_id, login_claro, email_claro, nome_completo, area, funcao, recurso, ip, cidade, estado, pais, localizacao, user_agent, created_at
          FROM access_logs
          ${whereSql}
          ORDER BY created_at DESC
          LIMIT 300
        `;
        const logs = await env.DB.prepare(logsQuery).bind(...params).all();

        return json(logs.results || []);
      }

      // POST /api/admin/broadcast (Notificação de Atualização de Relatório)
      if (pathname === '/api/admin/broadcast' && request.method === 'POST') {
        const { relatorio, assunto, mensagem } = await request.json();
        if (!relatorio || !assunto) {
          return json({ error: 'Relatório e Assunto são obrigatórios.' }, 400);
        }

        const approvedUsers = await env.DB.prepare(`
          SELECT email_claro, nome_completo FROM users
          WHERE status = 'aprovado' AND notify_updates = 1
        `).all();

        const recipients = approvedUsers.results || [];
        let sentCount = 0;

        for (const u of recipients) {
          const updateHtml = `
            <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
              <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
                <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Atualização de Base e Indicadores</h2>
              </div>
              <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
                <p style="margin-top:0">Prezado(a) <strong>${u.nome_completo}</strong>,</p>
                <p>Informamos que o módulo analítico <strong>${relatorio}</strong> foi consolidado e atualizado na plataforma regional.</p>
                
                ${mensagem ? `
                  <div style="background:#f7f8fa;border-left:3px solid #c0191f;padding:12px 14px;margin:16px 0;font-size:12.5px;color:#27323f">
                    ${mensagem.replace(/\n/g, '<br>')}
                  </div>
                ` : ''}

                <div style="margin:24px 0;text-align:center">
                  <a href="${baseUrl}/churn/" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                    Abrir Painel Atualizado
                  </a>
                </div>

                <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
                  Central de Inteligência Operacional Comercial — Regional Norte.
                </p>
              </div>
            </div>
          `;

          await sendEmail(env, {
            to: u.email_claro,
            subject: `[Pephub Regional] ${assunto}`,
            html: updateHtml,
            text: `O relatório ${relatorio} foi atualizado. Acesse: ${baseUrl}/churn/`,
          });
          sentCount++;
        }

        await logAccess(env, request, currentUser, `ADMIN_BROADCAST:${relatorio}`);
        return json({ success: true, sent: sentCount });
      }

      // GET /api/admin/system-controls (Listagem de travas e controles do sistema)
      if (pathname === '/api/admin/system-controls' && request.method === 'GET') {
        const rows = await env.DB.prepare('SELECT key, value, label, description, updated_at, updated_by FROM system_controls ORDER BY key ASC').all();
        return json(rows.results || []);
      }

      // POST /api/admin/system-controls (Atualiza trava ou controle global)
      if (pathname === '/api/admin/system-controls' && request.method === 'POST') {
        const body = await request.json();
        const { key, value } = body;
        if (!key || (value !== '0' && value !== '1' && value !== 0 && value !== 1)) {
          return json({ error: 'Parâmetros inválidos para alteração de trava de sistema.' }, 400);
        }
        const strVal = String(value);
        await env.DB.prepare(`
          UPDATE system_controls 
          SET value = ?, updated_at = datetime('now'), updated_by = ? 
          WHERE key = ?
        `).bind(strVal, currentUser.nome_completo || currentUser.email_claro, key).run();

        invalidateSystemControlsCache();
        await logAccess(env, request, currentUser, `ADMIN_SYSTEM_CONTROL:${key}:${strVal}`);
        return json({ success: true, key, value: strVal });
      }

      // GET /api/admin/modules (Listagem completa das ferramentas e status - Otimizado sem N+1)
      if (pathname === '/api/admin/modules' && request.method === 'GET') {
        await ensureSystemModulesSeeded(env);
        const modules = await env.DB.prepare(`
          SELECT id, name, short_name, section, description, route, status, sort_order, created_at, updated_at
          FROM system_modules
          ORDER BY section ASC, sort_order ASC
        `).all();

        const users = await env.DB.prepare(`
          SELECT modules_allowed FROM users WHERE is_admin = 0
        `).all();

        const userList = users.results || [];
        const totalRegularUsers = userList.length;

        const results = (modules.results || []).map(m => {
          const usersWithAccess = userList.filter(u => {
            const raw = u.modules_allowed || '';
            return raw === 'all' || (',' + raw + ',').includes(',' + m.id + ',');
          }).length;
          return {
            ...m,
            users_with_access: usersWithAccess,
            total_regular_users: totalRegularUsers,
          };
        });

        return json(results);
      }

      // POST /api/admin/modules (Cadastra ou atualiza ferramenta/relatório)
      if (pathname === '/api/admin/modules' && request.method === 'POST') {
        const body = await request.json();
        const { id, name, short_name, section, description, route, status, sort_order } = body;
        if (!id || !name || !section) {
          return json({ error: 'ID, Nome e Seção são obrigatórios.' }, 400);
        }
        const cleanId = String(id).trim().toLowerCase().replace(/[^a-z0-9_-]/g, '');

        await env.DB.prepare(`
          INSERT INTO system_modules (id, name, short_name, section, description, route, status, sort_order, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
          ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            short_name = excluded.short_name,
            section = excluded.section,
            description = excluded.description,
            route = excluded.route,
            status = excluded.status,
            sort_order = excluded.sort_order,
            updated_at = datetime('now')
        `).bind(
          cleanId,
          name.trim(),
          (short_name || name).trim(),
          section.trim(),
          description ? description.trim() : '',
          route ? route.trim() : `/${cleanId}/`,
          status || 'ativo',
          sort_order !== undefined ? Number(sort_order) : 0
        ).run();

        invalidateModuleSuspensionCache();
        await logAccess(env, request, currentUser, `ADMIN_UPSERT_MODULE:${cleanId}:${status || 'ativo'}`);
        return json({ success: true, id: cleanId });
      }

      // DELETE /api/admin/modules/:id (Exclui uma ferramenta do catálogo)
      if (pathname.match(/^\/api\/admin\/modules\/[^/]+$/) && request.method === 'DELETE') {
        const modId = pathname.split('/')[4];
        await env.DB.prepare('DELETE FROM system_modules WHERE id = ?').bind(modId).run();
        invalidateModuleSuspensionCache();
        await logAccess(env, request, currentUser, `ADMIN_DELETE_MODULE:${modId}`);
        return json({ success: true, id: modId });
      }

      // POST /api/admin/modules/:id/bulk-access (Concede ou revoga permissão de um relatório para TODOS os não-admins)
      if (pathname.match(/^\/api\/admin\/modules\/[^/]+\/bulk-access$/) && request.method === 'POST') {
        const rawModId = pathname.split('/')[4];
        const modId = normalizeModuleId(rawModId);
        const body = await request.json();
        const action = body.action; // 'grant_all' | 'revoke_all'
        if (action !== 'grant_all' && action !== 'revoke_all') {
          return json({ error: 'Ação inválida. Utilize grant_all ou revoke_all.' }, 400);
        }

        const regularUsers = await env.DB.prepare('SELECT id, modules_allowed FROM users WHERE is_admin = 0').all();
        const users = regularUsers.results || [];

        for (const u of users) {
          let mods;
          if (u.modules_allowed === 'all') {
            mods = [...ALL_SYSTEM_MODULES];
          } else if (u.modules_allowed === 'none' || !u.modules_allowed) {
            mods = [];
          } else {
            mods = u.modules_allowed.split(',').map(s => normalizeModuleId(s.trim())).filter(s => s && s !== 'none' && s !== 'all');
          }

          if (action === 'grant_all') {
            if (!mods.includes(modId)) mods.push(modId);
          } else {
            mods = mods.filter(m => m !== modId);
          }
          const finalModsStr = mods.length > 0 ? mods.join(',') : 'none';
          await env.DB.prepare('UPDATE users SET modules_allowed = ? WHERE id = ?')
            .bind(finalModsStr, u.id).run();
        }

        await logAccess(env, request, currentUser, `ADMIN_BULK_ACCESS_MODULE:${modId}:${action}`);
        return json({ success: true, action, module_id: modId, affected: users.length });
      }

      // POST /api/admin/modules/bulk-access-all (Concede ou revoga TODOS os relatórios para TODOS os não-admins)
      if (pathname === '/api/admin/modules/bulk-access-all' && request.method === 'POST') {
        const body = await request.json();
        const action = body.action; // 'grant_all' | 'revoke_all'
        if (action !== 'grant_all' && action !== 'revoke_all') {
          return json({ error: 'Ação inválida. Utilize grant_all ou revoke_all.' }, 400);
        }

        if (action === 'grant_all') {
          const allMods = await env.DB.prepare("SELECT id FROM system_modules WHERE status != 'suspenso'").all();
          const allIds = (allMods.results || []).length > 0
            ? (allMods.results || []).map(r => normalizeModuleId(r.id)).join(',')
            : ALL_SYSTEM_MODULES.join(',');
          await env.DB.prepare("UPDATE users SET modules_allowed = ? WHERE is_admin = 0").bind(allIds).run();
          await logAccess(env, request, currentUser, `ADMIN_BULK_ACCESS_ALL:grant_all`);
          return json({ success: true, action: 'grant_all', modules: allIds });
        } else {
          await env.DB.prepare("UPDATE users SET modules_allowed = 'none' WHERE is_admin = 0").run();
          await logAccess(env, request, currentUser, `ADMIN_BULK_ACCESS_ALL:revoke_all`);
          return json({ success: true, action: 'revoke_all' });
        }
      }

      // GET /api/admin/profile-fields (Campos obrigatórios de cadastro)
      if (pathname === '/api/admin/profile-fields' && request.method === 'GET') {
        const rows = await env.DB.prepare('SELECT * FROM required_profile_fields ORDER BY created_at ASC').all();
        return json(rows.results || []);
      }

      // POST /api/admin/profile-fields (Cadastra ou atualiza campo obrigatório)
      if (pathname === '/api/admin/profile-fields' && request.method === 'POST') {
        const body = await request.json();
        const { key, label, field_type, placeholder, validation_regex, is_required } = body;
        if (!key || !label) {
          return json({ error: 'Chave e rótulo do campo são obrigatórios.' }, 400);
        }
        const cleanKey = String(key).trim().toLowerCase().replace(/[^a-z0-9_]/g, '');

        await env.DB.prepare(`
          INSERT INTO required_profile_fields (key, label, field_type, placeholder, validation_regex, is_required)
          VALUES (?, ?, ?, ?, ?, ?)
          ON CONFLICT(key) DO UPDATE SET
            label = excluded.label,
            field_type = excluded.field_type,
            placeholder = excluded.placeholder,
            validation_regex = excluded.validation_regex,
            is_required = excluded.is_required
        `).bind(
          cleanKey,
          label.trim(),
          field_type || 'text',
          placeholder ? placeholder.trim() : '',
          validation_regex ? validation_regex.trim() : '',
          is_required !== undefined ? (is_required ? 1 : 0) : 1
        ).run();

        await logAccess(env, request, currentUser, `ADMIN_UPSERT_PROFILE_FIELD:${cleanKey}`);
        return json({ success: true, key: cleanKey });
      }

      // DELETE /api/admin/profile-fields/:key (Remove campo obrigatório)
      if (pathname.match(/^\/api\/admin\/profile-fields\/[^/]+$/) && request.method === 'DELETE') {
        const fieldKey = pathname.split('/')[4];
        await env.DB.prepare('DELETE FROM required_profile_fields WHERE key = ?').bind(fieldKey).run();
        await logAccess(env, request, currentUser, `ADMIN_DELETE_PROFILE_FIELD:${fieldKey}`);
        return json({ success: true, key: fieldKey });
      }

  return null;
}
