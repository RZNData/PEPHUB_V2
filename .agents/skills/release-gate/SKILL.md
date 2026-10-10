---
name: release-gate
description: Orquestra todos os agentes de auditoria (layout, segurança, arquitetura) e só autoriza deploy se todos atingirem as notas mínimas corporativas. Use antes de qualquer wrangler deploy ou push para produção.
---

# Skill: Release Gate — Checklist Pre-Deploy Corporativo

Executa os 3 agentes de auditoria em sequência e retorna status de **APROVADO** ou **BLOQUEADO** para o deploy.

## Como Usar

```bash
# Executar todos os gates de qualidade
python scripts/release_gate.py

# Integrar no pipeline de deploy
python scripts/release_gate.py && wrangler deploy
```

## Notas Mínimas de Aprovação

| Agente | Nota Mínima | Grau |
|---|---|---|
| Layout & UX/UI | 85/100 | A |
| Segurança AppSec | 90/100 | A |
| Arquitetura | 80/100 | B |

## Fluxo de Deploy Recomendado

```bash
# 1. Auditar qualidade antes do deploy
python scripts/release_gate.py

# 2. Otimizar queries D1
python scripts/db_optimizer.py

# 3. Inventariar scripts obsoletos
python scripts/scripts_auditor.py

# 4. Deploy (somente se gate aprovado)
wrangler deploy
```

## Comportamento

- `exit code 0` → deploy autorizado
- `exit code 1` → deploy bloqueado — lista os gates reprovados com delta de pontos necessário

## Quando Usar Esta Skill

- Antes de qualquer `wrangler deploy`
- Antes de merge de PRs com mudanças no worker ou painéis
- Como verificação semanal de conformidade do sistema
