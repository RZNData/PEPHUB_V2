/**
 * Sub-roteador de Presença e Solicitações de Acesso
 * Rotas:
 *   POST /api/auth/heartbeat                       (sinal de presença do usuário logado)
 *   GET  /api/access-requests/mine                 (solicitações do próprio usuário)
 *   POST /api/access-requests                      (cria solicitação com justificativa + e-mail ao responsável)
 *   GET  /api/access-requests/review               (página de decisão aberta pelo link do e-mail)
 *   POST /api/access-requests/review               (confirma decisão a partir da página do e-mail)
 *   GET  /api/admin/access-requests                (lista para o painel administrativo)
 *   POST /api/admin/access-requests/:id/decide     (aprova/nega pelo painel administrativo)
 */

import {
  SECURITY_HEADERS,
  json,
  parseCookies,
  getSessionUser,
  touchSessionPresence,
  ensureAccessRequestsTable,
  normalizeModuleId,
  checkReportAccess,
  invalidateSessionUserCache,
  sendEmail,
  randomHex,
  logAccess,
  DEFAULT_SYSTEM_MODULES,
} from '../utils/security.js';

const MAX_REQUESTS_PER_DAY = 10;
const REVIEW_LINK_TTL_DAYS = 30;

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function htmlResponse(html, status = 200) {
  const headers = new Headers({
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  for (const [k, v] of Object.entries(SECURITY_HEADERS)) headers.set(k, v);
  return new Response(html, { status, headers });
}

function emailShell(title, bodyHtml) {
  return `
    <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
      <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
        <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">${title}</h2>
      </div>
      <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">${bodyHtml}</div>
    </div>
  `;
}

function reviewPage(title, bodyHtml) {
  return htmlResponse(`<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · Pephub</title>
<style>
  body{margin:0;background:#f4f6f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;color:#1c2430}
  .bar{background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:14px 22px;color:#fff}
  .bar small{display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;opacity:.9}
  .bar b{font-size:17px}
  .box{max-width:560px;margin:28px auto;background:#fff;border:1px solid #dfe3e8;border-radius:4px;padding:22px}
  .row{margin:0 0 12px;font-size:13px}
  .row span{display:block;font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;color:#5b6675;margin-bottom:2px}
  .just{background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:10px 12px;white-space:pre-wrap}
  textarea{width:100%;box-sizing:border-box;border:1px solid #cfd6de;border-radius:3px;padding:8px;font:13px 'Segoe UI',Arial;min-height:60px}
  .actions{display:flex;gap:10px;margin-top:16px}
  button{border:0;border-radius:3px;padding:10px 20px;font:700 13px 'Segoe UI',Arial;cursor:pointer;color:#fff}
  .ok{background:#2f7d5d}.no{background:#c0191f}
  .note{font-size:12px;color:#5b6675}
</style></head><body>
<div class="bar"><small>Regional Norte</small><b>Pephub · Solicitação de Acesso a Relatório</b></div>
<div class="box">${bodyHtml}</div></body></html>`);
}

async function findModuleName(env, canonicalId) {
  try {
    const rows = await env.DB.prepare('SELECT id, name FROM system_modules').all();
    const hit = (rows.results || []).find((r) => normalizeModuleId(r.id) === canonicalId);
    if (hit) return hit.name;
  } catch (_) { /* tabela ainda não existe: usa catálogo padrão */ }
  const def = DEFAULT_SYSTEM_MODULES.find((m) => normalizeModuleId(m[0]) === canonicalId);
  return def ? def[1] : null;
}

async function getResponsibleEmails(env) {
  const list = [];
  if (env.ADMIN_EMAIL) list.push(String(env.ADMIN_EMAIL).trim().toLowerCase());
  if (list.length === 0) {
    const admins = await env.DB.prepare("SELECT email_claro FROM users WHERE is_admin = 1 AND status = 'aprovado'").all().catch(() => ({ results: [] }));
    for (const a of admins.results || []) if (a.email_claro) list.push(String(a.email_claro).toLowerCase());
  }
  return [...new Set(list)];
}

function isReviewLinkExpired(createdAt) {
  if (!createdAt) return false;
  const d = new Date(String(createdAt).replace(' ', 'T') + 'Z');
  return Date.now() - d.getTime() > REVIEW_LINK_TTL_DAYS * 86400 * 1000;
}

/**
 * Aplica a decisão. Aprovando, grava o módulo em users.modules_allowed (mesma lista exibida
 * em "Privilégios") e invalida o cache de sessão para refletir imediatamente.
 */
async function applyDecision(env, request, baseUrl, reqRow, action, decidedBy, note) {
  if (reqRow.status !== 'pendente') {
    return { ok: false, error: `Esta solicitação já foi ${reqRow.status === 'aprovado' ? 'aprovada' : 'negada'}.` };
  }
  const approve = action === 'aprovar';
  const target = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(reqRow.user_id).first();

  if (approve) {
    if (!target) return { ok: false, error: 'Colaborador não localizado (cadastro removido).' };
    const raw = target.modules_allowed;
    if (!target.is_admin && raw !== 'all') {
      const current = raw && raw !== 'none'
        ? String(raw).split(',').map(normalizeModuleId).filter(Boolean)
        : [];
      if (!current.includes(reqRow.module_id)) current.push(reqRow.module_id);
      await env.DB.prepare('UPDATE users SET modules_allowed = ? WHERE id = ?').bind(current.join(','), target.id).run();
      invalidateSessionUserCache();
    }
  }

  await env.DB.prepare(`
    UPDATE access_requests
    SET status = ?, decided_by = ?, decision_note = ?, decided_at = datetime('now'), decision_token = NULL
    WHERE id = ? AND status = 'pendente'
  `).bind(approve ? 'aprovado' : 'negado', decidedBy, note || null, reqRow.id).run();

  if (target && target.email_claro) {
    const noteHtml = note
      ? `<div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:10px 12px;margin:12px 0"><strong>Observação do responsável:</strong><br>${esc(note)}</div>`
      : '';
    const body = approve
      ? `<p style="margin-top:0">Prezado(a) <strong>${esc(target.nome_completo)}</strong>,</p>
         <p>Sua solicitação de acesso ao relatório <strong>${esc(reqRow.module_name)}</strong> foi <strong style="color:#2f7d5d">aprovada</strong>.</p>${noteHtml}
         <p>O relatório já está disponível no seu catálogo.</p>
         <div style="margin:22px 0;text-align:center"><a href="${baseUrl}/" style="background:#1b2430;color:#fff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">Abrir Catálogo</a></div>`
      : `<p style="margin-top:0">Prezado(a) <strong>${esc(target.nome_completo)}</strong>,</p>
         <p>Sua solicitação de acesso ao relatório <strong>${esc(reqRow.module_name)}</strong> <strong style="color:#c0191f">não foi aprovada</strong> neste momento.</p>${noteHtml}
         <p>Em caso de dúvidas, fale diretamente com o responsável pela ferramenta.</p>`;
    await sendEmail(env, {
      to: target.email_claro,
      subject: `[Pephub Regional] Solicitação de acesso ${approve ? 'aprovada' : 'negada'}: ${reqRow.module_name}`,
      html: emailShell(approve ? 'Acesso Aprovado' : 'Solicitação Não Aprovada', body),
      text: `Sua solicitação de acesso ao relatório ${reqRow.module_name} foi ${approve ? 'aprovada' : 'negada'}.${note ? ' Observação: ' + note : ''}`,
    }).catch(() => {});
  }

  return { ok: true, status: approve ? 'aprovado' : 'negado' };
}

export async function handleAccessRoutes(request, env, url, pathname) {
  // ------------------------------------------------------------------
  // POST /api/auth/heartbeat — presença em tempo real
  // ------------------------------------------------------------------
  if (pathname === '/api/auth/heartbeat' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user) return json({ ok: false }, 401);
    const token = parseCookies(request)['pephub_session'];
    await touchSessionPresence(env, token);
    return json({ ok: true });
  }

  if (!pathname.startsWith('/api/access-requests') && !pathname.startsWith('/api/admin/access-requests')) {
    return null;
  }

  await ensureAccessRequestsTable(env);
  const baseUrl = env.PUBLIC_BASE_URL || `${url.protocol}//${url.host}`;

  // ------------------------------------------------------------------
  // GET /api/access-requests/mine
  // ------------------------------------------------------------------
  if (pathname === '/api/access-requests/mine' && request.method === 'GET') {
    const user = await getSessionUser(request, env);
    if (!user) return json({ error: 'Não autenticado' }, 401);
    const rows = await env.DB.prepare(`
      SELECT id, module_id, module_name, status, created_at, decided_at, decision_note
      FROM access_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 50
    `).bind(user.id).all();
    return json({ requests: rows.results || [] });
  }

  // ------------------------------------------------------------------
  // POST /api/access-requests — nova solicitação
  // ------------------------------------------------------------------
  if (pathname === '/api/access-requests' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user) return json({ error: 'Não autenticado' }, 401);

    const body = await request.json().catch(() => ({}));
    const moduleId = normalizeModuleId(body.module_id);
    const justification = String(body.justification || '').trim();

    if (!moduleId) return json({ error: 'Relatório não informado.' }, 400);
    if (justification.length < 10) return json({ error: 'Descreva a justificativa com pelo menos 10 caracteres.' }, 400);
    if (justification.length > 1000) return json({ error: 'A justificativa deve ter no máximo 1000 caracteres.' }, 400);

    const moduleName = await findModuleName(env, moduleId);
    if (!moduleName) return json({ error: 'Relatório inexistente no catálogo.' }, 404);

    if (checkReportAccess(user, moduleId)) {
      return json({ error: 'Você já possui acesso a este relatório.' }, 409);
    }

    const pending = await env.DB.prepare(
      "SELECT id FROM access_requests WHERE user_id = ? AND module_id = ? AND status = 'pendente'"
    ).bind(user.id, moduleId).first();
    if (pending) return json({ error: 'Já existe uma solicitação pendente para este relatório.' }, 409);

    const today = await env.DB.prepare(
      "SELECT COUNT(*) AS c FROM access_requests WHERE user_id = ? AND datetime(created_at) > datetime('now','-1 day')"
    ).bind(user.id).first();
    if ((today?.c || 0) >= MAX_REQUESTS_PER_DAY) {
      return json({ error: 'Limite diário de solicitações atingido. Tente novamente amanhã.' }, 429);
    }

    const id = crypto.randomUUID();
    const token = randomHex(32);
    await env.DB.prepare(`
      INSERT INTO access_requests (id, user_id, user_name, user_email, module_id, module_name, justification, status, decision_token, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'pendente', ?, datetime('now'))
    `).bind(id, user.id, user.nome_completo, user.email_claro, moduleId, moduleName, justification, token).run();

    const approveUrl = `${baseUrl}/api/access-requests/review?id=${id}&token=${token}&action=aprovar`;
    const denyUrl = `${baseUrl}/api/access-requests/review?id=${id}&token=${token}&action=negar`;
    const recipients = await getResponsibleEmails(env);

    let emailSent = false;
    if (recipients.length > 0) {
      const html = emailShell('Solicitação de Acesso a Relatório', `
        <p style="margin-top:0">Um colaborador solicitou acesso a um relatório da plataforma:</p>
        <table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0">
          <tr><td style="padding:6px 8px;color:#5b6675;width:32%">Colaborador</td><td style="padding:6px 8px"><strong>${esc(user.nome_completo)}</strong></td></tr>
          <tr><td style="padding:6px 8px;color:#5b6675">E-mail</td><td style="padding:6px 8px">${esc(user.email_claro)}</td></tr>
          <tr><td style="padding:6px 8px;color:#5b6675">Canal / Função</td><td style="padding:6px 8px">${esc(user.area || '-')} · ${esc(user.funcao || '-')}</td></tr>
          <tr><td style="padding:6px 8px;color:#5b6675">Relatório</td><td style="padding:6px 8px"><strong>${esc(moduleName)}</strong></td></tr>
        </table>
        <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:12px;white-space:pre-wrap"><strong>Justificativa:</strong><br>${esc(justification)}</div>
        <div style="margin:24px 0;text-align:center">
          <a href="${approveUrl}" style="background:#2f7d5d;color:#fff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block;margin-right:8px">Revisar e Aprovar</a>
          <a href="${denyUrl}" style="background:#c0191f;color:#fff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">Revisar e Negar</a>
        </div>
        <p style="font-size:11.5px;color:#5b6675">Você também pode decidir em <a href="${baseUrl}/admin/">Central Administrativa › Solicitações de Acesso</a>. O link é válido por ${REVIEW_LINK_TTL_DAYS} dias e de uso único.</p>
      `);
      const r = await sendEmail(env, {
        to: recipients,
        subject: `[Pephub Regional] Solicitação de acesso: ${moduleName} — ${user.nome_completo}`,
        html,
        text: `${user.nome_completo} (${user.email_claro}) solicitou acesso a "${moduleName}". Justificativa: ${justification}. Aprovar: ${approveUrl} | Negar: ${denyUrl}`,
      }).catch(() => ({ success: false }));
      emailSent = Boolean(r && r.success);
    }

    await logAccess(env, request, user, `ADMIN_ACCESS_REQUEST_CREATED:${moduleId}`);
    return json({ success: true, id, email_sent: emailSent, message: 'Solicitação enviada ao responsável pela ferramenta.' });
  }

  // ------------------------------------------------------------------
  // Página de decisão aberta pelo link do e-mail (exige confirmação via POST: evita
  // aprovação acidental por pré-visualização/scanner de links)
  // ------------------------------------------------------------------
  if (pathname === '/api/access-requests/review') {
    const isPost = request.method === 'POST';
    let id; let token; let action; let note = '';
    if (isPost) {
      const form = await request.formData().catch(() => null);
      if (!form) return reviewPage('Solicitação inválida', '<p>Requisição inválida.</p>');
      id = String(form.get('id') || '');
      token = String(form.get('token') || '');
      action = String(form.get('action') || '');
      note = String(form.get('note') || '').trim().slice(0, 500);
    } else {
      id = url.searchParams.get('id') || '';
      token = url.searchParams.get('token') || '';
      action = url.searchParams.get('action') || '';
    }

    const row = id ? await env.DB.prepare('SELECT * FROM access_requests WHERE id = ?').bind(id).first() : null;
    if (!row) return reviewPage('Solicitação não encontrada', '<p>Esta solicitação não existe ou foi removida.</p>');

    if (row.status !== 'pendente') {
      return reviewPage('Solicitação já decidida', `<p>Esta solicitação já foi <strong>${row.status === 'aprovado' ? 'aprovada' : 'negada'}</strong>${row.decided_at ? ' em ' + esc(row.decided_at) + ' (UTC)' : ''}.</p>`);
    }
    if (!row.decision_token || row.decision_token !== token || isReviewLinkExpired(row.created_at)) {
      return reviewPage('Link inválido ou expirado', '<p>Este link não é mais válido. Utilize a Central Administrativa para decidir a solicitação.</p>');
    }

    if (isPost) {
      if (action !== 'aprovar' && action !== 'negar') return reviewPage('Ação inválida', '<p>Ação não reconhecida.</p>');
      const result = await applyDecision(env, request, baseUrl, row, action, 'link-email', note);
      if (!result.ok) return reviewPage('Não foi possível concluir', `<p>${esc(result.error)}</p>`);
      return reviewPage('Decisão registrada', `
        <p><strong>Solicitação ${result.status === 'aprovado' ? 'aprovada' : 'negada'} com sucesso.</strong></p>
        <p class="note">${result.status === 'aprovado'
          ? `O relatório <strong>${esc(row.module_name)}</strong> já foi liberado para ${esc(row.user_name)} e o colaborador foi avisado por e-mail.`
          : `${esc(row.user_name)} foi avisado(a) por e-mail.`}</p>
      `);
    }

    const verb = action === 'negar' ? 'Negar' : 'Aprovar';
    return reviewPage('Revisar solicitação', `
      <div class="row"><span>Colaborador</span><strong>${esc(row.user_name)}</strong> · ${esc(row.user_email)}</div>
      <div class="row"><span>Relatório solicitado</span><strong>${esc(row.module_name)}</strong></div>
      <div class="row"><span>Justificativa</span><div class="just">${esc(row.justification)}</div></div>
      <form method="POST" action="/api/access-requests/review">
        <input type="hidden" name="id" value="${esc(row.id)}">
        <input type="hidden" name="token" value="${esc(token)}">
        <div class="row"><span>Observação ao colaborador (opcional)</span><textarea name="note" maxlength="500"></textarea></div>
        <div class="actions">
          <button class="${action === 'negar' ? 'no' : 'ok'}" type="submit" name="action" value="${action === 'negar' ? 'negar' : 'aprovar'}">Confirmar: ${verb}</button>
          <button class="${action === 'negar' ? 'ok' : 'no'}" type="submit" name="action" value="${action === 'negar' ? 'aprovar' : 'negar'}">${action === 'negar' ? 'Aprovar' : 'Negar'} em vez disso</button>
        </div>
      </form>
    `);
  }

  // ------------------------------------------------------------------
  // Rotas administrativas (painel)
  // ------------------------------------------------------------------
  if (pathname.startsWith('/api/admin/access-requests')) {
    const admin = await getSessionUser(request, env);
    if (!admin || !admin.is_admin) return json({ error: 'Acesso restrito ao responsável pela ferramenta.' }, 403);

    if (pathname === '/api/admin/access-requests' && request.method === 'GET') {
      const statusFilter = url.searchParams.get('status');
      let rows;
      if (statusFilter && statusFilter !== 'todos') {
        rows = await env.DB.prepare(`
          SELECT r.id, r.user_id, r.user_name, r.user_email, r.module_id, r.module_name, r.justification,
                 r.status, r.decided_by, r.decision_note, r.created_at, r.decided_at,
                 u.area AS user_area, u.funcao AS user_funcao
          FROM access_requests r LEFT JOIN users u ON u.id = r.user_id
          WHERE r.status = ?
          ORDER BY CASE r.status WHEN 'pendente' THEN 0 ELSE 1 END, r.created_at DESC
          LIMIT 200
        `).bind(statusFilter).all();
      } else {
        rows = await env.DB.prepare(`
          SELECT r.id, r.user_id, r.user_name, r.user_email, r.module_id, r.module_name, r.justification,
                 r.status, r.decided_by, r.decision_note, r.created_at, r.decided_at,
                 u.area AS user_area, u.funcao AS user_funcao
          FROM access_requests r LEFT JOIN users u ON u.id = r.user_id
          ORDER BY CASE r.status WHEN 'pendente' THEN 0 ELSE 1 END, r.created_at DESC
          LIMIT 200
        `).all();
      }
      const pendingCount = await env.DB.prepare("SELECT COUNT(*) AS c FROM access_requests WHERE status = 'pendente'").first();
      return json({ requests: rows.results || [], pending: pendingCount?.c || 0 });
    }

    const m = pathname.match(/^\/api\/admin\/access-requests\/([^/]+)\/decide$/);
    if (m && request.method === 'POST') {
      const body = await request.json().catch(() => ({}));
      const action = body.action === 'negar' ? 'negar' : body.action === 'aprovar' ? 'aprovar' : null;
      if (!action) return json({ error: 'Ação inválida.' }, 400);
      const row = await env.DB.prepare('SELECT * FROM access_requests WHERE id = ?').bind(m[1]).first();
      if (!row) return json({ error: 'Solicitação não localizada.' }, 404);
      const result = await applyDecision(env, request, baseUrl, row, action, admin.email_claro || admin.login_claro, String(body.note || '').trim().slice(0, 500));
      if (!result.ok) return json({ error: result.error }, 409);
      await logAccess(env, request, admin, `ADMIN_ACCESS_REQUEST_${action.toUpperCase()}:${row.module_id}:${row.user_email}`);
      return json({ success: true, status: result.status });
    }

    return json({ error: 'Rota administrativa não encontrada.' }, 404);
  }

  return null;
}
