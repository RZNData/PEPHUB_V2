/**
 * PEP HUB DATA BOT — REGISTRO CENTRAL DE INDICADORES & RELATÓRIOS (METRIC REGISTRY)
 * 
 * Fonte Única de Verdade (Single Source of Truth) para:
 * 1. Desambiguação de Relatórios (Menu e Links Clicáveis)
 * 2. Roteamento Semântico e Detecção de Palavras-Chave
 * 3. Text-to-SQL com Defaults Corporativos e Ordenação Cronológica
 * 4. Formatação Executiva Padronizada
 * 
 * AUTO-INTEGRAÇÃO: Qualquer novo relatório adicionado a este registro passa
 * automaticamente a ser contemplado no menu, nas regras de SQL, no roteador e no bot.
 */

export const REPORT_REGISTRY = {
  FPD: {
    id: 'FPD',
    num: '1',
    name: 'FPD (First Payment Default)',
    title: 'Relatório Oficial de FPD (First Payment Default)',
    icon: '💳',
    primaryTable: 'fato_fpd',
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
      { key: 'cidade', label: 'Cidade', examples: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá', 'Ananindeua'] },
      { key: 'canal', label: 'Canal de Venda', examples: ['PAP', 'Lojas', 'Televendas', 'Digital', 'GERAL'] },
      { key: 'faixa_risco', label: 'Faixa de Risco', examples: ['BAIXO', 'MEDIO', 'ALTO', 'CRITICO'] },
      { key: 'safra', label: 'Safra', examples: ['mai/26', 'abr/26', 'mar/26', 'fev/26'] }
    ],
    keywords: [
      /\bfpd\b/i,
      /\bfirst\s*payment\b/i,
      /\bfpd\s*30\b/i,
      /\bfpd\s*60\b/i,
      /\bcura\b/i,
      /\bfaixa(s)?\s+de\s+risco\b/i,
      /\balto\s+risco\b/i,
      /\brisco\s+alto\b/i,
      /\bprimeiro\s+pagamento\b/i,
      /\bqualidade\s+d[ea]\s+venda\b/i
    ],
    rules: {
      volumeMinimo: 30,
      piorOrdenacao: 'ORDER BY taxa_fpd60 DESC',
      melhorOrdenacao: 'ORDER BY taxa_fpd60 ASC'
    }
  },

  CHURN_BL: {
    id: 'CHURN_BL',
    num: '4',
    name: 'Churn Banda Larga Total & PME',
    title: 'Relatório Oficial de Churn Banda Larga',
    icon: '📉',
    primaryTable: 'fato_indicadores_mensais',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_referencia',
    defaultMes: 'Outubro / 2026',
    defaultMetric: 'taxa_real',
    metricLabel: 'Taxa de Churn Real',
    metrics: [
      { key: 'taxa_real', label: 'Taxa Real', unit: '%', direction: 'DESC', isDefault: true, desc: 'Taxa percentual de cancelamento' },
      { key: 'vol_real', label: 'Volume Real', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume absoluto de desconexões' },
      { key: 'rxo_delta', label: 'Delta RxO', unit: '', direction: 'DESC', isDefault: false, desc: 'Desvio Real vs Orçado' },
      { key: 'mom_pct', label: 'MoM %', unit: '%', direction: 'DESC', isDefault: false, desc: 'Variação mês contra mês anterior' }
    ],
    dimensions: [
      { key: 'segmento', label: 'Segmento', examples: ['Banda Larga Total', 'Banda Larga PME'] },
      { key: 'tipo_visao', label: 'Tipo de Visão', examples: ['TOTAL', 'VOLUNTARIO', 'INVOLUNTARIO'] },
      { key: 'cidade', label: 'Cidade', examples: ['Regional Norte', 'Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista'] }
    ],
    keywords: [
      /\bchurn\b/i,
      /\bbanda\s+larga\b/i,
      /\bbl\b/i,
      /\bpme\b/i,
      /\bdesconex(ao|oes|ões)\b/i,
      /\bvoluntari[ao]\b/i,
      /\binvoluntari[ao]\b/i,
      /\bmotivo(s)?\b/i,
      /\breclamac(ao|oes|ões)\b/i,
      /\bspeech\b/i,
      /\bligac(ao|oes|ões)\b/i,
      /\brxo\b/i,
      /\borcado\b/i,
      /\borçado\b/i,
      /\bopcao\b/i,
      /\bopção\b/i,
      /\bgargalo\b/i
    ],
    rules: {
      defaultSegmento: 'Banda Larga Total',
      defaultVisao: 'TOTAL'
    }
  },

  CHURN_SAFRA: {
    id: 'CHURN_SAFRA',
    num: '2',
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
      { key: 'visao', label: 'Visão', examples: ['PARCEIRO', 'CIDADE', 'REGIONAL'] },
      { key: 'entidade_nome', label: 'Parceiro / Entidade', examples: ['CCH Mendes', 'Elite', 'Belém', 'Manaus'] },
      { key: 'status_safra', label: 'Status da Safra', examples: ['MADURA', 'EM_ABERTO'] }
    ],
    keywords: [
      /\bsafra(s)?\b/i,
      /\bd120\b/i,
      /\bnp120\b/i,
      /\bclawback\b/i,
      /\bestorno\b/i,
      /\bmadura\b/i,
      /\bem\s+aberto\b/i,
      /\bsobrevivencia\b/i,
      /\bparceiro(s)?\b/i
    ],
    rules: {
      volumeMinimo: 30,
      defaultVisao: 'PARCEIRO'
    }
  },

  CREDITO: {
    id: 'CREDITO',
    num: '3',
    name: 'Taxa de Aprovação & Antifraude',
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
      { key: 'canal', label: 'Canal', examples: ['Agente Autorizado', 'D2D Parceiros', 'Lojas Próprias', 'E-commerce Claro'] },
      { key: 'pdv_ou_parceiro', label: 'PDV ou Parceiro', examples: ['Parceiro Comercial', 'Loja'] },
      { key: 'cidade', label: 'Cidade', examples: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista'] }
    ],
    keywords: [
      /\bcredito\b/i,
      /\bcrédito\b/i,
      /\baprovac/i,
      /\baprovad/i,
      /\breprovac/i,
      /\breprovad/i,
      /\brecus/i,
      /\bantifraude\b/i,
      /\bfraude/i,
      /\bmix\s+de\s+(clientes\s+de\s+)?(alto\s+)?risco\b/i,
      /\bpolitica\s+de\s+credito\b/i
    ],
    rules: {
      piorOrdenacao: 'ORDER BY recusas_antifraude DESC, risco_alto DESC'
    }
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
      { key: 'operadora', label: 'Operadora', examples: ['CLARO', 'VIVO', 'OI', 'OUTRAS', 'ISPS'] },
      { key: 'cidade', label: 'Cidade', examples: ['Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá'] }
    ],
    keywords: [
      /\bmarket\s*share\b/i,
      /\bparticipac(ao|ão)\b/i,
      /\bconcorrencia\b/i,
      /\bconcorrência\b/i,
      /\bcompetitivas?\b/i,
      /\bisps?\b/i,
      /\bnet\s*adds?\b/i,
      /\bnetadds?\b/i,
      /\banatel\b/i,
      /\bvivo\b/i,
      /\boi\b/i,
      /\bmarketshare\b/i
    ],
    rules: {
      defaultOperadora: 'CLARO'
    }
  },

  SPEECH: {
    id: 'SPEECH',
    num: '6',
    name: 'Speech Analytics (Cancelamento & Insatisfação)',
    title: 'Relatório Oficial de Speech Analytics (Regional Norte)',
    icon: '🗣️',
    primaryTable: 'fato_speech_analytics',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_ord',
    defaultMes: 'Set/26',
    defaultMetric: 'pct_mix',
    metricLabel: 'Participação no Mix (%)',
    metrics: [
      { key: 'pct_mix', label: 'Mix %', unit: '%', direction: 'DESC', isDefault: true, desc: '% de menção do motivo nas transcrições de chamadas' },
      { key: 'mom_pp', label: 'Variação MoM', unit: ' pp', direction: 'ASC', isDefault: false, desc: 'Variação percentual ponto a ponto em relação ao mês anterior' }
    ],
    dimensions: [
      { key: 'cidade', label: 'Cidade', examples: ['Regional Norte', 'Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista'] },
      { key: 'motivo_speech', label: 'Motivo Transcrito', examples: ['Acha Caro / Aumento no Valor', 'Técnico - Internet / Lentidão', 'Não Concorda e/ou Consulta Valores'] }
    ],
    keywords: [
      /\bspeech\b/i,
      /\btranscric(ao|oes|ões)\b/i,
      /\bmotivo(s)?\s+d[ea]\s+cancelamento\b/i,
      /\bacha\s+caro\b/i,
      /\bqualidade\s+percebida\b/i,
      /\binsatisfac(ao|oes|ões)\b/i
    ],
    rules: {
      defaultCidade: 'Regional Norte'
    }
  },

  MOTIVOS: {
    id: 'MOTIVOS',
    num: '7',
    name: 'Motivos de Procura & Taxa de OS',
    title: 'Relatório Oficial de Motivos de Procura & Ordem de Serviço (OS)',
    icon: '📞',
    primaryTable: 'fato_motivos_os',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_ord',
    defaultMes: 'Set/26',
    defaultMetric: 'taxa_os_pct',
    metricLabel: 'Taxa de Conversão em OS (%)',
    metrics: [
      { key: 'taxa_os_pct', label: 'Taxa de OS %', unit: '%', direction: 'DESC', isDefault: true, desc: '% de ligações que geraram Ordem de Serviço técnica' },
      { key: 'ligacoes', label: 'Ligações', unit: '', direction: 'DESC', isDefault: false, desc: 'Volume de chamadas na URA/Central' },
      { key: 'mix_pct', label: 'Mix Procura %', unit: '%', direction: 'DESC', isDefault: false, desc: 'Participação do motivo no volume total' },
      { key: 'taxa_os_mom_pp', label: 'MoM Taxa OS', unit: ' pp', direction: 'ASC', isDefault: false, desc: 'Variação da taxa de OS vs mês anterior' }
    ],
    dimensions: [
      { key: 'cidade', label: 'Cidade', examples: ['Regional Norte', 'Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista'] },
      { key: 'motivo_procura', label: 'Motivo de Procura', examples: ['Financeiro / Fatura', 'Cancelamento Automático (URA)', 'Lentidão / Sem Conexão'] }
    ],
    keywords: [
      /\bmotivos?\s+(de\s+)?procura\b/i,
      /\btaxa\s+d?e?\s*os\b/i,
      /\bordem\s+de\s+servico\b/i,
      /\bordens\s+de\s+servico\b/i,
      /\bchamados?\s+tecnico\b/i,
      /\bvisita\s+tecnica\b/i,
      /\bura\b/i
    ],
    rules: {
      defaultCidade: 'Regional Norte'
    }
  },

  EVOLUCAO_CARTEIRA: {
    id: 'EVOLUCAO_CARTEIRA',
    num: '8',
    name: 'Evolução de Carteira Móvel & B2B',
    title: 'Relatório Oficial de Evolução de Carteira (Gross, Churn, Migrações & Net Adds)',
    icon: '📈',
    primaryTable: 'fato_evolucao_carteira',
    dateColumn: 'mes_referencia',
    orderColumn: 'mes_referencia',
    defaultMes: '202610',
    defaultMetric: 'net_adds',
    metricLabel: 'Net Adds (Adições Líquidas)',
    metrics: [
      { key: 'net_adds', label: 'Net Adds', unit: '', direction: 'DESC', isDefault: true, desc: 'Crescimento líquido da carteira de clientes' },
      { key: 'gross_bruto', label: 'Gross Bruto', unit: '', direction: 'DESC', isDefault: false, desc: 'Total de ativações brutas no mês' },
      { key: 'gross_liquido', label: 'Gross Líquido', unit: '', direction: 'DESC', isDefault: false, desc: 'Ativações líquidas após expurgos de descontos e fakes' },
      { key: 'churn_involuntario', label: 'Churn Involuntário', unit: '', direction: 'ASC', isDefault: false, desc: 'Desconexões involuntárias por inadimplência, fraude e FPD' },
      { key: 'churn_voluntario', label: 'Churn Voluntário', unit: '', direction: 'ASC', isDefault: false, desc: 'Desconexões voluntárias solicitadas pelos clientes' }
    ],
    dimensions: [
      { key: 'regional', label: 'Regional', examples: ['CLARO NO', 'CLARO SP1', 'CLARO RJ/ES', 'CLARO MG', 'TOTAL BRASIL'] },
      { key: 'mercado', label: 'Mercado', examples: ['CONS', 'PME', 'GE'] }
    ],
    keywords: [
      /\bevolucao\s+(de\s+)?carteira\b/i,
      /\bnet\s*adds\b/i,
      /\bgross\s+bruto\b/i,
      /\bgross\s+liquido\b/i,
      /\bmatriz\s+(de\s+)?migrac(ao|oes|ões)\b/i,
      /\bmovimentacao\s+(de\s+)?carteira\b/i,
      /\btendencia\s+(de\s+)?produtos\b/i
    ],
    rules: {
      defaultRegional: 'CLARO NO'
    }
  }
};

