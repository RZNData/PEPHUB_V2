import { REPORT_REGISTRY, buildDeterministicAnalyticalSQL } from '../worker/bot_registry.js';
import { resolveTargetReport } from '../worker/routes/bot.js';

const queries = [
  { q: "Qual o pior pdv de Belém em FPD?", expectedReport: "FPD" },
  { q: "Qual o churn safra atual e qual canal está pior?", expectedReport: "CHURN_SAFRA" },
  { q: "Quais são meus vendedores ofensores em Churn safra?", expectedReport: "CHURN_SAFRA" },
  { q: "Quanto é o market share atual da claro e qual a média de net adds dos últimos 6 meses? E a concorrência?", expectedReport: "MARKET_SHARE" },
  { q: "Quanto é o orçamento do churn de banda larga para novembro e quanto está o YTD26 versus YTD25?", expectedReport: "CHURN_BL" },
  { q: "Qual o pior vendedor do canal Porta a Porta em FPD em abril, considere apenas os que tem mais de 10 vendas.", expectedReport: "FPD" }
];

console.log("=== TESTANDO CLASSIFICAÇÃO E ROTEAMENTO DAS 6 PERGUNTAS DO USUÁRIO ===");

async function testAll() {
  const dummyEnv = { DB: null };
  for (let i = 0; i < queries.length; i++) {
    const item = queries[i];
    const res = await resolveTargetReport(dummyEnv, item.q, 'web_admin', 'web');
    const repId = res.report ? res.report.id : 'NENHUM';
    const status = repId === item.expectedReport ? 'OK' : 'FALHA';
    
    // Check deterministic SQL
    const detSql = buildDeterministicAnalyticalSQL(item.q, res.report, 'web_admin');
    const delegatesToLLM = detSql === null ? 'SIM (Delegado ao Gemini)' : 'NÃO (SQL rígido gerado: ' + detSql + ')';

    console.log(`[${status}] Pergunta ${i + 1}: "${item.q}"`);
    console.log(`     -> Relatório detectado: ${repId} (Esperado: ${item.expectedReport})`);
    console.log(`     -> Raciocínio via LLM: ${delegatesToLLM}`);
  }
}

testAll().catch(console.error);
