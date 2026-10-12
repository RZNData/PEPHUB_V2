/**
 * Cloudflare Worker — Pephub Plataforma Regional
 * Autenticação Corporativa, Gestão de Acessos, D1 Database, Logs de Auditoria, Estatísticas e Proteção de Rotas
 */

// Security Headers corporativos para mitigação de Clickjacking, MIME-Sniffing e proteção XSS
export const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  // CSP: restringe carregamento de scripts/estilos ao próprio domínio e autoriza tiles de mapas e fontes corporativas.
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data: blob: https://*.arcgisonline.com https://services.arcgisonline.com https://server.arcgisonline.com https://*.tile.opentopomap.org https://*.tile.openstreetmap.org https://*.basemaps.cartocdn.com; connect-src 'self' https://nominatim.openstreetmap.org; font-src 'self' data: https://cdnjs.cloudflare.com; frame-ancestors 'none'",
};


// Helper JSON
export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      ...SECURITY_HEADERS,
      ...headers,
    },
  });
}

// Helpers Criptográficos (Web Crypto PBKDF2)
export function bufToHex(buf) {
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export function hexToBuf(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}

export function randomHex(bytesCount = 16) {
  const bytes = new Uint8Array(bytesCount);
  crypto.getRandomValues(bytes);
  return bufToHex(bytes);
}

export function generateTempPassword() {
  const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
  let code = '';
  const bytes = new Uint8Array(6);
  crypto.getRandomValues(bytes);
  for (let i = 0; i < 6; i++) {
    code += chars[bytes[i] % chars.length];
  }
  return `Claro#${code}`;
}

export async function hashPassword(password, saltHex = null, iterations = 30000) {
  const encoder = new TextEncoder();
  const salt = saltHex ? hexToBuf(saltHex) : crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );
  const derivedKey = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: iterations,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'HMAC', hash: 'SHA-256', length: 256 },
    true,
    ['sign']
  );
  const rawKey = await crypto.subtle.exportKey('raw', derivedKey);
  return {
    salt: bufToHex(salt),
    hash: bufToHex(rawKey),
  };
}

export async function verifyPassword(password, saltHex, expectedHashHex) {
  const { hash: hashFast } = await hashPassword(password, saltHex, 30000);
  if (hashFast === expectedHashHex) return true;
  // Fallback transparente para hashes criados anteriormente com 100k iterações
  const { hash: hashLegacy } = await hashPassword(password, saltHex, 100000);
  return hashLegacy === expectedHashHex;
}

// Rate Limiting / Brute-force Protection (CWE-307)
export async function checkLoginRateLimit(env, ip, login) {
  try {
    if (!env.DB) return { allowed: true };
    const record = await env.DB.prepare(
      "SELECT fail_count, locked_until FROM login_attempts WHERE ip = ? AND login = ?"
    ).bind(ip, login).first();

    if (!record) return { allowed: true };

    if (record.locked_until) {
      const lockTime = new Date(record.locked_until).getTime();
      const now = Date.now();
      if (now < lockTime) {
        const remainingMin = Math.ceil((lockTime - now) / 60000);
        return {
          allowed: false,
          error: `Muitas tentativas incorretas. Acesso bloqueado temporariamente por ${remainingMin} minuto(s).`
        };
      }
    }
    return { allowed: true, fail_count: record.fail_count };
  } catch (_) {
    return { allowed: true };
  }
}

export async function recordLoginFailure(env, ip, login) {
  try {
    if (!env.DB) return;
    const record = await env.DB.prepare(
      "SELECT fail_count FROM login_attempts WHERE ip = ? AND login = ?"
    ).bind(ip, login).first();

    const currentFails = (record ? record.fail_count : 0) + 1;
    const maxAttempts = 5;
    const lockoutMinutes = 15;
    let lockedUntil = null;

    if (currentFails >= maxAttempts) {
      lockedUntil = new Date(Date.now() + lockoutMinutes * 60000).toISOString();
    }

    await env.DB.prepare(`
      INSERT INTO login_attempts (ip, login, fail_count, last_attempt, locked_until)
      VALUES (?, ?, ?, datetime('now'), ?)
      ON CONFLICT(ip, login) DO UPDATE SET
        fail_count = ?,
        last_attempt = datetime('now'),
        locked_until = ?
    `).bind(ip, login, currentFails, lockedUntil, currentFails, lockedUntil).run();
  } catch (_) {}
}

export async function clearLoginAttempts(env, ip, login) {
  try {
    if (!env.DB) return;
    await env.DB.prepare("DELETE FROM login_attempts WHERE ip = ? AND login = ?").bind(ip, login).run();
  } catch (_) {}
}


// Cookies & Sessão
export function parseCookies(request) {
  const list = {};
  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) return list;

  cookieHeader.split(';').forEach((cookie) => {
    let [name, ...rest] = cookie.split('=');
    name = name?.trim();
    if (!name) return;
    const value = rest.join('=').trim();
    list[name] = decodeURIComponent(value);
  });
  return list;
}

// In-memory cache de sessões ativas (TTL 30s para eliminar queries redundantes ao D1)
const _sessionUserCache = new Map();

export function invalidateSessionUserCache(token) {
  if (token) _sessionUserCache.delete(token);
  else _sessionUserCache.clear();
}

