# Diretrizes Estritas de Padronização de Layout — Regional Norte

Este documento define as regras obrigatórias de design e layout para qualquer relatório ou painel analítico da Regional Norte.

## 1. Estrutura de Painel (.panel)
- Todo componente ou bloco visual analítico deve estar encapsulado dentro de um elemento com a classe `.panel`.
- O cabeçalho deve conter:
  - Uma tag `<h2>` com o título do relatório/visão em maiúsculas (`text-transform: uppercase` ou caixa alta no texto).
  - Uma nota descritiva explicativa em `<span class="note">...</span>`.
  - Um botão de ajuda contextual alinhado à direita com a classe `.hlp` e o atributo `data-h="nome_do_topico"`.
- O identificador `data-h` DEVE obrigatoriamente possuir uma entrada explicativa no dicionário central `HELP` do JavaScript.

## 2. Abas e Alternâncias (.tabs)
- Todos os controles de seleção de dimensão ou modo devem utilizar a classe `.tabs`.
- Os botões internos devem ser `<button class="" data-algo="...">Texto</button>`.
- O botão ativo deve conter unicamente a classe `.on` (`background: var(--nav); color: #fff`).

## 3. Cores Semânticas
- Nunca utilizar cores inline arbitrárias ou genéricas.
- Respeitar estritamente a semântica:
  - `--red` (`#c0392b`): Inadimplência, aumento de taxa (piora), cancelamento.
  - `--green` (`#2f7d5d`): Adimplência, redução de taxa (melhora), contratos em dia.
  - `--amber` (`#c98a15`): Safra foco, dados em maturação/parciais, atenção.
  - `--blue` (`#2a5d8f`): Seleções e links ativos.
  - `--nav` (`#1b2430`): Fundo de destaques, barras e botões ativos.

## 4. Tabelas e Tipografia
- Tipografia oficial: `'Segoe UI', Arial, sans-serif`.
- Colunas textuais alinhadas à esquerda (`.l`).
- Colunas numéricas alinhadas à direita.
- Cabeçalhos ordenáveis com `.sortable`.
