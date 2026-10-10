# Contexto Consolidado do Projeto: Churn Safra e Painel FPD (Regional Norte)

> **Documento para inicialização de nova conversa no agente.**  
> Este documento resume todos os alinhamentos de negócio, definições metodológicas, correções técnicas recentes e o estado atual dos painéis.

---

## 1. Visão Geral dos Projetos e Relatórios

O ambiente é composto por relatórios executivos de inteligência analítica desenvolvidos para o portal **PEP HUB** da Diretoria e Operação da **Regional Norte (Claro)**.

Existem dois produtos analíticos principais que compartilham a mesma mecânica de frontend de alto desempenho (Canvas Mercator, decodificação zlib em memória no navegador, laço livre espacial, tabelas ordenáveis e filtros dinâmicos cruzados):

| Dimensão | Churn Safra (Painel 28) | Painel FPD (First Payment Default) |
| :--- | :--- | :--- |
| **Objetivo Principal** | Desconexões e cancelamentos definitivos de contratos | Qualidade de venda e adimplência da 1ª fatura de instalação |
| **Janela de Apuração** | 120 dias (responsabilidade de canal/parceiro) até 150d+ | 60 dias (1ª fatura de ciclo cheio / FPD 60 oficial) e 30 dias (pró-rata) |
| **Delay de Envio** | Relatório com safras abertas e fechadas ao longo de 13 meses | **Já enviado com delay oficial corporativo** (todas as safras presentes são maduras) |
| **Universo de Análise** | Assinatura e Domicílio (abre em Assinatura para evitar duplicidade) | **100% Domicílio** (segmentado por famílias de produto: Dados, Vídeo, etc.) |
| **Safra Foco Padrão** | Safra fechada de 110–120 dias atrás | **Sempre a última safra do período disponível** (ex: `mai/26`) |
| **Base de Dados Fonte** | Base consolidada Churn Safra (348.866 registros) | `FPD_JAN_MAI_26.csv` (53.972 instalações domiciliares) |

---

## 2. Alinhamentos Críticos Realizados na Rodada Atual (FPD)

### Item 1: Remoção de Aging 90 para Frente
- **Fato verificado na base**: Na base de FPD (`FPD_JAN_MAI_26.csv`), as colunas `AGING90`, `AGING120`, `AGING150` e `OVER90` estão **100% zeradas** (0 contratos).
- **Ação realizada**:
  - Removido o card FPD 90 dos KPIs.
  - Removida a curva pc90 e tooltips de 90d do gráfico de safras (`drawSafra`).
  - Removidas colunas de 90d, 120d e 150d das tabelas de Cidades IBGE (`drawCid`), Esteira (`drawEsteira`) e Ranking (`drawRank`).
  - Removidas as opções `c90`, `c120` e `c150` do seletor de métrica do mapa geográfico.
  - O foco visual e analítico foi centralizado em: **FPD 60 (Oficial)**, **FPD 30 (Pré-FPD / Pró-rata)** e **Taxa de Adimplência (Em dia)**.

### Item 2: Safra Foco e Delay de Envio
- **Conceito de Negócio**: O FPD não usa lógica de safras parciais ou 120 dias de atraso de maturação. O indicador já é enviado pela área corporativa com o delay necessário para consolidação dos pagamentos das primeiras faturas.
- **Implementação**:
  - Todas as safras presentes (`jan/26` a `mai/26`) são tratadas como **fechadas e consolidadas** (`isParcial = false`, `maturoR = true`, `ABERTAS = new Set()`).
  - A função `defaultAnchor()` seleciona **sempre a safra mais recente do período (`mai/26`)** por padrão.
  - O painel calcula automaticamente o **MoM (Mês sobre Mês)** de `mai/26` em relação a `abr/26` (variação de p.p. na taxa e % de volume instalado).
  - O seletor de "Status da safra" (fechadas vs abertas) foi ocultado por não se aplicar ao FPD.

### Item 3: Visão 100% Domicílio e Correção da Coluna Node
- **Visão Domicílio**: Na base de FPD, 100% dos registros possuem `NM_VISAO_ANALISE = 'Domicílio'`. Foi removido qualquer filtro forçado ou resquício de `Assinatura`.
- **Filtro de Produto**: O filtro `produto` foi mapeado para a família de produtos do domicílio (`NM_TIPO_ASS_DOMICILIO`), permitindo abrir o painel com todos os produtos e filtrar por `Dados`, `Vídeo + Dados`, `Vídeo`, `Dados + Voz` e `Vídeo + Dados + Voz`.
- **Correção da Coluna Node**: No arquivo de geocódigo (`Base_Churn_Geocod_v3_FALLBACK_CEP.csv`), o cabeçalho oficial é `CD_NODE` (índice 13), e não `NODE`. Corrigido o indexador, resultando em **53.971 contratos com Node identificado (100.0% de match)** e **6.914 nodes reais mapeados** (ex: `BLM041`, `MA448`, `JPMABB`, etc.).

