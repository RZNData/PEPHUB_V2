# 🛡️ Guia Oficial de Skills, Agentes e Governança Técnica — PEP HUB

> **Documento Normativo de Engenharia de Software e Garantia de Qualidade**  
> **Plataforma:** PEP HUB — Regional Norte (Claro Brasil)  
> **Objetivo:** Detalhar a finalidade, escopo, regras de pontuação, penalidades e critérios de cada Skill / Agente de Auditoria do projeto.  
> **Versão:** 2.0 (Outubro/2026)

---

## 1. Visão Geral do Framework de Qualidade

Para garantir que a plataforma PEP HUB opere com **altíssimo desempenho, zero custo de infraestrutura desnecessária, segurança corporativa rigorosa e padronização visual perfeita**, o projeto conta com um framework de **6 Skills / Agentes Especializados de Auditoria Estática**.

Esses agentes atuam como "guardiões automatizados", inspecionando o código-fonte antes de qualquer release ou colaboração em equipe:

```
                            ┌────────────────────────────────────────┐
                            │          DESENVOLVEDOR / TIME          │
                            └───────────────────┬────────────────────┘
                                                │
                                                ▼
                            ┌────────────────────────────────────────┐
                            │    scripts/release_gate.py (Skill)     │
                            │      "O Guardião do Pre-Deploy"        │
                            └───────┬───────────┬────────────┬───────┘
                                    │           │            │
             ┌──────────────────────┘           │            └──────────────────────┐
             ▼                                  ▼                                   ▼
┌─────────────────────────┐        ┌─────────────────────────┐        ┌─────────────────────────┐
│     layout-checker      │        │    security-auditor     │        │  architecture-sanitizer │
│  (UX/UI & Design Claro) │        │ (AppSec & Defesa Nuvem) │        │ (7 Pilares & Escalabil.)│
│    Nota Mínima: 85/100  │        │   Nota Mínima: 90/100   │        │   Nota Mínima: 80/100   │
└─────────────────────────┘        └─────────────────────────┘        └─────────────────────────┘
             │                                  │                                   │
             └──────────────────────────────────┼───────────────────────────────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │  DEPLOY HOMOLOGADO    │
                                    │  (wrangler deploy)    │
                                    └───────────────────────┘
```

---

## 2. Tabela Comparativa Consolidada das Skills

| Skill | Tipo / Especialidade | Script Executor | Requisito Release Gate | Nota Atual no Sistema |
|---|---|---|:---:|:---:|
| **`layout-checker`** | UX/UI, Design System & Identidade Claro | `scripts/layout_checker_agent.py` | $\ge 85/100$ (Grau A) | **95/100 (A+)** |
| **`security-auditor`** | AppSec, OWASP Top 10 & Cloudflare Hardening | `scripts/security_auditor.py` | $\ge 90/100$ (Grau A) | **97/100 (A+)** |
| **`architecture-sanitizer`** | Arquitetura, Streams, RAG Readiness & Escalabilidade | `scripts/architecture_sanitizer.py` | $\ge 80/100$ (Grau B) | **94/100 (A+)** |
| **`release-gate`** | Orquestrador Mestre de Deploy | `scripts/release_gate.py` | 100% dos gates aprovados | **APROVADO (A+)** |
| **`db-optimizer`** | Performance de Banco SQLite / Cloudflare D1 | `scripts/db_optimizer.py` | Zero findings HIGH | **Conforme** |
| **`scripts-auditor`** | Inventário & Governança de Scripts ETL | `scripts/scripts_auditor.py` | Higiene operacional | **Conforme** |

---

## 3. Detalhamento Técnico Skill por Skill

---

### 🎨 Skill 1: `layout-checker` (Auditor de Padronização de Design & UX/UI v2)

