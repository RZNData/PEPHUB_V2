/**
 * Cloudflare Worker — Pephub Bot RAG & Text-to-SQL Router
 * Módulo de Inteligência Artificial para WhatsApp (Evolution API & Baileys Bridge)
 * Roteamento Semântico: Classificador de Intenção -> Text-to-SQL vs Semantic RAG
 * Regional Norte (AM, PA, MA, AP, RR)
 */

import { json, SECURITY_HEADERS, getSystemControl } from '../utils/security.js';
import {
  REPORT_REGISTRY,
  getAllReports,
  getReportById,
  getReportByNum,
  buildDisambiguationMenu,
  buildBaseSelectionMenu,
  buildProductSelectionMenu,
  buildSegmentSelectionMenu,
  buildActionSelectionMenu,
  buildPartnerChannelPromptMenu,
  buildPartnerCityPromptMenu,
  buildChannelCityPromptMenu,
  buildCityChannelPromptMenu,
  buildChannelPromptMenu,
  buildChannelListMenu,
  buildCityPromptMenu,
  buildCityListMenu,
  buildDddPromptMenu,
  buildSpeechPromptMenu,
  buildMotivosPromptMenu,
  buildCardFooterLinks,
  buildActionCardFooterLinks,
  executeExecutiveSummaryCard,
  executeLast3MonthsCard,
  executePartnerRankingCard,
  executeChannelRankingCard,
  executeCityRankingCard,
  executeChurnBlSummaryCard,
  executeChurnBlLast3MonthsCard,
  executeChurnBlCityRankingCard,
  executeMarketShareRegionalCard,
  executeMarketShareResidencialCard,
  executeMarketShareMovelCard,
  executeSpeechCard,
  executeMotivosCard,
  OFFICIAL_14_CITIES,
  OFFICIAL_CHANNELS,
  OFFICIAL_PRODUCTS,
  OFFICIAL_DDDS,
  buildSchemaPromptContext,
  buildDeterministicAnalyticalSQL
} from '../bot_registry.js';

export const OFFICIAL_REPORTS = REPORT_REGISTRY;

// Chave e modelo padrão do Gemini
const DEFAULT_GEMINI_KEY = 'AIzaSyDcI6EfL_1N1eq-o9XSLktSeiS4MxwyzYo';
const DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash';

// Configuração padrão da Evolution API
const DEFAULT_EVOLUTION_URL = 'http://localhost:8080';
const DEFAULT_EVOLUTION_KEY = 'pephub_secret_token_2026';
const DEFAULT_EVOLUTION_INSTANCE = 'pephub-bot';

/**
 * Normaliza número de telefone (apenas dígitos, mínimo 10)
 */
export function normalizePhone(rawPhone) {
  if (!rawPhone) return '';
  const digits = String(rawPhone).replace(/\D/g, '');
  // Remove sufixos como @s.whatsapp.net ou :44@s.whatsapp.net
  return digits;
}

/**
 * Verifica autorização do número remetente no D1
 */
export async function verifyBotSender(env, rawPhone) {
  const cleanPhone = normalizePhone(rawPhone);
  if (!cleanPhone) {
    return { allowed: false, phone: '', reason: 'empty_phone' };
  }

  // 1. Verifica suspensão administrativa global do bot
  const isSuspended = await getSystemControl(env, 'suspend_whatsapp_bot');
  if (isSuspended) {
    return { allowed: false, phone: cleanPhone, reason: 'suspended' };
  }

  if (!env.DB) {
    return { allowed: true, phone: cleanPhone, user: { nome: 'Operação Regional' }, scope: { permissao_total: 1 } };
  }

  // 2. Busca na tabela dim_carteirizacao
  try {
    const carteira = await env.DB.prepare(`
      SELECT * FROM dim_carteirizacao WHERE telefone = ? OR telefone LIKE ?
    `).bind(cleanPhone, `%${cleanPhone.slice(-8)}%`).first();

    if (carteira) {
      return {
        allowed: true,
        phone: cleanPhone,
        scope: {
          regional: carteira.regional || 'REGIONAL NORTE',
          canal: carteira.canal || 'TODOS',
          cidade: carteira.cidade || 'TODAS',
          permissao_total: carteira.permissao_total ?? 1,
        },
        user: { nome: carteira.nome },
      };
    }

    // 3. Fallback: busca na tabela users (usuários corporativos aprovados)
    const user = await env.DB.prepare(`
      SELECT id, nome_completo, area, funcao, is_admin, status, telefone
      FROM users
      WHERE status = 'aprovado' AND (telefone = ? OR telefone LIKE ?)
    `).bind(cleanPhone, `%${cleanPhone.slice(-8)}%`).first();

    if (user) {
      return {
        allowed: true,
        phone: cleanPhone,
        scope: {
          regional: 'REGIONAL NORTE',
          canal: 'TODOS',
          cidade: 'TODAS',
          permissao_total: 1,
        },
        user: {
          id: user.id,
          nome: user.nome_completo,
          area: user.area,
          isAdmin: Boolean(user.is_admin),
        },
      };
    }
  } catch (err) {
    console.error('[Bot Auth] Erro ao validar telefone no D1:', err);
  }

  return { allowed: false, phone: cleanPhone, reason: 'not_found' };
}

/**
 * Chamada à API Google Gemini REST
 */
async function callGemini(env, systemInstruction, userPrompt, temperature = 0.1) {
  const apiKey = env?.GEMINI_API_KEY || DEFAULT_GEMINI_KEY;
  const primaryModel = env?.GEMINI_MODEL || DEFAULT_GEMINI_MODEL;
  const modelsToTry = [primaryModel, 'gemini-2.5-flash-lite', 'gemini-2.5-flash'];
  const uniqueModels = [...new Set(modelsToTry)];

  for (const model of uniqueModels) {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    const payload = {
      contents: [
        {
          parts: [
            { text: `${systemInstruction}\n\n${userPrompt}` }
          ]
        }
      ],
      generationConfig: {
        temperature,
        maxOutputTokens: 2048,
        thinkingConfig: { thinkingBudget: 0 }
      }
    };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errText = await res.text();
        console.warn(`[Gemini Error - ${model}] HTTP ${res.status}:`, errText);
        continue;
      }

      const data = await res.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (text && text.trim()) {
        return text.trim();
      }
    } catch (err) {
      console.warn(`[Gemini Exception - ${model}]`, err.message);
    }
  }

  return null;
}