### Item 4: Associação Metodológica de "Nunca Pagou" e "Pró-rata"
- **Origem dos Dados**: A associação foi feita **100% com as colunas nativas do arquivo FPD**, sem cruzamento com o Churn Safra.
- **Regra Analítica**:
  - **Nunca Pagou (FPD 60 Efetivo)**: `AGING30 == 1 AND AGING60 == 1`  
    Clientes que atrasaram a fatura proporcional e continuaram inadimplentes na fatura cheia (0 pagamentos efetuados após 60 dias). **13.979 contratos (25,90% da base)**.
  - **Atraso Pró-rata (Curado / Regularizado)**: `AGING30 == 1 AND AGING60 == 0`  
    Clientes que atrasaram a fatura inicial de 30 dias (onboarding / pró-rata de instalação), mas regularizaram o pagamento antes dos 60 dias e não entraram no FPD 60 Oficial Claro. **17.467 contratos (32,36% da base total, o que representa uma cura de 55,5% dos atrasos de 30d)**.
  - **100% Adimplente em Dia**: `AGING30 == 0 AND AGING60 == 0`  
    Clientes que pagaram rigorosamente em dia tanto o pró-rata quanto o ciclo cheio. **22.526 contratos (41,74% da base)**.

### Item 5: Visão de Produto na Última Tabela (`tblRank`)
- Adicionada a aba **"Produto (Família Domicílio)"** como 2ª dimensão de quebra em destaque logo ao lado de "Parceiro Comercial":
  ```
  [ Parceiro Comercial ]  [ Produto (Família Domicílio) ]  [ Vendedor ]  [ Cidade ]  ...
  ```
- Exibe métricas consolidadas por família de domicílio:
  - `Dados`: 44.794 inst | 23,61% FPD 60 | 57,21% FPD 30 | 76,39% Em Dia | 10.537 Nunca Pagou
  - `Vídeo + Dados`: 4.346 inst | 39,07% FPD 60 | 63,85% FPD 30 | 60,93% Em Dia | 1.686 Nunca Pagou
  - `Vídeo`: 4.205 inst | 36,72% FPD 60 | 64,57% FPD 30 | 63,28% Em Dia | 1.542 Nunca Pagou
  - `Dados + Voz`: 456 inst | 25,44% FPD 60 | 50,88% FPD 30 | 74,56% Em Dia | 115 Nunca Pagou
  - `Vídeo + Dados + Voz`: 137 inst | 27,01% FPD 60 | 59,85% FPD 30 | 72,99% Em Dia | 37 Nunca Pagou

---

## 3. Correções Técnicas dos Problemas de Abertura ("Fica descompactando e não sai")

Dois problemas em cadeia no JavaScript impediam a inicialização da aplicação:

1. **SyntaxError de Aspas no Seletor de Safra**:
   - *Causa*: Na injeção do HTML do seletor `fSafra`, havia a string `font:12px \'Segoe UI\',Arial`. Durante a geração pelo Python, a barra de escape foi consumida e o arquivo final recebeu `'Segoe UI'` sem escape dentro de uma string JavaScript com aspas simples, gerando `SyntaxError: Unexpected identifier 'Segoe'`.
   - *Solução*: A declaração de fonte foi padronizada para `font:12px sans-serif`.

2. **Supressão das Variáveis Globais de Estado (`sel`, `IDX`, `buildIndex`) e Escopo de `SAFRA_DISP`**:
   - *Causa*: O regex de substituição matemática da função `addRow` utilizava como delimitador final `(?=function aggTot)`. Como no código original as declarações globais de filtro (`const sel={}`, `let IDX=...`, `function buildIndex` e `function aggBy`) estavam localizadas entre `addRow` e `aggTot`, elas foram inadvertidamente apagadas, gerando `ReferenceError: sel is not defined` no momento em que `init()` chamava `readFiltersFromUI()`. Além disso, a variável `SAFRA_DISP` precisava ser declarada no topo para evitar Temporal Dead Zone durante a resolução assíncrona do `boot()`.
   - *Solução*: O delimitador do regex foi ajustado para `(?=function mrg)`, preservando integralmente `sel`, `IDX`, `buildIndex` e `aggBy`, e `var SAFRA_DISP=[];` foi devidamente içada no topo das variáveis globais.

