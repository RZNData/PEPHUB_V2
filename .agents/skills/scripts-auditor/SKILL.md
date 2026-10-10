---
name: scripts-auditor
description: Inventaria e classifica os 120+ scripts do diretório scripts/ em categorias (oficiais, diagnósticos temporários, versões antigas, utilitários). Detecta funções duplicadas entre scripts e recomenda limpeza para reduzir débito técnico operacional.
---

# Skill: Scripts Auditor — Inventário e Limpeza do Diretório scripts/

O diretório `scripts/` acumula scripts de diagnóstico, investigação e build ao longo do desenvolvimento. Esta skill mantém o inventário organizado.

## Como Executar

```bash
python scripts/scripts_auditor.py
```

## Categorias de Classificação

| Categoria | Critério | Ação |
|---|---|---|
| **oficial** | Lista allowlist — nunca remover | Manter |
| **utility** | Scripts de build/extração sem prefixo temporário | Avaliar |
| **diagnostic_temp** | Prefixos `check_`, `find_`, `inspect_`, `test_`, `verify_` | Revisar periodicamente |
| **old_version** | Sufixos `_v1`, `_v2`, `_old`, `_bkp`, `_legacy` | Remover |

## Scripts Oficiais (Nunca Remover)

```
layout_checker_agent.py    — Auditoria UX/UI
security_auditor.py        — Auditoria de Segurança
architecture_sanitizer.py  — Auditoria de Arquitetura
release_gate.py            — Gate de deploy
db_optimizer.py            — Otimização de queries D1
scripts_auditor.py         — Este próprio script
extract_churn_data.py      — Pipeline de extração de dados
build_fpd_definitive.py    — Build do painel FPD
generate_fpd_from_churn_safra.py — Gerador de painéis
validate_js_syntax.py      — Validação de sintaxe JS
```

## Workflow de Limpeza Recomendado

```bash
# 1. Ver inventário completo
python scripts/scripts_auditor.py

# 2. Mover scripts obsoletos para arquivo
mkdir -p scripts/archive
# mover versões antigas manualmente

# 3. Consolidar funções duplicadas em utils.py
# (criar scripts/utils.py com helpers compartilhados)
```

## Quando Usar Esta Skill

- Mensalmente para manter o repositório limpo
- Antes de onboarding de novos colaboradores
- Ao identificar que o diretório `scripts/` está com 100+ arquivos
