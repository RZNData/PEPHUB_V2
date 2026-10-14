/**
 * Cloudflare Worker — PEP HUB Semantic Data Catalog & Dimensional Introspection
 * Regional Norte (AM, PA, MA, AP, RR)
 * 
 * Camada Semântica Oficial que mapeia:
 * 1. Granularidades dimensionais de cada tabela do SQLite D1 (pephub-db).
 * 2. Compatibilidade entre entidades requisitadas (canal, parceiro, vendedor, etc.) e tabelas.
 * 3. Dicionário de termos e sinônimos analíticos da Claro Regional Norte.
 * 4. Regras anti-alucinação dimensional e salvaguardas da Regra de Ouro da Veracidade.
 */

export const SEMANTIC_TABLES = {
  fato_fpd: {
    reportId: 'FPD',
    reportName: 'FPD (First Payment Default)',
    tableName: 'fato_fpd',
    primaryMetric: 'taxa_fpd60',
    primaryMetricLabel: 'FPD 60',
    description: 'Monitoramento da qualidade de vendas no primeiro pagamento (safras de venda).',
    columns: [
      'safra', 'safra_ord', 'cidade', 'uf', 'canal', 'familia_produto',
      'parceiro', 'vendedor', 'instalacoes', 'fpd30', 'taxa_fpd30',
      'fpd60', 'taxa_fpd60', 'cura', 'taxa_cura', 'faixa_risco'
    ],
    supportedDimensions: ['canal', 'parceiro', 'vendedor', 'cidade', 'safra', 'familia_produto'],
    unsupportedDimensions: ['operadora', 'concorrente', 'segmento_pme', 'motivo_chamada', 'ddd'],
    latestSafraDefault: 'mai/26',
    channelValues: ['PAP', 'Lojas', 'Televendas', 'Agente Autorizado', 'D2D Parceiros', 'Digital', 'TODOS'],
    notes: 'Possui Canal, Parceiro e Vendedor individual. Indicador foco é FPD 60.'
  },

  fato_churn_safra: {
    reportId: 'CHURN_SAFRA',
    reportName: 'Churn Safra D120',
    tableName: 'fato_churn_safra',
    primaryMetric: 'taxa_d120',
    primaryMetricLabel: 'Churn D120',
    description: 'Sobrevivência de clientes até o 4º mês (D120) e estorno de comissão.',
    columns: [
      'safra', 'safra_ord', 'visao', 'entidade_nome', 'cidade', 'instalacoes',
      'churn_d30', 'taxa_d30', 'churn_d60', 'taxa_d60', 'churn_d120', 'taxa_d120',
      'np120', 'taxa_np120', 'inadimplencia', 'fraude', 'status_safra'
    ],
    supportedDimensions: ['parceiro', 'cidade', 'safra', 'visao'],
    unsupportedDimensions: ['canal', 'vendedor', 'operadora', 'ddd', 'produto_especifico'],
    notes: 'IMPORTANTE: Esta base consolida por Parceiro (visao = "PARCEIRO") e por Cidade (visao = "CIDADE"). NÃO possui a dimensão Canal nem Vendedor individual!'
  },

  fato_aprovacao_credito: {
    reportId: 'CREDITO',
    reportName: 'Aprovação de Crédito & Antifraude',
    tableName: 'fato_aprovacao_credito',
    primaryMetric: 'taxa_aprovacao',
    primaryMetricLabel: 'Taxa de Aprovação',
    description: 'Eficácia do motor de crédito, volume de consultas, recusas por política e antifraude.',
    columns: [
      'mes_referencia', 'cidade', 'canal', 'pdv_ou_parceiro', 'consultas',
      'aprovados', 'taxa_aprovacao', 'recusas_politica', 'recusas_antifraude', 'risco_alto'
    ],
    supportedDimensions: ['canal', 'parceiro', 'pdv', 'cidade', 'mes_referencia'],
    unsupportedDimensions: ['vendedor', 'operadora', 'safra_d120', 'ddd'],
    channelValues: ['Porta a Porta', 'Canais Presenciais', 'Lojas', 'Televendas', 'Agentes'],
    notes: 'Possui Canal e PDV/Parceiro, mas não possui vendedor individual.'
  },

  fato_indicadores_mensais: {
    reportId: 'CHURN_BL',
    reportName: 'Churn Banda Larga Total & PME',
    tableName: 'fato_indicadores_mensais',
    primaryMetric: 'taxa_real',
    primaryMetricLabel: 'Taxa de Churn',
    description: 'Desconexões mensais de Banda Larga fixa, metas orçamentárias (RxO) e acumulado YTD.',
    columns: [
      'segmento', 'mes_referencia', 'tipo_visao', 'cidade', 'base_real',
      'vol_real', 'vol_orc', 'rxo_delta', 'rxo_pct', 'taxa_real', 'taxa_orc',
      'taxa_delta_pp', 'ytd_real', 'ytd_orc', 'mom_pct'
    ],
    supportedDimensions: ['cidade', 'segmento', 'tipo_visao', 'mes_referencia'],
    unsupportedDimensions: ['canal', 'parceiro', 'vendedor', 'pdv', 'operadora', 'ddd'],
    notes: 'Apenas visão Cidade e Regional Norte. NÃO possui Canal nem Parceiro!'
  },

  fato_market_share: {
    reportId: 'MARKET_SHARE',
    reportName: 'Market Share & Concorrência (Anatel)',
    tableName: 'fato_market_share',
    primaryMetric: 'market_share_pct',
    primaryMetricLabel: 'Market Share %',
    description: 'Participação de mercado oficial da Anatel, acessos e adições líquidas (Net Adds).',
    columns: [
      'id', 'mes_referencia', 'cidade', 'uf', 'ddd', 'operadora',
      'produto', 'segmento', 'acessos', 'market_share_pct', 'net_adds', 'posicao_ranking'
    ],
    supportedDimensions: ['operadora', 'produto', 'segmento', 'cidade', 'ddd', 'mes_referencia'],
    unsupportedDimensions: ['canal', 'parceiro', 'vendedor', 'pdv', 'instalacoes', 'cura'],
    notes: 'Exclusiva para concorrentes (Claro, Vivo, TIM, Brisanet, Outras). NÃO possui Canal ou Parceiro.'
  },

  fato_speech_analytics: {
    reportId: 'SPEECH',
    reportName: 'Speech Analytics (Cancelamentos Transcritos)',
    tableName: 'fato_speech_analytics',
    primaryMetric: 'share_pct',
    primaryMetricLabel: 'Share de Motivos %',
    description: 'Transcrição e análise de motivos alegados por clientes no cancelamento.',
    columns: ['mes_referencia', 'cidade', 'motivo_cancelamento', 'submotivo', 'volume_chamadas', 'share_pct'],
    supportedDimensions: ['cidade', 'motivo', 'mes_referencia'],
    unsupportedDimensions: ['canal', 'parceiro', 'vendedor', 'operadora', 'safra']
  },

  fato_motivos_os: {
    reportId: 'MOTIVOS_OS',
    reportName: 'Motivos de Procura & Taxa de OS',
    tableName: 'fato_motivos_os',
    primaryMetric: 'taxa_os_concluida',
    primaryMetricLabel: 'Taxa de OS',
    description: 'Visitas técnicas, rechamadas em 48h e motivos de acionamento de suporte.',
    columns: ['mes_referencia', 'cidade', 'motivo_procura', 'taxa_rechamada_48h', 'taxa_os_concluida'],
    supportedDimensions: ['cidade', 'motivo', 'mes_referencia'],
    unsupportedDimensions: ['canal', 'parceiro', 'vendedor', 'operadora', 'safra']
  }
};

