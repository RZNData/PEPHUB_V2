# Painel de Churn Safra — Regional Norte
## Documentação técnica e funcional completa (handoff para outra IA)

> **Objetivo deste documento:** permitir que outra IA (ou analista) entenda, mantenha e evolua o painel sem precisar reconstruir o raciocínio do zero. Ele descreve o negócio, as regras de cálculo, o pipeline de dados, a arquitetura do HTML, cada seção da interface, as decisões tomadas (e por quê), os bugs já encontrados e as preferências do usuário.

---

## 0. Resumo executivo

- **O que é:** um painel HTML **único e autocontido** (~5,5 MB) que analisa o **churn safra** de instalações de banda larga/TV (Claro/NET) da **Regional Norte** (AM, PA, MA, AP, RR).
- **Grão:** cada linha = **uma instalação** (contrato). Base atual: **348.866 linhas**, 13 safras (**set/2025 a set/2026**).
- **Pergunta central:** das instalações de um mês (safra), quantas desconectaram em até **120 dias** — a janela pela qual o **parceiro de venda é responsável**.
- **Stack:** Python (pandas, openpyxl) para o pipeline de dados → payload JSON comprimido embutido no HTML → JavaScript puro (sem bibliotecas) para toda a interface, gráficos SVG e mapa em Canvas.
- **Arquivo vigente:** `Painel_Churn_Safra 28.html` (a numeração vem do SharePoint do usuário; cada entrega incrementa).
- **Usuário:** Arthur Rezende, analista de Operação Comercial (Belém/PA). Trabalha com safras, churn por aging, carteirização de parceiros e análise geográfica. É detalhista, iterativo e valoriza precisão numérica.

---

## 1. Conceitos de negócio

### 1.1 Safra
Mês de **instalação** do contrato. Derivada de `SK_DATA_REFERENCIA` (formato `AAAAMMDD`) → rótulo `mmm/aa` (ex.: `mai/26`).
Ordem canônica: `set/25, out/25, nov/25, dez/25, jan/26, fev/26, mar/26, abr/26, mai/26, jun/26, jul/26, ago/26, set/26`.

### 1.2 Churn Safra e janelas (D30…D150)
- **Churn DX** = instalações da safra desconectadas em **até X dias** após a instalação.
- As janelas são **acumuladas**: D120 contém D30, D60 e D90.
- Colunas de origem: `QT_CHURN_SAFRA_ATE_30`, `_60`, `_90`, `_120`, `_150` (valor 1 = desconectou até aquele prazo).
- **Indicador oficial = Churn Safra D120.** É a janela de responsabilidade do parceiro.
- **Terminologia exigida pelo usuário:** usar **“Churn Safra D120”**, e **não** “taxa de churn”/“taxa de desconexão” — “taxa” pressupõe base de clientes, que este material não tem. Para motivos usar “**Desconexões por X / instalações**”. Sempre usar **“/”** no sentido de divisão (nunca “sobre”).

### 1.3 Limite de aging — 150 dias (limitação dura da origem)
Verificado calculando `DT_DESCONEXAO − DT_INSTALACAO` nos 348.866 registros: **máximo exatamente 150 dias, zero ocorrências acima**. O indicador CHURN SAFRA da origem já corta na extração. Por isso a matriz tem **5 colunas (M1–M5)** e não as 24 do relatório corporativo. Para M6+ seria preciso nova extração com `QT_CHURN_SAFRA_ATE_180/210…`. Isso está documentado no painel.

### 1.4 Maturidade — **por contrato** (regra vigente)
- **Data de posição:** `20/09/2026` (última `DT_INSTALACAO` da base). Constantes no JS: `POS_Y=2026, POS_M=9, POS_D=20`.
- Um contrato é **maduro** (janela completa) quando `dias desde a instalação ≥ 120`.
- Função JS: `diasDe(r)` reconstrói a data de instalação a partir da safra + `C.dinst[r]` (dia do mês) e compara com a posição; `maturoR(r) = diasDe(r) >= 120`.
- **Histórico importante (não regredir):**
  1. Primeira versão: lista fixa das 4 safras mais recentes como “abertas” → causou inconsistência.
  2. Segunda versão: maturidade por **safra inteira** (última instalação do mês + 120d). mai/26 (113 dias) ficava inteira fora.
  3. **Versão atual:** por **contrato**. Em mai/26, **75,2%** dos contratos já completaram 120 dias. A base oficial subiu de 92.106 para **99.942** instalações (Assinatura+Dados, todas as safras), Churn D120 de 12,54% → **12,84%**.
- Ainda existe `MATUR` (maturidade por safra, dias desde a última instalação do mês) e `isParcial(s)` = `MATUR[s] < 120`. São usados para **rótulos visuais** (etiqueta PARCIAL/FECHADA em tabelas por safra, tracejado em gráficos, marcação `*`). O **cálculo dos KPIs** usa a maturidade por contrato (`IDXC`).

| Safra | Maturidade da safra (dias) | % contratos maduros |
|---|---|---|
| set/25 … abr/26 | 356 … 144 | 100% |
| mai/26 | 113 | **75%** |
| jun/26 … set/26 | 83 … 1 | 0% |

### 1.5 Visão de análise (risco de dupla contagem)
`NM_VISAO_ANALISE` tem **Assinatura** e **Domicílio** para o **mesmo universo**. Somar as duas duplica. O painel **abre filtrado em Assinatura**.

