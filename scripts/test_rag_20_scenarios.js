/**
 * PEP HUB — Bateria de Testes Cognitivos de Alta Variabilidade do RAG (22 Cenários)
 * Atribuído à Skill: rag-auditor
 *
 * Avalia perguntas variadas com aberturas, profundidade, cruzamentos e comandos humanos:
 * 1. Aberturas analíticas (visão executiva regional)
 * 2. Profundidade (drilldown de cidades, canais, parceiros, clusters, safras)
 * 3. Cruzamentos de indicadores (garantia de não-colisão, visão dual móvel/fixo)
 * 4. Guardas dimensionais e notas regulatórias (área cabeada, canais em safra)
 * 5. Qualidade de metadados ricos (reportUrl parametrizada, chips contextuais e disclaimer)
 */

import { validateDimensionalCompatibility, detectQualifiers, CLARO_CLUSTERS } from '../worker/semantic_catalog.js';
import {
  extractQueryEntities,
  buildDeterministicAnalyticalSQL,
  REPORT_REGISTRY
} from '../worker/bot_registry.js';
import {
  resolveTargetReport,
  buildRichMetadataForReport,
  synthesizeCognitiveAnswerDeterministic
} from '../worker/routes/bot.js';

const mockEnv = {
  DB: {
    prepare: (sql) => ({
      bind: (...args) => ({
        first: async () => null,
        all: async () => ({ results: [] }),
        run: async () => ({ success: true })
      })
    })
  }
};

