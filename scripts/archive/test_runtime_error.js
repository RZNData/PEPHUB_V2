const fs = require('fs');
const zlib = require('zlib');
const vm = require('vm');

const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
let jsCode = html.substring(sIdx + 8, eIdx);

// Descomprimir colunas previamente
const pStart = html.indexOf('const PAYLOAD = ') + 'const PAYLOAD = '.length;
const pEnd = html.indexOf('/* ============ decodificação ============ */');
const payloadJson = html.substring(pStart, pEnd).trim().replace(/;$/, '');
const PAYLOAD = JSON.parse(payloadJson);

// Substituir apenas a função inflate por uma que retorna o buffer real
jsCode = jsCode.replace('async function inflate(u8){', 'async function inflate(u8){ return globalThis.__uncomp(u8);');

// Criar elementos mock
const elements = {};
function getEl(id) {
  if (!elements[id]) {
    elements[id] = {
      id,
      value: id === 'fSafra' ? 'mai/26' : (id === 'mapMetric' ? 'c60' : ''),
      checked: false,
      innerHTML: '',
      textContent: '',
      style: {},
      dataset: {},
      options: [], children: [], removeChild: () => {},
      selectedOptions: [],
      setAttribute: () => {}, getAttribute: () => null, classList: {
        add: () => {},
        remove: () => {},
        toggle: () => {},
        contains: () => false
      },
      appendChild: (c) => c,
      querySelector: (sel) => getEl('sel_' + sel.replace(/[^a-zA-Z0-9]/g, '_')),
      querySelectorAll: (sel) => [],
      addEventListener: () => {},
      getContext: () => ({
        fillRect: () => {},
        clearRect: () => {},
        beginPath: () => {},
        arc: () => {},
        fill: () => {},
        stroke: () => {}, setTransform: () => {}, resetTransform: () => {}, save: () => {}, restore: () => {}, scale: () => {}, translate: () => {}, getImageData: () => ({data: new Uint8ClampedArray(4)}), putImageData: () => {}
      })
    };
  }
  return elements[id];
}

const mockBody = getEl('body');
const mockDoc = {
  body: mockBody,
  getElementById: (id) => getEl(id),
  querySelector: (s) => getEl('qs_' + s.replace(/[^a-zA-Z0-9]/g, '_')),
  querySelectorAll: (s) => [],
  createElement: (tag) => getEl('tag_' + tag),
  createElementNS: (ns, tag) => getEl('svg_' + tag),
  addEventListener: () => {}
};

const sandbox = {
  document: mockDoc,
  window: {
    addEventListener: () => {},
    innerWidth: 1920,
    innerHeight: 945,
    devicePixelRatio: 1
  },
  console: console,
  requestAnimationFrame: (fn) => fn(), setTimeout: (fn, delay) => {
    try { fn(); } catch(e) { console.error("ERRO DENTRO DO SETTIMEOUT:", e); }
  },
  clearTimeout: () => {},
  Math: Math,
  Date: Date,
  Set: Set,
  Map: Map,
  Int32Array: Int32Array,
  Uint8Array: Uint8Array,
  Uint16Array: Uint16Array,
  Uint32Array: Uint32Array,
  Float32Array: Float32Array,
  Array: Array,
  Object: Object,
  String: String,
  Number: Number,
  RegExp: RegExp,
  JSON: JSON,
  atob: (s) => Buffer.from(s, 'base64').toString('binary'),
  btoa: (s) => Buffer.from(s, 'binary').toString('base64'), localStorage: { getItem: () => null, setItem: () => {} },
  __uncomp: (u8) => {
    const uncomp = zlib.inflateSync(Buffer.from(u8));
    return uncomp.buffer.slice(uncomp.byteOffset, uncomp.byteOffset + uncomp.byteLength);
  }
};

async function test() {
  try {
    vm.createContext(sandbox);
    vm.runInContext(jsCode, sandbox);
    console.log("Script global executado com sucesso!");
    await new Promise(r => setTimeout(r, 200));
    console.log("TESTE FINALIZADO: NENHUM ERRO ENCONTRADO!");
    console.log("\n=== CONTEÚDO RENDERIZADO DE tblMtx ===");
    console.log(getEl('tblMtx').innerHTML.substring(0, 1400));
    console.log("\n=== TFOOT DE tblMtx ===");
    console.log(getEl('tblMtx').innerHTML.substring(getEl('tblMtx').innerHTML.lastIndexOf('<tfoot>')));
  } catch (err) {
    console.error("ERRO CAPTURADO:", err);
  }
}

test();