/**
 * Dicionário Semântico de Sinônimos e Termos Operacionais da Claro Regional Norte
 */
export const SEMANTIC_SYNONYMS = {
  // Ordenações e Sentidos
  ofensores: ['ofensor', 'ofensores', 'pior', 'piores', 'critico', 'criticos', 'sangria', 'maior perda', 'mais cancela', 'maior inadimplencia'],
  destaques: ['melhor', 'melhores', 'destaque', 'destaques', 'menor perda', 'mais saudavel', 'maior aprovacao', 'top desempenho'],
  
  // Entidades Dimensionais
  canal: ['canal', 'canais', 'pap', 'porta a porta', 'porta-a-porta', 'loja', 'lojas', 'televendas', 'call center', 'agente autorizado', 'agentes'],
  parceiro: ['parceiro', 'parceiros', 'pdv', 'pdvs', 'empresa', 'empresas', 'agente comercial', 'top connect', 'all rede', 'star link', 'rcell', 'cch', 'mendes'],
  vendedor: ['vendedor', 'vendedores', 'vendedora', 'vendedoras', 'consultor', 'consultores', 'equipe de venda', 'promotor'],
  operadora: ['concorrencia', 'concorrente', 'concorrentes', 'claro', 'vivo', 'tim', 'brisanet', 'oi', 'desktop', 'alfa'],
  
  // Períodos e Metas
  safra: ['safra', 'safras', 'safra recente', 'ultima safra', 'd120', 'd30', 'd60', 'madura'],
  orcamento: ['orcamento', 'orcado', 'meta', 'rxo', 'mom', 'yoy', 'ytd', 'acumulado']
};

