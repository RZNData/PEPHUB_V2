---
name: system-integrity-auditor
description: Agente especialista em estabilidade operacional e integridade do sistema. Audita fluxos de cadastro, login, logout atômico, bloqueios, permissões granulares, integridade de rotas, importações do Worker e resiliência das políticas de sessão e cache.
---

# Skill: System Integrity Auditor — Auditor de Estabilidade e Integridade Operacional v2.1

Agente especialista encarregado de verificar a consistência estrita de todos os fluxos críticos de acesso, roteamento, permissões e estabilidade da plataforma PEP HUB.

---

## Como Executar

```bash
# Executar a auditoria completa de integridade
python scripts/system_integrity_agent.py
```

---

## 10 Pilares de Integridade do Sistema

### 1. Integridade de Importações e Símbolos do Worker (Zero ReferenceErrors)
- **Regra**: Todo método e função utilitária invocado nos sub-roteadores (`routes/auth.js`, `routes/admin.js`, `routes/tv.js`, `routes/uploads.js`, `index.js`) **DEVE estar explicitamente importado**.
- **Checagem estrita**: Prevenir falhas em tempo de execução como `randomHex is not defined`, `parseCookies is not defined`, `createSession is not defined`.

### 2. Ciclo de Vida de Autenticação & Cadastro Padronizado
- **Cadastro Corporativo**:
  - `nome_completo`, `login_claro`, `area`, `funcao` **estritamente em MAIÚSCULO**.
  - `email_claro` **integralmente em minúsculo**.
  - `password` **preservada à risca** conforme escolha do colaborador.
- **Máscara de Telefone**:
  - Permite apagar livremente com Backspace sem re-injetar delimitadores ou travar ao ultrapassar 5 dígitos.
- **Logout Atômico**:
  - Eliminação de sessões no D1, envio de `Set-Cookie: Max-Age=0`, descarte de Storages locais e purga de cache no Service Worker.

### 3. Server-Side Gate & Porta de Entrada Única
- **Regra**: A rota raiz `/`, `/index.html` e todas as rotas de relatórios (`/churn*`, `/fpd*`, `/panorama*`, `/market-share*`, etc.) interceptam usuários anônimos ou com sessão expirada, redirecionando via HTTP 302 diretamente para `/login/`.
- **Proibição**: Nenhuma página analítica pode ser entregue a usuários deslogados.

### 4. Gestão de Inatividade, TTL e Prevenção de Cache Stale
- **Expiração**: Sessões no D1 limitadas a 12 horas.
- **Headers Anti-Cache**: Todas as respostas HTML devem conter `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`.
- **Service Worker**: Navegações HTML usam obrigatoriamente **Network-Only**.

### 5. Controle de Acesso, RBAC e Status de Usuário
- **Status do Usuário**:
  - `aprovado`: acesso liberado aos módulos permitidos.
  - `pendente`: bloqueado com aviso amigável de autorização pendente.
  - `bloqueado` / `rejeitado`: acesso revogado imediatamente.
- **Isolamento Administrativo**: Rotas `/admin/*` e `/api/admin/*` protegidas por checagem estrita de `user.is_admin`.

### 6. Travas e Controles Globais do Sistema (System Controls & Killswitches)
- **Interruptores Mestres Canônicos**:
  - `suspend_emails`: Pausa temporariamente todos os e-mails automáticos enviados pela plataforma (notificações de cadastro, aprovações e comunicados).
  - `suspend_portal_access`: Bloqueia temporariamente o acesso de colaboradores aos painéis e ferramentas com mensagem corporativa de manutenção programada (503). Administradores continuam com acesso total.
  - `suspend_whatsapp_bot`: Pausa e bloqueia temporariamente o Assistente Analítico RAG no portal web e o Bot corporativo no WhatsApp com mensagem de manutenção programada. Administradores mantêm acesso para testes com aviso informativo de suspensão.
  - `suspend_tv_submissions`: Pausa a submissão de novas imagens e vídeos pelos colaboradores no painel de Divulgação Corporativa, mantendo a grade atual em exibição.
- **Resiliência e Performance**:
  - Leitura ultra-rápida via cache in-memory (`_systemControlsCache`) de 30 segundos, purgado imediatamente após qualquer alteração via `invalidateSystemControlsCache()`.
  - Tratamento de aliases canônicos: `suspend_bot` mapeado transparentemente para `suspend_whatsapp_bot`.
- **Garantia de Não-Bloqueio do Gestor (Admin Bypass)**:
  - Todas as travas preservam o acesso de credenciais `is_admin = 1` para permitir auditoria, manutenção e testes ao vivo.
- **Auditoria Transparente**:
  - Todas as ativações e desativações de travas registram logs com matrícula e nome do gestor em `access_logs` (`ADMIN_SYSTEM_CONTROL:<key>:<val>`).

