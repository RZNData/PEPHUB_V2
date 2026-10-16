---
name: layout-checker
description: Audita e valida a conformidade de layout, identidade visual e design system dos painéis e relatórios da Regional Norte contra o PADRAO_DESIGN_PAINEIS.md. Versão 2 com 14 verificações ponderadas, suporte a multi-arquivo e scoring por severidade.
---

# Skill: Layout Checker — Auditor de Padronização de Design v2

Agente especializado em garantir a conformidade estética, estrutural e de identidade visual dos painéis PEP HUB contra o `PADRAO_DESIGN_PAINEIS.md`.

## Preferências do Usuário (arthur.rezende)

- **Padrão visual**: Corporativo e sóbrio — sem emojis, sem cores vibrantes fora da paleta, sem CDNs externos.
- **Tipografia**: Segoe UI / Roboto nativo, nunca webfonts externas (Google Fonts, etc.).
- **Identidade**: Gradiente Claro `#8a0f18 → #c0191f → #e23a1e → #f47a1f → #f9b233`, subtítulo "Regional Norte".
- **Componentes obrigatórios**: Gaveta de filtros `.drawer-btn`, helpers `.hlp` com HELP completo, abas `.tabs` com `.on`, cards KPI `.kpi`/`.kpis`.
- **Gráficos**: SVG nativo com `viewBox`, halo branco em rótulos (`paint-order: stroke fill`), tooltips `.gtip`.
- **Zero dependências externas**: nenhum CDN, nenhuma lib de terceiros.

## Como Executar

```bash
# Auditar todos os painéis de uma vez (recomendado)
python scripts/layout_checker_agent.py

# Auditar um painel específico
python scripts/layout_checker_agent.py public/fpd/index.html
python scripts/layout_checker_agent.py public/churn/index.html
python scripts/layout_checker_agent.py public/churn-bl-total/index.html
```

## Verificações Realizadas (18 checks)

| # | Verificação | Severidade | Pontos |
|---|---|---|---|
| 1 | Paleta CSS completa — 14 variáveis incluindo `--purple` e `--blue` | CRITICAL | -20 |
| 2 | Gradiente institucional Claro no cabeçalho | CRITICAL | -20 |
| 3 | Subtítulo "Regional Norte" | WARNING | -5 |
| 4 | Barra de contexto `.hd-sub` | WARNING | -5 |
| 5 | Tipografia Segoe UI / Roboto | WARNING | -5 |
| 6 | KPI 22px com classes `.kpi` / `.kpis` | WARNING | -5 |
| 7 | Ausência de emojis informais | ERROR | -10 |
| 8 | Zero CDNs externos (jsdelivr, unpkg, googleapis, etc.) | CRITICAL | -20 |
| 9 | Helpers `.hlp` todos registrados no dicionário `HELP` | ERROR | -10 |
| 10 | SVG nativo com `viewBox` responsivo | ERROR | -10 |
| 11 | Halo branco em rótulos SVG (`paint-order`) | WARNING | -5 |
| 12 | Tooltips flutuantes `.gtip` em painéis com gráficos | WARNING | -5 |
| 13 | Gaveta de filtros `.drawer-btn` | WARNING | -5 |
| 14 | Exportação CSV no cliente via Blob | INFO | -0 |
| 15 | Tabelas analíticas com ordenação interativa de colunas (.sortable / sortTable) | WARNING | -5 |
| 16 | Padrão Ouro Churn Safra: Estrutura (.panel), Mês Foco (.th-foco) e Histórico (.th-hist-start) | WARNING | -5 |
| 17 | Cabeçalho Padrão Corporativo: Apenas 2 ações ('Voltar ao Catálogo' e 'Sair') para colaborador, e widget '🟢 X Online' dinâmico (com Hover Card) para Administrador | WARNING | -5 |
| 18 | Restrição de Exportação HTML: Proibido download de pacote HTML no cabeçalho e cards (exclusivo do Admin) | ERROR | -10 |
| 19 | Numeração Sequencial de Indicadores: Todo indicador de KPI deve ter prefixo numérico (ex: 1. Instalações) | WARNING | -5 |
| 20 | Botões Padrão Churn Safra: Ação principal (.primary) e Segmented Controls (.tabs com .on) | WARNING | -5 |
| 21 | Alinhamento numérico à direita em todas as linhas e subtotais (.grp-total-row td com text-align: right) | WARNING | -5 |
| 22 | Comparativos de pontos percentuais estritamente em minúsculo ('p.p.', nunca 'P.P.') | WARNING | -5 |
| 23 | Identidade Visual Padronizada dos Modais: Cabeçalho com Gradiente Claro (#8a0f18 a #f9b233), subtítulo corporativo em <small>, botão fechar circular translúcido, e botões de rodapé (.btn-secondary e .btn-primary) sem classes conflitantes | ERROR | -10 |

## Escala de Graus

| Score | Grau | Significado |
|---|---|---|
| 95–100 | **A+** | Conformidade exemplar |
| 85–94 | **A** | Alta conformidade — pronto para deploy |
| 70–84 | **B** | Pontos a corrigir antes do release |
| 55–69 | **C** | Desvios relevantes |
| 0–54 | **D** | Reformulação necessária |

## Integração com o Release Gate

Este agente é executado automaticamente pelo `release_gate.py` antes de todo deploy. Score mínimo exigido: **85/100 (Grau A)**.


### Diretriz Dinâmica Incorporada: Cabecalho_Minimalista_Apenas_Catalogo_E_Sair
- **Regra**: Cabeçalho de relatórios analíticos deve ter apenas botões padronizados ('Voltar ao Catálogo' e 'Sair' para colaboradores; administradores recebem botão executivo '🟢 X Online' em tempo real). Proibido links externos azuis/roxos desformatados, tags estáticas de perfil ou exportar HTML no cabeçalho.
- **Registrado em**: 09/10/2026 14:41:28