* **Localização:** `.agents/skills/layout-checker/SKILL.md`
* **Script Executor:** `python scripts/layout_checker_agent.py`
* **Objetivo:** Auditar todos os painéis e relatórios analíticos contra o normativo [`PADRAO_DESIGN_PAINEIS.md`](file:///c:/Users/F138138/DEV/Churn_Safra/PADRAO_DESIGN_PAINEIS.md), assegurando sobriedade corporativa, paleta institucional da Claro e ausência de dependências frágeis.

#### Arquivos Inspecionados:
1. `public/churn/index.html` (Churn Safra 28)
2. `public/churn-bl-total/index.html` (Banda Larga Residencial)
3. `public/churn-bl-pme/index.html` (Banda Larga PME)
4. `public/fpd/index.html` (Painel FPD Regional Norte)

#### As 14 Verificações Ponderadas:
| # | Verificação | Severidade | Penalidade | O que é verificado no código |
|---|---|:---:|:---:|---|
| 1 | **Paleta CSS Completa** | `CRITICAL` | -20 pts | Presença das 14 variáveis CSS no `:root` (incluindo `--purple: #6b4b8a` para inadimplência e `--blue`). |
| 2 | **Gradiente Oficial Claro** | `CRITICAL` | -20 pts | Cabeçalho `.hd-bar` com `linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%)`. |
| 3 | **Subtítulo Regional Norte** | `WARNING` | -5 pts | Presença obrigatória da assinatura territorial "Regional Norte". |
| 4 | **Barra de Contexto (`.hd-sub`)** | `WARNING` | -5 pts | Barra escura de contexto abaixo do header com metadados de safra/posição. |
| 5 | **Tipografia Corporativa** | `WARNING` | -5 pts | Uso de `Segoe UI`, `Roboto` ou `Arial` nativos. Proibido links para Google Fonts. |
| 6 | **KPIs Padronizados** | `WARNING` | -5 pts | Classes `.kpi` / `.kpis` com tipografia grande de 22px para números principais. |
| 7 | **Ausência de Emojis Informais** | `ERROR` | -10 pts | Varredura de unicode: proibido emojis (ex: 🔥, 🚀, 💩). Permitidos apenas símbolos vetoriais sóbrios (`▲ ▼ ▶ ⟳ ⤢ ✎`). |
| 8 | **Zero CDNs Externos** | `CRITICAL` | -20 pts | Proibido qualquer `<script src="https://...">` ou `<link href="https://...">` via CDN. |
| 9 | **Dicionário HELP Contextual** | `ERROR` | -10 pts | Todo botão `.hlp` com atributo `data-h="xyz"` deve possuir entrada correspondente no objeto JavaScript `HELP`. |
| 10 | **SVG com viewBox Responsivo** | `ERROR` | -10 pts | Gráficos SVG devem conter `viewBox` para escalar fluidamente em qualquer tela. |
| 11 | **Halo Branco em Rótulos SVG** | `WARNING` | -5 pts | Propriedade `paint-order: stroke fill` para garantir legibilidade de textos sobrepostos. |
| 12 | **Tooltips Flutuantes (`.gtip`)** | `WARNING` | -5 pts | Contêiner flutuante `.gtip` para exibição de detalhes ao passar o mouse. |
| 13 | **Gaveta de Filtros (`.drawer-btn`)** | `WARNING` | -5 pts | Botão retrátil para não poluir a tela com menus abertos por padrão. |
| 14 | **Visões Críticas Padronizadas** | `ERROR` | -10 pts | Módulos de Dispersão e Risco devem possuir botões de ajuda identificados (`data-h="scatter"` e `data-h="risco"`). |

#### Escala de Classificação:
* **95 a 100:** Grau **A+** (Conformidade Exemplar — Estado Atual: **95/100**)
* **85 a 94:** Grau **A** (Alta Conformidade — Liberado para Deploy)
* **70 a 84:** Grau **B** (Atenção — Pontos a Corrigir)
* **0 a 69:** Grau **C/D** (Reprovado)

---

### 🔒 Skill 2: `security-auditor` (Especialista em Segurança AppSec & Cloudflare v2)

* **Localização:** `.agents/skills/security-auditor/SKILL.md`
* **Script Executor:** `python scripts/security_auditor.py`
* **Objetivo:** Inspecionar vulnerabilidades baseando-se no **OWASP Top 10**, padrões internacionais **CWE** (Common Weakness Enumeration) e hardening do Cloudflare Workers e banco D1.

#### Escopo e Regras Auditadas:

#### A. Backend Serverless (`worker/index.js`):
1. **SQL Injection (`CWE-89` | `HIGH` -20 pts):**
   * *Regra:* Toda instrução SQL no D1 deve usar `env.DB.prepare(sql).bind(...params)`. É proibida concatenação direta de variáveis ou interpolação com template strings.
2. **Criptografia Forte de Senhas (`CWE-916` | `CRITICAL` -25 pts):**
   * *Regra:* Senhas devem ser protegidas via `PBKDF2` com 100.000 iterações, `SHA-256` e salt aleatório único de 16 bytes.
3. **Segurança de Sessão e Cookies (`CWE-1004` / `CWE-614` / `CWE-1275` | `MEDIUM` -10 pts cada):**
   * *Regra:* Os cookies gerados devem obrigatoriamente conter as diretivas `HttpOnly` (mitiga roubo via XSS), `Secure` (somente HTTPS) e `SameSite=Lax` (mitiga CSRF).
4. **Controle de Acesso Baseado em Funções (`CWE-285` | `CRITICAL` -30 pts):**
   * *Regra:* Todas as rotas administrativas `/api/admin/*` devem verificar expressamente o guard `currentUser.is_admin === 1` e `status === 'aprovado'`.
5. **Headers de Defesa HTTP (`CWE-693` / `CWE-1021` / `CWE-319` | `LOW` -5 pts cada):**
   * *Regra:* Presença obrigatória de `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security` (HSTS) e `Permissions-Policy`.
6. **Content-Security-Policy (CSP) (`CWE-693` | `MEDIUM` -10 pts):**
   * *Regra:* Restrição rigorosa: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'`.
7. **Rate Limiting e Defesa Brute-force (`CWE-307` | `MEDIUM` -10 pts):**
   * *Regra:* Bloqueio de 15 minutos após 5 falhas consecutivas em `/api/auth/login` e `/api/auth/forgot-password`, gerenciado na tabela `login_attempts` do D1.
8. **Consultas N+1 como Vetor de DoS (`CWE-400` | `MEDIUM` -10 pts):**
   * *Regra:* Proibido executar subqueries correlacionadas em `access_logs` por usuário. Deve-se consolidar consultas com `LEFT JOIN` e `GROUP BY`.
9. **Trilha de Auditoria (`CWE-778` | `MEDIUM` -10 pts):**
   * *Regra:* Toda ação sensível (login, download, exportação) deve acionar a função `logAccess` com gravação de IP, Localidade, User-Agent e Recurso.
10. **Prevenção de Vazamento de Stack Traces (`CWE-209` | `LOW` -5 pts):**
    * *Regra:* Proibido retornar `err.stack` em respostas de API ao cliente externo.

#### B. WhatsApp Bot (`whatsapp-bot/bot.js`):
1. **Autorização de Remetente (`CWE-285` | `HIGH` -15 pts):** O bot só responde a números previamente homologados no banco D1 (`verifySenderAccess`).
2. **Zero Dependências CDN (`CWE-829` | `LOW` -3 pts):** Proibido carregar scripts externos como `jsdelivr` ou `unpkg`.
3. **Credenciais Hardcoded (`CWE-798` | `CRITICAL` -20 pts):** Nenhuma chave de API ou token em texto puro no código.

#### C. Configuração da Infraestrutura (`wrangler.toml`):
1. **Exposição de Secrets (`CWE-798` | `CRITICAL` -20 pts):** Segredos corporativos devem estar no cofre de segredos da Cloudflare (`wrangler secret put`), nunca na seção pública `[vars]`.

---

### 🏗 Skill 3: `architecture-sanitizer` (Arquiteto de Software & Saneamento Corporativo v2)

* **Localização:** `.agents/skills/architecture-sanitizer/SKILL.md`
* **Script Executor:** `python scripts/architecture_sanitizer.py`
* **Objetivo:** Garantir a saúde arquitetural, a escalabilidade para volumes massivos de dados, o desacoplamento de camadas e a uniformidade entre os módulos da plataforma.

#### Os 7 Pilares Ponderados:
O score final é uma média ponderada dos 7 pilares corporativos:

$$\text{Score Global} = (P_1 \times 0.15) + (P_2 \times 0.10) + (P_3 \times 0.20) + (P_4 \times 0.20) + (P_5 \times 0.10) + (P_6 \times 0.10) + (P_7 \times 0.15)$$

#### 1. Zero Dependências Externas (Peso: 15% | Nota: 100/100)
* Aplicação autossuficiente: não depende de React, Vue, jQuery, Tailwind, Bootstrap, D3 ou Leaflet.
* Todo o desenho gráfico é feito via SVG nativo ou Canvas Mercator em Vanilla JS.

#### 2. Sobriedade & Identidade Visual (Peso: 10% | Nota: 100/100)
* Respeito às variáveis semânticas de cores Claro (`--red`, `--amber`, `--green`, `--blue`, `--purple`).
* Proibição de emojis em ambientes analíticos de diretoria.

#### 3. Performance de Dados Massivos (Peso: 20% | Nota: 100/100)
* **DecompressionStream ('deflate'):** Payloads grandes devem ser comprimidos em Base64 Zlib (reduzindo arquivos em mais de 60%) e descompactados em stream no navegador.
* **Coleções Numéricas em TypedArrays:** Uso de `Uint32Array` e `Float32Array` para armazenamento de volumes e bases, consumindo 5× menos memória RAM no cliente.
* **Estado Unidirecional `sel`:** Um único objeto JavaScript como fonte da verdade dos filtros.
* **Filtros em Passe Único O(N):** Função `refreshAvailability` que recalcula o grafo de filtros em uma única varredura linear.

#### 4. Escalabilidade Backend Cloudflare Workers & D1 (Peso: 20% | Nota: 100/100)
* Prepared statements obrigatórios em 100% das operações SQL.
* Índices cobrindo colunas filtradas (`created_at`, `email_claro`, `recurso`, `user_id`).
* `LIMIT` explícito em listagens para evitar esgotamento de memória no Worker.
* Consultas agregadas eficientes sem subqueries correlacionadas.

#### 5. Higiene & Tamanho de Módulos (Peso: 10% | Nota: 61/100)
* Monitoramento de tamanho de arquivos para evitar monolitos incontroláveis:
  * `worker/index.js`: limite crítico de 2.000 linhas.
  * `public/admin/index.html`: limite crítico de 2.500 linhas.
  * Painéis analíticos: limite crítico de 4.000 linhas.
  * `whatsapp-bot/bot.js`: limite crítico de 600 linhas.
* Detecção de arquivos HTML duplicados na mesma pasta.
* Zero declarações `debugger` em produção.

#### 6. Bot RAG Readiness (Peso: 10% | Nota: 100/100)
* Endpoint `/api/bot/context` publicado no Worker fornecendo os KPIs consolidados.
* Gestão de sessões ativas por remetente (`sessions = new Map()`) com TTL de 10 minutos.
* Mapa estruturado de comandos (`commandHandlers`).
* Fallback offline em arquivo JSON (`whatsapp-bot/context.json`).

#### 7. Conformidade Cruzada Entre Painéis (Peso: 15% | Nota: 100/100)
* Garante que melhorias aplicadas em um painel (ex: `DecompressionStream`, `TypedArrays`, `sel`, `refreshAvailability`) sejam replicadas uniformemente em todos os outros módulos (Churn Safra, FPD, BL Total e BL PME).

---

### 🚦 Skill 4: `release-gate` (O Guardião de Produção Pre-Deploy)

* **Localização:** `.agents/skills/release-gate/SKILL.md`
* **Script Executor:** `python scripts/release_gate.py`
* **Objetivo:** Orquestrar a execução dos 3 auditores em cadeia e determinar se o deploy para o ambiente de produção está autorizado ou bloqueado.

#### Critérios Mínimos Exigidos:
1. `layout-checker` $\ge 85/100$ (Grau A)
2. `security-auditor` $\ge 90/100$ (Grau A)
3. `architecture-sanitizer` $\ge 80/100$ (Grau B)

#### Comportamento no Terminal:
* **Se APROVADO:** Retorna código de saída `exit code 0` e autoriza o comando de deploy.
* **Se BLOQUEADO:** Retorna código de saída `exit code 1`, bloqueia a esteira de publicação e lista exatamente quantos pontos faltam em cada área para atingir a conformidade.

---

### 🗄 Skill 5: `db-optimizer` (Otimizador de Queries Cloudflare D1)

* **Localização:** `.agents/skills/db-optimizer/SKILL.md`
* **Script Executor:** `python scripts/db_optimizer.py`
* **Objetivo:** Inspecionar o código SQL do backend e identificar gargalos e anti-patterns específicos do SQLite distribuído na borda.

#### Principais Padrões Inspecionados:
1. **N+1 Subqueries:** Alerta quando queries internas disparam subconsultas por linha.
2. **SELECT \* em Tabelas Densas:** Alerta quando a query traz colunas desnecessárias, recomendando a projeção seletiva de campos.
3. **LIKE de Sufixo (`LIKE '%termo%'`):** Alerta que o SQLite não utiliza índices B-Tree em buscas com curinga no início, causando Full Table Scan.
4. **Queries sem LIMIT:** Garante que toda query `.all()` tenha paginação controlada para não exceder os limites de tempo de CPU da Cloudflare.
5. **Índices Ausentes:** Recomenda a criação de índices em colunas usadas frequentemente em cláusulas `WHERE`.

---

### 🧹 Skill 6: `scripts-auditor` (Inventário & Governança da Pasta `scripts/`)

* **Localização:** `.agents/skills/scripts-auditor/SKILL.md`
* **Script Executor:** `python scripts/scripts_auditor.py`
* **Objetivo:** Catalogar e classificar os scripts da pasta `scripts/`, impedindo o acúmulo desordenado de arquivos temporários e detectando funções duplicadas.

#### As 4 Categorias de Scripts:
1. **`oficial` (Allowlist):** Scripts vitais de build e agentes de auditoria. **Nunca devem ser removidos.**
   * `release_gate.py`, `security_auditor.py`, `architecture_sanitizer.py`, `layout_checker_agent.py`, `db_optimizer.py`, `scripts_auditor.py`, `build_fpd_definitive.py`, `generate_churn_reports.py`.
2. **`utility`:** Scripts utilitários de suporte e pipelines auxiliares.
3. **`diagnostic_temp`:** Scripts com prefixos `check_`, `find_`, `inspect_`, `test_` criados para diagnósticos rápidos. Devem ser revisados periodicamente.
4. **`old_version`:** Arquivos com sufixos `_v1`, `_v2`, `_old`, `_bkp`, `_legacy`. Podem ser arquivados ou descartados com segurança.

---

## 4. Como Executar a Bateria de Testes em Modo Colaborativo

Para você ou seu amigo colaborador validarem o sistema completo em menos de 1 minuto, basta rodar a sequência no terminal:

```bash
# 1. Auditoria Visual e de Design (UX/UI)
python scripts/layout_checker_agent.py

# 2. Auditoria de Segurança Corporativa (AppSec)
python scripts/security_auditor.py

# 3. Auditoria de Arquitetura e Performance Massiva
python scripts/architecture_sanitizer.py

# 4. Auditoria de Queries D1
python scripts/db_optimizer.py

# 5. O Grande Portão de Homologação (Release Gate)
python scripts/release_gate.py
```

Se o `release_gate.py` retornar `DEPLOY AUTORIZADO`, o sistema estará **100% pronto para subir para a nuvem**:

```bash
npx wrangler deploy
```