### 7. Padronização Institucional de Cabeçalhos e Monitoramento de Sessões Ativas
- **Componente Oficial**: Todos os relatórios analíticos devem integrar `/js/header-widget.js` e o botão padronizado `btn-nav-catalog`.
- **Experiência do Colaborador**: Cabeçalho estritamente com `Voltar ao Catálogo` e `Sair`, sem tags de perfil (`Nome (ÁREA)`) e sem links desformatados azuis/roxos sublinhados.
- **Experiência do Administrador**: Botão executivo dinâmico `🟢 X Online` exibindo em tempo real quem está conectado no D1, com **Hover Card interativo** listando colaboradores ao passar o mouse, fuso horário de Brasília (UTC-3), botão `Admin` e `Sair`.

### 8. Proteção de Limite de CPU no Cloudflare Workers (Free Tier 10ms)
- **Fast Static Bypass**: Requisições de arquivos estáticos (`.css`, `.js`, imagens, fontes) são interceptadas no topo de `worker/index.js` e entregues via `env.ASSETS.fetch()` sem execução de lógica D1 (<0.2ms de CPU).
- **Sem Overhead em Segundo Plano**: Proibido `ctx.waitUntil(ensureAppSchema(env))` em requisições de leitura ou assets estáticos.
- **Criptografia Otimizada**: Hash PBKDF2 balanceado em 30.000 iterações com fallback transparente para 100.000 iterações em credenciais legadas.

### 9. Integridade Sintática de Scripts nos Painéis Analíticos
- **Regra**: Todos os arquivos HTML de relatórios analíticos devem possuir estrutura sintática 100% balanceada, sem tags `<script>` aninhadas acidentalmente ou blocos de código abertos sem fechamento.
- **Prevenção**: Elimina falhas catastróficas de execução JavaScript que impedem carregamento de dados em tela (ex: FPD Residencial).

### 10. Gestão Precisa de Privilégios & Status em `/api/auth/me`
- **Prevenção de Falso Logout**: O endpoint `/api/auth/me` obrigatoriamente retorna `status: user.status || 'aprovado'`. O `header-widget.js` nunca desloga sessões legítimas.
- **Nomenclatura Estrita de Ações**: Fim do botão "Configurar Acessos". A gestão de relatórios é realizada exclusivamente através do botão oficial **`Privilégios`**.
- **Indicação de Conexão em Tempo Real**: Tanto na aba de Colaboradores quanto no Panorama / Stats, os usuários exibem tags dinâmicas `🟢 Online` ou `⚪ Offline`.
- **Zero Flicker**: Leitura síncrona do cache local de módulos em `sessionStorage` ao carregar o catálogo de relatórios, com suporte a `normalizeModuleId` em todos os nós da aplicação.

---

## Tabela de Pontuação por Severidade (100 pontos base)

| # | Pilar Auditado | Severidade | Impacto |
|---|---|---|---|
| 1 | Símbolos não importados no Worker (ReferenceError) | CRITICAL | -30 |
| 2 | Normalização de Cadastro (MAIÚSCULO/minúsculo) | HIGH | -15 |
| 3 | Máscara de Telefone funcional com Backspace | MEDIUM | -10 |
| 4 | Server-Side Gate na Raiz e Relatórios | CRITICAL | -25 |
| 5 | Anti-cache em HTML e Service Worker Network-Only | HIGH | -15 |
| 6 | Travas e Controles Globais do Sistema (System Controls & Killswitches) | HIGH | -20 |
| 7 | Cabeçalho Padronizado e Header-Widget | HIGH | -15 |
| 8 | Otimização de CPU Worker e Fast Static Bypass | HIGH | -15 |
| 9 | Integridade Sintática de Scripts nos Relatórios | CRITICAL | -20 |
| 10 | Status em /api/auth/me, Botão 'Privilégios' e Hover Online | HIGH | -15 |

---

## Escala de Classificação

- **A+ (95–100%)**: Integridade exemplar e estabilidade total.
- **A (85–94%)**: Aprovado para produção.
- **B/C/D (<85%)**: Bloqueio de deploy pelo Release Gate.

---

### Diretrizes Dinâmicas Incorporadas:
1. **Validacao_Input_Cadastro_Uppercase**: Campos cadastrais em MAIÚSCULO exceto email (minúsculo) e senha livre.
2. **Cabecalho_Estrito_E_Monitoramento_Ativos**: Cabeçalho de relatórios com 'Voltar ao Catálogo' e 'Sair' para colaboradores; administradores possuem botão '🟢 X Online' com Hover Card em tempo real no fuso de Brasília.
3. **Gestao_Privilegios_Zero_Flicker**: Acesso a relatórios salvo individualmente sem herança indesejada, rotulado estritamente como 'Privilégios', com Toast de confirmação e tags '🟢 Online'/'⚪ Offline' em Colaboradores e Panorama.
4. **Protecao_CPU_Worker_Free_Tier**: Fast bypass na borda para static assets garantindo conformidade com limites de CPU da Cloudflare.
5. **Integridade_Sintatica_Scripts**: Proibido tags `<script>` aninhadas ou blocos abertos dentro de HTML de relatórios analíticos.