export async function getSessionUser(request, env) {
  const cookies = parseCookies(request);
  const sessionToken = cookies['pephub_session'];
  if (!sessionToken || !env.DB) return null;

  const now = Date.now();
  const cached = _sessionUserCache.get(sessionToken);
  if (cached && cached.expiresAt > now) {
    return cached.user;
  }

  try {
    const session = await env.DB.prepare(`
      SELECT s.id as session_id, s.token, s.expires_at, u.*
      FROM sessions s
      JOIN users u ON s.user_id = u.id
      WHERE s.token = ? AND datetime(s.expires_at) > datetime('now')
    `).bind(sessionToken).first();

    if (!session) {
      _sessionUserCache.delete(sessionToken);
      return null;
    }

    // Se o usuário foi bloqueado, rejeitado ou não está com status aprovado, invalida imediatamente a sessão no D1
    if (session.status !== 'aprovado') {
      await env.DB.prepare('DELETE FROM sessions WHERE token = ?').bind(sessionToken).run().catch(() => {});
      _sessionUserCache.delete(sessionToken);
      return null;
    }

    // Cacheia sessão válida por 30 segundos
    _sessionUserCache.set(sessionToken, { user: session, expiresAt: now + 30000 });
    return session;
  } catch (err) {
    console.error('Erro getSessionUser:', err);
    return null;
  }
}

export async function createSession(userId, env) {
  const token = randomHex(32);
  // Sessão corporativa com expiração estrita (12 horas = 1 turno de trabalho)
  const SESSION_TTL_HOURS = 12;
  const expiresAt = new Date(Date.now() + SESSION_TTL_HOURS * 3600 * 1000).toISOString();
  const id = crypto.randomUUID();

  await env.DB.prepare(`
    INSERT INTO sessions (id, user_id, token, expires_at, created_at)
    VALUES (?, ?, ?, ?, datetime('now'))
  `).bind(id, userId, token, expiresAt).run();

  // Limpeza proativa de sessões expiradas no D1
  env.DB.prepare("DELETE FROM sessions WHERE datetime(expires_at) <= datetime('now')").run().catch(() => {});

  return `pephub_session=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${SESSION_TTL_HOURS * 3600}`;
}

// ==========================================
// PRESENÇA EM TEMPO REAL (HEARTBEAT)
// "Online" = heartbeat recebido nos últimos 3 minutos (sessão válida sozinha não significa online)
// ==========================================
export const ONLINE_WINDOW_SECONDS = 180;
let _presenceReady = false;

export async function ensureSessionPresenceColumns(env) {
  if (_presenceReady || !env.DB) return;
  const probe = await env.DB.prepare('SELECT last_seen, online_since FROM sessions LIMIT 1').first().catch(() => undefined);
  if (probe === undefined) {
    await env.DB.prepare('ALTER TABLE sessions ADD COLUMN last_seen TEXT').run().catch(() => {});
    await env.DB.prepare('ALTER TABLE sessions ADD COLUMN online_since TEXT').run().catch(() => {});
  }
  _presenceReady = true;
}

export async function touchSessionPresence(env, token) {
  if (!env.DB || !token) return false;
  // Em SQLite todas as expressões do SET usam os valores ANTERIORES da linha:
  // se o último sinal tem mais de 3 min, recomeça a contagem de "online há".
  const sql = `
    UPDATE sessions SET
      online_since = CASE
        WHEN last_seen IS NULL OR online_since IS NULL
          OR (julianday('now') - julianday(last_seen)) * 86400 > ${ONLINE_WINDOW_SECONDS}
        THEN datetime('now') ELSE online_since END,
      last_seen = datetime('now')
    WHERE token = ?
  `;
  try {
    await env.DB.prepare(sql).bind(token).run();
    return true;
  } catch (_) {
    await ensureSessionPresenceColumns(env);
    try {
      await env.DB.prepare(sql).bind(token).run();
      return true;
    } catch (err) {
      console.error('Erro touchSessionPresence:', err);
      return false;
    }
  }
}

// ==========================================
// SOLICITAÇÕES DE ACESSO A RELATÓRIOS
// ==========================================
let _accessReqReady = false;
export async function ensureAccessRequestsTable(env) {
  if (_accessReqReady || !env.DB) return;
  await env.DB.prepare(`
    CREATE TABLE IF NOT EXISTS access_requests (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      user_name TEXT,
      user_email TEXT,
      module_id TEXT NOT NULL,
      module_name TEXT,
      justification TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pendente',
      decision_token TEXT,
      decided_by TEXT,
      decision_note TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      decided_at TEXT
    )
  `).run().catch(() => {});
  await env.DB.prepare('CREATE INDEX IF NOT EXISTS idx_access_requests_user ON access_requests (user_id, status)').run().catch(() => {});
  await env.DB.prepare('CREATE INDEX IF NOT EXISTS idx_access_requests_status ON access_requests (status, created_at DESC)').run().catch(() => {});
  _accessReqReady = true;
}

export async function deleteSession(token, env) {
  if (token) {
    _sessionUserCache.delete(token);
    if (env.DB) {
      await env.DB.prepare('DELETE FROM sessions WHERE token = ?').bind(token).run().catch(() => {});
    }
  }
  return 'pephub_session=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT';
}