- **Validação Automatizada de Ponta a Ponta**:  
  Criamos o script `scripts/test_runtime_error.js`, que simula integralmente o ciclo de vida do navegador: decodificação das 38 colunas comprimidas com zlib, execução do `boot()`, `init()`, `buildIndex()`, `readFiltersFromUI()` e `render_()` (desenhando KPIs, gráficos SVG, tabelas e canvas do mapa). O teste confirmou execução 100% limpa e sem nenhum erro (`TESTE FINALIZADO: NENHUM ERRO ENCONTRADO!`).

---

## 4. Arquivos Mestre e Estrutura do Repositório

- **Painel FPD na Raiz**: `Painel_FPD_Regional_Norte.html`
- **Rotas Públicas FPD**: `public/fpd/index.html` e `public/fpd/Painel_FPD_Regional_Norte.html`
- **Script Gerador Mestre**: `scripts/build_fpd_refined_painel.py`
- **Scripts de Verificação**:
  - `scripts/verify_fpd_refined.js` (valida os requisitos de dados e decodificação)
  - `scripts/test_syntax_exec.js` (valida sintaxe do JS gerado)
  - `scripts/test_runtime_error.js` (valida execução limpa de runtime no ciclo de vida DOM)
- **Base de Dados FPD**: `FPD_JAN_MAI_26.csv`
- **Base de Geocódigo e Nodes**: `Base_Churn_Geocod_v3_FALLBACK_CEP.csv`
- **Painel Churn Safra de Referência**: `Painel_Churn_Safra 28.html`

---

## 5. Rodada 2: Refinamentos Estratégicos e Técnicos do Painel FPD (6 Itens Atendidos)

### Item 1: Gráfico de Dispersão MoM & YoY (Substituição da Curva de Maturação)
- **Substituição Conceitual**: Como o FPD não tem curvas de maturação ao longo de 120/150 dias, o espaço foi ocupado pelo componente analítico executivo **"Dispersão MoM & YoY evolução da taxa FPD 60 vs volume"**.
- **Mecânica Interativa**:
  - Alternância de Comparação:
    - `MoM (vs Safra Anterior)`: compara a safra foco (`mai/26`) com o mês imediatamente anterior (`abr/26`).
    - `vs Jan/26 (Início Série)`: compara o comportamento atual vs o benchmark inicial da série histórica consolidada (YoY / YTD).
  - Alternância de 5 Dimensões Analíticas com 1 clique:
    1. `Cidade` (Belém, Manaus, São Luís, Imperatriz, etc.)
    2. `Canal` (Porta a Porta, Receptivo, Lojas Próprias, Canais Eletrônicos, etc.)
    3. `Produto` (Famílias Domicílio: Dados, Vídeo + Dados, etc.)
    4. `Empresa` (Parceiros comerciais / credenciados)
    5. `Vendedor` (Top consultores da Regional)
  - **Eixos e Elementos Visuais**:
    - Eixo X: Taxa FPD 60 Oficial atual (em %).
    - Eixo Y: Variação $\Delta$ em pontos percentuais (p.p.), com linha horizontal em `0,0 p.p.` e legendas explicativas `↑ Piora` / `↓ Melhora`.
    - Bolhas dimensionadas proporcionalmente ao volume de instalações da entidade.
    - Cores inteligentes: Verde para redução de taxa (ganho de qualidade) e Vermelho para elevação de taxa (alerta de risco).

### Item 2: Remoção Definitiva da Visão de Matriz de Safra
- A matriz triangular de safra foi eliminada tanto do layout visual (HTML) quanto da lógica JavaScript (`drawMtx` e listeners órfãos em `init()`), despoluindo o painel e eliminando conceitos que pertenciam exclusivamente ao churn clássico.

### Item 3: Visão de Risco com `FX_RISCO_NV`
- Mapeada a coluna oficial de risco `FX_RISCO_NV` (coluna 146 do CSV original) e integrada como seção visual prioritária: **"Qualidade de Venda & Perfil de Crédito"**.
- Gráficos horizontais e tabela de composição exibindo as 7 faixas oficiais:
  - `Baixissimo`: 328 inst (3,4%) · FPD 60 de **6,4%**
  - `Baixo`: 918 inst (9,4%) · FPD 60 de **8,9%**
  - `Medio`: 3.550 inst (36,4%) · FPD 60 de **17,0%**
  - `Alto`: 1.984 inst (20,3%) · FPD 60 de **30,1%**
  - `Altissimo1`: 464 inst (4,8%) · FPD 60 de **48,1%**
  - `Altissimo2`: 2.417 inst (24,8%) · FPD 60 de **42,2%**
  - `SCORE 0 e 1`: 101 inst (1,0%) · FPD 60 de **39,6%**