/**
 * Validador Dimensional Pré-Query:
 * Verifica se a dimensão solicitada pelo usuário é suportada pelo relatório de destino.
 * Caso não seja, retorna explicação detalhada e alternativas para evitar alucinação.
 */
export function validateDimensionalCompatibility(requestedDimension, targetReportId) {
  if (!requestedDimension || !targetReportId) {
    return { compatible: true };
  }

  const dim = requestedDimension.toLowerCase();
  const repId = targetReportId.toUpperCase();

  // 1. Caso crítico: CANAL solicitado em CHURN SAFRA
  if (dim === 'canal' && repId === 'CHURN_SAFRA') {
    return {
      compatible: false,
      reason: 'A base oficial de Churn Safra D120 consolida os dados exclusivamente por Parceiro Comercial e por Cidade (não possui a dimensão Canal de Venda).',
      alternativeDimension: 'parceiro',
      alternativeTables: ['fato_fpd', 'fato_aprovacao_credito'],
      alternativeReports: [
        { id: 'FPD', name: 'FPD 60', metric: 'Qualidade no Primeiro Pagamento' },
        { id: 'CREDITO', name: 'Aprovação de Crédito', metric: 'Eficácia de Entrada' }
      ],
      suggestedMessage: 'Na base oficial de *Churn Safra D120*, a consolidação é realizada por *Parceiro Comercial* e por *Cidade* (não há segregação por canal de venda). Os parceiros mais ofensores são apresentados abaixo. Para analisar a ofensa específica por canais (ex: PAP, Lojas, Televendas), consulte os indicadores de *FPD 60* ou *Aprovação de Crédito*.'
    };
  }

  // 2. Caso crítico: CANAL solicitado em CHURN BANDA LARGA
  if (dim === 'canal' && (repId === 'CHURN_BL' || repId === 'CHURN_PME')) {
    return {
      compatible: false,
      reason: 'A base oficial de Churn Banda Larga (desconexões mensais) consolida apenas por Cidade e Regional Norte (não possui segregação por canal de venda).',
      alternativeTables: ['fato_fpd', 'fato_aprovacao_credito'],
      suggestedMessage: 'A base de *Churn Banda Larga Mensal* possui dados abertos apenas por *Cidade* e *Regional Norte* (sem visão de canal). Para verificar canais de venda, consulte *FPD 60* ou *Aprovação de Crédito*.'
    };
  }

  // 3. Caso crítico: VENDEDOR solicitado em CHURN SAFRA ou CHURN BL
  if (dim === 'vendedor' && repId !== 'FPD') {
    return {
      compatible: false,
      reason: 'Apenas a base de FPD possui a granularidade individual de Vendedores.',
      alternativeDimension: 'parceiro',
      alternativeTables: ['fato_fpd'],
      suggestedMessage: 'O acompanhamento nominal de *Vendedores* está disponível exclusivamente na base de *FPD (First Payment Default)*. Nas demais bases, a consolidação chega até o nível de Parceiro Comercial.'
    };
  }

  // 4. Caso crítico: OPERADORA solicitada fora de MARKET SHARE
  if (dim === 'operadora' && repId !== 'MARKET_SHARE') {
    return {
      compatible: false,
      reason: 'Dados de concorrência e operadoras estão restritos ao Market Share oficial da Anatel.',
      alternativeTables: ['fato_market_share']
    };
  }

  return { compatible: true };
}

/**
 * Retorna as tabelas que suportam uma determinada dimensão
 */
