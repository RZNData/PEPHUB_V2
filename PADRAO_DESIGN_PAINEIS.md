# Padrão Oficial de Design System e Arquitetura — Painéis Regionais

Este documento consolida o **padrão oficial de design, arquitetura e engenharia** para todos os relatórios e painéis analíticos da Regional Norte, derivado da arquitetura do `Painel_Churn_Safra 28.html`.

---

## 1. Princípios Fundamentais de Engenharia

1. **Zero Dependências Externas (Self-Contained):**
   - Não utilizar bibliotecas pesadas de terceiros (React, Vue, jQuery, Chart.js, D3.js, Leaflet, Mapbox, Bootstrap, Tailwind).
   - O painel deve ser um arquivo único ou estático nativo, executando 100% no cliente em JavaScript Vanilla moderno (ES6+), HTML5 e CSS3.
   - Gráficos renderizados programaticamente em **SVG nativo** (com `viewBox` responsivo).
   - Mapas geoespaciais renderizados em **HTML5 Canvas 2D** com projeção matemática pura (Web Mercator).

2. **Alta Performance com Dados Massivos:**
   - Payload compactado em formato colunar com `zlib/deflate` codificado em Base64.
   - Descompressão instantânea no navegador via Stream nativa: `DecompressionStream('deflate')`.
   - Armazenamento em memória através de **Typed Arrays** (`Uint8Array`, `Uint16Array`, `Uint32Array`), reduzindo consumo de RAM em mais de 80% comparado a objetos JavaScript genéricos.
   - Dicionários indexados para dimensões categóricas (strings armazenadas uma única vez).
   - Reconstrução de atributos derivados no cliente (datas relativas, agings, status).

3. **Fonte Única da Verdade no Estado:**
   - Estado centralizado em um objeto único: `sel = { dimensao: Set(códigos) }`.
   - Filtros de UI nunca controlam o estado por leitura direta do DOM durante os loops de renderização; a UI é um espelho do estado `sel`.

4. **Filtros Dependentes de Passe Único (Slicer O(N)):**
   - Algoritmo de filtragem dimensional que avalia todas as dimensões ativas em uma única varredura dos registros (`refreshAvailability`), desabilitando opções mutuamente exclusivas e movendo itens indisponíveis para o rodapé em cinza e itálico, sem se auto-restringir.

---

## 2. Design System & Identidade Visual

### 2.1 Paleta de Cores

```css
:root {
  /* Fundos e Painéis */
  --bg: #f4f5f7;          /* Fundo principal limpo e neutro */
  --panel: #ffffff;       /* Fundo dos cartões e painéis */
  
  /* Textos e Tipografia */
  --ink: #1c2430;         /* Texto primário de alto contraste */
  --ink2: #5b6675;        /* Texto secundário e rótulos técnicos */
  --ink3: #8b95a3;        /* Texto terciário, notas e placeholders */
  
  /* Linhas e Divisórias */
  --line: #dfe3e8;        /* Bordas externas de painéis e tabelas */
  --line2: #eceef1;       /* Divisórias sutis entre linhas e seções */
  
  /* Navegação e Destaques Escuros */
  --nav: #1b2430;         /* Barra de contexto e botões principais */
  --nav2: #27323f;        /* Estados de hover em elementos escuros */
  
  /* Semântica Analítica */
  --red: #c0392b;         /* Churn, cancelamento, inadimplência e alertas */
  --amber: #c98a15;       /* Períodos parciais, atenção, safra em foco */
  --green: #2f7d5d;       /* Retenção, sucesso, safras fechadas */
  --blue: #2a5d8f;        /* Links, seleções ativas, contratos ativos */
  --purple: #6b4b8a;      /* Inadimplência sem pagamento (NP) */
}
```

### 2.2 Identidade do Cabeçalho

- **Faixa Superior:** Gradiente horizontal corporativo:
  `linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%)`
- **Ícone de Identidade:** Círculo com borda branca semi-translúcida (`2.4px solid rgba(255,255,255,.95)`).
- **Tipografia do Título:** `font-weight: 800` para a marca/assunto principal, `font-weight: 300` para o complemento institucional (`Regional Norte`).
- **Barra de Contexto Escura (`.hd-sub`):** Fundo `--nav`, texto claro com pontos separadores (`.dot`), indicando versão, data de posição dos dados e escopo.

### 2.3 Tipografia e Hierarquia

- Família: `"Segoe UI", Roboto, Arial, sans-serif` (nativa de alta legibilidade, sem dependência de webfonts externas).
- Tamanhos e pesos:
  - Títulos de painel: `12px`, maiúsculas, `letter-spacing: 0.6px`, `font-weight: 600`, cor `--ink2`.
  - Valores de KPI: `22px`, `font-weight: 600`, `letter-spacing: -0.3px`.
  - Rótulos de KPI: `10.5px`, maiúsculas, `letter-spacing: 0.5px`, cor `--ink3`.
  - Tabelas e dados: `12px`, altura de linha `1.45`.