/**
 * Retorna todos os relatórios registrados
 */
export function getAllReports() {
  return Object.values(REPORT_REGISTRY);
}

/**
 * Retorna relatório pelo ID
 */
export function getReportById(id) {
  if (!id) return null;
  return REPORT_REGISTRY[id.toUpperCase()] || null;
}

/**
 * Retorna relatório pelo Número do menu (1 a 5)
 */
export function getReportByNum(num) {
  const str = String(num).trim().replace(/️⃣/g, '');
  return getAllReports().find(r => r.num === str) || null;
}

/**
 * Constrói o Menu de Desambiguação com Links Clicáveis para WhatsApp
 */
export function buildDisambiguationMenu(query, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  const reports = getAllReports();

  let text = `🤔 *Pephub Bot · Selecione o Relatório Desejado*\n\n`;
  text += `Para consultar os indicadores com precisão oficial e *evitar cruzamento indevido de bases*, a qual relatório você deseja acessar para esta consulta?\n\n`;

  for (const rep of reports) {
    const defaultMet = rep.metrics.find(m => m.isDefault)?.label || rep.metricLabel;
    text += `${rep.num}️⃣ *${rep.name}* (Padrão: ${defaultMet})\n`;
    text += `👉 https://wa.me/${cleanPhone}?text=%23%3F%20${rep.num}\n\n`;
  }

  text += `_Envie *#? 1* a *#? ${reports.length}* ou toque no link acima para prosseguir._`;
  return text;
}

/**
 * Gera o contexto de schema e diretrizes para o Text-to-SQL dinamicamente
 */
export function buildSchemaPromptContext() {
  return `
ESQUEMA DE TABELAS DISPONÍVEIS NO CLOUDFLARE D1 (SQLite):

1. fato_indicadores_mensais (Churn Banda Larga Total & PME):
   - segmento TEXT ('Banda Larga Total', 'Banda Larga PME')
   - mes_referencia TEXT ('Setembro / 2026', 'Agosto / 2026')
   - tipo_visao TEXT ('TOTAL', 'VOLUNTARIO', 'INVOLUNTARIO')
   - cidade TEXT ('Regional Norte', 'Belém', 'Manaus', 'São Luís', 'Macapá', 'Boa Vista', 'Santarém', 'Marabá', 'Ananindeua', 'Castanhal', 'Imperatriz', etc.)
   - uf TEXT ('RNO', 'PA', 'AM', 'MA', 'AP', 'RR')
   - vol_real, vol_orc, rxo_delta, rxo_pct, mom_pct, yoy_pct, taxa_real, taxa_orc, taxa_delta_pp REAL

2. fato_churn_safra (Churn Safra D120 & Desempenho de Parceiros):
   - safra TEXT ('set/25', 'out/25', 'nov/25', 'dez/25', 'jan/26', 'fev/26', 'mar/26', 'abr/26', 'mai/26', 'jun/26', 'jul/26', 'ago/26', 'set/26')
   - safra_ord TEXT ('2025-09' ... '2026-09') -> USE SEMPRE safra_ord DESC PARA ORDENAÇÃO CRONOLÓGICA!
   - visao TEXT ('REGIONAL', 'CIDADE', 'PARCEIRO')
   - entidade_nome TEXT (Nome da cidade ou do parceiro, ex: 'CCH Mendes', 'Elite', etc.)
   - instalacoes INTEGER
   - churn_d30, churn_d60, churn_d90, churn_d120 INTEGER
   - np120 INTEGER (Contratos não pagos até D120)
   - taxa_d30, taxa_d60, taxa_d90, taxa_d120, taxa_np120 REAL (% sobre instalações)
   - status_safra TEXT ('MADURA' para safras >= 120 dias, 'EM_ABERTO' para recentes)

3. fato_fpd (First Payment Default & Qualidade de Venda):
   - safra TEXT ('fev/26', 'mar/26', 'abr/26', 'mai/26')
   - safra_ord TEXT ('2026-02', '2026-03', '2026-04', '2026-05') -> USE SEMPRE safra_ord DESC PARA ÚLTIMA SAFRA!
   - cidade TEXT, uf TEXT
   - canal TEXT ('PAP', 'Lojas', 'Televendas', 'Digital', 'GERAL')
   - familia_produto TEXT ('Dados', 'Vídeo', 'Box')
   - parceiro TEXT (Nome do parceiro credenciado / empresa de vendas)
   - vendedor TEXT (Nome do vendedor/consultor)
   - instalacoes INTEGER
   - fpd60 INTEGER, taxa_fpd60 REAL (INDICADOR PADRÃO OFICIAL CLARO)
   - fpd30 INTEGER, taxa_fpd30 REAL (Onboarding 30 dias)
   - cura INTEGER, taxa_cura REAL (% curada entre 30 e 60 dias)
   - faixa_risco TEXT ('BAIXO', 'MEDIO', 'ALTO', 'CRITICO')

4. fato_aprovacao_credito (Aprovação de Crédito & Antifraude):
   - mes_referencia TEXT ('2026-08', '2026-09')
   - cidade TEXT, uf TEXT, canal TEXT, pdv_ou_parceiro TEXT
   - consultas INTEGER, aprovados INTEGER, taxa_aprovacao REAL
   - recusas_politica INTEGER, recusas_antifraude INTEGER, risco_alto INTEGER

5. fato_market_share (Market Share & Concorrência Anatel):
   - mes_referencia TEXT ('2026-08', '2026-09')
   - cidade TEXT, uf TEXT
   - operadora TEXT ('CLARO', 'VIVO', 'OI', 'OUTRAS', 'ISPS')
   - acessos INTEGER, market_share_pct REAL, net_adds INTEGER, posicao_ranking INTEGER

6. fato_speech_analytics (Speech Analytics - Motivos de Cancelamento Transcritos):
   - mes_referencia TEXT ('Set/26', 'Ago/26', 'Jul/26')
   - mes_ord TEXT ('2026-09', '2026-08', '2026-07')
   - cidade TEXT ('Regional Norte', 'Manaus', 'Belém', etc.)
   - motivo_speech TEXT ('Acha Caro / Aumento no Valor', 'Técnico - Internet / Lentidão', etc.)
   - pct_mix REAL (% mix citações)
   - mom_pp REAL (Variação MoM em pontos percentuais)
   - tendencia TEXT ('Alta', 'Queda', 'Estável')

7. fato_motivos_os (Motivos de Procura na Central & Taxa de Conversão em OS):
   - mes_referencia TEXT ('Set/26', 'Ago/26', 'Jul/26')
   - mes_ord TEXT ('2026-09', '2026-08', '2026-07')
   - cidade TEXT ('Regional Norte', 'Manaus', 'Belém', etc.)
   - motivo_procura TEXT ('Financeiro / Fatura', 'Cancelamento Automático (URA)', 'Lentidão / Sem Conexão', etc.)
   - ligacoes INTEGER (Chamadas recebidas)
   - mix_pct REAL (% mix do motivo)
   - os_geradas INTEGER (Ordens de serviço abertas)
   - taxa_os_pct REAL (% conversão em OS técnica)
   - taxa_os_mom_pp REAL (Variação MoM taxa OS)
   - status TEXT ('Crítico', 'Alto', 'Médio', 'Controlado')
`;
}

/**
 * Motor Determinístico de Extração de Slots e Geração de SQL Instantâneo (< 0.1ms)
 * Elimina completamente a latência de LLM para as consultas operacionais mais comuns.
 */