### 1.6 Nunca pagou
- Derivado de `SK_FC_GEROU_PAGOU_EM_{30,60,90,120,150}_DIAS` (1 = gerou e pagou até aquele prazo; 0 = não).
- **Não usar isoladamente** `SK_FC_NUNCA_PG_CHURN_N_DIAS`: é um resultado combinado (“não pagou **ou** desconectou”) e superestima a inadimplência.
- Na base original os flags vinham como SK: **`4014778675` = SIM (1)** e **`845347815` = NÃO (0)**. Na base atual já vêm 0/1.
- Quatro estados usados na seção “Nunca pagou × churn”: desconectou sem pagar; desconectou após pagar; ativo sem pagamento (risco latente); ativo e pagante.

### 1.7 Motivo da desconexão
`SK_TIPO_DESCONEXAO`. Na base original era SK: **`1797991040` = Inadimplência**, **`2511950065` = Opção**, **`2612290563` = Fraude**, vazio = Sem desconexão. Na base atual já vem textual. Preenchido em 100% dos desconectados (totais fecham exatamente com o churn).

### 1.8 Mercado (porte IBGE)
`IBGE.TIPO` exibido com nomenclatura comercial:
`Grandes` → **Grandes Mercados**; `Desenvolvimento` → **Mercados em Desenvolvimento**; `Outros` → **Demais Mercados**. (Mapa `MERCADO` no JS.)

### 1.9 Padrões de abertura do painel
- Visão = **Assinatura**; Produto = **Dados**; Safra = **mai/26** (a safra mais recente com maturidade ≥110 dias; função `defaultAnchor()`).
- Filtro de safra seleciona **um único mês de instalação**; os 120 dias de observação já estão no aging de cada contrato (não somar meses seguintes — foi um erro corrigido).
- Mapa abre mostrando **toda a regional** (zoom ~6), métrica **Volume de desconexões D120**, mínimo por célula = **1**.
- Ranking por dimensão: mínimo de instalações = **1**, “apenas safras fechadas” **desmarcado**.
- Gaveta de filtros **recolhida** por padrão.

---

## 2. Fontes de dados

### 2.1 Base de churn — `Base_Churn_Geocod_v3_FALLBACK_CEP.csv`
~194 MB, separador `;`, 71 colunas, 348.866 linhas. Colunas usadas pelo pipeline:

| Grupo | Colunas |
|---|---|
| Chaves | `CHAVE_CARTEIRA` (21 chars = SK_MUNICIPIO 7 + CNPJ 14), `NR_CONTRATO`, `SK_MUNICIPIO` |
| Tempo | `SK_DATA_REFERENCIA`, `DT_INSTALACAO`, `DT_DESCONEXAO` |
| Churn | `QT_CHURN_SAFRA_ATE_30/60/90/120/150`, `SK_TIPO_DESCONEXAO` |
| Pagamento | `SK_FC_GEROU_PAGOU_EM_30/60/90/120/150_DIAS` |
| Comercial | `NM_CANAL_VENDA_GRUPO`, `NM_CANAL_VENDA_SUBGRUPO`, `NM_PARCEIRO_BI` (fallback `NM_PARCEIRO`), `NM_EMPRESA_EXECUCAO`, `NM_VENDEDOR` |
| Produto/cliente | `NM_TIPO_ASS_DOMICILIO`, `NM_MARCA`, `NM_PERFIL_CLIENTE`, `NM_FORMA_PAGAMENTO_BI`, `NM_VISAO_ANALISE` |
| Geografia | `IBGE.SG_UF`, `IBGE.NM_CIDADE_CI`, `IBGE.NR_DDD`, `IBGE.TIPO_CIDADE`, `IBGE.TIPO`, `BAIRRO`, `CD_NODE` |
| Coordenadas | `LAT_FINAL(FALLBACK_2)`, `LONG_FINAL(FALLBACK_2)` |

**Evolução das bases (útil para entender decisões antigas):**
1. 13 arquivos `Churn_Safra_M0..M12.txt` + `NOVO_GEOCOD.csv` (cruzamento por `COD_IMOVEL`, 60,6% de cobertura geo).
2. `Base_Churn_Geocod.xlsx` consolidada com dimensões **IBGE** (resolveu 87.532 linhas sem cidade e “VIA EMBRATEL”; 16 → 133 cidades).
3. v2 com segunda fonte `GEOCOD_LAT_LONG_RNO_jul26` e `LAT_FINAL/LONG_FINAL` (66,8%). **Continha 3.145 coordenadas (0,0)** → tratadas como ausentes.
4. v2 FALLBACK_CEP: `LAT_FINAL(FALLBACK_2)` com centroide de CEP (**81,4%**).
5. **v3**: igual à anterior + `CHAVE_CARTEIRA` pronta.

**Armadilha histórica:** no CSV v2, `NR_CNPJ` vinha em **notação científica** (`1,96394E+13`) em 98% das linhas — a exportação truncou para 6 dígitos significativos. Zerar à esquerda **não** recupera. A solução foi o usuário gerar `CHAVE_CARTEIRA` na origem. Se voltar a acontecer, peça reexportação com a coluna como **Texto**.

