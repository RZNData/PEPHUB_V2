/**
 * Sub-roteador de Gestão, Monitoramento e Rastreamento de E-mails Corporativos
 * Regional Norte — Pephub Plataforma
 *
 * Rotas Públicas / Webhooks:
 *   GET  /api/emails/track/:id         (pixel transparente 1x1 de rastreamento de abertura)
 *   POST /api/emails/webhook           (webhook de eventos do Resend: opened, delivered, bounced)
 *   POST /api/emails/inbound           (recebimento de e-mails / mensagens inbound)
 *
 * Rotas Administrativas:
 *   GET  /api/admin/emails             (lista de e-mails com filtros por usuário, direção, status e busca)
 *   GET  /api/admin/emails/:id         (detalhes completos do e-mail com conteúdo HTML/texto)
 *   POST /api/admin/emails/resend/:id  (reenvio de e-mail com falha)
 *   POST /api/admin/emails/test-send   (disparo de e-mail teste para colaborador)
 *   POST /api/admin/emails/simulate-inbound (simulação de recebimento para auditoria)
 */

import {
  json,
  getSessionUser,
  randomHex,
  sendEmail,
  SECURITY_HEADERS,
} from '../utils/security.js';

// GIF 1x1 transparente (43 bytes padrão GIF89a)
const PIXEL_GIF = new Uint8Array([
  0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00,
  0x80, 0x00, 0x00, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x21,
  0xf9, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00, 0x2c, 0x00, 0x00,
  0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
  0x01, 0x00, 0x3b
]);

let _emailTablesInitialized = false;