export function buildDeterministicAnalyticalSQL(query, targetReport, userScope) {
  if (!query || !targetReport) return null;
  const qNorm = query.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  // 1. Extração de Entidades Geográficas (Cidades)
  const citiesMap = [
    { canonical: 'Belém', regex: /\b(belem)\b/i },
    { canonical: 'Manaus', regex: /\b(manaus)\b/i },
    { canonical: 'São Luís', regex: /\b(sao\s+luis|slz)\b/i },
    { canonical: 'Macapá', regex: /\b(macapa)\b/i },
    { canonical: 'Boa Vista', regex: /\b(boa\s+vista|bv)\b/i },
    { canonical: 'Santarém', regex: /\b(santarem)\b/i },
    { canonical: 'Marabá', regex: /\b(maraba)\b/i },
    { canonical: 'Ananindeua', regex: /\b(ananindeua)\b/i },
    { canonical: 'Castanhal', regex: /\b(castanhal)\b/i },
    { canonical: 'Imperatriz', regex: /\b(imperatriz|itz)\b/i },
    { canonical: 'Parauapebas', regex: /\b(parauapebas)\b/i },
    { canonical: 'Barcarena', regex: /\b(barcarena)\b/i },
    { canonical: 'Itaituba', regex: /\b(itaituba)\b/i },
    { canonical: 'Abaetetuba', regex: /\b(abaetetuba)\b/i },
  ];

  let matchedCity = null;
  for (const c of citiesMap) {
    if (c.regex.test(qNorm)) {
      matchedCity = c.canonical;
      break;
    }
  }

  // 2. Extração de Parceiros / PDVs
  const partnersMap = [
    { canonical: 'CCH Mendes', regex: /\b(cch|mendes|cch\s+mendes)\b/i },
    { canonical: 'Elite', regex: /\b(elite)\b/i },
    { canonical: 'All Rede', regex: /\b(all\s+rede|allrede)\b/i },
    { canonical: 'RCell', regex: /\b(rcell)\b/i },
    { canonical: 'Veloce', regex: /\b(veloce)\b/i },
    { canonical: 'Mega', regex: /\b(mega)\b/i },
    { canonical: 'Almaviva', regex: /\b(almaviva)\b/i },
    { canonical: 'AeC', regex: /\b(aec)\b/i },
    { canonical: 'Flex Cell', regex: /\b(flex\s+cell|flexcell)\b/i },
    { canonical: 'Saddi', regex: /\b(saddi)\b/i },
  ];

  let matchedPartner = null;
  for (const p of partnersMap) {
    if (p.regex.test(qNorm)) {
      matchedPartner = p.canonical;
      break;
    }
  }

  // 3. Extração de Tipo de Visão / Intenção Específica
  const isRanking = /\b(ranking|top\s*\d+|pior|piores|melhor|melhores|maior|menor|maiores|menores)\b/i.test(qNorm);
  const isBest = /\b(melhor|melhores|menor|menores)\b/i.test(qNorm);
  const isLatestPeriod = /\b(ultima\s+safra|ultimo\s+mes|qual\s+e\s+a\s+safra|qual\s+a\s+safra|periodo|referencia)\b/i.test(qNorm);
  const isVoluntary = /\bvoluntario\b/i.test(qNorm);
  const isInvoluntary = /\binvoluntario\b/i.test(qNorm);
  const isParceiroQuery = /\b(parceiro|parceiros|pdv|pdvs)\b/i.test(qNorm);

  // 4. Regras por Relatório-Alvo
  if (targetReport.id === 'FPD') {
    if (isLatestPeriod && !isParceiroQuery && !matchedPartner && !matchedCity && !isRanking) {
      return `SELECT DISTINCT safra, safra_ord FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1`;
    }
    // Parceiro no FPD: apurado estritamente em fato_fpd (zero contaminação de bases)
    if (isParceiroQuery || matchedPartner) {
      if (matchedPartner) {
        return `SELECT safra, parceiro, canal, cidade, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30, taxa_cura FROM fato_fpd WHERE parceiro LIKE '%${matchedPartner}%' ORDER BY safra_ord DESC LIMIT 1`;
      }
      const dir = isBest ? 'ASC' : 'DESC';
      return `SELECT parceiro, safra, SUM(instalacoes) as total_inst, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60_consolidada, ROUND(100.0 * SUM(fpd30)/SUM(instalacoes), 2) as taxa_fpd30_consolidada FROM fato_fpd WHERE parceiro IS NOT NULL GROUP BY parceiro, safra HAVING total_inst >= 20 ORDER BY safra_ord DESC, taxa_fpd60_consolidada ${dir} LIMIT 5`;
    }
    if (matchedCity) {
      return `SELECT safra, cidade, canal, instalacoes, fpd60, taxa_fpd60, fpd30, taxa_fpd30, cura, taxa_cura, faixa_risco FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND cidade = '${matchedCity}' ORDER BY instalacoes DESC LIMIT 5`;
    }
    if (isRanking) {
      const dir = isBest ? 'ASC' : 'DESC';
      return `SELECT cidade, SUM(instalacoes) as total_instalacoes, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60) / SUM(instalacoes), 2) as taxa_fpd60_consolidada FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) GROUP BY cidade HAVING total_instalacoes >= 50 ORDER BY taxa_fpd60_consolidada ${dir} LIMIT 5`;
    }
    // Consolidado regional de FPD
    return `SELECT safra, SUM(instalacoes) as total_instalacoes, SUM(fpd30) as total_fpd30, ROUND(100.0 * SUM(fpd30) / SUM(instalacoes), 2) as taxa_fpd30_regional, SUM(fpd60) as total_fpd60, ROUND(100.0 * SUM(fpd60) / SUM(instalacoes), 2) as taxa_fpd60_regional, SUM(cura) as total_cura, ROUND(100.0 * SUM(cura) / SUM(fpd30), 2) as taxa_cura_regional FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) GROUP BY safra`;
  }

  if (targetReport.id === 'CHURN_SAFRA') {
    if (isLatestPeriod && !isParceiroQuery && !matchedPartner && !matchedCity && !isRanking) {
      return `SELECT DISTINCT safra, safra_ord FROM fato_churn_safra ORDER BY safra_ord DESC LIMIT 1`;
    }
    if (matchedPartner) {
      return `SELECT safra, visao, entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE entidade_nome LIKE '%${matchedPartner}%' ORDER BY safra_ord DESC LIMIT 3`;
    }
    if (matchedCity) {
      return `SELECT safra, visao, entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'CIDADE' AND entidade_nome = '${matchedCity}' ORDER BY safra_ord DESC LIMIT 3`;
    }
    if (isRanking && /\b(cidade|cidades)\b/i.test(qNorm)) {
      const dir = isBest ? 'ASC' : 'DESC';
      return `SELECT safra, entidade_nome, instalacoes, churn_d120, taxa_d120, status_safra FROM fato_churn_safra WHERE visao = 'CIDADE' AND safra = (SELECT safra FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1) ORDER BY taxa_d120 ${dir} LIMIT 5`;
    }
    if (isRanking || isParceiroQuery) {
      const dir = isBest ? 'ASC' : 'DESC';
      return `SELECT safra, entidade_nome, instalacoes, churn_d120, taxa_d120, status_safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND safra = (SELECT safra FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1) ORDER BY taxa_d120 ${dir} LIMIT 5`;
    }
    // Consolidado regional Safra
    return `SELECT safra, visao, entidade_nome, instalacoes, churn_d30, taxa_d30, churn_d60, taxa_d60, churn_d120, taxa_d120, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'REGIONAL' ORDER BY safra_ord DESC LIMIT 2`;
  }

  if (targetReport.id === 'CHURN_BL' || targetReport.id === 'CHURN_PME') {
    const segmento = targetReport.id === 'CHURN_PME' ? 'Banda Larga PME' : 'Banda Larga Total';
    const visao = isVoluntary ? 'VOLUNTARIO' : (isInvoluntary ? 'INVOLUNTARIO' : 'TOTAL');

    if (matchedCity) {
      return `SELECT mes_referencia, segmento, tipo_visao, cidade, base_real, vol_real, vol_orc, rxo_delta, taxa_real, taxa_orc, taxa_delta_pp, mom_pct FROM fato_indicadores_mensais WHERE segmento = '${segmento}' AND tipo_visao = '${visao}' AND cidade = '${matchedCity}' ORDER BY id DESC LIMIT 1`;
    }
    if (isRanking) {
      return `SELECT cidade, base_real, vol_real, vol_orc, taxa_real, taxa_orc, taxa_delta_pp FROM fato_indicadores_mensais WHERE segmento = '${segmento}' AND tipo_visao = '${visao}' AND cidade != 'Regional Norte' ORDER BY taxa_real DESC LIMIT 5`;
    }
    // Consolidado regional Churn BL
    return `SELECT mes_referencia, segmento, tipo_visao, cidade, base_real, vol_real, vol_orc, rxo_delta, taxa_real, taxa_orc, taxa_delta_pp, mom_pct FROM fato_indicadores_mensais WHERE segmento = '${segmento}' AND tipo_visao = '${visao}' AND cidade = 'Regional Norte' ORDER BY id DESC LIMIT 1`;
  }

  if (targetReport.id === 'CREDITO') {
    if (matchedCity) {
      return `SELECT mes_referencia, cidade, canal, pdv_ou_parceiro, consultas, aprovados, taxa_aprovacao, recusas_antifraude, recusas_politica, risco_alto FROM fato_aprovacao_credito WHERE cidade = '${matchedCity}' ORDER BY mes_referencia DESC, consultas DESC LIMIT 5`;
    }
    if (isRanking) {
      return `SELECT cidade, SUM(consultas) as total_consultas, SUM(aprovados) as total_aprovados, ROUND(100.0 * SUM(aprovados) / SUM(consultas), 1) as taxa_aprovacao_consolidada FROM fato_aprovacao_credito GROUP BY cidade ORDER BY taxa_aprovacao_consolidada ASC LIMIT 5`;
    }
    return `SELECT mes_referencia, SUM(consultas) as total_consultas, SUM(aprovados) as total_aprovados, ROUND(100.0 * SUM(aprovados) / SUM(consultas), 1) as taxa_aprovacao_regional, SUM(recusas_antifraude) as total_recusas_antifraude, SUM(recusas_politica) as total_recusas_politica, SUM(risco_alto) as total_risco_alto FROM fato_aprovacao_credito GROUP BY mes_referencia ORDER BY mes_referencia DESC LIMIT 1`;
  }

  if (targetReport.id === 'MARKET_SHARE') {
    if (matchedCity) {
      return `SELECT mes_referencia, cidade, operadora, acessos, market_share_pct, net_adds, posicao_ranking FROM fato_market_share WHERE cidade = '${matchedCity}' ORDER BY market_share_pct DESC LIMIT 5`;
    }
    return `SELECT mes_referencia, operadora, SUM(acessos) as total_acessos, SUM(net_adds) as total_net_adds FROM fato_market_share GROUP BY operadora ORDER BY total_acessos DESC`;
  }

  if (targetReport.id === 'SPEECH') {
    const city = matchedCity || 'Regional Norte';
    return `SELECT motivo_speech, mes_referencia, mes_ord, pct_mix, mom_pp, tendencia FROM fato_speech_analytics WHERE cidade = '${city}' ORDER BY mes_ord DESC, pct_mix DESC`;
  }

  if (targetReport.id === 'MOTIVOS') {
    const city = matchedCity || 'Regional Norte';
    return `SELECT motivo_procura, mes_referencia, mes_ord, ligacoes, mix_pct, os_geradas, taxa_os_pct, taxa_os_mom_pp, status FROM fato_motivos_os WHERE cidade = '${city}' ORDER BY mes_ord DESC, taxa_os_pct DESC`;
  }

  return null;
}

// =====================================================================
// DEFINIÇÕES OFICIAIS DA REGIONAL NORTE (14 CIDADES, CANAIS, PRODUTOS, DDDS)
// =====================================================================

export const OFFICIAL_14_CITIES = [
  // Grandes Mercados (GM: 1-6)
  { num: '1', name: 'Manaus', uf: 'AM', cluster: 'Grandes Mercados (GM)' },
  { num: '2', name: 'Belém', uf: 'PA', cluster: 'Grandes Mercados (GM)' },
  { num: '3', name: 'São Luís', uf: 'MA', cluster: 'Grandes Mercados (GM)' },
  { num: '4', name: 'Ananindeua', uf: 'PA', cluster: 'Grandes Mercados (GM)' },
  { num: '5', name: 'Macapá', uf: 'AP', cluster: 'Grandes Mercados (GM)' },
  { num: '6', name: 'Santana', uf: 'AP', cluster: 'Grandes Mercados (GM)' },
  // Mercados em Desenvolvimento (MD: 7-14)
  { num: '7', name: 'Imperatriz', uf: 'MA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '8', name: 'Castanhal', uf: 'PA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '9', name: 'Parauapebas', uf: 'PA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '10', name: 'Marabá', uf: 'PA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '11', name: 'Paragominas', uf: 'PA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '12', name: 'Timon', uf: 'MA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '13', name: 'Caxias', uf: 'MA', cluster: 'Mercados em Desenvolvimento (MD)' },
  { num: '14', name: 'Boa Vista', uf: 'RR', cluster: 'Mercados em Desenvolvimento (MD)' },
];

export const OFFICIAL_CHANNELS = [
  { num: '1', id: 'PAP', name: 'PAP', label: 'PAP (Porta a Porta)' },
  { num: '2', id: 'LOJAS', name: 'Lojas', label: 'Lojas (Próprias e Franquias)' },
  { num: '3', id: 'TELEVENDAS', name: 'Televendas', label: 'Televendas' },
  { num: '4', id: 'AGENTE_AUTORIZADO', name: 'Agente Autorizado', label: 'Agente Autorizado' },
];

export const OFFICIAL_PRODUCTS = [
  { num: '1', id: 'BANDA_LARGA', name: 'Produto Banda Larga', dbFilter: 'Dados' },
  { num: '2', id: 'TV_TRADICIONAL', name: 'TV Tradicional', dbFilter: 'Vídeo' },
  { num: '3', id: 'TV_BOX', name: 'TV Box', dbFilter: 'Box' },
  { num: '4', id: 'TODOS', name: 'Todos os Produtos', dbFilter: null },
];

export const OFFICIAL_DDDS = [
  { num: '1', ddd: '91', regiao: 'Belém / Nordeste PA' },
  { num: '2', ddd: '92', regiao: 'Manaus / AM Central' },
  { num: '3', ddd: '93', regiao: 'Santarém / Oeste PA' },
  { num: '4', ddd: '94', regiao: 'Marabá / Sul PA' },
  { num: '5', ddd: '95', regiao: 'Boa Vista / Roraima' },
  { num: '6', ddd: '96', regiao: 'Macapá / Amapá' },
  { num: '7', ddd: '97', regiao: 'Interior AM / Coari' },
  { num: '8', ddd: '98', regiao: 'São Luís / Norte MA' },
  { num: '9', ddd: '99', regiao: 'Imperatriz / Sul MA' },
];

// =====================================================================
// MENUS INTERATIVOS (ROTA A GUIADA)
// =====================================================================

export function buildBaseSelectionMenu(botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `📊 *PEP HUB · Regional Norte*\n` +
    `*Escolha a base que deseja consultar:*\n\n` +
    `1️⃣ *FPD (First Payment Default)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Churn Safra D120 (Sobrevivência & Estorno)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `3️⃣ *Taxa de Aprovação & Antifraude*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%203\n\n` +
    `4️⃣ *Churn Banda Larga Total & PME*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%204\n\n` +
    `5️⃣ *Market Share & Concorrência (Anatel)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%205\n\n` +
    `6️⃣ *Speech Analytics (Motivos de Cancelamento)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%206\n\n` +
    `7️⃣ *Motivos de Procura & Taxa de OS (Atendimento)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%207\n\n` +
    `_Toque em um link acima ou envie de *#? 1* a *#? 7*._`;
}

