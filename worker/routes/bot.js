/**
 * Cloudflare Worker — Pephub Bot RAG & Text-to-SQL Router
 * Módulo de Inteligência Artificial para WhatsApp (Evolution API & Baileys Bridge)
 * Roteamento Semântico: Classificador de Intenção -> Text-to-SQL vs Semantic RAG
 * Regional Norte (AM, PA, MA, AP, RR)
 */

import { json, SECURITY_HEADERS, getSystemControl, getSessionUser } from '../utils/security.js';
import { buildSemanticCatalogPrompt, validateDimensionalCompatibility, SEMANTIC_TABLES, detectQualifiers, CLARO_CLUSTERS } from '../semantic_catalog.js';
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
  buildDeterministicAnalyticalSQL,
  buildProactiveClarificationResponse,
  extractQueryEntities
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
export async function verifyBotSender(env, rawPhone, sessionUser = null) {
  // Se usuário autenticado da sessão web do PEP HUB
  if (sessionUser && sessionUser.status === 'aprovado') {
    const isSuspended = await getSystemControl(env, 'suspend_whatsapp_bot');
    if (isSuspended && !sessionUser.is_admin) {
      return { allowed: false, phone: rawPhone, reason: 'suspended' };
    }
    return {
      allowed: true,
      phone: rawPhone || sessionUser.telefone || `web_${sessionUser.id}`,
      scope: {
        regional: 'REGIONAL NORTE',
        canal: 'TODOS',
        cidade: 'TODAS',
        permissao_total: 1,
      },
      user: {
        id: sessionUser.id,
        nome: sessionUser.nome_completo,
        area: sessionUser.area,
        isAdmin: Boolean(sessionUser.is_admin),
      },
    };
  }

  // Se for identificador web com ID de usuário aprovado
  if (rawPhone && String(rawPhone).startsWith('web_')) {
    const uid = String(rawPhone).replace('web_', '');
    if (env.DB) {
      const u = await env.DB.prepare('SELECT id, nome_completo, area, is_admin, status FROM users WHERE id = ? AND status = "aprovado"').bind(uid).first().catch(() => null);
      if (u) {
        return {
          allowed: true,
          phone: rawPhone,
          scope: { regional: 'REGIONAL NORTE', canal: 'TODOS', cidade: 'TODAS', permissao_total: 1 },
          user: { id: u.id, nome: u.nome_completo, area: u.area, isAdmin: Boolean(u.is_admin) }
        };
      }
    }
  }

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
export async function resolveTargetReport(env, query, phone, channel = 'whatsapp') {
  const norm = query.toLowerCase().trim();
  const cleanDigits = String(phone || '').startsWith('web_') ? String(phone || '') : String(phone || '').replace(/\D/g, '');

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

  // 2. Classificação Semântica Prioritária e Anti-Colisão
  const normClean = norm.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const entities = extractQueryEntities(query);

  const isChurnWord = /\b(churn|desconex(ao|oes|ões)|cancelament[oa]|desconexoes)\b/i.test(normClean);
  const isSafraWord = /\b(safra(s)?|d120|np120|clawback|estorno|sobrevivencia)\b/i.test(normClean);
  const isMktShareWord = /\b(market\s*share|marketshare|concorrencia|concorrência|participac(ao|ão)|net\s*adds?|netadds?|anatel|operadora(s)?|competitivas?|isps?|vivo|tim|oi|sky|surf)\b/i.test(normClean);
  const isFpdWord = /\b(fpd|first\s*payment|cura|taxa_fpd|qualidade\s+d[ea]\s+venda)\b/i.test(normClean);
  const isCreditoWord = /\b(credito|crédito|antifraude|aprovac|reprovac|politica\s+de\s+credito)\b/i.test(normClean);
  const isSpeechWord = /\b(speech|transcric|ouvir|grava[çc][ãa]o|ouvir\s+chamada)\b/i.test(normClean) || /\bmotivos?\s+de\s+cancelamento\b/i.test(normClean);
  const isMotivosWord = /\b(motivo(s)?\s+de\s+procura|taxa\s*os|orden(s)?\s+de\s+servi[cç]o|ordem\s+de\s+servi[cç]o|visita\s+tecnica|rechamada)\b/i.test(normClean);

  let targetRep = null;
  if (isSpeechWord) {
    targetRep = REPORT_REGISTRY.SPEECH;
  } else if (isMotivosWord) {
    targetRep = REPORT_REGISTRY.MOTIVOS;
  } else if (isChurnWord) {
    targetRep = isSafraWord ? REPORT_REGISTRY.CHURN_SAFRA : REPORT_REGISTRY.CHURN_BL;
  } else if (isSafraWord) {
    targetRep = REPORT_REGISTRY.CHURN_SAFRA;
  } else if (isFpdWord) {
    targetRep = REPORT_REGISTRY.FPD;
  } else if (isCreditoWord) {
    targetRep = REPORT_REGISTRY.CREDITO;
  } else if (isMktShareWord) {
    targetRep = REPORT_REGISTRY.MARKET_SHARE;
  }

  // Fallback secundário por palavras-chave com precedência segura (Market Share por último)
  if (!targetRep) {
    for (const key of ['FPD', 'SPEECH', 'MOTIVOS', 'CREDITO', 'CHURN_SAFRA', 'CHURN_BL', 'MARKET_SHARE']) {
      const rep = REPORT_REGISTRY[key];
      if (!rep) continue;
      for (const pat of rep.keywords) {
        if (pat.test(norm)) {
          targetRep = rep;
          break;
        }
      }
      if (targetRep) break;
    }
  }

  if (targetRep) {
    if (env.DB && cleanDigits) {
      try {
        await env.DB.prepare('DELETE FROM bot_pending_sessions WHERE phone = ?').bind(cleanDigits).run();
      } catch (_) {}
    }

    // Guarda Dimensional 1: Canal solicitado em Churn Safra
    if (targetRep.id === 'CHURN_SAFRA' && entities.isChannelQuery && !entities.isParceiroQuery) {
      const directAnswer = `📉 *Análise de Sobrevivência · Churn Safra D120*\n\n` +
        `🧭 *Cenário da Análise:*\n` +
        `• 🏷️ *Produto / Serviço:* Banda Larga Residencial (Churn Safra · Sobrevivência D120)\n` +
        `• 🏛️ *Fonte dos Dados:* Base Oficial de Sobrevivência e Estornos Claro (D1)\n\n` +
        `🚫 *Incompatibilidade Dimensional:* A base oficial corporativa de **Churn Safra D120** é consolidada exclusivamente nos níveis **Regional**, **Cidade** e **Parceiro Comercial** (Top Connect, All Rede, Star Link, etc.). **Não há segregação por canal de venda** (PAP, Lojas, Televendas) nesta base de estornos.\n\n` +
        `💡 *Onde consultar canais de venda ofensores:*\n` +
        `• **FPD 60:** Possui visão completa de canais (Porta a Porta, Lojas, Televendas, Agente Autorizado) e vendedores individuais.\n` +
        `• **Aprovação de Crédito:** Apresenta a taxa de aprovação e recusas por canal e PDV.\n\n` +
        `Selecione uma ação rápida abaixo para consultar os canais ofensores:`;
      return {
        report: targetRep,
        directAnswer,
        reportUrl: '/fpd-residencial/',
        reportName: 'FPD Residencial (Canais)',
        chips: [
          { label: '🚪 Ver Canais em FPD', query: 'quais os canais ofensores em FPD?' },
          { label: '🛡️ Ver Canais em Crédito', query: 'quais canais têm pior aprovação de crédito?' },
          { label: '🤝 Ver Parceiros em Churn Safra', query: 'quais os piores parceiros em Churn Safra?' }
        ],
        disambiguated: false
      };
    }

    // Guarda Dimensional 2: Canal solicitado em Churn Banda Larga
    if ((targetRep.id === 'CHURN_BL' || targetRep.id === 'CHURN_PME') && entities.isChannelQuery && !entities.isParceiroQuery) {
      const directAnswer = `📉 *Painel de Desconexões · Churn Banda Larga*\n\n` +
        `🧭 *Cenário da Análise:*\n` +
        `• 🏷️ *Produto / Serviço:* Banda Larga Fixa (Cancelamentos Mensais)\n` +
        `• 🏛️ *Fonte dos Dados:* Base Oficial de Desconexões e RxO Claro (D1)\n\n` +
        `🚫 *Incompatibilidade Dimensional:* A base de **Churn Banda Larga Mensal** possui acompanhamento executivo aberto apenas por **Cidade** e **Regional Norte** (não possui segregação por canal de venda na apuração mensal).\n\n` +
        `💡 *Onde consultar canais de venda ofensores:*\n` +
        `• **FPD 60:** Qualidade de vendas por canal (PAP, Lojas, Televendas).\n` +
        `• **Aprovação de Crédito:** Desempenho de entrada por canal.\n\n` +
        `Selecione uma ação rápida abaixo:`;
      return {
        report: targetRep,
        directAnswer,
        reportUrl: '/fpd-residencial/',
        reportName: 'FPD Residencial (Canais)',
        chips: [
          { label: '🚪 Ver Canais em FPD', query: 'qual o FPD por canal de venda?' },
          { label: '📍 Ranking de Cidades no Churn BL', query: 'ranking de cidades com pior churn banda larga' }
        ],
        disambiguated: false
      };
    }

    return { report: targetRep, effectiveQuery: query, disambiguated: false };
  }

  // 3. Consulta ambígua: salva na memória persistente D1
  if (env.DB && cleanDigits) {
    try {
      await env.DB.prepare('INSERT OR REPLACE INTO bot_pending_sessions (phone, query, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)').bind(cleanDigits, query).run();
    } catch (e) {
      console.warn('[D1 Pending Session Save Error]', e.message);
    }
  }

  // Postura Questionadora Proativa: se detectar entidade (cidade, canal, DDD ou parceiro) sem métrica
  const detectedLabel = entities.matchedCity || entities.matchedDdd?.label || entities.matchedChannel || (entities.isChannelQuery ? 'Canais de Venda' : null) || entities.matchedPartner || (entities.isParceiroQuery ? 'Parceiros Comerciais' : null);

  if (detectedLabel) {
    return {
      needDisambiguation: true,
      menuText: buildProactiveClarificationResponse(detectedLabel, channel, cleanDigits),
      detectedEntity: detectedLabel
    };
  }

  return { needDisambiguation: true, menuText: buildDisambiguationMenu(query, cleanDigits, channel) };
}

/**
 * Gerador Text-to-SQL Estrito por Relatório
 */
/**
 * Gerador Text-to-SQL Estrito por Relatório
 */
async function generateSQL(env, query, userPhone, userScope, targetReport) {
  const norm = query.toLowerCase().trim();

  // Fast-Path 0: Motor Determinístico apenas para consultas muito simples de catálogo
  const deterministicSql = buildDeterministicAnalyticalSQL(query, targetReport, userScope);
  if (deterministicSql) {
    return deterministicSql;
  }

  // Fast-Path 1: Última safra de FPD
  if (targetReport.id === 'FPD' && (/^qual\s+a\s+(última|ultima)\s+safra\s+de\s+fpd\??$/i.test(norm))) {
    return `SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1`;
  }

  // Fast-Path 2: Última safra de Churn Safra
  if (targetReport.id === 'CHURN_SAFRA' && (/^qual\s+a\s+(última|ultima)\s+safra\s+de\s+(churn|safra)\??$/i.test(norm))) {
    return `SELECT DISTINCT safra, safra_ord FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1`;
  }

  const schemaContext = buildSchemaPromptContext();

  const reportPromptRule = targetReport.id === 'FPD' ? `
- RELATÓRIO OBRIGATÓRIO: FPD (First Payment Default & Qualidade de Venda)
  - Tabela exclusiva: fato_fpd (possui colunas safra, safra_ord, cidade, uf, canal, familia_produto, parceiro, vendedor, instalacoes, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura, faixa_risco).
  - SAFRA MAIS RECENTE / ÚLTIMA SAFRA: A ordenação cronológica das safras DEVE ser feita por safra_ord DESC. A última safra oficial de FPD é 'mai/26'.
  - INDICADOR PADRÃO OFICIAL: FPD 60 (coluna taxa_fpd60).
  - SE O USUÁRIO PERGUNTAR POR PDV / PARCEIRO (ex: 'qual o pior pdv de Belém em FPD', 'pdv mais ofensor em FPD', 'ranking de parceiros'):
    Consulte fato_fpd agrupando por parceiro:
    SELECT parceiro, cidade, canal, safra, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60) / SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE parceiro IS NOT NULL \${cidadeFilter} GROUP BY parceiro HAVING total_instalacoes >= 10 ORDER BY taxa_fpd60 DESC LIMIT 5;
  - SE O USUÁRIO PERGUNTAR POR VENDEDOR (ex: 'qual o pior vendedor do canal Porta a Porta em FPD em abril, considere apenas os que tem mais de 10 vendas', 'vendedores ofensores em FPD'):
    Consulte fato_fpd filtrando canal, período e corte de vendas:
    SELECT vendedor, parceiro, cidade, canal, safra, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30 FROM fato_fpd WHERE vendedor IS NOT NULL \${filtros} AND instalacoes > 10 ORDER BY taxa_fpd60 DESC LIMIT 5;
  - SE FOR CONSULTA SOBRE CIDADES OU CANAIS:
    Agrupe por cidade ou canal calculando SUM(fpd60) e SUM(instalacoes) com taxa consolidada.
` : targetReport.id === 'CHURN_BL' ? `
- RELATÓRIO OBRIGATÓRIO: Churn Banda Larga
  - Tabela exclusiva: fato_indicadores_mensais.
  - Colunas: segmento, mes_referencia, tipo_visao, cidade, vol_real, vol_orc, rxo_delta, rxo_pct, taxa_real, taxa_orc, taxa_delta_pp, ytd_real, ytd_orc.
  - Se o usuário pedir orçamento (ex: 'orçamento de churn para novembro'):
    Selecione mes_referencia, vol_orc, taxa_orc, taxa_real, rxo_delta, ytd_real, ytd_orc filtrando o período (ex: mes_referencia LIKE '%nov%' ou mês recente).
  - Se o usuário pedir YTD ou acumulado do ano:
    Selecione ytd_real, ytd_orc, taxa_real, taxa_orc.
` : targetReport.id === 'CHURN_SAFRA' ? `
- RELATÓRIO OBRIGATÓRIO: Churn Safra D120
  - Tabela exclusiva: fato_churn_safra.
  - Colunas: safra, safra_ord, visao, entidade_nome, cidade, instalacoes, churn_d120, taxa_d120, np120, taxa_np120, inadimplencia, fraude, status_safra.
  - Safras maduras oficiais: status_safra = 'MADURA' (ordene por safra_ord DESC).
  - ATENÇÃO DIMENSIONAL MANDATÓRIA: A base fato_churn_safra consolida até Parceiro Comercial (visao = 'PARCEIRO') e Cidade (visao = 'CIDADE'). NÃO possui a dimensão Canal de Venda (PAP, Lojas, Televendas, etc.).
  - SE O USUÁRIO PERGUNTAR QUAL CANAL ESTÁ PIOR OU OFENSOR EM CHURN SAFRA:
    Busque os parceiros mais ofensores (SELECT entidade_nome, safra, visao, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND status_safra = 'MADURA' ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 5;) mas o sintetizador DEVE explicar que a base consolida por Parceiro Comercial (não por canal), e sugerir consultar FPD para canais.
  - SE O USUÁRIO PERGUNTAR POR PARCEIROS OFENSORES OU RANKING DE PARCEIROS:
    SELECT entidade_nome, safra, visao, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND status_safra = 'MADURA' ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 5;
  - SE O USUÁRIO PERGUNTAR POR VENDEDORES EM CHURN SAFRA:
    A tabela fato_churn_safra consolida até Parceiro e Cidade (não possui vendedor individual). Busque os parceiros comerciais mais ofensores (visao = 'PARCEIRO' AND instalacoes >= 20 ORDER BY taxa_d120 DESC LIMIT 5) para que o sintetizador explique a característica da base e ofereça a visão de parceiros ou vendedores de FPD.
` : targetReport.id === 'CREDITO' ? `
- RELATÓRIO OBRIGATÓRIO: Aprovação de Crédito & Antifraude
  - Tabela exclusiva: fato_aprovacao_credito.
  - Colunas: mes_referencia, cidade, canal, pdv_ou_parceiro, consultas, aprovados, taxa_aprovacao, recusas_politica, recusas_antifraude, risco_alto.
` : `
- RELATÓRIO OBRIGATÓRIO: Market Share & Concorrência (Anatel)
  - Tabela exclusiva: fato_market_share.
  - Colunas: id, mes_referencia, cidade, uf, ddd, operadora, produto, segmento, acessos, market_share_pct, net_adds, posicao_ranking.
  - REGRAS MANDATÓRIAS DE PRODUTO E SEGMENTO:
    * Se o usuário perguntar sobre BANDA LARGA, RESIDENCIAL, FIXA ou SCM:
      Filtre OBRIGATORIAMENTE: produto = 'BANDA_LARGA' AND segmento = 'RESIDENCIAL'
    * Se o usuário perguntar sobre MÓVEL, PÓS PAGO, SEM M2M, CELULAR ou pergunta padrão de Market Share:
      Filtre OBRIGATORIAMENTE: produto = 'MOVEL' AND segmento = 'POS_PAGO_SEM_M2M'
    * Se o usuário perguntar sobre 5G:
      Filtre OBRIGATORIAMENTE: produto = 'MOVEL' AND segmento = '5G'
  - SE O USUÁRIO PERGUNTAR POR CIDADE (ex: Belém, Manaus, São Luís):
    SELECT mes_referencia, cidade, operadora, produto, segmento, acessos, market_share_pct, net_adds, posicao_ranking FROM fato_market_share WHERE produto = '<PRODUTO>' AND segmento = '<SEGMENTO>' AND (cidade = '<CIDADE>' OR cidade LIKE '%<CIDADE>%') ORDER BY market_share_pct DESC LIMIT 6;
  - SE O USUÁRIO PERGUNTAR POR CONSOLIDAÇÃO REGIONAL OU CONCORRÊNCIA NA REGIONAL:
    SELECT mes_referencia, cidade, operadora, produto, segmento, acessos, market_share_pct, net_adds, posicao_ranking FROM fato_market_share WHERE produto = '<PRODUTO>' AND segmento = '<SEGMENTO>' AND cidade = 'Regional Norte' ORDER BY market_share_pct DESC LIMIT 6;
`;

  const systemInstruction = `Você é um Arquiteto e Engenheiro de Dados Sênior especialista em SQLite D1 para Telecomunicações da Claro (Regional Norte).
Sua missão é converter a pergunta em linguagem natural do usuário em uma única consulta SQL SELECT precisa, eficiente e diretamente executável.

DIRETRIZES FUNDAMENTAIS:
1. Responda APENAS o código SQL puro dentro de um bloco \`\`\`sql ou texto puro, sem comentários conversacionais adicionais.
2. NUNCA gere instruções destrutivas (UPDATE, DELETE, DROP, INSERT). Apenas SELECT ou WITH...SELECT.
3. Tratamento de Cidades e Acentos no SQLite D1:
   - O SQLite D1 NÃO normaliza acentuação gráfica com o operador LIKE.
   - As cidades no banco estão gravadas com acentuação oficial: 'Belém', 'São Luís', 'Santarém', 'Macapá', 'Marabá'.
   - Para garantir correspondência perfeita, SEMPRE use cláusulas OR para cidades com acento:
     (cidade LIKE '%Belém%' OR cidade LIKE '%Belem%')
     (cidade LIKE '%São Luís%' OR cidade LIKE '%Sao Luis%' OR cidade LIKE '%SLZ%')
     (cidade LIKE '%Santarém%' OR cidade LIKE '%Santarem%')
     (cidade LIKE '%Macapá%' OR cidade LIKE '%Macapa%')
     (cidade LIKE '%Marabá%' OR cidade LIKE '%Maraba%')
4. Formatos de Safras e Períodos:
   - Em fato_fpd e fato_churn_safra: safra é formatada como 'mmm/aa' (ex: 'abr/26', 'mai/26'). Se o usuário disser 'abril', use: (safra LIKE '%abr%' OR safra LIKE '%04%').
   - Em fato_indicadores_mensais: mes_referencia é 'Mês / Ano' (ex: 'Outubro / 2026'). Se o usuário pedir um mês específico que não existir na base, busque o mês mais recente disponível ordenando por id DESC.
5. REGRAS OBRIGATÓRIAS DE PADRÃO (DEFAULTS):
   - MÊS/SAFRA PADRÃO: Se o usuário não especificar safra/mês, ordene pela mais recente (safra_ord DESC ou mes_referencia DESC).
   - LIMITES DE VARREDURA: Sempre use LIMIT 5 a 10 para rankings e agregações.
5. REGRAS DO RELATÓRIO SOLICITADO:
${reportPromptRule}

${buildSemanticCatalogPrompt()}

6. SEGURANÇA E CARTEIRIZAÇÃO:
   - Usuário solicitante: '${userPhone}'.
   ${(userScope?.permissao_total === 1 || userScope?.cidade === 'TODAS' || userScope?.cidade === 'Regional Norte') ? `
   - Gestor Regional com Acesso Total. NÃO restrinja com filtros restritivos forçados na cláusula WHERE a menos que o usuário tenha pedido na pergunta.
   ` : `
   - Usuário restrito à cidade '${userScope?.cidade}'. Adicione filtro obrigatório: (cidade = '${userScope?.cidade}' OR cidade = 'Regional Norte').
   `}

${schemaContext}`;

  const raw = await callGemini(env, systemInstruction, `Pergunta do Usuário: "${query}"`, 0.0);
  if (raw) {
    const clean = raw.replace(/```sql/gi, '').replace(/```/g, '').trim();
    if (clean) return clean;
  }

  // Fallback Resiliente: se a API Gemini estiver sem chave ou indisponível,
  // infere a consulta SQL analítica correspondente com base no padrão da pergunta do gestor:
  return inferComplexAnalyticalSQL(query, targetReport, userScope);
}

/**
 * Inferência Analítica Semântica de Alta Resiliência
 * Executada quando o LLM remoto oscila ou não está disponível.
 */
export function inferComplexAnalyticalSQL(query, targetReport, userScope) {
  if (!query || !targetReport) return null;
  const qNorm = query.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  if (targetReport.id === 'FPD') {
    const isPdvOrParceiro = /\b(pdv|pdvs|parceiro|parceiros|ofensor|ofensores|loja|franquia)\b/i.test(qNorm);
    const isVendedor = /\b(vendedor|vendedores|vendedora|consultor)\b/i.test(qNorm);

    // Cidade
    let cidadeFilter = '';
    if (/\b(belem)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%Belém%' OR cidade LIKE '%Belem%')`;
    else if (/\b(manaus)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%Manaus%')`;
    else if (/\b(sao\s+luis|slz)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%São Luís%' OR cidade LIKE '%Sao Luis%')`;
    else if (/\b(santarem)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%Santarém%' OR cidade LIKE '%Santarem%')`;
    else if (/\b(macapa)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%Macapá%' OR cidade LIKE '%Macapa%')`;
    else if (/\b(maraba)\b/i.test(qNorm)) cidadeFilter = `AND (cidade LIKE '%Marabá%' OR cidade LIKE '%Maraba%')`;

    // Canal
    let canalFilter = '';
    if (/\b(pap|porta\s+a\s+porta)\b/i.test(qNorm)) canalFilter = `AND canal LIKE '%PAP%'`;
    else if (/\b(loja|lojas)\b/i.test(qNorm)) canalFilter = `AND canal LIKE '%Loja%'`;
    else if (/\b(televendas)\b/i.test(qNorm)) canalFilter = `AND canal LIKE '%Televendas%'`;

    // Safra / Mês
    let safraFilter = '';
    if (/\b(abril|abr)\b/i.test(qNorm)) safraFilter = `AND (safra LIKE '%abr%' OR safra LIKE '%04%')`;
    else if (/\b(maio|mai)\b/i.test(qNorm)) safraFilter = `AND (safra LIKE '%mai%' OR safra LIKE '%05%')`;
    else if (/\b(marco|mar)\b/i.test(qNorm)) safraFilter = `AND (safra LIKE '%mar%' OR safra LIKE '%03%')`;

    // Corte de vendas
    let corteFilter = 'AND instalacoes >= 5';
    const mCorte = qNorm.match(/(?:mais\s+de|maior\s+que|corte\s+de|minimo\s+de)\s+(\d+)/i);
    if (mCorte) {
      corteFilter = `AND instalacoes > ${mCorte[1]}`;
    }

    if (isVendedor) {
      return `SELECT vendedor, parceiro, canal, safra, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30 FROM fato_fpd WHERE vendedor IS NOT NULL ${canalFilter} ${safraFilter} ${cidadeFilter} ${corteFilter} ORDER BY taxa_fpd60 DESC LIMIT 5`;
    }

    if (isPdvOrParceiro) {
      return `SELECT parceiro, cidade, canal, safra, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60) / SUM(instalacoes), 2) as taxa_fpd60, ROUND(100.0 * SUM(fpd30) / SUM(instalacoes), 2) as taxa_fpd30 FROM fato_fpd WHERE parceiro IS NOT NULL ${cidadeFilter} ${canalFilter} GROUP BY parceiro HAVING total_instalacoes >= 10 ORDER BY taxa_fpd60 DESC LIMIT 5`;
    }

    return `SELECT parceiro, cidade, canal, safra, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60) / SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE parceiro IS NOT NULL ${cidadeFilter} GROUP BY parceiro HAVING total_instalacoes >= 20 ORDER BY taxa_fpd60 DESC LIMIT 5`;
  }

  if (targetReport.id === 'CHURN_SAFRA') {
    return `SELECT safra, visao, entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE status_safra = 'MADURA' AND (visao = 'REGIONAL' OR (visao = 'PARCEIRO' AND instalacoes >= 20)) ORDER BY safra_ord DESC, CASE WHEN visao = 'REGIONAL' THEN 0 ELSE 1 END, taxa_d120 DESC LIMIT 10`;
  }

  if (targetReport.id === 'MARKET_SHARE') {
    const isBandaLarga = /\b(banda\s*larga|residencial|fixa|scm|fibra|gpon)\b/i.test(qNorm);
    const is5G = /\b5g\b/i.test(qNorm);
    const produtoTarget = isBandaLarga ? 'BANDA_LARGA' : 'MOVEL';
    const segmentoTarget = isBandaLarga ? 'RESIDENCIAL' : (is5G ? '5G' : 'POS_PAGO_SEM_M2M');

    let cidadeWhere = "cidade = 'Regional Norte'";
    if (/\b(belem)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Belém' OR cidade LIKE '%Belém%')";
    else if (/\b(manaus)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Manaus' OR cidade LIKE '%Manaus%')";
    else if (/\b(sao\s+luis|slz)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'São Luís' OR cidade LIKE '%São Luís%')";
    else if (/\b(macapa)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Macapá' OR cidade LIKE '%Macapá%')";
    else if (/\b(boa\s+vista|bv)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Boa Vista' OR cidade LIKE '%Boa Vista%')";
    else if (/\b(santarem)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Santarém' OR cidade LIKE '%Santarém%')";
    else if (/\b(maraba)\b/i.test(qNorm)) cidadeWhere = "(cidade = 'Marabá' OR cidade LIKE '%Marabá%')";

    const mDdd = qNorm.match(/\b(?:ddd|mercado|regiao)\s*(9[1-9])\b/i);
    if (mDdd) {
      cidadeWhere = `(ddd = '${mDdd[1]}' OR cidade = 'DDD ${mDdd[1]}')`;
    }

    return `SELECT mes_referencia, cidade, operadora, produto, segmento, acessos, acessos as total_acessos, market_share_pct, market_share_pct as market_share_recente, net_adds, net_adds as media_net_adds, net_adds as total_net_adds, posicao_ranking FROM fato_market_share WHERE produto = '${produtoTarget}' AND segmento = '${segmentoTarget}' AND ${cidadeWhere} ORDER BY market_share_pct DESC LIMIT 6`;
  }

  if (targetReport.id === 'CHURN_BL' || targetReport.id === 'CHURN_PME') {
    return `SELECT mes_referencia, segmento, tipo_visao, cidade, vol_real, vol_orc, rxo_delta, taxa_real, taxa_orc, ytd_real, ytd_orc, mom_pct FROM fato_indicadores_mensais WHERE cidade = 'Regional Norte' AND tipo_visao = 'TOTAL' AND segmento = 'Banda Larga Total' ORDER BY id DESC LIMIT 5`;
  }

  if (targetReport.id === 'CREDITO') {
    return `SELECT mes_referencia, cidade, canal, pdv_ou_parceiro, consultas, aprovados, taxa_aprovacao, recusas_antifraude, recusas_politica, risco_alto FROM fato_aprovacao_credito ORDER BY mes_referencia DESC, consultas DESC LIMIT 5`;
  }

  return null;
}

/**
 * Utilitários de Extração Segura de Métricas (Imunes a NaN e undefined)
 */
function getValNum(obj, keys, fallback = 0) {
  if (!obj) return fallback;
  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null && obj[k] !== '') {
      const n = Number(obj[k]);
      if (!isNaN(n)) return n;
    }
  }
  return fallback;
}

function getValPct(obj, keys, fallback = 0, digits = 1) {
  const n = getValNum(obj, keys, fallback);
  return n.toFixed(digits) + '%';
}

function getValFmt(obj, keys, fallback = 0) {
  const n = getValNum(obj, keys, fallback);
  return Math.round(n).toLocaleString('pt-BR');
}

export function formatPeriodoLabel(val) {
  if (!val) return 'Período Recente';
  const str = String(val).trim();
  const m = str.match(/^(\d{4})-(\d{2})$/);
  if (m) {
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const idx = parseInt(m[2], 10) - 1;
    if (idx >= 0 && idx < 12) return `${meses[idx]}/${m[1]}`;
  }
  return str;
}

/**
 * Síntese Cognitiva Analítica via Gemini (LLM-in-the-Loop)
 * Transforma dados brutos do SQLite D1 em raciocínio executivo fluido,
 * com honestidade sobre limites e sugestões inteligentes estilo Google.
 */
export async function synthesizeAnalyticalAnswerWithLLM(env, query, dbRows, targetReport, safeSql, userPhone, userScope, channel = 'web') {
  const isWeb = channel === 'web' || String(userPhone || '').startsWith('web_');
  const targetChannelName = isWeb ? 'portal web do PEP HUB' : 'WhatsApp';

  const systemInstruction = `Você é o Consultor Sênior de Inteligência Analítica e BI da Claro Regional Norte (PEP HUB).
Sua missão é responder diretamente à dúvida do gestor/usuário com alto nível de precisão executiva, raciocínio quantitativo fundamentado e postura orientadora e inteligente (semelhante ao motor de respostas do Google).

DIRETRIZES FUNDAMENTAIS DE QUALIDADE E GOVERNANÇA:
1. DESCRIÇÃO OBRIGATÓRIA E EXPLÍCITA DO CENÁRIO DA ANÁLISE (ZERO DÚVIDAS):
   - No início de TODA resposta executiva, inclua obrigatoriamente um bloco de contextualização do cenário da análise, para que o gestor nunca tenha dúvida sobre o produto, período, praça ou fonte:
     🧭 *Cenário da Análise:*
     • 🏷️ *Produto / Serviço:* Especifique de forma precisa e sem ambiguidade o produto ou segmento consultado (ex: "Telefonia Móvel (SMP · Mercado Total & 5G)", "Banda Larga Fixa Residencial (SCM)", "Banda Larga PME", "Serviços Residenciais (FPD 60)", "Banda Larga Residencial (Churn Safra D120)"). NUNCA cite apenas "Market Share" ou "Churn" sem declarar expressamente o produto!
     • 📅 *Período / Safra de Referência:* Mês de referência ou safra apurada (ex: "Setembro/2026", "Safra abr/26").
     • 📍 *Abrangência Geográfica:* Cidade apurada (ex: "Belém/PA", "Manaus/AM") ou "Regional Norte (PA, AM, MA, AP, RR)".
     • 🏛️ *Fonte dos Dados:* Fonte oficial corporativa ou regulatória (ex: "Dados Oficiais Anatel (SMP)", "Base Corporativa D1 PEP HUB").
     • ℹ️ *Premissas Analíticas:* Breve explicação da métrica (ex: "Participação calculada sobre base de acessos ativos em serviço e Net Adds mensais").
    - DIRETRIZES DE MARKET SHARE ANATEL (MÓVEL SMP vs BANDA LARGA FIXA SCM):
      * A base SQLite D1 possui dados regulatórios OFICIAIS completos para AMBOS os produtos:
        a) Telefonia Móvel (SMP · Pós-pago sem M2M e 5G):
           - "Pós-pago sem M2M" é o padrão executivo oficial Claro na Regional Norte (base pura pós-paga sem IoT). Operadoras: Claro, Vivo, TIM, Surf, Competitivas/Outras.
           - Belém Móvel Pós: Claro líder isolada com 44.14% e +4.704 net adds, TIM 30.93%, Vivo 23.93%.
           - Regional Norte Móvel Pós: Vivo líder acumulada com 42.41%, Claro vice-líder com 37.04% e líder absoluta em crescimento (+27.120 Net Adds).
        b) Banda Larga Fixa Residencial (SCM · GPON + HFC · Filtro Oficial 02.BL):
           - Belém Banda Larga: Claro líder absoluta com 33.88% de Market Share e saldo de +131 Net Adds, superando Oi (27.26%), Competitivas/ISPs (18.74%) e Vivo (17.42%).
           - Regional Norte Banda Larga: Competitivas/ISPs somam 66.27% (2.250.782 acessos). Entre as grandes operadoras nacionais, a Claro lidera com 12.98% (440.893 acessos e +591 Net Adds), à frente de Oi (12.15%) e Vivo (6.59%).
      * NUNCA entregue números de Móvel quando o usuário perguntar sobre Banda Larga ou Residencial! E vice-versa.
      * Declare com absoluta precisão o produto no Cenário da Análise:
        - Se Móvel Pós sem M2M: "Telefonia Móvel (SMP · Pós-pago sem M2M)"
        - Se Banda Larga: "Banda Larga Fixa Residencial (SCM · GPON + HFC)"
        - Se Móvel 5G: "Telefonia Móvel (SMP · Penetração 5G)" 

2. RACIOCÍNIO ANALÍTICO BASEADO EM DADOS REAIS:
   - Analise os dados retornados pelo banco SQLite D1 e redija uma resposta executiva completa, clara e fluida.
   - Aponte com destaque o líder, o ofensor ou o indicador solicitado, informando percentuais com 2 casas decimais para shares (ex: 33.88%) e volumes nominais reais.
   - Se foi pedida uma média móvel, comparação com concorrência ou acumulado YTD, apresente os números com clareza matemática.

3. FIDELIDADE ABSOLUTA E ZERO ALUCINAÇÃO:
   - NUNCA invente números, nomes ou métricas que não estejam presentes nos dados fornecidos abaixo.
   - NUNCA misture indicadores (FPD é FPD, Churn Safra D120 é Churn Safra D120, Churn BL é Churn BL).

4. TRANSPARÊNCIA DIMENSIONAL ABSOLUTA (CANAL vs PARCEIRO vs CIDADE):
   - A base fato_churn_safra consolida até Parceiro Comercial (visao = 'PARCEIRO') e Cidade (visao = 'CIDADE'). Ela NÃO possui a dimensão Canal de Venda (PAP, Lojas, Televendas, etc.).
   - Se o usuário perguntar por "canal ofensor", "qual canal está pior" ou "canais" em Churn Safra:
     NUNCA chame os parceiros comerciais (Top Connect, All Rede, Star Link, etc.) de "canal"!
     Explique com clareza executiva e transparência:
     "Na base oficial de Churn Safra D120, a consolidação é realizada por Parceiro Comercial e por Cidade (não há segregação por canal de venda). Os parceiros mais ofensores de D120 são: [listar os parceiros retornados]. Para analisar canais ofensores (ex: Porta a Porta, Lojas, Televendas), consulte os indicadores de FPD 60 ou Aprovação de Crédito."
   - A base fato_indicadores_mensais (Churn BL) NÃO possui Canal nem Parceiro (apenas Cidade e Regional).
   - Somente fato_fpd e fato_aprovacao_credito possuem canais de venda!

5. REGRA DE OURO DA VERACIDADE (SE NÃO SOUBER OU TIVER DÚVIDA, PERGUNTE OU DIGA QUE NÃO SABE):
   - SE VOCÊ NÃO SOUBER UM VALOR, SE OS DADOS RETORNADOS FOREM INSUFICIENTES OU SE HOUVER DÚVIDA/AMBIGUIDADE:
     NUNCA CHUTE, NUNCA INVENTE E NUNCA APROXIME NÚMEROS!
     Diga com clareza executiva e transparência: "Não localizei esse dado específico na base oficial consolidada no D1" ou pergunte educadamente ao usuário para esclarecer os parâmetros desejados (ex: praça, período ou produto).
   - O gestor toma decisões estratégicas críticas com base nestas respostas; a precisão analítica deve ser de 100%.

6. PROVOCAÇÃO ANALÍTICA / SUGESTÃO DE APROFUNDAMENTO:
   - Ao final de cada resposta, termine sempre com uma seção de aprofundamento proativo:
     💡 *Sugestão de Aprofundamento:* [Um próximo passo analítico lógico e perspicaz para o usuário explorar a seguir].

7. FORMATAÇÃO EXECUTIVA E CANAL:
   - Use emojis de negócio discretos (💳, 📉, 🛡️, 📊, 📍, 🏢), use *negrito* nos números e nomes principais.
   - Não exiba o código SQL puro ao usuário, a menos que ele tenha pedido expressamente para ver a consulta.
   - ${isWeb ? 'CANAL WEB: NUNCA mencione #dados, #ajuda ou links wa.me.' : 'CANAL WHATSAPP: Mensagens compatíveis com leitura móvel.'}
   - Mantenha tom cordial, profissional e sênior.`;

  const rowsSnippet = JSON.stringify((dbRows || []).slice(0, 25), null, 2);
  const prompt = `Pergunta Original do Usuário: "${query}"
Relatório Alvo: ${targetReport?.name || targetReport?.title || 'Indicadores Regionais'}
SQL Executado no D1:
${safeSql}

Dados Retornados do SQLite D1 (${dbRows?.length || 0} registros):
${rowsSnippet}

Redija a resposta executiva final fundamentada exclusivamente nestes dados:`;

  const answer = await callGemini(env, systemInstruction, prompt, 0.15);
  if (answer && answer.trim()) {
    return answer.trim();
  }

  // Fallback Cognitivo Analítico: se a API do Gemini não responder,
  // produz a resposta com raciocínio analítico fluido e postura consultiva
  return synthesizeCognitiveAnswerDeterministic(query, dbRows, targetReport, channel);
}

/**
 * Síntese Cognitiva Analítica Determinística
 * Raciocínio executivo de alto padrão quando o LLM remoto estiver indisponível.
 */
export function synthesizeCognitiveAnswerDeterministic(query, dbRows, targetReport, channel = 'web') {
  if (!dbRows || dbRows.length === 0) {
    return `⚠️ *${targetReport?.title || targetReport?.name || 'PEP HUB'} · Regional Norte*\n\nNão foram encontrados registros para os parâmetros informados nesta consulta.\n\n💡 *Sugestão de Aprofundamento:* Tente consultar a visão consolidada regional ou verificar a safra mais recente disponível.`;
  }

  const qNorm = (query || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  // 1. Relatório FPD
  if (targetReport?.id === 'FPD') {
    const isVendedor = /\b(vendedor|vendedores|consultor)\b/i.test(qNorm);
    const first = dbRows[0];
    const safraLabel = first.safra || 'Safra Recente (abr/26)';
    const cidadeLabel = first.cidade ? first.cidade : 'Regional Norte';

    if (isVendedor && first.vendedor) {
      const top = first;
      const topTaxa = getValNum(top, ['taxa_fpd60', 'taxa_fpd60_consolidada', 'taxa_fpd60_regional']);
      const topInst = getValNum(top, ['instalacoes', 'total_instalacoes', 'total_inst']);
      const topFpd = getValNum(top, ['fpd60', 'total_fpd60']);
      const finalTaxaStr = topTaxa > 0 ? topTaxa.toFixed(1) : (topInst > 0 ? ((100.0 * topFpd) / topInst).toFixed(1) : '0.0');

      let out = `💳 *Ranking Oficial de Vendedores · Qualidade de Venda (FPD 60)*\n\n`;
      out += `🧭 *Cenário da Análise:*\n`;
      out += `• 🏷️ *Produto / Serviço:* Serviços Residenciais & Banda Larga (FPD 60 · Inadimplência Inicial)\n`;
      out += `• 📅 *Safra de Referência:* *${safraLabel}*\n`;
      out += `• 📍 *Abrangência Geográfica:* *${cidadeLabel}*\n`;
      out += `• 🏛️ *Fonte dos Dados:* Base Corporativa de Vendas & Faturamento PEP HUB (D1)\n`;
      out += `• ℹ️ *Premissas:* Contratos instalados com 1º pagamento vencido há mais de 60 dias.\n\n`;

      out += `O vendedor mais ofensor identificado na apuração é *${top.vendedor}*`;
      if (top.parceiro) out += ` (${top.parceiro})`;
      if (top.canal) out += ` no canal *${top.canal}*`;
      out += `, com taxa de FPD 60 de *${finalTaxaStr}%* (${Math.round(topFpd).toLocaleString('pt-BR')} contratos inadimplentes em ${Math.round(topInst).toLocaleString('pt-BR')} instalações efetuadas).\n\n`;

      out += `📊 *Principais Vendedores Ofensores:*\n`;
      dbRows.slice(0, 5).forEach((r, idx) => {
        const rTaxaNum = getValNum(r, ['taxa_fpd60', 'taxa_fpd60_consolidada', 'taxa_fpd60_regional']);
        const rInst = getValNum(r, ['instalacoes', 'total_instalacoes', 'total_inst']);
        const rFpd = getValNum(r, ['fpd60', 'total_fpd60']);
        const rFpd30 = getValNum(r, ['taxa_fpd30', 'taxa_fpd30_consolidada', 'taxa_fpd30_regional']);
        const rTaxaStr = rTaxaNum > 0 ? rTaxaNum.toFixed(1) : (rInst > 0 ? ((100.0 * rFpd) / rInst).toFixed(1) : '0.0');

        out += `${idx + 1}. 🔴 *${r.vendedor}* (${r.parceiro || r.canal || ''}): *${rTaxaStr}%* FPD 60 (${Math.round(rFpd).toLocaleString('pt-BR')}/${Math.round(rInst).toLocaleString('pt-BR')} contratos | FPD 30: ${rFpd30.toFixed(1)}%)\n`;
      });

      out += `\n💡 *Sugestão de Aprofundamento:*\nDeseja verificar se os contratos destes vendedores concentram-se em algum produto específico ou checar a taxa de cura da safra?`;
      return out;
    }

    if (first.parceiro) {
      const top = first;
      const cidadeLabel = top.cidade ? ` · ${top.cidade}` : '';
      const topTaxa = getValNum(top, ['taxa_fpd60', 'taxa_fpd60_consolidada', 'taxa_fpd60_regional']);
      const topInst = getValNum(top, ['total_instalacoes', 'total_inst', 'instalacoes']);
      const topFpd60 = getValNum(top, ['total_fpd60', 'fpd60']);
      const finalTopTaxa = topTaxa > 0 ? topTaxa.toFixed(1) : (topInst > 0 ? ((100.0 * topFpd60) / topInst).toFixed(1) : '0.0');

      let out = `💳 *Análise de Ofensores de FPD 60${cidadeLabel} (Regional Norte)*\n\n`;
      out += `🧭 *Cenário da Análise:*\n`;
      out += `• 🏷️ *Produto / Serviço:* Serviços Residenciais & Banda Larga (FPD 60 · Inadimplência Inicial)\n`;
      out += `• 📅 *Safra de Referência:* *${safraLabel}*\n`;
      out += `• 📍 *Abrangência Geográfica:* *${top.cidade || 'Regional Norte'}*\n`;
      out += `• 🏛️ *Fonte dos Dados:* Base Corporativa de Vendas & Faturamento PEP HUB (D1)\n`;
      out += `• ℹ️ *Premissas:* Contratos residenciais com 1º pagamento em aberto após 60 dias.\n\n`;

      out += `O PDV/Parceiro com maior volume de inadimplência inicial (FPD 60) é a *${top.parceiro}*`;
      if (top.cidade) out += ` em *${top.cidade}*`;
      out += `, registrando taxa crítica de *${finalTopTaxa}%* em ${Math.round(topInst).toLocaleString('pt-BR')} contratos instalados.\n\n`;

      out += `📊 *Top PDVs com Maior Risco de Primeiro Pagamento:*\n`;
      dbRows.slice(0, 5).forEach((r, idx) => {
        const rTaxaNum = getValNum(r, ['taxa_fpd60', 'taxa_fpd60_consolidada', 'taxa_fpd60_regional']);
        const rInst = getValNum(r, ['total_instalacoes', 'total_inst', 'instalacoes']);
        const rFpd = getValNum(r, ['total_fpd60', 'fpd60']);
        const rTaxa = rTaxaNum > 0 ? rTaxaNum.toFixed(1) : (rInst > 0 ? ((100.0 * rFpd) / rInst).toFixed(1) : '0.0');
        const icon = Number(rTaxa) >= 50 ? '🔴' : (Number(rTaxa) >= 30 ? '🟠' : '🟡');
        out += `${idx + 1}. ${icon} *${r.parceiro}*: *${rTaxa}%* FPD 60 (${Math.round(rFpd).toLocaleString('pt-BR')} contratos em ${Math.round(rInst).toLocaleString('pt-BR')} inst)\n`;
      });

      out += `\n💡 *Sugestão de Aprofundamento:*\nGostaria de auditar a taxa de aprovação de crédito e recusas antifraude desse parceiro para entender se a causa raiz é fraude na esteira de entrada?`;
      return out;
    }
  }

  // 2. Churn Safra
  if (targetReport?.id === 'CHURN_SAFRA') {
    const isCanalQuery = /\b(canal|canais)\b/i.test(qNorm);
    const isVendedorQuery = /\b(vendedor|vendedores)\b/i.test(qNorm);

    const regionalRow = dbRows.find(r => r.visao === 'REGIONAL') || dbRows[0];
    const parceirosRows = dbRows.filter(r => r.visao === 'PARCEIRO');
    const safraNome = regionalRow?.safra || 'Safra Madura Recente (abr/26)';

    let out = `📉 *Análise de Sobrevivência · Churn Safra D120*\n\n`;
    out += `🧭 *Cenário da Análise:*\n`;
    out += `• 🏷️ *Produto / Serviço:* Banda Larga Residencial (Churn Safra · Sobrevivência D120)\n`;
    out += `• 📅 *Safra Madura de Referência:* *${safraNome}*\n`;
    out += `• 📍 *Abrangência Geográfica:* *Regional Norte (PA, AM, MA, AP, RR)*\n`;
    out += `• 🏛️ *Fonte dos Dados:* Base Oficial de Sobrevivência e Estornos Claro (D1)\n`;
    out += `• ℹ️ *Premissas:* Desconexões até 120 dias da instalação (D120) e contratos sem pagamento (NP120).\n\n`;

    if (isVendedorQuery || isCanalQuery) {
      out += `ℹ️ *Nota de Governança:* A base oficial corporativa de *Churn Safra D120* é consolidada nos níveis *Regional*, *Cidade* e *Parceiro Comercial* (a operadora não disponibiliza vendedores individuais nem segmentação de canais nesta base de estornos).\n\n`;
    }

    if (regionalRow) {
      const regTaxaD120 = getValNum(regionalRow, ['taxa_d120', 'taxa_churn_d120']);
      const regTaxaNp = getValNum(regionalRow, ['taxa_np120']);
      const regInst = getValNum(regionalRow, ['instalacoes', 'total_instalacoes', 'total_inst']);
      const regChurn = getValNum(regionalRow, ['churn_d120']);

      out += `• *Taxa Churn D120 Regional:* *${regTaxaD120.toFixed(2)}%* (${Math.round(regChurn).toLocaleString('pt-BR')} desconexões em ${Math.round(regInst).toLocaleString('pt-BR')} instalações)\n`;
      if (regTaxaNp > 0) out += `• *Taxa Não Pagos (NP 120):* *${regTaxaNp.toFixed(2)}%*\n\n`;
    }

    if (parceirosRows.length > 0) {
      out += `🏢 *Parceiros Comerciais Mais Ofensores de D120:*\n`;
      parceirosRows.slice(0, 5).forEach((p, idx) => {
        const pTaxa = getValNum(p, ['taxa_d120', 'taxa_churn_d120']);
        const pChurn = getValNum(p, ['churn_d120']);
        const pInst = getValNum(p, ['instalacoes', 'total_instalacoes', 'total_inst']);
        out += `${idx + 1}. 🔴 *${p.entidade_nome}*: *${pTaxa.toFixed(1)}%* D120 (${Math.round(pChurn).toLocaleString('pt-BR')}/${Math.round(pInst).toLocaleString('pt-BR')} inst)\n`;
      });
      out += `\n`;
    }

    out += `💡 *Sugestão de Aprofundamento:*\n${isVendedorQuery || isCanalQuery ? 'Para ver a performance comercial de vendedores e canais de venda (PAP, Lojas, Televendas), podemos consultar a base de *FPD*. Deseja abrir os vendedores em FPD?' : 'Deseja detalhar a curva de sobrevivência deste parceiro por cidade?'}`;
    return out;
  }

  // 3. Market Share & Concorrência
  if (targetReport?.id === 'MARKET_SHARE') {
    const qualifiers = detectQualifiers(query);
    const isBandaLarga = dbRows[0]?.produto === 'BANDA_LARGA' || /\b(banda\s*larga|fixa|scm|residencial|fibra|gpon)\b/i.test(qNorm) || qualifiers.isAreaCabeada;
    const is5G = dbRows[0]?.segmento === '5G' || /\b5g\b/i.test(qNorm);
    const marketTotalAcessos = dbRows.reduce((acc, r) => acc + getValNum(r, ['total_acessos', 'acessos']), 0);
    const claroRow = dbRows.find(r => String(r.operadora || '').toLowerCase().includes('claro')) || dbRows[0];
    const mesRef = dbRows[0]?.mes_referencia || '2026-08';
    const mesRefLabel = formatPeriodoLabel(mesRef);
    const cidadeRow = dbRows.find(r => r.cidade && r.cidade !== 'Regional Norte');
    const cidadeLabel = cidadeRow?.cidade ? `${cidadeRow.cidade}${cidadeRow.uf ? `/${cidadeRow.uf}` : ''}` : 'Regional Norte (PA, AM, MA, AP, RR)';

    const prodLabel = isBandaLarga
      ? 'Banda Larga Fixa Residencial (SCM · GPON + HFC)'
      : (is5G ? 'Telefonia Móvel 5G (SMP · Penetração 5G)' : 'Telefonia Móvel (SMP · Pós-pago sem M2M)');
    const fonteLabel = isBandaLarga ? 'Dados Regulatórios Oficiais da Anatel (SCM)' : 'Dados Regulatórios Oficiais da Anatel (SMP)';
    const premissaLabel = isBandaLarga
      ? 'Participação apurada sobre total de acessos ativos de banda larga fixa residencial (serviço 02.BL) e Net Adds mensais.'
      : (is5G
          ? 'Participação apurada sobre acessos ativos em tecnologia 5G e expansão de cobertura.'
          : 'Participação apurada sobre total de acessos pós-pagos puros (excluídos acessos M2M/IoT) e Net Adds mensais.');

    let out = `📊 *Market Share & Dinâmica Competitiva · Anatel*\n\n`;
    out += `🧭 *Cenário da Análise:*\n`;
    out += `• 🏷️ *Produto / Serviço:* ${prodLabel}\n`;
    out += `• 📅 *Período de Referência:* *${mesRefLabel}* · Posição Oficial Anatel\n`;
    out += `• 📍 *Abrangência Geográfica:* *${cidadeLabel}*\n`;
    out += `• 🏛️ *Fonte dos Dados:* ${fonteLabel}\n`;
    out += `• ℹ️ *Premissas:* ${premissaLabel}\n\n`;

    if (qualifiers.isAreaCabeada) {
      out += `ℹ️ *Nota Regulatória sobre Área Cabeada:*\nA base oficial pública da Anatel apura o Market Share sobre o mercado total do município/regional no serviço SCM (Banda Larga Fixa). O recorte restrito a *"Área Cabeada"* (Homes Passed / rede passada HFC/FTTH) é uma métrica interna de engenharia e rede não pública na Anatel. Apresentando os dados oficiais consolidados do mercado total de Banda Larga Fixa Residencial:\n\n`;
    }

    if (qualifiers.isGrandesMercados) {
      out += `🏛️ *Visão de Grandes Mercados (GMs - Belém, Manaus, São Luís):*\n` +
        `• *Belém/PA:* Claro líder com *33.88%* de share em Banda Larga (+131 Net Adds) e *44.14%* em Móvel (+4.704 Net Adds)\n` +
        `• *Manaus/AM:* Claro líder com *32.19%* de share em Banda Larga (-362 Net Adds) e forte presença móvel\n` +
        `• *São Luís/MA:* Claro vice-líder consolidada com *18.45%* de share em Banda Larga\n\n`;
    }

    if (qualifiers.isMercadosDesenvolvimento) {
      out += `🏛️ *Visão de Mercados em Desenvolvimento (MEDs):*\n` +
        `Nos polos *Macapá/AP, Boa Vista/RR, Santarém/PA, Marabá/PA e Imperatriz/MA*, os provedores locais (Competitivas/ISPs) concentram a maior fatia de fibra óptica no interior, com a Claro operando como alternativa premium nas capitais e polos regionais.\n\n`;
    }

    const claroShare = getValNum(claroRow, ['market_share_pct', 'market_share_recente', 'share_pct']);
    const claroAcessos = getValNum(claroRow, ['total_acessos', 'acessos']);
    const claroMediaNet = getValNum(claroRow, ['media_net_adds', 'net_adds']);
    const claroTotalNet = getValNum(claroRow, ['total_net_adds', 'net_adds']);
    const claroNetSign = claroMediaNet > 0 ? '+' : '';

    if (isBandaLarga) {
      if (cidadeRow) {
        const seg2 = dbRows[1] ? `${dbRows[1].operadora} (${Number(dbRows[1].market_share_pct).toFixed(2)}%)` : '';
        const seg3 = dbRows[2] ? `${dbRows[2].operadora} (${Number(dbRows[2].market_share_pct).toFixed(2)}%)` : '';
        out += `🏆 A *Claro* é a líder absoluta de Banda Larga Fixa Residencial em *${cidadeLabel}* com *${Number(claroShare).toFixed(2)}%* de Market Share (${Math.round(claroAcessos).toLocaleString('pt-BR')} acessos ativos) e saldo de *${claroNetSign}${Math.round(claroMediaNet).toLocaleString('pt-BR')}* Net Adds no período, à frente de ${seg2} e ${seg3}.\n\n`;
      } else {
        const ispsRow = dbRows.find(r => /isp|competitiva/i.test(r.operadora)) || dbRows[0];
        const ispsShare = ispsRow ? Number(ispsRow.market_share_pct).toFixed(2) : '66.27';
        const ispsAc = ispsRow ? Math.round(ispsRow.acessos).toLocaleString('pt-BR') : '2.250.782';
        const oiRow = dbRows.find(r => r.operadora === 'Oi');
        const vivoRow = dbRows.find(r => r.operadora === 'Vivo');
        const oiStr = oiRow ? `Oi (${Number(oiRow.market_share_pct).toFixed(2)}%)` : '';
        const vivoStr = vivoRow ? `Vivo (${Number(vivoRow.market_share_pct).toFixed(2)}%)` : '';
        out += `🏆 Na *Regional Norte*, os provedores locais (*Competitivas/ISPs*) somam a maior fatia de Banda Larga com *${ispsShare}%* de Market Share (${ispsAc} acessos), reflexo da capilaridade da fibra óptica no interior. Entre as grandes operadoras nacionais, a *Claro* é a **líder consolidada** com *${Number(claroShare).toFixed(2)}%* de share (${Math.round(claroAcessos).toLocaleString('pt-BR')} acessos ativos) e saldo positivo de *${claroNetSign}${Math.round(claroMediaNet).toLocaleString('pt-BR')}* Net Adds, à frente de ${oiStr} e ${vivoStr}.\n\n`;
      }
    } else {
      if (cidadeRow) {
        const seg2 = dbRows[1] ? `${dbRows[1].operadora} (${Number(dbRows[1].market_share_pct).toFixed(2)}%)` : '';
        const seg3 = dbRows[2] ? `${dbRows[2].operadora} (${Number(dbRows[2].market_share_pct).toFixed(2)}%)` : '';
        out += `🏆 A *Claro* lidera com folga em *${cidadeLabel}* com *${Number(claroShare).toFixed(2)}%* de Market Share consolidado em Pós-pago sem M2M (${Math.round(claroAcessos).toLocaleString('pt-BR')} acessos ativos) e forte tração de crescimento (${claroNetSign}${Math.round(claroMediaNet).toLocaleString('pt-BR')} net adds no período), à frente de ${seg2} e ${seg3}.\n\n`;
      } else {
        const vivoRow = dbRows.find(r => String(r.operadora || '').toLowerCase().includes('vivo')) || dbRows[0];
        const vivoShare = getValNum(vivoRow, ['market_share_pct']);
        const vivoAcessos = getValNum(vivoRow, ['total_acessos', 'acessos']);
        out += `🏆 Na *Regional Norte*, a *Vivo* detém a maior base acumulada de Pós-pago sem M2M com *${Number(vivoShare).toFixed(2)}%* (${Math.round(vivoAcessos).toLocaleString('pt-BR')} acessos). A *Claro* posiciona-se logo em seguida com *${Number(claroShare).toFixed(2)}%* de Market Share (${Math.round(claroAcessos).toLocaleString('pt-BR')} acessos), destacando-se como a **líder absoluta em adições líquidas** (+27.120 Net Adds no período), capturando 48,5% de todo o crescimento líquido regional.\n\n`;
      }
    }

    out += `📈 *Comparativo Completo com a Concorrência:*\n`;
    dbRows.forEach((r, idx) => {
      const medal = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : '🔻'));
      let share = getValNum(r, ['market_share_pct', 'market_share_recente', 'share_pct']);
      if (share === 0 && marketTotalAcessos > 0) {
        share = (100.0 * getValNum(r, ['total_acessos', 'acessos'])) / marketTotalAcessos;
      }
      const mediaNet = getValNum(r, ['media_net_adds', 'net_adds']);
      const acCount = getValNum(r, ['total_acessos', 'acessos']);
      const netSign = mediaNet > 0 ? '+' : '';

      out += `• ${medal} *${r.operadora}:* *${Number(share).toFixed(2)}%* share (${Math.round(acCount).toLocaleString('pt-BR')} acessos) | Média/Saldo Net Adds: *${netSign}${Math.round(mediaNet).toLocaleString('pt-BR')}*\n`;
    });

    if (!isBandaLarga && cidadeRow && /belem/i.test(cidadeLabel)) {
      out += `\n💡 *Visão Complementar de Banda Larga Fixa:* Em Belém, a Claro também lidera em Banda Larga Residencial com *33.88%* de Market Share (110.219 acessos) e saldo de *+131* Net Adds.\n`;
    }

    out += `\n💡 *Sugestão de Aprofundamento:*\n${cidadeRow ? `Deseja comparar a dinâmica competitiva de ${cidadeLabel} com a média consolidada da Regional Norte ou analisar a evolução histórica dos Net Adds?` : 'Deseja detalhar o Market Share por cidade (ex: Belém, Manaus, São Luís) ou verificar a evolução recente dos Net Adds?'}`;
    return out;
  }

    // 4. Churn Banda Larga & Metas RxO
  if (targetReport?.id === 'CHURN_BL' || targetReport?.id === 'CHURN_PME') {
    const isNov = /\b(nov|novembro)\b/i.test(qNorm);
    const recRow = dbRows.find(r => r.tipo_visao === 'TOTAL' && r.segmento === 'Banda Larga Total') || dbRows[0];
    const segmentoNome = recRow?.segmento || (targetReport?.id === 'CHURN_PME' ? 'Banda Larga PME' : 'Banda Larga Total');
    const mesRefLabel = recRow?.mes_referencia ? formatPeriodoLabel(recRow.mes_referencia) : 'Outubro/2026';

    let out = `📉 *Painel de Desconexões & RxO · Churn ${segmentoNome}*\n\n`;
    out += `🧭 *Cenário da Análise:*\n`;
    out += `• 🏷️ *Produto / Serviço:* ${segmentoNome} (${segmentoNome.includes('PME') ? 'Conexão Negócios PME' : 'Residencial + PME'})\n`;
    out += `• 📅 *Período de Referência:* *${mesRefLabel}*\n`;
    out += `• 📍 *Abrangência Geográfica:* *Regional Norte · Consolidação Executiva*\n`;
    out += `• 🏛️ *Fonte dos Dados:* Base Oficial de Desconexões e Orçamento RxO Claro (D1)\n`;
    out += `• ℹ️ *Premissas:* Desconexões voluntárias e involuntárias vs meta orçada e acompanhamento YTD.\n\n`;

    if (isNov) {
      out += `ℹ️ *Transparência de Período:* O mês de *Novembro/2026* ainda não possui fechamento consolidado na base oficial (o mês mais recente fechado é *${mesRefLabel}*).\n\n`;
    }

    if (recRow) {
      const volReal = getValNum(recRow, ['vol_real']);
      const volOrc = getValNum(recRow, ['vol_orc']);
      const taxaReal = getValNum(recRow, ['taxa_real']);
      const taxaOrc = getValNum(recRow, ['taxa_orc']);
      const ytdReal = getValNum(recRow, ['ytd_real']);
      const ytdOrc = getValNum(recRow, ['ytd_orc']);

      out += `📊 *Fechamento Oficial Recente (${recRow.mes_referencia}):*\n`;
      out += `• *Volume Real:* *${volReal.toLocaleString('pt-BR')}* desconexões vs meta orçada de *${volOrc.toLocaleString('pt-BR')}*\n`;
      out += `• *Taxa de Churn Real:* *${taxaReal.toFixed(2)}%* vs orçamento de *${taxaOrc.toFixed(2)}%*\n\n`;

      if (ytdReal > 0) {
        out += `📈 *Acumulado YTD 2026:*\n`;
        out += `• *YTD Real 2026:* *${ytdReal.toLocaleString('pt-BR')}* desconexões\n`;
        out += `• *YTD Orçado 2026:* *${ytdOrc.toLocaleString('pt-BR')}* desconexões\n\n`;
      }
    }

    out += `💡 *Sugestão de Aprofundamento:*\nDeseja comparar a quebra do churn entre visão Voluntária vs Involuntária (inadimplência) para identificar o principal ofensor do desvio orçamentário?`;
    return out;
  }

  // 5. Relatório Aprovação de Crédito & Antifraude
  if (targetReport?.id === 'CREDITO') {
    const first = dbRows[0];
    const mesRefLabel = formatPeriodoLabel(first?.mes_referencia || '2026-09');
    const cidadeLabel = first?.cidade && first.cidade !== 'Regional Norte' ? first.cidade : 'Regional Norte';

    let out = `🛡️ *Painel de Aprovação de Crédito & Antifraude*\n\n`;
    out += `🧭 *Cenário da Análise:*\n`;
    out += `• 🏷️ *Produto / Serviço:* Esteira de Crédito Comercial & Antifraude (Propostas Residenciais)\n`;
    out += `• 📅 *Período de Referência:* *${mesRefLabel}*\n`;
    out += `• 📍 *Abrangência Geográfica:* *${cidadeLabel}*\n`;
    out += `• 🏛️ *Fonte dos Dados:* Motor de Risco e Política de Crédito Claro (D1)\n`;
    out += `• ℹ️ *Premissas:* Taxa de aprovação sobre propostas consultadas, recusas de política e bloqueios antifraude.\n\n`;

    const topAprov = getValNum(first, ['taxa_aprovacao', 'taxa_aprovacao_regional', 'taxa_aprovacao_consolidada']);
    const cons = getValNum(first, ['total_consultas', 'consultas']);
    const aprov = getValNum(first, ['total_aprovados', 'aprovados']);
    const fraudes = getValNum(first, ['total_recusas_antifraude', 'recusas_antifraude']);

    out += `📊 *Resumo da Eficiência da Esteira:*\n`;
    out += `• *Taxa de Aprovação:* *${topAprov.toFixed(1)}%* (${Math.round(aprov).toLocaleString('pt-BR')} propostas aprovadas em ${Math.round(cons).toLocaleString('pt-BR')} consultas)\n`;
    if (fraudes > 0) out += `• *Recusas por Antifraude:* *${Math.round(fraudes).toLocaleString('pt-BR')}* bloqueios\n\n`;

    if (dbRows.length > 1) {
      out += `📋 *Detalhamento por Entidade/Canal:*\n`;
      dbRows.slice(0, 5).forEach((r, idx) => {
        const ent = r.pdv_ou_parceiro ? `*${r.pdv_ou_parceiro}*` : (r.cidade ? `*${r.cidade}*` : `Entidade ${idx + 1}`);
        const rTaxa = getValNum(r, ['taxa_aprovacao', 'taxa_aprovacao_consolidada']);
        const rCons = getValNum(r, ['consultas', 'total_consultas']);
        out += `${idx + 1}. ${ent}: *${rTaxa.toFixed(1)}%* aprovação (${Math.round(rCons).toLocaleString('pt-BR')} consultas)\n`;
      });
      out += `\n`;
    }

    out += `💡 *Sugestão de Aprofundamento:*\nDeseja cruzar esses índices com a taxa de inadimplência (FPD 60) desse canal para verificar a eficácia do filtro de crédito?`;
    return out;
  }

  // Fallback analítico determinístico
  return formatAnalyticalAnswer(dbRows, query, targetReport);
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

    // Se for ranking consolidado (cidade, parceiro, vendedor)
    if (first.taxa_fpd60_consolidada !== undefined || (first.parceiro !== undefined && first.taxa_fpd60 !== undefined)) {
      const isParceiro = first.parceiro !== undefined;
      const isVendedor = first.vendedor !== undefined;
      const titleType = isVendedor ? 'Vendedores' : isParceiro ? 'PDVs / Parceiros' : 'Cidades';
      let out = `💳 *Ranking Oficial de ${titleType} · FPD 60 (Regional Norte)*\n\n`;
      for (const r of rows.slice(0, 5)) {
        const entName = r.vendedor ? `*${r.vendedor}* (${r.parceiro || r.canal || ''})` :
                        r.parceiro ? `*${r.parceiro}*` :
                        r.cidade ? `*${r.cidade}*` :
                        r.canal ? `*${r.canal}*` : 'Entidade';
        const taxaNum = getValNum(r, ['taxa_fpd60_consolidada', 'taxa_fpd60', 'taxa_fpd60_regional']);
        const instVal = getValNum(r, ['total_instalacoes', 'total_inst', 'instalacoes']);
        const fpdCount = getValNum(r, ['total_fpd60', 'fpd60']);
        const finalTaxa = taxaNum > 0 ? taxaNum.toFixed(1) : (instVal > 0 ? ((100.0 * fpdCount) / instVal).toFixed(1) : '0.0');
        const taxa = `FPD 60: *${finalTaxa}%*`;
        const fpd60 = fpdCount > 0 ? `(${Math.round(fpdCount).toLocaleString('pt-BR')} contratos)` : '';
        const inst = instVal > 0 ? `em ${Math.round(instVal).toLocaleString('pt-BR')} inst` : '';
        out += `• ${entName}: ${[taxa, fpd60, inst].filter(Boolean).join(' ')}\n`;
      }
      out += `\n_Critério: ordenado por maior ofensor de primeiro pagamento na safra._`;
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
    const isBL = rows[0]?.produto === 'BANDA_LARGA';
    const is5G = rows[0]?.segmento === '5G';
    const mesRef = rows[0]?.mes_referencia ? formatPeriodoLabel(rows[0].mes_referencia) : 'Posição Oficial Recente';
    const cidRow = rows.find(r => r.cidade && r.cidade !== 'Regional Norte');
    const cidLabel = cidRow?.cidade ? `${cidRow.cidade}${cidRow.uf ? `/${cidRow.uf}` : ''}` : 'Regional Norte (PA, AM, MA, AP, RR)';
    const prodLabel = isBL ? 'Banda Larga Fixa Residencial (SCM · GPON + HFC)' : (is5G ? 'Telefonia Móvel 5G (SMP · Penetração 5G)' : 'Telefonia Móvel (SMP · Pós-pago sem M2M)');
    const fonteLabel = isBL ? 'Dados Regulatórios Oficiais da Anatel (SCM)' : 'Dados Regulatórios Oficiais da Anatel (SMP)';

    let out = `📊 *Relatório Oficial de Market Share & Anatel · Regional Norte*\n\n`;
    out += `🧭 *Cenário da Análise:*\n`;
    out += `• 🏷️ *Produto / Serviço:* ${prodLabel}\n`;
    out += `• 📅 *Período de Referência:* *${mesRef}*\n`;
    out += `• 📍 *Abrangência Geográfica:* *${cidLabel}*\n`;
    out += `• 🏛️ *Fonte dos Dados:* ${fonteLabel}\n`;
    out += `• ℹ️ *Premissas:* Participação apurada sobre acessos ativos em serviço e Net Adds mensais.\n\n`;
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
 * Constrói Metadados Ricos (URL parametrizada para o relatório oficial, chips de aprofundamento)
 */
export function buildRichMetadataForReport(targetReport, query, dbRows) {
  const norm = (query || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const entities = extractQueryEntities(query);
  const city = entities?.matchedCity || (dbRows && dbRows[0]?.cidade && dbRows[0].cidade !== 'Regional Norte' ? dbRows[0].cidade : null);
  const repId = targetReport?.id;
  let reportUrl = '/';
  let reportName = targetReport?.name || 'Relatório Oficial';
  let chips = [];

  if (repId === 'MARKET_SHARE') {
    const isBandaLarga = dbRows?.[0]?.produto === 'BANDA_LARGA' || entities?.isBandaLargaQuery || /\b(banda\s*larga|residencial|fixa|scm)\b/i.test(norm);
    if (isBandaLarga) {
      reportName = city ? `Market Share Residencial (${city})` : 'Market Share Residencial Regional';
      reportUrl = city ? `/market-share-residencial/?cidade=${encodeURIComponent(city)}` : '/market-share-residencial/';
      chips = [
        { label: city ? `📱 Ver Móvel em ${city}` : '📱 Ver Móvel Regional', query: city ? `qual o market share móvel em ${city}?` : 'qual o market share móvel na Regional Norte?' },
        { label: '🗺️ Comparar Regional Norte', query: 'qual o market share residencial da Regional Norte?' },
        { label: '📈 Ver Saldo de Net Adds', query: city ? `qual o saldo de net adds de banda larga em ${city}?` : 'qual o saldo de net adds de banda larga na Regional Norte?' }
      ];
    } else {
      reportName = city ? `Market Share Móvel (${city})` : 'Market Share Móvel Regional';
      reportUrl = city ? `/market-share-movel/?cidade=${encodeURIComponent(city)}&segmento=POS_PAGO_SEM_M2M` : '/market-share-movel/';
      chips = [
        { label: city ? `🌐 Ver Banda Larga em ${city}` : '🌐 Ver Banda Larga Regional', query: city ? `qual o market share de banda larga em ${city}?` : 'qual o market share de banda larga na Regional Norte?' },
        { label: '📶 Penetração do 5G', query: city ? `qual o market share 5G em ${city}?` : 'qual a penetração de 5G na Regional Norte?' },
        { label: '📈 Ranking de Net Adds', query: 'quem lidera as adições líquidas de pós-pago na Regional?' }
      ];
    }
  } else if (repId === 'CHURN_BL' || repId === 'CHURN_PME') {
    reportName = city ? `Churn Banda Larga (${city})` : 'Churn Banda Larga Regional';
    reportUrl = city ? `/churn-bl/?cidade=${encodeURIComponent(city)}` : '/churn-bl/';
    chips = [
      { label: city ? `🏢 Ver PME em ${city}` : '🏢 Ver Churn PME', query: city ? `qual a taxa de churn PME em ${city}?` : 'qual a taxa de churn no segmento PME?' },
      { label: '📍 Ranking de Cidades', query: 'ranking de cidades com pior churn banda larga' },
      { label: '📊 Orçado vs Real (RxO)', query: 'qual o desvio de churn real contra o orçado?' },
      { label: city ? `🌱 Ver Churn Safra em ${city}` : '🌱 Ver Churn Safra D120', query: city ? `qual o churn safra em ${city}?` : 'qual a taxa de churn safra D120 Regional?' }
    ];
  } else if (repId === 'CHURN_SAFRA') {
    reportName = city ? `Churn Safra D120 (${city})` : 'Churn Safra D120 Regional';
    reportUrl = city ? `/churn/?cidade=${encodeURIComponent(city)}&safra=mai%2F26` : '/churn/?safra=mai%2F26&visao=PARCEIRO';
    chips = [
      { label: '🤝 Piores Parceiros D120', query: 'quais os piores parceiros em Churn Safra?' },
      { label: '🏙️ Ranking Cidades Safra', query: 'ranking de cidades com pior churn safra' },
      { label: '🌱 Safras em Aberto', query: 'como estão as safras em aberto?' },
      { label: '💳 Ver Canais em FPD', query: 'quais os canais de venda com pior FPD?' }
    ];
  } else if (repId === 'FPD') {
    reportName = city ? `FPD Residencial (${city})` : 'FPD Residencial Regional';
    reportUrl = city ? `/fpd-residencial/?cidade=${encodeURIComponent(city)}&safra=mai%2F26` : '/fpd-residencial/?safra=mai%2F26';
    chips = [
      { label: '🚪 FPD por Canal (PAP/Lojas)', query: 'qual o FPD por canal de venda?' },
      { label: '📍 Ranking Cidades FPD', query: 'ranking de cidades com pior FPD 60' },
      { label: '💊 Taxa de Cura (30d ➔ 60d)', query: 'qual a taxa de cura da última safra?' },
      { label: '👔 Vendedores Ofensores', query: 'quais os vendedores com maior taxa de FPD 60?' }
    ];
  } else if (repId === 'CREDITO') {
    reportName = city ? `Aprovação de Crédito (${city})` : 'Aprovação de Crédito Regional';
    reportUrl = city ? `/aprovacao-credito/?cidade=${encodeURIComponent(city)}` : '/aprovacao-credito/';
    chips = [
      { label: '⚠️ Cidades com Mais Antifraude', query: 'quais cidades tiveram mais recusa antifraude?' },
      { label: '🚪 Aprovação por Canal', query: 'qual o canal com menor aprovação de crédito?' },
      { label: '🛡️ Volume de Alto Risco', query: 'qual o percentual de contratos em alto risco?' }
    ];
  } else if (repId === 'SPEECH') {
    reportName = 'Speech Analytics';
    reportUrl = '/speech/';
    chips = [
      { label: '🗣️ Top Motivos de Cancelamento', query: 'quais os principais motivos de cancelamento no Speech?' },
      { label: '💰 Motivo "Acha Caro"', query: 'qual o percentual do motivo acha caro no Speech?' }
    ];
  } else if (repId === 'MOTIVOS') {
    reportName = 'Motivos de Procura & OS';
    reportUrl = '/motivos-os/';
    chips = [
      { label: '🔧 Motivos com Mais OS Técnica', query: 'quais motivos de procura geram mais visita técnica?' },
      { label: '🏙️ Taxa de OS por Cidade', query: 'qual a taxa de OS técnica em Belém e Manaus?' }
    ];
  }

  return { reportUrl, reportName, chips };
}

/**
 * Execução Text-to-SQL Segura no D1 com Escopo Rígido de Relatório
 */
async function executeAnalyticalPipeline(env, query, userPhone, userScope, targetReport, channel = 'whatsapp') {
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

  // 4. Síntese Cognitiva com Inteligência LLM (Cérebro Pensante - Gemini 2.5 Flash)
  let answer = await synthesizeAnalyticalAnswerWithLLM(env, query, dbRows, targetReport, safeSql, userPhone, userScope, channel);
  if (!answer || !answer.trim()) {
    answer = formatAnalyticalAnswer(dbRows, query, targetReport);
  }

  const richMeta = buildRichMetadataForReport(targetReport, query, dbRows);

  return {
    success: true,
    sql: safeSql,
    answer,
    rowsCount: dbRows.length,
    targetReport: targetReport.id,
    reportUrl: richMeta.reportUrl,
    reportName: richMeta.reportName,
    chips: richMeta.chips,
    disclaimer: "⚠️ Respostas geradas com base no contexto D1 do PEP HUB. Supervisão humana recomendada."
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
export function formatCorporateGlossaryDirect(chunks, query, channel = 'whatsapp') {
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
  if (channel === 'web') {
    out += `• Digite sua pergunta sobre qualquer indicador (ex: FPD, Churn, Safra, Crédito, Market Share).\n`;
    out += `• Ou clique nas perguntas predefinidas acima para uma consulta rápida.`;
  } else {
    out += `• Envie *#dados* para consultar indicadores operacionais em tempo real.\n`;
    out += `• Envie *#ajuda* para o catálogo completo de comandos e métricas.`;
  }
  return out;
}

/**
 * Execução Semantic RAG (Perguntas Conceituais e Regras de Negócio)
 * Otimizado com Fast-Retrieval no D1 (< 25ms) e Fallback Gemini Inteligente
 */
async function executeConceptualPipeline(env, query, channel = 'whatsapp') {
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
    const directAnswer = formatCorporateGlossaryDirect(chunks, query, channel);
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
  const channelContext = channel === 'web' ? 'portal web Pephub' : 'WhatsApp';
  const systemInstruction = `Você é o Consultor Especialista de Regras de Negócio da Claro Regional Norte (Pephub).
Responda à dúvida conceitual do usuário utilizando EXCLUSIVAMENTE o contexto das Regras Oficiais fornecidas abaixo.

DIRETRIZES:
1. Explique de forma didática, clara e objetiva para o ${channelContext}.
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
function handleOutOfScopeQuery(phone = '5591980547171', channel = 'whatsapp') {
  return {
    success: true,
    answer: buildBaseSelectionMenu(phone, channel)
  };
}

/**
 * Pipeline Central do Roteador (Ask Handler)
 */
export async function processBotQuery(env, phone, query, sessionUser = null, channel = 'whatsapp') {
  const isWeb = channel === 'web' || String(phone || '').startsWith('web_');
  const activeChannel = isWeb ? 'web' : 'whatsapp';

  if (!query || !query.trim()) {
    return {
      success: true,
      answer: buildBaseSelectionMenu(phone, activeChannel),
      intent: 'MENU_PASSO_1',
      phone
    };
  }

  // 1. Validação de Autorização e Escopo
  const auth = await verifyBotSender(env, phone, sessionUser);
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
  const cleanDigits = String(phone || '').startsWith('web_') ? String(phone || '') : String(phone || '').replace(/\D/g, '');
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
      answer: buildBaseSelectionMenu(phone, activeChannel),
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
      return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
    }

    const rep = getReportById(activeSession.reportId);

    if (activeSession.menu === 'LIST_PARCEIRO_CANAL') {
      const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
      await saveSession(updated);
      return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_PARCEIRO_CANAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_PARCEIRO_CIDADE') {
      if (activeSession.selectedChannel && activeSession.selectedChannel !== 'TODOS') {
        const updated = { ...activeSession, menu: 'LIST_PARCEIRO_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildChannelListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
      } else {
        const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
      }
    }
    if (activeSession.menu === 'LIST_PARCEIRO_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CIDADE' };
      await saveSession(updated);
      return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, `Ranking 10 Piores Parceiros (${activeSession.selectedChannel || 'Geral'}, activeChannel)`), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_CANAL_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_CANAL_CIDADE' };
      await saveSession(updated);
      return { success: true, answer: buildChannelCityPromptMenu(rep, updated, phone, 'Ranking Canais', activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_CANAL_CIDADE') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_CIDADE_CANAL') {
      const updated = { ...activeSession, menu: 'PROMPT_CIDADE_CANAL' };
      await saveSession(updated);
      return { success: true, answer: buildCityChannelPromptMenu(rep, updated, phone, 'Ranking Cidades', activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_CIDADE_CANAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MKT_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_MKT_RESIDENCIAL' };
      await saveSession(updated);
      return { success: true, answer: buildCityPromptMenu(rep, updated, phone, 'Market Share Residencial', activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MKT_RESIDENCIAL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MKT_DDD') {
      const updated = { ...activeSession, menu: 'PROMPT_MKT_MOVEL' };
      await saveSession(updated);
      return { success: true, answer: buildDddPromptMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MKT_MOVEL') {
      const updated = { ...activeSession, menu: 'SELECT_ACTION' };
      await saveSession(updated);
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_SPEECH_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_SPEECH_ABRANGENCIA' };
      await saveSession(updated);
      return { success: true, answer: buildSpeechPromptMenu(phone, activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_SPEECH_ABRANGENCIA') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'LIST_MOTIVOS_CIDADE') {
      const updated = { ...activeSession, menu: 'PROMPT_MOTIVOS_ABRANGENCIA' };
      await saveSession(updated);
      return { success: true, answer: buildMotivosPromptMenu(phone, activeChannel), intent: 'MENU', phone };
    }
    if (activeSession.menu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'SELECT_ACTION') {
      if (rep.id === 'FPD' || rep.id === 'CREDITO') {
        const updated = { ...activeSession, menu: 'SELECT_PRODUCT' };
        await saveSession(updated);
        return { success: true, answer: buildProductSelectionMenu(rep, phone, activeChannel), intent: 'MENU', phone };
      }
      if (rep.id === 'CHURN_BL') {
        const updated = { ...activeSession, menu: 'SELECT_SEGMENT' };
        await saveSession(updated);
        return { success: true, answer: buildSegmentSelectionMenu(rep, phone, activeChannel), intent: 'MENU', phone };
      }
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
    }

    if (activeSession.menu === 'SELECT_PRODUCT' || activeSession.menu === 'SELECT_SEGMENT') {
      await clearSession();
      return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
    }

    await clearSession();
    return { success: true, answer: buildBaseSelectionMenu(phone, activeChannel), intent: 'MENU', phone };
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
        return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, `Ranking 10 Piores Parceiros (${ch.name}, activeChannel)`), intent: 'MENU', phone };
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
        return { success: true, answer: buildChannelListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
      } else {
        const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CIDADE', selectedChannel: 'TODOS' };
        await saveSession(updated);
        return { success: true, answer: buildPartnerCityPromptMenu(rep, updated, phone, 'Ranking 10 Piores Parceiros (Todos os Canais, activeChannel)'), intent: 'MENU', phone };
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
        return { success: true, answer: buildCityListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
      } else {
        let card = await executePartnerRankingCard(env, rep, { ...activeSession, selectedCity: 'TODAS' });
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_CANAL_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_CIDADE_CANAL' };
        await saveSession(updated);
        return { success: true, answer: buildChannelListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_MKT_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
        const updated = { ...activeSession, menu: 'SELECT_ACTION' };
        await saveSession(updated);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const updated = { ...activeSession, menu: 'LIST_MKT_DDD' };
        await saveSession(updated);
        return { success: true, answer: buildDddListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks(rep, { isSubmenu: true }, phone, activeChannel);
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
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone, activeChannel);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Últimos 3 meses
          let card = await executeLast3MonthsCard(env, rep, activeSession);
          card += buildActionCardFooterLinks(rep, 2, activeSession, phone, activeChannel);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 3) { // Ranking 10 Piores Parceiros
          const updated = { ...activeSession, menu: 'PROMPT_PARCEIRO_CANAL' };
          await saveSession(updated);
          return { success: true, answer: buildPartnerChannelPromptMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
        } else if (act === 4) { // Ranking Canais (Últimos 3 meses)
          const updated = { ...activeSession, menu: 'PROMPT_CANAL_CIDADE' };
          await saveSession(updated);
          return { success: true, answer: buildChannelCityPromptMenu(rep, updated, phone, `Ranking Canais (${rep.name}, activeChannel)`), intent: 'MENU', phone };
        } else if (act === 5) { // Ranking Cidades (Últimos 3 meses)
          const updated = { ...activeSession, menu: 'PROMPT_CIDADE_CANAL' };
          await saveSession(updated);
          return { success: true, answer: buildCityChannelPromptMenu(rep, updated, phone, `Ranking Cidades (${rep.name}, activeChannel)`), intent: 'MENU', phone };
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
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone, activeChannel);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Últimos 3 meses
          let card = await executeChurnBlLast3MonthsCard(env, activeSession);
          card += buildActionCardFooterLinks(rep, 2, activeSession, phone, activeChannel);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 3) { // Ranking Cidades
          let card = await executeChurnBlCityRankingCard(env, activeSession);
          card += buildActionCardFooterLinks(rep, 3, activeSession, phone, activeChannel);
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
          card += buildActionCardFooterLinks(rep, 1, activeSession, phone, activeChannel);
          return { success: true, answer: card, intent: 'ANALITICA', phone };
        } else if (act === 2) { // Residencial
          const updated = { ...activeSession, menu: 'PROMPT_MKT_RESIDENCIAL' };
          await saveSession(updated);
          return { success: true, answer: buildCityPromptMenu(rep, updated, phone, 'Market Share Residencial', activeChannel), intent: 'MENU', phone };
        } else if (act === 3) { // Móvel
          const updated = { ...activeSession, menu: 'PROMPT_MKT_MOVEL' };
          await saveSession(updated);
          return { success: true, answer: buildDddPromptMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
      return { success: true, answer: buildActionSelectionMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
    }
  }

  // S1) SE ESTÁ NO MENU: PROMPT_SPEECH_ABRANGENCIA (1: Resumo Geral, 2: Filtrar por Cidade)
  if (activeSession && activeSession.menu === 'PROMPT_SPEECH_ABRANGENCIA') {
    const optMatch = norm.match(/^([1-2])$/);
    if (optMatch) {
      if (optMatch[1] === '1') {
        let card = await executeSpeechCard(env, 'Regional Norte', phone);
        card += buildCardFooterLinks({ name: 'Speech Analytics' }, { isSubmenu: false }, phone, activeChannel);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'LIST_SPEECH_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks({ name: 'Speech Analytics' }, { isSubmenu: true }, phone, activeChannel);
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
        card += buildCardFooterLinks({ name: 'Motivos & OS' }, { isSubmenu: false }, phone, activeChannel);
        return { success: true, answer: card, intent: 'ANALITICA', phone };
      } else {
        const rep = getReportById(activeSession.reportId);
        const updated = { ...activeSession, menu: 'LIST_MOTIVOS_CIDADE' };
        await saveSession(updated);
        return { success: true, answer: buildCityListMenu(rep, updated, phone, activeChannel), intent: 'MENU', phone };
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
        card += buildCardFooterLinks({ name: 'Motivos & OS' }, { isSubmenu: true }, phone, activeChannel);
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
        return { success: true, answer: buildProductSelectionMenu(selectedReport, phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'SELECT_SEGMENT') {
        return { success: true, answer: buildSegmentSelectionMenu(selectedReport, phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_SPEECH_ABRANGENCIA') {
        return { success: true, answer: buildSpeechPromptMenu(phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
        return { success: true, answer: buildMotivosPromptMenu(phone, activeChannel), intent: 'MENU', phone };
      } else {
        return { success: true, answer: buildActionSelectionMenu(selectedReport, newSession, phone, activeChannel), intent: 'MENU', phone };
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
        return { success: true, answer: buildProductSelectionMenu(selectedReport, phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'SELECT_SEGMENT') {
        return { success: true, answer: buildSegmentSelectionMenu(selectedReport, phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_SPEECH_ABRANGENCIA') {
        return { success: true, answer: buildSpeechPromptMenu(phone, activeChannel), intent: 'MENU', phone };
      } else if (nextMenu === 'PROMPT_MOTIVOS_ABRANGENCIA') {
        return { success: true, answer: buildMotivosPromptMenu(phone, activeChannel), intent: 'MENU', phone };
      } else {
        return { success: true, answer: buildActionSelectionMenu(selectedReport, newSession, phone, activeChannel), intent: 'MENU', phone };
      }
    }
  }

  // 2. Classificação de Intenção Semântica (Router)
  const classification = await classifyIntent(env, cleanQuery);
  const intent = classification.intent;

  // 3. Roteamento Especializado
  if (intent === 'FORA_ESCOPO') {
    return {
      ...handleOutOfScopeQuery(phone, activeChannel),
      intent,
      phone,
    };
  }

  if (intent === 'CONCEITUAL') {
    const conceptualResult = await executeConceptualPipeline(env, cleanQuery, activeChannel);
    return {
      ...conceptualResult,
      intent,
      phone,
    };
  }

  // Intenção Analítica (Roteamento de Relatório-Alvo com Anti-Cruzamento de Indicadores)
  const resolution = await resolveTargetReport(env, cleanQuery, phone, activeChannel);
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
      phone,
      reportUrl: resolution.reportUrl,
      reportName: resolution.reportName,
      chips: resolution.chips,
      messageId: 'msg_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7),
      disclaimer: "⚠️ Respostas geradas com base no contexto D1 do PEP HUB. Supervisão humana recomendada."
    };
  }

  const analyticalResult = await executeAnalyticalPipeline(env, resolution.effectiveQuery, phone, auth.scope, resolution.report, activeChannel);
  return {
    ...analyticalResult,
    intent,
    phone,
    reportUrl: analyticalResult.reportUrl || resolution.reportUrl,
    reportName: analyticalResult.reportName || resolution.reportName,
    chips: analyticalResult.chips || resolution.chips,
    disclaimer: analyticalResult.disclaimer || "⚠️ Respostas geradas com base no contexto D1 do PEP HUB. Supervisão humana recomendada.",
    messageId: 'msg_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7)
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

  // 2. Endpoint REST direto: POST /api/bot/ask (Consumido pelo Baileys bot, CLI, testes, app, chatbot web)
  if (pathname === '/api/bot/ask') {
    if (request.method !== 'POST') {
      return json({ error: 'Método não permitido. Use POST.' }, 405);
    }

    try {
      const body = await request.json().catch(() => ({}));
      let phone = body.phone || body.sender || body.number || '';
      const query = body.query || body.message || body.text || '';
      const channel = body.channel || 'web';

      // Tenta obter usuário logado via cookie/sessão web
      let sessionUser = null;
      try {
        sessionUser = await getSessionUser(request, env);
      } catch (_) {}

      if (!phone && sessionUser) {
        phone = sessionUser.telefone || `web_${sessionUser.id}`;
      }

      if (!phone || !query) {
        return json({ error: 'Parâmetros obrigatórios ausentes: informe a pergunta.' }, 400);
      }

      const result = await processBotQuery(env, phone, query, sessionUser, channel);
      return json(result, result.unauthorized ? 403 : 200);
    } catch (err) {
      console.error('[Bot Ask Route Error]', err);
      return json({ error: 'Erro interno ao processar requisição do bot.', details: err.message }, 500);
    }
  }

  // 3. Endpoint de Feedback do RAG/Chatbot: POST /api/bot/feedback
  if (pathname === '/api/bot/feedback') {
    if (request.method !== 'POST') {
      return json({ error: 'Método não permitido. Use POST.' }, 405);
    }

    try {
      let sessionUser = null;
      try {
        sessionUser = await getSessionUser(request, env);
      } catch (_) {}

      const body = await request.json().catch(() => ({}));
      const rating = body.rating || 'correct'; // 'correct', 'partially_correct', 'incorrect'
      const query = (body.query || '').trim();
      const responseText = (body.responseText || body.answer || '').trim();
      const reportId = body.reportId || null;
      const comment = (body.comment || body.feedback || '').trim();
      const messageId = body.messageId || null;
      const id = 'fb_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);

      if (!query && !messageId) {
        return json({ error: 'Parâmetro obrigatório ausente: informe query ou messageId.' }, 400);
      }

      const userId = sessionUser?.id || (sessionUser?.matricula ? String(sessionUser.matricula) : null);
      const userName = sessionUser?.nome_completo || 'Colaborador';
      const userEmail = sessionUser?.email || null;

      if (env.DB) {
        await env.DB.prepare(`
          INSERT INTO bot_feedback (id, user_id, user_name, user_email, message_id, query, response_text, report_id, rating, comment, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        `).bind(id, userId, userName, userEmail, messageId, query, responseText, reportId, rating, comment).run();
      }

      return json({ success: true, id, message: 'Feedback analítico registrado com sucesso no D1.' });
    } catch (err) {
      console.error('[Bot Feedback Route Error]', err);
      return json({ error: 'Erro ao gravar feedback.', details: err.message }, 500);
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
      const result = await processBotQuery(env, cleanPhone, query, null, 'whatsapp');

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
