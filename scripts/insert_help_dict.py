"""Script para inserir dicionario HELP no painel FPD"""

HELP_JS = """const HELP = {
  filtros: [
    'Gaveta de Filtros',
    '<p>Use os filtros para selecionar quais dados aparecem em todos os paineis simultaneamente.</p>' +
    '<p><strong>Como usar:</strong> Clique em qualquer item (UF, Safra, Canal, Produto) para ativa-lo. Os paineis atualizam instantaneamente.</p>' +
    '<p><strong>Botao T:</strong> Seleciona todos os itens visiveis da dimensao.</p>' +
    '<p><strong>Botao x:</strong> Limpa a selecao daquele filtro.</p>' +
    '<p><strong>Campo de busca:</strong> Digite para encontrar rapidamente UFs, cidades ou safras.</p>'
  ],
  kpis: [
    'Indicadores de FPD',
    '<p><strong>FPD 60 Oficial:</strong> Porcentagem de clientes que nao pagaram a 1a fatura em ate 60 dias. Indicador oficial Claro de inadimplencia inicial.</p>' +
    '<p><strong>FPD 30 Onboarding:</strong> Versao antecipada medida em 30 dias. Indica tendencia antes do fechamento oficial.</p>' +
    '<p><strong>Contratos Ativos:</strong> Total de instalacoes dentro da selecao de filtros aplicada.</p>' +
    '<p><em>Apenas safras fechadas (com maturacao completa de 60 dias) sao exibidas.</em></p>'
  ],
  safra: [
    'Evolucao do FPD Safra a Safra',
    '<p>Historico das ultimas 13 safras, comparando FPD 60 Oficial com FPD 30 Onboarding.</p>' +
    '<p><strong>Safra:</strong> Mes de instalacao do contrato. Ex: Jan/25 = clientes instalados em janeiro de 2025.</p>' +
    '<p><strong>Linha solida:</strong> Safras fechadas — dados consolidados e confiaveis.</p>' +
    '<p><strong>Linha tracejada:</strong> Safra em andamento — ainda em maturacao, pode mudar.</p>' +
    '<p><em>Clique em um ponto do grafico para filtrar o painel inteiro por aquela safra.</em></p>'
  ],
  scatter: [
    'Dispersao MoM & YoY',
    '<p>Grafico que posiciona cada dimensao (UF, cidade, canal) pela combinacao de taxa de FPD e volume.</p>' +
    '<p><strong>MoM (Month over Month):</strong> Variacao em relacao ao mes anterior.</p>' +
    '<p><strong>YoY (Year over Year):</strong> Variacao em relacao ao mesmo periodo do ano passado.</p>' +
    '<p><strong>Quadrante superior esquerdo:</strong> Alto FPD, baixo volume — risco prioritario.</p>' +
    '<p><em>Passe o mouse sobre os pontos para ver os detalhes de cada praca ou canal.</em></p>'
  ],
  mapa: [
    'Mapa de Concentracao Geografica',
    '<p>Visualiza a distribuicao geografica dos contratos e das taxas de FPD nas pracas da Regional Norte.</p>' +
    '<p><strong>Intensidade da cor:</strong> Quanto mais escuro, maior a taxa de FPD naquela localidade.</p>' +
    '<p><strong>Tamanho do marcador:</strong> Proporcional ao volume de contratos.</p>' +
    '<p><strong>Ferramenta lasso:</strong> Desenhe uma area no mapa para filtrar apenas aquela regiao.</p>' +
    '<p><strong>Modos de visualizacao:</strong> Alterne entre Celulas, Pontos e Calor nos botoes acima do mapa.</p>'
  ],
  cidades: [
    'Visao por Cidades (IBGE)',
    '<p>Tabela com o desempenho de FPD em cada uma das 13 pracas da Regional Norte, seguindo codificacao IBGE.</p>' +
    '<p><strong>FPD 60:</strong> Taxa de inadimplencia de primeira fatura em 60 dias.</p>' +
    '<p><strong>FPD 30:</strong> Indicador antecipado de onboarding.</p>' +
    '<p><strong>Vol.:</strong> Volume de contratos na praca no periodo selecionado.</p>' +
    '<p><em>Clique no cabecalho para reordenar. Use o botao de export para baixar em CSV.</em></p>'
  ],
  risco: [
    'Qualidade de Venda & Perfil de Credito',
    '<p>Analisa a composicao do FPD sob a otica do risco de credito no momento da venda.</p>' +
    '<p><strong>FX_RISCO_NV:</strong> Faixa de risco atribuida pelo sistema Claro na instalacao. Valores: Baixo, Medio, Alto, Muito Alto.</p>' +
    '<p><strong>FXULTSCORE:</strong> Faixa de score de credito (bureaux). Quanto mais alta, melhor o historico.</p>' +
    '<p><em>Use esta visao para entender se o FPD e concentrado em risco alto (problema de venda) ou afeta todos os perfis (problema operacional).</em></p>'
  ],
  matriz: [
    'Matriz de Safra FPD',
    '<p>Tabela de maturacao: para cada safra, mostra como o FPD evoluiu mes a mes apos a instalacao.</p>' +
    '<p><strong>Linhas:</strong> Cada safra de instalacao (mes de ativacao).</p>' +
    '<p><strong>Colunas:</strong> Meses apos a instalacao (Mes 1, Mes 2... ate o mes atual).</p>' +
    '<p><strong>Marco FPD 60 Oficial:</strong> Linha divisoria entre meses pre e pos fechamento oficial.</p>' +
    '<p><strong>Cor da celula:</strong> Verde = baixo FPD; Ambar = atencao; Vermelho = FPD elevado.</p>'
  ],
  ranking: [
    'Ranking por Dimensao',
    '<p>Classifica os itens de cada dimensao analitica (UF, Cidade, Canal, Produto, Risco) pelo FPD.</p>' +
    '<p><strong>Como usar as abas:</strong> Selecione a dimensao desejada nas abas acima da tabela.</p>' +
    '<p><strong>Ordenar:</strong> Clique em qualquer cabecalho de coluna para reordenar crescente/decrescente.</p>' +
    '<p><em>Clique em qualquer linha para filtrar o painel inteiro por aquele item. Exporte para CSV no botao de download.</em></p>'
  ],
  upload: [
    'Atualizacao da Base de Dados',
    '<p>Area restrita ao responsavel pelo painel para carregar nova versao da base de dados FPD.</p>' +
    '<p><strong>Formato aceito:</strong> Arquivo CSV gerado pelo script oficial build_fpd_definitive.py.</p>' +
    '<p><strong>Processo:</strong> O arquivo e comprimido automaticamente e integrado ao painel, sem republcacao.</p>' +
    '<p><strong>Atencao:</strong> Certifique-se de que o arquivo cobre o periodo completo antes de publicar. Substitui a base anterior.</p>'
  ],
  metodo: [
    'Notas Metodologicas FPD',
    '<p><strong>FPD 60 Oficial Claro:</strong> Contrato sem nenhum pagamento efetivo nos primeiros 60 dias corridos apos o vencimento da 1a fatura.</p>' +
    '<p><strong>Safra de referencia:</strong> Mes civil de instalacao/ativacao do contrato.</p>' +
    '<p><strong>Maturacao minima:</strong> Safra so e "fechada" quando todos os contratos ultrapassaram 60 dias de avaliacao.</p>' +
    '<p><strong>FX_RISCO_NV:</strong> Atribuido no momento da instalacao pelo motor de credito Claro. Nao se altera apos a venda.</p>' +
    '<p><strong>FXULTSCORE:</strong> Ultima pontuacao de credito disponivel no momento da consulta pre-venda (bureaux).</p>'
  ]
};
"""

TARGET = 'function openHelp(k){ const h=HELP[k]; if(!h)return;'
FILES = [
    'public/fpd/index.html',
    'public/churn/index.html',
    'public/churn-bl-total/index.html',
    'public/churn-bl-pme/index.html',
]

for path in FILES:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'const HELP' in content:
            print(f'SKIP {path}: HELP ja declarado.')
            continue
        if TARGET not in content:
            print(f'SKIP {path}: openHelp nao encontrado.')
            continue
        content = content.replace(TARGET, HELP_JS + TARGET, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK {path}: HELP inserido.')
    except Exception as e:
        print(f'ERRO {path}: {e}')