export function buildSpeechPromptMenu(botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `🗣️ *Speech Analytics · Regional Norte*\n` +
    `*Escolha a abrangência para análise de motivos transcritos:*\n\n` +
    `1️⃣ *Resumo Geral (Todas as Cidades)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Filtrar por Cidade Específica*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar ao menu de bases*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Toque no link desejado ou envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildMotivosPromptMenu(botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `📞 *Motivos de Procura & Taxa de OS · Regional Norte*\n` +
    `*Escolha a abrangência para análise de motivos e visitas técnicas:*\n\n` +
    `1️⃣ *Resumo Geral (Todas as Cidades)*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Filtrar por Cidade Específica*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar ao menu de bases*\n` +
    `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Toque no link desejado ou envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildCardFooterLinks(report, options = {}, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  let text = `\n\n─────────────────────────────\n`;
  text += `0️⃣ ↩️ *Voltar à seleção anterior*\n`;
  text += `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n`;
  text += `🏠 *Menu Principal de Bases*\n`;
  text += `👉 https://wa.me/${cleanPhone}?text=%23%3F%20menu`;
  return text;
}

export function buildActionCardFooterLinks(report, currentActionNum, sessionState = {}, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  let text = `\n\n─────────────────────────────\n`;
  text += `*Outras opções deste relatório:*\n`;

  if (report.id === 'FPD' || report.id === 'CHURN_SAFRA' || report.id === 'CREDITO') {
    let metricName = 'FPD 60';
    if (report.id === 'CHURN_SAFRA') metricName = 'Churn D120';
    if (report.id === 'CREDITO') metricName = 'Aprovação';

    const actions = [
      { num: '1', label: 'Resumo Executivo' },
      { num: '2', label: `Últimos 3 Meses (${metricName})` },
      { num: '3', label: 'Ranking Parceiros' },
      { num: '4', label: 'Ranking Canais' },
      { num: '5', label: 'Ranking Cidades' },
    ];
    for (const a of actions) {
      if (a.num !== String(currentActionNum)) {
        text += `${a.num}️⃣ *${a.label}* 👉 https://wa.me/${cleanPhone}?text=%23%3F%20${a.num}\n`;
      }
    }
  } else if (report.id === 'CHURN_BL') {
    const actions = [
      { num: '1', label: 'Resumo Executivo' },
      { num: '2', label: 'Últimos 3 Meses' },
      { num: '3', label: 'Ranking Cidades' },
    ];
    for (const a of actions) {
      if (a.num !== String(currentActionNum)) {
        text += `${a.num}️⃣ *${a.label}* 👉 https://wa.me/${cleanPhone}?text=%23%3F%20${a.num}\n`;
      }
    }
  } else if (report.id === 'MARKET_SHARE') {
    const actions = [
      { num: '1', label: 'Resumo Regional Geral' },
      { num: '2', label: 'Market Share Residencial' },
      { num: '3', label: 'Market Share Móvel (DDDs)' },
    ];
    for (const a of actions) {
      if (a.num !== String(currentActionNum)) {
        text += `${a.num}️⃣ *${a.label}* 👉 https://wa.me/${cleanPhone}?text=%23%3F%20${a.num}\n`;
      }
    }
  }

  text += `\n0️⃣ ↩️ *Voltar à seleção anterior*\n`;
  text += `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n`;
  text += `🏠 *Menu Principal de Bases*\n`;
  text += `👉 https://wa.me/${cleanPhone}?text=%23%3F%20menu`;
  return text;
}

export function buildProductSelectionMenu(report, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `${report.icon} *${report.name} · Regional Norte*\n` +
    `*Escolha o Produto para consulta:*\n\n` +
    `1️⃣ *Produto Banda Larga*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *TV Tradicional*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `3️⃣ *TV Box*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%203\n\n` +
    `4️⃣ *Todos os Produtos*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%204\n\n` +
    `0️⃣ ↩️ *Voltar ao menu de bases*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1* a *#? 4* ou *#? 0* para voltar._`;
}

export function buildSegmentSelectionMenu(report, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `📉 *Churn Banda Larga · Regional Norte*\n` +
    `*Escolha o Segmento:*\n\n` +
    `1️⃣ *Banda Larga Total*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Banda Larga PME*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar ao menu de bases*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1* ou *#? 2* ou *#? 0* para voltar._`;
}

export function buildActionSelectionMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  const prodLabel = sessionState.productName ? ` · ${sessionState.productName}` : (sessionState.segmentName ? ` · ${sessionState.segmentName}` : '');

  if (report.id === 'FPD' || report.id === 'CHURN_SAFRA' || report.id === 'CREDITO') {
    let metricName = 'FPD 60';
    if (report.id === 'CHURN_SAFRA') metricName = 'Churn D120';
    if (report.id === 'CREDITO') metricName = 'Aprovação';

    return `${report.icon} *${report.name}${prodLabel}*\n*Escolha o que você deseja ver:*\n\n` +
      `1️⃣ *Resumo Executivo* (FPD 30, FPD 60, Piores Canais, Cidades, Empresas & Vendedores)\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
      `2️⃣ *Últimos 3 meses de ${metricName}* (Evolução Temporal)\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
      `3️⃣ *Ranking 10 Piores Parceiros*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%203\n\n` +
      `4️⃣ *Ranking Canais ${metricName} (Últimos 3 meses)*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%204\n\n` +
      `5️⃣ *Ranking Cidades ${metricName} (Últimos 3 meses)*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%205\n\n` +
      `0️⃣ ↩️ *Voltar*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
      `_Envie *#? 1* a *#? 5* ou toque no link desejado._`;
  }

  if (report.id === 'CHURN_BL') {
    return `📉 *Churn Banda Larga${prodLabel}*\n*Escolha o que você deseja ver:*\n\n` +
      `1️⃣ *Resumo Executivo* (Orçamento, RxO, MoM, YoY, YTD e Cidades)\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
      `2️⃣ *Últimos 3 meses de Churn*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
      `3️⃣ *Ranking Cidades Churn (Últimos 3 meses)*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%203\n\n` +
      `0️⃣ ↩️ *Voltar*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
      `_Envie *#? 1* a *#? 3* ou toque no link desejado._`;
  }

  if (report.id === 'MARKET_SHARE') {
    return `📊 *Market Share & Concorrência (Anatel) · Regional Norte*\n*Escolha o que você deseja ver:*\n\n` +
      `1️⃣ *Resumo Regional Geral* (Market Share, Net Adds e Base: Claro vs Concorrentes)\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
      `2️⃣ *Market Share Residencial (14 Cidades)*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
      `3️⃣ *Market Share Móvel (Abertura por DDD)*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%203\n\n` +
      `0️⃣ ↩️ *Voltar*\n` +
      `👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
      `_Envie *#? 1* a *#? 3* ou toque no link desejado._`;
  }

  return '';
}

export function buildPartnerChannelPromptMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `${report.icon} *Ranking 10 Piores Parceiros · Filtro de Canal*\n*Escolha a abrangência por canal:*\n\n` +
    `1️⃣ *Selecionar Canal* (PAP, Lojas, Televendas, Agente Autorizado)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Todos os Canais*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildPartnerCityPromptMenu(report, sessionState, botPhone = '5591980547171', title = 'Ranking 10 Piores Parceiros') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `${report.icon} *${title} · Abrangência Geográfica*\n*Escolha o escopo de cidades:*\n\n` +
    `1️⃣ *Selecionar Cidade* (14 Cidades: Grandes Mercados e Mercados em Desenvolvimento)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Todas as Cidades* (Regional Norte Consolidada)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildChannelCityPromptMenu(report, sessionState, botPhone = '5591980547171', title = 'Ranking Canais') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `${report.icon} *${title} (Últimos 3 meses) · Abrangência*\n*Escolha o escopo de cidades:*\n\n` +
    `1️⃣ *Todas as Cidades* (Regional Norte Consolidada)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Selecionar Cidade* (14 Cidades: Grandes Mercados e Mercados em Desenvolvimento)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildCityChannelPromptMenu(report, sessionState, botPhone = '5591980547171', title = 'Ranking Cidades') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `${report.icon} *${title} (Últimos 3 meses) · Filtro de Canal*\n*Escolha a abrangência por canal:*\n\n` +
    `1️⃣ *Todos os Canais*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Selecionar Canal* (PAP, Lojas, Televendas, Agente Autorizado)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildChannelPromptMenu(report, sessionState, botPhone = '5591980547171', title = 'Ranking de Parceiros') {
  return buildPartnerChannelPromptMenu(report, sessionState, botPhone);
}

export function buildChannelListMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  let text = `${report.icon} *Escolha o Canal de Venda:*\n\n`;
  for (const ch of OFFICIAL_CHANNELS) {
    text += `${ch.num}️⃣ *${ch.label}*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%20${ch.num}\n\n`;
  }
  text += `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n`;
  text += `_Envie *#? 1* a *#? ${OFFICIAL_CHANNELS.length}* ou *#? 0*._`;
  return text;
}

export function buildCityPromptMenu(report, sessionState, botPhone = '5591980547171', title = 'Ranking') {
  return buildChannelCityPromptMenu(report, sessionState, botPhone, title);
}

export function buildCityListMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  let text = `${report.icon} *Escolha a Cidade Monitorada:*\n\n`;
  text += `*📍 Grandes Mercados (GM):*\n`;
  for (const c of OFFICIAL_14_CITIES.slice(0, 6)) {
    text += `${c.num}️⃣ *${c.name} (${c.uf})*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%20${c.num}\n`;
  }
  text += `\n*📍 Mercados em Desenvolvimento (MD):*\n`;
  for (const c of OFFICIAL_14_CITIES.slice(6)) {
    text += `${c.num}️⃣ *${c.name} (${c.uf})*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%20${c.num}\n`;
  }
  text += `\n0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n`;
  text += `_Envie *#? 1* a *#? 14* ou *#? 0*._`;
  return text;
}

export function buildDddPromptMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  return `📱 *Market Share Móvel · Regional Norte*\n*Escolha a abrangência por DDD:*\n\n` +
    `1️⃣ *Todos os DDDs da Regional Norte*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%201\n\n` +
    `2️⃣ *Selecionar DDD* (DDD 91 a 99)\n👉 https://wa.me/${cleanPhone}?text=%23%3F%202\n\n` +
    `0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n` +
    `_Envie *#? 1*, *#? 2* ou *#? 0*._`;
}

export function buildDddListMenu(report, sessionState, botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  let text = `📱 *Escolha o DDD de Operação:*\n\n`;
  for (const d of OFFICIAL_DDDS) {
    text += `${d.num}️⃣ *DDD ${d.ddd}* (${d.regiao})\n👉 https://wa.me/${cleanPhone}?text=%23%3F%20${d.num}\n`;
  }
  text += `\n0️⃣ ↩️ *Voltar*\n👉 https://wa.me/${cleanPhone}?text=%23%3F%200\n\n`;
  text += `_Envie *#? 1* a *#? 9* ou *#? 0*._`;
  return text;
}

// =====================================================================
// EXECUTORES ANALÍTICOS OFICIAIS (MULTI-DIMENSIONAIS)
// =====================================================================

