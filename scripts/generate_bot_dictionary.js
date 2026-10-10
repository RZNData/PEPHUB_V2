/**
 * PEP HUB — GERADOR AUTOMATIZADO DO DICIONÁRIO UNIVERSAL DE PERGUNTAS DO BOT
 *
 * Lê o REPORT_REGISTRY e gera:
 * 1. docs/DICIONARIO_UNIVERSAL_PERGUNTAS_BOT.md (Documentação executiva completa)
 * 2. worker/bot_dictionary.json (Dicionário estruturado para fast-paths e testes)
 */

const fs = require('fs');
const path = require('path');

const REPORT_REGISTRY = {
  FPD: {
    id: 'FPD',
    num: '1',
    name: 'FPD (First Payment Default & Qualidade de Venda)',
    title: 'Relatório Oficial de FPD (First Payment Default)',
    icon: '💳',
    primaryTable: 'fato_fpd',
    partnerTable: 'fato_churn_safra',
    dateColumn: 'safra',
    orderColumn: 'safra_ord',
    defaultSafra: 'mai/26',
    defaultMetric: 'taxa_fpd60',
    metricLabel: 'FPD 60',
    metrics: [
      { key: 'taxa_fpd60', label: 'FPD 60', unit: '%', direction: 'DESC', isDefault: true, desc: 'Inadimplência oficial no 1º pagamento após 60 dias' },
      { key: 'taxa_fpd30', label: 'FPD 30', unit: '%', direction: 'DESC', isDefault: false, desc: 'Inadimplência onboarding pró-rata 30 dias' },
      { key: 'taxa_cura', label: 'Cura', unit: '%', direction: 'ASC', isDefault: false, desc: 'Percentual de contratos regularizados entre 30 e 60 dias' },
      { key: 'instalacoes', label: 'Instalações', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume total de contratos instalados' }
    ],
    dimensions: [
      { key: 'cidade', label: 'Cidade', values: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá', 'Ananindeua', 'Castanhal', 'Imperatriz'] },
      { key: 'canal', label: 'Canal de Venda', values: ['PAP', 'Lojas', 'Televendas', 'Digital', 'GERAL'] },
      { key: 'faixa_risco', label: 'Faixa de Risco', values: ['BAIXO', 'MEDIO', 'ALTO', 'CRITICO'] },
      { key: 'safra', label: 'Safra', values: ['mai/26', 'abr/26', 'mar/26', 'fev/26'] }
    ],
    partners: ['TEL CENTRO DE CONTATOS LTDA', 'HITSS DO BRASIL SERVICOS TECNOLOGICOS LTDA', 'PRUDENTE SOLUCOES E INTERMEDIACAO LTDA', 'A C CAMPOS DINIZ COELHO', 'CCH Mendes', 'Elite']
  },

  CHURN_BL: {
    id: 'CHURN_BL',
    num: '2',
    name: 'Churn Banda Larga Total & PME',
    title: 'Relatório Oficial de Churn Banda Larga',
    icon: '📉',
    primaryTable: 'fato_indicadores_mensais',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_referencia',
    defaultMes: 'Setembro / 2026',
    defaultMetric: 'taxa_real',
    metricLabel: 'Taxa de Churn Real',
    metrics: [
      { key: 'taxa_real', label: 'Taxa Real', unit: '%', direction: 'DESC', isDefault: true, desc: 'Taxa percentual de cancelamento' },
      { key: 'vol_real', label: 'Volume Real', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume absoluto de desconexões' },
      { key: 'rxo_delta', label: 'Delta RxO', unit: '', direction: 'DESC', isDefault: false, desc: 'Desvio Real vs Orçado' },
      { key: 'mom_pct', label: 'MoM %', unit: '%', direction: 'DESC', isDefault: false, desc: 'Variação mês contra mês anterior' }
    ],
    dimensions: [
      { key: 'segmento', label: 'Segmento', values: ['Banda Larga Total', 'Banda Larga PME'] },
      { key: 'tipo_visao', label: 'Tipo de Visão', values: ['TOTAL', 'VOLUNTARIO', 'INVOLUNTARIO'] },
      { key: 'cidade', label: 'Cidade', values: ['Regional Norte', 'Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá', 'Ananindeua'] }
    ]
  },

  CHURN_SAFRA: {
    id: 'CHURN_SAFRA',
    num: '3',
    name: 'Churn Safra D120 (Sobrevivência & Estorno)',
    title: 'Relatório Oficial de Churn Safra D120',
    icon: '🌱',
    primaryTable: 'fato_churn_safra',
    dateColumn: 'safra',
    orderColumn: 'safra_ord',
    defaultSafra: 'mai/26',
    defaultMetric: 'taxa_np120',
    metricLabel: 'Não Pagamento 120 dias (NP120)',
    metrics: [
      { key: 'taxa_np120', label: 'Taxa NP120', unit: '%', direction: 'DESC', isDefault: true, desc: 'Cancelamentos sem nenhum pagamento até 120 dias (estorno)' },
      { key: 'taxa_d120', label: 'Taxa D120', unit: '%', direction: 'DESC', isDefault: false, desc: 'Desconexão acumulada até 120 dias' },
      { key: 'taxa_d30', label: 'Taxa D30 (1º Pagamento)', unit: '%', direction: 'DESC', isDefault: false, desc: 'Perda inicial no primeiro pagamento' },
      { key: 'instalacoes', label: 'Instalações', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume de vendas da safra' }
    ],
    dimensions: [
      { key: 'visao', label: 'Visão', values: ['PARCEIRO', 'CIDADE', 'REGIONAL'] },
      { key: 'entidade_nome', label: 'Parceiro / Cidade', values: ['TEL CENTRO DE CONTATOS LTDA', 'HITSS DO BRASIL', 'CCH Mendes', 'Elite', 'Belém', 'Manaus', 'São Luís'] },
      { key: 'status_safra', label: 'Status da Safra', values: ['MADURA', 'EM_ABERTO'] }
    ]
  },

  CREDITO: {
    id: 'CREDITO',
    num: '4',
    name: 'Aprovação de Crédito & Antifraude',
    title: 'Relatório Oficial de Aprovação de Crédito & Antifraude',
    icon: '🛡️',
    primaryTable: 'fato_aprovacao_credito',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_referencia',
    defaultMes: '2026-09',
    defaultMetric: 'taxa_aprovacao',
    metricLabel: 'Taxa de Aprovação',
    metrics: [
      { key: 'taxa_aprovacao', label: 'Taxa Aprovação', unit: '%', direction: 'ASC', isDefault: true, desc: '% de propostas aprovadas pelo motor de crédito' },
      { key: 'recusas_antifraude', label: 'Recusas Antifraude', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume de propostas barradas por suspeita de fraude' },
      { key: 'recusas_politica', label: 'Recusas Política', unit: '', direction: 'DESC', isDefault: false, desc: 'Reprovações por score ou restrição cadastral' },
      { key: 'risco_alto', label: 'Alto Risco', unit: '', direction: 'DESC', isDefault: false, desc: 'Contratos aprovados na faixa de alto risco' }
    ],
    dimensions: [
      { key: 'canal', label: 'Canal', values: ['Agente Autorizado', 'D2D Parceiros', 'Lojas Próprias', 'E-commerce Claro'] },
      { key: 'cidade', label: 'Cidade', values: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá'] }
    ]
  },

  MARKET_SHARE: {
    id: 'MARKET_SHARE',
    num: '5',
    name: 'Market Share & Concorrência (Anatel)',
    title: 'Relatório Oficial de Market Share & Anatel',
    icon: '📊',
    primaryTable: 'fato_market_share',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_referencia',
    defaultMes: '2026-08',
    defaultMetric: 'market_share_pct',
    metricLabel: 'Participação de Mercado (Share)',
    metrics: [
      { key: 'market_share_pct', label: 'Market Share', unit: '%', direction: 'DESC', isDefault: true, desc: 'Percentual de participação de mercado na cidade' },
      { key: 'net_adds', label: 'Net Adds', unit: '', direction: 'DESC', isDefault: false, desc: 'Saldo líquido de adições no mês' },
      { key: 'acessos', label: 'Acessos Ativos', unit: '', direction: 'DESC', isDefault: false, desc: 'Base total de contratos em serviço' },
      { key: 'posicao_ranking', label: 'Posição no Ranking', unit: '', direction: 'ASC', isDefault: false, desc: 'Posição da operadora no mercado local' }
    ],
    dimensions: [
      { key: 'operadora', label: 'Operadora', values: ['CLARO', 'VIVO', 'OI', 'OUTRAS', 'ISPS'] },
      { key: 'cidade', label: 'Cidade', values: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá'] }
    ]
  }
};

function generateUniversalDictionary() {
  const dictionary = [];
  let md = `# Dicionário Universal de Perguntas & Contextos — Pephub Bot RAG\n\n`;
  md += `> **Conformidade Executiva**: Todos os relatórios, filtros, métricas e cruzamentos oficiais da Regional Norte.\n`;
  md += `> **Data de Atualização**: Outubro / 2026 | **Versão**: 3.0\n\n`;

  md += `## 1. Princípios de Funcionamento do Bot\n`;
  md += `- **Métrica Padrão de FPD**: FPD 60 (\`taxa_fpd60\`). FPD 30 somente quando solicitado explicitamente.\n`;
  md += `- **Última Safra de FPD**: **mai/26** (resolvida cronologicamente por \`safra_ord DESC\`).\n`;
  md += `- **FPD de Parceiros**: Consultada em \`fato_churn_safra\` (\`visao = 'PARCEIRO'\`), avaliando \`taxa_d30\` e \`taxa_np120\` na safra madura com mínimo de 30 instalações.\n`;
  md += `- **Desambiguação Interativa**: Respostas como \`1\`, \`2\`, \`3\`, \`4\`, \`5\` ou links \`wa.me\` resolvem a consulta pendente sem necessidade de prefixo \`#?\`.\n\n`;

  for (const [repKey, rep] of Object.entries(REPORT_REGISTRY)) {
    md += `## 2.${rep.num} ${rep.name}\n\n`;
    md += `| Propriedade | Valor Oficial |\n| :--- | :--- |\n`;
    md += `| **Tabela D1** | \`${rep.primaryTable}\` |\n`;
    md += `| **Métrica Padrão** | **${rep.metricLabel}** (\`${rep.defaultMetric}\`) |\n`;
    md += `| **Coluna de Ordenação Temporal** | \`${rep.orderColumn}\` |\n\n`;

    md += `### Perguntas Suportadas e Padrões de Resposta\n\n`;

    const repQuestions = [];

    // 1. Perguntas de Período / Última Safra
    repQuestions.push({
      categoria: 'Período e Safras',
      pergunta: `Qual a última safra de ${rep.name.split(' ')[0]}?`,
      exemploSql: `SELECT DISTINCT ${rep.dateColumn}, ${rep.orderColumn} FROM ${rep.primaryTable} ORDER BY ${rep.orderColumn} DESC LIMIT 1`,
      retornoEsperado: `Safra mais recente consolidada (${rep.defaultSafra || rep.defaultMes})`
    });

    repQuestions.push({
      categoria: 'Período e Safras',
      pergunta: `Quais safras estão disponíveis em ${rep.name.split(' ')[0]}?`,
      exemploSql: `SELECT DISTINCT ${rep.dateColumn} FROM ${rep.primaryTable} ORDER BY ${rep.orderColumn} DESC`,
      retornoEsperado: `Lista das safras disponíveis`
    });

    // 2. Rankings e Extremos (Pior / Melhor)
    repQuestions.push({
      categoria: 'Rankings e Extremos',
      pergunta: `Quem tem o pior ${rep.metricLabel}?`,
      exemploSql: `SELECT cidade, ${rep.defaultMetric} FROM ${rep.primaryTable} ORDER BY ${rep.defaultMetric} DESC LIMIT 5`,
      retornoEsperado: `Ranking com as 5 piores entidades/cidades no indicador padrão`
    });

    repQuestions.push({
      categoria: 'Rankings e Extremos',
      pergunta: `Quem tem o melhor ${rep.metricLabel}?`,
      exemploSql: `SELECT cidade, ${rep.defaultMetric} FROM ${rep.primaryTable} ORDER BY ${rep.defaultMetric} ASC LIMIT 5`,
      retornoEsperado: `Ranking com as 5 melhores entidades/cidades`
    });

    // 3. Perguntas por Dimensões (Cidades, Canais, etc.)
    for (const dim of rep.dimensions) {
      for (const val of dim.values.slice(0, 3)) {
        repQuestions.push({
          categoria: `Filtro por ${dim.label}`,
          pergunta: `Qual o ${rep.metricLabel} de ${val}?`,
          exemploSql: `SELECT ${rep.dateColumn}, ${dim.key}, ${rep.defaultMetric} FROM ${rep.primaryTable} WHERE ${dim.key} LIKE '%${val}%' ORDER BY ${rep.orderColumn} DESC LIMIT 1`,
          retornoEsperado: `Resultado analítico para ${val} no período mais recente`
        });
      }
    }

    // 4. Se for FPD: Parceiros
    if (rep.id === 'FPD') {
      repQuestions.push({
        categoria: 'Parceiros de Venda',
        pergunta: `Qual o parceiro com pior FPD?`,
        exemploSql: `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 30 ORDER BY safra_ord DESC, taxa_d30 DESC LIMIT 5`,
        retornoEsperado: `Ranking de parceiros com maior perda de 1º pagamento (Taxa D30) e estorno (NP120) com volume mínimo de 30 instalações`
      });
      for (const p of rep.partners.slice(0, 3)) {
        repQuestions.push({
          categoria: 'Parceiros de Venda',
          pergunta: `Qual o FPD do parceiro ${p}?`,
          exemploSql: `SELECT safra, entidade_nome, instalacoes, taxa_d30, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND entidade_nome LIKE '%${p}%' ORDER BY safra_ord DESC LIMIT 1`,
          retornoEsperado: `Desempenho de 1º pagamento e estorno do parceiro ${p}`
        });
      }
    }

    md += `| Categoria | Exemplo de Pergunta | Consulta D1 (Text-to-SQL) | Retorno Esperado |\n`;
    md += `| :--- | :--- | :--- | :--- |\n`;
    for (const q of repQuestions) {
      md += `| ${q.categoria} | *"${q.pergunta}"* | \`${q.exemploSql}\` | ${q.retornoEsperado} |\n`;
      dictionary.push({
        reportId: rep.id,
        category: q.categoria,
        question: q.pergunta,
        sql: q.exemploSql,
        expectedResult: q.retornoEsperado
      });
    }
    md += `\n`;
  }

  // Gravação dos artefatos
  const docPath = path.join(__dirname, '../docs/DICIONARIO_UNIVERSAL_PERGUNTAS_BOT.md');
  const jsonPath = path.join(__dirname, '../worker/bot_dictionary.json');

  fs.writeFileSync(docPath, md, 'utf-8');
  fs.writeFileSync(jsonPath, JSON.stringify(dictionary, null, 2), 'utf-8');

  console.log(`[Gerador] Documento gerado com sucesso em: ${docPath}`);
  console.log(`[Gerador] Dicionário JSON gerado com sucesso em: ${jsonPath}`);
  console.log(`[Gerador] Total de padrões de perguntas mapeados: ${dictionary.length}`);
}

generateUniversalDictionary();