---

## 3. Componentes da Interface

### 3.1 Painéis (`.panel`)
- Fundo branco, borda `1px solid var(--line)`, raio sutil `3px`, margem inferior `14px`.
- Cabeçalho `h2` integrado com título à esquerda, nota de apoio `span.note` e botão de ajuda contextual `.hlp` (`?`) alinhado à extrema direita.

### 3.2 Botões de Ajuda Contextual (`.hlp`) & Modais
- Botão circular discreto: `19px x 19px`, `border: 1px solid var(--line)`, texto `?`.
- Ao clicar, abre modal com fundo esmaecido (`rgba(18,24,32,.55)`).
- Todo botão `?` deve possuir verbete correspondente no dicionário central `HELP`.

### 3.3 Cards de KPI (`.kpis` e `.kpi`)
- Grade flexível responsiva com divisórias sutis.
- Rótulo superior curto em maiúsculas (`.k`).
- Valor em destaque (`.v`) com cor semântica.
- Linha de detalhamento (`.d`) com porcentagens ou bases absolutas.
- Badges inline (`.pc`) em tom âmbar quando o indicador envolver dados parciais.

### 3.4 Gaveta de Filtros Retrátil
- Botão expansor `.drawer-btn` que preserva espaço em tela.
- Chips visuais no topo resumindo filtros ativos com opção de remoção imediata (`×`).
- Cada seletor possui campo de busca rápida integrado, botão `T` (marcar visíveis) e botão `×` (limpar seletor).

### 3.5 Separação de Tags de Filtro por Origem
- **Filtros Herdados:** Aplicados na gaveta superior (UF, Safra, Canal, etc.).
- **Filtros Desta Seção:** Aplicados interativamente por cliques em gráficos, linhas da tabela de concentração ou laço no mapa.
- Garante total clareza ao usuário sobre por que os dados estão filtrados.

---

## 4. Gráficos & Visualização de Dados (SVG Puro)

1. **Responsividade:** Uso obrigatório de `viewBox` no SVG, com regras de CSS escopadas para o contêiner do gráfico (nunca aplicar `svg { width: 100% }` globalmente).
2. **Halo e Contraste:** Rótulos numéricos sobre barras ou linhas devem ter halo branco (`stroke: #fff; stroke-width: 3px; paint-order: stroke fill;`) para leitura infalível.
3. **Diferenciação de Status:**
   - Períodos fechados/consolidados: linhas sólidas, marcadores preenchidos.
   - Períodos parciais/imaturas: linhas tracejadas (`stroke-dasharray`), cores atenuadas, asterisco (`*`).
   - Elemento em foco: traço espesso em tom âmbar/destaque.
4. **Tooltips Flutuantes (`.gtip`):** Elemento único com captura via `hitRect`, posicionado dinamicamente com contenção dentro da viewport.

---

## 5. Tabelas Analíticas

1. **Cabeçalhos Fixos (`position: sticky; top: 0`):** Fundos sólidos com z-index adequado para navegação fluida em grandes volumes.
2. **Formatação Condicional Sem Ruído:** Gradiente de cor calculado proporcionalmente entre a mediana (início da tonalidade) e percentil 97 (p97, saturação máxima), evitando que outliers distorçam a escala.
3. **Ordenação Nativa:** Clique no cabeçalho ordena alternando entre descendente e ascendente.
4. **Sem Cortes Arbitrários:** Evitar truncar linhas por cortes fixos (ex: mínimo 10), permitindo explorar pequenos municípios ou grupos mantendo a consistência.
5. **Exportação Integrada:** Botão direto para download em CSV gerado no cliente via `URL.createObjectURL(new Blob(...))`.

---

## 6. Módulo Geoespacial (Canvas Puro)

1. **Sem Bibliotecas Pesadas:** Projeção Web Mercator calculada matematicamente no Canvas HTML5.
2. **Múltiplos Modos:**
   - Células Agrupadas (grades proporcionais à raiz do volume; agrupadas por cidade em zoom amplo < 9.5).
   - Pontos Simples (individualizados por instalação, coloridos por status).
   - Mapa de Calor (kernel gaussiano offscreen com amortecimento bayesiano `n/(n+6) * √n`).
3. **Ferramenta de Laço Livre (Lasso Tool):** Captura de polígono com algoritmo ray-casting para teste ponto-em-polígono, disparando filtro imediato em todo o painel.
4. **Inferência Espacial Offline:** Resolução de cadastros sem bairro via algoritmo k-NN ponderado pela distância (< 1.2 km) na mesma cidade, mantendo o código original e sinalizando a origem com losangos no mapa.

---

## 7. Padrão Oficial de Cabeçalho e Navegação dos Relatórios

