# 🤖 Pephub WhatsApp Data Bot — Regional Norte

Assistente inteligente para responder dúvidas sobre indicadores de **Churn (Banda Larga Total e PME)**, **Projeções Involuntárias (FPD, Fraude, Suspensão)** e **Call Center / Speech Analytics** diretamente em **Grupos do WhatsApp** ou conversas individuais.

---

## 🚀 Regra de Acionamento (Zero Spam & Privacidade)

Como o bot opera integrado ao seu número do WhatsApp:
1. **Zero Spam:** O bot **não** responde a mensagens casuais, conversas privadas pessoais ou mensagens comuns de grupos.
2. **Gatilho Único Obrigatório:** O bot só é ativado quando a mensagem iniciar estritamente com o prefixo **`#?`**:
   - Exemplo: `#? como está Manaus?`
   - Exemplo: `#? fpd de Belém`
   - Exemplo: `#? 1` (para escolher opções do menu)
3. **Whitelist de Segurança:** No arquivo `config.json`, você pode restringir os grupos autorizados e permissões de privacidade.

---

## 📋 Exemplos de Perguntas Suportadas

O bot possui roteamento inteligente conectado ao Cloudflare D1 e fallback local calibrado:

* **Cidades & Segmentos:**
  * `#? como está Manaus?`
  * `#? qual o churn de Belém em PME?`
  * `#? resumo da Regional Norte`
  * `#? como está Grandes Mercados (GM)?`
  * `#? como está Mercados em Desenvolvimento (MD)?`
* **FPD & Qualidade:**
  * `#? qual a última safra de FPD?`
  * `#? fpd 60 de Belém`
  * `#? quem tem o pior FPD 60?`
  * `#? fpd do parceiro CCH Mendes`
* **Rankings:**
  * `#? quais as piores cidades no orçado?`
  * `#? ranking de cidades em PME`
  * `#? melhores cidades em meta`
* **Involuntário & Fraude:**
  * `#? como está o involuntário da Regional?`
  * `#? involuntário de São Luís`
  * `#? perdas por FPD e Fraude`
* **Call Center & Speech Analytics:**
  * `#? speech analytics de Manaus`
  * `#? quais os principais motivos de cancelamento?`
* **Menu de Ajuda:**
  * `#? ajuda`

---

## 🛠️ Teste Rápido no Terminal (Sem precisar do WhatsApp)

Você pode testar qualquer consulta analítica agora mesmo pelo terminal:

```bash
cd whatsapp-bot
python agent.py "como está Manaus?"
python agent.py "qual o churn de Belém em PME?"
python agent.py "quais as piores cidades no orçado?"
python agent.py "como está o involuntário de São Luís?"
python agent.py "speech analytics de Manaus"
```

---

## 📱 Iniciando a Conexão com o WhatsApp

1. No terminal, dentro da pasta `whatsapp-bot`, execute:
   ```bash
   npm start
   ```
2. Um **QR Code** será exibido no terminal (e também salvo como `qr.html` para abrir no navegador).
3. Abra o WhatsApp no seu celular:
   * **Configurações / Opções** > **Aparelhos Conectados** > **Conectar um Aparelho**.
   * Aponte a câmera para o QR Code.
4. Assim que conectar, a sessão fica salva na pasta `auth_info/` (não precisará escanear de novo nas próximas inicializações).
5. No grupo de teste, envie `!dados como está Manaus?` e receba a resposta formatada!