### 2.2 Carteira — `CARTEIRA_UNIFICADA_MANUAL.xlsx`
Aba **`CARTEIRA_UNIFI`** (a aba `CARTEIRA` está vazia). 918 linhas, 449 chaves distintas. Colunas relevantes:
`CHAVE 2` (chave de join), `CARTEIRA/CANAL` (ex.: `CARTEIRA - AGENTE AUTORIZADO.xlsx`), `TIPO_CANAL` (AA, BCC, INDIRETO, NACIONAL, REGIONAL, BRAND SHOP), `EXECUTIVO (NOME COMPLETO)`, `NOME COORDENADOR`, `NOME GERENTE`, `NOME FILIAL`, `KEY ACCOUNT`, `RAZÃO SOCIAL`, `NOME FANTASIA`.
Atenção: há **colunas com nome duplicado** (`MATRÍCULA`, `LOGIN`) — ler por posição ou renomear.

---

## 3. Pipeline de dados (Python)

Script de referência: `pipe.py` (roda em ~40 s). Etapas:

### 3.1 Leitura
- CSV via módulo `csv` (não pandas direto) com `csv.field_size_limit(10**9)`, `encoding='utf-8-sig'`, `delimiter=';'`, mantendo só as colunas necessárias.
- **Evitar ler o XLSX de 116 MB com openpyxl** quando houver CSV: leva ~5 min. Se for XLSX, rodar em background (`nohup … &`) e fazer polling, porque cada chamada de ferramenta tem limite de ~60 s.

### 3.2 Carteirização (join exato)
```python
mapa = {chave: {campo: valor_consensual}}  # agrupado por CHAVE 2
d.CHAVE_CARTEIRA  → mapa.get(chave)
```
- 82 chaves aparecem em mais de uma linha da carteira. **Regra de consenso:** cada campo só é preenchido se **todas as linhas da chave concordam**; senão fica vazio.
- Campos derivados: `executivo`, `coordenador`, `ger_negocio` (NOME GERENTE), `ger_filial` (NOME FILIAL), `key_account`, `ger_canal` (nome do arquivo em CARTEIRA/CANAL, sem prefixo/sufixo, Title Case), `tipo_canal`.
- Sem match → **“Sem carteira”** (categoria filtrável).
- Resultado: **92.413 casados (26,5%)**. Não é falha: a carteira só cobre canais **indiretos** — Porta a Porta Indireto 96%, Porta a Porta Exclusivo 78%, Agente Autorizado 73%; canais diretos 0%.
- As salvaguardas antigas (arredondamento `sci6`, desempate por razão social, **guarda de compatibilidade de canal** via `TIPO_CANAL`) foram **removidas** com a chave exata. Se a chave voltar a ficar corrompida, elas estão descritas na seção 10.

### 3.3 Dimensões
Função `S(x)`: strip, trata `''`, `None`, `nan`, `-1`, `-` como ausentes → `'Não Informado'`. Cidade, bairro, vendedor e hierarquia em Title Case.
- `abk` (uint8): faixa de aging da desconexão: 0 = não desconectou até 150; 1..5 = até D30…D150 (calculado da mais larga para a mais estreita).
- `pbk` (uint8): mesma lógica para “gerou e pagou”; 0 = nunca pagou até 150.
- `tpk`: 1 Inadimplência, 2 Opção, 3 Fraude, 0 sem desconexão. Invariante validada: `(tpk>0) == (abk>0)`.
- `contrato` (uint32), `dinst` (dia do mês da instalação, uint8), `aging` (dias até a desconexão, 255 = sem desconexão). A data de desconexão é **reconstruída no navegador** (safra + dinst + aging) para economizar bytes. Invariante validada: zero incoerências entre `aging` e `abk`.
- Coordenadas: descartar `lat==0 or lon==0`, nulos, e fora do bbox `lat ∈ [-35, 6]`, `lon ∈ [-75, -30]`.

### 3.4 Normalização de bairros (`norm5.py`)
Objetivo: unificar grafias do mesmo bairro **dentro da mesma cidade** (homônimos entre cidades são preservados).
**Camada determinística:** remove acentos/pontuação; expande abreviações (`Jd→Jardim`, `Vl→Vila`, `Cj/Cjr→Conjunto`, `Pq/Prq→Parque`, `Res→Residencial`, `Col→Colonia`, `Dr→Doutor`, `Sta→Santa` …); remove distritos redundantes (`icoaraci, outeiro, mosqueiro, coqueiro, maracana, calhau, anjo da guarda, turu`); expande iniciais **pelo contexto da cidade** (`A Lindas → Aguas Lindas`, `Prq 10 N → Parque 10 de Novembro`); `y→i`; partículas (de/da/do) ignoradas na comparação.
**Camada de erro de digitação:** Levenshtein ≤1 (nomes <8 chars) ou ≤2, **somente se**:
- a variante for **minoritária** (volume < 30% da forma principal), **e**
- havendo coordenadas (≥4 pontos em cada), os **centroides distarem < 1,5 km**.
**Sufixo numérico/romano é identidade:** `Cohab Anil I–IV` e `Cohatrac I–V` **nunca** se fundem (o usuário exigiu isso explicitamente). Comparação é feita **apenas dentro do mesmo setor**.
**Guardas validadas:** `Lago Azul` × `Lagoa Azul` (Manaus) ficam separados (volumes 926/456, 1,38 km). Distância pura **não** separa setores (Cohab Anil I/II distam 0,34 km) — por isso o sufixo é regra dura.
**Rótulo canônico:** o nome com mais tokens úteis, penalizando iniciais e ruído (“etapa”), desempate por volume. Setor em algarismo romano maiúsculo; `D Agua → D'Agua`.
Resultado: ~115 grupos, ~165 grafias absorvidas; **1.014 bairros**.
**O de-para (`depara`) é embarcado no payload** (`{cidade: {bairro_bruto: bairro_canônico}}`, 1.451 entradas) e é **reaplicado a cada atualização** para manter a unificação constante. Em reconstruções, ler o `depara` do HTML anterior em vez de recalcular.