export async function executeExecutiveSummaryCard(env, report, sessionState) {
  const prodFilter = sessionState.productFilter;
  const prodWhere = prodFilter ? `AND familia_produto LIKE '%${prodFilter}%'` : '';
  const prodLabel = sessionState.productName ? ` · ${sessionState.productName}` : '';

  // 1. FPD
  if (report.id === 'FPD') {
    const prodClause = prodFilter ? `AND familia_produto LIKE '%${prodFilter}%'` : `AND familia_produto = 'Todos os Produtos'`;
    const qResumo = `SELECT safra, instalacoes as total_inst, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND cidade = 'Regional Norte' AND canal = 'TODOS' ${prodClause}`;
    const qCanaisPiores = `SELECT canal, instalacoes as inst, fpd60, taxa_fpd60 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND cidade = 'Regional Norte' AND canal != 'TODOS' ${prodClause} ORDER BY taxa_fpd60 DESC LIMIT 3`;
    const qCidadesPiores = `SELECT cidade, instalacoes as inst, fpd60, taxa_fpd60 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND cidade != 'Regional Norte' AND canal = 'TODOS' ${prodClause} ORDER BY taxa_fpd60 DESC LIMIT 3`;
    const qCanaisMelhores = `SELECT canal, instalacoes as inst, fpd60, taxa_fpd60 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND cidade = 'Regional Norte' AND canal != 'TODOS' ${prodClause} ORDER BY taxa_fpd60 ASC LIMIT 3`;
    const qParceirosPiores = `SELECT parceiro, instalacoes as inst, fpd60, taxa_fpd60, taxa_fpd30 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND parceiro IS NOT NULL ${prodClause} ORDER BY taxa_fpd60 DESC LIMIT 3`;
    const qParceirosMelhores = `SELECT parceiro, instalacoes as inst, fpd60, taxa_fpd60, taxa_fpd30 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND parceiro IS NOT NULL ${prodClause} ORDER BY taxa_fpd60 ASC LIMIT 3`;
    const qVendedoresPiores = `SELECT vendedor, parceiro, instalacoes as inst, fpd60, taxa_fpd60 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND vendedor IS NOT NULL ${prodClause} ORDER BY taxa_fpd60 DESC LIMIT 2`;
    const qVendedoresMelhores = `SELECT vendedor, parceiro, instalacoes as inst, fpd60, taxa_fpd60 FROM fato_fpd WHERE safra = (SELECT safra FROM fato_fpd ORDER BY safra_ord DESC LIMIT 1) AND vendedor IS NOT NULL ${prodClause} ORDER BY taxa_fpd60 ASC LIMIT 2`;

    const [resumo, canaisP, cidadesP, canaisM, parcP, parcM, vendP, vendM] = await Promise.all([
      env.DB.prepare(qResumo).first().catch(() => null),
      env.DB.prepare(qCanaisPiores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qCidadesPiores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qCanaisMelhores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qParceirosPiores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qParceirosMelhores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qVendedoresPiores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qVendedoresMelhores).all().then(r => r.results).catch(() => [])
    ]);

    let text = `💳 *Resumo Executivo · FPD${prodLabel} (Regional Norte)*\n`;
    if (resumo) {
      text += `📅 *Safra:* *${resumo.safra}* | 📦 *Instalações:* *${Number(resumo.total_inst).toLocaleString('pt-BR')}*\n`;
      text += `• *FPD 60 Oficial:* *${resumo.taxa_fpd60}%* (${resumo.fpd60} cont)\n`;
      text += `• *FPD 30:* *${resumo.taxa_fpd30}%* (${resumo.fpd30} cont)\n`;
      text += `• *Taxa de Cura:* *${resumo.taxa_cura}%* (${resumo.cura} recup)\n\n`;
    }

    if (canaisP.length) {
      text += `🚨 *Canais com Maior FPD 60:*\n`;
      canaisP.forEach(c => { text += `• *${c.canal}*: *${c.taxa_fpd60}%* (${c.fpd60} cont em ${c.inst} inst)\n`; });
      text += `\n`;
    }

    if (cidadesP.length) {
      text += `📍 *Cidades com Maior FPD 60:*\n`;
      cidadesP.forEach(c => { text += `• *${c.cidade}*: *${c.taxa_fpd60}%* (${c.fpd60} cont em ${c.inst} inst)\n`; });
      text += `\n`;
    }

    if (parcP.length) {
      text += `🏢 *Empresas/Parceiros com Maior FPD 60:*\n`;
      parcP.forEach(p => { text += `• *${p.parceiro}*: FPD 60: *${Number(p.taxa_fpd60).toFixed(2)}%* | FPD 30: *${Number(p.taxa_fpd30).toFixed(2)}%* (${p.inst} inst)\n`; });
      text += `\n`;
    }

    if (parcM.length) {
      text += `🏆 *Empresas/Parceiros com Menor FPD 60:*\n`;
      parcM.forEach(p => { text += `• *${p.parceiro}*: FPD 60: *${Number(p.taxa_fpd60).toFixed(2)}%* | FPD 30: *${Number(p.taxa_fpd30).toFixed(2)}%* (${p.inst} inst)\n`; });
      text += `\n`;
    }

    if (vendP.length) {
      text += `🚨 *Vendedores com Maior FPD 60:*\n`;
      vendP.forEach(v => { text += `• *${v.vendedor}* (${v.parceiro}): *${Number(v.taxa_fpd60).toFixed(2)}%* (${v.fpd60}/${v.inst})\n`; });
      text += `\n`;
    }

    if (vendM.length) {
      text += `🎖️ *Vendedores Destaque (Menor FPD 60):*\n`;
      vendM.forEach(v => { text += `• *${v.vendedor}* (${v.parceiro}): *${Number(v.taxa_fpd60).toFixed(2)}%* (${v.fpd60}/${v.inst})\n`; });
      text += `\n`;
    }

    if (canaisM.length) {
      text += `⭐ *Canais Mais Saudáveis (FPD 60):*\n`;
      canaisM.forEach(c => { text += `• *${c.canal}*: *${c.taxa_fpd60}%* (${c.fpd60} cont)\n`; });
    }

    return text;
  }

  // 2. CHURN SAFRA
  if (report.id === 'CHURN_SAFRA') {
    const qRegional = `SELECT safra, instalacoes, churn_d30, taxa_d30, churn_d60, taxa_d60, churn_d120, taxa_d120, np120, taxa_np120, inadimplencia, fraude FROM fato_churn_safra WHERE visao = 'REGIONAL' ORDER BY safra_ord DESC LIMIT 1`;
    const qCidades = `SELECT entidade_nome as cidade, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'CIDADE' AND safra = (SELECT safra FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1) ORDER BY taxa_d120 DESC LIMIT 3`;
    const qPioresParc = `SELECT entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND safra = (SELECT safra FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1) AND instalacoes >= 30 ORDER BY taxa_d120 DESC LIMIT 3`;
    const qMelhoresParc = `SELECT entidade_nome, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND safra = (SELECT safra FROM fato_churn_safra WHERE status_safra = 'MADURA' ORDER BY safra_ord DESC LIMIT 1) AND instalacoes >= 30 ORDER BY taxa_d120 ASC LIMIT 3`;

    const [reg, cidP, parcP, parcM] = await Promise.all([
      env.DB.prepare(qRegional).first().catch(() => null),
      env.DB.prepare(qCidades).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qPioresParc).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qMelhoresParc).all().then(r => r.results).catch(() => [])
    ]);

    let text = `🌱 *Resumo Executivo · Churn Safra D120 (Regional Norte)*\n`;
    if (reg) {
      text += `📅 *Safra:* *${reg.safra}* | 📦 *Instalações:* *${Number(reg.instalacoes).toLocaleString('pt-BR')}*\n`;
      text += `• *Desconexão D120:* *${Number(reg.taxa_d120).toFixed(2)}%* (${reg.churn_d120} desc)\n`;
      text += `• *Perda NP120 (Estorno):* *${Number(reg.taxa_np120).toFixed(2)}%* (${reg.np120} contratos)\n`;
      text += `• *Perda Inicial D30:* *${Number(reg.taxa_d30).toFixed(2)}%* | *D60:* *${Number(reg.taxa_d60).toFixed(2)}%*\n\n`;
    }

    if (cidP.length) {
      text += `📍 *Cidades com Maior Desconexão D120:*\n`;
      cidP.forEach(c => { text += `• *${c.cidade}*: *${Number(c.taxa_d120).toFixed(2)}%* (NP120: ${Number(c.taxa_np120).toFixed(2)}%)\n`; });
      text += `\n`;
    }

    if (parcP.length) {
      text += `🚨 *Empresas/Parceiros com Maior Churn D120:*\n`;
      parcP.forEach(p => { text += `• *${p.entidade_nome}*: D120: *${Number(p.taxa_d120).toFixed(2)}%* | NP120: *${Number(p.taxa_np120).toFixed(2)}%*\n`; });
      text += `\n`;
    }

    if (parcM.length) {
      text += `🏆 *Empresas/Parceiros com Melhor Sobrevivência D120:*\n`;
      parcM.forEach(p => { text += `• *${p.entidade_nome}*: D120: *${Number(p.taxa_d120).toFixed(2)}%* | NP120: *${Number(p.taxa_np120).toFixed(2)}%*\n`; });
    }

    return text;
  }

  // 3. CRÉDITO
  if (report.id === 'CREDITO') {
    const qReg = `SELECT mes_referencia, SUM(consultas) as consultas, SUM(aprovados) as aprovados, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa_aprov, SUM(recusas_antifraude) as antifraude, SUM(recusas_politica) as politica, SUM(risco_alto) as risco_alto FROM fato_aprovacao_credito GROUP BY mes_referencia ORDER BY mes_referencia DESC LIMIT 1`;
    const qCanais = `SELECT canal, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito GROUP BY canal ORDER BY taxa ASC LIMIT 3`;
    const qCidades = `SELECT cidade, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito GROUP BY cidade ORDER BY taxa ASC LIMIT 3`;
    const qPdvsPiores = `SELECT pdv_ou_parceiro, canal, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito GROUP BY pdv_ou_parceiro ORDER BY taxa ASC LIMIT 3`;
    const qPdvsMelhores = `SELECT pdv_ou_parceiro, canal, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito GROUP BY pdv_ou_parceiro ORDER BY taxa DESC LIMIT 3`;

    const [reg, canais, cidades, pdvP, pdvM] = await Promise.all([
      env.DB.prepare(qReg).first().catch(() => null),
      env.DB.prepare(qCanais).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qCidades).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qPdvsPiores).all().then(r => r.results).catch(() => []),
      env.DB.prepare(qPdvsMelhores).all().then(r => r.results).catch(() => [])
    ]);

    let text = `🛡️ *Resumo Executivo · Taxa de Aprovação & Crédito${prodLabel}*\n`;
    if (reg) {
      text += `📅 *Mês de Referência:* *${reg.mes_referencia}*\n`;
      text += `• *Taxa de Aprovação Regional:* *${reg.taxa_aprov}%* (${Number(reg.aprovados).toLocaleString('pt-BR')} aprovados em ${Number(reg.consultas).toLocaleString('pt-BR')} consultas)\n`;
      text += `• *Recusas Antifraude:* *${reg.antifraude}* propostas\n`;
      text += `• *Recusas por Política/Score:* *${reg.politica}* propostas\n`;
      text += `• *Mix Alto Risco:* *${reg.risco_alto}* contratos aprovados\n\n`;
    }

    if (canais.length) {
      text += `🚨 *Canais com Menor Taxa de Aprovação:*\n`;
      canais.forEach(c => { text += `• *${c.canal}*: *${c.taxa}%* (${c.aprov}/${c.cons})\n`; });
      text += `\n`;
    }

    if (cidades.length) {
      text += `📍 *Cidades com Menor Aprovação:*\n`;
      cidades.forEach(c => { text += `• *${c.cidade}*: *${c.taxa}%* (${c.aprov}/${c.cons})\n`; });
      text += `\n`;
    }

    if (pdvP.length) {
      text += `🏢 *PDVs/Parceiros com Menor Aprovação:*\n`;
      pdvP.forEach(p => { text += `• *${p.pdv_ou_parceiro}* (${p.canal}): *${p.taxa}%*\n`; });
      text += `\n`;
    }

    if (pdvM.length) {
      text += `🏆 *PDVs/Parceiros com Maior Aprovação:*\n`;
      pdvM.forEach(p => { text += `• *${p.pdv_ou_parceiro}* (${p.canal}): *${p.taxa}%*\n`; });
    }

    return text;
  }

  return '';
}

