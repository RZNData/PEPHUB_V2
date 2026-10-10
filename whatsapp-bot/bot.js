/**
 * Pephub WhatsApp Data Bot — Conector Baileys
 * Permite que um número existente do WhatsApp responda a dúvidas sobre os dados
 * dentro de um Grupo ou conversa privada.
 */

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  Browsers,
} = require("@whiskeysockets/baileys");
const { Boom } = require("@hapi/boom");
const pino = require("pino");
const qrcode = require("qrcode-terminal");
const fs = require("fs");
const path = require("path");
const { execFile } = require("child_process");

const CONFIG_PATH = path.join(__dirname, "config.json");
const AUTH_DIR = path.join(__dirname, "auth_info");
const { saveQrHtml, savePairingCodeHtml, QR_HTML_PATH } = require("./qr_helper");

let config = {
  allowed_groups: ["*"],
  require_trigger_in_groups: true,
  require_trigger_in_private: true,
  allow_self_messages: true,
  trigger_prefixes: ["#?"],
  respond_to_private: true,
  typing_delay_ms: 0,
  python_executable: "python",
};

if (fs.existsSync(CONFIG_PATH)) {
  try {
    config = { ...config, ...JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8")) };
  } catch (e) {
    console.error("[Config] Erro ao ler config.json, usando padrões:", e);
  }
}

// Limpeza segura de credenciais obsoletas/corrompidas
function wipeAuthInfo() {
  if (fs.existsSync(AUTH_DIR)) {
    try {
      const files = fs.readdirSync(AUTH_DIR);
      for (const f of files) {
        try {
          fs.unlinkSync(path.join(AUTH_DIR, f));
        } catch (_) {}
      }
      console.log("[Auth Reset] Pasta auth_info limpa para novo pareamento via QR Code.");
    } catch (e) {
      console.error("[Auth Reset Error]", e.message);
    }
  }
}

// Verificação proativa de inicialização: se creds.json tiver registered: false, limpa antes de travar
const credsFile = path.join(AUTH_DIR, "creds.json");
if (fs.existsSync(credsFile)) {
  try {
    const credsData = JSON.parse(fs.readFileSync(credsFile, "utf-8"));
    if (credsData && credsData.registered === false) {
      console.log("[Init Check] creds.json possui registered: false. Resetando credenciais para permitir novo pareamento...");
      wipeAuthInfo();
    }
  } catch (_) {}
}

// Rastreamento de mensagens enviadas pelo próprio bot para prevenir loops de eco
const botSentMessageIds = new Set();

// Gestão de Sessões Conversacionais (RAG Readiness)
const sessions = new Map();
const SESSION_TTL_MS = 10 * 60 * 1000; // 10 min

function getOrCreateSession(jid) {
  const now = Date.now();
  if (sessions.has(jid)) {
    const s = sessions.get(jid);
    if (now - s.lastSeen < SESSION_TTL_MS) {
      s.lastSeen = now;
      return s;
    }
  }
  const newSession = { history: [], lastSeen: now, conversationState: {} };
  sessions.set(jid, newSession);
  return newSession;
}

// Mapa estruturado de comandos (RAG Readiness)
const commandHandlers = {
  '/churn': async (query) => executeAgent(`churn ${query}`),
  '/fpd': async (query) => executeAgent(`fpd ${query}`),
  '/ajuda': async () => executeAgent('menu'),
  '/menu': async () => executeAgent('menu'),
  '/status': async () => "Sistema operacional. Conectado ao PEP HUB.",
};

// Validação e Autorização de Telefones (Auth Helper)
const { verifySenderAccess, fetchAuthorizedPhones } = require("./auth_helper");

async function executeAgent(query, senderPhone = "") {
  const workerBaseUrl = config.pephub_api_url || config.worker_url || process.env.WORKER_URL || "https://pephub.cloud";
  const workerAskUrl = `${workerBaseUrl.replace(/\/$/, "")}/api/bot/ask`;
  const t0 = Date.now();

  // 1. Tentativa Primária: Cloudflare Worker RAG Router (Text-to-SQL + Semantic RAG)
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000); // 45s de margem segura

    const res = await fetch(workerAskUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: senderPhone, query: query }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    const elapsed = Date.now() - t0;
    if (res.ok) {
      const data = await res.json();
      if (data && data.answer) {
        console.log(`[Worker RAG] Resposta recebida em ${elapsed}ms (Intenção: ${data.intent || 'OK'} | FastPath: ${Boolean(data.fastPath)})`);
        return data.answer;
      }
    } else {
      console.warn(`[Worker RAG Warn] Status HTTP ${res.status} em ${elapsed}ms, acionando fallback local...`);
    }
  } catch (err) {
    const elapsed = Date.now() - t0;
    console.warn(`[Worker RAG Offline/Timeout] (${err.message}) após ${elapsed}ms. Acionando fallback local Python...`);
  }

  // 2. Fallback Secundário: Motor Local Python (agent.py)
  return new Promise((resolve) => {
    const scriptPath = path.join(__dirname, "agent.py");
    const py = config.python_executable || "python";

    execFile(
      py,
      [scriptPath, query],
      {
        cwd: __dirname,
        encoding: "utf-8",
        env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      },
      (error, stdout, stderr) => {
        if (error) {
          console.error("[Local Agent Error]", stderr || error);
          resolve("⚠️ Ocorreu um erro ao processar sua consulta. Tente novamente em instantes.");
        } else {
          resolve((stdout || "").trim());
        }
      }
    );
  });
}

