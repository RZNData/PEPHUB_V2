/**
 * Cloudflare Worker — Pephub Central de Uploads & Insumos de Relatórios
 * Área centralizada para upload e gestão de bases analíticas dos painéis:
 * - Churn Safra D120
 * - FPD Regional Norte
 * - Churn Banda Larga Total
 * - Churn Banda Larga PME
 * - Panorama Market Share
 * - Taxa de Aprovação de Crédito PF
 * - Base de Regras & Conhecimento RAG do Bot
 * 
 * Controle de Acesso Estrito: Apenas Administrador ou Colaboradores Delegados
 */

import {
  json,
  SECURITY_HEADERS,
  getSessionUser,
  logAccess,
  canManageUploads,
  OFFICIAL_REPORT_INPUTS,
} from '../utils/security.js';

export async function handleUploadRoutes(request, env, url, pathname) {
  if (!pathname.startsWith('/api/uploads')) {
    return null;
  }

  // 0. GET /api/uploads/template/:key (Download livre da estrutura / modelo oficial de dados da base)
  if (pathname.startsWith('/api/uploads/template/') && request.method === 'GET') {
    const reportKey = pathname.split('/')[4];
    const validReport = OFFICIAL_REPORT_INPUTS.find(r => r.key === reportKey);
    if (!validReport) {
      return json({ error: `Relatório inválido: '${reportKey}'.` }, 404);
    }

    const TEMPLATES = {
      'churn-safra': {
        filename: 'estrutura_base_churn_safra.csv',
        header: '"SAFRA";"COD_EMPRESA";"NM_EMPRESA";"CANAL";"CIDADE";"UF";"TIPO_VENDA";"QT_ATIVACAO";"DESCONEXAO_D30";"DESCONEXAO_D60";"DESCONEXAO_D90";"DESCONEXAO_D120";"DESCONEXAO_D150";"CHURN_D120_PCT";"NUNCA_PAGOU_PCT";"FRAUDE_PCT";"RESPONSABILIDADE_PARCEIRO_PCT"',
        sample: '"mai/26";"1024";"PARCEIRO NORTE TELECOM";"PAP";"MANAUS";"AM";"BANDA LARGA";150;4;8;12;15;18;10.0;1.2;0.5;8.3'
      },
      'fpd': {
        filename: 'estrutura_base_fpd_regional_norte.csv',
        header: '"ID_ANOMES_BASE";"SK_DATA";"SK_MUNICIPIO";"NR_CPF_CNPJ_ASSINANTE";"NR_CONTRATO";"DT_INI_CONTRATO";"DT_INI_ASSINATURA";"DT_SOLICITACAO";"DT_VENDA";"CD_OPERADORA";"NR_ANO_MES";"NM_VISAO_ANALISE";"NM_INDICADOR_NEGOCIO";"NM_MARCA";"NM_PERFIL_CLIENTE";"NM_LINHA_NEGOCIO";"NM_TIPO_ASS_DOMICILIO";"NM_FORMA_PAGAMENTO";"NM_MERCADO";"NM_EQUIPE_VENDA";"NM_CANAL_VENDA";"NM_CANAL_VENDA_SUBGRUPO";"NM_CANAL_VENDA_GRUPO";"NR_CPF_CNPJ_VENDEDOR";"NM_VENDEDOR";"NR_CNPJ";"NM_PARCEIRO";"COD_MUNICIPIO";"NM_CIDADE";"NM_REGIONAL";"PRODUTO_ATUAL";"NM_TIPO_PONTO_INSTALADO";"PRODUTO_DADOS";"SAFRA";"SAFRA_M3";"CPF";"ULT_DTCONSULTA";"CODIGO_LOG";"LOGON";"IDPOLITICA";"IDSTATUSDECISAO";"IDLOGONGESTOR";"HORA";"IDCIDADE";"PARTICIPACAO_EM_FALENCIA_PIE";"QT_ACOES_JUDICIAIS_ATE_A_DATA";"QT_PROTESTOS_ATE_A_DATA";"QT_CHEQUES_S_FUNDOS_ATE_A_DATA";"QT_CHEQUES_SUSTADOS_ATE_A_DATA";"QT_PEND_FINANC_PEFIN";"QT_PEND_FINANC_REFIN";"VL_TOT_DIVIDA";"SEMELHANCA_DE_GRAFIA";"DC_NUMERO_CONTRATO";"SCORE";"CPF_MEIO";"CLARO_VL_DIVIDA";"EMBRATEL_VL_DIVIDA";"NET_VL_DIVIDA";"VIA_EMBRATEL_VL_DIVIDA";"CLARO_AGING_VL_DIVIDA";"EMBRATEL_AGING_DIVIDA";"NET_AGING_DIVIDA";"VIA_EMBRATEL_AGING_DIVIDA";"IDPRODUTO";"IDTPDECISAO";"IDRECOMENDACAO1";"IDRECOMENDACAO2";"DE_CIDADE_OPERADORA";"SCORE_FINAL";"PRODUTO";"SCORE_FRAUDE";"IDSCFSTRECEITA";"SCF_SCORE_CREDITO_NET";"SCF_SCORE_FRAUDE_NET";"SIMILARIDADE_WL";"SIMILARIDADE_BB";"POLITICA";"RECOMENDACAO_1";"RECOMENDACAO_2";"NOME_RAZAO_SOCIAL";"DV_EQUIPE_VENDA";"DV_ATENDENTE";"DV_VENDEDOR";"PRODUTO_CONSULTA";"TP_CONSULTA";"TP_POLITICA";"MOTIVO_RECUSA_AGR";"MOTIVO_RECUSA";"MOTIVO_RECUSA_AGR2";"MOTIVO_RECUSA2";"SISTEMA";"ULT_AMOSTRA";"POL_20";"TP_POLITICA_II";"TP_POLITICA_OK";"CPF_TESTE";"REAPROV";"ULT_AP";"CHAVE";"FL_SERASA1";"ULT_RESTEX";"FL_IND_MOD";"FXSCORE";"FXRISCO";"WL";"FX_SCORE_WL";"NM_OPERADORA";"ULTCPF";"RETDT";"DIFDTPRI";"FL_5D";"FL_SERASA";"ULT_SCORE";"FXULTSCORE";"FLPROD";"FLAG_INAD_INT";"INAD_INT";"AGING_INAD_INT";"FAIXA_INAD_INT";"FAIXA_AGING_INAD_INT";"CIDADE_OP";"UF";"IBGE_GPOM";"CIDADE2";"GPON";"NM_REGIONAL_CMV";"MOB";"OVER90";"AGING30";"AGING60";"AGING90";"AGING120";"AGING150";"AGING180";"SEGUNDO_NIVEL";"SEGUNDO_NIVEL_BACKOF";"BASE";"MOTIVO_RECUSA_1";"MOTIVO_RECUSA_";"DIA";"OVERRIDE";"MOT_RECUSA_REC";"MOTIVO_RECUSA_OK";"MOTIVO_RECUSA_OK_V1";"IND_CLARO_BOX";"FX_RISCO_NV";"SCORE_FX_RISCO";"COD_FORNECEDOR_PONTO_VENDA";"DSC_NOME_REDE_PONTO_VENDA";"DSC_NOME_REDE";"DSC_STATUS_AGENTE";"DSC_TIPO_AGENTE";"DSC_NOME_PONTO_VENDA";"DENOMINADOR";"PORTFOLIO_TV";"DSC_SEGM_MUNICIPIO_BI"',
        sample: '"202605";"20260515";"1302603";"12345678900";"99887766";"2026-05-15";"2026-05-15";"2026-05-15";"2026-05-15";"01";"202605";"NET";"FPD";"CLARO";"RESIDENCIAL";"BANDA LARGA";"INDIVIDUAL";"BOLETO";"MANAUS";"EQUIPE PAP NORTE";"PAP";"EXTERNO";"PARCEIROS";"11223344556";"VENDEDOR EXEMPLO";"00112233000199";"PARCEIRO EXEMPLO";"1302603";"MANAUS";"REGIONAL NORTE";"BL 500M";"PRINCIPAL";"BANDA LARGA";"mai/26";"fev/26";"12345678900";"";"";"";"";"";"";"";"";"0";"0";"0";"0";"0";"0";"0";"0";"";"";"750";"";"0";"0";"0";"0";"0";"0";"0";"0";"";"";"";"";"MANAUS";"750";"BANDA LARGA";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"";"FX3";"BAIXO";"";"";"CLARO";"";"";"";"";"";"750";"";"";"0";"0";"0";"0";"0";"MANAUS";"AM";"1302603";"MANAUS";"SIM";"REGIONAL NORTE";"1";"0";"0";"0";"0";"0";"0";"0";"";"";"1";"";"";"15";"0";"";"";"";"0";"";"";"";"";"";"";"";"";"1";"BANDA LARGA";"MANAUS"'
      },
      'churn-bl-total': {
        filename: 'estrutura_base_churn_bl_total.csv',
        header: '"MES_REFERENCIA";"TENDENCIA";"PRACA";"UF";"CLUSTER";"TIPO_DESCONEXAO";"BASE_REAL";"BASE_ORC";"VOL_REAL";"VOL_ORC";"RXO_DELTA";"RXO_PCT";"VOL_MOM";"MOM_PCT";"VOL_YOY";"YOY_PCT";"YTD_REAL";"YTD_ORC";"YTD_2025";"TAXA_REAL";"TAXA_ORC"',
        sample: '"Outubro / 2026";"1ª Tendência (T1)";"MANAUS";"AM";"GM";"TOTAL";185400;192000;4200.5;4180.0;20.5;0.49;4100.0;2.45;4350.0;-3.44;41500.0;40200.0;38900.0;2.27;2.18'
      },
      'churn-bl-pme': {
        filename: 'estrutura_base_churn_bl_pme.csv',
        header: '"MES_REFERENCIA";"TENDENCIA";"PRACA";"UF";"CLUSTER";"TIPO_DESCONEXAO";"BASE_REAL";"VOL_REAL";"VOL_MOM";"MOM_PCT";"VOL_YOY";"YOY_PCT";"YTD_REAL";"YTD_2025";"TAXA_REAL"',
        sample: '"Outubro / 2026";"1ª Tendência (T1)";"MANAUS";"AM";"GM";"TOTAL";18250;450.0;465.0;-3.23;410.0;9.76;4410.0;3980.0;2.47'
      },
      'panorama-market-share': {
        filename: 'estrutura_base_panorama_market_share.csv',
        header: '"ANO_MES";"UF";"MUNICIPIO";"COD_IBGE";"GRUPO_ECONOMICO";"OPERADORA";"TECNOLOGIA";"MEIO_ACESSO";"FAIXA_VELOCIDADE";"ACESSOS_ATIVOS";"MARKET_SHARE_PCT";"NET_ADDS"',
        sample: '"202609";"AM";"MANAUS";"1302603";"CLARO";"CLARO";"FIBRA";"CABO/FIBRA";"> 300MB";145200;48.5;1250'
      },
      'aprovacao-credito': {
        filename: 'estrutura_base_taxa_aprovacao_credito.csv',
        header: '"ANO_MES";"SAFRA";"REGIONAL";"UF";"CIDADE";"CANAL_VENDA";"NOME_PARCEIRO";"PRODUTO";"TOTAL_CONSULTAS";"APROVADAS";"RECUSADAS_POLITICA";"RECUSADAS_FRAUDE";"TX_APROVACAO_PCT";"FAIXA_SCORE";"FAIXA_RISCO"',
        sample: '"202609";"set/26";"REGIONAL NORTE";"PA";"BELEM";"PAP";"PARCEIRO BELEM";"BANDA LARGA";850;620;180;50;72.9;"ALTO";"BAIXO RISCO"'
      },
      'bot-knowledge': {
        filename: 'estrutura_base_bot_knowledge_rag.csv',
        header: '"ID";"CATEGORIA";"TITULO";"CONTEUDO_REGRA_NEGOCIO";"PALAVRAS_CHAVE";"FONTE_OFICIAL";"ULTIMA_ATUALIZACAO"',
        sample: '"FPD_REGRA_01";"FPD";"Definição de FPD 60";"O First Payment Default a 60 dias (FPD 60) mede contratos de safra que não realizaram pagamento da primeira fatura até 60 dias após a instalação.";"fpd, fpd60, inadimplencia, aging60";"Manual de Churn & Qualidade Regional Norte";"2026-10-05"'
      }
    };

    const tmpl = TEMPLATES[reportKey];
    if (!tmpl) {
      return json({ error: 'Modelo não configurado para este relatório.' }, 404);
    }

    const csvContent = "\uFEFF" + tmpl.header + "\r\n" + tmpl.sample + "\r\n";
    return new Response(new TextEncoder().encode(csvContent), {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="${tmpl.filename}"`,
        'Cache-Control': 'no-store',
        ...SECURITY_HEADERS,
      }
    });
  }

  // Todas as rotas seguintes exigem sessão ativa
  const user = await getSessionUser(request, env);
  if (!user) {
    return json({ error: 'Sessão expirada ou não autenticada.' }, 401);
  }

  // 1. GET /api/uploads/config (Lista os 7 insumos, status de última carga e permissões)
  if (pathname === '/api/uploads/config' && request.method === 'GET') {
    const hasAnyAccess = await canManageUploads(user, env);
    if (!hasAnyAccess) {
      return json({ error: 'Acesso restrito à administração ou usuários delegados.' }, 403);
    }

    const items = [];
    for (const inp of OFFICIAL_REPORT_INPUTS) {
      const canUpload = await canManageUploads(user, env, inp.key);
      let lastUpload = null;
      if (env.DB) {
        try {
          lastUpload = await env.DB.prepare(`
            SELECT id, filename, filesize, filetype, uploader_name, uploader_email, status, records_count, summary_metadata, created_at
            FROM report_uploads
            WHERE report_key = ?
            ORDER BY created_at DESC
            LIMIT 1
          `).bind(inp.key).first();
        } catch (_) {}
      }

      items.push({
        ...inp,
        can_upload: canUpload,
        last_upload: lastUpload || null,
      });
    }

    return json({
      is_admin: Boolean(user.is_admin),
      user: {
        id: user.id,
        nome: user.nome_completo,
        email: user.email_claro,
      },
      inputs: items,
    });
  }

  // 2. GET /api/uploads/history (Histórico de envios)
  if (pathname === '/api/uploads/history' && request.method === 'GET') {
    const hasAnyAccess = await canManageUploads(user, env);
    if (!hasAnyAccess) {
      return json({ error: 'Acesso não autorizado.' }, 403);
    }

    const reportKey = url.searchParams.get('report');
    let uploads = [];
    if (env.DB) {
      try {
        if (reportKey) {
          const res = await env.DB.prepare(`
            SELECT id, report_key, filename, filesize, filetype, uploader_name, uploader_email, status, records_count, summary_metadata, error_message, created_at
            FROM report_uploads
            WHERE report_key = ?
            ORDER BY created_at DESC
            LIMIT 30
          `).bind(reportKey).all();
          uploads = res?.results || [];
        } else {
          const res = await env.DB.prepare(`
            SELECT id, report_key, filename, filesize, filetype, uploader_name, uploader_email, status, records_count, summary_metadata, error_message, created_at
            FROM report_uploads
            ORDER BY created_at DESC
            LIMIT 50
          `).all();
          uploads = res?.results || [];
        }
      } catch (err) {
        console.error('[Uploads History Error]', err);
      }
    }

    return json({ uploads });
  }

  // 3. POST /api/uploads/submit (Recebe arquivo, registra e persiste chunks)
  if (pathname === '/api/uploads/submit' && request.method === 'POST') {
    try {
      const body = await request.json();
      const { report_key, filename, filesize, filetype, content_base64, chunk_data, chunk_index, total_chunks, metadata } = body;

      if (!report_key || !filename) {
        return json({ error: 'Parâmetros obrigatórios ausentes: report_key e filename.' }, 400);
      }

      // Valida se o insumo pertence à lista oficial
      const validReport = OFFICIAL_REPORT_INPUTS.find(r => r.key === report_key);
      if (!validReport) {
        return json({ error: `Relatório inválido: '${report_key}'.` }, 400);
      }

      // Valida autorização estrita (Admin ou Delegado do relatório específico)
      const authorized = await canManageUploads(user, env, report_key);
      if (!authorized) {
        return json({ error: `Você não possui permissão delegada para carregar insumos de '${validReport.name}'.` }, 403);
      }

      const uploadId = body.upload_id || crypto.randomUUID();
      const now = new Date().toISOString();
      const currentChunk = chunk_index ?? 0;
      const numChunks = total_chunks ?? 1;

      // Se for o primeiro chunk, cria o registro do upload
      if (currentChunk === 0 && env.DB) {
        const recordsCount = metadata?.records_count || 0;
        const metaStr = metadata ? JSON.stringify(metadata) : '{}';

        await env.DB.prepare(`
          INSERT INTO report_uploads (
            id, report_key, filename, filesize, filetype, uploader_id, uploader_name, uploader_email, status, records_count, summary_metadata, created_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?, ?, ?)
        `).bind(
          uploadId,
          report_key,
          filename,
          filesize || 0,
          filetype || 'application/octet-stream',
          user.id,
          user.nome_completo,
          user.email_claro,
          recordsCount,
          metaStr,
          now
        ).run();
      }

      // Salva chunk no D1 se enviado
      const dataPayload = chunk_data || content_base64 || '';
      if (dataPayload && env.DB) {
        await env.DB.prepare(`
          INSERT INTO upload_file_chunks (id, upload_id, chunk_index, chunk_data, created_at)
          VALUES (?, ?, ?, ?, ?)
        `).bind(crypto.randomUUID(), uploadId, currentChunk, dataPayload, now).run().catch(() => {});
      }

      // Registra log de auditoria corporativa
      await logAccess(env, request, user, `UPLOAD_INPUT:${report_key.toUpperCase()}:${filename}`);

      return json({
        success: true,
        upload_id: uploadId,
        report_key,
        filename,
        chunk_index: currentChunk,
        total_chunks: numChunks,
        message: `Insumo de ${validReport.name} carregado com sucesso!`
      });
    } catch (err) {
      console.error('[Upload Submit Error]', err);
      return json({ error: 'Erro ao processar envio do insumo.', details: err.message }, 500);
    }
  }

  // 4. GET /api/uploads/download/:id (Download do arquivo original)
  if (pathname.startsWith('/api/uploads/download/') && request.method === 'GET') {
    const hasAnyAccess = await canManageUploads(user, env);
    if (!hasAnyAccess) {
      return json({ error: 'Acesso não autorizado.' }, 403);
    }

    const uploadId = pathname.split('/')[4];
    if (!uploadId || !env.DB) {
      return json({ error: 'ID de upload inválido.' }, 400);
    }

    const rec = await env.DB.prepare('SELECT * FROM report_uploads WHERE id = ?').bind(uploadId).first();
    if (!rec) {
      return json({ error: 'Insumo não localizado.' }, 404);
    }

    // Busca os chunks
    const chunksRes = await env.DB.prepare(`
      SELECT chunk_data FROM upload_file_chunks
      WHERE upload_id = ?
      ORDER BY chunk_index ASC
    `).bind(uploadId).all();

    const chunks = chunksRes?.results || [];
    let fullBase64 = chunks.map(c => c.chunk_data).join('');

    // Se tiver prefixo data:...;base64,
    if (fullBase64.includes('base64,')) {
      fullBase64 = fullBase64.split('base64,')[1];
    }

    let binaryData;
    try {
      const binaryString = atob(fullBase64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      binaryData = bytes;
    } catch (_) {
      // Se for texto plano
      binaryData = new TextEncoder().encode(fullBase64);
    }

    return new Response(binaryData, {
      status: 200,
      headers: {
        'Content-Type': rec.filetype || 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${encodeURIComponent(rec.filename)}"`,
        'Cache-Control': 'no-store',
        ...SECURITY_HEADERS,
      }
    });
  }

  // 5. GESTÃO DE DELEGAÇÕES (Apenas Administradores)
  if (pathname === '/api/uploads/delegations') {
    if (!user.is_admin) {
      return json({ error: 'Apenas administradores podem gerenciar delegações.' }, 403);
    }

    // Listar delegações
    if (request.method === 'GET') {
      const res = await env.DB.prepare(`
        SELECT d.*, u.area, u.funcao
        FROM upload_delegations d
        LEFT JOIN users u ON d.delegated_user_id = u.id
        ORDER BY d.created_at DESC
      `).all();
      return json(res?.results || []);
    }

    // Criar nova delegação
    if (request.method === 'POST') {
      const { delegated_user_id, scope_type } = await request.json();
      if (!delegated_user_id || !scope_type) {
        return json({ error: 'Campos obrigatórios: delegated_user_id e scope_type.' }, 400);
      }

      const targetUser = await env.DB.prepare(
        'SELECT id, nome_completo, email_claro FROM users WHERE id = ?'
      ).bind(delegated_user_id).first();

      if (!targetUser) {
        return json({ error: 'Colaborador selecionado não foi encontrado.' }, 404);
      }

      const delId = crypto.randomUUID();
      const now = new Date().toISOString();

      await env.DB.prepare(`
        INSERT INTO upload_delegations (id, scope_type, scope_value, delegated_user_id, delegated_user_name, delegated_user_email, created_at, created_by)
        VALUES (?, ?, 'ALL', ?, ?, ?, ?, ?)
      `).bind(
        delId,
        scope_type,
        targetUser.id,
        targetUser.nome_completo,
        targetUser.email_claro,
        now,
        user.email_claro
      ).run();

      await logAccess(env, request, user, `DELEGATE_UPLOAD:${targetUser.nome_completo}:${scope_type}`);
      return json({ success: true, id: delId });
    }
  }

  // Revogar delegação
  if (pathname.startsWith('/api/uploads/delegations/') && request.method === 'DELETE') {
    if (!user.is_admin) {
      return json({ error: 'Apenas administradores podem revogar delegações.' }, 403);
    }

    const delId = pathname.split('/')[4];
    await env.DB.prepare('DELETE FROM upload_delegations WHERE id = ?').bind(delId).run();
    await logAccess(env, request, user, `REVOKE_DELEGATION:${delId}`);
    return json({ success: true });
  }

  return null;
}