### 3.5 Encode do payload (`enc.py` / etapa 4 do pipe)
- Cada dimensão vira dicionário ordenado + vetor de códigos: **uint8** se < 256 valores, senão **uint16** (cidade, bairro, node, parceiro, empresa, vendedor).
- Numéricos: `abk, pbk, tpk, dinst, aging` (uint8), `ctr` (uint32).
- Coordenadas **quantizadas em uint16** no bbox (`gx, gy`, 0 = sem coordenada), resolução ~30–45 m (suficiente para concentração, sem expor endereço exato).
- **Malha de referência offline** (`bmx, bmy, bmn`): grade de 0,0005° com contagem de imóveis — usada como mapa base quando provedores externos falham.
- Cada vetor: `zlib.compress(level 6)` → base64. JSON: `{n, nb, dicts, bbox, cols:{k:{t:'u8|u16|u32', b:base64}}, depara}`.
- Tamanho atual: ~5,3 MB de payload, HTML final ~5,5 MB.

### 3.6 Montagem do HTML
O HTML é dividido em `tpl_head.txt` (tudo até `const PAYLOAD = `), o JSON do payload e `tpl_tail.txt` (resto). Montagem = `head + data.json + tail`. Para atualizar só o código, extraia head/tail do HTML mais recente e mantenha o payload; para atualizar dados, gere novo `data.json` e reutilize head/tail.
```python
i = s.index('const PAYLOAD = '); j = s.index('\n', i)
head, payload, tail = s[:i+16], s[i+16:j].rstrip().rstrip(';'), s[j:]
```

---

## 4. Arquitetura do front-end (JavaScript puro)

### 4.1 Carga
1. Tela “Descompactando base…”.
2. Para cada coluna: `atob` → `DecompressionStream('deflate')` → `Uint8Array | Uint16Array | Uint32Array` em `C[k]`. Dicionários em `D[k]`, total em `N`.
3. `init()` monta a UI e chama `render()`.
4. `autoQualify()` roda ~60 ms depois (inferência de bairros offline, seção 6.6).

Exige navegador moderno (Edge/Chrome atualizado) por causa do `DecompressionStream`.

### 4.2 Estado global — `sel` é a **fonte única de verdade**
- `sel = { dimensao: Set(códigos) }`. Filtro ausente = todos.
- `statusF`: `'all' | 'fechadas' | 'abertas'` (rótulo exibido: “Somente parciais”).
- `lassoSet`: Set de linhas dentro da área desenhada no mapa (ou null).
- `filterSrc = { dim: Map(código → 'topo'|'mapa') }` — origem de cada filtro, usada para separar as tags “herdados” × “desta seção”.
- **Lição aprendida:** o `render()` antigo relia os `<select>` do DOM a cada ciclo e apagava os filtros vindos do mapa. Agora: `readFiltersFromUI()` só é chamada quando o usuário mexe na gaveta; `syncFilterUI()` espelha `sel` de volta nos selects. Não inverter isso.

### 4.3 Índices
`buildIndex()` percorre as N linhas uma vez e produz:
| Índice | Conteúdo | Usado por |
|---|---|---|
| `IDX` | todos os filtros, **inclusive safra** | KPIs, mapa, cidades, ranking, tabela de concentração |
| `IDXC` | subconjunto de `IDX` com **contrato maduro** (`maturoR`) | indicadores oficiais |
| `IDXT` | todos os filtros **exceto safra** | séries temporais (gráficos/tabelas por mês) |

`IDXT` existe para que **todas as safras continuem visíveis** nos gráficos por mês mesmo com uma safra selecionada; a safra escolhida é apenas **destacada** (fundo âmbar, etiqueta “EM FOCO”, série própria em linha grossa na curva). Isso foi pedido explicitamente.

### 4.4 Agregação
`blank()` → `{inst, c[5], np[5], npc[5], tp[3]}`. `addRow(o,r)` preenche churn acumulado por janela, nunca pagou, churn sem pagamento e motivo (só dentro de D120). `aggBy(dim, idx)` e `aggTot(idx)`.

### 4.5 Ciclo de render
`render()` mostra o overlay “processando seleção…” e chama `render_()` num `requestAnimationFrame`:
`applySafra → updateSelCounts → buildIndex → refreshAvailability → drawKpis, drawSafra, drawCurva, drawCid, drawNp, drawMot, drawMtx, drawEsteira, drawRank, drawChips, buildCityOptions, drawMapRank, drawFilterTags → drawGeoFoot → mapa`.

### 4.6 Filtros dependentes (slicer) — `refreshAvailability()`
**Passe único** (7× mais rápido que um passe por dimensão): para cada linha conta em quantas dimensões ativas ela falha. 0 falhas → disponível para todas; exatamente 1 → disponível só para aquela dimensão; 2+ → nenhuma. Um filtro **não se auto-restringe**.
Opções indisponíveis: cinza, itálico, `disabled`, **movidas para o fim da lista**; disponíveis no topo em ordem alfabética. Rodapé: “X de Y disponíveis”.

### 4.7 Gráficos
SVG gerado à mão (`svg()`, `el()`, `tx()`), `viewBox` responsivo. **Cuidado:** a regra CSS de largura 100% está **escopada** aos contêineres de gráfico (`#chSafra svg, …`). Uma regra global `svg{width:100%}` já esticou um ícone de legenda até ocupar o painel inteiro. Ícones inline usam a classe `svg.ico`.
Tooltips: `hov(elemento, html)` e `hitRect()` (área invisível de captura); div `.gtip` fixa, reposicionada para não sair da tela.