### Item 4: Visão de Score por Faixas Numéricas (`FXULTSCORE`)
- Mapeada a coluna `FXULTSCORE` (coluna 114) com botão de alternância imediata na mesma seção de risco.
- Permite avaliar a elasticidade da inadimplência por faixas de score de crédito:
  - `551--600`: 3.548 inst (36,3%) · FPD 60 de 23,2%
  - `501--550`: 2.941 inst (30,1%) · FPD 60 de 42,1%
  - `601--650`: 1.948 inst (20,0%) · FPD 60 de 12,6%
  - `651--700`: 681 inst (7,0%) · FPD 60 de 9,0%
  - `451--500`: 246 inst (2,5%) · FPD 60 de 54,1%
  - `701--750`: 210 inst (2,2%) · FPD 60 de 10,5%
  - `751--800` a `951--1000`: taxas residuais inferiores a 5%.

### Item 5: Filtro e Dimensão de `PORTFOLIO_TV`
- Adicionado seletor com busca e multiseleção na gaveta de filtros (`fDrawer` / `DIMDEF`) para a coluna `PORTFOLIO_TV`:
  - `SEM TV`: 45.250 contratos (83,9% da base)
  - `TV BOX`: 8.085 contratos (15,0% da base)
  - `TV TRADICIONAL`: 637 contratos (1,2% da base)
- Integrado também como dimensão oficial no ranking de concentrações (`RANKDIMS`), permitindo contrastar o FPD de ofertas com e sem conteúdo de vídeo.

### Item 6: Diagnóstico e Resolução do Agrupamento Excessivo de Coordenadas
- **Causa Raiz Identificada**:
  1. *Fallback Estático Único*: No código herdado, 10.245 contratos (19,0% da base) que não encontravam correspondência direta na tabela de geocódigo eram jogados para a coordenada estática de Manaus (`-3.1190, -60.0217`), acumulando contratos de Belém, São Luís, Parauapebas, etc. em um único ponto no centro da capital amazonense.
  2. *Centroides Idênticos de CEP*: No arquivo `Base_Churn_Geocod_v3_FALLBACK_CEP.csv`, múltiplos contratos cadastrados no mesmo CEP compartilhavam rigorosamente a mesma latitude e longitude até a 6ª casa decimal (ex: 169 contratos num único ponto em Parauapebas).
- **Tratamento e Qualificação Implementados**:
  1. *Centroides Urbanos por Município*: Mapeadas as coordenadas centrais oficiais das 13 principais cidades da Regional Norte (Belém, Manaus, São Luís, Macapá, Ananindeua, Marabá, Imperatriz, Parauapebas, Castanhal, Timon, Caxias, Santana, Paragominas). Quando um contrato não possui geocódigo fino, ele é associado ao centróide urbano da **sua própria cidade**.
  2. *Dispersão Polar Determinística (Pseudo-Jitter)*: Aplicado um deslocamento radial pseudo-aleatório baseado no hash do número do contrato:
     - Para contratos com CEP georreferenciado: dispersão de ~25 a 40 metros, permitindo visualizar a densidade real sem sobreposição estrita de marcadores no mesmo pixel.
     - Para contratos em fallback de cidade: dispersão urbana realista de 800m a 2.500m dentro da mancha urbana do município correspondente.
  - *Resultado*: 100% dos contratos geolocalizados nas suas cidades reais, eliminando completamente a anomalia de aglomeração artificial.

---

## 4. Alinhamentos da Rodada 3 (Base FPD JUN25–JUN26, Matriz com Marco FPD 60, Helpers, WhatsApp Auth e Agente Auditor)

