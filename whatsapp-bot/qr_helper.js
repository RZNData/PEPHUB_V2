const fs = require("fs");
const path = require("path");
let QRCode = null;
try {
  QRCode = require("qrcode");
} catch (_) {}

const QR_HTML_PATH = path.join(__dirname, "qr.html");

/**
 * Salva Código de Pareamento de 8 dígitos em HTML amigável
 */
function savePairingCodeHtml(code, phone) {
  const clean = String(code || "").trim();
  const formattedCode = clean.length === 8 ? `${clean.slice(0, 4)}-${clean.slice(4)}` : clean;
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Código de Pareamento — Pephub Bot</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background: #0b141a; color: #e9edef; margin: 0; padding: 20px; box-sizing: border-box; }
    .card { background: #111b21; padding: 32px 28px; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); max-width: 480px; width: 100%; border: 1px solid #202c33; }
    h2 { margin-top: 0; color: #00a884; font-size: 20px; font-weight: 700; }
    p { color: #8696a0; font-size: 13.5px; line-height: 1.5; margin-bottom: 16px; }
    .code-container { background: #0b141a; padding: 18px 24px; border-radius: 10px; border: 2px solid #00a884; display: inline-block; margin: 12px 0 18px; box-shadow: 0 0 15px rgba(0, 168, 132, 0.2); }
    .code-val { font-size: 38px; font-weight: 800; letter-spacing: 6px; color: #00a884; font-family: Consolas, monospace; }
    .phone-tag { font-size: 12px; color: #8696a0; margin-top: 6px; }
    .steps { text-align: left; background: #0b141a; border-radius: 8px; padding: 14px 18px; margin-top: 18px; font-size: 12.5px; color: #d1d7db; line-height: 1.7; border: 1px solid #202c33; }
    .steps ol { margin: 0; padding-left: 20px; }
    .steps strong { color: #00a884; }
    .badge { display: inline-block; background: #1f2c34; color: #00a884; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-bottom: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">Pephub Regional Norte · Pareamento Direto</div>
    <h2>Conectar com Código de 8 Dígitos</h2>
    <p>Sem câmera e sem falha de leitura! Digite o código abaixo no seu WhatsApp:</p>
    
    <div class="code-container">
      <div class="code-val">${formattedCode}</div>
      <div class="phone-tag">Número Solicitante: <strong>+${phone}</strong></div>
    </div>

    <div class="steps">
      <ol>
        <li>Abra o WhatsApp no celular</li>
        <li>Toque em <strong>Mais opções</strong> (⋮) ou <strong>Configurações</strong> (⚙️)</li>
        <li>Toque em <strong>Aparelhos Conectados</strong> &gt; <strong>Conectar um aparelho</strong></li>
        <li>Toque na opção <strong>"Conectar com número de telefone"</strong> (na parte inferior da tela)</li>
        <li>Digite o código de 8 dígitos: <strong>${formattedCode}</strong></li>
      </ol>
    </div>
  </div>
</body>
</html>`;
  fs.writeFileSync(QR_HTML_PATH, html, "utf-8");
}

/**
 * Salva QR Code em HTML local autossuficiente com imagem renderizada
 */
async function saveQrHtml(qrString) {
  let imgHtml = '';
  if (QRCode) {
    try {
      const dataUrl = await QRCode.toDataURL(qrString, { width: 320, margin: 2 });
      imgHtml = `
        <div style="background:#fff;padding:16px;border-radius:8px;display:inline-block;box-shadow:0 2px 10px rgba(0,0,0,0.3);margin-top:14px">
          <img src="${dataUrl}" alt="QR Code WhatsApp" style="display:block;width:280px;height:280px">
        </div>
      `;
    } catch (_) {}
  }

  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Escanear WhatsApp — Pephub Bot</title>
  <meta http-equiv="refresh" content="25">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background: #0b141a; color: #e9edef; margin: 0; padding: 20px; box-sizing: border-box; }
    .card { background: #111b21; padding: 28px; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); max-width: 440px; width: 100%; }
    h2 { margin-top: 0; color: #00a884; font-size: 19px; }
    p { color: #8696a0; font-size: 13px; line-height: 1.5; margin-bottom: 12px; }
    .steps { text-align: left; background: #0b141a; border-radius: 6px; padding: 12px 16px; margin-top: 18px; font-size: 12px; color: #8696a0; line-height: 1.6; }
    .steps ol { margin: 0; padding-left: 18px; }
    .badge { display: inline-block; background: #1f2c34; color: #00a884; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-bottom: 10px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">Pephub Regional Norte</div>
    <h2>Conectar Bot ao WhatsApp</h2>
    <p>Aponte a câmera do seu WhatsApp para o QR Code abaixo para parear a sessão corporativa:</p>
    ${imgHtml}
    <div class="steps">
      <ol>
        <li>Abra o WhatsApp no celular</li>
        <li>Toque em <strong>Mais opções</strong> (⋮) ou <strong>Configurações</strong> (⚙️)</li>
        <li>Toque em <strong>Aparelhos Conectados</strong> &gt; <strong>Conectar um aparelho</strong></li>
        <li>Aponte a câmera para esta tela</li>
      </ol>
    </div>
  </div>
</body>
</html>`;
  fs.writeFileSync(QR_HTML_PATH, html, "utf-8");
}

module.exports = { saveQrHtml, savePairingCodeHtml, QR_HTML_PATH };