---

## 5. Seções da interface (de cima para baixo)

1. **Cabeçalho** — faixa em degradê vermelho→laranja→âmbar (`#8a0f18 → #c0191f → #e23a1e → #f47a1f → #f9b233`), ícone circular à esquerda, título “**Churn Safra** Regional Norte” (peso forte + leve). Barra escura abaixo com contexto. **Sem ícone no canto direito** (removido a pedido).
2. **Filtros (gaveta recolhida)** — botão “Filtros” + resumo textual do que está ativo. Cada filtro tem busca própria, botão `T` (seleciona visíveis) e `×` (limpa só aquele). Filtro de safra especial (seletor único, com “(parcial)” nas imaturas). Dimensões: visão, UF, cidade, mercado, tipo de cidade (cabo), DDD, bairro, node, canal grupo/subgrupo, parceiro, empresa de execução, **vendedor**, **carteira·canal, carteira·tipo, gerente de negócio, gerente de filial, coordenador, executivo, key account**, produto, marca, perfil, pagamento, motivo.
3. **Indicadores (KPIs)** — calculados sobre `IDXC`. Cartões: Instalações (“X com janela completa · Y%”), Churn Safra D120, D30, D90, Nunca pagou D120, Churn sem pagamento, Churn após pagar, Ativos sem pagamento, Churn por inadimplência/fraude/opção (% do churn), Retenção D120, **Ainda em maturação** (contratos da seleção que ainda não completaram 120 dias). Se nenhum contrato for maduro, cai para a própria seleção com etiqueta “parcial” (evita tela de traços).
4. **Churn safra por safra** — barras de instalação + linhas %D120 (vermelho `#e03131`) e %nunca pagou (roxo `#7d4bb0`), com **halo branco**, marcadores com anel e rótulos com caixa branca (contraste pedido pelo usuário). Safras parciais em cinza claro/tracejado.
5. **Curva de maturação** — % acumulado D30→D150; linha preta = média das maduras; safras parciais tracejadas; safra em foco em âmbar grosso; linha vertical em D120 (“janela oficial”).
6. **Mapa de concentração geográfica** (seção 6).
7. **Cidades — visão IBGE** — abas Cidade/Mercado/Tipo(cabo)/UF/DDD; gráfico top 20 + tabela completa com D30…D150, nunca pagou, motivos, retenção.
8. **Nunca pagou × churn** — barras empilhadas nos 4 estados por safra (% ou absoluto) + tabela.
9. **Motivo da desconexão** — composição do churn D120 por safra + tabela (% do churn e % da safra).
10. **Matriz de safra — responsabilidade do parceiro** — triângulo M1–M5; **faixa vermelha “RESPONSABILIDADE DO PARCEIRO — 120 DIAS” sobre M1–M4**, borda vertical grossa após M4, M5 esmaecido (“APÓS A JANELA”). Modos: % acumulado, absoluto acumulado, absoluto no período, % no período. Células parciais **exibidas** com `*` e borda âmbar (opção de ocultar). “Abrir por” troca linhas por canal/parceiro/empresa/cidade/mercado/produto. Escala vermelha normalizada pelo p95.
11. **Esteira de instalações × desconexões** — barras por faixa de aging (0–30…121–150 + conectado) e tabela com D30…D150 (inclui D60), maturidade, retenção.
12. **Ranking por dimensão** — abas com todas as dimensões (inclui vendedor e hierarquia de carteira), colunas D30/D60/D90/D120, nunca pagou, churn s/ pgto, % inadimplência, fraude, “vs. média” em p.p. Ordenável. Defaults: mín. 1, “apenas safras fechadas” desmarcado. Botão “Exportar visão (CSV)”.
13. **Atualização da base** (área restrita — seção 7).
14. **Notas metodológicas**.
Todas as seções têm botão **“?”** com pop-up explicativo (objeto `HELP` no JS: `filtros, kpis, safra, curva, mapa, cidades, np, motivo, esteira, ranking, matriz, upload, carteira, metodo`). Ao adicionar seção nova, **criar o verbete** — há validação de que todo botão tem verbete.

---

## 6. Mapa (Canvas, Web Mercator, sem bibliotecas)

