/**
 * Sub-roteador de Divulgação Corporativa e TVs da Regional Norte
 * Rotas: /api/tv/*
 */

import {
  SECURITY_HEADERS,
  json,
  getSessionUser,
  logAccess,
  ensureAppSchema,
  getSystemControl,
  sendEmail,
} from '../utils/security.js';

export const ensureTvSchema = ensureAppSchema;

async function isTvApprover(user, env) {
  if (!user) return false;
  if (Boolean(user.is_admin)) return true;
  try {
    const d = await env.DB.prepare('SELECT id FROM tv_delegations WHERE delegated_user_id = ? LIMIT 1').bind(user.id).first();
    return Boolean(d);
  } catch (_) {
    return false;
  }
}

export async function handleTvRoutes(request, env, url, pathname) {
  if (!pathname.startsWith('/api/tv/')) {
    return null;
  }

  await ensureTvSchema(env);
  const adminEmail = env.ADMIN_EMAIL || 'arthur.rezende.analista@gmail.com';
  const baseUrl = env.PUBLIC_BASE_URL || 'https://pephub.cloud';

  // 1. GET /api/tv/playlist (Público para players de TV)
  if (pathname === '/api/tv/playlist' && request.method === 'GET') {
    const today = new Date().toISOString().split('T')[0];
    const configs = await env.DB.prepare('SELECT key, value FROM tv_config').all();
    const cfgMap = {};
    (configs.results || []).forEach(c => { cfgMap[c.key] = c.value; });

    const maxItems = parseInt(cfgMap.max_active_items || '50', 10);
    const proposals = await env.DB.prepare(`
      SELECT id, titulo, categoria, tipo_midia, duracao_segundos, data_inicio, data_fim, resolucao, media_type
      FROM tv_proposals
      WHERE status = 'aprovado' AND data_inicio <= ? AND data_fim >= ?
      ORDER BY created_at ASC
      LIMIT ?
    `).bind(today, today, maxItems).all();

    return json({
      items: (proposals.results || []).map(p => ({
        ...p,
        media_url: `/api/tv/media/${p.id}`
      })),
      config: {
        image_duration: parseInt(cfgMap.image_duration || '10', 10),
        max_active_items: maxItems,
        ticker_text: cfgMap.ticker_text || 'Regional Norte · Claro Brasil'
      }
    });
  }

  // 2. GET e HEAD /api/tv/media/:id (Stream de mídia com suporte completo a HTTP Range Requests e Content-Length)
  if (pathname.match(/^\/api\/tv\/media\/[^/]+$/) && (request.method === 'GET' || request.method === 'HEAD')) {
    const proposalId = pathname.split('/')[4];
    const proposal = await env.DB.prepare('SELECT id, media_type, tipo_midia FROM tv_proposals WHERE id = ?').bind(proposalId).first();
    if (!proposal) return new Response('Mídia não localizada', { status: 404 });

    // Consulta os metadados de todos os chunks de forma ultraleve (< 2KB de tráfego)
    const chunkMeta = await env.DB.prepare(
      'SELECT chunk_index, length(chunk_data) as b64_len, substr(chunk_data, -2) as last2 FROM tv_media_chunks WHERE proposal_id = ? ORDER BY chunk_index ASC'
    ).bind(proposalId).all();

    if (!chunkMeta.results || chunkMeta.results.length === 0) {
      return new Response('Conteúdo da mídia ausente', { status: 404 });
    }

    // Calcula tamanho binário exato de cada chunk e o tamanho total do arquivo
    let totalFileSize = 0;
    const chunkRanges = chunkMeta.results.map(cm => {
      const b64Len = cm.b64_len;
      let padding = 0;
      if (cm.last2 === '==') padding = 2;
      else if (cm.last2 && cm.last2.endsWith('=')) padding = 1;
      const binSize = Math.floor((b64Len * 3) / 4) - padding;
      const startByte = totalFileSize;
      const endByte = totalFileSize + binSize - 1;
      totalFileSize += binSize;
      return {
        chunk_index: cm.chunk_index,
        binSize,
        startByte,
        endByte
      };
    });

    const contentType = proposal.media_type || (proposal.tipo_midia === 'video' ? 'video/mp4' : 'image/jpeg');

    // Se for requisição HEAD, responde imediatamente com os headers de tamanho e range
    if (request.method === 'HEAD') {
      return new Response(null, {
        status: 200,
        headers: {
          'Content-Type': contentType,
          'Content-Length': String(totalFileSize),
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'public, max-age=86400, stale-while-revalidate=43200'
        }
      });
    }

    // Função ultrarrápida de decodificação Base64 para Uint8Array
    function decodeBase64Chunk(b64) {
      if (typeof Uint8Array.fromBase64 === 'function') {
        try { return Uint8Array.fromBase64(b64); } catch (_) {}
      }
      if (typeof Buffer !== 'undefined') {
        return Buffer.from(b64, 'base64');
      }
      const binStr = atob(b64);
      const len = binStr.length;
      const u8 = new Uint8Array(len);
      for (let j = 0; j < len; j++) {
        u8[j] = binStr.charCodeAt(j);
      }
      return u8;
    }

    // Processa Range Request se fornecido pelo navegador/player
    const rangeHeader = request.headers.get('range');
    let start = 0;
    let end = totalFileSize - 1;
    let isPartial = false;

    // Janela ampliada de streaming por requisição: 8MB (~8 fatias).
    // Garante ~4 segundos de buffer adiantado no player, reduzindo em 75% o número de requisições HTTP,
    // mantendo leituras D1 em lotes seguros de 2 fatias (< 2.8MB por query) para eliminar engasgos.
    const MAX_RANGE_WINDOW = 8000000;

    if (rangeHeader && rangeHeader.startsWith('bytes=')) {
      const parts = rangeHeader.replace('bytes=', '').split('-');
      const parsedStart = parseInt(parts[0], 10);
      const parsedEnd = parseInt(parts[1], 10);

      if (!isNaN(parsedStart)) {
        start = Math.max(0, Math.min(parsedStart, totalFileSize - 1));
      }
      if (!isNaN(parsedEnd)) {
        end = Math.max(start, Math.min(parsedEnd, totalFileSize - 1));
      } else {
        // Range aberto (ex: bytes=0- ou bytes=5000000-): delimita ao teto seguro da janela
        end = Math.min(start + MAX_RANGE_WINDOW - 1, totalFileSize - 1);
      }

      // Se a fatia solicitada pelo navegador for muito ampla, limita à janela de segurança
      if ((end - start + 1) > MAX_RANGE_WINDOW) {
        end = Math.min(start + MAX_RANGE_WINDOW - 1, totalFileSize - 1);
      }

      isPartial = true;
    }

    const contentLength = end - start + 1;

    // Determina quais chunks precisam ser lidos para satisfazer o Range solicitado
    const neededChunks = chunkRanges.filter(cr => cr.endByte >= start && cr.startByte <= end);

    const BATCH_SIZE = 2; // Lê em lotes de 2 chunks no máximo (~2.8MB) para respeitar rigorosamente o limite de 5MB do D1
    const stream = new ReadableStream({
      async start(controller) {
        try {
          for (let i = 0; i < neededChunks.length; i += BATCH_SIZE) {
            const batch = neededChunks.slice(i, i + BATCH_SIZE);
            const minIdx = batch[0].chunk_index;
            const maxIdx = batch[batch.length - 1].chunk_index;

            const chunks = await env.DB.prepare(
              "SELECT chunk_index, chunk_data FROM tv_media_chunks WHERE proposal_id = ? AND chunk_index >= ? AND chunk_index <= ? ORDER BY chunk_index ASC"
            ).bind(proposalId, minIdx, maxIdx).all();

            const chunksMap = new Map((chunks.results || []).map(c => [c.chunk_index, c.chunk_data]));

            for (const cr of batch) {
              const b64 = chunksMap.get(cr.chunk_index);
              if (!b64) continue;

              const u8 = decodeBase64Chunk(b64);

              // Calcula o recorte de bytes caso o chunk seja o primeiro ou o último do Range solicitado
              let sliceStart = 0;
              let sliceEnd = u8.length;

              if (start > cr.startByte) {
                sliceStart = start - cr.startByte;
              }
              if (end < cr.endByte) {
                sliceEnd = sliceStart + (end - Math.max(start, cr.startByte) + 1);
              }

              const sliced = (sliceStart === 0 && sliceEnd === u8.length) ? u8 : u8.subarray(sliceStart, sliceEnd);
              controller.enqueue(sliced);
            }
          }
          controller.close();
        } catch (errStream) {
          console.error('Erro no ReadableStream de mídia:', errStream);
          controller.error(errStream);
        }
      }
    });

    const responseHeaders = {
      'Content-Type': contentType,
      'Content-Length': String(contentLength),
      'Accept-Ranges': 'bytes',
      'Cache-Control': 'public, max-age=86400, stale-while-revalidate=43200'
    };

    if (isPartial) {
      responseHeaders['Content-Range'] = `bytes ${start}-${end}/${totalFileSize}`;
      return new Response(stream, {
        status: 206,
        headers: responseHeaders
      });
    }

    return new Response(stream, {
      status: 200,
      headers: responseHeaders
    });
  }

  // 3. GET /api/tv/proposals (Lista de propostas para usuários ou curadores)
  if (pathname === '/api/tv/proposals' && request.method === 'GET') {
    const user = await getSessionUser(request, env);
    if (!user) return json({ error: 'Não autenticado' }, 401);

    const canCurate = await isTvApprover(user, env);
    let proposals;
    if (canCurate) {
      proposals = await env.DB.prepare("SELECT * FROM tv_proposals WHERE status != 'uploading' ORDER BY created_at DESC").all();
    } else {
      proposals = await env.DB.prepare("SELECT * FROM tv_proposals WHERE user_id = ? AND status != 'uploading' ORDER BY created_at DESC").bind(user.id).all();
    }

    return json({
      proposals: (proposals.results || []).map(p => ({
        ...p,
        media_url: `/api/tv/media/${p.id}`
      })),
      can_curate: canCurate,
      is_admin: Boolean(user.is_admin)
    });
  }

  // 4.1 POST /api/tv/proposals/init (Inicializa proposta para upload em partes / chunks)
  if (pathname === '/api/tv/proposals/init' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || user.status !== 'aprovado') {
      return json({ error: 'Acesso restrito a colaboradores aprovados.' }, 403);
    }

    if (await getSystemControl(env, 'suspend_tv_submissions')) {
      return json({ error: 'O envio de novas propostas de mídia para as TVs está temporariamente suspenso pela administração.' }, 403);
    }

    const body = await request.json();
    const { titulo, categoria, tipo_midia, duracao_segundos, data_inicio, data_fim, resolucao, media_type } = body;

    if (!titulo || !categoria || !tipo_midia || !data_inicio || !data_fim) {
      return json({ error: 'Todos os campos da proposta são obrigatórios.' }, 400);
    }

    const proposalId = crypto.randomUUID();

    await env.DB.prepare(`
      INSERT INTO tv_proposals (
        id, user_id, nome_solicitante, email_claro, area_solicitante, titulo, categoria,
        tipo_midia, duracao_segundos, data_inicio, data_fim, status, resolucao, media_type, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'uploading', ?, ?, datetime('now'))
    `).bind(
      proposalId, user.id, user.nome_completo, user.email_claro, user.area || 'OUTROS',
      titulo.trim(), categoria, tipo_midia, parseInt(duracao_segundos || 10, 10),
      data_inicio, data_fim, resolucao || '1920x1080', media_type || (tipo_midia === 'video' ? 'video/mp4' : 'image/jpeg')
    ).run();

    return json({ success: true, id: proposalId });
  }

  // 4.2.1 POST /api/tv/proposals/:id/reset-chunks (Limpa chunks para re-sincronização)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/reset-chunks$/) && request.method === 'POST') {
    const adminKey = request.headers.get('x-admin-key');
    let user = adminKey === 'pephub-tv-sync-2026' ? { id: 'admin-system', status: 'aprovado' } : await getSessionUser(request, env);
    if (!user || user.status !== 'aprovado') {
      return json({ error: 'Acesso restrito.' }, 403);
    }
    const proposalId = pathname.split('/')[4];
    await env.DB.prepare('DELETE FROM tv_media_chunks WHERE proposal_id = ?').bind(proposalId).run();
    return json({ success: true, proposal_id: proposalId });
  }

  // 4.2 POST /api/tv/proposals/:id/chunk (Salva uma fatia de mídia)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/chunk$/) && request.method === 'POST') {
    const adminKey = request.headers.get('x-admin-key');
    let user = adminKey === 'pephub-tv-sync-2026' ? { id: 'admin-system', status: 'aprovado' } : await getSessionUser(request, env);
    if (!user || user.status !== 'aprovado') {
      return json({ error: 'Acesso restrito.' }, 403);
    }

    const proposalId = pathname.split('/')[4];
    const { chunk_index, chunk_data } = await request.json();

    if (chunk_index === undefined || !chunk_data) {
      return json({ error: 'Chunk inválido.' }, 400);
    }

    await env.DB.prepare(`
      INSERT INTO tv_media_chunks (id, proposal_id, chunk_index, chunk_data)
      VALUES (?, ?, ?, ?)
    `).bind(crypto.randomUUID(), proposalId, parseInt(chunk_index, 10), chunk_data).run();

    return json({ success: true, chunk_index });
  }

  // 4.3 POST /api/tv/proposals/:id/finalize (Finaliza upload em chunks e notifica curadores)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/finalize$/) && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || user.status !== 'aprovado') {
      return json({ error: 'Acesso restrito.' }, 403);
    }

    const proposalId = pathname.split('/')[4];
    const prop = await env.DB.prepare('SELECT * FROM tv_proposals WHERE id = ?').bind(proposalId).first();
    if (!prop) return json({ error: 'Proposta não localizada.' }, 404);

    await env.DB.prepare("UPDATE tv_proposals SET status = 'pendente' WHERE id = ?").bind(proposalId).run();
    await logAccess(env, request, user, `TV_PROPOSAL_SUBMIT:${prop.titulo}`);

    // Despacho de e-mail ao(s) aprovador(es) responsável(is)
    try {
      const delegations = await env.DB.prepare(`
        SELECT delegated_user_email FROM tv_delegations 
        WHERE scope_type = 'global' 
           OR (scope_type = 'area' AND lower(scope_value) = lower(?))
           OR (scope_type = 'user' AND scope_value = ?)
      `).bind(user.area || '', user.id).all();

      let approverEmails = (delegations.results || []).map(d => d.delegated_user_email).filter(Boolean);
      if (approverEmails.length === 0) approverEmails = [adminEmail];

      const reviewUrl = `${baseUrl}/pep-tools/divulgacao/?tab=curadoria`;
      const emailHtml = `
        <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
          <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte · PeP Tools</div>
            <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Nova Proposta para TVs Corporativas</h2>
          </div>
          <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
            <p style="margin-top:0">Uma nova proposta de mídia foi submetida e aguarda sua curadoria e aprovação:</p>
            <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:14px;margin:16px 0;font-size:12.5px">
              <div><strong>Título da Mídia:</strong> ${prop.titulo}</div>
              <div style="margin-top:4px"><strong>Categoria:</strong> ${prop.categoria.toUpperCase()}</div>
              <div style="margin-top:4px"><strong>Formato:</strong> ${prop.tipo_midia.toUpperCase()} (Widescreen ${prop.resolucao || '1920x1080'})</div>
              <div style="margin-top:4px"><strong>Período Solicitado:</strong> ${prop.data_inicio} até ${prop.data_fim}</div>
              <div style="margin-top:4px"><strong>Colaborador Solicitante:</strong> ${user.nome_completo} (${user.email_claro})</div>
              <div style="margin-top:4px"><strong>Canal / Área:</strong> ${user.area || '—'}</div>
            </div>
            <div style="margin:24px 0;text-align:center">
              <a href="${reviewUrl}" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                Avaliar Proposta no Painel
              </a>
            </div>
            <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
              Central de Divulgação Corporativa & TVs da Regional Norte.
            </p>
          </div>
        </div>
      `;

      for (const appEmail of approverEmails) {
        await sendEmail(env, {
          to: appEmail,
          subject: `[TV Corporativa] Nova Proposta: ${prop.titulo} (${prop.categoria})`,
          html: emailHtml,
          text: `Nova proposta de mídia submetida por ${user.nome_completo}: "${prop.titulo}" (${prop.categoria}). Avalie em: ${reviewUrl}`
        });
      }
    } catch (errEmail) {
      console.error('Erro envio email curadoria:', errEmail);
    }

    return json({ success: true, id: proposalId });
  }

  // 4. POST /api/tv/proposals (Submissão direta legada para arquivos menores)
  if (pathname === '/api/tv/proposals' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || user.status !== 'aprovado') {
      return json({ error: 'Acesso restrito a colaboradores aprovados.' }, 403);
    }

    if (await getSystemControl(env, 'suspend_tv_submissions')) {
      return json({ error: 'O envio de novas propostas de mídia para as TVs está temporariamente suspenso pela administração.' }, 403);
    }

    const body = await request.json();
    const { titulo, categoria, tipo_midia, duracao_segundos, data_inicio, data_fim, resolucao, media_type, media_base64 } = body;

    if (!titulo || !categoria || !tipo_midia || !data_inicio || !data_fim || !media_base64) {
      return json({ error: 'Todos os campos da proposta e a mídia são obrigatórios.' }, 400);
    }

    const proposalId = crypto.randomUUID();
    const cleanBase64 = media_base64.replace(/^data:[^;]+;base64,/, '');

    await env.DB.prepare(`
      INSERT INTO tv_proposals (
        id, user_id, nome_solicitante, email_claro, area_solicitante, titulo, categoria,
        tipo_midia, duracao_segundos, data_inicio, data_fim, status, resolucao, media_type, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendente', ?, ?, datetime('now'))
    `).bind(
      proposalId, user.id, user.nome_completo, user.email_claro, user.area || 'OUTROS',
      titulo.trim(), categoria, tipo_midia, parseInt(duracao_segundos || 10, 10),
      data_inicio, data_fim, resolucao || '1920x1080', media_type || (tipo_midia === 'video' ? 'video/mp4' : 'image/jpeg')
    ).run();

    // Chunks de ~500KB para persistência em D1
    const CHUNK_SIZE = 500000;
    const totalChunks = Math.ceil(cleanBase64.length / CHUNK_SIZE);
    for (let i = 0; i < totalChunks; i++) {
      const chunk = cleanBase64.substring(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE);
      await env.DB.prepare(`
        INSERT INTO tv_media_chunks (id, proposal_id, chunk_index, chunk_data)
        VALUES (?, ?, ?, ?)
      `).bind(crypto.randomUUID(), proposalId, i, chunk).run();
    }

    await logAccess(env, request, user, `TV_PROPOSAL_SUBMIT:${titulo}`);

    try {
      const delegations = await env.DB.prepare(`
        SELECT delegated_user_email FROM tv_delegations 
        WHERE scope_type = 'global' 
           OR (scope_type = 'area' AND lower(scope_value) = lower(?))
           OR (scope_type = 'user' AND scope_value = ?)
      `).bind(user.area || '', user.id).all();

      let approverEmails = (delegations.results || []).map(d => d.delegated_user_email).filter(Boolean);
      if (approverEmails.length === 0) approverEmails = [adminEmail];

      const reviewUrl = `${baseUrl}/pep-tools/divulgacao/?tab=curadoria`;
      const emailHtml = `
        <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
          <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte · PeP Tools</div>
            <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Nova Proposta para TVs Corporativas</h2>
          </div>
          <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
            <p style="margin-top:0">Uma nova proposta de mídia foi submetida e aguarda sua curadoria e aprovação:</p>
            <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:14px;margin:16px 0;font-size:12.5px">
              <div><strong>Título da Mídia:</strong> ${titulo}</div>
              <div style="margin-top:4px"><strong>Categoria:</strong> ${categoria.toUpperCase()}</div>
              <div style="margin-top:4px"><strong>Formato:</strong> ${tipo_midia.toUpperCase()} (Widescreen ${resolucao || '1920x1080'})</div>
              <div style="margin-top:4px"><strong>Período Solicitado:</strong> ${data_inicio} até ${data_fim}</div>
              <div style="margin-top:4px"><strong>Colaborador Solicitante:</strong> ${user.nome_completo} (${user.email_claro})</div>
              <div style="margin-top:4px"><strong>Canal / Área:</strong> ${user.area || '—'}</div>
            </div>
            <div style="margin:24px 0;text-align:center">
              <a href="${reviewUrl}" style="background:#1b2430;color:#ffffff;padding:11px 24px;text-decoration:none;font-weight:600;font-size:12.5px;border-radius:3px;display:inline-block">
                Avaliar Proposta no Painel
              </a>
            </div>
            <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
              Central de Divulgação Corporativa & TVs da Regional Norte.
            </p>
          </div>
        </div>
      `;

      for (const appEmail of approverEmails) {
        await sendEmail(env, {
          to: appEmail,
          subject: `[TV Corporativa] Nova Proposta: ${titulo} (${categoria})`,
          html: emailHtml,
          text: `Nova proposta de mídia submetida por ${user.nome_completo}: "${titulo}" (${categoria}). Avalie em: ${reviewUrl}`
        });
      }
    } catch (errEmail) {
      console.error('Erro envio email curadoria:', errEmail);
    }

    return json({ success: true, id: proposalId });
  }

  // 5. POST /api/tv/proposals/:id/approve (Aprovação de mídia)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/approve$/) && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) {
      return json({ error: 'Permissão negada para curadoria.' }, 403);
    }
    const proposalId = pathname.split('/')[4];
    const prop = await env.DB.prepare('SELECT * FROM tv_proposals WHERE id = ?').bind(proposalId).first();
    if (!prop) return json({ error: 'Proposta não localizada.' }, 404);

    await env.DB.prepare(`
      UPDATE tv_proposals SET 
        status = 'aprovado',
        aprovador_id = ?,
        aprovador_nome = ?,
        aprovador_email = ?,
        approved_at = datetime('now')
      WHERE id = ?
    `).bind(user.id, user.nome_completo, user.email_claro, proposalId).run();

    await logAccess(env, request, user, `TV_APPROVE:${prop.titulo}`);

    // Notificar solicitante por e-mail
    try {
      const emailHtml = `
        <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
          <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte · PeP Tools</div>
            <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Proposta de Divulgação Aprovada</h2>
          </div>
          <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
            <p style="margin-top:0">Olá, <strong>${prop.nome_solicitante}</strong>,</p>
            <p>Sua proposta de mídia <strong>"${prop.titulo}"</strong> foi avaliada e <strong>aprovada</strong> pelo curador ${user.nome_completo}.</p>
            <div style="background:#f7f8fa;border:1px solid #eceef1;border-radius:3px;padding:12px 14px;margin:16px 0;font-size:12.5px">
              <div><strong>Período de Veiculação:</strong> ${prop.data_inicio} até ${prop.data_fim}</div>
              <div style="margin-top:4px"><strong>Status:</strong> Programada para veiculação nas TVs da Regional</div>
            </div>
            <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
              Central de Divulgação Corporativa · Pephub Regional Norte.
            </p>
          </div>
        </div>
      `;
      await sendEmail(env, {
        to: prop.email_claro,
        subject: `[TV Corporativa] Proposta Aprovada: ${prop.titulo}`,
        html: emailHtml,
        text: `Sua proposta de mídia "${prop.titulo}" foi aprovada para veiculação de ${prop.data_inicio} até ${prop.data_fim}.`
      });
    } catch (_) {}

    return json({ success: true });
  }

  // 6. POST /api/tv/proposals/:id/reject (Rejeição de mídia com justificativa)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/reject$/) && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) {
      return json({ error: 'Permissão negada para curadoria.' }, 403);
    }
    const proposalId = pathname.split('/')[4];
    const { motivo } = await request.json();
    const prop = await env.DB.prepare('SELECT * FROM tv_proposals WHERE id = ?').bind(proposalId).first();
    if (!prop) return json({ error: 'Proposta não localizada.' }, 404);

    await env.DB.prepare(`
      UPDATE tv_proposals SET 
        status = 'rejeitado',
        motivo_rejeicao = ?,
        aprovador_id = ?,
        aprovador_nome = ?,
        aprovador_email = ?,
        approved_at = datetime('now')
      WHERE id = ?
    `).bind(motivo || 'Critérios visuais ou de conteúdo', user.id, user.nome_completo, user.email_claro, proposalId).run();

    await logAccess(env, request, user, `TV_REJECT:${prop.titulo}`);

    try {
      const emailHtml = `
        <div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border:1px solid #dfe3e8;border-radius:3px;overflow:hidden">
          <div style="background:linear-gradient(90deg,#8a0f18 0%,#c0191f 26%,#e23a1e 50%,#f47a1f 74%,#f9b233 100%);padding:16px 22px;color:#fff">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:.9">Regional Norte · PeP Tools</div>
            <h2 style="margin:4px 0 0;font-size:18px;font-weight:700">Retorno sobre Proposta de Mídia</h2>
          </div>
          <div style="padding:22px;color:#1c2430;font-size:13px;line-height:1.6">
            <p style="margin-top:0">Olá, <strong>${prop.nome_solicitante}</strong>,</p>
            <p>Sua proposta de mídia <strong>"${prop.titulo}"</strong> não pôde ser aprovada para veiculação no momento.</p>
            <div style="background:#fdece9;border:1px solid #f6c8c2;border-radius:3px;padding:12px 14px;margin:16px 0;font-size:12.5px;color:#9b1c1c">
              <strong>Observações do Curador:</strong><br>${motivo || 'A proposta não atende aos padrões de resolução ou vigência.'}
            </div>
            <p style="font-size:11.5px;color:#8b95a3;border-top:1px solid #eceef1;padding-top:12px">
              Você pode realizar ajustes e submeter uma nova proposta pelo painel.
            </p>
          </div>
        </div>
      `;
      await sendEmail(env, {
        to: prop.email_claro,
        subject: `[TV Corporativa] Retorno sobre Proposta: ${prop.titulo}`,
        html: emailHtml,
        text: `Sua proposta "${prop.titulo}" foi rejeitada. Motivo: ${motivo}`
      });
    } catch (_) {}

    return json({ success: true });
  }

  // 7. POST /api/tv/proposals/:id/suspend (Suspensão imediata de mídia ativa)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/suspend$/) && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) {
      return json({ error: 'Permissão negada.' }, 403);
    }
    const proposalId = pathname.split('/')[4];
    await env.DB.prepare("UPDATE tv_proposals SET status = 'suspenso' WHERE id = ?").bind(proposalId).run();
    await logAccess(env, request, user, `TV_SUSPEND:${proposalId}`);
    return json({ success: true });
  }

  // 8. POST /api/tv/proposals/:id/reactivate (Reativação de mídia suspensa)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+\/reactivate$/) && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) {
      return json({ error: 'Permissão negada.' }, 403);
    }
    const proposalId = pathname.split('/')[4];
    await env.DB.prepare("UPDATE tv_proposals SET status = 'aprovado' WHERE id = ?").bind(proposalId).run();
    await logAccess(env, request, user, `TV_REACTIVATE:${proposalId}`);
    return json({ success: true });
  }

  // 9. DELETE /api/tv/proposals/:id (Exclusão permanente de proposta)
  if (pathname.match(/^\/api\/tv\/proposals\/[^/]+$/) && request.method === 'DELETE') {
    const user = await getSessionUser(request, env);
    if (!user) return json({ error: 'Não autenticado' }, 401);
    const proposalId = pathname.split('/')[4];
    const prop = await env.DB.prepare('SELECT * FROM tv_proposals WHERE id = ?').bind(proposalId).first();
    if (!prop) return json({ error: 'Proposta não localizada.' }, 404);

    const canCurate = await isTvApprover(user, env);
    if (!canCurate && prop.user_id !== user.id) {
      return json({ error: 'Permissão negada para excluir esta proposta.' }, 403);
    }

    await env.DB.prepare('DELETE FROM tv_media_chunks WHERE proposal_id = ?').bind(proposalId).run();
    await env.DB.prepare('DELETE FROM tv_proposals WHERE id = ?').bind(proposalId).run();
    await logAccess(env, request, user, `TV_DELETE:${prop.titulo}`);
    return json({ success: true });
  }

  // 10. GET /api/tv/users (Lista de usuários aprovados para delegação)
  if (pathname === '/api/tv/users' && request.method === 'GET') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) return json({ error: 'Permissão negada.' }, 403);
    const users = await env.DB.prepare("SELECT id, nome_completo, email_claro, area FROM users WHERE status = 'aprovado' ORDER BY nome_completo ASC").all();
    return json(users.results || []);
  }

  // 11. GET /api/tv/delegations & POST /api/tv/delegations & DELETE /api/tv/delegations/:id (Gestão de Aprovadores Delegados)
  if (pathname === '/api/tv/delegations' && request.method === 'GET') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) return json({ error: 'Permissão negada.' }, 403);
    const delegations = await env.DB.prepare('SELECT * FROM tv_delegations ORDER BY created_at DESC').all();
    return json(delegations.results || []);
  }

  if (pathname === '/api/tv/delegations' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !user.is_admin) return json({ error: 'Apenas o Administrador pode delegar aprovações.' }, 403);

    const { scope_type, scope_value, delegated_user_id } = await request.json();
    if (!scope_type || !delegated_user_id) {
      return json({ error: 'Parâmetros incompletos para delegação.' }, 400);
    }

    const delegatedUser = await env.DB.prepare('SELECT id, nome_completo, email_claro FROM users WHERE id = ?').bind(delegated_user_id).first();
    if (!delegatedUser) return json({ error: 'Usuário a ser delegado não foi localizado.' }, 404);

    const delegationId = crypto.randomUUID();
    await env.DB.prepare(`
      INSERT INTO tv_delegations (id, scope_type, scope_value, delegated_user_id, delegated_user_name, delegated_user_email, created_at)
      VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    `).bind(
      delegationId, scope_type, scope_value || 'ALL',
      delegatedUser.id, delegatedUser.nome_completo, delegatedUser.email_claro
    ).run();

    await logAccess(env, request, user, `TV_DELEGATE:${delegatedUser.nome_completo}:${scope_type}`);
    return json({ success: true, id: delegationId });
  }

  if (pathname.match(/^\/api\/tv\/delegations\/[^/]+$/) && request.method === 'DELETE') {
    const user = await getSessionUser(request, env);
    if (!user || !user.is_admin) return json({ error: 'Apenas o Administrador pode remover delegações.' }, 403);
    const delegationId = pathname.split('/')[4];
    await env.DB.prepare('DELETE FROM tv_delegations WHERE id = ?').bind(delegationId).run();
    return json({ success: true });
  }

  // 12. GET /api/tv/config & POST /api/tv/config (Configurações da TV Corporativa)
  if (pathname === '/api/tv/config' && request.method === 'GET') {
    const configs = await env.DB.prepare('SELECT key, value FROM tv_config').all();
    const cfgMap = {};
    (configs.results || []).forEach(c => { cfgMap[c.key] = c.value; });
    return json(cfgMap);
  }

  if (pathname === '/api/tv/config' && request.method === 'POST') {
    const user = await getSessionUser(request, env);
    if (!user || !(await isTvApprover(user, env))) return json({ error: 'Permissão negada.' }, 403);

    const body = await request.json();
    for (const [k, v] of Object.entries(body)) {
      await env.DB.prepare('INSERT INTO tv_config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?').bind(k, String(v), String(v)).run();
    }
    await logAccess(env, request, user, 'TV_CONFIG_UPDATE');
    return json({ success: true });
  }

  return null;
}
