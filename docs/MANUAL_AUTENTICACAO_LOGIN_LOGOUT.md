# Manual Técnico Corporativo: Fluxo de Autenticação, Sessão e Logout do PEP HUB

**Plataforma Regional Norte — Claro Brasil**  
**Versão**: 3.0.0 | **Data de Publicação**: Outubro/2026  
**Auditoria de Segurança**: AppSec v3 / OWASP ASVS Level 2 / CIS Benchmark

---

## 1. Visão Geral da Arquitetura

O **PEP HUB** adota o modelo arquitetural **Zero Trust Edge Security** implementado sobre **Cloudflare Workers** e banco relacional de borda **Cloudflare D1**.

Toda e qualquer requisição direcionada à raiz (`/`), à Home Page do portal (`/index.html`) ou a qualquer relatório analítico (`/fpd-residencial/`, `/churn/`, `/market-share/`, etc.) é interceptada **antes** de qualquer entrega de byte HTML pelo subsistema de borda do Worker.

```
                      [ NAVEGADOR DO COLABORADOR ]
                                   │
                                   ▼
                   [ Cloudflare Edge / Worker Gateway ]
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
     [ Rota Pública / Asset ]                  [ Rota Protegida (/, /fpd, etc.) ]
     (/login/, /manifest, .png)                         │
              │                                 [ getSessionUser() ]
              ▼                                         │
        [ ASSETS 200 OK ]                     ┌─────────┴─────────┐
                                              ▼                   ▼
                                       [ Sessão Válida ]   [ Expirada / Nula ]
                                              │                   │
                                     [ ASSETS 200 OK ]     [ 302 /login/ ]
                                    (no-store, no-cache)  (Set-Cookie: Max-Age=0)
```

---

## 2. Fluxo de Entrada (Login)

### 2.1 Porta de Entrada Obrigatória
- A partir da versão 3.0.0, **não existe visualização anônima** do portal ou de relatórios.
- Se o usuário acessar `https://pephub.com/`, ele é imediatamente redirecionado via HTTP `302 Found` para `/login/`.
- O parâmetro opcional `?redirect=/caminho/solicitado` preserva o destino original para que, após a autenticação bem-sucedida, o colaborador seja levado diretamente ao relatório que desejava consultar.

### 2.2 Etapas de Autenticação Segura
1. **Envio de Credenciais**:
   - `POST /api/auth/login` transportando `{ login, password }`.
2. **Defesa contra Força Bruta (Brute-Force & Credential Stuffing - CWE-307)**:
   - O Worker consulta a tabela `login_attempts` no D1 por IP e login.
   - Após 5 falhas consecutivas, a conta é bloqueada por **15 minutos** com resposta informativa.
3. **Validação Criptográfica (CWE-916)**:
   - As senhas nunca trafegam nem são armazenadas em texto plano.
   - Utiliza-se derivação de chave **PBKDF2-HMAC-SHA256** com **100.000 iterações** e salt criptográfico individual de 16 bytes gerado via `crypto.getRandomValues()`.
4. **Criação da Sessão**:
   - Gera-se um token de alta entropia (`randomHex(32)` = 256 bits).
   - O registro é inserido no Cloudflare D1 com `expires_at = datetime('now', '+12 hours')`.
   - Um cabeçalho `Set-Cookie` é emitido com diretivas rigorosas:
     - `HttpOnly`: Impede acesso por scripts via JavaScript (mitigação total de XSS token theft).
     - `Secure`: Transmissão obrigatória por canal cifrado HTTPS/TLS 1.3.
     - `SameSite=Lax`: Mitigação nativa de Cross-Site Request Forgery (CSRF).
     - `Path=/`: Válido para todo o ecossistema PEP HUB.
     - `Max-Age=43200`: Expiração de 1 turno operacional (12 horas).
5. **Trilha de Auditoria (CWE-778)**:
   - Registro instantâneo em `access_logs` gravando ID do colaborador, timestamp UTC, IP, localidade geográfica (cidade/UF via Cloudflare Headers) e User-Agent.

---

## 3. Gestão de Inatividade, Tempo Limite e Prevenção de "Acesso Fantasma"

### 3.1 O Problema do Acesso Após Inatividade (Ex: 1 Dia Sem Uso)
No modelo anterior, se um usuário permanecesse inativo por 1 dia, ao tentar navegar para um relatório, ocorria o fenômeno do "acesso fantasma": o Service Worker entregava a página HTML do cache do disco antes que o script fizesse `fetch('/api/auth/me')` para descobrir a expiração.