// Registro de Acesso e Auditoria
export async function logAccess(env, request, user, recurso) {
  try {
    if (!env.DB || !user) return;
    const ip = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '127.0.0.1';
    const city = request.cf?.city || 'Localidade não identificada';
    const region = request.cf?.regionCode || request.cf?.region || '';
    const country = request.cf?.country || 'BR';
    const localizacao = region ? `${city} - ${region}, ${country}` : `${city}, ${country}`;
    const userAgent = request.headers.get('user-agent') || 'Navegador';

    await env.DB.prepare(`
      INSERT INTO access_logs (id, user_id, login_claro, email_claro, nome_completo, area, funcao, recurso, ip, cidade, estado, pais, localizacao, user_agent, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    `).bind(
      crypto.randomUUID(),
      user.id,
      user.login_claro,
      user.email_claro,
      user.nome_completo,
      user.area || 'OUTROS',
      user.funcao || 'OUTROS',
      recurso,
      ip,
      city,
      region,
      country,
      localizacao,
      userAgent
    ).run();
  } catch (err) {
    console.error('Erro ao registrar access_log:', err);
  }
}

// Módulos oficiais ativos da plataforma Pephub (Regional Norte)
export const ALL_SYSTEM_MODULES = [
  'churn_bl_pme',
  'churn_bl_total',
  'churn_safra',
  'aprovacao_credito',
  'fpd',
  'fpd_residencial',
  'market_share_movel',
  'market_share_residencial',
  'panorama_market_share',
  'divulgacao',
  'tv'
];
export const ALL_DEFAULT_MODULES_STR = ALL_SYSTEM_MODULES.join(',');

export const DEFAULT_SYSTEM_MODULES = [
  ['churn_safra', 'Painel de Churn Safra', 'Safra', 'Painéis & Relatórios Oficiais', 'Acompanhamento de Churn Safra da Regional Norte', '/churn/', 'ativo', 1],
  ['churn_bl_total', 'Painel de Churn Banda Larga Total', 'BL Total', 'Painéis & Relatórios Oficiais', 'Acompanhamento de Churn Horizontal BL Total (Residencial + PME)', '/churn-bl-total/', 'ativo', 2],
  ['churn_bl_pme', 'Painel de Churn Banda Larga PME', 'BL PME', 'Painéis & Relatórios Oficiais', 'Acompanhamento de Churn Horizontal BL PME', '/churn-bl-pme/', 'ativo', 3],
  ['fpd', 'Painel de FPD 60/30 (First Payment Default)', 'FPD Regional', 'Painéis & Relatórios Oficiais', 'Inadimplência de primeira fatura (FPD 30 e FPD 60)', '/fpd/', 'ativo', 4],
  ['fpd_residencial', 'FPD Residencial (Executivo Fixa)', 'FPD Residencial', 'Painéis & Relatórios Oficiais', 'Relatório Executivo Oficial de FPD 60 da Fixa por Canal, Cidade e Parceiro', '/fpd-residencial/', 'ativo', 5],
  ['market_share_movel', 'Market Share Móvel', 'MS Móvel', 'Painéis & Relatórios Oficiais', 'Relatório Executivo Oficial de Market Share Móvel (Anatel · Telefonia Móvel & 5G)', '/market-share-movel/', 'ativo', 6],
  ['market_share_residencial', 'Market Share Residencial', 'MS Residencial', 'Painéis & Relatórios Oficiais', 'Relatório Executivo Oficial de Market Share Residencial (Anatel · Banda Larga)', '/market-share-residencial/', 'ativo', 7],
  ['panorama_market_share', 'Panorama & Market Share', 'Panorama', 'Painéis & Relatórios Oficiais', 'Market share móvel e residencial Anatel e dinâmica concorrencial', '/panorama-market-share/', 'ativo', 8],
  ['aprovacao_credito', 'Painel de Taxa de Aprovação de Crédito', 'Taxa Crédito', 'Painéis & Relatórios Oficiais', 'Taxa de aprovação por canal, parceiro e cidade', '/aprovacao-credito/', 'ativo', 9],
  ['divulgacao', 'Divulgação Corporativa (TVs)', 'TV Divulgação', 'PeP Tools & Operações', 'Propostas de mídia, curadoria e exibição nas TVs da Regional', '/pep-tools/divulgacao/', 'ativo', 10],
  ['tv', 'Player TV (16:9 Fullscreen)', 'Player TV', 'PeP Tools & Operações', 'Acesso direto ao reprodutor widescreen para recepções e salas', '/pep-tools/divulgacao/tv.html', 'ativo', 11]
];