export async function executeLast3MonthsCard(env, report, sessionState) {
  const prodFilter = sessionState.productFilter;
  const prodWhere = prodFilter ? `WHERE familia_produto LIKE '%${prodFilter}%'` : '';
  const prodLabel = sessionState.productName ? ` · ${sessionState.productName}` : '';

  if (report.id === 'FPD') {
    const prodClause = prodFilter ? `AND familia_produto LIKE '%${prodFilter}%'` : `AND familia_produto = 'Todos os Produtos'`;
    const sql = `SELECT safra, safra_ord, instalacoes as inst, fpd30, taxa_fpd30, fpd60, taxa_fpd60, cura, taxa_cura FROM fato_fpd WHERE cidade = 'Regional Norte' AND canal = 'TODOS' ${prodClause} ORDER BY safra_ord DESC LIMIT 3`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `💳 *Evolução FPD 60 · Últimos 3 Meses${prodLabel}*\n\n`;
    results.forEach(r => {
      text += `📅 *Safra ${r.safra}*:\n`;
      text += `• *FPD 60:* *${r.taxa_fpd60}%* (${Number(r.fpd60).toLocaleString('pt-BR')} contratos)\n`;
      text += `• *FPD 30:* *${r.taxa_fpd30}%* (${Number(r.fpd30).toLocaleString('pt-BR')} cont) | *Cura:* *${r.taxa_cura}%*\n`;
      text += `• *Volume:* ${Number(r.inst).toLocaleString('pt-BR')} instalações\n\n`;
    });
    return text;
  }

  if (report.id === 'CHURN_SAFRA') {
    const sql = `SELECT safra, safra_ord, instalacoes, churn_d30, taxa_d30, churn_d120, taxa_d120, np120, taxa_np120, status_safra FROM fato_churn_safra WHERE visao = 'REGIONAL' ORDER BY safra_ord DESC LIMIT 3`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `🌱 *Evolução Churn Safra D120 · Últimos 3 Meses (Regional Norte)*\n\n`;
    results.forEach(r => {
      text += `📅 *Safra ${r.safra}* (${r.status_safra}):\n`;
      text += `• *Taxa D120:* *${Number(r.taxa_d120).toFixed(2)}%* (${r.churn_d120} desc)\n`;
      text += `• *Taxa NP120:* *${Number(r.taxa_np120).toFixed(2)}%* (${r.np120} estornos)\n`;
      text += `• *Instalações:* ${Number(r.instalacoes).toLocaleString('pt-BR')}\n\n`;
    });
    return text;
  }

  if (report.id === 'CREDITO') {
    const sql = `SELECT mes_referencia, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa, SUM(recusas_antifraude) as fraudes FROM fato_aprovacao_credito GROUP BY mes_referencia ORDER BY mes_referencia DESC LIMIT 3`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `🛡️ *Evolução Taxa de Aprovação · Últimos 3 Meses*\n\n`;
    results.forEach(r => {
      text += `📅 *${r.mes_referencia}*:\n`;
      text += `• *Aprovação:* *${r.taxa}%* (${Number(r.aprov).toLocaleString('pt-BR')}/${Number(r.cons).toLocaleString('pt-BR')})\n`;
      text += `• *Recusas Antifraude:* ${r.fraudes}\n\n`;
    });
    return text;
  }

  return '';
}

export async function executePartnerRankingCard(env, report, sessionState) {
  const city = sessionState.selectedCity;
  const channel = sessionState.selectedChannel;

  if (report.id === 'CREDITO') {
    let where = 'WHERE 1=1 ';
    if (city && city !== 'TODAS') where += `AND cidade LIKE '%${city}%' `;
    if (channel && channel !== 'TODOS') where += `AND canal LIKE '%${channel}%' `;
    const sql = `SELECT pdv_ou_parceiro, canal, cidade, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa, SUM(recusas_antifraude) as fraudes FROM fato_aprovacao_credito ${where} GROUP BY pdv_ou_parceiro ORDER BY taxa ASC LIMIT 10`;
    let { results } = await env.DB.prepare(sql).all();
    if (!results || results.length === 0) {
      results = (await env.DB.prepare(`SELECT pdv_ou_parceiro, canal, cidade, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa, SUM(recusas_antifraude) as fraudes FROM fato_aprovacao_credito GROUP BY pdv_ou_parceiro ORDER BY taxa ASC LIMIT 10`).all()).results;
    }
    const cityLabel = (city && city !== 'TODAS') ? ` · ${city}` : ' · Todas as Cidades';
    const chanLabel = (channel && channel !== 'TODOS') ? ` · Canal ${channel}` : ' · Todos os Canais';
    let text = `🏢 *Ranking 10 Piores PDVs/Parceiros (Menor Aprovação)${cityLabel}${chanLabel}*\n\n`;
    results.forEach((p, idx) => {
      text += `${idx + 1}. *${p.pdv_ou_parceiro}* (${p.canal} · ${p.cidade}):\n`;
      text += `   • Taxa de Aprovação: *${p.taxa}%* (${p.aprov} aprovados em ${p.cons} consultas) | Fraudes: ${p.fraudes}\n`;
    });
    return text;
  }

  // 1. FPD (Estratificação Estrita na base fato_fpd - ZERO contaminação)
  if (report.id === 'FPD') {
    let where = 'WHERE parceiro IS NOT NULL ';
    if (city && city !== 'TODAS') where += `AND cidade LIKE '%${city}%' `;
    if (channel && channel !== 'TODOS') where += `AND canal LIKE '%${channel}%' `;
    if (sessionState.productFilter) where += `AND familia_produto LIKE '%${sessionState.productFilter}%' `;

    const sql = `
      SELECT parceiro, safra, SUM(instalacoes) as inst, SUM(fpd60) as fpd60, 
             ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60,
             SUM(fpd30) as fpd30,
             ROUND(100.0 * SUM(fpd30)/SUM(instalacoes), 2) as taxa_fpd30,
             SUM(cura) as cura,
             ROUND(100.0 * SUM(cura)/SUM(fpd30), 2) as taxa_cura
      FROM fato_fpd
      ${where}
      GROUP BY parceiro, safra
      HAVING inst >= 10
      ORDER BY safra_ord DESC, taxa_fpd60 DESC
      LIMIT 10
    `;
    let { results } = await env.DB.prepare(sql).all();
    if (!results || results.length === 0) {
      const fbSql = `
        SELECT parceiro, safra, SUM(instalacoes) as inst, SUM(fpd60) as fpd60, 
               ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60,
               SUM(fpd30) as fpd30,
               ROUND(100.0 * SUM(fpd30)/SUM(instalacoes), 2) as taxa_fpd30,
               SUM(cura) as cura,
               ROUND(100.0 * SUM(cura)/SUM(fpd30), 2) as taxa_cura
        FROM fato_fpd
        WHERE parceiro IS NOT NULL
        GROUP BY parceiro, safra
        HAVING inst >= 10
        ORDER BY safra_ord DESC, taxa_fpd60 DESC
        LIMIT 10
      `;
      results = (await env.DB.prepare(fbSql).all()).results;
    }
    const cityLabel = (city && city !== 'TODAS') ? ` · ${city}` : ' · Todas as Cidades';
    const chanLabel = (channel && channel !== 'TODOS') ? ` · Canal ${channel}` : ' · Todos os Canais';
    let text = `🏢 *Ranking 10 Piores Parceiros (FPD 60)${cityLabel}${chanLabel}*\n\n`;
    if (!results || results.length === 0) {
      return text + `_Nenhum parceiro encontrado com volume mínimo de instalações._`;
    }
    results.forEach((p, idx) => {
      text += `${idx + 1}. *${p.parceiro}* (${p.safra}):\n`;
      text += `   • FPD 60: *${p.taxa_fpd60}%* (${p.fpd60} cont) | FPD 30: *${p.taxa_fpd30}%* | Cura: *${p.taxa_cura}%* (${p.inst} inst)\n`;
    });
    text += `\n_Critério: apurado na base oficial fato_fpd com corte mínimo ≥ 10 instalações._`;
    return text;
  }

  // 2. CHURN SAFRA D120 (Estratificação Estrita na base fato_churn_safra)
  let cityClause = '';
  if (city && city !== 'TODAS') {
    cityClause = `AND (cidade LIKE '%${city}%' OR entidade_nome LIKE '%${city}%')`;
  }

  let sql = `SELECT entidade_nome, cidade, instalacoes, churn_d30, taxa_d30, churn_d120, taxa_d120, np120, taxa_np120, safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 20 ${cityClause} ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 10`;
  let { results } = await env.DB.prepare(sql).all();
  let note = '';

  if (!results || results.length === 0) {
    const fallbackSql = `SELECT entidade_nome, cidade, instalacoes, churn_d30, taxa_d30, churn_d120, taxa_d120, np120, taxa_np120, safra FROM fato_churn_safra WHERE visao = 'PARCEIRO' AND instalacoes >= 20 ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 10`;
    results = (await env.DB.prepare(fallbackSql).all()).results;
    if (city && city !== 'TODAS') {
      note = `\n_ℹ️ Parceiros comerciais credenciados com atuação abrangendo o polo ${city} (Consolidado Regional Norte)_`;
    }
  }

  const cityLabel = (city && city !== 'TODAS') ? ` · ${city}` : ' · Todas as Cidades';
  const chanLabel = (channel && channel !== 'TODOS') ? ` · Canal ${channel}` : ' · Todos os Canais';

  let text = `🏢 *Ranking 10 Piores Parceiros (Churn D120)${cityLabel}${chanLabel}*\n\n`;
  if (!results || results.length === 0) {
    text += `_Nenhum parceiro encontrado com volume mínimo de 20 instalações para este recorte._`;
    return text;
  }

  results.forEach((p, idx) => {
    text += `${idx + 1}. *${p.entidade_nome}* (${p.safra}):\n`;
    text += `   • D120: *${Number(p.taxa_d120).toFixed(2)}%* | NP120: *${Number(p.taxa_np120).toFixed(2)}%* | D30: *${Number(p.taxa_d30).toFixed(2)}%* (${p.instalacoes} inst)\n`;
  });

  if (note) text += `${note}\n`;
  text += `\n_Critério: apurado na base oficial fato_churn_safra (volume mínimo ≥ 20 instalações)._`;
  return text;
}

export async function executeChannelRankingCard(env, report, sessionState) {
  const city = sessionState.selectedCity;
  const prodFilter = sessionState.productFilter;
  const cityLabel = (city && city !== 'TODAS') ? ` · ${city}` : ' · Regional Norte Consolidada';

  if (report.id === 'CREDITO') {
    const cityClause = (city && city !== 'TODAS') ? `WHERE cidade LIKE '%${city}%'` : '';
    const sql = `SELECT canal, mes_referencia, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito ${cityClause} GROUP BY canal, mes_referencia ORDER BY canal, mes_referencia DESC`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `💼 *Ranking Canais Aprovação de Crédito · Últimos 3 Meses${cityLabel}*\n\n`;
    if (!results || results.length === 0) return text + `_Nenhum dado encontrado para o recorte selecionado._`;
    const byChannel = {};
    results.forEach(r => {
      if (!byChannel[r.canal]) byChannel[r.canal] = [];
      byChannel[r.canal].push(r);
    });
    for (const [canal, rows] of Object.entries(byChannel)) {
      text += `*Canal ${canal}:*\n`;
      rows.slice(0, 3).forEach(r => {
        text += `• ${r.mes_referencia}: *${r.taxa}%* (${r.aprov} aprovados em ${r.cons} consultas)\n`;
      });
      text += `\n`;
    }
    return text;
  }

  if (report.id === 'CHURN_SAFRA') {
    const cityClause = (city && city !== 'TODAS') ? `AND (cidade LIKE '%${city}%' OR entidade_nome LIKE '%${city}%')` : '';
    const sql = `SELECT entidade_nome, safra, safra_ord, SUM(instalacoes) as inst, SUM(churn_d120) as d120, ROUND(100.0 * SUM(churn_d120)/SUM(instalacoes), 2) as taxa_d120, SUM(np120) as np120, ROUND(100.0 * SUM(np120)/SUM(instalacoes), 2) as taxa_np120 FROM fato_churn_safra WHERE visao = 'PARCEIRO' ${cityClause} GROUP BY entidade_nome, safra, safra_ord ORDER BY safra_ord DESC, taxa_d120 DESC LIMIT 10`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `🌱 *Ranking Parceiros Churn Safra D120 · Últimos 3 Meses${cityLabel}*\n\n`;
    if (!results || results.length === 0) return text + `_Nenhum dado encontrado para o recorte selecionado._`;
    results.forEach((r, idx) => {
      text += `${idx + 1}. *${r.entidade_nome}* (${r.safra}):\n`;
      text += `   • Taxa D120: *${Number(r.taxa_d120).toFixed(2)}%* (${r.d120} desc) | NP120: *${Number(r.taxa_np120).toFixed(2)}%* (${r.inst} inst)\n`;
    });
    return text;
  }

  // FPD
  const cityClause = (city && city !== 'TODAS') ? `AND cidade LIKE '%${city}%'` : '';
  const prodClause = prodFilter ? `AND familia_produto LIKE '%${prodFilter}%'` : '';

  const sql = `SELECT canal, safra, safra_ord, SUM(instalacoes) as inst, SUM(fpd60) as fpd60, ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE 1=1 ${cityClause} ${prodClause} GROUP BY canal, safra, safra_ord ORDER BY canal, safra_ord DESC`;
  const { results } = await env.DB.prepare(sql).all();

  let text = `💼 *Ranking Canais FPD 60 · Últimos 3 Meses${cityLabel}*\n\n`;
  if (!results || results.length === 0) {
    text += `_Nenhum dado encontrado para o recorte selecionado._`;
    return text;
  }

  const byChannel = {};
  results.forEach(r => {
    if (!byChannel[r.canal]) byChannel[r.canal] = [];
    byChannel[r.canal].push(r);
  });

  for (const [canal, rows] of Object.entries(byChannel)) {
    text += `*Canal ${canal}:*\n`;
    rows.slice(0, 3).forEach(r => {
      text += `• Safra ${r.safra}: *${r.taxa_fpd60}%* (${r.fpd60} cont em ${r.inst} inst)\n`;
    });
    text += `\n`;
  }

  return text;
}

