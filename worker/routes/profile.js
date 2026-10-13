/**
 * Cloudflare Worker — Sub-roteador de Perfil, Configurações de Notificação e Feedback
 * Rotas:
 *   GET  /api/user/profile                      (dados cadastrais, foto, pendências, módulos acessíveis)
 *   POST /api/user/profile/photo                (atualização/remoção direta da foto de perfil pelo próprio usuário)
 *   POST /api/user/profile/request-change       (solicita alteração cadastral de nome/área/função/telefone com validação do admin)
 *   GET  /api/user/profile/review               (página/link seguro para o admin aprovar ou rejeitar)
 *   POST /api/user/profile/review               (processamento da decisão cadastral do admin)
 *   GET  /api/admin/profile-requests            (lista de solicitações para a central admin)
 *   POST /api/admin/profile-requests/:id/decide (aprovação/rejeição pelo painel administrativo)
 *   POST /api/user/preferences                  (preferências de alertas de relatórios)
 *   POST /api/user/feedback                     (reporte de erro ou comentário do colaborador)
 *   POST /api/user/profile/password-reset       (solicita link de recuperação/troca de senha)
 */

import {
  SECURITY_HEADERS,
  json,
  getSessionUser,
  logAccess,
  sendEmail,
  randomHex,
  invalidateSessionUserCache,
  getResponsibleEmails,
  DEFAULT_SYSTEM_MODULES,
  normalizeModuleId,
} from '../utils/security.js';

let _profileSchemaReady = false;

export async function ensureProfileSchema(env) {
  if (_profileSchemaReady || !env.DB) return;
  try {
    await env.DB.prepare("ALTER TABLE users ADD COLUMN foto TEXT").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE users ADD COLUMN profile_metadata TEXT").run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS profile_change_requests (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        user_name TEXT,
        user_email TEXT,
        proposed_changes TEXT NOT NULL,
        current_snapshot TEXT NOT NULL,
        justification TEXT,
        status TEXT NOT NULL DEFAULT 'pendente',
        decision_token TEXT,
        decided_by TEXT,
        decision_note TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        decided_at TEXT
      )
    `).run().catch(() => {});

    await env.DB.prepare('CREATE INDEX IF NOT EXISTS idx_profile_req_user ON profile_change_requests (user_id, status)').run().catch(() => {});
    await env.DB.prepare('CREATE INDEX IF NOT EXISTS idx_profile_req_status ON profile_change_requests (status, created_at DESC)').run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS user_feedbacks (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        user_name TEXT,
        user_email TEXT,
        category TEXT NOT NULL,
        module_id TEXT,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      )
    `).run().catch(() => {});

    await env.DB.prepare('CREATE INDEX IF NOT EXISTS idx_user_feedbacks_created ON user_feedbacks (created_at DESC)').run().catch(() => {});
    _profileSchemaReady = true;
  } catch (err) {
    console.error('Erro ensureProfileSchema:', err);
  }
}

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function emailShell(title, bodyHtml) {
  return `
    <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:4px;overflow:hidden">
      <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte · Plataforma Pephub</div>
        <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">${title}</h2>
      </div>
      <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">${bodyHtml}</div>
    </div>
  `;
}