1. **Cabeçalho Minimalista e Exclusivo:**
   - Todo relatório deve conter **estritamente dois controles de ação no cabeçalho**:
     1. Botão **"Voltar ao Catálogo"** (`a.hd-btn.btn-nav-catalog` direcionando para `/`).
     2. Widget do Usuário com identificação e botão **"Sair"** (logout seguro e atômico).
   - **Proibido** adicionar atalhos cruzados para outros relatórios no cabeçalho (ex: links para Churn, FPD, Panorama MS, etc.). Toda navegação transversal deve ocorrer através do catálogo unificado (`/`).
   - **Proibido** link textual redundante `‹ Portal Pephub` no canto superior esquerdo da barra escura `.hd-sub`. O retorno ao catálogo é feito unicamente pelo botão oficial no cabeçalho.

2. **Proibição de Exportar HTML em Relatórios Analíticos:**
   - Relatórios e painéis analíticos não devem conter botões de "Exportar HTML" ou "Download HTML" em seus cabeçalhos ou cards de indicadores.
   - A exportação em formato HTML (.html completo/autônomo) fica **estritamente restrita** às áreas corporativas de Administração e Gestão de Ferramentas (`/admin/` e `/pep-tools/`).
   - Nos relatórios analíticos, a exportação de dados é permitida unicamente em **CSV** gerado no cliente via Blob.

---

## 8. Numeração Sequencial Obrigatória de Indicadores (KPIs)

1. **Rastreabilidade e Clareza Analítica:**
   - Todo cartão ou métrica de KPI deve iniciar obrigatoriamente com sua numeração sequencial: `1. Nome do Indicador`, `2. Taxa...`, `3. Volume...`.
   - Essa convenção elimina qualquer ambiguidade entre gestores, analistas e o assistente de IA ao referenciar métricas em solicitações, diagnósticos e ajustes de código.

---

## 9. Separação Dimensional Estrita: Segmento de Mercado vs. Produto / Plataforma

1. **Vedação a Agrupamentos Ambíguos:**
   - É **estritamente vedado** aglutinar Segmento de Mercado e Produto/Tecnologia em um mesmo seletor (ex: `SEGMENTO / PRODUTO`).
   - São dimensões de negócio ortogonais e independentes:
     - **Segmento de Mercado (Público-Alvo / Portfólio):** Consumo Massivo (PF), PME (PE + ME), Grandes Empresas (GE).
     - **Produto / Plataforma (Tecnologia / Modalidade):** Controle (AUTOC / CTLFC), Pós-pago / Conta, Flex, Pré-pago.
   - Cada dimensão deve possuir seu próprio campo de seleção independente (`.f` com `<label>` próprio e `<select>` ou drawer específico), permitindo que o gestor filtre, por exemplo, "PME" combinado com "Controle", ou analise "Consumo Massivo" para "Pós-pago".
2. **Chips e Resumo Ativo:**
   - Cada filtro ativo deve gerar seu chip individual (`.chip`) com remoção rápida (`×`) e badge contador (`.cnt`).

---

## 10. Arquitetura e Mecânica de Cards e Filtros Padrão Churn Safra

1. **Painel de Filtros Integrado (`#pnFiltros`):**
   - Estrutura em `.panel` com grade `.filters-row` (colunas responsivas `minmax(185px, 1fr)`).
   - Cada item `.f` possui rótulo em caixa alta (`label`), contador de seleção ativa (`.cnt`), seletor estilizado (`select` ou `.drawer-btn`), barra de ações `.fbar` com botão principal (`button.primary`), botão de redefinição (`.fbtn`) e contêiner dinâmico de chips (`.chips`).
2. **Grade Contínua de Cards de KPI (`.panel > h2` + `.kpis`):**
   - Os cards de KPI devem ser encapsulados diretamente dentro de um `.panel` com cabeçalho `h2 Indicadores` (com nota de apoio e botão contextual `?`).
   - Grid contínuo `.kpis` sem espaçamentos desconexos ou sombras externas individuais (`box-shadow: none`).
   - Divisões internas limpas via `border-right: 1px solid var(--line2)` e `border-bottom: 1px solid var(--line2)`.
   - Estrutura de cada cartão `.kpi`:
     - `.k`: Rótulo numerado (`1. Saldo Final`, `2. Adições...`) em `10.5px`, caixa alta, cor `--ink3`.
     - `.v`: Valor principal em `22px`, semibold (`font-weight: 600`), numerais tabulares.
     - `.d`: Detalhamento explicativo em `11px`, cor `--ink3`.
   - Classes de semântica visual para `.v`:
     - `.acc`: Vermelho/alerta (`var(--red)`).
     - `.pos`: Verde/positivo (`var(--green)`).
     - `.np`: Roxo/inadimplência (`var(--purple)`).
     - `.parc`: Fundo suave para períodos parciais (`var(--amber-bg)`).
     - `.pc`: Badge âmbar (`.pc`) de sinalização de dados parciais.