export function getTablesSupportingDimension(dimension) {
  const dim = (dimension || '').toLowerCase();
  const results = [];
  for (const [key, t] of Object.entries(SEMANTIC_TABLES)) {
    if (t.supportedDimensions.includes(dim)) {
      results.push(t);
    }
  }
  return results;
}

/**
 * Retorna o bloco de contexto semântico detalhado para injeção no prompt do gerador Text-to-SQL
 */
export function buildSemanticCatalogPrompt() {
  return `
=== CATÁLOGO SEMÂNTICO & REGRAS DE GRANULARIDADE DIMENSIONAL (CLARO REGIONAL NORTE) ===
MANDATÓRIO: Respeite estritamente as dimensões disponíveis em cada tabela. NUNCA invente colunas nem misture conceitos!

1. TABELA fato_fpd (Relatório FPD):
   - Dimensões disponíveis: canal ('PAP', 'Lojas', 'Televendas', 'Agente Autorizado', 'TODOS'), parceiro, vendedor, cidade, safra.
   - Indicador oficial padrão: FPD 60 (taxa_fpd60).
   - Se o usuário perguntar por 'canal ofensor' ou 'qual canal está pior' em FPD:
     SELECT canal, safra, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE canal IS NOT NULL AND canal != 'TODOS' AND canal != 'GERAL' GROUP BY canal, safra HAVING total_instalacoes >= 20 ORDER BY safra_ord DESC, taxa_fpd60 DESC LIMIT 5;
   - Se o usuário perguntar por 'parceiro ofensor' ou 'pdv ofensor' em FPD:
     SELECT parceiro, canal, cidade, safra, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE parceiro IS NOT NULL GROUP BY parceiro, safra HAVING total_instalacoes >= 10 ORDER BY safra_ord DESC, taxa_fpd60 DESC LIMIT 5;

2. TABELA fato_churn_safra (Relatório Churn Safra D120):
   - ATENÇÃO CRÍTICA: Esta tabela NÃO possui a coluna 'canal'!
   - Dimensão 'entidade_nome':
     * Quando visao = 'PARCEIRO', entidade_nome é o PARCEIRO COMERCIAL (ex: 'Top Connect', 'All Rede', 'Star Link'). NÃO É CANAL!
     * Quando visao = 'CIDADE', entidade_nome é a CIDADE (ex: 'Belém', 'Manaus').
   - SE O USUÁRIO PERGUNTAR POR CANAL EM CHURN SAFRA:
     Você DEVE retornar os parceiros ofensores e instruir o sintetizador a avisar ao usuário que a base consolida por Parceiro e Cidade, sem visão de canal.
     SELECT safra, visao, entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND status_safra = 'MADURA' ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 5;

3. TABELA fato_aprovacao_credito (Relatório Crédito & Antifraude):
   - Dimensões disponíveis: canal ('Porta a Porta', 'Canais Presenciais', 'Lojas', 'Televendas'), pdv_ou_parceiro, cidade, mes_referencia.
   - Indicador principal: taxa_aprovacao.
   - Se o usuário perguntar por 'canal ofensor' em crédito (menor aprovação):
     SELECT canal, mes_referencia, SUM(consultas) as total_consultas, SUM(aprovados) as total_aprovados, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa_aprovacao FROM fato_aprovacao_credito WHERE canal IS NOT NULL GROUP BY canal, mes_referencia ORDER BY mes_referencia DESC, taxa_aprovacao ASC LIMIT 5;

4. TABELA fato_indicadores_mensais (Relatório Churn Banda Larga):
   - Dimensões disponíveis: cidade ('Regional Norte' ou 14 cidades), segmento ('Banda Larga Total', 'Banda Larga PME'), tipo_visao ('TOTAL', 'VOLUNTARIO', 'INVOLUNTARIO').
   - ATENÇÃO: NÃO possui canal, parceiro nem vendedor!

5. TABELA fato_market_share (Relatório Market Share Anatel):
   - Dimensões disponíveis: operadora ('Claro', 'Vivo', 'TIM', etc.), produto ('BANDA_LARGA', 'MOVEL'), segmento ('RESIDENCIAL', 'POS_PAGO_SEM_M2M', '5G'), cidade, ddd.
   - ATENÇÃO: Se a pergunta for sobre Banda Larga/Residencial, filtre produto = 'BANDA_LARGA' AND segmento = 'RESIDENCIAL'.
`;
}
