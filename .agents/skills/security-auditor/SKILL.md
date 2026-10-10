---
name: security-auditor
description: Agente especialista em segurança corporativa (AppSec & Cloudflare Workers). Audita vulnerabilidades OWASP Top 10, CSP, rate limiting, N+1 DoS, IDOR, RBAC, bot authorization, wrangler exposure, XSS, headers de hardening, Server-Side Gate obrigatório, ciclo de vida de sessão e logout atômico. Versão 3.
---

# Skill: Security Auditor — Especialista em Segurança de Aplicações v3

Agente especialista em segurança da informação e AppSec para Cloudflare Workers, Edge Computing e ecossistema analítico PEP HUB.

---

## Como Executar

```bash
python scripts/security_auditor.py
```

---

## Escopo de Auditoria v3 (Novas Normativas Corporativas)

### 1. Backend e Autenticação (worker/index.js & worker/utils/security.js)
| Check | CWE | Severidade | Descrição / Normativa |
|---|---|---|---|
| **Server-Side Gate na Raiz '/' e Relatórios (NOVO v3)** | CWE-285/306 | CRITICAL | Raiz `/` e páginas HTML de relatórios NUNCA abrem anônimas. Redirecionam 302 imediatamente para `/login/`. |
| **Proibição de Entrega de HTML Pré-Autenticação (NOVO v3)** | CWE-306 | CRITICAL | Nenhum byte de relatório pode ser servido se a sessão no D1 estiver expirada ou inativa. |
| **Headers Anti-Cache em Documentos HTML (NOVO v3)** | CWE-524 | HIGH | Respostas HTML protegidas devem conter `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`. |
| **Logout Atômico e Infalível (NOVO v3)** | CWE-613 | HIGH | POST `/api/auth/logout` e GET `/logout` invalidam D1, enviam `Set-Cookie` com Max-Age=0 e limpam storages. |
| **Expiração e TTL Estrito de Sessão (NOVO v3)** | CWE-613 | HIGH | Sessão corporativa com TTL (12 horas). Sessões expiradas são expurgadas ativamente do D1. |
| SQL Injection via interpolação/concatenação | CWE-89 | HIGH | Uso exclusivo de queries parametrizadas (`.prepare().bind()`). |
| PBKDF2 + Salt de Alta Entropia | CWE-916 | CRITICAL | Derivação com PBKDF2 (100.000 iterações SHA-256) e salt aleatório de 16 bytes. |
| Cookie HttpOnly / Secure / SameSite | CWE-1004/614/1275 | HIGH | Cookies de sessão com flags `HttpOnly; Secure; SameSite=Lax; Path=/`. |
| RBAC guard `is_admin` nas rotas admin | CWE-285 | CRITICAL | Validação server-side estrita de privilégios de usuário. |
| Hardening de Headers (HSTS, CSP, X-Frame-Options) | CWE-693/1021 | MEDIUM | CSP restritivo, HSTS com preload, X-Content-Type-Options: nosniff. |
| Rate Limiting no Login & Brute-Force | CWE-307 | MEDIUM | Bloqueio temporário (15min) após 5 falhas consecutivas de login por IP/usuário. |
| N+1 queries como vetor DoS | CWE-400 | MEDIUM | Agregações SQL consolidadas para evitar esgotamento de CPU e D1 subrequests. |
| Audit logging corporativo (logAccess) | CWE-778 | MEDIUM | Registro em trilha de auditoria com IP, localidade, user-agent e recurso acessado. |
| IDOR em rotas de usuário e uploads | CWE-639 | MEDIUM | Checagem de propriedade de recursos antes de mutações de cadastro. |

### 2. Service Worker e PWA (public/sw.js)
| Check | CWE | Severidade | Descrição / Normativa |
|---|---|---|---|
| **Network-Only para Navegação HTML (NOVO v3)** | CWE-524 | CRITICAL | O Service Worker NUNCA serve relatórios confidenciais de caches obsoletos. Requisições HTML vão direto à rede. |
| **Purga de Cache no Evento de Logout (NOVO v3)** | CWE-384 | HIGH | Ao receber postMessage `{ type: 'LOGOUT' }`, o Service Worker elimina todos os caches locais. |
| **Não Pre-cachear a Raiz '/' (NOVO v3)** | CWE-306 | HIGH | Proibido incluir rotas que exigem login na lista de pré-cache de instalação do PWA. |

### 3. WhatsApp Bot (whatsapp-bot/)
| Check | CWE | Severidade | Descrição / Normativa |
|---|---|---|---|
| Autorização de remetente e RBAC | CWE-285 | HIGH | Validação de número de telefone contra catálogo de usuários aprovados no D1. |
| Ausência de credenciais hardcoded | CWE-798 | CRITICAL | Tokens, chaves e senhas isolados em variáveis de ambiente. |

### 4. Infraestrutura (wrangler.toml)
| Check | CWE | Severidade | Descrição / Normativa |
|---|---|---|---|
| Segredos e Chaves fora de vars | CWE-798 | CRITICAL | Nenhuma API key em texto puro no wrangler.toml. |
| database_id seguro | CWE-312 | LOW | Acesso protegido por bindings autenticados da Cloudflare. |

---

## Escala de Postura de Segurança

| Score | Grau | Postura |
|---|---|---|
| 95–100 | **A+** | Máxima postura defensiva corporativa |
| 85–94 | **A** | Alta postura — aprovado para produção |
| 70–84 | **B** | Hardening recomendado |
| 55–69 | **C** | Vulnerabilidades a corrigir |
| 0–54 | **D** | Riscos severos — deploy bloqueado |

---

## Integração com o Release Gate

Score mínimo exigido: **90/100** para autorizar deploy em produção pelo `release_gate.py`.

---

## Checklist de Conformidade Rápida

1. **Acesso Inicial**: A porta de entrada do domínio é SEMPRE `/login/` para usuários não autenticados.
2. **Tempo Limite**: Ao expirar a sessão (inatividade / 1 dia), o primeiro clique deve redirecionar 302 para login com limpeza de cookies.
3. **Logout**: Botão "Sair" deve executar rotina síncrona/atômica limpando D1, cookies, storages e caches antes do redirecionamento.
4. **HTML Sem Cache**: Documentos HTML não podem ser guardados em cache de disco por navegadores.