### 6.1 Mapa base
Provedores **gratuitos e sem chave de API**: Esri Light Gray (**padrão**), Esri ruas, Esri topográfico, Esri satélite, Esri Dark Gray, OpenTopoMap, **Malha de imóveis (offline)**, sem mapa base.
- **Removidos por decisão do usuário/técnica:** OpenStreetMap padrão (retornou **403 – tile usage policy**) e CARTO (passou a exigir chave e devolve tile com marca d'água, sem erro HTTP).
- Se 5 tiles falharem sem nenhum sucesso, o painel exibe aviso e cai para a malha offline.
- Tiles carregados com reaproveitamento do tile “pai” durante o zoom (evita buracos).

### 6.2 Modos de exibição
- **Células agrupadas** — grade de 7 px no zoom atual; raio ∝ √volume; cor pela métrica. Abaixo do zoom 9,5 agrega **por cidade** (bolhas rotuladas).
- **Ponto simples** — um marcador por instalação; **seletor de métrica oculto** (não se aplica); duas cores (azul ativo, vermelho desconectado); filtro “Exibir”: todos / somente desconectados D30, D60, D90, D120, até D150; tamanho e opacidade reguláveis.
- **Mapa de calor** — kernel gaussiano em canvas offscreen, rampa térmica, **sensibilidade 1–10 (padrão 8)**; “ponderar pela métrica” usa encolhimento bayesiano `n/(n+6) × √n` para não deixar célula de 1 registro dominar. Legenda de origem do bairro **oculta** neste modo.

### 6.3 Métricas (seletor agrupado)
Volume (instalações; **desconexões D120 — padrão**; não desconectaram D120; não desconectaram e nunca pagaram) · Churn safra D30/D60/D90/D120/D150 · Pagamento (nunca pagou / instalações; churn sem pagamento / instalações; ativos sem pagamento / instalações) · Motivo (inadimplência/fraude/opção / instalações).
Rampas **sem branco na base** (saturação desde o início, pedido do usuário): azul, vermelho/âmbar e roxo. A seção “Qualidade do cadastro” foi **removida** do seletor.

### 6.4 Interações
- Arrastar, roda do mouse, duplo clique, botões +/−/⤢.
- **Laço livre (✎)**: desenha polígono; guardado em lon/lat; ponto-em-polígono por ray casting; escurece o exterior; `⌫` limpa, Esc cancela. Vira tag “Área desenhada”.
- **Hover**: célula → volumes, churn, nunca pagou, motivos, quantos inferidos. Ponto simples → bairro, cidade, node, total e até 5 contratos (número, data de desconexão, motivo, vendedor). Plurais corrigidos (`plur()`).
- **Clique** (ponto ou célula) → **popup de contratos**: contrato, instalação, desconexão, aging, tipo, pagamento, safra, canal, parceiro, **vendedor, executivo, ger. filial**, perfil, produto, bairro (com `*` se inferido), cidade, node. Exportável em CSV (inclui toda a hierarquia de carteira).
- **Enquadrar cidade**: seletor agrupado por mercado (**Grandes Mercados primeiro**, depois Desenvolvimento, Demais), cada grupo por volume, com contagem **respeitando os filtros ativos** (exceto o próprio de cidade). É um filtro real (grava em `sel.cidade`).
- **Reenquadramento** (`refitMap`): ao filtrar, enquadra a **cidade inteira** do recorte (não só os pontos filtrados) se o recorte tiver ≤ 6 cidades; senão, pelos próprios pontos.

### 6.5 Tabela “Maiores concentrações” (lateral)
- Seletor: Geografia (segue o zoom: cidade → bairro a partir do zoom 13), cidade, bairro, node, canal agrupado, subgrupo, parceiro, perfil, produto e grupo **Força de venda** (vendedor, executivo, coordenador, gerente de negócio, gerente de filial, key account, carteira, tipo de carteira).
- Colunas: nome · Inst. · coluna da métrica (em “Concentração de instalações” fica **Inst / D120 / %D120**) · %D120 com **formatação condicional** (vermelho proporcional acima da mediana até o p97; barra de intensidade foi removida a pedido).
- **Ordenável** por qualquer coluna; **totalizador** no rodapé (+ “Total geral” se houver corte de 400 linhas).
- **Sem corte mínimo** (antes um mínimo de 10 escondia a tabela inteira em recortes pequenos). Exceção: vendedor sem recorte geográfico usa mínimo 3 (8 mil nomes).
- **Clique na linha = filtro rápido global** (seção 6.7).
- **Disclaimer** acima das tags: os filtros valem para **todo o painel**.

### 6.6 Bairros “Não Informado” e inferência
- 87.534 registros sem bairro; só **26.437 têm coordenada** (os 61.097 sem coordenada são irredutíveis por geolocalização).
- **Inferência espacial offline** (automática na carga): vizinho mais próximo geocodificado **na mesma cidade**, com corte de 1,2 km. Validação por holdout: **≈86% de acerto**. Resolve **25.906** registros (~98% dos qualificáveis) em < 1 s.
- **O bairro inferido recebe o MESMO código do bairro real** (sem sufixo, sem duplicar linha). A origem fica em `revFlag` (Uint8Array). **Não** voltar a criar rótulos “Nome *” no dicionário — gerou duplicatas e foi rejeitado.
- Distinção **apenas visual no mapa**: **losango** (ponto simples e células majoritariamente inferidas) vs. círculo; legenda “Origem do bairro”. No popup/CSV, bairro inferido leva `*`.
- Botão “⟳ Qualificar bairros não identificados via API”: popup com **abas “Cenário filtrado” (padrão, primeira) e “Toda a base”**, mostrando **total sem bairro → com coordenada → sem coordenada**. Opção de usar **Nominatim/OSM** para o que sobrar (células de ~220 m, 1 req/s). Barra de progresso com tempo decorrido/estimado, botão interromper e **relatório final** com a lista de **bairros que receberam registros** e quantos.
- Sinal de negócio relevante (sempre manter visível): registros **sem coordenada** têm churn D120 ~72% contra ~7% dos com coordenada — possivelmente falha de cadastro de algum canal ou endereço apagado na desconexão.

### 6.7 Filtros rápidos (mapa/tabela refletem na ferramenta toda)
- `quickFilter(dim, nome)` alterna o valor em `sel`, marca origem `'mapa'`, sincroniza a gaveta, re-renderiza tudo e reenquadra.
- Filtros **acumulam** entre dimensões (ex.: cidade Manaus → bairro Centro → trocar tabela para Canal = canais do Centro de Manaus). Validado: 10.972 → 324 → 55 com interseção correta.
- **Tags separadas por origem** acima da tabela:
  - **Herdados** (gaveta do topo, incluindo safra e status);
  - **Desta seção** (mapa/tabela, incluindo área desenhada).
  Cada tag com `×`; cada grupo com seu “limpar”; “limpar todos os filtros” quando há os dois.
- Clique respeita o escopo (bairro homônimo de outra cidade não entra — “Centro” tem 9.823 na base, só 324 no recorte de Manaus).

### 6.8 Tabela abaixo do mapa
Mostra **tudo que está na tela** (não só safras fechadas): com coordenada × sem coordenada × **total**, com Instalações, métrica corrente, %D120, % nunca pagou e **“Janela 120d completa”** (quantos contratos já maduros). Responde aos filtros, cidade e laço.

---

## 7. Área de atualização da base

- **Restrição por IP/hostname** (IP `10.89.202.230`, hostname `CLR0AN001242041`): tentativa de detectar IP via WebRTC; se não expuser, liberação manual digitando hostname/IP (grava em `localStorage`).
- **Importante e já comunicado ao usuário:** num HTML estático **isto não é segurança**, é um guarda operacional contra uso acidental. Controle real exige hospedar com autenticação.
- Aceita **CSV `;`** com nomes de coluna originais (XLSX é recusado com orientação — o leitor pesaria mais que o painel).
- Pipeline no navegador: valida colunas obrigatórias (aborta se faltar) → monta dimensões → **aplica o de-para de bairros embarcado** → valida coordenadas → reconstrói dicionários, índices, filtros, malha → dispara inferência de bairros.
- A troca vale para a sessão; “Exportar pacote atualizado” gera o JSON para regenerar o HTML.
- **Pendência técnica:** o upload no navegador foi escrito antes da carteirização. Ele monta contrato, datas e aging, mas **não** gera as dimensões `vendedor`, `executivo`, `coordenador`, `ger_negocio`, `ger_filial`, `key_account`, `ger_canal`, `tipo_canal` (nem lê a carteira). Após um upload pelo navegador essas dimensões ficariam ausentes. Para atualizações completas, **usar o pipeline Python** (seção 3) até que o upload seja estendido.

---

## 8. Números de referência (para validar qualquer reconstrução)

Recorte **Visão = Assinatura, Produto = Dados**:

| Verificação | Valor esperado |
|---|---|
| Linhas totais da base | 348.866 |
| Linhas Assinatura+Dados (todas as safras) | 140.700 |
| Contratos maduros (≥120 d) em Assinatura+Dados | **99.942** |
| Churn Safra D120 oficial (maduros) | **12,84%** |
| mai/26 Assinatura+Dados | 10.447 inst · 7.836 maduros (75%) |
| mai/26 todas as visões/produtos | 26.101 inst · 19.627 maduros (75,2%) · Churn D120 17,77% |
| Motivos no churn D120 (safras fechadas, versão antiga) | Inadimplência ~61% · Opção ~26% · Fraude ~13% |
| Churn sem nenhum pagamento | ~73% de todo o churn D120 |
| Cobertura de coordenadas | 283.854 (81,4%) |
| Bairros após normalização | 1.014 |
| Bairros inferidos | 25.906 |
| Casados com carteira | 92.413 (26,5%) |
| Distintos: executivo / ger. filial / ger. negócio / coordenador / vendedor | 21 / 6 / 2 / 3 / 7.985 (sem contar “Sem carteira”) |

Invariantes que sempre devem valer:
- soma dos motivos dentro de D120 = churn D120;
- ativos D120 + churn D120 = instalações;
- churn sem pagamento + ativos sem pagamento = nunca pagou D120;
- acumulado da matriz = soma dos incrementais;
- `(tpk>0) == (abk>0)`;
- nenhuma célula com `aging` incoerente com `abk`.

---

## 9. Como validar alterações (processo que funcionou)

1. **Sintaxe:** extrair o `<script>` e rodar `new Function(src)` no Node.
2. **IDs:** conferir que todo `getElementById('x')` usado no JS existe no HTML (script de checagem por regex).
3. **Execução real:** há um **simulador de DOM em Node** (`sim.js`) que stuba `document`, `canvas`, `select`, `requestAnimationFrame` e substitui o `DecompressionStream` por `zlib.inflateSync`. Ele executa o painel inteiro, permite chamar funções (`quickFilter`, `drawMapRank`…) e inspecionar o `innerHTML` gerado.
   - **Lição:** só checar sintaxe não basta. Um erro de escopo (`fEl is not defined` dentro de `init()`) deixou o painel “carregando” para sempre e só foi pego executando.
   - `render()` é assíncrono (rAF): nos testes, aguardar ~80 ms após cada ação.
4. **Números:** decodificar o payload em Node e recalcular os KPIs de referência (seção 8).
5. **Ajuda:** conferir que todo botão `data-h` tem verbete em `HELP`.

---

## 10. Decisões, erros já cometidos e lições (não repetir)

| Tema | O que aconteceu | Regra atual |
|---|---|---|
| Aberto × fechado | Lista fixa de 4 meses divergia da maturidade real; mai/26 aparecia fechada num lugar e parcial em outro, e contaminava o KPI | Critério único; hoje por **contrato** |
| Safra âncora | Selecionar mai/26 somava jun–set nas instalações | Safra = um único mês; 120 d vêm do aging |
| Séries por mês | Filtrar safra escondia os outros meses | Usar `IDXT`; safra só destacada |
| Mapa não aparecia | Zoom regional fazia tudo virar pontos invisíveis | Agregar por cidade abaixo do zoom 9,5 |
| Tiles | OSM 403; CARTO exige chave | Esri + OpenTopoMap + malha offline |
| SVG global | `svg{width:100%}` inflou ícone de legenda | Regra escopada + classe `.ico` |
| Bairros inferidos | Rótulo “Nome *” criou duplicatas na tabela | Mesmo código, flag paralela, distinção só no mapa |
| Tabela vazia | Corte mínimo de 10 escondia tudo em recortes pequenos | Sem corte (exceto vendedor sem recorte) |
| Seletor de cidade | Contagem fixa da base toda | Recalculada com os filtros ativos |
| Filtros do mapa | Só “realçavam” e confundiam | Filtros globais reais, acumuláveis, com tags por origem |
| `render()` | Relia o DOM e apagava filtros do mapa | `sel` como fonte única |
| Disponibilidade | Um passe por dimensão (~540 ms) | Passe único (~76 ms) |
| Arquivo solto | Matriz entregue em HTML separado; usuário reclamou | **Sempre integrar no painel existente** |
| CNPJ | Notação científica no CSV | Usar `CHAVE_CARTEIRA` pronta; se corromper, pedir reexportação como texto |
| Carteira sem chave exata (histórico) | Arredondamento a 6 dígitos gerava colisões e falsos positivos (varejo herdando executivo de PAP) | Se voltar: arredondar os dois lados, desempatar por razão social normalizada, consenso por campo e **guarda de canal** (`TIPO_CANAL` compatível com `NM_CANAL_VENDA_GRUPO`) |
| Coordenadas | 3.145 pontos (0,0) iam parar no Atlântico | Descartar zero e fora do bbox |
| Upload “trava de IP” | Pedido de restringir por IP | Implementado como guarda operacional, com aviso explícito de que não é segurança |

---

## 11. Ambiente de trabalho (particularidades)

- O ambiente de execução **reinicia com frequência** e perde `/home/claude`. Os arquivos em `/mnt/user-data/uploads` normalmente sobrevivem, mas nem sempre.
- Estratégia de recuperação: o **HTML mais recente contém tudo** (código + payload + de-para). Basta extrair head/payload/tail (seção 3.6). Se o usuário não reenviar, peça **o HTML mais recente** (não um antigo — já se perdeu trabalho partindo do 25 em vez do 26).
- Uploads grandes às vezes falham silenciosamente. Verificar a pasta por ~2–3 min antes de concluir que não chegou; sugerir CSV reduzido às colunas necessárias ou envio isolado.
- Chamadas de ferramenta têm limite de ~60 s: processamentos longos em `nohup … &` com polling.
- Entregas vão para `/mnt/user-data/outputs/Painel_Churn_Safra.html` (o SharePoint numera automaticamente).

---

## 12. Perfil e preferências do usuário

- Escreve em português do Brasil; respostas devem ser em PT-BR, estruturadas (títulos, tabelas curtas), explicando **a causa raiz** de cada problema e **o que mudou**, com números que comprovem.
- Muito atento a detalhes de UI: plural (“1 desconexão / 2 desconexões”), contraste, legendas, tamanho de fonte, rótulos cortados, esmaecimento, enquadramento do mapa.
- Quer que **tudo reflita em tudo**: filtros do mapa/tabela = filtros globais; tabelas devem mostrar o que está na tela.
- Prefere **mostrar tudo** (sem cortes silenciosos) e sinalizar os maiores com formatação.
- Exige rigor conceitual (terminologia de churn safra, janela de 120 d, maturidade por contrato).
- Não quer que o trabalho anterior seja descartado — **evoluir o arquivo existente**.
- Aceita bem ressalvas técnicas honestas (ex.: limite de 150 dias, trava de IP não ser segurança, CNPJ corrompido) desde que venham com alternativa.

---

## 13. Ideias e pendências em aberto

1. Estender o **upload no navegador** para ler a carteira e gerar vendedor + hierarquia comercial e maturidade por contrato (hoje só o pipeline Python faz).
2. Nova extração com aging > 150 d para estender a matriz a M6+.
3. Investigar o grupo **sem coordenada/sem bairro** (churn ~72%): qual canal gera, se o endereço é apagado na desconexão.
4. Enriquecer por CEP os 61 mil registros sem coordenada.
5. Carteira cobre só canais indiretos — se houver carteira de canais diretos (Ativo, Lojas, Eletrônicos, Receptivo), cruzar pela mesma `CHAVE_CARTEIRA`.
6. Hospedar o painel com autenticação real se a área de upload precisar de controle de acesso de verdade.

---

## 14. Glossário rápido

| Termo | Significado |
|---|---|
| Safra | Mês de instalação |
| DX | Desconectado em até X dias após a instalação (acumulado) |
| Maduro / janela completa | Contrato com ≥ 120 dias desde a instalação na data de posição |
| Parcial | Safra/contrato que ainda não percorreu os 120 dias |
| NP | Nunca pagou (nenhuma fatura gerada e paga na janela) |
| Churn sem pagamento | Desconectado **e** nunca pagou |
| Ativo sem pagamento | Não desconectou **e** nunca pagou (risco latente) |
| Carteira | Estrutura comercial do parceiro (executivo, coordenador, gerentes, key account) |
| Inferido | Bairro atribuído por vizinho geográfico, não pelo cadastro |
| Herdados / desta seção | Origem dos filtros ativos: gaveta do topo × mapa/tabela |
| Posição | 20/09/2026 — data de referência do cálculo de maturidade |
