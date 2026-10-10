/**
 * Sub-roteador de Autenticação, Cadastro e Aprovação de Usuários
 * Rotas: /api/auth/* e /api/approve, /api/reject, /api/bot/context
 */

import {
  SECURITY_HEADERS,
  json,
  randomHex,
  parseCookies,
  hashPassword,
  verifyPassword,
  checkLoginRateLimit,
  recordLoginFailure,
  clearLoginAttempts,
  getSessionUser,
  createSession,
  deleteSession,
  logAccess,
  sendEmail,
  checkUserProfileRequirements,
  getSystemControl,
  ALL_DEFAULT_MODULES_STR,
} from '../utils/security.js';

export async function handleAuthRoutes(request, env, url, pathname, ip) {
  const baseUrl = env.PUBLIC_BASE_URL || `${url.protocol}//${url.host}`;
  const adminEmail = env.ADMIN_EMAIL || 'arthur.rezende.analista@gmail.com';

    // POST /api/auth/register (Solicitação de Cadastro)
    if (pathname === '/api/auth/register' && request.method === 'POST') {
      try {
        const body = await request.json();
        const { nome_completo, login_claro, email_claro, telefone, area, funcao, password } = body;

        if (!nome_completo || !login_claro || !email_claro || !telefone || !area || !funcao || !password) {
          return json({ error: 'Todos os campos, incluindo WhatsApp Corporativo, são de preenchimento obrigatório.' }, 400);
        }

        if (password.length < 6) {
          return json({ error: 'A senha deve conter no mínimo 6 dígitos.' }, 400);
        }

        // Padronização corporativa: Todas as palavras em MAIÚSCULO, exceto e-mail (minúsculo) e senha (livre)
        const cleanNome = (nome_completo || '').trim().toUpperCase();
        const cleanLogin = (login_claro || '').trim().toUpperCase();
        const cleanArea = (area || '').trim().toUpperCase();
        const cleanFuncao = (funcao || '').trim().toUpperCase();
        const cleanEmail = (email_claro || '').trim().toLowerCase();
        let rawPhone = (telefone || '').replace(/\D/g, '');
        if (rawPhone.length === 10 || rawPhone.length === 11) {
          rawPhone = '55' + rawPhone;
        }

        // Garante existência da coluna telefone na tabela users
        try {
          await env.DB.prepare('ALTER TABLE users ADD COLUMN telefone TEXT').run();
        } catch (_) {}

        // Verifica duplicidade
        const existing = await env.DB.prepare('SELECT id, status FROM users WHERE lower(email_claro) = ? OR lower(login_claro) = ?').bind(cleanEmail, cleanLogin.toLowerCase()).first();
        if (existing) {
          if (existing.status === 'pendente') {
            return json({ error: 'Já existe uma solicitação de cadastro pendente com este e-mail ou login corporativo.' }, 400);
          }
          return json({ error: 'Este e-mail ou login já possui cadastro na plataforma.' }, 400);
        }

        const { salt, hash } = await hashPassword(password);
        const userId = crypto.randomUUID();
        const approvalToken = randomHex(32);
        const isAdmin = (cleanEmail === adminEmail || cleanLogin.toLowerCase() === 'admin') ? 1 : 0;
        const initialStatus = isAdmin ? 'aprovado' : 'pendente';

        await env.DB.prepare(`
          INSERT INTO users (id, nome_completo, login_claro, email_claro, telefone, area, funcao, password_hash, salt, status, approval_token, is_admin, notify_updates, modules_allowed, created_at, approved_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, datetime('now'), CASE WHEN ? = 1 THEN datetime('now') ELSE NULL END)
        `).bind(userId, cleanNome, cleanLogin, cleanEmail, rawPhone, cleanArea, cleanFuncao, hash, salt, initialStatus, approvalToken, isAdmin, ALL_DEFAULT_MODULES_STR, isAdmin).run();

        // Se for colaborador pendente, dispara e-mail formal para o responsável pela ferramenta
        if (!isAdmin) {
          const approveUrl = `${baseUrl}/api/approve?id=${userId}&token=${approvalToken}`;
          const rejectUrl = `${baseUrl}/api/reject?id=${userId}&token=${approvalToken}`;

          const emailHtml = `
            <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
              <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
                <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Solicitação de Acesso Corporativo</h2>
              </div>
              <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
                <p style="margin-top:0">Prezado Arthur (Responsável pela Ferramenta),</p>
                <p>Foi registrada uma nova solicitação de acesso para a plataforma de inteligência regional. Detalhes cadastrados:</p>
                
                <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:12.5px">
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675;width:140px"><strong>Nome Completo:</strong></td><td style="padding:7px 0"><strong>${nome_completo}</strong></td></tr>
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675"><strong>Login Claro:</strong></td><td style="padding:7px 0"><code>${cleanLogin}</code></td></tr>
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675"><strong>E-mail Claro:</strong></td><td style="padding:7px 0">${cleanEmail}</td></tr>
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675"><strong>WhatsApp Corp:</strong></td><td style="padding:7px 0"><strong>${rawPhone}</strong></td></tr>
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675"><strong>Área:</strong></td><td style="padding:7px 0">${area}</td></tr>
                  <tr style="border-bottom:1px solid #eceef1"><td style="padding:7px 0;color:#5b6675"><strong>Função:</strong></td><td style="padding:7px 0">${funcao}</td></tr>
                  <tr><td style="padding:7px 0;color:#5b6675"><strong>Data e Hora:</strong></td><td style="padding:7px 0">${new Date().toLocaleString('pt-BR')}</td></tr>
                </table>

                <div style="margin:26px 0 16px;text-align:center">
                  <a href="${approveUrl}" style="background:#2f7d5d;color:#ffffff;padding:11px 22px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block;margin-right:10px">
                    Aprovar Solicitação
                  </a>
                  <a href="${rejectUrl}" style="background:#fff;color:#c0392b;border:1px solid #e0a39c;padding:10px 18px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                    Rejeitar Solicitação
                  </a>
                </div>

                <p style="font-size:11.5px;color:#8b95a3;margin-top:22px;border-top:1px solid #eceef1;padding-top:12px">
                  Esta deliberação também pode ser realizada diretamente pelo <a href="${baseUrl}/admin/" style="color:#2a5d8f;font-weight:600">Painel Administrativo</a>.
                </p>
              </div>
            </div>
          `;

          await sendEmail(env, {
            to: adminEmail,
            subject: `[Solicitação de Acesso] ${nome_completo} (${area} / ${funcao})`,
            html: emailHtml,
            text: `Nova solicitação de acesso:\nNome: ${nome_completo}\nLogin Claro: ${cleanLogin}\nE-mail: ${cleanEmail}\nWhatsApp: ${rawPhone}\nÁrea: ${area}\nFunção: ${funcao}\n\nAprovar: ${approveUrl}\nRejeitar: ${rejectUrl}`,
          });
        }

        return json({ success: true, status: initialStatus });
      } catch (err) {
        console.error('Erro register:', err);
        return json({ error: 'Erro interno ao processar cadastro: ' + err.message }, 500);
      }
    }

    // GET /api/auth/authorized-phones (Lista de telefones autorizados para integração com WhatsApp Bot)
    if (pathname === '/api/auth/authorized-phones' && request.method === 'GET') {
      try {
        if (await getSystemControl(env, 'suspend_whatsapp_bot')) {
          return json({ count: 0, phones: [], bot_suspended: true, message: 'Integração com WhatsApp Bot temporariamente suspensa pelo Administrador.' });
        }
        const rows = await env.DB.prepare("SELECT telefone, profile_metadata, nome_completo, login_claro FROM users WHERE status = 'aprovado'").all();
        const phones = [];
        for (const r of (rows.results || [])) {
          let tel = r.telefone;
          if (!tel && r.profile_metadata) {
            try {
              const meta = JSON.parse(r.profile_metadata);
              tel = meta.telefone || meta.whatsapp || meta.phone || null;
            } catch (_) {}
          }
          if (tel && String(tel).trim()) {
            phones.push({
              telefone: String(tel).replace(/\D/g, ''),
              nome: r.nome_completo,
              login: r.login_claro
            });
          }
        }
        return json({ count: phones.length, phones, bot_suspended: false });
      } catch (err) {
        return json({ error: err.message }, 500);
      }
    }

    // GET /api/bot/context (Contexto consolidado de KPIs para o assistente WhatsApp RAG)
    if (pathname === '/api/bot/context' && request.method === 'GET') {
      try {
        const botContext = {
          timestamp: new Date().toISOString(),
          regional: 'Regional Norte (Claro Brasil)',
          churn: {
            safra_fechada_foco: 'mai/26',
            volume_desconexoes: '348.866 contratos apurados na série histórica',
            taxa_churn_safra: '12,4% (Média Regional)',
            janela_maturacao: '110 a 120 dias',
            principais_ofensores: ['Involuntário (Fadiga Financeira)', 'Competição Fibra Local']
          },
          fpd: {
            safra_foco: 'mai/26',
            instalacoes_totais: 53972,
            taxa_fpd60_oficial: '25,90%',
            taxa_fpd30_prorata: '58,25%',
            taxa_cura_30d: '55,50%',
            taxa_100_em_dia: '41,74%',
            nunca_pagou_volume: 13979,
            faixas_risco: {
              baixo_baixissimo: '6,4% - 8,9% FPD 60',
              medio: '17,0% FPD 60',
              alto: '30,1% FPD 60',
              altissimo: '42,2% - 48,1% FPD 60'
            }
          },
          bl_total: {
            segmento: 'Banda Larga Residencial',
            total_adicoes: 44794,
            taxa_fpd60: '23,61%'
          },
          bl_pme: {
            segmento: 'PME (Pequenas e Médias Empresas)',
            total_adicoes: 4346,
            taxa_fpd60: '27,01%'
          }
        };
        return json(botContext);
      } catch (err) {
        return json({ error: err.message }, 500);
      }
    }


    // POST /api/auth/login (Suporta e-mail corporativo OU login de rede como 'admin')
    if (pathname === '/api/auth/login' && request.method === 'POST') {
      try {
        const body = await request.json();
        const { email_claro, password } = body;

        if (!email_claro || !password) {
          return json({ error: 'Informe o usuário/e-mail e a respectiva senha.' }, 400);
        }

        const identifier = email_claro.trim().toLowerCase();
        const clientIp = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '127.0.0.1';

        // Verificação de Rate Limiting / Brute-force lockout
        const rateCheck = await checkLoginRateLimit(env, clientIp, identifier);
        if (!rateCheck.allowed) {
          return json({ error: rateCheck.error }, 429);
        }

        const user = await env.DB.prepare(`
          SELECT * FROM users 
          WHERE lower(email_claro) = ? OR lower(login_claro) = ?
        `).bind(identifier, identifier).first();

        if (!user) {
          await recordLoginFailure(env, clientIp, identifier);
          return json({ error: 'Usuário não cadastrado. Verifique a digitação ou solicite seu cadastro.' }, 401);
        }

        // Validação de senha por PBKDF2
        const valid = await verifyPassword(password, user.salt, user.password_hash);
        if (!valid) {
          await recordLoginFailure(env, clientIp, identifier);
          return json({ error: 'Credenciais inválidas. Verifique seu login e senha.' }, 401);
        }

        // Sucesso na senha: limpa contador de falhas
        await clearLoginAttempts(env, clientIp, identifier);

        // Bloqueio
        if (user.status === 'bloqueado' || user.status === 'rejeitado') {
          return json({ error: 'Acesso corporativo suspenso ou não autorizado pelo responsável pela ferramenta.', status: user.status }, 403);

        }

        // Pendente
        if (user.status === 'pendente') {
          return json({ error: 'Seu cadastro está pendente de aprovação.', status: 'pendente' }, 403);
        }

        // Registra log de acesso do login
        await logAccess(env, request, user, 'LOGIN');

        // Cria sessão
        const cookie = await createSession(user.id, env);

        // Verifica conformidade de campos obrigatórios de cadastro
        const profileReqs = await checkUserProfileRequirements(env, user);
        let parsedMeta = {};
        if (user.profile_metadata) {
          try { parsedMeta = JSON.parse(user.profile_metadata); } catch(e) { parsedMeta = {}; }
        }

        return json({
          success: true,
          must_change_password: Boolean(user.must_change_password),
          needs_profile_completion: profileReqs.needs_completion,
          missing_profile_fields: profileReqs.missing_fields,
          user: {
            id: user.id,
            nome_completo: user.nome_completo,
            login_claro: user.login_claro,
            email_claro: user.email_claro,
            telefone: user.telefone || '',
            area: user.area,
            funcao: user.funcao,
            is_admin: Boolean(user.is_admin),
            modules_allowed: user.modules_allowed !== null && user.modules_allowed !== undefined ? user.modules_allowed : ALL_DEFAULT_MODULES_STR,
            profile_metadata: parsedMeta
          }
        }, 200, {
          'Set-Cookie': cookie,
        });
      } catch (err) {
        console.error('Erro login:', err);
        return json({ error: 'Erro no servidor durante a autenticação.' }, 500);
      }
    }

    // POST /api/auth/change-password (Troca obrigatória de senha temporária ou voluntária)
    if (pathname === '/api/auth/change-password' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) {
        return json({ error: 'Sessão expirada. Efetue login novamente.' }, 401);
      }

      const { new_password } = await request.json();
      if (!new_password || new_password.length < 6) {
        return json({ error: 'A nova senha deve conter no mínimo 6 dígitos.' }, 400);
      }

      const { salt, hash } = await hashPassword(new_password);
      await env.DB.prepare(`
        UPDATE users 
        SET password_hash = ?, salt = ?, must_change_password = 0 
        WHERE id = ?
      `).bind(hash, salt, user.id).run();

      await logAccess(env, request, user, 'PASSWORD_CHANGE');
      return json({ success: true, message: 'Senha atualizada com sucesso.' });
    }

    // POST /api/auth/complete-profile (Preenchimento obrigatório de campos corporativos adicionados após o cadastro)
    if (pathname === '/api/auth/complete-profile' && request.method === 'POST') {
      const user = await getSessionUser(request, env);
      if (!user) {
        return json({ error: 'Sessão expirada. Efetue login novamente.' }, 401);
      }

      const body = await request.json();
      const requiredRows = await env.DB.prepare("SELECT key, label, validation_regex FROM required_profile_fields WHERE is_required = 1").all();
      const fields = requiredRows.results || [];

      let metadata = {};
      if (user.profile_metadata) {
        try { metadata = JSON.parse(user.profile_metadata); } catch(e) { metadata = {}; }
      }

      let updatedTelefone = user.telefone;
      for (const f of fields) {
        const submittedVal = body[f.key] !== undefined ? String(body[f.key]).trim() : '';
        if (!submittedVal) {
          return json({ error: `O campo '${f.label}' é de preenchimento obrigatório para continuar.` }, 400);
        }
        if (f.validation_regex) {
          const rx = new RegExp(f.validation_regex);
          const cleanTest = f.key === 'telefone' ? submittedVal.replace(/\D/g, '') : submittedVal;
          if (!rx.test(cleanTest)) {
            return json({ error: `Valor inválido para o campo '${f.label}'.` }, 400);
          }
        }
        if (f.key === 'telefone') {
          updatedTelefone = submittedVal.replace(/\D/g, '');
        } else {
          metadata[f.key] = submittedVal;
        }
      }

      for (const [k, v] of Object.entries(body)) {
        if (!['telefone', 'password', 'is_admin', 'status', 'modules_allowed', 'id'].includes(k)) {
          metadata[k] = typeof v === 'string' ? v.trim() : v;
        }
      }

      await env.DB.prepare(`
        UPDATE users 
        SET telefone = ?, profile_metadata = ?
        WHERE id = ?
      `).bind(updatedTelefone, JSON.stringify(metadata), user.id).run();

      await logAccess(env, request, user, 'PROFILE_COMPLETED');
      return json({ success: true, message: 'Dados cadastrais atualizados com sucesso.' });
    }

    // POST ou GET /api/auth/logout e /logout (Encerramento de sessão infalível)
    if ((pathname === '/api/auth/logout' || pathname === '/logout') && (request.method === 'POST' || request.method === 'GET')) {
      const cookies = parseCookies(request);
      const sessionToken = cookies['pephub_session'];
      const clearCookie = await deleteSession(sessionToken, env);
      
      const isHtmlNav = pathname === '/logout' || (request.headers.get('accept') || '').includes('text/html');
      if (isHtmlNav) {
        return new Response(null, {
          status: 302,
          headers: {
            'Location': `${url.origin}/login/`,
            'Set-Cookie': clearCookie,
            'Cache-Control': 'no-cache, no-store, must-revalidate'
          }
        });
      }

      return json({ success: true, redirect: '/login/' }, 200, {
        'Set-Cookie': clearCookie,
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      });
    }

    // GET /api/auth/me
    if (pathname === '/api/auth/me') {
      const user = await getSessionUser(request, env);
      if (!user) {
        return json({ authenticated: false }, 401);
      }

      const profileReqs = await checkUserProfileRequirements(env, user);
      let parsedMeta = {};
      if (user.profile_metadata) {
        try { parsedMeta = JSON.parse(user.profile_metadata); } catch(e) { parsedMeta = {}; }
      }

      return json({
        authenticated: true,
        id: user.id,
        status: user.status || 'aprovado',
        nome_completo: user.nome_completo,
        login_claro: user.login_claro,
        email_claro: user.email_claro,
        telefone: user.telefone || '',
        area: user.area,
        funcao: user.funcao,
        is_admin: Boolean(user.is_admin),
        must_change_password: Boolean(user.must_change_password),
        modules_allowed: user.modules_allowed !== null && user.modules_allowed !== undefined ? user.modules_allowed : ALL_DEFAULT_MODULES_STR,
        profile_metadata: parsedMeta,
        needs_profile_completion: profileReqs.needs_completion,
        missing_profile_fields: profileReqs.missing_fields
      });
    }

    // POST /api/telemetry/log (Auditoria de Eventos de Cliente: Exportação CSV, etc.)
    if (pathname === '/api/telemetry/log' && request.method === 'POST') {
      try {
        const user = await getSessionUser(request, env);
        if (!user) return json({ error: 'Não autenticado' }, 401);
        const body = await request.json().catch(() => ({}));
        const recurso = body.recurso || body.action || 'EXPORT_CSV';
        await logAccess(env, request, user, recurso);
        return json({ success: true });
      } catch (err) {
        return json({ error: err.message }, 500);
      }
    }

    // POST /api/auth/forgot-password
    if (pathname === '/api/auth/forgot-password' && request.method === 'POST') {
      try {
        const { email_claro } = await request.json();
        if (!email_claro) return json({ error: 'Informe seu e-mail corporativo.' }, 400);

        const cleanEmail = email_claro.trim().toLowerCase();
        const clientIp = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '127.0.0.1';

        const rateCheck = await checkLoginRateLimit(env, clientIp, 'forgot:' + cleanEmail);
        if (!rateCheck.allowed) {
          return json({ error: rateCheck.error }, 429);
        }

        const user = await env.DB.prepare('SELECT id, nome_completo, email_claro FROM users WHERE lower(email_claro) = ?').bind(cleanEmail).first();

        if (!user) {
          await recordLoginFailure(env, clientIp, 'forgot:' + cleanEmail);
        } else {
          await clearLoginAttempts(env, clientIp, 'forgot:' + cleanEmail);
        }


        if (user) {
          const resetToken = randomHex(32);
          const expiresAt = new Date(Date.now() + 60 * 60 * 1000).toISOString();

          await env.DB.prepare(`
            UPDATE users SET reset_token = ?, reset_expires_at = ? WHERE id = ?
          `).bind(resetToken, expiresAt, user.id).run();

          const resetUrl = `${baseUrl}/reset-password/?token=${resetToken}`;
          const emailHtml = `
            <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
              <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
                <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Redefinição de Senha de Acesso</h2>
              </div>
              <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
                <p style="margin-top:0">Olá, <strong>${user.nome_completo}</strong>,</p>
                <p>Recebemos uma solicitação de redefinição de senha para o seu acesso corporativo na plataforma regional.</p>
                <div style="margin:24px 0;text-align:center">
                  <a href="${resetUrl}" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                    Redefinir Senha
                  </a>
                </div>
                <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
                  Este link é válido por 60 minutos. Se você não solicitou esta redefinição, desconsidere este comunicado.
                </p>
              </div>
            </div>
          `;

          await sendEmail(env, {
            to: cleanEmail,
            subject: '[Pephub Regional] Instruções para Redefinição de Senha',
            html: emailHtml,
            text: `Redefina sua senha em: ${resetUrl}`,
          });
        }

        return json({ success: true, message: 'Se o e-mail estiver cadastrado, as instruções foram enviadas.' });
      } catch (err) {
        console.error('Erro forgot-password:', err);
        return json({ error: 'Erro ao processar solicitação.' }, 500);
      }
    }

    // POST /api/auth/reset-password
    if (pathname === '/api/auth/reset-password' && request.method === 'POST') {
      try {
        const { token, new_password } = await request.json();
        if (!token || !new_password || new_password.length < 6) {
          return json({ error: 'Token ou nova senha inválida (mínimo de 6 dígitos).' }, 400);
        }

        const user = await env.DB.prepare(`
          SELECT id, email_claro FROM users 
          WHERE reset_token = ? AND datetime(reset_expires_at) > datetime('now')
        `).bind(token).first();

        if (!user) {
          return json({ error: 'Token inválido ou expirado. Solicite uma nova redefinição.' }, 400);
        }

        const { salt, hash } = await hashPassword(new_password);
        await env.DB.prepare(`
          UPDATE users 
          SET password_hash = ?, salt = ?, reset_token = NULL, reset_expires_at = NULL, must_change_password = 0
          WHERE id = ?
        `).bind(hash, salt, user.id).run();

        return json({ success: true, message: 'Senha redefinida com sucesso.' });
      } catch (err) {
        console.error('Erro reset-password:', err);
        return json({ error: 'Erro ao redefinir senha.' }, 500);
      }
    }

    // ==========================================
    // APROVAÇÃO RÁPIDA POR TOKEN (/api/approve /api/reject)
    // ==========================================

    if (pathname === '/api/approve' || pathname === '/api/reject') {
      const isApprove = pathname === '/api/approve';
      const id = url.searchParams.get('id');
      const token = url.searchParams.get('token');

      if (!id || !token) {
        return new Response('Parâmetros de validação ausentes.', { status: 400, headers: SECURITY_HEADERS });
      }

      const user = await env.DB.prepare('SELECT * FROM users WHERE id = ? AND approval_token = ?').bind(id, token).first();
      if (!user) {
        return new Response('Solicitação não localizada ou token de validação expirado.', { status: 404, headers: SECURITY_HEADERS });
      }

      const newStatus = isApprove ? 'aprovado' : 'rejeitado';
      await env.DB.prepare(`
        UPDATE users SET status = ?, approved_at = CASE WHEN ? = 1 THEN datetime('now') ELSE NULL END WHERE id = ?
      `).bind(newStatus, isApprove ? 1 : 0, id).run();

      if (isApprove) {
        const welcomeHtml = `
          <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
            <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte</div>
              <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Liberação de Acesso Confirmada</h2>
            </div>
            <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
              <p style="margin-top:0">Prezado(a) <strong>${user.nome_completo}</strong>,</p>
              <p>Informamos que sua solicitação de acesso ao ambiente corporativo de relatórios da Regional Norte foi <strong>aprovada pelo responsável pela ferramenta</strong>.</p>
              
              <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:12px 14px;margin:16px 0;font-size:12.5px">
                <div><strong>Login / E-mail de Acesso:</strong> ${user.email_claro}</div>
                <div style="margin-top:3px"><strong>Área:</strong> ${user.area} | <strong>Função:</strong> ${user.funcao}</div>
                <div style="margin-top:3px"><strong>Senha:</strong> A senha cadastrada previamente</div>
              </div>

              <div style="margin:24px 0;text-align:center">
                <a href="${baseUrl}/login/?msg=approved" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                  Acessar Plataforma Regional
                </a>
              </div>

              <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
                Você receberá comunicados formais quando novos ciclos de apuração e dados de mercado forem consolidados.
              </p>
            </div>
          </div>
        `;

        await sendEmail(env, {
          to: user.email_claro,
          subject: '[Pephub Regional] Liberação de Acesso Confirmada',
          html: welcomeHtml,
          text: `Seu acesso foi liberado. Entre em: ${baseUrl}/login`,
        });
      }

      const responseHtml = `
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head><meta charset="utf-8"><title>Decisão Registrada | Pephub</title>
        <style>body{margin:0;font:13px/1.5 "Segoe UI",Arial;background:#f4f5f7;display:flex;align-items:center;justify-content:center;min-height:100vh}
        .box{background:#fff;border:1px solid #dfe3e8;border-radius:4px;padding:28px 32px;max-width:460px;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,.04)}
        h2{color:#1c2430;margin-top:0;font-size:18px} p{color:#5b6675}
        a{display:inline-block;margin-top:14px;background:#1b2430;color:#fff;padding:9px 18px;text-decoration:none;border-radius:3px;font-weight:600;font-size:12px}
        </style></head>
        <body>
          <div class="box">
            <h2>Status Atualizado: ${newStatus.toUpperCase()}</h2>
            <p>O colaborador <strong>${user.nome_completo}</strong> (${user.email_claro}) está registrado como <strong>${newStatus}</strong>.</p>
            <a href="${baseUrl}/admin/">Acessar Painel Administrativo</a>
          </div>
        </body>
        </html>
      `;

      return new Response(responseHtml, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }


  return null;
}