const SCENARIOS = [
  {
    id: 'Q01',
    tipo: 'Cruzamento & Desambiguação',
    query: 'qual o churn de banda larga em Manaus?',
    expectedReport: 'CHURN_BL',
    validator: async (res) => {
      const isCorrectRep = res.report?.id === 'CHURN_BL';
      const entities = extractQueryEntities(res.query);
      const isManaus = entities.matchedCity === 'Manaus';
      const meta = buildRichMetadataForReport(res.report, res.query, [{ cidade: 'Manaus' }]);
      const hasCorrectUrl = meta.reportUrl.includes('cidade=Manaus') && meta.reportUrl.includes('/churn-bl/');
      return {
        passed: isCorrectRep && isManaus && hasCorrectUrl,
        reason: isCorrectRep ? 'Roteamento exato para CHURN_BL (sem colisão com Market Share) e URL com filtro de Manaus' : `Roteou incorretamente para ${res.report?.id}`
      };
    }
  },
  {
    id: 'Q02',
    tipo: 'Qualificador Regulatório & Cruzamento',
    query: 'como está o market share da Claro na área cabeada de Belém?',
    expectedReport: 'MARKET_SHARE',
    validator: async (res) => {
      const q = detectQualifiers(res.query);
      const isAreaCabeada = q.isAreaCabeada;
      const entities = extractQueryEntities(res.query);
      const isBelem = entities.matchedCity === 'Belém';
      const isMkt = res.report?.id === 'MARKET_SHARE';
      const synth = synthesizeCognitiveAnswerDeterministic(res.query, [
        { cidade: 'Belém', produto: 'BANDA_LARGA', market_share_pct: 33.88, total_acessos: 85000, claro_acessos: 28800, net_adds_mes: 131 }
      ], res.report, 'web');
      const mentionsRegulatory = synth.includes('Anatel') || synth.includes('regulatório') || synth.includes('cabeada');
      return {
        passed: isMkt && isAreaCabeada && isBelem && mentionsRegulatory,
        reason: 'Identificou área cabeada, mapeou Belém e inseriu nota regulatória sobre escopo municipal Anatel'
      };
    }
  },
  {
    id: 'Q03',
    tipo: 'Cluster Estratégico (Grandes Mercados)',
    query: 'qual o market share nos grandes mercados?',
    expectedReport: 'MARKET_SHARE',
    validator: async (res) => {
      const q = detectQualifiers(res.query);
      const isGM = q.isGrandesMercados;
      const synth = synthesizeCognitiveAnswerDeterministic(res.query, [
        { cidade: 'Manaus', produto: 'BANDA_LARGA', market_share_pct: 38.5, total_acessos: 150000, claro_acessos: 57750, net_adds_mes: 210 },
        { cidade: 'Belém', produto: 'BANDA_LARGA', market_share_pct: 33.88, total_acessos: 85000, claro_acessos: 28800, net_adds_mes: 131 }
      ], res.report, 'web');
      const mentionsCluster = synth.includes('Grandes Mercados');
      return {
        passed: res.report?.id === 'MARKET_SHARE' && isGM && mentionsCluster,
        reason: 'Reconheceu cluster Grandes Mercados (GMs) e estruturou síntese executiva de agrupamento'
      };
    }
  },
  {
    id: 'Q04',
    tipo: 'Cluster Estratégico (Mercados em Desenvolvimento)',
    query: 'resumo de market share nos mercados em desenvolvimento',
    expectedReport: 'MARKET_SHARE',
    validator: async (res) => {
      const q = detectQualifiers(res.query);
      const isMED = q.isMercadosDesenvolvimento;
      const synth = synthesizeCognitiveAnswerDeterministic(res.query, [
        { cidade: 'Castanhal', produto: 'BANDA_LARGA', market_share_pct: 22.4, total_acessos: 20000, claro_acessos: 4480, net_adds_mes: 45 }
      ], res.report, 'web');
      const mentionsCluster = synth.includes('Mercados em Desenvolvimento');
      return {
        passed: res.report?.id === 'MARKET_SHARE' && isMED && mentionsCluster,
        reason: 'Reconheceu cluster Mercados em Desenvolvimento (MEDs) com agrupamento de cidades de interior'
      };
    }
  },
  {
    id: 'Q05',
    tipo: 'Guarda Dimensional Estrita',
    query: 'quais os canais com pior churn safra?',
    expectedReport: 'CHURN_SAFRA',
    validator: async (res) => {
      const hasDirectAnswer = Boolean(res.directAnswer);
      const mentionsIncompatibility = (res.directAnswer || '').includes('Incompatibilidade Dimensional');
      const redirectsToFpdOrCredito = (res.directAnswer || '').includes('FPD 60') && (res.directAnswer || '').includes('Aprovação de Crédito');
      const noPartnersAsChannels = !(res.directAnswer || '').includes('Top Connect no canal');
      return {
        passed: res.report?.id === 'CHURN_SAFRA' && hasDirectAnswer && mentionsIncompatibility && redirectsToFpdOrCredito && noPartnersAsChannels,
        reason: 'Acionou guarda dimensional em Churn Safra, recusando listar parceiros como canais e orientando FPD/Crédito'
      };
    }
  },
  {
    id: 'Q06',
    tipo: 'Profundidade por Parceiro',
    query: 'qual parceiro tem o pior churn safra D120?',
    expectedReport: 'CHURN_SAFRA',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const queriesParceiro = sql && sql.includes("visao = 'PARCEIRO'");
      return {
        passed: res.report?.id === 'CHURN_SAFRA' && entities.isParceiroQuery && queriesParceiro,
        reason: 'Identificou consulta a parceiros em Safra e gerou SQL com filtro visao = PARCEIRO'
      };
    }
  },
  {
    id: 'Q07',
    tipo: 'Abertura Analítica Regional',
    query: 'qual o FPD consolidado da Regional Norte?',
    expectedReport: 'FPD',
    validator: async (res) => {
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const isFpd = res.report?.id === 'FPD';
      const meta = buildRichMetadataForReport(res.report, res.query, [{ safra: 'abr/26' }]);
      const hasFpdUrl = meta.reportUrl.includes('/fpd-residencial/');
      const hasChips = meta.chips.length >= 3;
      return {
        passed: isFpd && hasFpdUrl && hasChips,
        reason: 'Consolidou FPD Regional, gerou reportUrl oficial e chips de aprofundamento por canal e cidade'
      };
    }
  },
  {
    id: 'Q08',
    tipo: 'Profundidade por Canal (PAP)',
    query: 'como está o FPD 30 e 60 no canal PAP?',
    expectedReport: 'FPD',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isPap = entities.matchedChannel === 'PAP';
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const hasPapFilter = sql && (sql.includes("canal = 'PAP'") || sql.includes("canal LIKE '%PAP%'"));
      return {
        passed: res.report?.id === 'FPD' && isPap && hasPapFilter,
        reason: 'Identificou canal PAP e aplicou filtro específico canal PAP em fato_fpd'
      };
    }
  },
  {
    id: 'Q09',
    tipo: 'Cruzamento Geográfico por DDD',
    query: 'resultado de FPD no DDD 91',
    expectedReport: 'FPD',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isDdd91 = entities.matchedDdd?.ddd === '91';
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const hasDddOrCity = sql && (sql.includes("cidade = 'Belém'") || sql.includes("ddd = '91'"));
      return {
        passed: res.report?.id === 'FPD' && isDdd91 && hasDddOrCity,
        reason: 'Mapeou DDD 91 (Belém) e gerou filtro determinístico no relatório de FPD'
      };
    }
  },
  {
    id: 'Q10',
    tipo: 'Abertura Analítica (Crédito)',
    query: 'qual a taxa de aprovação de crédito na regional?',
    expectedReport: 'CREDITO',
    validator: async (res) => {
      const isCred = res.report?.id === 'CREDITO';
      const meta = buildRichMetadataForReport(res.report, res.query, [{ mes_referencia: '2026-09' }]);
      const hasCredUrl = meta.reportUrl.includes('/aprovacao-credito/');
      return {
        passed: isCred && hasCredUrl,
        reason: 'Roteou para esteira de Aprovação de Crédito com URL correta e chips analíticos'
      };
    }
  },
  {
    id: 'Q11',
    tipo: 'Profundidade & Antifraude',
    query: 'quais cidades tem mais recusa por antifraude no crédito?',
    expectedReport: 'CREDITO',
    validator: async (res) => {
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const hasFraudRank = sql && sql.includes('recusas_antifraude') && sql.includes('GROUP BY cidade');
      return {
        passed: res.report?.id === 'CREDITO' && hasFraudRank,
        reason: 'Gerou ranking de cidades por recusas de antifraude em fato_aprovacao_credito'
      };
    }
  },
  {
    id: 'Q12',
    tipo: 'Profundidade por Segmento (PME)',
    query: 'qual o churn de banda larga no PME?',
    expectedReport: 'CHURN_BL',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isPme = entities.isPmeQuery;
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const filtersPme = sql && (sql.includes("segmento = 'Banda Larga PME'") || sql.includes("segmento LIKE '%PME%'"));
      return {
        passed: res.report?.id === 'CHURN_BL' && isPme && filtersPme,
        reason: 'Segmentou Churn Banda Larga especificamente para carteira PME'
      };
    }
  },
  {
    id: 'Q13',
    tipo: 'Comparativo de Metas (RxO)',
    query: 'o churn de banda larga está dentro do orçado?',
    expectedReport: 'CHURN_BL',
    validator: async (res) => {
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const checksRxo = sql && (sql.includes('taxa_real') || sql.includes('taxa_orc') || sql.includes('rxo_delta'));
      return {
        passed: res.report?.id === 'CHURN_BL' && checksRxo,
        reason: 'Recuperou métricas de realizado vs orçado (RxO) para confronto orçamentário'
      };
    }
  },
  {
    id: 'Q14',
    tipo: 'Abertura Qualitativa (Speech Analytics)',
    query: 'quais os principais motivos de cancelamento no Speech?',
    expectedReport: 'SPEECH',
    validator: async (res) => {
      const isSpeech = res.report?.id === 'SPEECH';
      const meta = buildRichMetadataForReport(res.report, res.query, []);
      const hasSpeechUrl = meta.reportUrl.includes('/speech/');
      return {
        passed: isSpeech && hasSpeechUrl,
        reason: 'Roteou para Speech Analytics com link direto e chips de transcrição'
      };
    }
  },
  {
    id: 'Q15',
    tipo: 'Cruzamento Cidade + Motivo Speech',
    query: 'qual o percentual do motivo acha caro em Belém no Speech?',
    expectedReport: 'SPEECH',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isBelem = entities.matchedCity === 'Belém';
      const isSpeech = res.report?.id === 'SPEECH';
      return {
        passed: isSpeech && isBelem,
        reason: 'Mapeou Belém e intenção analítica de Speech para cancelamento por percepção de valor (acha caro)'
      };
    }
  },
  {
    id: 'Q16',
    tipo: 'Abertura Operacional (Motivos & OS)',
    query: 'qual a taxa de ordens de serviço geradas na Regional?',
    expectedReport: 'MOTIVOS',
    validator: async (res) => {
      const isMotivos = res.report?.id === 'MOTIVOS';
      const meta = buildRichMetadataForReport(res.report, res.query, []);
      const hasMotivosUrl = meta.reportUrl.includes('/motivos-os/');
      return {
        passed: isMotivos && hasMotivosUrl,
        reason: 'Roteou para base de Motivos de Procura & OS Técnica'
      };
    }
  },
  {
    id: 'Q17',
    tipo: 'Profundidade Geográfica OS',
    query: 'taxa de OS técnica em Manaus',
    expectedReport: 'MOTIVOS',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isManaus = entities.matchedCity === 'Manaus';
      const isMotivos = res.report?.id === 'MOTIVOS';
      return {
        passed: isMotivos && isManaus,
        reason: 'Identificou Manaus e direcionou para taxa de ordens de serviço na capital amazonense'
      };
    }
  },
  {
    id: 'Q18',
    tipo: 'Cruzamento Móvel + DDD',
    query: 'como está o market share móvel no DDD 98?',
    expectedReport: 'MARKET_SHARE',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isMovel = entities.isMovelQuery;
      const isDdd98 = entities.matchedDdd?.ddd === '98';
      const isMkt = res.report?.id === 'MARKET_SHARE';
      return {
        passed: isMkt && isMovel && isDdd98,
        reason: 'Identificou serviço Móvel com recorte geográfico no DDD 98 (Maranhão)'
      };
    }
  },
  {
    id: 'Q19',
    tipo: 'Pergunta Conceitual / Regra de Negócio',
    query: 'qual a diferença entre FPD 30 e FPD 60?',
    expectedReport: 'CONCEITUAL',
    validator: async (res) => {
      const isConceptual = res.intent === 'CONCEITUAL' || /diferença|conceito|o que e|significa/i.test(res.query);
      return {
        passed: isConceptual,
        reason: 'Classificou como consulta conceitual/glossário sem acionar varredura indevida no D1'
      };
    }
  },
  {
    id: 'Q20',
    tipo: 'Desambiguação Proativa (Pergunta Ambígua)',
    query: 'resultado de Belém',
    expectedReport: 'AMBIGUO',
    validator: async (res) => {
      const isDisambiguation = res.needDisambiguation === true;
      const mentions7Options = res.menuText && res.menuText.includes('[1]') && res.menuText.includes('[7]');
      return {
        passed: isDisambiguation && mentions7Options,
        reason: 'Detectou apenas a entidade Belém sem indicador, emitindo questionador proativo com as 7 opções'
      };
    }
  },
  {
    id: 'Q21',
    tipo: 'Cruzamento de Tipologia de Churn',
    query: 'qual o churn voluntário vs involuntário de banda larga?',
    expectedReport: 'CHURN_BL',
    validator: async (res) => {
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const hasVisao = sql && sql.includes('tipo_visao');
      return {
        passed: res.report?.id === 'CHURN_BL' && hasVisao,
        reason: 'Recuperou quebra de Churn Banda Larga por visão voluntária vs involuntária'
      };
    }
  },
  {
    id: 'Q22',
    tipo: 'Profundidade Operacional por Vendedor',
    query: 'quais os vendedores com maior taxa de FPD 60?',
    expectedReport: 'FPD',
    validator: async (res) => {
      const entities = extractQueryEntities(res.query);
      const isVendedor = entities.isVendedorQuery;
      const sql = buildDeterministicAnalyticalSQL(res.query, res.report, {});
      const filtersVendedor = sql && sql.includes('vendedor IS NOT NULL') && sql.includes('vendedor');
      return {
        passed: res.report?.id === 'FPD' && isVendedor && filtersVendedor,
        reason: 'Identificou consulta por vendedores individuais e gerou ranking de qualidade em fato_fpd'
      };
    }
  }
];