### 3.2 A Solução Definitiva em Três Camadas

| Camada | Mecanismo de Bloqueio | Comportamento Técnico |
|---|---|---|
| **1. Edge Worker Gateway** | Server-Side Interception | O Worker intercepta a requisição antes de `env.ASSETS.fetch`. Se `datetime(s.expires_at) <= datetime('now')`, retorna imediatamente `302` para `/login/?redirect=...` enviando `Set-Cookie: pephub_session=; Max-Age=0`. |
| **2. Headers Anti-Cache** | Cache-Control Obrigatório | Todas as respostas HTML são servidas com `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`, `Pragma: no-cache` e `Expires: 0`. O navegador nunca guarda o HTML em cache de disco. |
| **3. Service Worker PWA** | Network-Only para HTML | Requisições com `mode: 'navigate'` ou `Accept: text/html` são tratadas estritamente com `Network-Only`. Caches do SW são reservados apenas a ícones, fontes e CSS/JS estáticos imutáveis. |

Com essa blindagem tripla:
- **Dando o tempo limite (12h ou inatividade), o colaborador é 100% deslogado de forma transparente e imediata, sem jamais abrir nenhum relatório antes.**

---

## 4. Fluxo de Saída (Logout Infalível)

### 4.1 Por Que o Botão "Sair" Falhava Anteriormente?
Anteriormente, o botão de logout executava um `fetch('/api/auth/logout')` seguido de `window.location.reload()`. Como a rota raiz `/` não validava a sessão no servidor, o recarregamento entregava a mesma página HTML do portal, criando a impressão de que "nada aconteceu".

### 4.2 Arquitetura do Logout Atômico v3.0

O fluxo atual realiza **5 operações atômicas síncronas**:

```
[ Usuário Clica em "Sair" ]
          │
          ├─► 1. Desabilita botão e exibe feedback ("Saindo...")
          │
          ├─► 2. Dispara postMessage({ type: 'LOGOUT' }) ao Service Worker
          │      └─► O Service Worker purga todos os caches de páginas
          │
          ├─► 3. Limpa Storage do Navegador (sessionStorage e localStorage)
          │
          ├─► 4. Executa POST /api/auth/logout
          │      └─► Exclui a sessão da tabela `sessions` no Cloudflare D1
          │      └─► Envia Set-Cookie de expiração imediata (Max-Age=0)
          │
          └─► 5. Redireciona via window.location.replace('/login/?logout=1')
                 (Fallback automático via GET /logout se a conexão falhar)
```

### 4.3 Endpoint Dual `/logout`
Se por qualquer motivo de rede o JavaScript do frontend falhar, navegar diretamente para `/logout` aciona o Worker na borda, que:
1. Deleta a sessão no D1.
2. Emite o cabeçalho `Set-Cookie: pephub_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; HttpOnly; Secure; SameSite=Lax`.
3. Retorna HTTP 302 redirecionando para `/login/?logout=1`.

---

## 5. Praticidade e Experiência do Colaborador (UX)

1. **Popup Flutuante "Conectado"**:
   - Reposicionado para o **canto inferior direito** (`bottom: 20px; right: 20px;`).
   - Não obstrui cabeçalhos, títulos ou filtros superiores.
   - Animação suave com fade-out após 3,5 segundos, reaparecendo automaticamente caso a rede caia para avisar sobre o modo offline.
2. **Redirecionamento Inteligente**:
   - Links diretos enviados por Teams ou WhatsApp (ex: link de um relatório específico) não se perdem: após digitar o login, o colaborador entra direto no relatório desejado.
3. **Instalação PWA**:
   - Suporte completo a instalação como aplicativo nativo no Windows, Android e iOS.
4. **Sem Perda de Contexto**:
   - Durante o turno de 12 horas, o colaborador pode alternar entre abas, painéis e PeP Tools sem reinserir senha.

---

## 6. Conformidade e Normativas Aplicadas

- **OWASP Top 10**: A01:2021 (Broken Access Control), A07:2021 (Identification and Authentication Failures).
- **CWEs Mitigadas**: CWE-285, CWE-306, CWE-307, CWE-384, CWE-524, CWE-613, CWE-614, CWE-778, CWE-916, CWE-1004, CWE-1275.
- **Auditoria Automatizada**: Integrado aos agentes `security_auditor.py`, `reports_quality_agent.py` e ao `release_gate.py`.