// Garante criação das tabelas e índices de e-mails no SQLite / D1
export async function ensureEmailTables(env) {
  if (_emailTablesInitialized || !env || !env.DB) return;
  _emailTablesInitialized = true;
  try {
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS email_logs (
        id TEXT PRIMARY KEY,
        direction TEXT NOT NULL DEFAULT 'outbound',
        user_id TEXT,
        user_name TEXT,
        user_email TEXT,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        subject TEXT NOT NULL,
        content_html TEXT,
        content_text TEXT,
        status TEXT NOT NULL DEFAULT 'sent',
        error_message TEXT,
        opened_at DATETIME,
        open_count INTEGER DEFAULT 0,
        ip_open TEXT,
        user_agent_open TEXT,
        resend_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_email_logs_user ON email_logs(user_id, created_at DESC)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_email_logs_to ON email_logs(to_address, created_at DESC)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_email_logs_direction ON email_logs(direction)
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_email_logs_created ON email_logs(created_at DESC)
    `).run().catch(() => {});
  } catch (err) {
    console.error('Erro em ensureEmailTables:', err);
  }
}

// Grava log detalhado de e-mail no D1
export async function recordEmailLog(env, {
  id,
  direction = 'outbound',
  userId = null,
  userName = null,
  userEmail = null,
  fromAddress,
  toAddress,
  subject,
  contentHtml = null,
  contentText = null,
  status = 'sent',
  errorMessage = null,
  resendId = null
}) {
  if (!env || !env.DB) return null;
  await ensureEmailTables(env);

  const logId = id || `eml_${randomHex(8)}`;

  // Tenta resolver usuário pelo e-mail se não fornecido
  let resolvedUserId = userId;
  let resolvedUserName = userName;
  let resolvedUserEmail = userEmail;

  if (!resolvedUserId) {
    const targetEmail = direction === 'inbound' ? fromAddress : toAddress;
    const cleanMail = String(targetEmail || '').toLowerCase().trim();
    if (cleanMail) {
      const u = await env.DB.prepare(
        "SELECT id, nome_completo, email_claro FROM users WHERE LOWER(email_claro) = LOWER(?) LIMIT 1"
      ).bind(cleanMail).first().catch(() => null);
      if (u) {
        resolvedUserId = u.id;
        resolvedUserName = u.nome_completo;
        resolvedUserEmail = u.email_claro;
      }
    }
  }

  try {
    await env.DB.prepare(`
      INSERT INTO email_logs (
        id, direction, user_id, user_name, user_email,
        from_address, to_address, subject, content_html, content_text,
        status, error_message, resend_id, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    `).bind(
      logId,
      direction,
      resolvedUserId,
      resolvedUserName,
      resolvedUserEmail,
      fromAddress,
      Array.isArray(toAddress) ? toAddress.join(', ') : toAddress,
      subject,
      contentHtml,
      contentText,
      status,
      errorMessage,
      resendId
    ).run();

    return logId;
  } catch (err) {
    console.error('Erro ao gravar email_logs:', err);
    return null;
  }
}

export async function handleEmailRoutes(request, env, url, pathname) {
  // 1. Rota de Rastreamento de Abertura (Tracking Pixel)
  const trackMatch = pathname.match(/^\/api\/emails\/track\/([^\/]+)$/);
  if (trackMatch && request.method === 'GET') {
    const emailId = trackMatch[1];
    await ensureEmailTables(env);

    try {
      const ip = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '127.0.0.1';
      const userAgent = request.headers.get('user-agent') || 'Desconhecido';

      await env.DB.prepare(`
        UPDATE email_logs
        SET 
          status = CASE WHEN status IN ('sent', 'simulated') THEN 'opened' ELSE status END,
          opened_at = COALESCE(opened_at, CURRENT_TIMESTAMP),
          open_count = COALESCE(open_count, 0) + 1,
          ip_open = ?,
          user_agent_open = ?
        WHERE id = ?
      `).bind(ip, userAgent, emailId).run().catch(() => {});
    } catch (_) {}

    return new Response(PIXEL_GIF, {
      status: 200,
      headers: {
        'Content-Type': 'image/gif',
        'Content-Length': String(PIXEL_GIF.length),
        'Cache-Control': 'no-store, no-cache, must-revalidate, private, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
  }

  // 2. Webhook do Resend (Eventos assíncronos: email.opened, email.delivered, email.bounced)
  if (pathname === '/api/emails/webhook' && request.method === 'POST') {
    await ensureEmailTables(env);
    try {
      const payload = await request.json().catch(() => ({}));
      const { type, data } = payload;
      const resendId = data?.email_id || data?.id;

      if (resendId) {
        if (type === 'email.opened') {
          await env.DB.prepare(`
            UPDATE email_logs
            SET 
              status = 'opened',
              opened_at = COALESCE(opened_at, CURRENT_TIMESTAMP),
              open_count = COALESCE(open_count, 0) + 1
            WHERE resend_id = ? OR id = ?
          `).bind(resendId, resendId).run().catch(() => {});
        } else if (type === 'email.bounced' || type === 'email.complained') {
          await env.DB.prepare(`
            UPDATE email_logs
            SET 
              status = 'failed',
              error_message = ?
            WHERE resend_id = ? OR id = ?
          `).bind(`Evento Resend: ${type}`, resendId, resendId).run().catch(() => {});
        } else if (type === 'email.delivered') {
          await env.DB.prepare(`
            UPDATE email_logs
            SET status = CASE WHEN status = 'opened' THEN 'opened' ELSE 'delivered' END
            WHERE resend_id = ? OR id = ?
          `).bind(resendId, resendId).run().catch(() => {});
        }
      }

      return json({ success: true, processed: true });
    } catch (err) {
      console.error('Erro no webhook de emails:', err);
      return json({ error: 'Falha ao processar webhook.' }, 500);
    }
  }

  // 3. Endpoint Inbound (Recebimento de e-mails para auditoria / registro)
  if (pathname === '/api/emails/inbound' && request.method === 'POST') {
    await ensureEmailTables(env);
    try {
      const body = await request.json().catch(() => ({}));
      const { from, to, subject, html, text } = body;

      if (!from || !subject) {
        return json({ error: 'Remetente (from) e Assunto (subject) são obrigatórios.' }, 400);
      }

      const logId = await recordEmailLog(env, {
        direction: 'inbound',
        fromAddress: from,
        toAddress: to || 'notificacoes@pephub.cloud',
        subject,
        contentHtml: html || null,
        contentText: text || html || '',
        status: 'received'
      });

      return json({ success: true, id: logId, message: 'E-mail recebido e registrado com sucesso.' }, 201);
    } catch (err) {
      console.error('Erro ao receber email inbound:', err);
      return json({ error: 'Falha ao registrar e-mail recebido.' }, 500);
    }
  }

  // =========================================================================
  // ROTAS ADMINISTRATIVAS (/api/admin/emails/*)
  // =========================================================================
  if (!pathname.startsWith('/api/admin/emails')) {
    return null;
  }

  const user = await getSessionUser(request, env);
  if (!user || user.status !== 'aprovado' || !Boolean(user.is_admin)) {
    return json({ error: 'Acesso restrito ao administrador corporativo.' }, 403);
  }

  await ensureEmailTables(env);
  const method = request.method.toUpperCase();

  // GET /api/admin/emails — Lista de e-mails com filtros e métricas analíticas
  if (pathname === '/api/admin/emails' && method === 'GET') {
    try {
      const userIdFilter = url.searchParams.get('user_id');
      const directionFilter = url.searchParams.get('direction'); // 'all', 'outbound', 'inbound'
      const statusFilter = url.searchParams.get('status');       // 'all', 'sent', 'opened', 'failed', 'simulated'
      const search = url.searchParams.get('search');
      const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') || '50', 10), 1), 200);
      const offset = Math.max(parseInt(url.searchParams.get('offset') || '0', 10), 0);

      let whereConditions = [];
      let params = [];

      if (userIdFilter && userIdFilter !== 'all') {
        whereConditions.push('(user_id = ? OR to_address LIKE ? OR from_address LIKE ?)');
        params.push(userIdFilter, `%${userIdFilter}%`, `%${userIdFilter}%`);
      }

      if (directionFilter && directionFilter !== 'all') {
        whereConditions.push('direction = ?');
        params.push(directionFilter);
      }

      if (statusFilter && statusFilter !== 'all') {
        whereConditions.push('status = ?');
        params.push(statusFilter);
      }

      if (search && search.trim()) {
        whereConditions.push('(subject LIKE ? OR to_address LIKE ? OR from_address LIKE ? OR user_name LIKE ?)');
        const s = `%${search.trim()}%`;
        params.push(s, s, s, s);
      }

      const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';

      // Consulta de E-mails (sem carregar corpo HTML pesado na lista inicial para alta performance)
      const listQuery = `
        SELECT 
          id, direction, user_id, user_name, user_email,
          from_address, to_address, subject,
          status, error_message, opened_at, open_count,
          resend_id, created_at,
          LENGTH(COALESCE(content_html, '')) as html_size
        FROM email_logs
        ${whereClause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
      `;

      const listParams = [...params, limit, offset];
      const { results } = await env.DB.prepare(listQuery).bind(...listParams).all();

      // Estatísticas Consolidadas (KPIs executivos)
      const statsQuery = `
        SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN direction = 'outbound' THEN 1 ELSE 0 END) as total_outbound,
          SUM(CASE WHEN direction = 'inbound' THEN 1 ELSE 0 END) as total_inbound,
          SUM(CASE WHEN status = 'opened' THEN 1 ELSE 0 END) as total_opened,
          SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as total_failed,
          SUM(CASE WHEN status = 'simulated' THEN 1 ELSE 0 END) as total_simulated,
          SUM(CASE WHEN status = 'suspended' THEN 1 ELSE 0 END) as total_suspended
        FROM email_logs
      `;
      const stats = await env.DB.prepare(statsQuery).first();

      const totalOutbound = stats?.total_outbound || 0;
      const totalOpened = stats?.total_opened || 0;
      const openRate = totalOutbound > 0 ? Math.round((totalOpened / totalOutbound) * 1000) / 10 : 0;

      // Lista de usuários para o dropdown de filtro no frontend
      const usersList = await env.DB.prepare(`
        SELECT id, nome_completo, email_claro, login_claro, area
        FROM users
        ORDER BY nome_completo ASC
      `).all().catch(() => ({ results: [] }));

      return json({
        success: true,
        emails: results || [],
        stats: {
          total: stats?.total || 0,
          total_outbound: totalOutbound,
          total_inbound: stats?.total_inbound || 0,
          total_opened: totalOpened,
          open_rate_pct: openRate,
          total_failed: stats?.total_failed || 0,
          total_simulated: stats?.total_simulated || 0,
          total_suspended: stats?.total_suspended || 0
        },
        users: usersList.results || [],
        pagination: { limit, offset }
      });
    } catch (err) {
      console.error('Erro ao listar e-mails admin:', err);
      return json({ error: 'Falha ao buscar registros de e-mail.' }, 500);
    }
  }

  // GET /api/admin/emails/:id — Detalhes completos do e-mail incluindo corpo HTML
  const singleMatch = pathname.match(/^\/api\/admin\/emails\/([^\/]+)$/);
  if (singleMatch && method === 'GET') {
    const emailId = singleMatch[1];
    try {
      const email = await env.DB.prepare('SELECT * FROM email_logs WHERE id = ?').bind(emailId).first();
      if (!email) {
        return json({ error: 'E-mail não localizado.' }, 404);
      }
      return json({ success: true, email });
    } catch (err) {
      console.error('Erro ao buscar e-mail:', err);
      return json({ error: 'Falha ao recuperar detalhes do e-mail.' }, 500);
    }
  }

  // POST /api/admin/emails/resend/:id — Reenvio de e-mail com falha
  const resendMatch = pathname.match(/^\/api\/admin\/emails\/resend\/([^\/]+)$/);
  if (resendMatch && method === 'POST') {
    const emailId = resendMatch[1];
    try {
      const original = await env.DB.prepare('SELECT * FROM email_logs WHERE id = ?').bind(emailId).first();
      if (!original) {
        return json({ error: 'Registro de e-mail não localizado para reenvio.' }, 404);
      }

      const sendResult = await sendEmail(env, {
        to: original.to_address,
        subject: original.subject,
        html: original.content_html,
        text: original.content_text,
        userId: original.user_id,
        userName: original.user_name
      });

      return json({
        success: sendResult.success,
        message: sendResult.success ? 'E-mail reenviado com sucesso.' : 'Falha ao reenviar e-mail.',
        details: sendResult
      });
    } catch (err) {
      console.error('Erro ao reenviar e-mail:', err);
      return json({ error: 'Falha interna ao tentar reenviar e-mail.' }, 500);
    }
  }

  // POST /api/admin/emails/test-send — Disparo de e-mail de teste para validação
  if (pathname === '/api/admin/emails/test-send' && method === 'POST') {
    try {
      const body = await request.json().catch(() => ({}));
      const { target_user_id, target_email, subject, message } = body;

      let destEmail = target_email;
      let destName = 'Colaborador';
      let destUserId = target_user_id;

      if (target_user_id) {
        const u = await env.DB.prepare('SELECT id, nome_completo, email_claro FROM users WHERE id = ?')
          .bind(target_user_id).first().catch(() => null);
        if (u) {
          destEmail = u.email_claro;
          destName = u.nome_completo;
          destUserId = u.id;
        }
      }

      if (!destEmail || !destEmail.includes('@')) {
        return json({ error: 'E-mail destinatário inválido ou não informado.' }, 400);
      }

      const emailSubject = subject?.trim() || '[PEP HUB] Comunicado / Teste de Notificação';
      const emailContent = message?.trim() || 'Este é um e-mail de verificação oficial da plataforma PEP HUB Regional Norte.';

      const htmlBody = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; margin: 0; padding: 20px; color: #1c2430; }
            .container { max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 6px; overflow: hidden; border: 1px solid #dfe3e8; box-shadow: 0 4px 14px rgba(0,0,0,0.06); }
            .header-bar { height: 4px; background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%); }
            .header { background: #1c2430; padding: 20px 24px; color: #ffffff; display: flex; align-items: center; justify-content: space-between; }
            .header h1 { margin: 0; font-size: 18px; font-weight: 700; }
            .header span { font-size: 12px; color: #f9b233; font-weight: 600; }
            .body { padding: 28px 24px; line-height: 1.5; font-size: 14px; }
            .greeting { font-size: 15px; font-weight: 700; margin-bottom: 14px; color: #1c2430; }
            .message-box { background: #f8f9fa; border-left: 4px solid #c0191f; padding: 14px 16px; border-radius: 0 4px 4px 0; margin: 18px 0; color: #334155; }
            .btn { display: inline-block; background: #1c2430; color: #ffffff !important; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-weight: 700; font-size: 13px; margin-top: 14px; }
            .footer { padding: 18px 24px; background: #fafbfc; border-top: 1px solid #eceef1; font-size: 11px; color: #7b8794; text-align: center; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header-bar"></div>
            <div class="header">
              <h1>PEP HUB — Regional Norte</h1>
              <span>Comunicação Oficial</span>
            </div>
            <div class="body">
              <div class="greeting">Olá, ${destName}!</div>
              <p>Você recebeu uma comunicação direta da coordenação do PEP HUB Regional Norte.</p>
              <div class="message-box">${emailContent.replace(/\n/g, '<br>')}</div>
              <p>Caso tenha dúvidas, consulte os painéis oficiais ou entre em contato com a equipe de governança.</p>
              <a href="https://pephub.cloud/" class="btn">Acessar Portal PEP HUB &rarr;</a>
            </div>
            <div class="footer">
              Regional Norte: AM · PA · MA · AP · RR | Esta mensagem é corporativa e confidencial.
            </div>
          </div>
        </body>
        </html>
      `;

      const sendResult = await sendEmail(env, {
        to: destEmail,
        subject: emailSubject,
        html: htmlBody,
        text: `${emailSubject}\n\nOlá, ${destName}!\n\n${emailContent}\n\nAcesse: https://pephub.cloud/`,
        userId: destUserId,
        userName: destName
      });

      return json({
        success: sendResult.success,
        message: sendResult.success ? `E-mail enviado com sucesso para ${destEmail}.` : `Falha no envio: ${sendResult.error || 'Erro desconhecido'}`,
        details: sendResult
      });
    } catch (err) {
      console.error('Erro ao disparar e-mail de teste:', err);
      return json({ error: 'Falha ao processar disparo de teste.' }, 500);
    }
  }

  // POST /api/admin/emails/simulate-inbound — Simula recebimento de mensagem/e-mail para testes
  if (pathname === '/api/admin/emails/simulate-inbound' && method === 'POST') {
    try {
      const body = await request.json().catch(() => ({}));
      const { user_id, subject, message } = body;

      let fromEmail = 'usuario.teste@claro.com.br';
      let fromName = 'Colaborador Teste';

      if (user_id) {
        const u = await env.DB.prepare('SELECT nome_completo, email_claro FROM users WHERE id = ?').bind(user_id).first().catch(() => null);
        if (u) {
          fromEmail = u.email_claro;
          fromName = u.nome_completo;
        }
      }

      const logId = await recordEmailLog(env, {
        direction: 'inbound',
        userId: user_id || null,
        userName: fromName,
        userEmail: fromEmail,
        fromAddress: fromEmail,
        toAddress: 'notificacoes@pephub.cloud',
        subject: subject || 'Dúvida sobre indicador de Churn Safra',
        contentHtml: `<p>${message || 'Solicito esclarecimento referente à safra fechada do último mês.'}</p>`,
        contentText: message || 'Solicito esclarecimento referente à safra fechada do último mês.',
        status: 'received'
      });

      return json({ success: true, id: logId, message: 'E-mail recebido simulado com sucesso.' }, 201);
    } catch (err) {
      console.error('Erro ao simular inbound:', err);
      return json({ error: 'Falha ao simular recebimento.' }, 500);
    }
  }

  return null;
}