async function startBot() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  console.log(`\n🚀 [Pephub Bot] Iniciando conector WhatsApp (Baileys v${version.join(".")})...`);

  const sock = makeWASocket({
    version,
    logger: pino({ level: "silent" }),
    printQRInTerminal: false,
    auth: state,
    browser: Browsers.ubuntu("Chrome"),
    syncFullHistory: false,
    keepAliveIntervalMs: 25000,
    defaultQueryTimeoutMs: 60000,
    connectTimeoutMs: 60000,
    markOnlineOnConnect: false,
    generateHighQualityLinkPreview: false,
  });

  sock.ev.on("creds.update", saveCreds);

  const usePairingCode = Boolean(config.use_pairing_code);
  const pairingPhone = String(config.pairing_phone || "").replace(/\D/g, "");

  if (usePairingCode && pairingPhone && !sock.authState.creds.registered) {
    setTimeout(async () => {
      try {
        console.log(`\n[Pairing Code] Solicitando código de pareamento para o número +${pairingPhone}...`);
        const code = await sock.requestPairingCode(pairingPhone);
        const formattedCode = code.length === 8 ? `${code.slice(0, 4)}-${code.slice(4)}` : code;
        console.log("\n=======================================================");
        console.log(`🔑 CÓDIGO DE PAREAMENTO DO WHATSAPP: ${formattedCode}`);
        console.log(`📱 Telefone: +${pairingPhone}`);
        console.log("No celular: WhatsApp > Aparelhos Conectados > Conectar um aparelho > Conectar com número de telefone");
        console.log(`Página visual gerada em: ${QR_HTML_PATH}`);
        console.log("=======================================================\n");
        savePairingCodeHtml(code, pairingPhone);
      } catch (err) {
        console.error("[Erro ao gerar Pairing Code]:", err.message || err);
      }
    }, 3000);
  }

  let isReconnecting = false;

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr && !usePairingCode) {
      console.log("\n[QR CODE] Escaneie o QR Code abaixo com seu WhatsApp:");
      console.log("   (WhatsApp > Aparelhos Conectados > Conectar um aparelho)\n");
      qrcode.generate(qr, { small: true });
      await saveQrHtml(qr);
      console.log(`\nTambem foi gerada uma pagina visual com QR Code em: ${QR_HTML_PATH}\n`);
    }

    if (connection === "close") {
      const statusCode =
        lastDisconnect?.error instanceof Boom
          ? lastDisconnect.error.output?.statusCode
          : lastDisconnect?.error?.output?.statusCode;
      const isLoggedOut = statusCode === DisconnectReason.loggedOut;
      const errMsg = lastDisconnect?.error?.message || "";
      const isPrecondition = errMsg.includes("Precondition") || errMsg.includes("Connection Terminated") || statusCode === 428 || statusCode === 401;

      console.log(
        `\n[Conexao Encerrada] Codigo: ${statusCode || "desconhecido"} (${errMsg || "Sem mensagem detalhada"})`
      );

      // Se a sessão expirou ou foi desconectada no celular, limpa as credenciais inválidas para emitir um novo QR
      if (isLoggedOut || isPrecondition || (state.creds && state.creds.registered === false)) {
        console.log(
          "[Sessao Expirada / Desconectada] WhatsApp requer novo pareamento. Limpando credenciais antigas e gerando QR Code..."
        );
        wipeAuthInfo();
        if (isReconnecting) return;
        isReconnecting = true;
        setTimeout(() => {
          isReconnecting = false;
          startBot();
        }, 2000);
        return;
      }

      if (!isLoggedOut) {
        if (isReconnecting) return;
        isReconnecting = true;
        const delayMs = statusCode === DisconnectReason.restartRequired ? 1500 : 3500;
        console.log(`[Auto-Reconexao] Reconectando automaticamente em ${delayMs / 1000}s...`);
        setTimeout(() => {
          isReconnecting = false;
          startBot();
        }, delayMs);
      }
    } else if (connection === "connecting") {
      console.log("[WhatsApp] Estabelecendo conexao com os servidores...");
    } else if (connection === "open") {
      console.log("\n[CONECTADO COM SUCESSO AO WHATSAPP]");
      console.log("O Bot de Dados do Pephub esta ativo e ouvindo mensagens.");
      console.log("Voce pode enviar consultas diretamente no chat.\n");
      if (fs.existsSync(QR_HTML_PATH)) {
        try { fs.unlinkSync(QR_HTML_PATH); } catch (_) {}
      }
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    for (const msg of messages) {
      if (!msg.message) continue;

      // Evita responder a mensagens geradas e enviadas pelo próprio bot
      if (botSentMessageIds.has(msg.key.id)) continue;

      const remoteJid = msg.key.remoteJid;
      const isGroup = remoteJid.endsWith("@g.us");
      const isFromMe = !!msg.key.fromMe;

      // Obter texto da mensagem
      const messageContent =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text ||
        msg.message.imageMessage?.caption ||
        "";

      const text = (messageContent || "").trim();
      if (!text) continue;

      // REGRA ESTRITA DE OURO: Somente permitir interação quando a mensagem iniciar com "#?"
      // Previne que o bot responda a conversas normais, grupos ou notas pessoais do usuário
      const cleanText = text.trim();
      const startsWithTrigger = cleanText.startsWith("#?") || cleanText.startsWith("＃?");
      if (!startsWithTrigger) {
        continue;
      }

      // Validação de Grupos Permitidos
      if (isGroup) {
        const allowed = config.allowed_groups.includes("*") || config.allowed_groups.includes(remoteJid);
        if (!allowed) continue;
      }

      // Validação de Conversas Privadas
      if (!isGroup && !isFromMe && !config.respond_to_private) {
        continue;
      }

      // Se for self-chat, valida se mensagens do próprio número estão autorizadas
      if (isFromMe && !config.allow_self_messages) {
        continue;
      }

      // Extrai a consulta real removendo o gatilho "#?"
      let query = cleanText.replace(/^(#\?|＃\?)\s*/, "").trim();
      if (!query) {
        query = "menu";
      }

      // Determinar remetente real da mensagem (grupo vs privado)
      const senderJid = isGroup
        ? (msg.key.participant || msg.participant || remoteJid)
        : (isFromMe ? (sock.user?.id || remoteJid) : remoteJid);

      // Verificação estrita de autorização e suspensão do bot
      const access = await verifySenderAccess(senderJid, isFromMe);

      if (access.reason === 'suspended') {
        console.log(`[Bot Suspenso] Consulta bloqueada para o telefone ${access.phone}`);
        try {
          const suspMsg = "Regional Norte · Pephub Data Bot\n\nAmbiente Temporariamente Indisponivel\nO bot corporativo de dados esta temporariamente suspenso pela administracao da Regional Norte para consolidacao de bases e manutencao.\n\nAcesse o portal corporativo: https://pephub.cloud/";
          const sent = await sock.sendMessage(remoteJid, { text: suspMsg }, { quoted: msg });
          if (sent?.key?.id) botSentMessageIds.add(sent.key.id);
        } catch (_) {}
        continue;
      }

      if (!access.allowed) {
        console.log(`[Acesso Recusado] Numero nao cadastrado/aprovado: ${access.phone} tentou consultar: "${text}"`);
        try {
          const denialText = `Regional Norte · Pephub Data Bot\n\nAcesso Restrito: O seu numero (${access.phone}) nao consta como cadastrado e aprovado na plataforma corporativa Pephub.\n\nPara ter acesso as consultas de churn, indicadores e bases operacionais da Regional Norte, realize seu cadastro corporativo no portal:\nhttps://pephub.cloud/login/\n\nApos a validacao e homologacao pelo gestor da ferramenta, seu acesso via WhatsApp sera liberado automaticamente.`;
          const sent = await sock.sendMessage(remoteJid, { text: denialText }, { quoted: msg });
          if (sent?.key?.id) botSentMessageIds.add(sent.key.id);
        } catch (errSend) {
          console.error('[Erro Envio Bloqueio]', errSend);
        }
        continue;
      }


      console.log(`\n[Mensagem Recebida] ${isGroup ? "Grupo" : "Privado"} (${access.phone}): "${text}" -> Consulta: "${query}"`);

      try {
        // Indicador de "Digitando..."
        await sock.sendPresenceUpdate("composing", remoteJid);

        if (config.typing_delay_ms > 0) {
          await new Promise((r) => setTimeout(r, config.typing_delay_ms));
        }

        const answer = await executeAgent(query, access.phone);

        // Envia resposta citando a pergunta do usuário
        const sent = await sock.sendMessage(
          remoteJid,
          { text: answer },
          { quoted: msg }
        );

        if (sent?.key?.id) {
          botSentMessageIds.add(sent.key.id);
          if (botSentMessageIds.size > 2000) {
            const first = botSentMessageIds.values().next().value;
            botSentMessageIds.delete(first);
          }
        }

        console.log(`[Resposta Enviada] para ${remoteJid}`);
      } catch (err) {
        console.error("[Erro Envio]", err);
      }
    }
  });
// Tratamento de erros globais para evitar que o Node.js encerre o processo em oscilações de rede
process.on("unhandledRejection", (err) => {
  console.error("[Aviso Nao-Fatal - Rejeicao]:", err?.message || err);
});
process.on("uncaughtException", (err) => {
  console.error("[Aviso Nao-Fatal - Excecao]:", err?.message || err);
});
startBot().catch((err) => {
  console.error("[Erro Fatal]", err);
});