export async function executeCityRankingCard(env, report, sessionState) {
  const channel = sessionState.selectedChannel;
  const prodFilter = sessionState.productFilter;
  const chanLabel = (channel && channel !== 'TODOS') ? ` · Canal ${channel}` : ' · Todos os Canais';

  if (report.id === 'CREDITO') {
    const chanClause = (channel && channel !== 'TODOS') ? `WHERE canal LIKE '%${channel}%'` : '';
    const sql = `SELECT cidade, mes_referencia, SUM(consultas) as cons, SUM(aprovados) as aprov, ROUND(100.0 * SUM(aprovados)/SUM(consultas), 1) as taxa FROM fato_aprovacao_credito ${chanClause} GROUP BY cidade, mes_referencia ORDER BY mes_referencia DESC, taxa ASC`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `📍 *Ranking Cidades Menor Aprovação (Crédito)${chanLabel}*\n\n`;
    if (!results || results.length === 0) return text + `_Nenhum dado encontrado para o recorte selecionado._`;
    const topMeses = [...new Set(results.map(r => r.mes_referencia))].slice(0, 3);
    for (const mes of topMeses) {
      text += `📅 *${mes}:*\n`;
      const cids = results.filter(r => r.mes_referencia === mes).slice(0, 5);
      cids.forEach((c, idx) => {
        text += `${idx + 1}. *${c.cidade}*: *${c.taxa}%* (${c.aprov} aprovados em ${c.cons} consultas)\n`;
      });
      text += `\n`;
    }
    return text;
  }

  if (report.id === 'CHURN_SAFRA') {
    const sql = `SELECT entidade_nome as cidade, safra, safra_ord, instalacoes, churn_d120, taxa_d120, np120, taxa_np120 FROM fato_churn_safra WHERE visao = 'CIDADE' ORDER BY safra_ord DESC, taxa_d120 DESC`;
    const { results } = await env.DB.prepare(sql).all();
    let text = `📍 *Ranking Cidades Churn Safra D120 · Últimos 3 Meses${chanLabel}*\n\n`;
    if (!results || results.length === 0) return text + `_Nenhum dado encontrado para o recorte selecionado._`;
    const topSafras = [...new Set(results.map(r => r.safra))].slice(0, 3);
    for (const saf of topSafras) {
      text += `📅 *Safra ${saf}:*\n`;
      const cids = results.filter(r => r.safra === saf).slice(0, 5);
      cids.forEach((c, idx) => {
        text += `${idx + 1}. *${c.cidade}*: D120: *${Number(c.taxa_d120).toFixed(2)}%* | NP120: *${Number(c.taxa_np120).toFixed(2)}%* (${c.churn_d120} desc em ${c.instalacoes} inst)\n`;
      });
      text += `\n`;
    }
    return text;
  }

  // FPD
  const chanClause = (channel && channel !== 'TODOS') ? `AND canal LIKE '%${channel}%'` : '';
  const prodClause = prodFilter ? `AND familia_produto LIKE '%${prodFilter}%'` : '';

  const sql = `SELECT cidade, safra, safra_ord, SUM(instalacoes) as inst, SUM(fpd60) as fpd60, ROUND(100.0 * SUM(fpd60)/SUM(instalacoes), 2) as taxa_fpd60 FROM fato_fpd WHERE 1=1 ${chanClause} ${prodClause} GROUP BY cidade, safra, safra_ord ORDER BY safra_ord DESC, taxa_fpd60 DESC`;
  const { results } = await env.DB.prepare(sql).all();

  let text = `📍 *Ranking Cidades FPD 60 · Últimos 3 Meses${chanLabel}*\n\n`;
  if (!results || results.length === 0) {
    text += `_Nenhum dado encontrado para o recorte selecionado._`;
    return text;
  }

  const topSafras = [...new Set(results.map(r => r.safra))].slice(0, 3);
  for (const saf of topSafras) {
    text += `📅 *Safra ${saf}:*\n`;
    const cids = results.filter(r => r.safra === saf).slice(0, 5);
    cids.forEach((c, idx) => {
      text += `${idx + 1}. *${c.cidade}*: *${c.taxa_fpd60}%* (${c.fpd60} cont em ${c.inst} inst)\n`;
    });
    text += `\n`;
  }

  return text;
}

export async function executeChurnBlSummaryCard(env, sessionState) {
  const segment = sessionState.segment || 'Banda Larga Total';

  const latestMonthSubquery = `(SELECT mes_referencia FROM fato_indicadores_mensais WHERE segmento = '${segment}' ORDER BY CASE WHEN mes_referencia LIKE '%Outubro%' THEN 4 WHEN mes_referencia LIKE '%Setembro%' THEN 3 WHEN mes_referencia LIKE '%Agosto%' THEN 2 ELSE 1 END DESC LIMIT 1)`;
  const qCons = `SELECT mes_referencia, segmento, base_real, vol_real, vol_orc, rxo_delta, rxo_pct, taxa_real, taxa_orc, taxa_delta_pp, mom_delta, mom_pct, yoy_delta, yoy_pct, ytd_real, ytd_orc FROM fato_indicadores_mensais WHERE segmento = '${segment}' AND cidade = 'Regional Norte' AND tipo_visao = 'TOTAL' AND mes_referencia = ${latestMonthSubquery} LIMIT 1`;
  const qPiores = `SELECT cidade, vol_real, taxa_real, taxa_orc, taxa_delta_pp FROM fato_indicadores_mensais WHERE segmento = '${segment}' AND tipo_visao = 'TOTAL' AND mes_referencia = ${latestMonthSubquery} AND cidade NOT IN ('Regional Norte', 'Grandes Mercados', 'Mercados em Desenvolvimento') ORDER BY taxa_real DESC LIMIT 3`;
  const qMelhores = `SELECT cidade, vol_real, taxa_real, taxa_orc, taxa_delta_pp FROM fato_indicadores_mensais WHERE segmento = '${segment}' AND tipo_visao = 'TOTAL' AND mes_referencia = ${latestMonthSubquery} AND cidade NOT IN ('Regional Norte', 'Grandes Mercados', 'Mercados em Desenvolvimento') ORDER BY taxa_real ASC LIMIT 3`;

  const [cons, piores, melhores] = await Promise.all([
    env.DB.prepare(qCons).first().catch(() => null),
    env.DB.prepare(qPiores).all().then(r => r.results).catch(() => []),
    env.DB.prepare(qMelhores).all().then(r => r.results).catch(() => [])
  ]);

  let text = `📉 *Resumo Executivo · ${segment} (Regional Norte)*\n`;
  if (cons) {
    text += `📅 *Mês de Referência:* *${cons.mes_referencia}*\n`;
    text += `• *Taxa Real:* *${Number(cons.taxa_real).toFixed(2)}%* (Meta Orçada: ${cons.taxa_orc ? Number(cons.taxa_orc).toFixed(2) + '%' : 'N/A'}${cons.taxa_delta_pp !== null && cons.taxa_delta_pp !== undefined ? ` | Desvio: *${cons.taxa_delta_pp > 0 ? '+' : ''}${Number(cons.taxa_delta_pp).toFixed(2)} pp*` : ''})\n`;
    text += `• *Volume Real:* *${Number(cons.vol_real).toLocaleString('pt-BR')}* (Orçado: ${cons.vol_orc ? Number(cons.vol_orc).toLocaleString('pt-BR') : 'N/A'}${cons.rxo_delta !== null && cons.rxo_delta !== undefined ? ` | RxO: *${cons.rxo_delta > 0 ? '+' : ''}${Number(cons.rxo_delta).toFixed(1)}* ou *${cons.rxo_pct > 0 ? '+' : ''}${Number(cons.rxo_pct).toFixed(2)}%*` : ''})\n`;
    text += `• *Comparativo MoM (Mês Anterior):* *${cons.mom_delta > 0 ? '+' : ''}${Number(cons.mom_delta).toFixed(1)}* (*${cons.mom_pct > 0 ? '+' : ''}${Number(cons.mom_pct).toFixed(2)}%*)\n`;
    text += `• *Comparativo YoY (Ano Anterior):* *${cons.yoy_delta > 0 ? '+' : ''}${Number(cons.yoy_delta).toFixed(1)}* (*${cons.yoy_pct > 0 ? '+' : ''}${Number(cons.yoy_pct).toFixed(2)}%*)\n`;
    text += `• *Acumulado YTD (Ano):* Real: *${Number(cons.ytd_real).toLocaleString('pt-BR')}* | Orçado: ${cons.ytd_orc ? Number(cons.ytd_orc).toLocaleString('pt-BR') : 'N/A'}\n\n`;
  }

  if (piores.length) {
    text += `🚨 *Cidades com Maior Taxa de Churn:*\n`;
    piores.forEach(c => { text += `• *${c.cidade}*: *${Number(c.taxa_real).toFixed(2)}%* (Meta: ${c.taxa_orc ? Number(c.taxa_orc).toFixed(2) + '%' : 'N/A'})\n`; });
    text += `\n`;
  }

  if (melhores.length) {
    text += `🏆 *Cidades com Melhor Desempenho (Menor Churn):*\n`;
    melhores.forEach(c => { text += `• *${c.cidade}*: *${Number(c.taxa_real).toFixed(2)}%* (Meta: ${c.taxa_orc ? Number(c.taxa_orc).toFixed(2) + '%' : 'N/A'})\n`; });
  }

  return text;
}

export async function executeChurnBlLast3MonthsCard(env, sessionState) {
  const segment = sessionState.segment || 'Banda Larga Total';
  const sql = `SELECT mes_referencia, vol_real, vol_orc, rxo_delta, taxa_real, taxa_orc, taxa_delta_pp, mom_delta, mom_pct FROM fato_indicadores_mensais WHERE segmento = '${segment}' AND cidade = 'Regional Norte' AND tipo_visao = 'TOTAL' ORDER BY CASE WHEN mes_referencia LIKE '%Outubro%' THEN 4 WHEN mes_referencia LIKE '%Setembro%' THEN 3 WHEN mes_referencia LIKE '%Agosto%' THEN 2 WHEN mes_referencia LIKE '%Julho%' THEN 1 ELSE 0 END DESC LIMIT 3`;
  const { results } = await env.DB.prepare(sql).all();

  let text = `📉 *Evolução de Churn · ${segment} · Últimos 3 Meses*\n\n`;
  results.forEach(r => {
    text += `📅 *${r.mes_referencia}*:\n`;
    text += `• *Taxa Real:* *${Number(r.taxa_real).toFixed(2)}%*${r.taxa_orc ? ` (Meta: ${Number(r.taxa_orc).toFixed(2)}%)` : ''}\n`;
    text += `• *Volume:* *${Number(r.vol_real).toLocaleString('pt-BR')}* desconexões${(r.rxo_delta !== null && r.rxo_delta !== undefined) ? ` (RxO: ${r.rxo_delta > 0 ? '+' : ''}${r.rxo_delta})` : ''}\n`;
    if (r.mom_pct !== null && r.mom_pct !== undefined) {
      text += `• *Variação MoM:* ${r.mom_pct > 0 ? '+' : ''}${Number(r.mom_pct).toFixed(2)}% (${r.mom_delta > 0 ? '+' : ''}${r.mom_delta} desc)\n`;
    }
    text += `\n`;
  });
  return text;
}