function normalizeQueryText(str) {
  return (str || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
}

/**
 * Classificador de Intenção do Roteador (Intent Classifier)
 * Otimizado com Fast-Path Determinístico (0.05ms) para consultas comuns
 */
export async function classifyIntent(env, query) {
  const norm = normalizeQueryText(query);

  // 1. FAST-PATH DETERMINÍSTICO (Zero Latência ~0.05ms)
  // Perguntas Conceituais / Glossário / Fórmulas / Regras de Negócio
  const conceptualPatterns = [
    /\bo\s+que\s+e(\s+|$|\?)/i,
    /\bo\s+que\s+significa(\s+|$|\?)/i,
    /\bqual\s+([ao]|e)\s+(conceito|definicao|significado|regra|formula)(\s+|$|\?)/i,
    /\bcomo\s+(calcula|calcular|funciona|opera)(\s+|$|\?)/i,
    /\bconceito\s+d[eo](\s+|$|\?)/i,
    /\bdefinicao\s+d[eo](\s+|$|\?)/i,
    /\bsignificado\s+d[eo](\s+|$|\?)/i,
    /\bdiferenca\s+entre(\s+|$|\?)/i,
    /\bqual\s+a\s+diferenca(\s+|$|\?)/i,
    /\bpor\s+que(\s+|$|\?)/i,
    /\bexpli(que|car)\s+(o\s+que\s+e|o\s+conceito|a\s+regra)/i,
    /\bglossario\b/i,
  ];

  for (const pattern of conceptualPatterns) {
    if (pattern.test(norm)) {
      return { intent: 'CONCEITUAL', reason: 'Fast-Path Determinístico Conceitual' };
    }
  }

  // Opções de Menu de Desambiguação (1 a 5 ou Opção 1 a 5)
  if (/^(?:op[çc][ãa]o\s*)?[1-5](?:[️⃣\.\)\-\s]|$)/i.test(norm)) {
    return { intent: 'ANALITICA', reason: 'Seleção de Menu de Desambiguação' };
  }

  // Cumprimentos, Menus e Comandos Rápidos de Ajuda
  const greetingOrHelpPatterns = [
    /^(oi|ola|bom\s+dia|boa\s+tarde|boa\s+noite|menu|ajuda|help|comandos|\?|#\?|status)$/i,
    /^(o\s+que\s+voce\s+faz|quem\s+e\s+voce|como\s+usar|opcoes)$/i,
  ];
  for (const pattern of greetingOrHelpPatterns) {
    if (pattern.test(norm)) {
      return { intent: 'FORA_ESCOPO', reason: 'Fast-Path Catálogo de Consultas e Boas-Vindas' };
    }
  }

  // Indicadores Analíticos (Metas, Volumes, Taxas, Cidades, Safras, Rankings)
  const analyticalPatterns = [
    /\b(churn|fpd|meta|metas|realizado|orcado|safra|safras|d120|np120|d30|d60|d90|instalacao|instalacoes|vendas|parceiro|parceiros|taxa|taxas|volume|volumes|desconexao|desconexoes|involuntario|involuntaria|voluntario|voluntaria|cura|aging30|aging60|pme|banda\s+larga|market\s+share|anatel|credito|aprovacao|recusas|antifraude|ranking|top\s*\d+|piores|melhores)\b/i,
    /\b(belem|manaus|sao\s+luis|macapa|boa\s+vista|santarem|maraba|ananindeua|castanhal|imperatriz|parauapebas|barcarena|itaituba)\b/i,
    /\b(quanto|quantos|quais|qual\s+foi|qual\s+e\s+o|qual\s+e\s+a|como\s+esta|resultado)\b/i,
  ];
  for (const pattern of analyticalPatterns) {
    if (pattern.test(norm)) {
      return { intent: 'ANALITICA', reason: 'Fast-Path Analítico Heurístico' };
    }
  }

  // 2. SLOW-PATH LLM (Apenas para consultas complexas e semanticamente ambíguas)
  const systemInstruction = `Você é um Classificador de Intenção de Consultas para o Bot de Dados Operacionais da Claro (Regional Norte).
Sua tarefa é analisar a pergunta do usuário e responder EXCLUSIVAMENTE um objeto JSON no formato:
{"intent": "ANALITICA" | "CONCEITUAL" | "FORA_ESCOPO", "reason": "breve justificativa"}

REGRAS:
1. "ANALITICA": Números, indicadores, metas, safras, rankings, volumes, taxas ou comparativos de telecom.
2. "CONCEITUAL": Definições, conceitos, siglas, regras de negócio ou fórmulas.
3. "FORA_ESCOPO": Perguntas gerais, não relacionadas à Claro, Pephub, telecom ou operações.
Responda APENAS o JSON válido.`;

  const raw = await callGemini(env, systemInstruction, `Pergunta: "${query}"`, 0.0);
  if (raw) {
    try {
      const cleanJson = raw.replace(/```json/gi, '').replace(/```/g, '').trim();
      const parsed = JSON.parse(cleanJson);
      if (['ANALITICA', 'CONCEITUAL', 'FORA_ESCOPO'].includes(parsed.intent)) {
        return parsed;
      }
    } catch (_) {}
  }

  return { intent: 'FORA_ESCOPO', reason: 'Não correlacionado a indicadores de telecom' };
}

/**
 * Validação Estrita de Segurança para SQL (Apenas SELECT, proíbe mutações e comandos destrutivos)
 */
export function validateSafeSQL(sql) {
  if (!sql || typeof sql !== 'string') return { safe: false, reason: 'SQL vazio' };
  const trimmed = sql.trim();

  // Permite apenas queries iniciadas por SELECT ou WITH (Common Table Expressions)
  if (!/^(\s*SELECT|\s*WITH)\b/i.test(trimmed)) {
    return { safe: false, reason: 'Comando SQL não iniciado por SELECT ou WITH' };
  }

  // Rejeita múltiplos comandos separados por ponto e vírgula
  const withoutTrailingSemicolon = trimmed.replace(/;\s*$/, '');
  if (withoutTrailingSemicolon.includes(';')) {
    return { safe: false, reason: 'Múltiplas instruções SQL detectadas (;)' };
  }

  // Lista proibida de comandos e palavras-chave de mutação / injeção
  const forbiddenPatterns = [
    /\bINSERT\b/i,
    /\bUPDATE\b/i,
    /\bDELETE\b/i,
    /\bDROP\b/i,
    /\bALTER\b/i,
    /\bCREATE\b/i,
    /\bREPLACE\b/i,
    /\bATTACH\b/i,
    /\bDETACH\b/i,
    /\bPRAGMA\b/i,
    /\bVACUUM\b/i,
    /\bREINDEX\b/i,
    /\bTRUNCATE\b/i,
    /\bEXEC\b/i,
    /\bEXECUTE\b/i,
    /--/, // comentários de injeção
    /\/\*/, // comentários de bloco
  ];

  for (const pattern of forbiddenPatterns) {
    if (pattern.test(withoutTrailingSemicolon)) {
      return { safe: false, reason: `Palavra-chave ou padrão não permitido: ${pattern}` };
    }
  }

  return { safe: true, sql: withoutTrailingSemicolon };
}

/**
 * Resolvedor de Relatório-Alvo com Memória de Sessão Persistida no D1
 */
export async function resolveTargetReport(env, query, phone) {
  const norm = query.toLowerCase().trim();
  const cleanDigits = String(phone || '').replace(/\D/g, '');

  // 1. Verifica se o usuário enviou uma opção de desambiguação direta (1 a 7, 1️⃣, opção 1, etc.)
  const menuMatch = norm.match(/^(?:op[çc][ãa]o\s*)?([1-7])(?:[️⃣\.\)\-\s]|$)/i);
  const singleDigit = menuMatch ? menuMatch[1] : null;

  if (singleDigit || /^(fpd|first\s*payment|churn|banda\s*larga|safra|d120|np120|credito|crédito|antifraude|market|mkt|share|anatel|speech|transcric|motivo|motivos|os|taxa\s*os|ura|visita\s*tecnica)$/i.test(norm)) {
    let pendingQuery = null;
    if (env.DB && cleanDigits) {
      try {
        const row = await env.DB.prepare('SELECT query FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).first();
        if (row && row.query) {
          pendingQuery = row.query;
          await env.DB.prepare('DELETE FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).run();
        }
      } catch (e) {
        console.warn('[D1 Pending Session Lookup Error]', e.message);
      }
    }

    let selectedReport = null;
    if (singleDigit) {
      selectedReport = getReportByNum(singleDigit);
    } else if (/^(fpd|first\s*payment)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.FPD;
    } else if (/^(churn|banda\s*larga)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CHURN_BL;
    } else if (/^(safra|d120|np120)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CHURN_SAFRA;
    } else if (/^(credito|crédito|antifraude)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CREDITO;
    } else if (/^(market|mkt|share|anatel)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.MARKET_SHARE;
    } else if (/^(speech|transcric)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.SPEECH;
    } else if (/^(motivo|motivos|os|taxa\s*os|ura|visita)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.MOTIVOS;
    }

    if (selectedReport) {
      if (pendingQuery) {
        return { report: selectedReport, effectiveQuery: `${pendingQuery} (${selectedReport.name})`, disambiguated: true };
      }
      return { report: selectedReport, effectiveQuery: `resumo dos indicadores oficiais de ${selectedReport.name}`, disambiguated: true };
    }
  }

  // 2. Detecção explícita na pergunta por palavras-chave registradas
  // Precedência de relatórios: FPD > SPEECH > MOTIVOS > CREDITO > MARKET_SHARE > CHURN_SAFRA > CHURN_BL
  for (const key of ['FPD', 'SPEECH', 'MOTIVOS', 'CREDITO', 'MARKET_SHARE', 'CHURN_SAFRA', 'CHURN_BL']) {
    const rep = REPORT_REGISTRY[key];
    if (!rep) continue;
    for (const pat of rep.keywords) {
      if (pat.test(norm)) {
        if (env.DB && cleanDigits) {
          try {
            await env.DB.prepare('DELETE FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).run();
          } catch (_) {}
        }
        return { report: rep, effectiveQuery: query, disambiguated: false };
      }
    }
  }

  // 3. Consulta ambígua: salva na memória persistente D1 e envia menu de desambiguação
  if (env.DB && cleanDigits) {
    try {
      await env.DB.prepare('INSERT OR REPLACE INTO bot_pending_sessions (phone, query, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)').bind(cleanDigits, query).run();
    } catch (e) {
      console.warn('[D1 Pending Session Save Error]', e.message);
    }
  }

  return { needDisambiguation: true, menuText: buildDisambiguationMenu(query, cleanDigits) };
}

/**
 * Gerador Text-to-SQL Estrito por Relatório
 */
async function generateSQL(env, query, userPhone, userScope, targetReport) {
  const norm = query.toLowerCase().trim();

  // Fast-Path 0: Motor Determinístico Centralizado (< 0.05ms)
  const deterministicSql = buildDeterministicAnalyticalSQL(query, targetReport, userScope);
  if (deterministicSql) {
    return deterministicSql;
  }

  // Fast-Path 1: Última safra de FPD / safras disponíveis
  if (targetReport.id === 'FPD' && (/\b(última|ultima|qual\s+a)\s+safra\b/i.test(norm) || /\bsafras?\s+dispon[ií]ve(l|is)\b/i.test(norm))) {
    return `SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1`;
  }

  // Fast-Path 2: Parceiro de pior FPD
  if (targetReport.id === 'FPD' && (/\bparceiro\b/i.test(norm) && /\b(pior|menor|ranking|top)\b/i.test(norm))) {
    return `SELECT safra, entidade_nome, instalacoes, churn_d30, taxa_d30, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 30 ORDER BY safra_ord DESC, taxa_d30 DESC LIMIT 5`;
  }

  // Fast-Path 3: Pior FPD geral (cidade/canal)
  if (targetReport.id === 'FPD' && /\b(pior\s+fpd|maior\s+fpd|ranking|top\s*5|quem\s+tem\s+o\s+pior)\b/i.test(norm) && !/\bparceiro\b/i.test(norm)) {
    return `SELECT safra, cidade, canal, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30, cura, taxa_cura, faixa_risco FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) ORDER BY taxa_fpd60 DESC LIMIT 5`;
  }

  // Fast-Path 4: Última safra de Churn Safra
  if (targetReport.id === 'CHURN_SAFRA' && /\b(última|ultima|qual\s+a)\s+safra\b/i.test(norm)) {
    return `SELECT DISTINCT safra, safra_ord FROM fato_churn_safra ORDER BY safra_ord DESC LIMIT 1`;
  }

  const schemaContext = buildSchemaPromptContext();

  const reportPromptRule = targetReport.id === 'FPD' ? `
- RELATÓRIO OBRIGATÓRIO: FPD (First Payment Default & Qualidade de Venda)
  - SAFRA MAIS RECENTE / ÚLTIMA SAFRA: A ordenação cronológica das safras DEVE ser feita por safra_ord DESC. A última safra oficial de FPD é 'mai/26'. NUNCA use safra DESC pois 'mar/26' vem antes de 'mai/26' alfabeticamente!
  - INDICADOR PADRÃO OFICIAL: FPD 60 (coluna taxa_fpd60). Sempre que o usuário pedir 'FPD', 'pior FPD', 'taxa de FPD', ordene ou selecione taxa_fpd60 DESC. Somente use FPD 30 (coluna taxa_fpd30) se o usuário pedir expressamente 'FPD 30' ou 'onboarding'.
  - SE FOR CONSULTA SOBRE PARCEIRO (ex: 'qual parceiro tem pior FPD', 'ranking de parceiros', 'parceiro CCH Mendes', 'qual o pior parceiro'):
    A tabela fato_fpd NÃO possui parceiro (possui apenas cidade, canal e faixa_risco).
    Portanto, para PARCEIRO, consulte a tabela fato_churn_safra com:
    visao = 'PARCEIRO' AND instalacoes >= 30
    Selecione: safra, entidade_nome, instalacoes, churn_d30, taxa_d30, np120, taxa_np120, status_safra.
    Se for pior parceiro: ordene por taxa_d30 DESC (ou taxa_np120 DESC) com safra_ord DESC LIMIT 5.
  - SE FOR CONSULTA SOBRE CIDADES, CANAIS, FAIXAS DE RISCO OU RANKING GERAL:
    Consulte a tabela fato_fpd selecionando: safra, cidade, canal, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30, cura, taxa_cura, faixa_risco.
    Se for pior FPD, ordene por taxa_fpd60 DESC LIMIT 5.
    Se não especificar safra, use a última safra: safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1).
  - Se a pergunta for "qual a última safra de FPD":
    SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1.
` : targetReport.id === 'CHURN_BL' ? `
- RELATÓRIO OBRIGATÓRIO: Churn Banda Larga
  - Tabela exclusiva: fato_indicadores_mensais.
  - Selecione: segmento, mes_referencia, tipo_visao, cidade, vol_real, vol_orc, rxo_delta, rxo_pct, taxa_real, taxa_orc, taxa_delta_pp.
  - Se o usuário não especificar segmento, use segmento = 'Banda Larga Total'.
  - Se o usuário não especificar mês, use o mês mais recente: mes_referencia = (SELECT MAX(mes_referencia) FROM fato_indicadores_mensais).
` : targetReport.id === 'CHURN_SAFRA' ? `
- RELATÓRIO OBRIGATÓRIO: Churn Safra D120
  - Tabela exclusiva: fato_churn_safra.
  - Selecione: safra, visao, entidade_nome, cidade, instalacoes, churn_d120, taxa_d120, np120, taxa_np120, inadimplencia, fraude, status_safra.
  - Se não especificar safra, utilize a safra madura oficial 'mai/26' ou ordene por safra_ord DESC com LIMIT 1.
` : targetReport.id === 'CREDITO' ? `
- RELATÓRIO OBRIGATÓRIO: Aprovação de Crédito & Antifraude
  - Tabela exclusiva: fato_aprovacao_credito.
  - Selecione: mes_referencia, cidade, canal, pdv_ou_parceiro, consultas, aprovados, taxa_aprovacao, recusas_politica, recusas_antifraude, risco_alto.
  - Se não especificar mês, use mes_referencia = (SELECT MAX(mes_referencia) FROM fato_aprovacao_credito).
` : `
- RELATÓRIO OBRIGATÓRIO: Market Share & Concorrência (Anatel)
  - Tabela exclusiva: fato_market_share.
  - Selecione: mes_referencia, cidade, operadora, acessos, market_share_pct, net_adds, posicao_ranking.
  - Se não especificar mês, use mes_referencia = (SELECT MAX(mes_referencia) FROM fato_market_share).
`;

  const systemInstruction = `Você é um Gerador Especialista de SQL SQLite D1 para Telecomunicações da Claro (Regional Norte).
Sua missão é converter a pergunta em linguagem natural do usuário em uma única consulta SQL SELECT precisa.

DIRETRIZES FUNDAMENTAIS:
1. Responda APENAS o código SQL puro dentro de um bloco \`\`\`sql ou texto puro, sem comentários conversacionais.
2. NUNCA gere instruções destrutivas (UPDATE, DELETE, DROP, INSERT). Apenas SELECT ou WITH...SELECT.
3. Tratamento de Cidades e Nomes: use LIKE '%cidade%' ou COLLATE NOCASE para evitar falhas de maiúsculas/minúsculas.
4. REGRAS OBRIGATÓRIAS DE PADRÃO (DEFAULTS):
   - MÊS/SAFRA PADRÃO: Sempre que o usuário não for específico no mês, selecione o mês mais recente disponível com dados.
   - PRODUTO PADRÃO: Sempre que não for específico em produto, adote Banda Larga (segmento = 'Banda Larga Total' ou familia_produto = 'Dados').
5. REGRAS DO RELATÓRIO SOLICITADO:
${reportPromptRule}

6. SEGURANÇA E CARTEIRIZAÇÃO:
   - O telefone do usuário solicitante é: '${userPhone}'.
   ${(userScope?.permissao_total === 1 || userScope?.cidade === 'TODAS' || userScope?.cidade === 'Regional Norte') ? `
   - Este usuário possui ACESSO TOTAL (Gestor Regional). NUNCA adicione filtros restritivos de carteirização na cláusula WHERE.
   ` : `
   - Usuário com escopo restrito à cidade '${userScope?.cidade}'. Adicione filtro obrigatório: (cidade = '${userScope?.cidade}' OR cidade = 'Regional Norte').
   `}

${schemaContext}`;

  const raw = await callGemini(env, systemInstruction, `Pergunta do Usuário: "${query}"`, 0.0);
  if (!raw) return null;

  const clean = raw.replace(/```sql/gi, '').replace(/```/g, '').trim();
  return clean;
}

/**
 * Formatador Executivo Determinístico Anti-Alucinação
 */
export function formatAnalyticalAnswer(rows, query, targetReport) {
  if (!rows || rows.length === 0) {
    return `⚠️ *${targetReport.title} · Regional Norte*\n\nNão foram encontrados registros na base de dados oficial para os filtros informados nesta consulta.\n\n_Para preservar a integridade da análise, nenhum dado de outro indicador foi exibido._`;
  }

  const first = rows[0];

  const hasKpiMetrics = (
    first.total_instalacoes !== undefined ||
    first.instalacoes !== undefined ||
    first.taxa_fpd60_regional !== undefined ||
    first.taxa_fpd30_regional !== undefined ||
    first.taxa_fpd60_consolidada !== undefined ||
    first.taxa_fpd60 !== undefined ||
    first.taxa_fpd30 !== undefined ||
    first.total_fpd60 !== undefined ||
    first.total_fpd30 !== undefined ||
    first.taxa_d30 !== undefined ||
    first.taxa_d120 !== undefined ||
    first.taxa_np120 !== undefined ||
    first.taxa_real !== undefined ||
    first.vol_real !== undefined ||
    first.taxa_aprovacao !== undefined ||
    first.taxa_aprovacao_regional !== undefined ||
    first.taxa_aprovacao_consolidada !== undefined ||
    first.market_share_pct !== undefined ||
    first.total_acessos !== undefined
  );

  // Caso especial: Pergunta sobre data/período (1 linha contendo apenas safra ou mes_referencia sem métricas de KPI)
  if (rows.length === 1 && !hasKpiMetrics && (first.safra || first.mes_referencia) && first.cidade === undefined && first.entidade_nome === undefined && first.canal === undefined) {
    const periodo = first.safra || first.mes_referencia;
    return `${targetReport.icon} *${targetReport.title} · Regional Norte*\n\n📅 A safra mais recente com dados consolidados de ${targetReport.name} é *${periodo}*.`;
  }

  // 1. Relatório FPD
  if (targetReport.id === 'FPD') {
    // Se retornou parceiros de fato_churn_safra
    if (first.entidade_nome || first.churn_d30 !== undefined || first.taxa_d30 !== undefined) {
      if (rows.length === 1) {
        const taxaD30 = first.taxa_d30 !== undefined ? Number(first.taxa_d30).toFixed(2) : '0.00';
        const taxaNp120 = first.taxa_np120 !== undefined ? Number(first.taxa_np120).toFixed(2) : '0.00';
        const instalacoes = first.instalacoes || 0;
        const churnD30 = first.churn_d30 || 0;
        const np120 = first.np120 || 0;
        const status = first.status_safra || 'EM_ABERTO';

        return `💳 *Relatório Oficial de FPD (First Payment Default) · Regional Norte*

• *Parceiro:* ${first.entidade_nome || 'Parceiro Comercial'}
• *Safra Consultada:* *${first.safra || 'Recente'}* (${status === 'MADURA' ? 'Safra Madura' : 'Em Acompanhamento'})
• *Instalações da Safra:* *${instalacoes}* contratos

📊 *Indicadores de Primeiro Pagamento:*
• *FPD 30 (Taxa D30):* *${taxaD30}%* (${churnD30} cancelamento(s) nos primeiros 30 dias)
• *Não Pagos D120 (NP120):* *${taxaNp120}%* (${np120} contrato(s) sem pagamento)

ℹ️ *Nota de Conformidade:*
O relatório analítico de FPD detalhado por faixas de risco e cura de 60 dias é consolidado por Cidade e Canal. Para parceiros de venda comerciais, o indicador oficial de 1º pagamento é apurado através do *FPD 30 (Taxa D30)* e perdas por *NP120*.`;
      }

      // Ranking de múltiplos parceiros
      let out = `💳 *Ranking Oficial de Parceiros · FPD 30 & Sobrevivência (Regional Norte)*\n\n`;
      for (const r of rows.slice(0, 5)) {
        const ent = r.entidade_nome || 'Parceiro';
        const safra = r.safra ? ` (${r.safra})` : '';
        const d30 = r.taxa_d30 !== undefined ? `FPD 30: *${Number(r.taxa_d30).toFixed(2)}%*` : '';
        const np = r.taxa_np120 !== undefined ? `NP120: *${Number(r.taxa_np120).toFixed(2)}%*` : '';
        const inst = r.instalacoes ? `(${r.instalacoes} inst)` : '';
        out += `• *${ent}*${safra}: ${[d30, np, inst].filter(Boolean).join(' | ')}\n`;
      }
      out += `\n_Critério: volume mínimo ≥ 30 instalações na safra._`;
      return out;
    }

    // Se for ranking consolidado por cidade (taxa_fpd60_consolidada)
    if (first.taxa_fpd60_consolidada !== undefined) {
      let out = `💳 *Ranking Oficial de Cidades · FPD 60 (Regional Norte)*\n\n`;
      for (const r of rows.slice(0, 5)) {
        const cid = r.cidade ? `*${r.cidade}*` : 'Cidade';
        const taxa = r.taxa_fpd60_consolidada !== undefined ? `FPD 60: *${Number(r.taxa_fpd60_consolidada).toFixed(1)}%*` : '';
        const fpd60 = r.total_fpd60 !== undefined ? `(${r.total_fpd60} contratos)` : '';
        const inst = r.total_instalacoes !== undefined ? `em ${r.total_instalacoes} inst` : '';
        out += `• ${cid}: ${[taxa, fpd60, inst].filter(Boolean).join(' ')}\n`;
      }
      out += `\n_Critério: volume mínimo ≥ 50 instalações na safra._`;
      return out;
    }

    // Se for ranking por produto (familia_produto)
    if (first.familia_produto !== undefined) {
      let out = `🏷️ *Ranking Oficial por Produto · FPD 60 (Regional Norte)*\n\n`;
      for (const r of rows) {
        const prod = r.familia_produto || 'Produto';
        const taxa = r.taxa_fpd60 !== undefined ? `FPD 60: *${Number(r.taxa_fpd60).toFixed(1)}%*` : '';
        const fpd60 = r.total_fpd60 !== undefined ? `(${r.total_fpd60} contratos)` : '';
        const inst = r.total_instalacoes ? `em ${Number(r.total_instalacoes).toLocaleString('pt-BR')} inst` : '';
        out += `• *${prod}*: ${[taxa, fpd60, inst].filter(Boolean).join(' ')}\n`;
      }
      return out;
    }

    // Se for ranking por canal de vendas / vendedor (canal sem cidade)
    if (first.canal !== undefined && first.cidade === undefined && first.entidade_nome === undefined) {
      let out = `💼 *Ranking Oficial por Canal de Venda · FPD 60 (Regional Norte)*\n\n`;
      for (const r of rows) {
        const can = r.canal || 'Canal';
        const taxa = r.taxa_fpd60 !== undefined ? `FPD 60: *${Number(r.taxa_fpd60).toFixed(1)}%*` : '';
        const fpd60 = r.total_fpd60 !== undefined ? `(${r.total_fpd60} contratos)` : '';
        const inst = r.total_instalacoes ? `em ${Number(r.total_instalacoes).toLocaleString('pt-BR')} inst` : '';
        out += `• *${can}*: ${[taxa, fpd60, inst].filter(Boolean).join(' ')}\n`;
      }
      out += `\n_Nota: Em conformidade com a governança executiva, o ranking comercial é apurado no nível de Canal / PDV._`;
      return out;
    }

    // Se for resumo regional consolidado (sem cidade/canal mas com métricas de agregação de FPD)
    if ((first.taxa_fpd60_regional !== undefined || first.total_fpd60 !== undefined || first.taxa_fpd30_regional !== undefined) && !first.cidade) {
      let out = `💳 *Relatório Oficial de FPD (First Payment Default) · Regional Norte*\n\n`;
      if (first.safra) out += `📅 *Safra de Referência:* *${first.safra}*\n`;
      const inst = first.total_instalacoes !== undefined ? Number(first.total_instalacoes).toLocaleString('pt-BR') : '0';
      const fpd60 = first.taxa_fpd60_regional !== undefined ? Number(first.taxa_fpd60_regional).toFixed(1) : '0.0';
      const fpd30 = first.taxa_fpd30_regional !== undefined ? Number(first.taxa_fpd30_regional).toFixed(1) : '0.0';
      const cura = first.taxa_cura_regional !== undefined ? Number(first.taxa_cura_regional).toFixed(1) : '0.0';
      out += `📦 *Total de Instalações:* *${inst}* contratos\n\n`;
      out += `📊 *Indicadores Regionais Consolidados:*\n`;
      out += `• *FPD 60 Oficial (Inadimplência 60d):* *${fpd60}%* (${first.total_fpd60 || 0} contratos)\n`;
      out += `• *FPD 30 (Onboarding 30d):* *${fpd30}%* (${first.total_fpd30 || 0} contratos)\n`;
      out += `• *Taxa de Cura (30d ➔ 60d):* *${cura}%* (${first.total_cura || 0} contratos recuperados)\n\n`;
      out += `ℹ️ *Nota Oficial:* O FPD 60 é o indicador oficial corporativo da Claro para qualidade de venda da Regional Norte.`;
      return out;
    }

    let out = `💳 *Relatório Oficial de FPD (First Payment Default) · Regional Norte*\n`;
    if (first.safra) out += `📅 *Safra de Referência:* *${first.safra}*\n\n`;

    for (const r of rows.slice(0, 10)) {
      const cid = r.cidade ? `*${r.cidade}*` : '';
      const canal = r.canal ? ` [${r.canal}]` : '';
      const risco = r.faixa_risco ? ` (Risco: *${r.faixa_risco}*)` : '';
      const fpd60 = r.taxa_fpd60 !== undefined ? `FPD60 Oficial: *${Number(r.taxa_fpd60).toFixed(1)}%*` : '';
      const fpd30 = r.taxa_fpd30 !== undefined ? `FPD30: *${Number(r.taxa_fpd30).toFixed(1)}%*` : '';
      const cura = r.taxa_cura !== undefined ? `Cura: *${Number(r.taxa_cura).toFixed(1)}%*` : '';
      const inst = r.instalacoes ? ` (${r.instalacoes} inst)` : '';
      out += `• ${cid}${canal}${risco}: ${[fpd60, fpd30, cura].filter(Boolean).join(' | ')}${inst}\n`;
    }
    return out;
  }

  // 2. Relatório Churn Banda Larga
  if (targetReport.id === 'CHURN_BL') {
    // Se for ranking por produto/segmento
    if (first.segmento && first.cidade === undefined) {
      let out = `🏷️ *Ranking Oficial por Segmento · Churn Banda Larga (Regional Norte)*\n\n`;
      for (const r of rows) {
        const seg = r.segmento || 'Segmento';
        const taxa = r.taxa_real !== undefined ? `Taxa: *${Number(r.taxa_real).toFixed(2)}%*` : '';
        const meta = r.taxa_orc !== undefined ? `(Meta: ${Number(r.taxa_orc).toFixed(2)}%)` : '';
        const vol = r.vol_real !== undefined ? `(Vol: ${r.vol_real})` : '';
        out += `• *${seg}*: ${[taxa, meta, vol].filter(Boolean).join(' ')}\n`;
      }
      return out;
    }
    // Se for ranking por motivo/visão
    if (first.tipo_visao && first.cidade === undefined) {
      let out = `📉 *Ranking Oficial por Motivo / Visão · Churn Banda Larga (Regional Norte)*\n\n`;
      for (const r of rows) {
        const vis = r.tipo_visao || 'Visão';
        const taxa = r.taxa_real !== undefined ? `Taxa: *${Number(r.taxa_real).toFixed(2)}%*` : '';
        const vol = r.vol_real !== undefined ? `(Vol: ${r.vol_real})` : '';
        out += `• *${vis}*: ${[taxa, vol].filter(Boolean).join(' ')}\n`;
      }
      return out;
    }

    let out = `📉 *Relatório Oficial de Churn Banda Larga · Regional Norte*\n\n`;
    for (const r of rows.slice(0, 10)) {
      const cid = r.cidade ? `*${r.cidade}*` : '';
      const seg = r.segmento ? ` (${r.segmento})` : '';
      const visao = r.tipo_visao && r.tipo_visao !== 'TOTAL' ? ` [${r.tipo_visao}]` : '';
      const mes = r.mes_referencia ? ` [${r.mes_referencia}]` : '';
      const taxa = r.taxa_real !== undefined ? `Taxa: *${Number(r.taxa_real).toFixed(2)}%*` : '';
      const meta = r.taxa_orc !== undefined ? ` (Meta: ${Number(r.taxa_orc).toFixed(2)}%)` : '';
      const vol = r.vol_real !== undefined ? `Vol: *${r.vol_real}*` : '';
      const rxo = r.rxo_delta !== undefined ? ` (RxO: ${r.rxo_delta > 0 ? '+' : ''}${r.rxo_delta})` : '';
      out += `• ${cid}${seg}${visao}${mes}: ${[taxa + meta, vol + rxo].filter(Boolean).join(' | ')}\n`;
    }
    return out;
  }

  // 3. Relatório Churn Safra D120
  if (targetReport.id === 'CHURN_SAFRA') {
    let out = `🌱 *Relatório Oficial de Churn Safra D120 · Regional Norte*\n\n`;
    for (const r of rows.slice(0, 10)) {
      const ent = r.entidade_nome ? `*${r.entidade_nome}*` : (r.cidade ? `*${r.cidade}*` : '');
      const safra = r.safra ? ` [${r.safra}]` : '';
      const status = r.status_safra ? ` (${r.status_safra})` : '';
      const inst = r.instalacoes ? `Instalações: *${r.instalacoes}*` : '';
      const d120 = r.taxa_d120 !== undefined ? `D120: *${Number(r.taxa_d120).toFixed(2)}%*` : '';
      const np120 = r.taxa_np120 !== undefined ? `NP120: *${Number(r.taxa_np120).toFixed(2)}%*` : '';
      out += `• ${ent}${safra}${status}: ${[inst, d120, np120].filter(Boolean).join(' | ')}\n`;
    }
    return out;
  }

  // 4. Relatório Aprovação de Crédito
  if (targetReport.id === 'CREDITO') {
    if (first.taxa_aprovacao_regional !== undefined) {
      const totalCons = first.total_consultas !== undefined ? Number(first.total_consultas).toLocaleString('pt-BR') : '0';
      const totalAprov = first.total_aprovados !== undefined ? Number(first.total_aprovados).toLocaleString('pt-BR') : '0';
      const taxa = first.taxa_aprovacao_regional !== undefined ? Number(first.taxa_aprovacao_regional).toFixed(1) : '0.0';
      const fraudes = first.total_recusas_antifraude || 0;
      const risco = first.total_risco_alto || 0;
      return `🛡️ *Relatório Oficial de Aprovação de Crédito & Antifraude · Regional Norte*\n\n📅 *Mês de Referência:* *${first.mes_referencia || 'Recente'}*\n📋 *Consultas Totais:* *${totalCons}* propostas\n✅ *Aprovados:* *${totalAprov}* (*${taxa}%* de aprovação regional)\n🚫 *Recusas Antifraude:* *${fraudes}*\n⚠️ *Propostas de Alto Risco:* *${risco}*`;
    }
    if (first.taxa_aprovacao_consolidada !== undefined) {
      let out = `🛡️ *Ranking Oficial de Aprovação de Crédito por Cidade · Regional Norte*\n\n`;
      for (const r of rows.slice(0, 5)) {
        const cid = r.cidade ? `*${r.cidade}*` : 'Cidade';
        const taxa = r.taxa_aprovacao_consolidada !== undefined ? `Aprovação: *${Number(r.taxa_aprovacao_consolidada).toFixed(1)}%*` : '';
        const cons = r.total_consultas ? `(${r.total_consultas} consultas)` : '';
        out += `• ${cid}: ${[taxa, cons].filter(Boolean).join(' ')}\n`;
      }
      return out;
    }
    let out = `🛡️ *Relatório Oficial de Aprovação de Crédito & Antifraude · Regional Norte*\n\n`;
    for (const r of rows.slice(0, 10)) {
      const ent = r.pdv_ou_parceiro ? `*${r.pdv_ou_parceiro}*` : (r.cidade ? `*${r.cidade}*` : '');
      const canal = r.canal ? ` [${r.canal}]` : '';
      const mes = r.mes_referencia ? ` (${r.mes_referencia})` : '';
      const aprov = r.taxa_aprovacao !== undefined ? `Aprovação: *${Number(r.taxa_aprovacao).toFixed(1)}%*` : '';
      const fraude = r.recusas_antifraude !== undefined ? `Fraudes: *${r.recusas_antifraude}*` : '';
      const risco = r.risco_alto !== undefined ? `Alto Risco: *${r.risco_alto}*` : '';
      out += `• ${ent}${canal}${mes}: ${[aprov, fraude, risco].filter(Boolean).join(' | ')}\n`;
    }
    return out;
  }

  // 5. Relatório Market Share
  if (targetReport.id === 'MARKET_SHARE') {
    let out = `📊 *Relatório Oficial de Market Share & Anatel · Regional Norte*\n\n`;
    for (const r of rows.slice(0, 10)) {
      const cid = r.cidade ? `*${r.cidade}*` : '';
      const op = r.operadora ? `*${r.operadora}*` : '';
      const share = r.market_share_pct !== undefined ? `Share: *${Number(r.market_share_pct).toFixed(1)}%*` : '';
      const totalAc = r.acessos || r.total_acessos;
      const acessos = totalAc ? `Acessos: *${Number(totalAc).toLocaleString('pt-BR')}*` : '';
      const totalNet = r.net_adds !== undefined ? r.net_adds : r.total_net_adds;
      const net = totalNet !== undefined ? `Net Adds: *${totalNet > 0 ? '+' : ''}${totalNet}*` : '';
      const rank = r.posicao_ranking ? `#${r.posicao_ranking}` : '';
      const header = [cid, op, rank].filter(Boolean).join(' ');
      out += `• ${header}: ${[share, acessos, net].filter(Boolean).join(' | ')}\n`;
    }
    return out;
  }

  return formatRowsFallback(rows);
}

/**
 * Execução Text-to-SQL Segura no D1 com Escopo Rígido de Relatório
 */
async function executeAnalyticalPipeline(env, query, userPhone, userScope, targetReport) {
  // 1. Gera SQL a partir da intenção com diretrizes específicas do relatório
  const generatedSql = await generateSQL(env, query, userPhone, userScope, targetReport);
  if (!generatedSql) {
    return {
      success: false,
      answer: `⚠️ Não consegui estruturar a consulta analítica para o relatório de *${targetReport.name}*. Por favor, especifique os filtros desejados (ex: cidade, período ou parceiro).`,
    };
  }

  // 2. Valida segurança do SQL
  const validation = validateSafeSQL(generatedSql);
  if (!validation.safe) {
    console.warn(`[SQL Rejeitado por Segurança] ${validation.reason} | SQL: ${generatedSql}`);
    return {
      success: false,
      answer: "⚠️ A consulta gerada contém parâmetros ou comandos não permitidos pelas regras de segurança corporativa.",
      debug: { generatedSql, reason: validation.reason }
    };
  }

  const safeSql = validation.sql;

  // 3. Executa no D1 Database
  let dbRows = [];
  try {
    if (env.DB) {
      const stmt = env.DB.prepare(safeSql);
      const res = await stmt.all();
      dbRows = res?.results || [];
    } else {
      console.warn('[D1 Binding] env.DB não disponível no ambiente');
    }
  } catch (err) {
    console.error('[D1 Execution Error]', err, 'SQL:', safeSql);
    return {
      success: false,
      answer: `⚠️ Ocorreu um erro ao consultar o ${targetReport.title} no D1. Verifique se os parâmetros informados constam na base.`,
      debug: { error: err.message, safeSql }
    };
  }

  // 4. Formata a resposta com garantia anti-alucinação e fidelidade ao relatório
  const answer = formatAnalyticalAnswer(dbRows, query, targetReport);

  return {
    success: true,
    sql: safeSql,
    answer,
    rowsCount: dbRows.length,
    targetReport: targetReport.id,
  };
}

/**
 * Formatação Fallback de Linhas do Banco caso o LLM oscile
 */
function formatRowsFallback(rows) {
  let out = "📊 *Regional Norte · Resultados Oficiais*\n\n";
  const sample = rows.slice(0, 5);
  for (const r of sample) {
    const keys = Object.keys(r).filter(k => k !== 'id' && k !== 'user_context');
    const items = keys.map(k => `${k}: *${r[k]}*`).join(' | ');
    out += `• ${items}\n`;
  }
  if (rows.length > 5) {
    out += `\n_...e mais ${rows.length - 5} registros encontrados._\n`;
  }
  return out;
}

// Stopwords em Português para extração semântica limpa
const PT_STOPWORDS = new Set([
  'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
  'em', 'no', 'na', 'nos', 'nas', 'por', 'pelo', 'pela', 'pelos', 'pelas', 'para',
  'com', 'como', 'que', 'qual', 'quais', 'quem', 'onde', 'quando', 'sobre', 'entre',
  'e', 'ou', 'se', 'mas', 'mais', 'menos', 'muito', 'muita', 'bem', 'bom', 'boa',
  'meu', 'sua', 'seu', 'suas', 'seus', 'este', 'esta', 'esse', 'essa', 'isso', 'isto',
  'significa', 'significado', 'conceito', 'definicao', 'definição', 'regra', 'regras',
  'formula', 'fórmula', 'calcula', 'calcular', 'calculo', 'cálculo', 'funciona', 'funcionar'
]);

/**
 * Formata Resposta Corporativa de Glossário com Padrão Executivo Oficial
 */
export function formatCorporateGlossaryDirect(chunks, query) {
  if (!chunks || chunks.length === 0) return null;

  const primary = chunks[0];
  let out = `💡 *Regional Norte · Glossário & Regras de Negócio*\n\n`;
  out += `*${primary.topico}*\n`;
  out += `${primary.conteudo}\n\n`;

  if (primary.regras_calculo) {
    out += `*Regra Oficial / Fórmula de Cálculo:*\n`;
    out += `• \`${primary.regras_calculo}\`\n\n`;
  }

  // Chunks correlacionados adicionais (ex: FPD 30 vs 60, Cura, Faixas de Risco)
  const related = chunks.slice(1, 4);
  if (related.length > 0) {
    out += `*Conceitos e Marcos Associados:*\n`;
    for (const r of related) {
      out += `• *${r.topico}:* ${r.conteudo}\n`;
      if (r.regras_calculo) {
        out += `  _Fórmula:_ \`${r.regras_calculo}\`\n`;
      }
    }
    out += `\n`;
  }

  out += `────────────────────────────\n`;
  out += `*Ações Rápidas:*\n`;
  out += `• Envie *#dados* para consultar indicadores operacionais em tempo real.\n`;
  out += `• Envie *#ajuda* para o catálogo completo de comandos e métricas.`;
  return out;
}

/**
 * Execução Semantic RAG (Perguntas Conceituais e Regras de Negócio)
 * Otimizado com Fast-Retrieval no D1 (< 25ms) e Fallback Gemini Inteligente
 */
async function executeConceptualPipeline(env, query) {
  let chunks = [];

  // 1. Extração de palavras-chave limpas (sem ruído de stopwords)
  const cleanTokens = query
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(w => !PT_STOPWORDS.has(w) && w.length >= 2);

  // 2. Busca de chunks relevantes no Cloudflare D1
  if (env.DB) {
    try {
      let sql = `SELECT modulo, topico, conteudo, regras_calculo, palavras_chave FROM bot_knowledge_chunks`;
      let params = [];

      if (cleanTokens.length > 0) {
        const likeClauses = cleanTokens.map(() => `(topico LIKE ? OR palavras_chave LIKE ? OR conteudo LIKE ?)`).join(' OR ');
        sql += ` WHERE ${likeClauses} ORDER BY CASE WHEN topico LIKE ? THEN 1 WHEN palavras_chave LIKE ? THEN 2 ELSE 3 END LIMIT 4`;
        for (const token of cleanTokens) {
          const p = `%${token}%`;
          params.push(p, p, p);
        }
        // Para a ordenação prioritária
        params.push(`%${cleanTokens[0]}%`, `%${cleanTokens[0]}%`);
      } else {
        sql += ` LIMIT 4`;
      }

      const stmt = env.DB.prepare(sql);
      const res = await (params.length > 0 ? stmt.bind(...params).all() : stmt.all());
      chunks = res?.results || [];
    } catch (err) {
      console.error('[RAG D1 Error]', err);
    }
  }

  // 3. Chunks estáticos de contingência corporativa
  if (chunks.length === 0) {
    const qLower = query.toLowerCase();
    if (qLower.includes('fpd') || qLower.includes('first payment')) {
      chunks = [
        {
          modulo: 'fpd',
          topico: 'Conceito e Definição de FPD (First Payment Default)',
          conteudo: 'O FPD (First Payment Default ou Inadimplência de Primeiro Pagamento) mede a qualidade da venda nos primeiros 60 dias da instalação do contrato. Ele avalia se o cliente quitou a primeira fatura (pró-rata) e a fatura cheia subsequente.',
          regras_calculo: 'Total de clientes que não pagaram / Total de instalações da safra'
        },
        {
          modulo: 'fpd',
          topico: 'Diferença entre FPD 30 e FPD 60',
          conteudo: 'O FPD 30 avalia a inadimplência da primeira fatura (pró-rata) até 30 dias após o vencimento (AGING30 = 1). O FPD 60 avalia a inadimplência cumulativa até 60 dias (AGING60 = 1). Um contrato que atrasa aos 30 dias mas quita antes dos 60 dias é considerado "Curado" e não vira FPD 60 efetivo.',
          regras_calculo: 'FPD 30: AGING30 == 1 | FPD 60 Efetivo: AGING30 == 1 AND AGING60 == 1'
        },
        {
          modulo: 'fpd',
          topico: 'Conceito de Cura do FPD',
          conteudo: 'A Cura ocorre quando o cliente atrasou a fatura pró-rata inicial de 30 dias (AGING30 = 1), porém efetuou o pagamento antes do marco de 60 dias (AGING60 = 0). Representa a recuperação de inadimplência da safra pela ação de régua de cobrança.',
          regras_calculo: 'Cura = (AGING30 == 1 AND AGING60 == 0) / Total Inadimplente em 30 dias'
        }
      ];
    } else {
      chunks = [
        {
          modulo: 'churn-safra',
          topico: 'Regra Oficial de Churn Safra D120',
          conteudo: 'A Safra D120 mede a sobrevivência e cancelamento dos contratos no período de observação de 120 dias da instalação. É a métrica de estorno e remuneração de parceiros. Uma safra só é considerada "Madura" após 110 a 120 dias do mês de venda.',
          regras_calculo: 'Churn Safra D120 (%) = Cancelamentos acumulados até D120 / Instalações da Safra * 100'
        },
        {
          modulo: 'churn-bl-total',
          topico: 'Diferença entre Churn Voluntário e Involuntário',
          conteudo: 'Churn Voluntário é quando o próprio cliente solicita a desconexão (motivos como preço, concorrência, mudança de endereço). Churn Involuntário é quando a Claro cancela o contrato compulsoriamente por inadimplência após os ciclos de corte.'
        },
        {
          modulo: 'geral',
          topico: 'Conceito de RxO (Realizado x Orçado)',
          conteudo: 'RxO mede a variação entre o resultado realizado e a meta orçada da companhia. RxO Delta = Realizado - Orçado. Para churn e desconexão, números abaixo do orçado são favoráveis (delta negativo).'
        }
      ];
    }
  }

  // 4. Se recuperamos chunks pertinentes, formata instantaneamente (< 25ms, Zero LLM Round-Trip)
  if (chunks.length > 0) {
    const directAnswer = formatCorporateGlossaryDirect(chunks, query);
    if (directAnswer) {
      return {
        success: true,
        answer: directAnswer,
        chunksUsed: chunks.length,
        fastPath: true,
      };
    }
  }

  // 5. Fallback com síntese generativa via Gemini (Apenas se não houver chunk estruturado)
  const systemInstruction = `Você é o Consultor Especialista de Regras de Negócio da Claro Regional Norte (Pephub).
Responda à dúvida conceitual do usuário utilizando EXCLUSIVAMENTE o contexto das Regras Oficiais fornecidas abaixo.

DIRETRIZES:
1. Explique de forma didática, clara e objetiva para WhatsApp.
2. Utilize *negrito* nos termos técnicos e siglas (ex: *FPD*, *D120*, *NP120*, *Aging*).
3. Se houver fórmula de cálculo associada, apresente-a claramente em destaque.
4. Cabeçalho: 💡 *Regional Norte · Glossário & Regras de Negócio*
5. Máximo de 150 a 180 palavras.`;

  const contextText = chunks.map((c, i) => `[Documento ${i + 1}] (${c.modulo} - ${c.topico}):\n${c.conteudo}\n${c.regras_calculo ? `Fórmula: ${c.regras_calculo}` : ''}`).join('\n\n');
  const prompt = `Contexto Oficial:\n${contextText}\n\nDúvida do Usuário: "${query}"`;

  const synthesized = await callGemini(env, systemInstruction, prompt, 0.1);
  return {
    success: true,
    answer: synthesized || `💡 *Regional Norte · Regras de Negócio*\n\n${chunks[0].conteudo}`,
    chunksUsed: chunks.length,
    fastPath: false,
  };
}

/**
 * Resposta para consultas Fora de Escopo e Catálogo Oficial
 */
function handleOutOfScopeQuery(phone = '5591980547171') {
  return {
    success: true,
    answer: buildBaseSelectionMenu(phone)
  };
}

/**
 * Pipeline Central do Roteador (Ask Handler)
 */
export async function processBotQuery(env, phone, query) {
  if (!query || !query.trim()) {
    return {
      success: true,
      answer: buildBaseSelectionMenu(phone),
      intent: 'MENU_PASSO_1',
      phone
    };
  }

  // 1. Validação de Autorização e Escopo
  const auth = await verifyBotSender(env, phone);
  if (!auth.allowed) {
    if (auth.reason === 'suspended') {
      return {
        success: false,
        unauthorized: true,
        answer: "Regional Norte · Pephub Data Bot\n\n*Ambiente Temporariamente Indisponível*\nO bot corporativo de dados está temporariamente suspenso pela administração da Regional Norte para consolidação de bases e manutenção.\n\nAcesse o portal corporativo: https://pephub.cloud/"
      };
    }

    return {
      success: false,
      unauthorized: true,
      answer: `Regional Norte · Pephub Data Bot\n\n*Acesso Restrito:* O seu número (${phone}) não consta como cadastrado e aprovado na plataforma corporativa Pephub.\n\nPara ter acesso às consultas de churn, indicadores e bases operacionais da Regional Norte, realize seu cadastro corporativo no portal:\nhttps://pephub.cloud/login/\n\nApós a validação e homologação pelo gestor, seu acesso via WhatsApp será liberado automaticamente.`
    };
  }

  const cleanQuery = (query || '').replace(/^(#\?|＃\?)\s*/, '').trim();
  const cleanDigits = String(phone || '').replace(/\D/g, '');
  const norm = cleanQuery.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  // 1.2. COMANDOS DE MENU / REINÍCIO DO FLUXO (menu, inicio, bases, ajuda)
  if (/^(menu|inicio|início|retornar|bases|ajuda|help)$/i.test(norm) || cleanQuery === '') {
    if (env.DB && cleanDigits) {
      try {
        await env.DB.prepare('DELETE FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).run();
      } catch (_) {}
    }
    return {
      success: true,
      answer: buildBaseSelectionMenu(phone),
      intent: 'MENU_PASSO_1',
      phone
    };
  }

  // 1.3. VERIFICAÇÃO DE SESSÃO ATIVA NO D1
  let activeSession = null;
  if (env.DB && cleanDigits) {
    try {
      const row = await env.DB.prepare('SELECT query FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).first();
      if (row && row.query) {
        try {
          activeSession = JSON.parse(row.query);
        } catch (_) {}
      }
    } catch (e) {
      console.warn('[D1 Session Lookup Error]', e.message);
    }
  }

  // Helper para salvar sessão
  const saveSession = async (state) => {
    if (env.DB && cleanDigits) {
      try {
        await env.DB.prepare('INSERT OR REPLACE INTO bot_pending_sessions (phone, query, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)')
          .bind(cleanDigits, JSON.stringify(state))
          .run();
      } catch (err) {
        console.warn('[D1 Save Session Error]', err.message);
      }
    }
  };

  // Helper para limpar sessão
  const clearSession = async () => {
    if (env.DB && cleanDigits) {
      try {
        await env.DB.prepare('DELETE FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).run();
      } catch (_) {}
    }
  };

  // 1.4. COMANDO DE VOLTAR (0 ou voltar)
  if (norm === '0' || norm === 'voltar') {
    if (!activeSession || !activeSession.menu || activeSession.menu === 'SELECT_BASE') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
    }

    const rep = getReportById(activeSession.reportId);

    if (activeSession.menu === 'LIST_PARCEIRO_CANAL') {
      const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
      await saveSession(updated);
      return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_PARCEIRO_CANAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_PARCEIRO_CIDADE') {
      if (activeSession.selectedChannel && activeSession.selectedChannel !== 'TODOS') {
        const updated = { ...activeSession, menu: 'LIST_PARCEIRO_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildChannelListMenu(rep, updated, phone), intent: 'MENU', phone };
      } else {
        const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
    if (activeSession.menu === 'LIST_PARCEIRO_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CIDADE' };
      await saveSession(updated);
      return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, `Ranking 10 Piores Parceiros (${activeSession.selectedChannel || 'Geral'})`), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_CANAL_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_CANAL_CIDADE' };
      await saveSession(updated);
      return { success: true, answer: buildChannelCityPromptMenu(rep, updated, phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_CANAL_CIDADE') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_CIDADE_CANAL') {
      const updated = { ...activeSession, menu: 'PROMPT_CIDADE_CANAL' };
      await saveSession(updated);
      return { success: true, answer: buildCityChannelPromptMenu(rep, updated, phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_CIDADE_CANAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MKT_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_MKT_RESIDENCIAL' };
      await saveSession(updated);
      return { success: true, answer: buildCityPromptMenu(rep, updated, phone, 'Market Share Residencial'), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MKT_RESIDENCIAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MKT_DDD') {
      const updated = { ...activeSession, menu: 'PROMPT_MKT_MOVEL' };
      await saveSession(updated);
      return { success: true, answer: buildDddPromptMenu(rep, updated, phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MKT_MOVEL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_SPEECH_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_SPEECH_ABRANGENCIA' };
      await saveSession(updated);
      return { success: true, answer: buildSpeechPromptMenu(phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_SPEECH_ABRANGENCIA') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MOTIVOS_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_MOTIVOS_ABRANGENCIA' };
      await saveSession(updated);
      return { success: true, answer: buildMotivosPromptMenu(phone), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'SELECT_ACTION') {
      if (rep.id === 'FPD' || rep.id === 'CREDITO') {
        const updated = { ...activeSession, menu: 'SELECT_PRODUCT' };
        await saveSession(updated);
        return { success: true, answer: buildProductSelectionMenu(rep, phone), intent: 'MENU', phone };
      }
      if (rep.id === 'CHURN_BL') {
        const updated = { ...activeSession, menu: 'SELECT_SEGMENT' };
        await saveSession(updated);
        return { success: true, answer: buildSegmentSelectionMenu(rep, phone), intent: 'MENU', phone };
      }
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'SELECT_PRODUCT' || activeSession.menu === 'SELECT_SEGMENT') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
    }

    await clearSession();
    return { success: true, answer: buildBaseSelectionMenu(phone), intent: 'MENU', phone };
  }

  // 1.5. NAVEGAÇÃO DOS SUBMENUS E AÇÕES ANALÍTICAS

  // A) SE ESTÁ NO MENU: LIST_PARCEIRO_CANAL (1 a 4)
  if (activeSession && activeSession.menu === 'LIST_PARCEIRO_CANAL') {
    const chMatch = norm.match(/^([1-4])$/);
    if (chMatch) {
      const idx = parseInt(chMatch[1], 10) - 1;
      const ch = OFFICIAL_CHANNELS[idx];
      if (ch) {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CIDADE', selectedChannel: ch.name };
        await saveSession(updated);
        return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, `Ranking 10 Piores Parceiros (${ch.name})`), intent: 'MENU', phone };
      }
    }
  }

  // B) SE ESTÁ NO MENU: PROMPT_PARCEIRO_CANAL (1: Selecionar Canal, 2: Todos os Canais)
  if (activeSession && activeSession.menu === 'PROMPT_PARCEIRO_CANAL') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        const updated = { ...activeSession, menu: 'LIST_PARCEIRO_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildChannelListMenu(rep, updated, phone), intent: 'MENU', phone };
      } else {
        const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CIDADE', selectedChannel: 'TODOS' };
        await saveSession(updated);
        return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, 'Ranking 10 Piores Parceiros (Todos os Canais)'), intent: 'MENU', phone };
      }
    }
  }

  // C) SE ESTÁ NO MENU: PROMPT_PARCEIRO_CIDADE (1: Selecionar Cidade, 2: Todas as Cidades)
  if (activeSession && activeSession.menu === 'PROMPT_PARCEIRO_CIDADE') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        const updated = { ...activeSession, menu: 'LIST_PARCEIRO_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone), intent: 'MENU', phone };
      } else {
        let card = await executePartnerRankingCard(env, rep, { ...activeSession, selectedCity: 'TODAS' });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // D) SE ESTÁ NO MENU: LIST_PARCEIRO_CIDADE (1 a 14)
  if (activeSession && activeSession.menu === 'LIST_PARCEIRO_CIDADE') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const city = OFFICIAL_14_CITIES[idx];
      if (city) {
        const rep = getReportById(activeSession.reportId);
        let card = await executePartnerRankingCard(env, rep, { ...activeSession, selectedCity: city.name });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // E) SE ESTÁ NO MENU: PROMPT_CANAL_CIDADE (Ranking Canais: 1: Todas, 2: Selecionar)
  if (activeSession && activeSession.menu === 'PROMPT_CANAL_CIDADE') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        let card = await executeChannelRankingCard(env, rep, { ...activeSession, selectedCity: 'TODAS' });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_CANAL_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // F) SE ESTÁ NO MENU: LIST_CANAL_CIDADE (1 a 14)
  if (activeSession && activeSession.menu === 'LIST_CANAL_CIDADE') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const city = OFFICIAL_14_CITIES[idx];
      if (city) {
        const rep = getReportById(activeSession.reportId);
        let card = await executeChannelRankingCard(env, rep, { ...activeSession, selectedCity: city.name });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // G) SE ESTÁ NO MENU: PROMPT_CIDADE_CANAL (Ranking Cidades: 1: Todos os Canais, 2: Selecionar)
  if (activeSession && activeSession.menu === 'PROMPT_CIDADE_CANAL') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        let card = await executeCityRankingCard(env, rep, { ...activeSession, selectedChannel: 'TODOS' });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_CIDADE_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildChannelListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // H) SE ESTÁ NO MENU: LIST_CIDADE_CANAL (1 a 4)
  if (activeSession && activeSession.menu === 'LIST_CIDADE_CANAL') {
    const chMatch = norm.match(/^([1-4])$/);
    if (chMatch) {
      const idx = parseInt(chMatch[1], 10) - 1;
      const ch = OFFICIAL_CHANNELS[idx];
      if (ch) {
        const rep = getReportById(activeSession.reportId);
        let card = await executeCityRankingCard(env, rep, { ...activeSession, selectedChannel: ch.name });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // I) SE ESTÁ NO MENU: PROMPT_MKT_RESIDENCIAL (1: Todas as Cidades, 2: Selecionar Cidade)
  if (activeSession && activeSession.menu === 'PROMPT_MKT_RESIDENCIAL') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        let card = await executeMarketShareResidencialCard(env, 'TODAS');
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_MKT_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // J) SE ESTÁ NO MENU: LIST_MKT_CIDADE (1 a 14)
  if (activeSession && activeSession.menu === 'LIST_MKT_CIDADE') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const city = OFFICIAL_14_CITIES[idx];
      if (city) {
        let card = await executeMarketShareResidencialCard(env, city.name);
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // K) SE ESTÁ NO MENU: PROMPT_MKT_MOVEL (1: Todos os DDDs, 2: Selecionar DDD)
  if (activeSession && activeSession.menu === 'PROMPT_MKT_MOVEL') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      const rep = getReportById(activeSession.reportId);
      if (optMatch[1] === '1') {
        let card = await executeMarketShareMovelCard(env, 'TODOS');
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_MKT_DDD' };
        await saveSession(updated);
        return { success: true, answer: buildDddListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // L) SE ESTÁ NO MENU: LIST_MKT_DDD (1 a 9)
  if (activeSession && activeSession.menu === 'LIST_MKT_DDD') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const ddd = OFFICIAL_DDDS[idx];
      if (ddd) {
        let card = await executeMarketShareMovelCard(env, ddd.ddd);
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // M) SE ESTÁ NO MENU: SELECT_ACTION
  if (activeSession && activeSession.menu === 'SELECT_ACTION') {
    const rep = getReportById(activeSession.reportId);

    // Relatórios FPD, CHURN_SAFRA, CREDITO (Opções 1 a 5)
    if (rep.id === 'FPD' || rep.id === 'CHURN_SAFRA' || rep.id === 'CREDITO') {
      const actMatch = norm.match(/^([1-5])$/);
      if (actMatch) {
        const act = parseInt(actMatch[1], 10);
        if (act === 1) { // Resumo Executivo
          let card = await executeExecutiveSummaryCard(env, rep, activeSession);
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Últimos 3 meses
          let card = await executeLast3MonthsCard(env, rep, activeSession);
          card += buildActionCardFooterLinks(rep, 2, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 3) { // Ranking 10 Piores Parceiros
          const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
          await saveSession(updated);
          return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone), intent: 'MENU', phone };
        } else if (act === 4) { // Ranking Canais (Últimos 3 meses)
          const updated = { ...activeSession, menu: 'PROMPT_CANAL_CIDADE' };
          await saveSession(updated);
          return { success: true, answer: buildChannelCityPromptMenu(rep, updated, phone, `Ranking Canais (${rep.name})`), intent: 'MENU', phone };
        } else if (act === 5) { // Ranking Cidades (Últimos 3 meses)
          const updated = { ...activeSession, menu: 'PROMPT_CIDADE_CANAL' };
          await saveSession(updated);
          return { success: true, answer: buildCityChannelPromptMenu(rep, updated, phone, `Ranking Cidades (${rep.name})`), intent: 'MENU', phone };
        }
      }
    }

    // Relatório CHURN_BL (Opções 1 a 3)
    if (rep.id === 'CHURN_BL') {
      const actMatch = norm.match(/^([1-3])$/);
      if (actMatch) {
        const act = parseInt(actMatch[1], 10);
        if (act === 1) { // Resumo Executivo
          let card = await executeChurnBlSummaryCard(env, activeSession);
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Últimos 3 meses
          let card = await executeChurnBlLast3MonthsCard(env, activeSession);
          card += buildActionCardFooterLinks(rep, 2, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 3) { // Ranking Cidades
          let card = await executeChurnBlCityRankingCard(env, activeSession);
          card += buildActionCardFooterLinks(rep, 3, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        }
      }
    }

    // Relatório MARKET_SHARE (Opções 1 a 3)
    if (rep.id === 'MARKET_SHARE') {
      const actMatch = norm.match(/^([1-3])$/);
      if (actMatch) {
        const act = parseInt(actMatch[1], 10);
        if (act === 1) { // Resumo Regional Geral
          let card = await executeMarketShareRegionalCard(env);
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Residencial
          const updated = { ...activeSession, menu: 'PROMPT_MKT_RESIDENCIAL' };
          await saveSession(updated);
          return { success: true, answer: buildCityPromptMenu(rep, updated, phone, 'Market Share Residencial'), intent: 'MENU', phone };
        } else if (act === 3) { // Móvel
          const updated = { ...activeSession, menu: 'PROMPT_MKT_MOVEL' };
          await saveSession(updated);
          return { success: true, answer: buildDddPromptMenu(rep, updated, phone), intent: 'MENU', phone };
        }
      }
    }
  }

  // N) SE ESTÁ NO MENU: SELECT_PRODUCT (1 a 4)
  if (activeSession && activeSession.menu === 'SELECT_PRODUCT') {
    const prodMatch = norm.match(/^([1-4])$/);
    if (prodMatch) {
      const idx = parseInt(prodMatch[1], 10) - 1;
      const prod = OFFICIAL_PRODUCTS[idx];
      if (prod) {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'SELECT_ACTION', productFilter: prod.dbFilter, productName: prod.name };
        await saveSession(updated);
        return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // O) SE ESTÁ NO MENU: SELECT_SEGMENT (1 ou 2)
  if (activeSession && activeSession.menu === 'SELECT_SEGMENT') {
    const segMatch = norm.match(/^([1-2])$/);
    if (segMatch) {
      const rep = getReportById(activeSession.reportId);
      const segName = segMatch[1] === '1' ? 'Banda Larga Total' : 'Banda Larga PME';
      const updated = { ...activeSession, menu: 'SELECT_ACTION', segment: segName, segmentName: segName };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone), intent: 'MENU', phone };
    }
  }

  // S1) SE ESTÁ NO MENU: PROMPT_SPEECH_ABRANGENCIA (1: Resumo Geral, 2: Filtrar por Cidade)
  if (activeSession && activeSession.menu === 'PROMPT_SPEECH_ABRANGENCIA') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      if (optMatch[1] === '1') {
        let card = await executeSpeechCard(env, 'Regional Norte', phone);
        card += buildCardFooterLinks({ name: 'Speech Analytics' }, { isSubmenu: false }, phone);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'LIST_SPEECH_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // S2) SE ESTÁ NO MENU: LIST_SPEECH_CIDADE (1 a 14)
  if (activeSession && activeSession.menu === 'LIST_SPEECH_CIDADE') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const city = OFFICIAL_14_CITIES[idx];
      if (city) {
        let card = await executeSpeechCard(env, city.name, phone);
        card += buildCardFooterLinks({ name: 'Speech Analytics' }, { isSubmenu: true }, phone);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // M1) SE ESTÁ NO MENU: PROMPT_MOTIVOS_ABRANGENCIA (1: Resumo Geral, 2: Filtrar por Cidade)
  if (activeSession && activeSession.menu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      if (optMatch[1] === '1') {
        let card = await executeMotivosCard(env, 'Regional Norte', phone);
        card += buildCardFooterLinks({ name: 'Motivos & OS' }, { isSubmenu: false }, phone);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'LIST_MOTIVOS_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone), intent: 'MENU', phone };
      }
    }
  }

  // M2) SE ESTÁ NO MENU: LIST_MOTIVOS_CIDADE (1 a 14)
  if (activeSession && activeSession.menu === 'LIST_MOTIVOS_CIDADE') {
    const numMatch = norm.match(/^(\d{1,2})$/);
    if (numMatch) {
      const idx = parseInt(numMatch[1], 10) - 1;
      const city = OFFICIAL_14_CITIES[idx];
      if (city) {
        let card = await executeMotivosCard(env, city.name, phone);
        card += buildCardFooterLinks({ name: 'Motivos & OS' }, { isSubmenu: true }, phone);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      }
    }
  }

  // P) SE NÃO TEM SESSÃO ATIVA (MENU PRINCIPAL DE BASES):
  const baseMatch = norm.match(/^([1-7])$/);
  if (baseMatch && !activeSession) {
    const opt = baseMatch[1];
    let selectedReport = null;
    let nextMenu = 'SELECT_ACTION';

    if (opt === '1') {
      selectedReport = REPORT_REGISTRY.FPD;
      nextMenu = 'SELECT_PRODUCT';
    } else if (opt === '2') {
      selectedReport = REPORT_REGISTRY.CHURN_SAFRA;
      nextMenu = 'SELECT_ACTION';
    } else if (opt === '3') {
      selectedReport = REPORT_REGISTRY.CREDITO;
      nextMenu = 'SELECT_PRODUCT';
    } else if (opt === '4') {
      selectedReport = REPORT_REGISTRY.CHURN_BL;
      nextMenu = 'SELECT_SEGMENT';
    } else if (opt === '5') {
      selectedReport = REPORT_REGISTRY.MARKET_SHARE;
      nextMenu = 'SELECT_ACTION';
    } else if (opt === '6') {
      selectedReport = REPORT_REGISTRY.SPEECH;
      nextMenu = 'PROMPT_SPEECH_ABRANGENCIA';
    } else if (opt === '7') {
      selectedReport = REPORT_REGISTRY.MOTIVOS;
      nextMenu = 'PROMPT_MOTIVOS_ABRANGENCIA';
    }

    if (selectedReport) {
      const newSession = { reportId: selectedReport.id, menu: nextMenu };
      await saveSession(newSession);

      if (nextMenu === 'SELECT_PRODUCT') {
        return { success: true, answer: buildProductSelectionMenu(selectedReport, phone), intent: 'MENU', phone };
      } else if (nextMenu === 'SELECT_SEGMENT') {
        return { success: true, answer: buildSegmentSelectionMenu(selectedReport, phone), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_SPEECH_ABRANGENCIA') {
        return { success: true, answer: buildSpeechPromptMenu(phone), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
        return { success: true, answer: buildMotivosPromptMenu(phone), intent: 'MENU', phone };
      } else {
        return { success: true, answer: buildActionSelectionMenu(selectedReport, newSession, phone), intent: 'MENU', phone };
      }
    }
  }

  // Q) Usuário digitou diretamente o nome da base (ex: "fpd", "churn", "safra", "credito", "market", "speech", "motivos")
  if (/^(fpd|first\s*payment|churn|banda\s*larga|safra|d120|np120|credito|crédito|antifraude|market|mkt|share|anatel|speech|transcric|motivo|motivos|os|taxa\s*os|ura|visita\s*tecnica)$/i.test(norm)) {
    let selectedReport = null;
    let nextMenu = 'SELECT_ACTION';

    if (/^(fpd|first\s*payment)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.FPD;
      nextMenu = 'SELECT_PRODUCT';
    } else if (/^(safra|d120|np120)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CHURN_SAFRA;
      nextMenu = 'SELECT_ACTION';
    } else if (/^(credito|crédito|antifraude)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CREDITO;
      nextMenu = 'SELECT_PRODUCT';
    } else if (/^(churn|banda\s*larga)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.CHURN_BL;
      nextMenu = 'SELECT_SEGMENT';
    } else if (/^(market|mkt|share|anatel)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.MARKET_SHARE;
      nextMenu = 'SELECT_ACTION';
    } else if (/^(speech|transcric)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.SPEECH;
      nextMenu = 'PROMPT_SPEECH_ABRANGENCIA';
    } else if (/^(motivo|motivos|os|taxa\s*os|ura|visita)/i.test(norm)) {
      selectedReport = REPORT_REGISTRY.MOTIVOS;
      nextMenu = 'PROMPT_MOTIVOS_ABRANGENCIA';
    }

    if (selectedReport) {
      const newSession = { reportId: selectedReport.id, menu: nextMenu };
      await saveSession(newSession);

      if (nextMenu === 'SELECT_PRODUCT') {
        return { success: true, answer: buildProductSelectionMenu(selectedReport, phone), intent: 'MENU', phone };
      } else if (nextMenu === 'SELECT_SEGMENT') {
        return { success: true, answer: buildSegmentSelectionMenu(selectedReport, phone), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_SPEECH_ABRANGENCIA') {
        return { success: true, answer: buildSpeechPromptMenu(phone), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
        return { success: true, answer: buildMotivosPromptMenu(phone), intent: 'MENU', phone };
      } else {
        return { success: true, answer: buildActionSelectionMenu(selectedReport, newSession, phone), intent: 'MENU', phone };
      }
    }
  }

  // 2. Classificação de Intenção Semântica (Router)
  const classification = await classifyIntent(env, cleanQuery);
  const intent = classification.intent;

  // 3. Roteamento Especializado
  if (intent === 'FORA_ESCOPO') {
    return {
      ...handleOutOfScopeQuery(),
      intent,
      phone,
    };
  }

  if (intent === 'CONCEITUAL') {
    const conceptualResult = await executeConceptualPipeline(env, cleanQuery);
    return {
      ...conceptualResult,
      intent,
      phone,
    };
  }

  // Intenção Analítica (Roteamento de Relatório-Alvo com Anti-Cruzamento de Indicadores)
  const resolution = await resolveTargetReport(env, cleanQuery, phone);
  if (resolution.needDisambiguation) {
    return {
      success: true,
      answer: resolution.menuText,
      intent: 'ANALITICA',
      disambiguation: true,
      phone
    };
  }

  if (resolution.directAnswer) {
    return {
      success: true,
      answer: resolution.directAnswer,
      intent: 'ANALITICA',
      phone
    };
  }

  const analyticalResult = await executeAnalyticalPipeline(env, resolution.effectiveQuery, phone, auth.scope, resolution.report);
  return {
    ...analyticalResult,
    intent,
    phone,
  };
}

/**
 * Disparo de Mensagem na Evolution API v2
 */
async function sendEvolutionMessage(env, remoteJid, text) {
  const evolutionUrl = env.EVOLUTION_URL || DEFAULT_EVOLUTION_URL;
  const apiKey = env.EVOLUTION_API_KEY || DEFAULT_EVOLUTION_KEY;
  const instance = env.EVOLUTION_INSTANCE || DEFAULT_EVOLUTION_INSTANCE;

  const endpoint = `${evolutionUrl.replace(/\/$/, '')}/message/sendText/${instance}`;
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': apiKey,
      },
      body: JSON.stringify({
        number: remoteJid,
        text: text,
      }),
    });

    const data = await res.json().catch(() => ({}));
    return { success: res.ok, data };
  } catch (err) {
    console.error('[Evolution Dispatch Error]', err);
    return { success: false, error: err.message };
  }
}

/**
 * Sub-roteador de Rotas do Bot para Cloudflare Worker
 */
export async function handleBotRoutes(request, env, url, pathname) {
  // 1. Healthcheck / Status do Bot
  if (pathname === '/api/bot/status' || pathname === '/api/bot/health') {
    const isSuspended = await getSystemControl(env, 'suspend_whatsapp_bot');
    return json({
      status: 'ok',
      service: 'pephub-bot-rag',
      suspended: Boolean(isSuspended),
      timestamp: new Date().toISOString(),
    });
  }

  // 2. Endpoint REST direto: POST /api/bot/ask (Consumido pelo Baileys bot, CLI, testes, app)
  if (pathname === '/api/bot/ask') {
    if (request.method !== 'POST') {
      return json({ error: 'Método não permitido. Use POST.' }, 405);
    }

    try {
      const body = await request.json();
      const phone = body.phone || body.sender || body.number || '';
      const query = body.query || body.message || body.text || '';

      if (!phone || !query) {
        return json({ error: 'Parâmetros obrigatórios ausentes: phone e query são necessários.' }, 400);
      }

      const result = await processBotQuery(env, phone, query);
      return json(result, result.unauthorized ? 403 : 200);
    } catch (err) {
      console.error('[Bot Ask Route Error]', err);
      return json({ error: 'Erro interno ao processar requisição do bot.', details: err.message }, 500);
    }
  }

  // 3. Webhook oficial da Evolution API v2: POST /api/bot/webhook/evolution
  if (pathname === '/api/bot/webhook/evolution' || pathname === '/api/bot/webhook') {
    if (request.method !== 'POST') {
      return json({ error: 'Método não permitido. Use POST.' }, 405);
    }

    try {
      const body = await request.json();

      // Estrutura padrão Evolution API v2: event = 'messages.upsert' ou 'MESSAGES_UPSERT'
      const eventType = body.event || body.type;
      const data = body.data || body;

      // Se for apenas teste de conexão da Evolution
      if (eventType === 'qrcode.updated' || eventType === 'connection.update') {
        return json({ received: true, event: eventType });
      }

      // Extrai dados da mensagem
      const key = data.key || {};
      const message = data.message || {};
      const isFromMe = Boolean(key.fromMe);
      const remoteJid = key.remoteJid || '';

      // Ignora mensagens do próprio bot para evitar loops
      if (isFromMe) {
        return json({ ignored: true, reason: 'from_me' });
      }

      // Extrai texto da conversa
      const text = message.conversation ||
        message.extendedTextMessage?.text ||
        message.imageMessage?.caption ||
        '';

      const cleanText = (text || '').trim();
      if (!cleanText) {
        return json({ ignored: true, reason: 'empty_text' });
      }

      // REGRA ESTRITA DE OURO: Somente mensagens iniciadas com "#?"
      const isTrigger = cleanText.startsWith('#?') || cleanText.startsWith('＃?');
      if (!isTrigger) {
        return json({ ignored: true, reason: 'missing_trigger_prefix' });
      }

      // Determina telefone remetente
      const senderJid = key.participant || remoteJid;
      const cleanPhone = normalizePhone(senderJid);

      // Extrai a consulta real removendo o gatilho "#?"
      const query = cleanText.replace(/^(#\?|＃\?)\s*/, '').trim() || 'ajuda';

      // Processa através do pipeline RAG
      const result = await processBotQuery(env, cleanPhone, query);

      // Envia a resposta de volta ao WhatsApp via Evolution API
      if (result && result.answer) {
        await sendEvolutionMessage(env, remoteJid, result.answer);
      }

      return json({
        success: true,
        handled: true,
        phone: cleanPhone,
        intent: result.intent,
      });
    } catch (err) {
      console.error('[Evolution Webhook Error]', err);
      return json({ error: 'Erro ao processar webhook da Evolution API.', details: err.message }, 500);
    }
  }

  return null;
}
