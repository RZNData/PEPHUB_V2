---
name: skills-meta-orchestrator
description: Skill orquestradora e líder de governança do ecossistema de agentes. Gerencia a equipe de skills, audita a consistência cruzada entre diretrizes, detecta contradições normativas entre agentes e assegura que todas as skills falem a mesma língua corporativa.
---

# Skill: Skills Meta-Orchestrator — Líder de Governança e Orquestração de Agentes v1.0

Agente orquestrador e maestro do ecossistema de inteligência do PEP HUB. Supervisiona a equipe de agentes e skills, assegurando harmonia normativa, eliminação de contradições e execução disciplinada de cada especialista.

---

## Como Executar

```bash
# Executar a governança completa e auditoria cruzada da equipe de skills
python scripts/skills_meta_orchestrator.py
```

---

## Papel e Atribuições do Orquestrador

Enquanto o `release_gate` tem a função estrita de aprovar ou reprovar deploys operacionais, o **Skills Meta-Orchestrator** opera como o **Gerente de Governança e Qualidade Normativa** da equipe de agentes:

```
                  ┌─────────────────────────────────────┐
                  │      SKILLS META-ORCHESTRATOR       │
                  │   (Governança & Coerência Cruzada)  │
                  └──────────────────┬──────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
[ SEGURANÇA & ACESSO ]      [ DADOS & QUALIDADE ]       [ ARQUITETURA & DEPLOY ]
 • security-auditor          • reports-quality-auditor   • architecture-sanitizer
 • system-integrity-auditor  • layout-checker            • release-gate
                             • sync-bot-reports          • db-optimizer / scripts
```

---

## 5 Pilares de Governança Inter-Skills

### 1. Detecção de Contradições Normativas (Non-Contradiction Matrix)
O orquestrador audita cruzadamente as instruções das skills para garantir que nenhuma normativa colida com outra:
- **Zero CDNs vs Bibliotecas Externas**: Se `security-auditor` e `layout-checker` exigem zero CDNs, nenhuma outra skill pode prescrever bibliotecas de terceiros.
- **Segurança vs Experiência**: A exigência de Server-Side Gate e anti-cache no `security-auditor` deve ser respeitada e suportada pelo `system-integrity-auditor` e `layout-checker`.
- **Formatação de Dados**: A notação `p.p.` estritamente em minúsculo do `reports-quality-auditor` deve ser validada harmoniosamente em todas as visões sem quebrar scripts analíticos.

### 2. Correspondência Funcional (Skill-to-Script Binding)
- Toda skill registrada em `.agents/skills/<skill-name>/SKILL.md` **deve possuir script automatizado e executável** correspondente no diretório `scripts/`.
- Proíbe a existência de "skills zumbis" (documentadas mas sem execução prática) ou "scripts órfãos" (executáveis sem documentação de propósito).

### 3. Taxonomia e Escala Padronizada
Todas as skills da equipe devem adotar a mesma taxonomia corporativa:
- **Pontuação**: Base 100 pontos (Score 0 a 100).
- **Escala de Graus**:
  - `A+`: 95–100 (Exemplar / Postura Máxima)
  - `A` : 85–94  (Conforme / Pronto para Produção)
  - `B` : 70–84  (Aprovado com Ressalvas / Melhorias Sugeridas)
  - `C/D`: <70   (Reprovado / Bloqueante)
- **Exit Codes**: `0` para Aprovação, `1` para Pendência ou Bloqueio.

### 4. Gestão da Equipe de Skills
O orquestrador inventaria e supervisiona ativamente:
1. `security-auditor` (AppSec, OWASP, Hardening)
2. `system-integrity-auditor` (Estabilidade, Login, Logout, Gating, Rotas)
3. `reports-quality-auditor` (Subtotais, Tabelas, Deltas, Benchmarks)
4. `layout-checker` (Design System, Gradiente Claro, Segoe UI, SVGs)
5. `architecture-sanitizer` (Escalabilidade, D1, N+1, Zero Deps)
6. `sync-bot-reports` (Sincronização de Dados com Bot WhatsApp)
7. `scripts-auditor` (Saneamento e Débito Técnico Operacional)
8. `db-optimizer` (Otimização de Índices e Performance D1)
9. `release-gate` (Orquestração de Pre-Deploy)

### 5. Índice de Harmonia Inter-Skills (IHI)
O orquestrador calcula o **IHI (0 a 100%)** baseado em:
- Alinhamento de diretrizes entre agentes (peso 40%).
- Cobertura de scripts executáveis (peso 30%).
- Consistência de notas mínimas no Release Gate (peso 30%).

### 6. Auto-Incorporação e Expansão Dinâmica por Prompt (Continuous Prompt Directive Ingestion)
Sempre que uma nova demanda, regra ou funcionalidade for solicitada via prompt pelo usuário:
- **Detecção & Classificação Automática**: O Orquestrador analisa o prompt e identifica a qual pilar ou skill a nova função/regra pertence (ex: Layout, Segurança, Qualidade, Integridade ou Arquitetura).
- **Auto-Registro Normativo**: Insere a regra automaticamente no mapa de checagem do orquestrador e no `SKILL.md` do especialista responsável.
- **Checagem de Não-Contradição Prévia**: Antes de registrar, o Orquestrador verifica se a nova diretriz colide com alguma regra pétrea existente (ex: Zero CDNs, soberania corporativa).
- **Vínculo com Script Auditor**: Atualiza os testes automatizados da skill para que a nova função passe a ser cobrada e pontuada nas auditorias seguintes.

---

## Escala do Índice de Harmonia (IHI)

| IHI | Estado da Equipe | Significado |
|---|---|---|
| **95–100%** | **Sinfonia Perfeita** | Skills 100% alinhadas, sem contradições e totalmente automatizadas |
| **85–94%**  | **Harmonia Operacional**| Alta coesão — equipe apta a operar em produção |
| **70–84%**  | **Divergência Leve**   | Ajustes de documentação ou pequenos conflitos de regras |
| **<70%**    | **Ruído Normativo**    | Contradições severas entre skills — requer alinhamento imediato |

