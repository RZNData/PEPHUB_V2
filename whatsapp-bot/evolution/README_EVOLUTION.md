# 🚀 Guia de Configuração: Evolution API (WhatsApp)

Este guia explica como colocar a **Evolution API v2** rodando para conectar seu WhatsApp ao bot do Pephub.

---

## 📁 Estrutura de Arquivos Criada

* `docker-compose.yml`: Definição dos containers Docker para a Evolution API.
* `.env`: Configurações de porta (`8080`), chave secreta e apontamento automático de Webhook para `http://host.docker.internal:8085/webhook`.
* `evolution_client.py`: Cliente Python de comunicação REST com a API da Evolution.
* `setup_instance.py`: Script de 1 clique que cria a instância `pephub-bot`, conecta e gera o QR Code no navegador.

---

## 🛠️ Passo a Passo para Iniciar (Amanhã)

### 1. Iniciar os Containers da Evolution API
No computador ou servidor com Docker instalado:
```bash
cd whatsapp-bot/evolution
docker compose up -d
```
Aguarde alguns segundos até o container subir na porta `8080`.

### 2. Iniciar o Servidor de Dados do Pephub
Em um terminal (ou segundo terminal):
```bash
cd whatsapp-bot
python server.py
```
O servidor estará ouvindo na porta `8085` e recebendo os webhooks.

### 3. Criar a Instância e Escanear o QR Code
No terminal:
```bash
cd whatsapp-bot/evolution
python setup_instance.py
```
1. O script criará a instância `pephub-bot` e configurará o webhook automaticamente.
2. Uma página HTML (`qr_evolution.html`) abrirá no seu navegador com o QR Code.
3. No seu celular:
   * Abra o WhatsApp > **Aparelhos Conectados** > **Conectar um Aparelho**.
   * Aponte a câmera para o QR Code na tela.

---

## 🎯 Teste no Grupo do WhatsApp

1. Adicione seu número em um grupo de teste.
2. Envie uma mensagem com o comando:
   ```text
   !dados como está Manaus?
   ```
3. O bot responderá instantaneamente com o card formatado de Churn!