### Item 1: Diagnóstico e Tratamento da Nova Base (`BASE_FPD_JUN25_JUN26.csv`)
- **Investigação da Base**: O arquivo `BASE_FPD_JUN25_JUN26.csv` disponibilizado na raiz possui 185.116 linhas em nível nacional, contemplando a safra `202605` (sendo 9.762 instalações da Regional Norte).
- **Dados de Aging**: As colunas `AGING90`, `AGING120` e `AGING150` encontram-se com valor `0` para a safra de maio/26 em virtude do tempo de maturação decorrido na data de extração da base (junho/julho de 2026).
- **Conceito Metodológico das 5 Janelas de FPD**:
  - **FPD 30 (Onboarding / Pró-rata)**: 1ª fatura emitida com cobrança proporcional entre o dia de instalação e o fechamento do primeiro ciclo. Mede atrito de onboarding, recusa inicial de entrega e inconsistências cadastrais.
  - **FPD 60 (Marco Oficial Claro)**: 1ª fatura de ciclo cheio (30 dias de uso completo). É o indicador oficial corporativo da Claro para metas operacionais, avaliação de qualidade de venda e remuneração variável.
  - **FPD 90 (Pré-Churn)**: Inadimplência crítica com 2 faturas vencidas consecutivas, gerando bloqueio parcial ou total do sinal de telecomunicações.
  - **FPD 120 (Churn Safra)**: Limiar de cancelamento definitivo no faturamento e estorno financeiro de comissão de parceiro/vendedor.
  - **FPD 150 (Perda Total / Cobrança Jurídica)**: Inadimplência consolidada, perda financeira contábil irreversível e encaminhamento para negativação cadastral (Serasa/SPC) e cobrança jurídica.

### Item 2: Retorno da Matriz de Safra com Divisão Oficial FPD 60
- **Reintrodução da Matriz**: Restaurada a Matriz de Safra FPD (`MATRIZ DE SAFRA FPD — ACOMPANHAMENTO DA MATURAÇÃO`) com suporte ao triângulo de maturação e aberturas analíticas por Canal, Parceiro, Produto, Cidade e Portfólio TV.
- **Divisão Visual Regulatória**:
  - **ONBOARDING (ANTES FPD 60)**: Banda estilizada em lilás/roxo suave sobre a coluna FPD 30.
  - **★ MARCO OFICIAL CLARO**: Banda âmbar/dourada destacada sobre a coluna FPD 60, com badge `OFICIAL` e bordas douradas.
  - **APÓS O FPD 60 (PRÉ-CHURN & CHURN)**: Banda avermelhada suave agrupando as colunas FPD 90, FPD 120 e FPD 150.
- **Métricas Suportadas**: `% acumulado` (padrão oficial), `Absoluto acum.`, `Absoluto no período` e `% no período`.

### Item 3: Padronização Visual das Novas Visões & Helpers Contextuais
- **Conformidade com `PADRAO_DESIGN_PAINEIS.md`**:
  - Todas as novas visões foram encapsuladas em containers padronizados `.panel`.
  - Títulos estruturados em `<h2>` maiúsculos com subtítulos descritivos em `<span class="note">`.
  - Controles de comparação e dimensão utilizam o grupo de abas institucional `.tabs` com classe `.on`.
  - Dicionário `HELP` (`?`) atualizado com verbetes ricos e detalhados para `scatter`, `risco`, `matriz`, `safra` e `esteira`.

### Item 4: Solicitação de WhatsApp Corporativo e Controle de Acesso no Bot
- **Formulário de Cadastro (`public/register/index.html`)**: Inserido campo obrigatório de telefone corporativo com máscara dinâmica `(XX) XXXXX-XXXX`, validação estrita de DDD e envio para o backend.
- **Banco de Dados & API (`schema.sql` e `worker/index.js`)**:
  - Adicionada coluna `telefone TEXT` na tabela `users` do Cloudflare D1.
  - O Worker padroniza o telefone no formato internacional E.164 (`55...`), salva no cadastro do usuário e inclui o número no e-mail de aprovação enviado ao gestor.
  - Criada a rota de sincronização autenticada `GET /api/auth/authorized-phones`.
- **Bot de WhatsApp (`whatsapp-bot/server.py`)**:
  - Implementada verificação de autorização com cache dinâmico de 5 minutos via `is_phone_authorized(phone_number)`.
  - Números não cadastrados ou não aprovados são bloqueados imediatamente com mensagem explicativa e link para cadastro no portal.

### Item 5: Agente Auditor de Layout & Design System
- Criado o script `scripts/layout_checker_agent.py` para auditoria automática de 8 dimensões de conformidade visual:
  1. Variáveis CSS `:root` oficiais.
  2. Gradiente institucional vermelho Claro do cabeçalho.
  3. Marca e subtítulo "Regional Norte".
  4. Registro estrito de botões `.hlp` no dicionário `HELP`.
  5. Padronização da visão de Dispersão MoM & YoY.
  6. Padronização da visão de Risco & Score.
  7. Padronização da Matriz de Safra FPD com Marco Oficial FPD 60.
  8. Uso do componente institucional `.tabs`.
- Governança documentada em `.agents/skills/layout-checker/SKILL.md` e `.agents/rules/layout_rules.md`.
- **Resultado da Auditoria**: Score de Conformidade de **100,0% (8/8 verificações aprovadas)**.


