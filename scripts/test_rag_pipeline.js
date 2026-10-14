/**
 * Teste Automatizado de Integração do RAG Funcional & Efetivo
 * Valida:
 * 1. Catálogo Semântico e Incompatibilidade Dimensional (Canal vs Parceiro).
 * 2. Prevenção de retorno de parceiros quando canal é solicitado.
 * 3. Ausência estrita de artefatos de WhatsApp (wa.me, #?) no canal Web.
 * 4. Resposta questionadora proativa para entidades sem métrica.
 */

import { validateDimensionalCompatibility, SEMANTIC_TABLES } from '../worker/semantic_catalog.js';
import {
  extractQueryEntities,
  buildDeterministicAnalyticalSQL,
  buildActionSelectionMenu,
  buildProductSelectionMenu,
  buildSegmentSelectionMenu,
  buildChannelListMenu,
  buildCityListMenu,
  buildDddListMenu,
  buildBaseSelectionMenu,
  buildCardFooterLinks,
  REPORT_REGISTRY
} from '../worker/bot_registry.js';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  [OK] ${message}`);
    passed++;
  } else {
    console.error(`  [FAIL] ${message}`);
    failed++;
  }
}

console.log("============================================================================");
console.log("  TESTE DE INTEGRAÇÃO DO RAG FUNCIONAL & CAMADA SEMÂNTICA (PEP HUB)");
console.log("============================================================================\n");

// 1. Catálogo Semântico & Incompatibilidade Dimensional
console.log("1. Validação de Compatibilidade Dimensional:");
const c1 = validateDimensionalCompatibility('canal', 'CHURN_SAFRA');
assert(c1.compatible === false, "Canal em Churn Safra é detectado como incompatível");
assert(c1.reason.includes('Parceiro Comercial e por Cidade'), "Explicação clara de que Safra é por Parceiro e Cidade");

const c2 = validateDimensionalCompatibility('canal', 'CHURN_BL');
assert(c2.compatible === false, "Canal em Churn BL é detectado como incompatível");

const c3 = validateDimensionalCompatibility('canal', 'FPD');
assert(c3.compatible === true, "Canal em FPD é compatível");

const c4 = validateDimensionalCompatibility('canal', 'CREDITO');
assert(c4.compatible === true, "Canal em Crédito é compatível");

// 2. Extração de Entidades
console.log("\n2. Extração Semântica de Entidades:");
const e1 = extractQueryEntities("qual o canal ofensor?");
assert(e1.isChannelQuery === true, "Identificou isChannelQuery = true");
assert(e1.isParceiroQuery === false, "Identificou isParceiroQuery = false");
assert(e1.isOfensorQuery === true, "Identificou isOfensorQuery = true");

const e2 = extractQueryEntities("qual o parceiro ofensor de Belém?");
assert(e2.isParceiroQuery === true, "Identificou isParceiroQuery = true");
assert(e2.matchedCity === 'Belém', "Identificou Belém como cidade");

// 3. Text-to-SQL Consciente do Schema
console.log("\n3. Geração de SQL com Prevenção de Falsos Positivos Dimensionais:");
const sqlSafraCanal = buildDeterministicAnalyticalSQL("qual o canal ofensor?", REPORT_REGISTRY.CHURN_SAFRA, {});
assert(sqlSafraCanal === null, "buildDeterministicAnalyticalSQL não retorna parceiros como canais em Churn Safra");

const sqlSafraParceiro = buildDeterministicAnalyticalSQL("qual o parceiro ofensor?", REPORT_REGISTRY.CHURN_SAFRA, {});
assert(sqlSafraParceiro !== null && sqlSafraParceiro.includes("visao = 'PARCEIRO'"), "buildDeterministicAnalyticalSQL retorna parceiro quando solicitado parceiro em Safra");

const sqlFpdCanal = buildDeterministicAnalyticalSQL("qual o canal ofensor?", REPORT_REGISTRY.FPD, {});
assert(sqlFpdCanal !== null && sqlFpdCanal.includes("canal IS NOT NULL") && sqlFpdCanal.includes("GROUP BY canal"), "buildDeterministicAnalyticalSQL gera agrupamento por canal em FPD");

const sqlCreditoCanal = buildDeterministicAnalyticalSQL("qual canal tem pior aprovação?", REPORT_REGISTRY.CREDITO, {});
assert(sqlCreditoCanal !== null && sqlCreditoCanal.includes("canal IS NOT NULL"), "buildDeterministicAnalyticalSQL gera agrupamento por canal em Crédito");

// 4. Desacoplamento Web vs WhatsApp (Zero wa.me e Zero #? na Web)
console.log("\n4. Desacoplamento Web vs WhatsApp nos Menus:");
const repFpd = REPORT_REGISTRY.FPD;
const menuActionWeb = buildActionSelectionMenu(repFpd, {}, 'web_user', 'web');
assert(!menuActionWeb.includes('wa.me'), "Menu de Ações Web não contém links wa.me");
assert(!menuActionWeb.includes('#?'), "Menu de Ações Web não contém comando #?");
assert(menuActionWeb.includes('[1]'), "Menu de Ações Web contém opções [1], [2], etc.");

const menuProdWeb = buildProductSelectionMenu(repFpd, 'web_user', 'web');
assert(!menuProdWeb.includes('wa.me') && !menuProdWeb.includes('#?'), "Menu de Produtos Web não contém wa.me nem #?");

const menuSegWeb = buildSegmentSelectionMenu(REPORT_REGISTRY.CHURN_BL, 'web_user', 'web');
assert(!menuSegWeb.includes('wa.me') && !menuSegWeb.includes('#?'), "Menu de Segmentos Web não contém wa.me nem #?");

const menuChannelsWeb = buildChannelListMenu(repFpd, {}, 'web_user', 'web');
assert(!menuChannelsWeb.includes('wa.me') && !menuChannelsWeb.includes('#?'), "Menu de Lista de Canais Web não contém wa.me nem #?");

const menuCitiesWeb = buildCityListMenu(repFpd, {}, 'web_user', 'web');
assert(!menuCitiesWeb.includes('wa.me') && !menuCitiesWeb.includes('#?'), "Menu de Lista de Cidades Web não contém wa.me nem #?");

const menuDddWeb = buildDddListMenu(REPORT_REGISTRY.MARKET_SHARE, {}, 'web_user', 'web');
assert(!menuDddWeb.includes('wa.me') && !menuDddWeb.includes('#?'), "Menu de Lista de DDDs Web não contém wa.me nem #?");

const footerWeb = buildCardFooterLinks(repFpd, {}, 'web_user', 'web');
assert(!footerWeb.includes('wa.me') && !footerWeb.includes('#?'), "Rodapé de cards Web não contém wa.me nem #?");

// 5. Bateria de 22 Cenários Cognitivos Humanos (rag-auditor)
console.log("\n5. Bateria de Testes Cognitivos de Alta Variabilidade (22 Cenários):");
import('./test_rag_20_scenarios.js').then(async (scen) => {
  const scenRes = await scen.run20CognitiveTests();
  assert(scenRes.failed === 0, `Todos os ${scenRes.total} cenários cognitivos foram aprovados com 100% de precisão`);

  console.log("\n============================================================================");
  console.log(`  RESULTADO CONSOLIDADO: ${passed} testes passaram, ${failed} falharam.`);
  console.log("============================================================================");

  process.exit(failed === 0 ? 0 : 1);
});