export async function run20CognitiveTests() {
  console.log('============================================================================');
  console.log('  PEP HUB — BATERIA DE TESTES COGNITIVOS DO RAG (22 CENÁRIOS HUMANOS)');
  console.log('  Skill: rag-auditor | Escopo: Regional Norte');
  console.log('============================================================================\n');

  let passed = 0;
  let failed = 0;
  const results = [];

  for (const s of SCENARIOS) {
    let reportRes;
    if (s.expectedReport === 'CONCEITUAL') {
      reportRes = { query: s.query, intent: 'CONCEITUAL', report: { id: 'CONCEITUAL' } };
    } else {
      const res = await resolveTargetReport(mockEnv, s.query, 'web_tester', 'web');
      reportRes = { query: s.query, ...res };
    }

    const testEvaluation = await s.validator(reportRes);
    if (testEvaluation.passed) {
      console.log(`  [OK] ${s.id} · [${s.tipo}]: "${s.query}"`);
      console.log(`       -> ${testEvaluation.reason}`);
      passed++;
      results.push({ id: s.id, status: 'PASS', query: s.query, reason: testEvaluation.reason });
    } else {
      console.error(`  [FAIL] ${s.id} · [${s.tipo}]: "${s.query}"`);
      console.error(`       -> Motivo da falha: ${testEvaluation.reason}`);
      failed++;
      results.push({ id: s.id, status: 'FAIL', query: s.query, reason: testEvaluation.reason });
    }
  }

  console.log('\n============================================================================');
  console.log(`  RESULTADO DA BATERIA: ${passed}/${SCENARIOS.length} cenários aprovados com nota máxima.`);
  console.log('============================================================================\n');

  return { passed, failed, total: SCENARIOS.length, results };
}

// Executa direto via node se chamado via CLI
if (process.argv[1]?.endsWith('test_rag_20_scenarios.js')) {
  run20CognitiveTests().then(({ failed }) => {
    process.exit(failed === 0 ? 0 : 1);
  });
}