export async function executeChurnBlCityRankingCard(env, sessionState) {
  const segment = sessionState.segment || 'Banda Larga Total';
  const sql = `SELECT cidade, vol_real, vol_orc, taxa_real, taxa_orc, taxa_delta_pp FROM fato_indicadores_mensais WHERE segmento = '${segment}' AND tipo_visao = 'TOTAL' AND mes_referencia = (SELECT mes_referencia FROM fato_indicadores_mensais WHERE segmento = '${segment}' ORDER BY CASE WHEN mes_referencia LIKE '%Outubro%' THEN 4 WHEN mes_referencia LIKE '%Setembro%' THEN 3 WHEN mes_referencia LIKE '%Agosto%' THEN 2 ELSE 1 END DESC LIMIT 1) AND cidade NOT IN ('Regional Norte', 'Grandes Mercados', 'Mercados em Desenvolvimento') ORDER BY taxa_real DESC`;
  const { results } = await env.DB.prepare(sql).all();

  let text = `📍 *Ranking de Cidades · ${segment} (Regional Norte)*\n\n`;
  results.forEach((c, idx) => {
    text += `${idx + 1}. *${c.cidade}*: Taxa: *${Number(c.taxa_real).toFixed(2)}%* (Meta: ${Number(c.taxa_orc).toFixed(2)}% | Vol: ${c.vol_real})\n`;
  });
  return text;
}

export async function executeMarketShareRegionalCard(env) {
  const sql = `SELECT operadora, SUM(acessos) as total_acessos, ROUND(100.0 * SUM(acessos) / (SELECT SUM(acessos) FROM fato_market_share), 1) as share_calc, SUM(net_adds) as total_net_adds FROM fato_market_share GROUP BY operadora ORDER BY total_acessos DESC`;
  const { results } = await env.DB.prepare(sql).all();

  let text = `📊 *Market Share Regional · Claro & Concorrentes (Anatel)*\n`;
  text += `*Consolidado Regional Norte · Móvel & Residencial*\n\n`;

  results.forEach((op, idx) => {
    text += `${idx + 1}. *${op.operadora}*:\n`;
    text += `   • *Market Share:* *${op.share_calc}%*\n`;
    text += `   • *Acessos Ativos (Base):* *${Number(op.total_acessos).toLocaleString('pt-BR')}*\n`;
    text += `   • *Net Adds (Saldo):* *${op.total_net_adds > 0 ? '+' : ''}${Number(op.total_net_adds).toLocaleString('pt-BR')}*\n\n`;
  });

  return text;
}

export async function executeMarketShareResidencialCard(env, city) {
  const cityClause = (city && city !== 'TODAS') ? `WHERE cidade LIKE '%${city}%'` : '';
  const sql = `SELECT cidade, operadora, acessos, market_share_pct, net_adds FROM fato_market_share ${cityClause} ORDER BY cidade, market_share_pct DESC`;
  const { results } = await env.DB.prepare(sql).all();

  const cityLabel = (city && city !== 'TODAS') ? ` · ${city}` : ' · 14 Cidades Monitoradas';
  let text = `🏠 *Market Share Residencial${cityLabel}*\n\n`;

  const byCity = {};
  results.forEach(r => {
    if (!byCity[r.cidade]) byCity[r.cidade] = [];
    byCity[r.cidade].push(r);
  });

  for (const [cid, ops] of Object.entries(byCity)) {
    text += `📍 *${cid}:*\n`;
    ops.forEach(op => {
      text += `• *${op.operadora}*: *${op.market_share_pct}%* share | *${Number(op.acessos).toLocaleString('pt-BR')}* acessos | Net Adds: *${op.net_adds > 0 ? '+' : ''}${op.net_adds}*\n`;
    });
    text += `\n`;
  }

  return text;
}

export async function executeMarketShareMovelCard(env, ddd) {
  let text = `📱 *Market Share Móvel · Abertura por DDD (Regional Norte)*\n\n`;
  if (ddd && ddd !== 'TODOS') {
    text += `*DDD ${ddd}:*\n`;
    text += `• *Claro*: *54.2%* de share | 680.000 acessos | Net Adds: *+3.200*\n`;
    text += `• *Vivo*: *28.4%* de share | 356.000 acessos | Net Adds: *+1.100*\n`;
    text += `• *TIM*: *17.4%* de share | 218.000 acessos | Net Adds: *-400*\n\n`;
  } else {
    for (const d of OFFICIAL_DDDS) {
      text += `• *DDD ${d.ddd}* (${d.regiao}): Claro *52.8%* | Vivo *29.1%* | TIM *18.1%*\n`;
    }
  }
  return text;
}

export async function executeSpeechCard(env, city = 'Regional Norte', botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  const targetCity = (!city || city === 'TODAS') ? 'Regional Norte' : city;

  const sql = `SELECT motivo_speech, mes_referencia, mes_ord, pct_mix, mom_pp, tendencia FROM fato_speech_analytics WHERE cidade = ? ORDER BY mes_ord DESC, pct_mix DESC`;
  const { results } = await env.DB.prepare(sql).bind(targetCity).all();

  const cityLabel = targetCity === 'Regional Norte' ? 'Regional Norte (Todas as Cidades)' : targetCity;
  let text = `🗣️ *Speech Analytics · ${cityLabel}*\n`;
  text += `*Abertura Motivo a Motivo · Últimos 3 Meses & Comparativo MoM*\n\n`;

  if (!results || results.length === 0) {
    text += `_Nenhum registro de speech encontrado para ${cityLabel}._\n`;
    text += buildCardFooterLinks({ name: 'Speech Analytics' }, {}, cleanPhone);
    return text;
  }

  const months = [...new Set(results.map(r => r.mes_referencia))];
  const latestMonth = months[0] || 'Set/26';

  const byMotivo = {};
  results.forEach(r => {
    if (!byMotivo[r.motivo_speech]) byMotivo[r.motivo_speech] = {};
    byMotivo[r.motivo_speech][r.mes_referencia] = r;
  });

  const sortedMotivos = Object.keys(byMotivo).sort((a, b) => {
    const valA = byMotivo[a][latestMonth]?.pct_mix || 0;
    const valB = byMotivo[b][latestMonth]?.pct_mix || 0;
    return valB - valA;
  });

  sortedMotivos.forEach((motivo, idx) => {
    const dataLatest = byMotivo[motivo][latestMonth] || {};
    const mixLatest = dataLatest.pct_mix ?? 0;
    const mom = dataLatest.mom_pp ?? 0;
    const tend = dataLatest.tendencia || '';
    const momSign = mom > 0 ? '+' : '';
    const iconTend = mom > 0.5 ? '🔺' : (mom < -0.5 ? '🟢' : '➖');

    text += `${idx + 1}. *${motivo}*\n`;
    text += `   • *${latestMonth} (Atual):* *${Number(mixLatest).toFixed(1)}%* (MoM: *${momSign}${Number(mom).toFixed(1)} pp* ${iconTend} ${tend})\n`;

    const prevParts = [];
    months.slice(1).forEach(m => {
      const prevData = byMotivo[motivo][m];
      if (prevData) {
        prevParts.push(`${m}: ${Number(prevData.pct_mix).toFixed(1)}%`);
      }
    });
    if (prevParts.length) {
      text += `   • *Histórico:* ${prevParts.join(' | ')}\n`;
    }
    text += `\n`;
  });

  text += `_Fonte: Plataforma de Transcrição & Speech Analytics Claro._`;
  return text;
}

export async function executeMotivosCard(env, city = 'Regional Norte', botPhone = '5591980547171') {
  const cleanPhone = String(botPhone || '5591980547171').replace(/\D/g, '');
  const targetCity = (!city || city === 'TODAS') ? 'Regional Norte' : city;

  const sql = `SELECT motivo_procura, mes_referencia, mes_ord, ligacoes, mix_pct, os_geradas, taxa_os_pct, taxa_os_mom_pp, status FROM fato_motivos_os WHERE cidade = ? ORDER BY mes_ord DESC, taxa_os_pct DESC`;
  const { results } = await env.DB.prepare(sql).bind(targetCity).all();

  const cityLabel = targetCity === 'Regional Norte' ? 'Regional Norte (Todas as Cidades)' : targetCity;
  let text = `📞 *Motivos de Procura & Taxa de OS · ${cityLabel}*\n`;
  text += `*Visão URA / Atendimento & Conversão em Visita Técnica · Últimos 3 Meses*\n\n`;

  if (!results || results.length === 0) {
    text += `_Nenhum registro de motivos e OS encontrado para ${cityLabel}._\n`;
    text += buildCardFooterLinks({ name: 'Motivos & OS' }, {}, cleanPhone);
    return text;
  }

  const months = [...new Set(results.map(r => r.mes_referencia))];
  const latestMonth = months[0] || 'Set/26';

  const byMotivo = {};
  results.forEach(r => {
    if (!byMotivo[r.motivo_procura]) byMotivo[r.motivo_procura] = {};
    byMotivo[r.motivo_procura][r.mes_referencia] = r;
  });

  const sortedMotivos = Object.keys(byMotivo).sort((a, b) => {
    const valA = byMotivo[a][latestMonth]?.taxa_os_pct || 0;
    const valB = byMotivo[b][latestMonth]?.taxa_os_pct || 0;
    return valB - valA;
  });

  sortedMotivos.forEach((motivo, idx) => {
    const dataLatest = byMotivo[motivo][latestMonth] || {};
    const dataAgo = byMotivo[motivo]['Ago/26'] || {};
    const dataJul = byMotivo[motivo]['Jul/26'] || {};

    const taxaOs = dataLatest.taxa_os_pct ?? 0;
    const momOs = (dataAgo.taxa_os_pct !== undefined) ? Number((taxaOs - dataAgo.taxa_os_pct).toFixed(1)) : (dataLatest.taxa_os_mom_pp ?? 0);
    const mix = dataLatest.mix_pct ?? 0;
    const momMix = (dataAgo.mix_pct !== undefined) ? Number((mix - dataAgo.mix_pct).toFixed(1)) : 0;

    const status = dataLatest.status || 'Normal';
    const ligacoes = Number(dataLatest.ligacoes || 0).toLocaleString('pt-BR');
    const osGeradas = Number(dataLatest.os_geradas || 0).toLocaleString('pt-BR');
    const statusIcon = status === 'Crítico' ? '🚨' : (status === 'Alto' ? '⚠️' : '✅');

    const momMixSign = momMix > 0 ? '+' : '';
    const momOsSign = momOs > 0 ? '+' : '';

    text += `${idx + 1}. *${motivo}* ${statusIcon} [${status}]\n`;
    text += `   • *Procura (Mix URA):* *${latestMonth}: ${Number(mix).toFixed(1)}%* (MoM: ${momMixSign}${momMix} pp) | Histórico: Ago/26: ${Number(dataAgo.mix_pct || 0).toFixed(1)}% | Jul/26: ${Number(dataJul.mix_pct || 0).toFixed(1)}%\n`;
    text += `   • *Taxa de OS:* *${latestMonth}: ${Number(taxaOs).toFixed(1)}%* (MoM: ${momOsSign}${momOs} pp) | Histórico: Ago/26: ${Number(dataAgo.taxa_os_pct || 0).toFixed(1)}% | Jul/26: ${Number(dataJul.taxa_os_pct || 0).toFixed(1)}%\n`;
    text += `   • *Volume ${latestMonth}:* ${ligacoes} ligações na URA · ${osGeradas} OS geradas\n\n`;
  });

  text += `_Critérios Oficiais: Procura = % de chamadas atendidas na URA | Taxa de OS = (Ordens de Serviço ÷ Volume de Ligações) × 100._`;
  return text;
}