function reviewHtmlPage(title, bodyHtml) {
  const headers = new Headers({
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  for (const [k, v] of Object.entries(SECURITY_HEADERS)) headers.set(k, v);
  const html = `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · Pephub</title>
<style>
  body{margin:0;background:#f4f6f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;color:#1c2430}
  .bar{background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:14px 22px;color:#fff}
  .bar small{display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;opacity:.9}
  .bar b{font-size:17px}
  .box{max-width:580px;margin:28px auto;background:#fff;border:1px solid #dfe3e8;border-radius:4px;padding:24px;box-shadow:0 4px 14px rgba(0,0,0,.04)}
  table{width:100%;border-collapse:collapse;margin:16px 0;font-size:12.5px}
  th,td{padding:8px 10px;border:1px solid #dfe3e8;text-align:left}
  th{background:#f7f9fb;font-weight:700;color:#5b6675;font-size:11px;text-transform:uppercase}
  .actions{display:flex;gap:12px;margin-top:20px}
  button, .btn{border:0;border-radius:3px;padding:10px 22px;font:700 13px 'Segoe UI',Arial;cursor:pointer;color:#fff;text-decoration:none;display:inline-block;text-align:center}
  .btn-ok{background:#2f7d5d}.btn-no{background:#c0191f}
  .note{font-size:12px;color:#5b6675;margin-top:14px}
</style></head><body>
<div class="bar"><small>Regional Norte</small><b>Pephub · Validação de Alteração Cadastral</b></div>
<div class="box">${bodyHtml}</div></body></html>`;
  return new Response(html, { status: 200, headers });
}

export async function handleProfileRoutes(request, env, url, pathname, ctx) {
  // Somente rotas sob /api/user/ e rotas administrativas de perfil
  const isProfileRoute = pathname.startsWith('/api/user/profile') ||
    pathname === '/api/user/preferences' ||
    pathname === '/api/user/feedback' ||
    pathname.startsWith('/api/admin/profile-requests');

  if (!isProfileRoute) return null;

  try {
    await ensureProfileSchema(env);
    const baseUrl = env.PUBLIC_BASE_URL || `${url.protocol}//${url.host}`;

    // ------------------------------------------------------------------
    // 1. GET /api/user/profile — Dados do perfil do usuário logado
    // ------------------------------------------------------------------
    if (pathname === '/api/user/profile' && request.method === 'GET') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      // Consulta se há solicitação pendente
      const pendingReq = await env.DB.prepare(
        "SELECT id, proposed_changes, created_at, status FROM profile_change_requests WHERE user_id = ? AND status = 'pendente' ORDER BY created_at DESC LIMIT 1"
      ).bind(user.id).first().catch(() => null);

      let parsedProposed = null;
      if (pendingReq && pendingReq.proposed_changes) {
        try { parsedProposed = JSON.parse(pendingReq.proposed_changes); } catch (_) {}
      }

      // Processa metadados / preferências
      let metadata = {};
      try {
        if (user.profile_metadata) metadata = JSON.parse(user.profile_metadata);
      } catch (_) {}

      // Lista de módulos permitidos e legíveis
      const allowedRaw = String(user.modules_allowed || '');
      const isAll = Boolean(user.is_admin) || allowedRaw === 'all';
      let accessibleModules = [];

      try {
        const dbMods = await env.DB.prepare("SELECT id, name, short_name FROM system_modules WHERE status = 'ativo' ORDER BY sort_order ASC").all().catch(() => null);
        if (dbMods && dbMods.results && dbMods.results.length > 0) {
          accessibleModules = dbMods.results.filter(m => isAll || allowedRaw.includes(m.id) || allowedRaw.includes(normalizeModuleId(m.id)));
        }
      } catch (_) {}

      if (accessibleModules.length === 0) {
        accessibleModules = DEFAULT_SYSTEM_MODULES
          .filter(m => isAll || allowedRaw.includes(m[0]) || allowedRaw.includes(normalizeModuleId(m[0])))
          .map(m => ({ id: m[0], name: m[1], short_name: m[2] }));
      }

      return json({
        authenticated: true,
        user: {
          id: user.id,
          nome_completo: user.nome_completo || '',
          login_claro: user.login_claro || '',
          email_claro: user.email_claro || '',
          area: user.area || '',
          funcao: user.funcao || '',
          telefone: user.telefone || '',
          foto: user.foto || '',
          is_admin: Boolean(user.is_admin),
          modules_allowed: user.modules_allowed || '',
          preferences: metadata.preferences || {
            alert_all: false,
            monitored_modules: [],
            notify_new_reports: false,
          }
        },
        pending_request: pendingReq ? {
          id: pendingReq.id,
          created_at: pendingReq.created_at,
          status: pendingReq.status,
          proposed: parsedProposed
        } : null,
        accessible_modules: accessibleModules
      });
    }

    // ------------------------------------------------------------------
    // 2. POST /api/user/profile/photo — Atualização Direta de Foto (Sem aprovação)
    // ------------------------------------------------------------------
    if (pathname === '/api/user/profile/photo' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      const body = await request.json().catch(() => ({}));
      let foto = body.foto ? String(body.foto).trim() : null;

      // Validação e sanitização
      if (foto && !foto.startsWith('data:image/')) {
        foto = null;
      }
      if (foto && foto.length > 350000) {
        return json({ error: 'A foto excede o tamanho limite permitido de 250KB.' }, 400);
      }

      await env.DB.prepare(`
        UPDATE users SET
          foto = ?,
          updated_at = datetime('now')
        WHERE id = ?
      `).bind(foto, user.id).run();

      invalidateSessionUserCache();

      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(logAccess(env, request, user, foto ? 'PROFILE_PHOTO_UPDATED' : 'PROFILE_PHOTO_REMOVED'));
      }

      return json({
        success: true,
        foto,
        message: foto ? 'Foto de perfil atualizada com sucesso!' : 'Foto de perfil removida com sucesso!'
      });
    }

    // ------------------------------------------------------------------
    // 3. POST /api/user/profile/request-change — Solicitar alteração de dados cadastrais
    // ------------------------------------------------------------------
    if (pathname === '/api/user/profile/request-change' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      const body = await request.json().catch(() => ({}));
      const nome = String(body.nome_completo || '').trim().toUpperCase();
      const telefone = String(body.telefone || '').trim();
      const area = String(body.area || '').trim().toUpperCase();
      const funcao = String(body.funcao || '').trim().toUpperCase();
      const justificativa = String(body.justificativa || '').trim();

      if (!nome || nome.length < 3) {
        return json({ error: 'Nome completo deve possuir no mínimo 3 caracteres.' }, 400);
      }
      if (!area) {
        return json({ error: 'Selecione uma área / setor corporativo válido.' }, 400);
      }
      if (!funcao) {
        return json({ error: 'Selecione uma função / cargo corporativo válido.' }, 400);
      }

      // SE O USUÁRIO FOR ADMINISTRADOR: Pode atualizar seus próprios dados diretamente
      if (user.is_admin) {
        await env.DB.prepare(`
          UPDATE users SET
            nome_completo = ?,
            telefone = ?,
            area = ?,
            funcao = ?,
            updated_at = datetime('now')
          WHERE id = ?
        `).bind(nome, telefone, area, funcao, user.id).run();

        invalidateSessionUserCache();
        if (ctx && typeof ctx.waitUntil === 'function') {
          ctx.waitUntil(logAccess(env, request, user, 'PROFILE_UPDATED_DIRECT_ADMIN'));
        }
        return json({
          success: true,
          direct: true,
          message: 'Seus dados cadastrais foram atualizados diretamente com privilégio de administrador.'
        });
      }

      // USUÁRIO COMUM (NÃO-ADMIN):
      // REGRA: Não permitir abrir segundo pedido sem que o administrador tenha aprovado ou rejeitado o anterior
      const existing = await env.DB.prepare(
        "SELECT id, created_at FROM profile_change_requests WHERE user_id = ? AND status = 'pendente'"
      ).bind(user.id).first().catch(() => null);

      if (existing) {
        return json({
          error: 'Você já possui uma solicitação de alteração cadastral pendente de validação pelo administrador. Aguarde a conclusão da análise antes de enviar novo pedido.'
        }, 400);
      }

      const proposed = {
        nome_completo: nome,
        telefone: telefone || user.telefone || '',
        area: area,
        funcao: funcao
      };

      const currentSnapshot = {
        nome_completo: user.nome_completo || '',
        telefone: user.telefone || '',
        area: user.area || '',
        funcao: user.funcao || ''
      };

      const reqId = crypto.randomUUID();
      const token = randomHex(32);

      await env.DB.prepare(`
        INSERT INTO profile_change_requests (id, user_id, user_name, user_email, proposed_changes, current_snapshot, justification, status, decision_token, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pendente', ?, datetime('now'))
      `).bind(reqId, user.id, user.nome_completo, user.email_claro, JSON.stringify(proposed), JSON.stringify(currentSnapshot), justificativa, token).run();

      // Dispara e-mail para o administrador responsável
      const recipients = await getResponsibleEmails(env);
      if (recipients.length > 0) {
        const approveUrl = `${baseUrl}/api/user/profile/review?id=${reqId}&token=${token}&action=aprovar`;
        const denyUrl = `${baseUrl}/api/user/profile/review?id=${reqId}&token=${token}&action=negar`;

        const diffRows = [
          { label: 'Nome Completo', oldV: currentSnapshot.nome_completo, newV: proposed.nome_completo },
          { label: 'Telefone', oldV: currentSnapshot.telefone, newV: proposed.telefone },
          { label: 'Área / Setor', oldV: currentSnapshot.area, newV: proposed.area },
          { label: 'Função', oldV: currentSnapshot.funcao, newV: proposed.funcao }
        ].filter(r => r.oldV !== r.newV);

        const tableRowsHtml = diffRows.map(r => `
          <tr>
            <td style="padding:7px 10px;border:1px solid #dfe3e8;font-weight:600;color:#1c2430">${esc(r.label)}</td>
            <td style="padding:7px 10px;border:1px solid #dfe3e8;color:#5b6675;background:#fbfbfc">${esc(r.oldV || '-')}</td>
            <td style="padding:7px 10px;border:1px solid #dfe3e8;color:#0b7285;font-weight:700;background:#e3fafc">${esc(r.newV || '-')}</td>
          </tr>
        `).join('');

        const emailBody = `
          <p style="margin-top:0">O colaborador <strong>${esc(user.nome_completo)}</strong> (${esc(user.login_claro)}) solicitou alteração de suas informações cadastrais na plataforma:</p>
          <table style="width:100%;border-collapse:collapse;margin:14px 0;font-size:12.5px">
            <thead>
              <tr style="background:#f7f9fb">
                <th style="padding:8px 10px;border:1px solid #dfe3e8;text-align:left">Campo</th>
                <th style="padding:8px 10px;border:1px solid #dfe3e8;text-align:left">Valor Atual</th>
                <th style="padding:8px 10px;border:1px solid #dfe3e8;text-align:left">Novo Valor Solicitado</th>
              </tr>
            </thead>
            <tbody>
              ${tableRowsHtml || '<tr><td colspan="3" style="padding:8px;text-align:center">Nenhuma alteração detectada.</td></tr>'}
            </tbody>
          </table>
          ${justificativa ? `<div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:10px 12px;margin:12px 0"><strong>Observação do Colaborador:</strong><br>${esc(justificativa)}</div>` : ''}
          <div style="margin:24px 0;text-align:center">
            <a href="${approveUrl}" style="background:#2f7d5d;color:#fff;padding:11px 22px;text-decoration:none;font-weight:700;font-size:12.5px;border-radius:3px;display:inline-block;margin-right:10px">Aprovar Alteração</a>
            <a href="${denyUrl}" style="background:#c0191f;color:#fff;padding:11px 22px;text-decoration:none;font-weight:700;font-size:12.5px;border-radius:3px;display:inline-block">Rejeitar Solicitação</a>
          </div>
          <p style="font-size:11.5px;color:#5b6675">Você também pode avaliar na <a href="${baseUrl}/admin/">Central Administrativa › Acessos & Equipe</a>.</p>
        `;

        try {
          await sendEmail(env, {
            to: recipients,
            subject: `[Pephub Regional] Solicitação de alteração cadastral: ${user.nome_completo}`,
            html: emailShell('Solicitação de Alteração Cadastral', emailBody),
            text: `O colaborador ${user.nome_completo} solicitou alteração cadastral. Acesse o painel para validar.`
          });
        } catch (emailErr) {
          console.error('Falha ao enviar e-mail de solicitação de alteração:', emailErr);
        }
      }

      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(logAccess(env, request, user, 'PROFILE_CHANGE_REQUESTED'));
      }

      return json({
        success: true,
        pending: true,
        message: 'Sua solicitação de alteração foi encaminhada ao administrador por e-mail para validação.'
      });
    }

    // ------------------------------------------------------------------
    // 4. GET /api/user/profile/review — Decisão do Administrador via E-mail
    // ------------------------------------------------------------------
    if (pathname === '/api/user/profile/review') {
      const id = url.searchParams.get('id');
      const token = url.searchParams.get('token');
      const action = url.searchParams.get('action');

      if (!id || !token) {
        return reviewHtmlPage('Parâmetros Inválidos', '<p>Identificador ou token de segurança ausente.</p>');
      }

      const row = await env.DB.prepare(
        "SELECT * FROM profile_change_requests WHERE id = ? AND decision_token = ?"
      ).bind(id, token).first().catch(() => null);

      if (!row) {
        return reviewHtmlPage('Solicitação Não Encontrada', '<p>Esta solicitação de alteração cadastral não existe ou o link expirou.</p>');
      }

      if (row.status !== 'pendente') {
        return reviewHtmlPage('Solicitação Já Finalizada', `
          <p>Esta solicitação já foi <strong>${row.status === 'aprovado' ? 'aprovada' : 'rejeitada'}</strong> anteriormente em ${esc(row.decided_at || '')} por ${esc(row.decided_by || 'administrador')}.</p>
          <p><a href="${baseUrl}/admin/" class="btn btn-ok">Acessar Painel de Controle</a></p>
        `);
      }

      let proposed = {};
      try { proposed = JSON.parse(row.proposed_changes); } catch (_) {}

      // Executa a aprovação ou negação
      if (action === 'aprovar' || action === 'negar') {
        const isApprove = action === 'aprovar';
        const decider = env.ADMIN_EMAIL || 'Administrador via E-mail';

        if (isApprove) {
          const pNome = proposed.nome_completo ? String(proposed.nome_completo).trim() : null;
          const pArea = proposed.area ? String(proposed.area).trim() : null;
          const pFuncao = proposed.funcao ? String(proposed.funcao).trim() : null;
          const pTel = proposed.telefone ? String(proposed.telefone).trim() : null;

          await env.DB.prepare(`
            UPDATE users SET
              nome_completo = COALESCE(?, nome_completo),
              area = COALESCE(?, area),
              funcao = COALESCE(?, funcao),
              telefone = COALESCE(?, telefone),
              updated_at = datetime('now')
            WHERE id = ?
          `).bind(pNome, pArea, pFuncao, pTel, row.user_id).run();

          await env.DB.prepare(`
            UPDATE profile_change_requests SET
              status = 'aprovado',
              decided_at = datetime('now'),
              decided_by = ?
            WHERE id = ?
          `).bind(decider, id).run();

          invalidateSessionUserCache();

          // Notifica o colaborador
          if (row.user_email) {
            try {
              await sendEmail(env, {
                to: row.user_email,
                subject: '[Pephub Regional] Sua alteração cadastral foi aprovada!',
                html: emailShell('Alteração Cadastral Aprovada', `
                  <p>Olá, <strong>${esc(row.user_name)}</strong>,</p>
                  <p>Sua solicitação de atualização cadastral foi <span style="color:#2f7d5d;font-weight:700">APROVADA</span> pelo administrador e os novos dados já estão ativos na plataforma.</p>
                  <p><a href="${baseUrl}/" style="background:#1c2430;color:#fff;padding:9px 18px;text-decoration:none;border-radius:3px;font-weight:700;display:inline-block">Acessar Pephub</a></p>
                `),
                text: `Olá ${row.user_name}, sua alteração cadastral foi aprovada pelo administrador.`
              });
            } catch (_) {}
          }

          return reviewHtmlPage('Alteração Aprovada com Sucesso', `
            <h3 style="color:#2f7d5d;margin-top:0">✓ Alteração Cadastral Aprovada!</h3>
            <p>Os dados cadastrais de <strong>${esc(row.user_name)}</strong> foram atualizados com sucesso no sistema.</p>
            <p><a href="${baseUrl}/admin/" class="btn btn-ok">Voltar à Central Administrativa</a></p>
          `);
        } else {
          await env.DB.prepare(`
            UPDATE profile_change_requests SET
              status = 'rejeitado',
              decided_at = datetime('now'),
              decided_by = ?
            WHERE id = ?
          `).bind(decider, id).run();

          // Notifica o colaborador
          if (row.user_email) {
            try {
              await sendEmail(env, {
                to: row.user_email,
                subject: '[Pephub Regional] Atualização cadastral não aprovada',
                html: emailShell('Solicitação Cadastral Não Aprovada', `
                  <p>Olá, <strong>${esc(row.user_name)}</strong>,</p>
                  <p>Sua solicitação de alteração cadastral foi revisada e <strong>não foi aprovada</strong> pela administração da Regional Norte. Seus dados cadastrais atuais permanecem inalterados.</p>
                `),
                text: `Olá ${row.user_name}, sua solicitação de alteração cadastral não foi aprovada.`
              });
            } catch (_) {}
          }

          return reviewHtmlPage('Solicitação Rejeitada', `
            <h3 style="color:#c0191f;margin-top:0">✕ Solicitação Rejeitada</h3>
            <p>A solicitação de alteração de <strong>${esc(row.user_name)}</strong> foi rejeitada. Nenhuma alteração foi realizada no cadastro.</p>
            <p><a href="${baseUrl}/admin/" class="btn btn-ok">Voltar à Central Administrativa</a></p>
          `);
        }
      }

      return reviewHtmlPage('Revisão Cadastral', '<p>Ação não especificada.</p>');
    }

    // ------------------------------------------------------------------
    // 5. GET /api/admin/profile-requests — Lista no Painel Administrativo
    // ------------------------------------------------------------------
    if (pathname === '/api/admin/profile-requests' && request.method === 'GET') {
      const user = await getSessionUser(request, env);
      if (!user || !user.is_admin) return json({ error: 'Acesso restrito.' }, 403);

      const rows = await env.DB.prepare(`
        SELECT r.*, u.login_claro, u.area as current_area, u.funcao as current_funcao
        FROM profile_change_requests r
        LEFT JOIN users u ON u.id = r.user_id
        ORDER BY CASE r.status WHEN 'pendente' THEN 0 ELSE 1 END, r.created_at DESC
        LIMIT 100
      `).all().catch(() => ({ results: [] }));

      return json({ requests: rows.results || [] });
    }

    // ------------------------------------------------------------------
    // 6. POST /api/admin/profile-requests/:id/decide — Decisão no Admin
    // ------------------------------------------------------------------
    const decideMatch = pathname.match(/^\/api\/admin\/profile-requests\/([^/]+)\/decide$/);
    if (decideMatch && request.method === 'POST') {
      const admin = await getSessionUser(request, env);
      if (!admin || !admin.is_admin) return json({ error: 'Acesso restrito.' }, 403);

      const reqId = decideMatch[1];
      const body = await request.json().catch(() => ({}));
      const action = body.action === 'aprovar' ? 'aprovar' : body.action === 'negar' ? 'negar' : null;
      if (!action) return json({ error: 'Ação inválida.' }, 400);

      const row = await env.DB.prepare("SELECT * FROM profile_change_requests WHERE id = ?").bind(reqId).first().catch(() => null);
      if (!row) return json({ error: 'Solicitação não localizada.' }, 404);
      if (row.status !== 'pendente') return json({ error: 'Esta solicitação já foi decidida.' }, 409);

      let proposed = {};
      try { proposed = JSON.parse(row.proposed_changes); } catch (_) {}

      if (action === 'aprovar') {
        const pNome = proposed.nome_completo ? String(proposed.nome_completo).trim() : null;
        const pArea = proposed.area ? String(proposed.area).trim() : null;
        const pFuncao = proposed.funcao ? String(proposed.funcao).trim() : null;
        const pTel = proposed.telefone ? String(proposed.telefone).trim() : null;

        await env.DB.prepare(`
          UPDATE users SET
            nome_completo = COALESCE(?, nome_completo),
            area = COALESCE(?, area),
            funcao = COALESCE(?, funcao),
            telefone = COALESCE(?, telefone),
            updated_at = datetime('now')
          WHERE id = ?
        `).bind(pNome, pArea, pFuncao, pTel, row.user_id).run();

        await env.DB.prepare(`
          UPDATE profile_change_requests SET
            status = 'aprovado',
            decided_at = datetime('now'),
            decided_by = ?
          WHERE id = ?
        `).bind(admin.email_claro || admin.login_claro, reqId).run();

        invalidateSessionUserCache();
      } else {
        await env.DB.prepare(`
          UPDATE profile_change_requests SET
            status = 'rejeitado',
            decided_at = datetime('now'),
            decided_by = ?
          WHERE id = ?
        `).bind(admin.email_claro || admin.login_claro, reqId).run();
      }

      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(logAccess(env, request, admin, `ADMIN_PROFILE_REQUEST_${action.toUpperCase()}:${row.user_email}`));
      }
      return json({ success: true, status: action === 'aprovar' ? 'aprovado' : 'rejeitado' });
    }

    // ------------------------------------------------------------------
    // 7. POST /api/user/preferences — Salvar preferências de notificação
    // ------------------------------------------------------------------
    if (pathname === '/api/user/preferences' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      const body = await request.json().catch(() => ({}));
      const alertAll = Boolean(body.alert_all);
      const monitoredModules = Array.isArray(body.monitored_modules) ? body.monitored_modules.map(String) : [];
      const notifyNewReports = Boolean(body.notify_new_reports);

      let metadata = {};
      try {
        if (user.profile_metadata) metadata = JSON.parse(user.profile_metadata);
      } catch (_) {}

      metadata.preferences = {
        alert_all: alertAll,
        monitored_modules: alertAll ? [] : monitoredModules,
        notify_new_reports: notifyNewReports,
        updated_at: new Date().toISOString()
      };

      await env.DB.prepare("UPDATE users SET profile_metadata = ?, updated_at = datetime('now') WHERE id = ?")
        .bind(JSON.stringify(metadata), user.id).run();

      invalidateSessionUserCache();

      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(logAccess(env, request, user, 'PREFERENCES_UPDATED'));
      }
      return json({ success: true, message: 'Preferências de notificação salvas com sucesso.' });
    }

    // ------------------------------------------------------------------
    // 8. POST /api/user/feedback — Informar erro ou fazer comentário
    // ------------------------------------------------------------------
    if (pathname === '/api/user/feedback' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      const body = await request.json().catch(() => ({}));
      const category = String(body.category || body.type || 'erro').trim();
      const moduleId = String(body.module_id || body.module || 'geral').trim();
      const message = String(body.message || '').trim();

      if (!message || message.length < 2) {
        return json({ error: 'Por favor, descreva sua mensagem antes de enviar.' }, 400);
      }
      if (message.length > 3000) {
        return json({ error: 'A mensagem não pode exceder 3.000 caracteres.' }, 400);
      }

      const fid = crypto.randomUUID();
      await env.DB.prepare(`
        INSERT INTO user_feedbacks (id, user_id, user_name, user_email, category, module_id, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
      `).bind(fid, user.id, user.nome_completo, user.email_claro, category, moduleId, message).run();

      // Notifica o administrador por e-mail protegido por try/catch
      const recipients = await getResponsibleEmails(env);
      if (recipients.length > 0) {
        const emailHtml = emailShell('Novo Feedback / Reporte de Usuário', `
          <p>O colaborador <strong>${esc(user.nome_completo)}</strong> (${esc(user.login_claro)} · ${esc(user.email_claro)}) enviou uma mensagem pelo formulário de configurações:</p>
          <p><strong>Categoria:</strong> ${esc(category.toUpperCase())}<br>
          <strong>Módulo / Área:</strong> ${esc(moduleId)}</p>
          <div style="background:#f7f8fa;border:1px solid #dfe3e8;border-radius:4px;padding:12px;margin:12px 0;white-space:pre-wrap">${esc(message)}</div>
        `);
        try {
          await sendEmail(env, {
            to: recipients,
            subject: `[Pephub Regional] Feedback do usuário: ${user.nome_completo} (${category})`,
            html: emailHtml,
            text: `Feedback de ${user.nome_completo}: ${message}`
          });
        } catch (_) {}
      }

      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(logAccess(env, request, user, `USER_FEEDBACK_${category.toUpperCase()}:${moduleId}`));
      }
      return json({ success: true, message: 'Sua mensagem foi recebida com sucesso e encaminhada aos responsáveis pela ferramenta.' });
    }

    // ------------------------------------------------------------------
    // 9. POST /api/user/profile/password-reset — Link de redefinição de senha
    // ------------------------------------------------------------------
    if (pathname === '/api/user/profile/password-reset' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) return json({ error: 'Não autenticado.' }, 401);

      const token = randomHex(32);
      await env.DB.prepare(`
        UPDATE users SET
          senha_salt = ?,
          must_change_password = 1,
          updated_at = datetime('now')
        WHERE id = ?
      `).bind(token, user.id).run();

      const resetLink = `${baseUrl}/login/?reset_token=${token}&login=${encodeURIComponent(user.login_claro)}`;

      if (user.email_claro) {
        try {
          await sendEmail(env, {
            to: user.email_claro,
            subject: '[Pephub Regional] Redefinição de Senha Solicitada',
            html: emailShell('Redefinição de Senha Solicitada', `
              <p>Olá, <strong>${esc(user.nome_completo)}</strong>,</p>
              <p>Você solicitou a redefinição de sua senha corporativa no Pephub. Clique no botão abaixo para cadastrar uma nova senha:</p>
              <div style="margin:20px 0;text-align:center">
                <a href="${resetLink}" style="background:#8a0f18;color:#fff;padding:10px 22px;text-decoration:none;font-weight:700;border-radius:3px;display:inline-block">Redefinir Minha Senha</a>
              </div>
              <p style="font-size:11.5px;color:#5b6675">Este link é válido para utilização imediata. Se você não solicitou esta alteração, ignore este e-mail.</p>
            `),
            text: `Acesse o link para redefinir sua senha: ${resetLink}`
          });
        } catch (_) {}
      }

      return json({
        success: true,
        message: `Um e-mail corporativo com o link para redefinição de senha foi enviado para ${user.email_claro}.`
      });
    }

    return null;
  } catch (err) {
    console.error('Erro handleProfileRoutes:', err);
    return json({ error: 'Erro interno ao processar requisição de perfil.', details: err.message }, 500);
  }
}