export async function ensureSystemModulesSeeded(env) {
  if (!env || !env.DB) return;
  for (const [mid, mname, mshort, msec, mdesc, mroute, mstat, mord] of DEFAULT_SYSTEM_MODULES) {
    await env.DB.prepare(`
      INSERT OR REPLACE INTO system_modules (id, name, short_name, section, description, route, status, sort_order)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(mid, mname, mshort, msec, mdesc, mroute, mstat, mord).run().catch(() => {});
  }
}

export function normalizeModuleId(id) {
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

// In-memory cache de travas do sistema (TTL 30s)
const _systemControlsCache = new Map();

export function invalidateSystemControlsCache() {
  _systemControlsCache.clear();
}

// Helper: Consultar estado de uma trava global do sistema (com cache in-memory)
export async function getSystemControl(env, key) {
  if (!env.DB) return false;
  const now = Date.now();
  const cached = _systemControlsCache.get(key);
  if (cached && cached.expiresAt > now) {
    return cached.value;
  }
  try {
    const row = await env.DB.prepare('SELECT value FROM system_controls WHERE key = ?').bind(key).first();
    const val = row ? row.value === '1' : false;
    _systemControlsCache.set(key, { value: val, expiresAt: now + 30000 });
    return val;
  } catch (_) {
    return false;
  }
}

// Disparo de E-mails (Resend API com suporte a suspensão administrativa)
export async function sendEmail(env, { to, subject, html, text }) {
  const from = env.MAIL_FROM || 'Pephub Regional <notificacoes@pephub.cloud>';
  const replyTo = env.MAIL_REPLY_TO || 'arthur.rezende.analista@gmail.com';

  // Verifica se o disparo global de e-mails está suspenso temporariamente
  if (await getSystemControl(env, 'suspend_emails')) {
    console.warn(`[EMAIL BLOQUEADO - DISPAROS SUSPENSOS ADMINISTRATIVAMENTE] Para: ${Array.isArray(to) ? to.join(',') : to} | Assunto: ${subject}`);
    if (env.DB) {
      await env.DB.prepare(`
        INSERT INTO audit_logs (id, action, user_email, details, created_at)
        VALUES (?, 'EMAIL_SUSPENDED_BY_ADMIN', ?, ?, datetime('now'))
      `).bind(crypto.randomUUID(), Array.isArray(to) ? to.join(',') : to, JSON.stringify({ subject, suspended: true })).run().catch(() => {});
    }
    return { success: true, suspended: true };
  }

  if (!env.RESEND_API_KEY) {
    console.warn(`[EMAIL SIMULADO] RESEND_API_KEY ausente. Para: ${to} | Assunto: ${subject}`);
    if (env.DB) {
      await env.DB.prepare(`
        INSERT INTO audit_logs (id, action, user_email, details, created_at)
        VALUES (?, 'EMAIL_SIMULATED', ?, ?, datetime('now'))
      `).bind(crypto.randomUUID(), Array.isArray(to) ? to.join(',') : to, JSON.stringify({ subject, simulated: true })).run().catch(() => {});
    }
    return { success: true, simulated: true };
  }

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: Array.isArray(to) ? to : [to],
        reply_to: replyTo,
        subject,
        html,
        text,
      }),
    });

    const data = await res.json();
    return { success: res.ok, data };
  } catch (err) {
    console.error('Erro ao enviar e-mail via Resend:', err);
    return { success: false, error: err.message };
  }
}

// Resposta corporativa para ambiente em manutenção
export function renderMaintenanceResponse(toolName) {
  const toolText = toolName ? `ao módulo "<strong>${toolName}</strong>"` : 'a este relatório / ferramenta';
  const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manutenção Temporária | Pephub Regional Norte</title>
<style>
:root{--bg:#f4f5f7;--ink:#1c2430;--ink2:#5b6675;--line:#dfe3e8;--nav:#1b2430}
body{margin:0;font:13px/1.5 "Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px;box-sizing:border-box}
.box{background:#fff;border:1px solid var(--line);border-radius:3px;padding:32px;max-width:540px;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.05)}
.badge{background:#fdf3e2;color:#8a5d06;border:1px solid #f0dcb4;display:inline-block;padding:4px 10px;border-radius:3px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:14px}
h2{margin:0 0 10px;font-size:19px;font-weight:700;color:var(--ink)}
p{margin:0 0 20px;color:var(--ink2);font-size:13px;line-height:1.6}
.btn{display:inline-block;background:var(--nav);color:#fff;padding:9px 18px;border-radius:3px;text-decoration:none;font-weight:600;font-size:12px;transition:background .15s}
.btn:hover{background:#27323f}
</style>
</head>
<body>
  <div class="box">
    <div class="badge">Suspensão Operacional</div>
    <h2>Ambiente Temporariamente Indisponível</h2>
    <p>O acesso ${toolText} foi temporariamente suspenso pela administração da Regional Norte para rotinas de consolidação ou manutenção preventiva. A liberação ocorrerá em instantes.</p>
    <a href="/" class="btn">Retornar ao Portal Principal</a>
  </div>
</body>
</html>`;
  return new Response(html, { 
    status: 503, 
    headers: { 
      'Content-Type': 'text/html; charset=utf-8',
      ...SECURITY_HEADERS,
    } 
  });
}

// In-memory cache de suspensão de módulos (TTL 30s)
const _moduleSuspensionCache = new Map();

export function invalidateModuleSuspensionCache() {
  _moduleSuspensionCache.clear();
}

// Helper: Verifica se um módulo específico está com status "suspenso" no D1 (com cache in-memory)
export async function isModuleSuspended(env, moduleId) {
  if (!env.DB) return false;
  const now = Date.now();
  const cached = _moduleSuspensionCache.get(moduleId);
  if (cached && cached.expiresAt > now) {
    return cached.value;
  }
  try {
    const row = await env.DB.prepare("SELECT status FROM system_modules WHERE id = ?").bind(moduleId).first();
    const val = Boolean(row && row.status === 'suspenso');
    _moduleSuspensionCache.set(moduleId, { value: val, expiresAt: now + 30000 });
    return val;
  } catch(e) {
    return false;
  }
}

// Helper: Verifica se o usuário possui pendências de preenchimento em campos obrigatórios do perfil
export async function checkUserProfileRequirements(env, user) {
  try {
    const requiredRows = await env.DB.prepare("SELECT key, label, field_type, placeholder, validation_regex, is_required FROM required_profile_fields WHERE is_required = 1").all();
    const fields = requiredRows.results || [];
    if (!fields.length) return { needs_completion: false, missing_fields: [] };

    let metadata = {};
    if (user.profile_metadata) {
      try { metadata = JSON.parse(user.profile_metadata); } catch(e) { metadata = {}; }
    }

    const missing = [];
    for (const f of fields) {
      let val = null;
      if (f.key in user && user[f.key] !== null && user[f.key] !== undefined) {
        val = String(user[f.key]).trim();
      } else if (metadata && f.key in metadata && metadata[f.key] !== null && metadata[f.key] !== undefined) {
        val = String(metadata[f.key]).trim();
      }
      if (!val) {
        missing.push({
          key: f.key,
          label: f.label,
          field_type: f.field_type || 'text',
          placeholder: f.placeholder || '',
          validation_regex: f.validation_regex || ''
        });
      }
    }

    return {
      needs_completion: missing.length > 0,
      missing_fields: missing
    };
  } catch (err) {
    console.error('Erro checkUserProfileRequirements:', err);
    return { needs_completion: false, missing_fields: [] };
  }
}

// ==========================================
// DIVULGAÇÃO CORPORATIVA & TVS REGIONAL (SCHEMA & HELPERS)
// ==========================================
let _appDbInitialized = false;
export async function ensureAppSchema(env, force = false) {
  if (_appDbInitialized && !force) return;
  if (!env.DB) return;
  _appDbInitialized = true;
  try {
    // Verificação ultra-rápida (1 roundtrip): se a tabela de controle já existe, a base já está totalmente migrada
    if (!force) {
      const probe = await env.DB.prepare("SELECT 1 FROM system_controls LIMIT 1").first().catch(() => null);
      if (probe) {
        return; // Schema pronto e validado — 0ms de overhead residual
      }
    }

    // 1. Garante colunas da tabela users se ausentes
    await env.DB.prepare("ALTER TABLE users ADD COLUMN telefone TEXT").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE users ADD COLUMN modules_allowed TEXT DEFAULT 'churn_safra,churn_bl_total,churn_bl_pme,fpd,pep_tools_divulgacao'").run().catch(() => {});
    await env.DB.prepare("ALTER TABLE users ADD COLUMN profile_metadata TEXT").run().catch(() => {});

    // 2. Garante tabela de travas e controles do sistema
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS system_controls (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        label TEXT NOT NULL,
        description TEXT NOT NULL,
        updated_at TEXT,
        updated_by TEXT
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      INSERT OR IGNORE INTO system_controls (key, value, label, description, updated_at) VALUES 
      ('suspend_emails', '0', 'Suspender Disparo de E-mails', 'Pausa temporariamente todos os e-mails automáticos enviados pela plataforma (notificações de cadastro, aprovações e comunicados).', datetime('now')),
      ('suspend_portal_access', '0', 'Impedir Acessos aos Relatórios & Ferramentas (Modo Manutenção)', 'Bloqueia temporariamente o acesso de colaboradores aos painéis e ferramentas com mensagem corporativa de manutenção programada. Administradores continuam com acesso total.', datetime('now')),
      ('suspend_whatsapp_bot', '0', 'Suspender Integração com Bot WhatsApp', 'Pausa o fornecimento de contatos e bloqueia temporariamente as interações automatizadas do bot corporativo de WhatsApp.', datetime('now')),
      ('suspend_tv_submissions', '0', 'Suspender Novas Propostas de Mídia para TVs', 'Pausa temporariamente a submissão de novas imagens e vídeos pelos colaboradores no painel de Divulgação Corporativa, mantendo a grade atual em exibição.', datetime('now'))
    `).run().catch(() => {});

    // 3. Garante tabelas de ferramentas e campos obrigatórios de cadastro
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS system_modules (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        short_name TEXT NOT NULL,
        section TEXT NOT NULL,
        description TEXT,
        route TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ativo',
        sort_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME
      )
    `).run().catch(() => {});

    // Seed canônico unificado dos módulos oficiais da plataforma
    await ensureSystemModulesSeeded(env);

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS required_profile_fields (
        key TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        field_type TEXT NOT NULL DEFAULT 'text',
        placeholder TEXT,
        validation_regex TEXT,
        is_required INTEGER NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    // 3. Garante tabelas da TV Corporativa
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS tv_proposals (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        nome_solicitante TEXT,
        email_claro TEXT,
        area_solicitante TEXT,
        titulo TEXT NOT NULL,
        categoria TEXT NOT NULL,
        tipo_midia TEXT NOT NULL,
        duracao_segundos INTEGER DEFAULT 10,
        data_inicio TEXT NOT NULL,
        data_fim TEXT NOT NULL,
        status TEXT DEFAULT 'pendente',
        aprovador_id TEXT,
        aprovador_nome TEXT,
        aprovador_email TEXT,
        motivo_rejeicao TEXT,
        resolucao TEXT,
        media_type TEXT,
        created_at TEXT NOT NULL,
        approved_at TEXT
      )
    `).run();

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS tv_media_chunks (
        id TEXT PRIMARY KEY,
        proposal_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_data TEXT NOT NULL
      )
    `).run();

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS tv_delegations (
        id TEXT PRIMARY KEY,
        scope_type TEXT NOT NULL,
        scope_value TEXT NOT NULL,
        delegated_user_id TEXT NOT NULL,
        delegated_user_name TEXT NOT NULL,
        delegated_user_email TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    `).run();

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS tv_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
      )
    `).run();

    await env.DB.prepare("INSERT OR IGNORE INTO tv_config (key, value) VALUES ('image_duration', '10')").run();
    await env.DB.prepare("INSERT OR IGNORE INTO tv_config (key, value) VALUES ('max_active_items', '50')").run();
    await env.DB.prepare("INSERT OR IGNORE INTO tv_config (key, value) VALUES ('ticker_text', 'Regional Norte · Claro Brasil')").run();

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS login_attempts (
        ip TEXT NOT NULL,
        login TEXT NOT NULL,
        fail_count INTEGER NOT NULL DEFAULT 1,
        last_attempt TEXT NOT NULL,
        locked_until TEXT,
        PRIMARY KEY (ip, login)
      )
    `).run().catch(() => {});


    // 4. Tabelas do Bot WhatsApp (Agentic RAG & Text-to-SQL)
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS dim_carteirizacao (
        id TEXT PRIMARY KEY,
        telefone TEXT NOT NULL UNIQUE,
        user_id TEXT,
        nome TEXT NOT NULL,
        regional TEXT DEFAULT 'REGIONAL NORTE',
        canal TEXT DEFAULT 'TODOS',
        cidade TEXT DEFAULT 'TODAS',
        permissao_total INTEGER NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS fato_indicadores_mensais (
        id TEXT PRIMARY KEY,
        segmento TEXT NOT NULL,
        mes_referencia TEXT NOT NULL,
        tipo_visao TEXT NOT NULL,
        cidade TEXT NOT NULL,
        uf TEXT NOT NULL,
        vol_real REAL DEFAULT 0,
        vol_orc REAL DEFAULT 0,
        rxo_delta REAL DEFAULT 0,
        rxo_pct REAL DEFAULT 0,
        mom_delta REAL DEFAULT 0,
        mom_pct REAL DEFAULT 0,
        yoy_delta REAL DEFAULT 0,
        yoy_pct REAL DEFAULT 0,
        base_real REAL DEFAULT 0,
        base_orc REAL DEFAULT 0,
        taxa_real REAL DEFAULT 0,
        taxa_orc REAL DEFAULT 0,
        taxa_delta_pp REAL DEFAULT 0,
        tendencia_t1 REAL DEFAULT 0,
        tendencia_t2 REAL DEFAULT 0,
        tendencia_t3 REAL DEFAULT 0,
        tendencia_t4 REAL DEFAULT 0,
        ytd_real REAL DEFAULT 0,
        ytd_orc REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS fato_churn_safra (
        id TEXT PRIMARY KEY,
        safra TEXT NOT NULL,
        safra_ord TEXT,
        visao TEXT NOT NULL,
        entidade_nome TEXT NOT NULL,
        cidade TEXT,
        uf TEXT,
        instalacoes INTEGER DEFAULT 0,
        churn_d30 INTEGER DEFAULT 0,
        churn_d60 INTEGER DEFAULT 0,
        churn_d90 INTEGER DEFAULT 0,
        churn_d120 INTEGER DEFAULT 0,
        np120 INTEGER DEFAULT 0,
        taxa_d30 REAL DEFAULT 0,
        taxa_d60 REAL DEFAULT 0,
        taxa_d90 REAL DEFAULT 0,
        taxa_d120 REAL DEFAULT 0,
        taxa_np120 REAL DEFAULT 0,
        inadimplencia INTEGER DEFAULT 0,
        fraude INTEGER DEFAULT 0,
        status_safra TEXT DEFAULT 'MADURA',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare("ALTER TABLE fato_churn_safra ADD COLUMN safra_ord TEXT").run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS fato_fpd (
        id TEXT PRIMARY KEY,
        safra TEXT NOT NULL,
        safra_ord TEXT,
        cidade TEXT NOT NULL,
        uf TEXT NOT NULL,
        canal TEXT DEFAULT 'GERAL',
        familia_produto TEXT DEFAULT 'Dados',
        instalacoes INTEGER DEFAULT 0,
        fpd30 INTEGER DEFAULT 0,
        taxa_fpd30 REAL DEFAULT 0,
        fpd60 INTEGER DEFAULT 0,
        taxa_fpd60 REAL DEFAULT 0,
        cura INTEGER DEFAULT 0,
        taxa_cura REAL DEFAULT 0,
        faixa_risco TEXT DEFAULT 'MEDIO',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare("ALTER TABLE fato_fpd ADD COLUMN safra_ord TEXT").run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS fato_aprovacao_credito (
        id TEXT PRIMARY KEY,
        mes_referencia TEXT NOT NULL,
        cidade TEXT NOT NULL,
        uf TEXT NOT NULL,
        canal TEXT DEFAULT 'TODOS',
        pdv_ou_parceiro TEXT,
        consultas INTEGER DEFAULT 0,
        aprovados INTEGER DEFAULT 0,
        taxa_aprovacao REAL DEFAULT 0,
        recusas_politica INTEGER DEFAULT 0,
        recusas_antifraude INTEGER DEFAULT 0,
        risco_alto INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS fato_market_share (
        id TEXT PRIMARY KEY,
        mes_referencia TEXT NOT NULL,
        cidade TEXT NOT NULL,
        uf TEXT NOT NULL,
        operadora TEXT NOT NULL,
        acessos INTEGER DEFAULT 0,
        market_share_pct REAL DEFAULT 0,
        net_adds INTEGER DEFAULT 0,
        posicao_ranking INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS bot_knowledge_chunks (
        id TEXT PRIMARY KEY,
        modulo TEXT NOT NULL,
        topico TEXT NOT NULL,
        pergunta_exemplo TEXT,
        conteudo TEXT NOT NULL,
        palavras_chave TEXT,
        regras_calculo TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS bot_pending_sessions (
        phone TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run().catch(() => {});

    // 5. Tabelas da Área Centralizada de Uploads & Insumos
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS upload_delegations (
        id TEXT PRIMARY KEY,
        scope_type TEXT NOT NULL,
        scope_value TEXT NOT NULL DEFAULT 'ALL',
        delegated_user_id TEXT NOT NULL,
        delegated_user_name TEXT NOT NULL,
        delegated_user_email TEXT NOT NULL,
        created_at TEXT NOT NULL,
        created_by TEXT
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS report_uploads (
        id TEXT PRIMARY KEY,
        report_key TEXT NOT NULL,
        filename TEXT NOT NULL,
        filesize INTEGER NOT NULL,
        filetype TEXT NOT NULL,
        uploader_id TEXT NOT NULL,
        uploader_name TEXT NOT NULL,
        uploader_email TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed',
        records_count INTEGER DEFAULT 0,
        summary_metadata TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL
      )
    `).run().catch(() => {});

    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS upload_file_chunks (
        id TEXT PRIMARY KEY,
        upload_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_data TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    `).run().catch(() => {});

    // 6. Índices D1 para otimização de consultas de auditoria, filtros, autenticação, RAG e Uploads
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_access_logs_created ON access_logs (created_at DESC)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_access_logs_email ON access_logs (email_claro)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_access_logs_recurso ON access_logs (recurso)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs (user_id)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_users_login ON users (login_claro)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email_claro)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_users_status ON users (status)").run().catch(() => {});

    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_carteirizacao_tel ON dim_carteirizacao (telefone)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_ind_seg_mes_cid ON fato_indicadores_mensais (segmento, mes_referencia, tipo_visao, cidade)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_safra_visao_ent ON fato_churn_safra (safra, visao, entidade_nome)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_safra_ord ON fato_churn_safra (safra_ord DESC)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_fpd_safra_cid ON fato_fpd (safra, cidade)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_fpd_safra_ord ON fato_fpd (safra_ord DESC)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_aprov_mes_cid ON fato_aprovacao_credito (mes_referencia, cidade)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_mkt_mes_cid_op ON fato_market_share (mes_referencia, cidade, operadora)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_knowledge_mod_topico ON bot_knowledge_chunks (modulo, topico)").run().catch(() => {});

    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_upload_del_user ON upload_delegations (delegated_user_id)").run().catch(() => {});
    await env.DB.prepare("CREATE INDEX IF NOT EXISTS idx_report_uploads_key ON report_uploads (report_key, created_at DESC)").run().catch(() => {});

    _appDbInitialized = true;
  } catch (err) {
    console.error('Erro ensureAppSchema:', err);
  }
}
const ensureTvSchema = ensureAppSchema;

export function checkReportAccess(user, moduleKey) {
  if (!user) return false;
  if (user.status !== 'aprovado') return false;
  if (Boolean(user.is_admin)) return true;

  const raw = user.modules_allowed;
  if (raw === 'all') return true;
  if (raw === 'none' || raw === '' || !raw) return false;

  const target = normalizeModuleId(moduleKey);
  const mods = raw.split(',').map(m => normalizeModuleId(m.trim())).filter(Boolean);
  if (mods.includes('all')) return true;
  if (mods.includes(target)) return true;

  // Permissão estrita e granular: concede apenas módulos explicitamente selecionados
  return false;
}

// Lista Oficial dos 7 Insumos de Relatórios para Upload Centralizado
export const OFFICIAL_REPORT_INPUTS = [
  {
    key: 'churn-safra',
    name: 'Churn Safra D120',
    panel: 'Painel Churn Safra',
    destination_module: 'Painel Churn Safra',
    panelRoute: '/churn/',
    formats: ['.csv', '.xlsx', '.json'],
    accepted_formats: ['.csv', '.xlsx', '.json'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_churn_safra',
    description: 'Instalações, desconexões acumuladas D30 a D150, responsabilidade D120 do parceiro, Nunca Pagou e fraudes.',
    icon: 'chart-safra'
  },
  {
    key: 'fpd',
    name: 'FPD (First Payment Default)',
    panel: 'Painel FPD Regional Norte',
    destination_module: 'Painel FPD Regional Norte',
    panelRoute: '/fpd/',
    formats: ['.csv', '.zip', '.json'],
    accepted_formats: ['.csv', '.zip', '.json'],
    maxSizeMb: 300,
    max_size_mb: 300,
    target_table: 'fato_fpd',
    description: 'Microdados de 1ª fatura (aging30 e aging60), cura, canais de venda, faixas de risco (NV e Score) e georreferenciamento.',
    icon: 'shield-check'
  },
  {
    key: 'churn-bl-total',
    name: 'Churn Banda Larga Total',
    panel: 'Painel BL Total',
    destination_module: 'Painel Churn Banda Larga Total',
    panelRoute: '/churn-bl-total/',
    formats: ['.xlsx', '.json', '.csv'],
    accepted_formats: ['.xlsx', '.json', '.csv'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_indicadores_mensais',
    description: 'Acompanhamento semanal (T1 a T4), comparativo com orçado (RxO), MoM, YoY, YTD, base ativa e Speech Analytics.',
    icon: 'activity'
  },
  {
    key: 'churn-bl-pme',
    name: 'Churn Banda Larga PME',
    panel: 'Painel BL PME B2B',
    destination_module: 'Painel Churn Banda Larga PME',
    panelRoute: '/churn-bl-pme/',
    formats: ['.xlsx', '.json', '.csv'],
    accepted_formats: ['.xlsx', '.json', '.csv'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_indicadores_mensais',
    description: 'Desconexões empresariais de micro e pequenas empresas, encerramento de CNPJs, link dedicado e estabilidade IP.',
    icon: 'briefcase'
  },
  {
    key: 'panorama-market-share',
    name: 'Panorama Market Share Anatel',
    panel: 'Panorama Market Share',
    destination_module: 'Panorama Market Share Anatel',
    panelRoute: '/panorama-market-share/',
    formats: ['.csv', '.xlsx', '.json'],
    accepted_formats: ['.csv', '.xlsx', '.json'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_market_share',
    description: 'Acessos oficiais Anatel, market share Claro vs Vivo/Oi/ISPs, Net Adds e mapas de liderança municipal na Regional Norte.',
    icon: 'pie-chart'
  },
  {
    key: 'aprovacao-credito',
    name: 'Taxa de Aprovação de Crédito PF',
    panel: 'Taxa de Aprovação Residencial',
    destination_module: 'Taxa de Aprovação de Crédito PF',
    panelRoute: '/aprovacao-credito/',
    formats: ['.xlsx', '.csv', '.json'],
    accepted_formats: ['.xlsx', '.csv', '.json'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_aprovacao_credito',
    description: 'Consultas submetidas à financeira, propostas aprovadas, recusas de política, antifraude e curvas de risco por PDV e canal.',
    icon: 'credit-card'
  },
  {
    key: 'evolucao-carteira',
    name: 'Evolução de Carteira Móvel & B2B',
    panel: 'Painel Evolução de Carteira',
    destination_module: 'Painel Evolução de Carteira',
    panelRoute: '/evolucao-carteira/',
    formats: ['.xlsm', '.xlsx', '.csv', '.json'],
    accepted_formats: ['.xlsm', '.xlsx', '.csv', '.json'],
    maxSizeMb: 100,
    max_size_mb: 100,
    target_table: 'fato_evolucao_carteira',
    description: 'Acompanhamento de Gross Bruto, Descontos, Churn Involuntário/Voluntário, Matriz de Migrações e Net Adds por Regional.',
    icon: 'trending-up'
  },
  {
    key: 'bot-knowledge',
    name: 'Base de Conhecimento RAG do Bot',
    panel: 'WhatsApp Bot RAG',
    destination_module: 'Base de Conhecimento RAG do Bot',
    panelRoute: '/api/bot/ask',
    formats: ['.xlsx', '.csv', '.json'],
    accepted_formats: ['.xlsx', '.csv', '.json'],
    maxSizeMb: 50,
    max_size_mb: 50,
    target_table: 'bot_knowledge_chunks',
    description: 'Dicionário de regras de negócio, perguntas frequentes, políticas operacionais e fórmulas oficiais para o bot.',
    icon: 'cpu'
  }
];

export async function canManageUploads(user, env, reportKey = null) {
  if (!user) return false;
  if (user.status !== 'aprovado') return false;
  if (Boolean(user.is_admin)) return true;
  if (!env.DB) return false;

  try {
    if (!reportKey) {
      const row = await env.DB.prepare('SELECT id FROM upload_delegations WHERE delegated_user_id = ? LIMIT 1').bind(user.id).first();
      return Boolean(row);
    }
    const row = await env.DB.prepare(
      'SELECT id FROM upload_delegations WHERE delegated_user_id = ? AND (scope_type = ? OR scope_type = "ALL") LIMIT 1'
    ).bind(user.id, reportKey).first();
    return Boolean(row);
  } catch (err) {
    console.error('Erro canManageUploads:', err);
    return false;
  }
}

